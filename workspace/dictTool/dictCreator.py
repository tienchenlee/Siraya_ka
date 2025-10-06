#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re

from collections import defaultdict
from docx import Document
from pathlib import Path
from pprint import pprint

splitPat = re.compile(r"[\t]+")
wordEndPat = re.compile(r"(?:[\.,\):?;]+$|^\()")
wordNormPat = re.compile(r"[-\.'’]")

dataDIR = Path.cwd().parent.parent / "data"
dataDIR.mkdir(exist_ok=True, parents=True)

def _orderFile(filePATH):
    """
    從檔案名稱中提取並返回數字部分，以便進行排序。

    參數:
        filePATH: 文件路徑。

    返回:
        int: 檔案名稱中的數字部分，轉換為整數。
    """
    match = re.search(r"\d+", filePATH)
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

def _dictAligner():
    """"""
    fileLIST = ["./All chapters, Gospel of Matthew, 2025.1.26",
                "./All chapters, Gospel of John, 2025.1.26"]

    textLIST = []

    for folderSTR in fileLIST:
        folderPATH = Path(folderSTR)

        _txtCreator(folderPATH)
        all_contentLIST = _readTxt(folderPATH)

        for contentLIST in all_contentLIST:
            for textSTR in contentLIST:
                if "\t" in textSTR:
                    # 處理語料編撰時，不一致問題，像是沒用 tab 分開詞彙，或是多用空格分開了一個字
                    if "  " in textSTR:
                        textSTR = textSTR.replace(" ", "\t")
                    else:
                        textSTR = textSTR.replace(" ", "")
                    textLIST.append(textSTR)
    #print(textLIST)
    return textLIST

def _checkPairs():
    """"""
    textLIST = _dictAligner()

    alignLIST = []

    if len(textLIST) % 2 != 0:  # 確保語料句子數量是偶數，因為是「西拉雅句」和「英文標記」兩兩對應
        raise ValueError(f"列表不是偶數，無法兩兩配對！")

    for i in range(0, len(textLIST), 2):
        sirayaLIST = [wordSTR for wordSTR in splitPat.split(textLIST[i])]
        glossLIST = [wordSTR for wordSTR in splitPat.split(textLIST[i+1])]

        # 確保兩兩對應的句子內，詞彙數量是相同的。
        if len(sirayaLIST) != len(glossLIST):
            print(f"檢查以下句子的詞彙一對一對應：")
            print(f"西拉雅句：{sirayaLIST}")
            print(f"英文標記：{glossLIST}")
            print()
        else:
            alignDICT = {
                "s": sirayaLIST,
                "g": glossLIST
            }

            alignLIST.append(alignDICT)

    print(f"寫出 alignLIST...")
    outputPATH = dataDIR / "alignLIST.json"
    with open(outputPATH, "w", encoding="utf-8") as f:
        json.dump(alignLIST, f, ensure_ascii=False, indent=4)

    return alignLIST

def main():
    """"""
    alignLIST = _checkPairs()
    globalDICT = defaultdict(set)

    for item_d in alignLIST:
        glossLIST = item_d["g"]
        sirayaLIST = item_d["s"]

        for keySTR, valueSTR in zip(sirayaLIST, glossLIST):
            # 去除字結尾的標點符號 (e.g. lava, -> lava)
            keySTR = wordEndPat.sub("", keySTR).lower() # 另外讓 key 的大小寫不分
            valueSTR = wordEndPat.sub("", valueSTR)

            # 另外將所有 key 存一個沒有標點符號的版本
            normKeySTR = wordNormPat.sub("", keySTR).lower()

            # 分別用 keySTR & normKeySTR 組成字典
            globalDICT[keySTR].add(valueSTR)
            globalDICT[normKeySTR].add(valueSTR)

    # 將 set 轉成 list
    globalDICT = {k: list(v) for k, v in globalDICT.items()}

    print(f"寫出 globalDICT...")
    dictPATH = dataDIR / "globalDICT.json"
    with open(dictPATH, "w", encoding="utf-8") as f:
        json.dump(globalDICT, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()

    #globalDICT = {
                   #"iau":["I", "me"],
                   # "makutalum":["curse.AV", "slander.AV"],
                   # ...
    # }