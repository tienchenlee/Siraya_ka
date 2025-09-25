#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re

from pprint import pprint

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
                dictionary["g"] = dictionary["g"].replace("And", "and")
                dictionary["s"] = re.sub("\s{2,}", " ", dictionary["s"])    #check whether siraya sentence have multiple adjacent space
                dictionary["s"] = dictionary["s"].replace("(ka", "ka")
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
                    "<ACTION_verb-PV-PFV> NOM <ENTITY_oov> ka <PAST-MODIFIER.AV>"
                ],
                "COMP": [
                    "<FUNC_inter> ka <PAST-ACTION_verb.AV> <ENTITY_pronoun-OBL>"
                ],
                ...
            }
        ]
        - 字典中的鍵為 gloss 值，值為與 "ka" 關聯的完整 POS 結構列表。
        - 如果某 gloss 重複出現，其相關的 POS 結構會追加到該 gloss 的列表中。
    """
    posDICT = {}
    resultLIST = []
    kaGlossSET = set()
    #checkLIST = []
    for contentLIST in all_contentLIST:
        for resultDICT in contentLIST:
            glossLIST = resultDICT["g"].split(" ")
            posLIST = resultDICT["p"].split(" ")
            for i in range(len(posLIST)):
                if posLIST[i] == "ka":
                    kaGlossSET.add(glossLIST[i])
            for gloss in kaGlossSET:
                markLIST = []
                for i in range(len(posLIST)):
                    if posLIST[i] == "ka" and i != 0 and glossLIST[i] == gloss:
                        markLIST.append(i)
                tmpPOSLIST = posLIST[:]
                for i in markLIST:
                    tmpPOSLIST[i] = "-ka-"
                markSTR = " ".join(tmpPOSLIST)
                for i in markLIST:
                    if glossLIST[i] == gloss:
                        if gloss in posDICT:
                            if markSTR not in posDICT[glossLIST[i]]:
                                posDICT[glossLIST[i]].append(markSTR)
                        else:
                            posDICT[glossLIST[i]] = [markSTR]

    resultLIST.append(posDICT)
    return resultLIST  

def org_ka_gloss(all_contentLIST: list) -> list:
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
                    "book OBL lineage GEN Jesus Christ REL PART son GEN David"
                ],
                "COMP": [
                    "when COMP think-PV he.GEN NOM this"
                ],
                ...
            }
        ]
        - 字典中的鍵為 ka 的所有可能 functions。
        - 如果該句子有 ka，就將 gloss 句添加到該 function 的 value 中。
    """
    resultLIST = []
    skipLIST = []
    glossDICT = {"REL": [],
                 "COMP": [],
                 "so.that": [],
                 "such.that": [],
                 "and": [],
                 "but": [],
                 "for": []}        
    for contentLIST in all_contentLIST:
        for resultDICT in contentLIST:
            sirayaLIST = resultDICT["s"].split(" ")
            glossLIST = resultDICT["g"].split(" ")
            posLIST = resultDICT["p"].split(" ")
            for i in range(len(posLIST)):
                if posLIST[i] == "ka":                    
                    for keySTR in glossDICT:
                        if glossLIST[i] == keySTR:
                            if resultDICT["g"] not in glossDICT[keySTR]:
                                glossDICT[keySTR].append(resultDICT["g"])
                if glossLIST[i] == "and" and sirayaLIST[i] not in ["apa", "ka", "Ka", "ka,"]:
                    print(sirayaLIST[i], i)
                    print(glossLIST[i], i)
                    print(resultDICT["s"])
                    print(resultDICT["g"])
                    print(f"--------------------")
                #if glossLIST[i] == "REL" and sirayaLIST[i] not in ["ka", "Ka"]:
                    #print(sirayaLIST[i], i)
                    #print(glossLIST[i], i)
                    #print(resultDICT["s"])
                    #print(resultDICT["g"])
                    #print(f"--------------------")
                #if glossLIST[i] == "COMP" and sirayaLIST[i] not in ["ka", "Ka"]:
                    #print(sirayaLIST[i], i)
                    #print(glossLIST[i], i)
                    #print(resultDICT["s"])
                    #print(resultDICT["g"])
                    #print(f"--------------------")
                if sirayaLIST[i] == "apa" and glossLIST[i] == "and":
                    skipLIST.append(resultDICT["g"])
                
    resultLIST.append(glossDICT)
    print(skipLIST)

    return resultLIST  


if __name__ == "__main__":
    #all_contentLIST = []
    #folder_path = ["./ka_in_Matthew", "ka_in_John"]
    #for folder in folder_path:
        #folder_contentLIST = read_json(folder)
        #all_contentLIST.extend(folder_contentLIST)
    
    #resultLIST = org_ka_POS(all_contentLIST)
    #with open("../../corpus/ka_POS_LIST.json", "w", encoding="utf-8") as f:
        #json.dump(resultLIST, f, ensure_ascii=False, indent=4)
    
    ## 動詞保留 (不換成 POS)
    #all_argcontentLIST = []
    #folder_path = ["./ka_in_Matthew_arg", "ka_in_John_arg"]
    #for folder in folder_path:
        #folder_contentLIST = read_json(folder)
        #all_argcontentLIST.extend(folder_contentLIST)
    
    #resultLIST = org_ka_POS(all_argcontentLIST)
    #with open("../../corpus/ka_POS_argLIST.json", "w", encoding="utf-8") as f:
        #json.dump(resultLIST, f, ensure_ascii=False, indent=4)
        
    # 挑出 gloss 句
    all_GcontentLIST = []
    folder_path = ["./ka_in_Matthew", "ka_in_John"]
    for folder in folder_path:
        folder_contentLIST = read_json(folder)
        all_GcontentLIST.extend(folder_contentLIST)
    
    gloss_resultLIST = org_ka_gloss(all_GcontentLIST)
    with open("../../corpus/ka_gloss_LIST.json", "w", encoding="utf-8") as f:
        json.dump(gloss_resultLIST, f, ensure_ascii=False, indent=4)