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

    # Step 2: 如果有兩個空格就替換成一個，並去除開頭空格 
    while "  " in inputSTR:
        inputSTR = inputSTR.replace("  ", " ")
    
    inputSTR = inputSTR.lstrip()
    
    # Step 3: 如果 inputSTR 有 "REL" or "COMP"，就替換成 "ka"
    outputSTR = inputSTR
    kaLIST = ["REL", "COMP"]
    for ka in kaLIST:
        while ka in outputSTR:
            outputSTR = outputSTR.replace(ka, "ka")

    return outputSTR

if __name__ == "__main__":
    udDICT = "../../corpus/USER_DEFINED.json"
    with open(udDICT, "r", encoding="utf-8") as f:
        udDICT = json.load(f)
        
    ka_gloss_LIST = "../../corpus/ka_gloss_LIST.json"
    with open(ka_gloss_LIST, "r", encoding="utf-8") as f:
        ka_gloss_LIST = json.load(f)
    
    # 將所有 training data 前處理
    #for kaDICT in ka_gloss_LIST:
        #for valueLIST in kaDICT.values():
            #for inputSTR in valueLIST:
                #outputSTR = main(udDICT, inputSTR)
                #print(outputSTR)
    
    # 可放入一句需前處理的句子，並直接印出
    inputSTR = "OBL this-also REL PAST-do-PV"
    print(f"inputSTR:\n{inputSTR}")    
    outputSTR = main(udDICT, inputSTR)
    print(f"outputSTR:\n{outputSTR}")