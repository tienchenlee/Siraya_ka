#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import logging
from Loki_REL.Relativizer.main import askLoki
from preLokiTool import udFilter
from pathlib import Path

def main(inputSTR, utterIdx):
    """"""
    refDICT = {"inputSTR": [inputSTR],
               "REL": [],
               "ka_index": [],
               "utter_index": [utterIdx]}


    resultDICT = askLoki(inputSTR, refDICT=refDICT)
    return resultDICT

if __name__ == "__main__":
    #kaPATH = Path.cwd().parent.parent / "data" / "kaLIST.json"
    #with open(kaPATH, "r", encoding="utf-8") as f:
        #kaLIST = json.load(f)

    #resultLIST = []
    #for utterIdx, inputSTR in enumerate(kaLIST[:400]):
        #resultDICT = main(inputSTR, utterIdx)
        #print(resultDICT)
        #print()
        #resultLIST.append(resultDICT)

    ##print(resultLIST)

    #predictionDIR = Path.cwd().parent.parent / "data" / "training"
    #predictionDIR.mkdir(exist_ok=True, parents=True)

    #with open(predictionDIR / "REL.json", "w", encoding="utf-8") as f:
        #json.dump(resultLIST, f, ensure_ascii=False, indent=4)

    #<單筆測試>
    inputSTR ="PAST- say .AV NOM they him -OBL why ka PAST- instruct -PV GEN Moses ka give -IV .IRR NOM scripture OBL divorcement ka cause.leave -PV .IRR NOM she ka wife OBL man"

    #filterSTR = udFilter(inputSTR)
    resultDICT = main(inputSTR, 0)  # 預設句子 index = 0
    print(resultDICT)
    #</單筆測試>