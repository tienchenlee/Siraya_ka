#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json

def main(udDICT, inputSTR):
    """
    依據自定義辭典 udDICT，處理 inputSTR 的字串。
    
    1. 對詞典中包含 "." 或 "-" 的詞彙，在 inputSTR 中出現時，將其前後加上空格，以利後續切分。
    2. 將 inputSTR 中多餘的空格（兩個以上連續空格）壓縮成單一空格。
    3. 將 inputSTR 中的 "REL" 或 "COMP" 替換為 "ka"。
    
    參數：
    - udDICT (dict): 使用者自定義詞典，格式為 {key: [value1, value2, ...]}。
    - inputSTR (str): 要進行處理的輸入字串。

    回傳：
    - outputSTR (str): 經過處理後的字串。
    """
    # Step 1: 在 inputSTR 中的 "." or "-" 符號的前後各加上一個空格
    for valueLIST in udDICT.values():
        for valueSTR in valueLIST:
            if "." in valueSTR or "-" in valueSTR:
                if valueSTR in inputSTR:
                    inputSTR = inputSTR.replace(valueSTR, f" {valueSTR} ")

    # Step 2: 如果有兩個空格就替換成一個    
    while "  " in inputSTR:
        inputSTR = inputSTR.replace("  ", " ")
    print(inputSTR)
    
    # Step 3: 如果 inputSTR 有 "REL" or "COMP"，就替換成 "ka"
    outputSTR = inputSTR
    kaLIST = ["REL", "COMP"]    #"and" 有可能是 "apa" or "ka" 所以不列，手動改
    for ka in kaLIST:
        while ka in inputSTR:
            outputSTR = inputSTR.replace(ka, "ka")

    return outputSTR

if __name__ == "__main__":
    udDICT = "../../corpus/USER_DEFINED.json"
    with open(udDICT, "r", encoding="utf-8") as f:
        udDICT = json.load(f)
    
    inputSTR = "because also COMP not need.AV NOM he COMP testify.AV-IRR NOM anyone OBL man for PC.self-PV he.GEN understand.AV NOM things REL at.inside.AV OBL man"
    
    outputSTR = main(udDICT, inputSTR)
    print(outputSTR)