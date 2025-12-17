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
    """
    將 ka1, ka2, ka3 的比對順序設為 COMP, and, REL。
    如果句首是 ka，則預設為「然後的 and」。
    """
    resultLIST = []
    kaIdxSET = set()
    askLokiLIST = [askCOMP, askAnd, askREL]

    # <句首為 ka 預設為「然後的 and」>
    inputWordLIST = inputSTR.split(" ")
    if inputWordLIST[0] == "ka":
        defaultKaDICT = {
            "inputSTR": [inputSTR],
            "and": [{"then": True}],
            "ka_index": [0],
            "utter_index": [utterIdx],
        }

        resultLIST.append(defaultKaDICT)
    # <句首為 ka 預設為「然後的 and」>

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
                        else:
                            pass    # 如果在前面的 project 已有該 ka_index，則跳過

                    if newIdxLIST:  # 過濾後的 ka_index 放回 lokiResultDICT
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
    for utterIdx, inputSTR in enumerate(kaLIST):
        resultLIST = main(inputSTR, utterIdx)
        predictionLIST.extend(resultLIST)

    trainingDIR = Path.cwd().parent / "data" / "training"
    trainingDIR.mkdir(exist_ok=True, parents=True)

    with open(trainingDIR / "predictionLIST.json", "w", encoding="utf-8") as f:
        json.dump(predictionLIST, f, ensure_ascii=False, indent=4)


    ##<單筆測試>
    #inputSTR ="So.much.so .AV ka PAST- marvel .AV NOM multitudes while see -LV they .GEN ka speak .AV NOM dumb .AV ka well .AV NOM maimed .AV ka walk .AV NOM lame .AV ka see .AV NOM blind .AV ka PAST- cause.high .AV NOM they cause.great -PV OBL status OBL God OBL Israel"

    ##filterSTR = udFilter(inputSTR)
    #resultLIST = main(inputSTR, 0)  # 預設句子 index = 0
    #print()
    #print(resultLIST)
    ##</單筆測試>

