#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json

from V_and_V.main import askLoki
from pathlib import Path
from time import sleep

G_dataDIR = Path.cwd().parent / "data"

def main(inputSTR):
    """"""
    refDICT = {
        "V_before": [],
        "V_after": []
    }


    resultDICT = askLoki(inputSTR, refDICT=refDICT)
    return resultDICT

if __name__ == "__main__":
    ##<單筆測試>
    #inputSTR ="because ka bind -PV they .GEN NOM burden ka heavy .AV ka not PC. able -PV carry .AV ka lay.on.shoulder -PV OBL man yet not.willing .AV move .AV NOM they OBL finger their"

    #resultDICT = main(inputSTR)
    #print(resultDICT)
    ##</單筆測試>

    with open(f"{G_dataDIR}/answer/and.json", "r", encoding="utf-8") as f:
        andAnsLIST = json.load(f)

    with open(f"{G_dataDIR}/kaLIST.json", "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    utterSET = set()
    for item_l in andAnsLIST:
        utterIdx = item_l[0]
        if utterIdx not in utterSET:
            utterSET.add(utterIdx)

    V_beforeSET = set()
    V_afterSET = set()
    for utterIdx in utterSET:
        inputSTR = kaLIST[utterIdx]
        resultDICT = main(inputSTR)
        sleep(0.8)
        print(resultDICT)
        print()
        if resultDICT["V_before"] and resultDICT["V_after"]:
            V_beforeSET.add(resultDICT["V_before"][0])
            V_afterSET.add(resultDICT["V_after"][0])

    with open(f"{Path.cwd()}/V_before.json", "w", encoding="utf-8") as f:
        json.dump(list(V_beforeSET), f, ensure_ascii=False, indent=4)
    with open(f"{Path.cwd()}/V_after.json", "w", encoding="utf-8") as f:
        json.dump(list(V_afterSET), f, ensure_ascii=False, indent=4)