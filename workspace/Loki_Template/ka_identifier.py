#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
from ud_extractor import main as udconv
from time import sleep
from Siraya_ka.main import askLoki

def main(inputSTR):
    """"""
    refDICT = {
        "REL_use": [],
        "COMP_use": [],
        "and_use": []
    }
    
    lokiResult = askLoki(inputSTR, refDICT=refDICT)
    return lokiResult


if __name__ == "__main__":
    udFILE = "./Siraya_ka/intent/USER_DEFINED.json"
    with open(udFILE, "r", encoding="utf-8") as f:
        udDICT = json.load(f)
    
    jsonFILE = "../../corpus/ka_gloss_LIST.json"
    with open(jsonFILE, "r", encoding="utf-8") as f:
        glossLIST = json.load(f)
        
    #inputSTR = "when COMP leave.AV there NOM DET Jesus"
    
    for kaDICT in glossLIST:
        for k, valueLIST in kaDICT.items():
            if k == "COMP":
                for inputSTR in valueLIST:
                    inputudSTR = udconv(udDICT, inputSTR)
                    lokiResult = main(inputudSTR)
                    sleep(0.8)
                    if not lokiResult["COMP_use"]:
                        print(inputSTR)
                        print(lokiResult)
                        print(f"pattern is not matched")
                        print(f"----------------------")
                    else:
                        print(f"測試句：\n{inputSTR}")
                        print(f"模型判斷意圖為：'COMP_use'")
                        print(f"-----------------------")
            elif k == "and":
                for inputSTR in valueLIST:
                    inputudSTR = udconv(udDICT, inputSTR)
                    lokiResult = main(inputudSTR)
                    sleep(0.8)
                    if not lokiResult["and_use"]:
                        print(inputSTR)
                        print(lokiResult)
                        print(f"pattern is not matched")
                        print(f"----------------------")
                    else:
                        print(f"測試句：\n{inputSTR}")
                        print(f"模型判斷意圖為：'and_use'")
                        print(f"-----------------------")
            #elif k == "REL":
                #for inputSTR in valueLIST:
                    #inputudSTR = udconv(udDICT, inputSTR)
                    #lokiResult = main(inputudSTR)
                    #sleep(0.8)
                    #if not lokiResult["REL_use"]:
                        #print(inputSTR)
                        #print(lokiResult)
                        #print(f"pattern is not matched")
                        #print(f"----------------------")
                    #else:
                        #print(f"測試句：\n{inputSTR}")
                        #print(f"模型判斷意圖為：'REL_use'")
                        #print(f"-----------------------")