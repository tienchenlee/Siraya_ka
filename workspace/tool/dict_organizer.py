#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re

from pprint import pprint

NounPAT = re.compile(r"(?<=ENTITY_)nouny|nounHead|oov")

def read_json(folder_path: str) -> list:
    """
    讀取指定資料夾內的所有 JSON 檔案內容，並將其組合成一個列表返回。
    
    參數:
        folder_path (str): 資料夾的路徑，其中包含需要讀取的 JSON 檔案。

    回傳:
        list: 該資料夾中所有 JSON 檔案內容的列表，其中每個元素對應一個 JSON 檔案的內容。
    返回的內容格式為：
    [
        [
            {"s": "Siraya",  # 西拉雅
             "g": "gloss",   # 詞彙對應
             "p": "pos"},    # 詞性標記
            ...
        ],
        [
            {"s": "Siraya",  # 西拉雅
             "g": "gloss",   # 詞彙對應
             "p": "pos"},    # 詞性標記
            ...
        ]
    ]
    每個子列表表示一個 JSON 檔案的內容，子列表中的元素為字典。
    """
    folder_contentLIST = []
    jsonFILES = [file for file in os.listdir(folder_path) if file.endswith(".json")]
    for jsonFILE in jsonFILES:
        file_path = os.path.join(folder_path, jsonFILE)                
        with open(file_path, "r", encoding="utf-8") as f:
            contentLIST = json.load(f)             #contentLIST 是一個 jsonFILE 的內容
            for dictionary in contentLIST:
                dictionary["p"] = re.sub(NounPAT, "noun", dictionary["p"])
                dictionary["g"] = dictionary["g"].replace("And", "and")
            folder_contentLIST.append(contentLIST) #folder_contentLIST 是一個 folder 內所有 jsonFILE 的內容
    return folder_contentLIST

def org_ka_POS(all_contentLIST: list) -> list:
    """
    提取 "ka" 的 gloss 值與 POS 結構，並將其組織為指定的字典格式。
    參數:
        all_contentLIST (list): 包含多層結構的資料列表，外層為內容列表，
            內層每個元素是一個字典，字典包含以下鍵:
            - "s" (str): 西拉雅字串
            - "g" (str): gloss，空格分隔的詞彙對應字串
            - "p" (str): POS，空格分隔的詞性標記字串
    回傳:
        list: 包含一個字典的列表，該字典結構如下:
        [
            {
                "REL": [
                    "ACTION_verb-PV-PFV NOM ENTITY_oov ka PAST-MODIFIER.AV"
                ],
                "COMP": [
                    "FUNC_inter ka PAST-ACTION_verb.AV ENTITY_pronoun-OBL"
                ],
                ...
            }
        ]
        - 字典中的鍵為 gloss 值，值為與 "ka" 關聯的完整 POS 結構列表。
        - 如果某 gloss 重複出現，其相關的 POS 結構會追加到該 gloss 的列表中。
    """
    posDICT = {}
    resultLIST = []
    #checkLIST = []
    for contentLIST in all_contentLIST:
        for resultDICT in contentLIST:
            glossLIST = resultDICT["g"].split(" ")
            posLIST = resultDICT["p"].split(" ")
            for i in range(len(posLIST)):
                if posLIST[i] == "ka":
                    tmpPOSLIST = posLIST[:i]
                    tmpPOSLIST.append("-ka-")
                    tmpPOSLIST.extend(posLIST[i+1:])
                    if glossLIST[i] in posDICT:
                        posDICT[glossLIST[i]].append(tmpPOSLIST)
                    else:
                        posDICT[glossLIST[i]] = tmpPOSLIST
                #if glossLIST[i] == "and":   #查看原句的 resultDICT
                    #checkLIST.append({"p": resultDICT["p"], "s": resultDICT["s"], "g": resultDICT["g"]})
    #pprint(checkLIST)
    resultLIST.append(posDICT)
    return resultLIST  


if __name__ == "__main__":
    all_contentLIST = []
    folder_path = ["./ka_in_Matthew", "ka_in_John"]
    for folder in folder_path:
        folder_contentLIST = read_json(folder)
        all_contentLIST.extend(folder_contentLIST)
    
    resultLIST = org_ka_POS(all_contentLIST)
    with open("../../corpus/ka_POS_LIST.json", "w", encoding="utf-8") as f:
        json.dump(resultLIST, f, ensure_ascii=False, indent=4)