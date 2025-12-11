#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import logging
from Loki_COMP.Complementizer.main import askLoki
from preLokiTool import udFilter
from pathlib import Path
from time import sleep

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",        # 格式：時間 - 等級 - 訊息
    handlers=[
        logging.FileHandler(Path.cwd() / "COMP_identifier.log", encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)

def main(inputSTR, utterIdx):
    """"""
    refDICT = {
        "inputSTR": [inputSTR],
        "COMP": [],
        "ka_index": [],
        "utter_index": [utterIdx],
    }

    resultDICT = askLoki(inputSTR, refDICT=refDICT)

    return resultDICT

if __name__ == "__main__":
    #kaPATH = Path.cwd().parent.parent / "data" / "kaLIST.json"
    #with open(kaPATH, "r", encoding="utf-8") as f:
        #kaLIST = json.load(f)

    #resultLIST = []
    #for utterIdx, inputSTR in enumerate(kaLIST[:400]):
        #attempts = 0
        #success = False

        #while attempts < 3 and not success:
            #resultDICT = main(inputSTR, utterIdx)
            #print(resultDICT)
            #print()
            #sleep(0.8)

            #if "status" in resultDICT.keys():
                #attempts += 1
                #logging.warning(f"第 {attempts} 次嘗試: {resultDICT}")
            #else:
                #resultLIST.append(resultDICT)
                #success = True

        #if not success:
            #logging.error(f"連續 3 次嘗試失敗，跳過此句: {resultDICT}")

    ##print(resultLIST)

    #predictionDIR = Path.cwd().parent.parent / "data" / "training"
    #predictionDIR.mkdir(exist_ok=True, parents=True)

    #with open(predictionDIR / "COMP.json", "w", encoding="utf-8") as f:
        #json.dump(resultLIST, f, ensure_ascii=False, indent=4)

    #<單筆測試>
    inputSTR = "ka again -PV I .GEN you .PL .NOM speak .AV ka more .AV be.able NOM large.animal ka heavy .AV OBL back go.through .AV LOC hole OBL needle ka enter .AV -IRR NOM rich .AV LOC kingdom OBL God"

    filterSTR = udFilter(inputSTR)
    resultDICT = main(filterSTR, 0)  # 預設句子 index = 0
    print(resultDICT)
    #</單筆測試>