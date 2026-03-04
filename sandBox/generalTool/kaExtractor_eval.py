#!/user/bin/env python
# -*- coding: utf-8 -*-

import json
import re

from collections import defaultdict
from docx import Document
from pathlib import Path
from preLokiTool import udFilter
import random

G_chiPat = re.compile(r"[\u4e00-\u9fff]")
G_splitPat = re.compile(r"\s")
G_verbPat = re.compile(r"(?:[\w\.]+(?=\.AV|-AV|\.PV|-PV|\.LV|-LV|-IV|-IRR|-PFV)|(?<=PAST-)[\w\.]+)")  # 以語態、時貌標記找動詞
G_leftPeripheryPAT = re.compile(r"(?<!asi\s)(?<!ta\s)(?=\b(?:mama-ki-mang|mamay-mang|malava|kaumang|aiku-an|hairu|iru|alay apa|alay)\ska\b)", re.I)

def _orderFile(filePATH):
    """
    從檔案名稱中提取並返回數字部分，以便進行排序。

    參數:
        filePATH: 文件路徑。

    返回:
        int: 檔案名稱中的數字部分，轉換為整數。
    """
    fileNameSTR = Path(filePATH).stem
    match = re.search(r"\d+(?=-)", fileNameSTR)
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
            #textSTR = re.sub(r"(\d+:\d+)", r"\n\1", textSTR)

            f.write(textSTR + "\n")  # 正常寫入

def _txtCreator(folderPATH):
    """
    將資料夾內所有 docx 檔案依序轉換為對應的 txt 檔案。
    調用 _docx2Txt() 輸出同名的 txt 檔案，與 docx 保存於同一目錄下。

    參數:
        folderPATH: 包含 docx 檔案的資料夾路徑。
    """
    docxLIST = [
        f for f in folderPATH.glob("*.docx")
        if not f.name.startswith("~$")
    ]
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

def _normalizeVerse(tmp_s):
    """
    處理語料編撰時，不一致問題，像是沒用 tab 分開詞彙，或是多用空格分開了一個字
    """
    if "  " in tmp_s:
        tmp_s = tmp_s.replace(" ", "\t")
    else:
        tmp_s = tmp_s.replace(" ", "")

    while "\t\t" in tmp_s:
        tmp_s = tmp_s.replace("\t\t", "\t")

    normalized_s = tmp_s.replace("\t", " ")

    return normalized_s

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
    tmpLIST = [c for c in contentLIST if isinstance(c, str) and not re.search(r"^\d+[:：]\s?\d+\.?$", c) and c != ""]

    chapterLIST = []
    currentDICT = defaultdict(list)
    for i, tmp_s in enumerate(tmpLIST):
        if i + 1 >= len(tmpLIST):
            continue

        next_s = tmpLIST[i+1]

        if "\t" in tmp_s and "\t" in next_s:
            currentDICT["verse"].append(_normalizeVerse(tmp_s))

        elif "\t" in tmp_s and "\t" not in next_s and not re.search(G_chiPat, next_s):
            currentDICT["verse"].append(_normalizeVerse(tmp_s))

            for j in (i + 1, i + 2, i + 3, i + 4):
                if j < len(tmpLIST):
                    if j in (i + 3, i + 4):
                        if re.search(G_chiPat, tmpLIST[j]):
                            currentDICT["paraphrase"].append(tmpLIST[j])
                    else:
                        currentDICT["paraphrase"].append(tmpLIST[j])

            if any(re.search(G_chiPat, s) for s in currentDICT["paraphrase"]):
                chapterLIST.append(currentDICT)
                currentDICT = defaultdict(list)
            else:
                print(currentDICT)
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
        "./All Questions, Catechism, 2025.1.26": "Catechism"
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

                if not any(re.search(G_chiPat, s) for s in item_d["paraphrase"]):  # 如果 paraphrase 的第一個元素不是中文
                    raise ValueError(f"無法在 paraphrase 找到中文！請檢查 {item_d['verse']} 以及 {item_d['paraphrase']}")

            jsonFilePATH = outputDIR / f"{outputSTR}_{idx}.json"
            with open(jsonFilePATH, "w", encoding="utf-8") as f:
                json.dump(chapterLIST, f, ensure_ascii=False, indent=4)

