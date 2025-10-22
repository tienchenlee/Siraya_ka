#!/user/bin/env python
# -*- coding: utf-8 -*-

import json
import re

from collections import defaultdict
from docx import Document
from pathlib import Path
from requests import post
from typing import Union

G_chiPat = re.compile(r"[\u4e00-\u9fff]")
G_splitPat = re.compile(r"\s")

def _orderFile(filePATH):
    """
    從檔案名稱中提取並返回數字部分，以便進行排序。

    參數:
        filePATH: 文件路徑。

    返回:
        int: 檔案名稱中的數字部分，轉換為整數。
    """
    fileNameSTR = Path(filePATH).stem
    match = re.search(r"\d+", fileNameSTR)
    return int(match.group())

def _docx2Txt(docxPATH, txtPATH):
    """
    讀取 docx 檔案內容，並寫成 txt 檔案。

    參數：
        docxPATH: 要讀取的 docx 檔案的路徑。
        txtPATH: 輸出的 txt 檔案的路徑。
    """
    document = Document(docxPATH)

    with open(txtPATH, "w", encoding="utf-8") as f:
        for paragraph in document.paragraphs:
            textSTR = paragraph.text.strip()  # 去除首尾空白

            # 檢查是否包含「數字:數字」，如果有，則在前面加上換行符號（處理 docx 沒有分頁符號問題）
            textSTR = re.sub(r"(\d+:\d+)", r"\n\1", textSTR)

            f.write(textSTR + "\n")  # 正常寫入

def _txtCreator(folderPATH):
    """
    將資料夾內所有 docx 檔案依序轉換為對應的 txt 檔案。
    調用 _docx2Txt() 輸出同名的 txt 檔案，與 docx 保存於同一目錄下。

    參數:
        folderPATH: 包含 docx 檔案的資料夾路徑。
    """
    docxLIST = list(folderPATH.glob("*.docx"))
    sortedLIST = sorted(docxLIST, key=lambda f: _orderFile(str(f)))

    for filePATH in sortedLIST:
        txtPATH = filePATH.with_suffix(".txt")
        _docx2Txt(str(filePATH), str(txtPATH))

def _readTxt(folderPATH):
    """
    讀取資料夾中的所有 txt 檔案內容，並將其整理為列表返回。

    參數:
        folderPATH: 包含 txt 檔案的資料夾路徑。

    回傳:
        list: 一個嵌套列表，其中每個內部列表對應一個 txt 檔案的所有行內容。
    """
    txtLIST = list(folderPATH.glob("*.txt"))
    sortedLIST = sorted(txtLIST, key=lambda f: _orderFile(str(f)))
    allContentLIST = []

    for filePATH in sortedLIST:
        with open(filePATH, "r", encoding="utf-8") as f:
            contentLIST = [line.strip() for line in f]  #contentLIST 是一個 txt 的內容
            #contentLIST = [r.replace("\n", "").strip() for r in f.readlines()]
            allContentLIST.append(contentLIST)

    return allContentLIST

def _getChapter(contentLIST: list) -> list:
    """
    從輸入的內容列表中篩選出包含 "ka" 的句子，如果 ka 位於句首會多拿前一句。

    參數:
        contentLIST (list): 包含多行文字的列表，每行可能是西拉雅語句子、gloss 句子。

    回傳:
        list: 篩選出包含 "ka" 的句子對列表。
            - 返回列表包含以下兩種格式:
                - 若直接匹配: [西拉雅, gloss]
                - 若額外加入前一句: ([西拉雅, gloss], [西拉雅, gloss])
    """

    #排除「第幾章」之前的文字、1:1 那行
    tmpLIST = [c for c in contentLIST if isinstance(c, str) and not re.search(r"\d+(?:-|\:)", c) and c != ""]
    for i, c in enumerate(tmpLIST):
        if "章" in c:
            tmpLIST = tmpLIST[i+1:]
            break
    #pprint(tmpLIST)

    chapterLIST = []
    currentDICT = defaultdict(list)
    for tmp_s in tmpLIST:
        if "\t" in tmp_s:
            # 處理語料編撰時，不一致問題，像是沒用 tab 分開詞彙，或是多用空格分開了一個字
            if "  " in tmp_s:
                tmp_s = tmp_s.replace(" ", "\t")
            else:
                tmp_s = tmp_s.replace(" ", "")

            while "\t\t" in tmp_s:
                tmp_s = tmp_s.replace("\t\t", "\t")

            tmp_s = tmp_s.replace("\t", " ")
            currentDICT["verse"].append(tmp_s)

        else:
            currentDICT["paraphrase"].append(tmp_s)

            if len(currentDICT["paraphrase"]) == 2:
                paraLIST = currentDICT["paraphrase"]

                # 檢查 paraphrase 是否存在中文句，沒有的話就是抓到 verse 了，先移至 verse，再重抓 paraphrase
                if not re.search(G_chiPat, paraLIST[0]) and not re.search(G_chiPat, paraLIST[1]):
                    currentDICT["verse"].extend(paraLIST)
                    currentDICT["paraphrase"].clear()
                    continue

                chapterLIST.append(currentDICT)
                currentDICT = defaultdict(list)

    #print(chapterLIST)

    return chapterLIST

