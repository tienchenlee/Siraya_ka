#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
from Relativizer.main import askLoki
from preLokiTool import udFilter
from pathlib import Path
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",        # 格式：時間 - 等級 - 訊息
    handlers=[
        logging.FileHandler(Path.cwd() / "REL_identifier.log", encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)

def main(inputSTR, utterIdx):
    """"""
    refDICT = {"inputSTR": [inputSTR],
               "REL": [],
               "ka_index": [utterIdx]}


    resultDICT = askLoki(inputSTR, refDICT=refDICT)
    return resultDICT

if __name__ == "__main__":
    kaPATH = Path.cwd().parent.parent / "data" / "kaLIST.json"
    with open(kaPATH, "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    resultLIST = []
    for utterIdx, inputSTR in enumerate(kaLIST[:200]):
        resultDICT = main(inputSTR, utterIdx)
        print(resultDICT)
        print()
        resultLIST.append(resultDICT)

    print(resultLIST)

    predictionDIR = Path.cwd().parent.parent / "data" / "training"
    predictionDIR.mkdir(exist_ok=True, parents=True)

    with open(predictionDIR / "REL.json", "w", encoding="utf-8") as f:
        json.dump(resultLIST, f, ensure_ascii=False, indent=4)

    #<單筆測試>
    #inputSTR ="when ka see-LV they.GEN NOM star then PAST-joyful.AV NOM they OBL joy ka exceeding.AV great.AV"

    #filterSTR = udFilter(inputSTR)
    #resultDICT = main(filterSTR, 0)  # 預設句子 index = 0
    #print(resultDICT)
    #</單筆測試>