def _segment():
    global tmpGlossLIST, tmpSirayaSTR, tmpAnsLIST
    global kaLIST, ansLIST

    cleanTmpSirayaSTR = tmpSirayaSTR.lower().strip().replace("(", "").replace(")", "")

    # 沒 ka，直接丟掉
    if not re.search(r"\bka\b", cleanTmpSirayaSTR):
        tmpGlossLIST = []
        tmpSirayaSTR = ""
        tmpAnsLIST = []
        return

    # 主要斷句：left periphery（可能切多段）
    if len(re.findall(G_leftPeripheryPAT, cleanTmpSirayaSTR)) > 1:
        alaykaLIST = [
            s.strip()
            for s in re.split(G_leftPeripheryPAT, cleanTmpSirayaSTR)
            if s.strip()
        ]

        tmpGlossWordLIST = " ".join(tmpGlossLIST).split()
        tmpAnsWordLIST = " ".join(tmpAnsLIST).split()
        idx = 0

        for alayka in alaykaLIST:
            wordCountINT = len(alayka.split())

            kaLIST.append(" ".join(tmpGlossWordLIST[idx:idx + wordCountINT]))
            ansLIST.append(" ".join(tmpAnsWordLIST[idx:idx + wordCountINT]))

            idx += wordCountINT

    # 次要斷句：整句收
    else:
        kaLIST.append(" ".join(tmpGlossLIST).strip())
        ansLIST.append(" ".join(tmpAnsLIST).strip())

    # reset
    tmpGlossLIST = []
    tmpSirayaSTR = ""
    tmpAnsLIST = []

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
    #方法2.
    global tmpGlossLIST, tmpSirayaSTR, tmpAnsLIST
    global kaLIST, ansLIST

    folderLIST = [Path.cwd() / "Catechism"]
    for bookDIR in folderLIST:
        for jsonFILE in bookDIR.glob("*.json"):
            with open(jsonFILE, "r", encoding="utf-8") as f:
                chapterLIST = json.load(f)

            for item_d in chapterLIST:
                verseLIST = item_d["verse"]

                # step 1: 檢查是否有 "ka"
                if any(re.search(r"\bka\b", v_s, re.I) for v_s in verseLIST):
                    print("有 ka 存在")

                    sirayaLIST = verseLIST[::2]
                    glossLIST = verseLIST[1::2]

                    # step 2: 將西拉雅語中為 ka 的位置，在英文標記的相同位置換成 ka
                    newSirayaLIST = []
                    newGlossLIST = []
                    newAnsLIST = []  # ansLIST 對齊斷句用

                    for s_s, g_s in zip(sirayaLIST, glossLIST):
                        sirayaWordLIST = s_s.split(" ")
                        glossWordLIST = g_s.split(" ")

                        for idx, wordSTR in enumerate(sirayaWordLIST):
                            if re.search(r"\bka\b", wordSTR.lower()):
                                if glossWordLIST[idx] in ["REL", "COMP", "and", "And"]:     #如果只先處理這三種
                                    glossWordLIST[idx] = "ka"
                            if re.search(r"\bk-[a-z]+\b", wordSTR.lower()):
                                if re.search(r"\b(?:REL|COMP|[Aa]nd)-", glossWordLIST[idx]):
                                    glossWordLIST[idx] = re.sub(r"\b(?:REL|COMP|[Aa]nd)-", "ka-", glossWordLIST[idx])

                        newSirayaLIST.append(" ".join(sirayaWordLIST))
                        newGlossLIST.append(" ".join(glossWordLIST))
                        newAnsLIST.append(" ".join(g_s.split(" ")))

                    # step 3: 用標點符號將 verse 斷句，最後輸出僅留下有 ka 的句子
                    tmpGlossLIST = []
                    tmpSirayaSTR = ""
                    tmpAnsLIST = []

                    kaLIST = []
                    ansLIST = []

                    for siraya_s, gloss_s, ans_s in zip(newSirayaLIST, newGlossLIST, newAnsLIST):
                        tmpGlossLIST.append(gloss_s)    # 收集此次 verse 的 gloss (替換成 ka)
                        tmpSirayaSTR += " " + siraya_s  # 收集此次 verse 的 siraya
                        tmpSirayaSTR = tmpSirayaSTR.lower().strip()
                        tmpAnsLIST.append(ans_s)        # 收集此次 verse 的 gloss (答案)

                        if re.search(r"[\.:;?]$", siraya_s.strip()):
                            _segment()

                    if tmpGlossLIST:
                        _segment()

                    print(kaLIST)
                    print()
                    item_d["kaLIST"] = kaLIST
                    item_d["ansLIST"] = ansLIST

                else:
                    print("無 ka 存在")
                    print()
                    pass

            with open(jsonFILE, "w", encoding="utf-8") as f:
                json.dump(chapterLIST, f, ensure_ascii=False, indent=4)