def checkFormat():
    """
    確認 rawData 的格式一致性，以利後續處理。
    - verse: 兩句一個 pair (siraya -> gloss)、每個 pair 中的詞彙數量要一樣
    - paraphrase: 兩句 (Chinese, English)

    output:
    {bookname}_{chapter}.json (e.g. Matthew_1.json / John_1.json ...)
    [
        {
        "verse": [
            "sirayaSentence",
            "glossSentence",...
        ],
        "paraphrase": [
            "亞伯拉罕的後裔，大衛的子孫，耶穌基督的家譜．〔後裔子孫原文都作兒子下同〕",
            "The book of the generation of Jesus Christ, the son of David, the son of Abraham."
        ],...
        }
    ]

    """
    fileDICT = {
        "./All chapters, Gospel of Matthew, 2025.1.26": "Matthew",
        "./All chapters, Gospel of John, 2025.1.26": "John"
    }

    for inputSTR, outputSTR in fileDICT.items():
        inputPATH = Path(inputSTR)
        outputDIR = Path(outputSTR)
        outputDIR.mkdir(exist_ok=True, parents=True)

        _txtCreator(inputPATH)
        allContentLIST = _readTxt(inputPATH)

        for idx, contentLIST in enumerate(allContentLIST, start=1):
            chapterLIST = _getChapter(contentLIST)
            #pprint(chapterLIST)

            for item_d in chapterLIST:
                if len(item_d["verse"]) % 2 != 0:   # 確保西拉雅語、英文標記有一對一的句子對應
                    raise ValueError(f"列表不是偶數，無法兩兩配對！")

                for i in range(0, len(item_d["verse"]), 2):
                    sirayaLIST = [wordSTR for wordSTR in G_splitPat.split(item_d["verse"][i])]
                    glossLIST = [wordSTR for wordSTR in G_splitPat.split(item_d["verse"][i+1])]

                    # 確保兩兩對應的句子內，詞彙數量是相同的。
                    if len(sirayaLIST) != len(glossLIST):
                        print(f"檢查以下句子的詞彙一對一對應：")
                        print(f"西拉雅句：{sirayaLIST}")
                        print(f"英文標記：{glossLIST}")
                        print()

                if not re.search(G_chiPat, item_d["paraphrase"][0]):  # 如果 paraphrase 的第一個元素不是中文
                    if re.search(G_chiPat, item_d["paraphrase"][1]):  # 先檢查是不是被放到第二個元素的位置，是的話先交換位置
                        item_d["paraphrase"][0], item_d["paraphrase"][1] = item_d["paraphrase"][1], item_d["paraphrase"][0]
                    else:
                        raise ValueError(f"無法在 paraphrase 找到中文！請檢查 {item_d['verse']} 以及 {item_d['paraphrase']}")

            jsonFilePATH = outputDIR / f"{outputSTR}_{idx}.json"
            with open(jsonFilePATH, "w", encoding="utf-8") as f:
                json.dump(chapterLIST, f, ensure_ascii=False, indent=4)


