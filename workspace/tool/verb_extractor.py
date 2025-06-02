#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import json
from pprint import pprint

verbPAT = re.compile(r"(?:\w+\.){0,2}\w+(?:\.AV|(?:\.|-)PV|(?:\.|-)LV|\.IV).+COMP") 

def main(glossLIST):
    """
    從 glossLIST 中的 COMP 欄位擷取出包含 COMP 的動詞詞組。
    
    參數：
    - glossLIST (list[dict]): gloss sentences that includes "ka".
    e.g. [
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
    
    回傳：
    - list[str]: 取出的句中「動詞詞組~COMP"」部分。
    """
    verbLIST = []
    for kaDICT in glossLIST:
        for key, value in kaDICT.items():
            if key == "COMP":
                compLIST = value
                for c in compLIST:
                    matchLIST = re.findall(verbPAT, c)
                    verbLIST.extend(matchLIST)            
    
    return list(set(verbLIST))


if __name__ == "__main__":
    jsonFILE = "../../corpus/ka_gloss_LIST.json"
    with open(jsonFILE, "r", encoding="utf-8") as f:
        glossLIST = json.load(f)
        
    verbLIST = main(glossLIST)
    pprint(verbLIST)
    