def kaDictCreator():
    """
    把每小節的 kaLIST 的句子拿出來整合成一個 allKaLIST，
    找到每個句子的第一個動詞，讀取 valencyDICT，根據 valency 分 intent，

    output:
    kaDICT = {
        "V1":["sentence", "sentence"],
        "V2":["sentence", "sentence"],
        "V3":["sentence", "sentence"]
    }
    """
    allKaLIST = []
    allAnsLIST = []

    folderLIST = [Path.cwd() / "Catechism"]
    for bookDIR in folderLIST:
        for jsonFILE in bookDIR.glob("*.json"):
            with open(jsonFILE, "r", encoding="utf-8") as f:
                chapterLIST = json.load(f)
                for item_d in chapterLIST:
                    if "kaLIST" in item_d.keys():
                        allKaLIST.extend(item_d["kaLIST"])
                    if "ansLIST" in item_d.keys():
                        allAnsLIST.extend(item_d["ansLIST"])

    #print(allKaLIST)
    print(f"input：{len(allKaLIST)} 句")
    print(f"ans：{len(allAnsLIST)} 句")

    allKaLIST = [udFilter(sentenceSTR) for sentenceSTR in allKaLIST]
    allAnsLIST = [udFilter(sentenceSTR) for sentenceSTR in allAnsLIST]

    kaLIST = ["COMP", "REL", "and"]

    singleKaDICT = {
        "COMP": [],
        "REL": [],
        "and": []
    }

    for idx, eval_s in enumerate(allAnsLIST):
        kaSET = set()
        for ka in kaLIST:
            if ka in eval_s:
                kaSET.add(ka)

        if len(kaSET) == 1:
            keySTR = next(iter(kaSET))
            singleKaDICT[keySTR].append(idx)

    allEvaluationIdxLIST = []
    for idxLIST in singleKaDICT.values():
        k = min(100, len(idxLIST))
        evaluationLIST = random.sample(idxLIST, k=k)
        allEvaluationIdxLIST.extend(evaluationLIST)

    allEvaluationKaLIST  = [allKaLIST[i]  for i in allEvaluationIdxLIST]
    allEvaluationAnsLIST = [allAnsLIST[i] for i in allEvaluationIdxLIST]

    kaListPATH = Path.cwd().parent.parent / "data" / "kaLIST_eval.json"
    with open(kaListPATH, "w", encoding="utf-8") as f:
        json.dump(allEvaluationKaLIST, f, ensure_ascii=False, indent=4)

    ansListPATH = Path.cwd().parent.parent / "data" / "ansLIST_eval.json"
    with open(ansListPATH, "w", encoding="utf-8") as f:
        json.dump(allEvaluationAnsLIST, f, ensure_ascii=False, indent=4)

def kaDictChecker():
    """
    檢查 kaDICT 的句子皆存在 ka!
    """
    kaDictPATH = Path.cwd().parent.parent / "data" / "kaDICT.json"
    with open(kaDictPATH, "r", encoding="utf-8") as f:
        kaDICT = json.load(f)

    for utteranceLIST in kaDICT.values():
        for utteranceSTR in utteranceLIST:
            if not re.search(r"\bka\b", utteranceSTR):
                raise ValueError(f"此句不存在 ka！請檢查 rawData 以及 getKaList() 演算法")

def main():
    checkFormat()
    getKaList()
    kaDictCreator()
    kaDictChecker()

if __name__ == "__main__":
    main()

