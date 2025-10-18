#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re
from pathlib import Path

G_wordPat = re.compile(fr"\b[\w\-\.’']+\b")

def siraya2gloss():
    """
    當一個西拉雅句進來時，先從 globalDICT 轉成英文標記。再用空格切分。

    回傳：
        glossSTR (str): 轉成英文標記的字串。
    """
    dictPATH = Path.cwd().parent.parent / "data" / "globalDICT.json"
    with open(dictPATH, "r", encoding="utf-8") as f:
        globalDICT = json.load(f)

    inputSTR = "Maita ka pataixail-en au matai.nado iau-an, ra matiktik ta pataixail-en au:"
    inputSTR = inputSTR.lower()
    print(f"使用者輸入：")
    print(inputSTR)
    print()
    inputLIST = re.findall(G_wordPat, inputSTR)

    outputLIST = []

    for sirayaSTR in inputLIST:
        if sirayaSTR.lower() == "ka":
            outputLIST.append("ka")
        elif sirayaSTR in globalDICT.keys():
            outputSTR = globalDICT[sirayaSTR][0]
            outputLIST.append(outputSTR)
        else:
            outputLIST.append(f"沒找到字")

    glossSTR = " ".join(outputLIST)

    return glossSTR

def main():
    """
    依據自定義辭典 udDICT，處理 glossSTR 的字串。

    1. 對詞典中包含 "." 或 "-" 的詞彙，在 glossSTR 中出現時，將其前後加上空格，以利後續切分。
    2. 將 glossSTR 中多餘的空格（兩個以上連續空格）壓縮成單一空格。

    回傳：
        outputSTR (str):進入 loki 的字串 (for either create utterance or test utterance)。
    """
    dictPATH = Path.cwd().parent.parent / "corpus" / "USER_DEFINED.json"
    with open(dictPATH, "r", encoding="utf-8") as f:
        udDICT = json.load(f)

    glossSTR = siraya2gloss()

    # Step 1: 在 inputSTR 中的 "." or "-" 符號的前後各加上一個空格
    for keySTR, valueLIST in udDICT.items():
        if keySTR == "_asVerb":
            continue
        for valueSTR in valueLIST:
            if "." in valueSTR or "-" in valueSTR:
                if valueSTR in glossSTR:
                    glossSTR = glossSTR.replace(valueSTR, f" {valueSTR} ")

    # Step 2: 如果有兩個空格就替換成一個，並去除開頭空格
    while "  " in glossSTR:
        glossSTR = glossSTR.replace("  ", " ")

    outputSTR = glossSTR.lstrip()

    print(f"loki 輸入句：")
    print(outputSTR)
    return outputSTR

if __name__ == "__main__":
    main()