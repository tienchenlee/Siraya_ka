#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import logging

from Loki_COMP.COMP_identifier import main as askCOMP
from Loki_and.and_identifier import main as askAnd
from Loki_REL.REL_identifier import main as askREL
from pathlib import Path
from preLokiTool import udFilter
from time import sleep

def main(inputSTR, utterIdx):
    """"""
    resultLIST = []
    askLokiLIST = [askCOMP, askAnd, askREL]

    kaIdxSET = set()
    for func in askLokiLIST:
        attempts = 0
        success = False

        while attempts < 3 and not success:
            lokiResultDICT = func(inputSTR, utterIdx)
            sleep(0.5)

            if "status" in lokiResultDICT.keys():   # Server Error 會回傳 status
                attempts += 1
                logging.warning(f"第 {attempts} 次嘗試: {lokiResultDICT}")
            else:
                success = True

                if lokiResultDICT["ka_index"] != []:
                    newIdxLIST = []

                    for idx in lokiResultDICT["ka_index"]:
                        if idx not in kaIdxSET:
                            kaIdxSET.add(idx)
                            newIdxLIST.append(idx)

                    if newIdxLIST:
                        filterDICT = lokiResultDICT.copy()
                        filterDICT["ka_index"] = newIdxLIST

                        resultLIST.append(filterDICT)
                        print(filterDICT)

        if not success:
            logging.error(f"連續 3 次嘗試失敗，跳過此測試句: {lokiResultDICT}")

    return resultLIST

if __name__ == "__main__":
    kaPATH = Path.cwd().parent / "data" / "kaLIST.json"
    with open(kaPATH, "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    predictionLIST = []
    for utterIdx, inputSTR in enumerate(kaLIST[:50]):
        resultLIST = main(inputSTR, utterIdx)
        predictionLIST.extend(resultLIST)

    predictionDIR = Path.cwd().parent / "data" / "training"
    predictionDIR.mkdir(exist_ok=True, parents=True)

    with open(predictionDIR / "predictionLIST.json", "w", encoding="utf-8") as f:
        json.dump(predictionLIST, f, ensure_ascii=False, indent=4)


    ##<單筆測試>
    #inputSTR ="when ka see-LV they.GEN NOM star then PAST-joyful.AV NOM they OBL joy ka exceeding.AV great.AV"

    #filterSTR = udFilter(inputSTR)
    #resultLIST = main(filterSTR, 0)  # 預設句子 index = 0
    #print()
    #print(resultLIST)
    ##</單筆測試>