def getKaList():
    """
    用標點符號將 verse 斷句，最後輸出僅留下有 ka 的句子。

    output:
    {bookname}_{chapter}.json (e.g. Matthew_1.json / John_1.json ...)
    [
        {
        "verse": [
            "sirayaSentence",
            "glossSentence",...
        ],
        "paraphrase": [
            "亞伯拉罕的後裔，大衛的子孫，耶穌基督的家譜．〔後裔子孫原文都作兒子下同〕",
            "The book of the generation of Jesus Christ, the son of David, the son of Abraham."
        ],
        "kaLIST":[
            "glossSentence that has the functional word 'ka'"
        ]
        }
    ]
    """
    #verseLIST = [
            #"Sulat ki kavuilan ti Jesus Christus,",
            #"book OBL lineage GEN Jesus Christ",
            #"ka na alak ti David,",
            #"REL PART son GEN David",
            #"ka na alak ti Abraham.",
            #"REL PART son GEN Abraham"
        #]

    ## 方法1.
    #kaLIST = []
    #for i in range(0, len(verseLIST), 2):
        #siraya_s = verseLIST[i]
        #gloss_s = verseLIST[i+1]

        #if "ka" not in siraya_s:
            #continue

        ## 單一 verse 中，ka 在句首時，就添加前一行句子，直到不是以 ka 為句首
        #if re.search(r"^ka", siraya_s):
            #collectLIST = [gloss_s]
            #prev_i = i - 2
            #tmpLIST = []

            #while prev_i >= 0:
                #prevSiraya_s = verseLIST[prev_i]
                #prevGloss_s = verseLIST[prev_i + 1]

                #tmpLIST.append(prevGloss_s)

                #if re.search(r"^ka", prevSiraya_s):
                    #prev_i -= 2
                #else:
                    #break

            #collectLIST = list(reversed(tmpLIST)) + collectLIST # 將順序反轉

    #kaLIST.append(" ".join(collectLIST))
        ##else:
            ##kaLIST.append(gloss_s)
    #print(collectLIST)

    #print(kaLIST)
    #=======

    #方法2.
    folderLIST = [Path.cwd() / "Matthew", Path.cwd() / "John"]
    for bookDIR in folderLIST:
        for jsonFILE in bookDIR.glob("*.json"):
            with open(jsonFILE, "r", encoding="utf-8") as f:
                chapterLIST = json.load(f)

            for item_d in chapterLIST:
                verseLIST = item_d["verse"]

                # step 1: 檢查是否有 "ka"
                if any("ka" in v_s.lower() for v_s in verseLIST):
                    print("有 ka 存在")

                    kaLIST = []

                    sirayaLIST = verseLIST[::2]
                    glossLIST = verseLIST[1::2]

                    # step 2: 將西拉雅語中為 ka 的位置，在英文標記的相同位置換成 ka
                    newSirayaLIST = []
                    newGlossLIST = []

                    for s_s, g_s in zip(sirayaLIST, glossLIST):
                        sirayaWordLIST = s_s.split(" ")
                        glossWordLIST = g_s.split(" ")

                        for idx, wordSTR in enumerate(sirayaWordLIST):
                            if wordSTR.lower() == "ka":
                                glossWordLIST[idx] = "ka"

                        newSirayaLIST.append(" ".join(sirayaWordLIST))
                        newGlossLIST.append(" ".join(glossWordLIST))

                    # step 3: 用標點符號將 verse 斷句，最後輸出僅留下有 ka 的句子
                    tmpGlossLIST = []
                    tmpSirayaSTR = ""

                    for siraya_s, gloss_s in zip(newSirayaLIST, newGlossLIST):
                        tmpGlossLIST.append(gloss_s)
                        tmpSirayaSTR += " " + siraya_s  # 用於檢查標點與 ka

                        if re.search(r"[.;:?]$", siraya_s.strip()):
                            # 若整段西拉雅語中有 ka，保留這一組 gloss
                            if "ka" in tmpSirayaSTR.lower():
                                kaLIST.append(" ".join(tmpGlossLIST).strip())

                            # 重置累積
                            tmpGlossLIST = []
                            tmpSirayaSTR = ""

                    # 沒有斷句用的標點符號存在於 verse，但是有 ka 存在，就整個當一句。
                    if tmpGlossLIST and "ka" in tmpSirayaSTR.lower():
                        kaLIST.append(" ".join(tmpGlossLIST).strip())

                    print(kaLIST)
                    print()
                    item_d["kaLIST"] = kaLIST

                else:
                    print("無 ka 存在")
                    print()
                    pass

            with open(jsonFILE, "w", encoding="utf-8") as f:
                json.dump(chapterLIST, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    getKaList()
    #checkFormat()


