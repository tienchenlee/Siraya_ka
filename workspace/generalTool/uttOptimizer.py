#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import exrex
import json
import re

from collections import defaultdict
from pathlib import Path

posTagPAT = re.compile("</?[a-zA-Z]+(_[a-zA-Z]+)?>")
notCapturePAT = re.compile(fr"\((?!\?)")

def main(refFILE, verbVarKey, replaceSRC):
    """"""
    refDICT = json.load(open(refFILE, encoding="utf-8"))
    atmDICT = json.load(open(str(refFILE).replace("ref", "atm"), encoding="utf-8"))
    verbLIST = list(exrex.generate(refDICT["var"][verbVarKey]))

    newIntentDICT = {}
    distributedLIST = []

    for utteranceSTR in refDICT["utterance"]:
        if replaceSRC in refDICT["utterance"][utteranceSTR]["pattern"]:
            for v in verbLIST:
                #先處理結果輸出的 newIntentDICT 資料結構
                if v in newIntentDICT:
                    pass
                else:
                    newIntentDICT[v] = []

                #再處理結果輸出的 newIntentDICT 中的 utterance，以便後續可以 insert 到新的 project 裡。
                replaceSRC_PAT = fr"({refDICT['var'][verbVarKey]})"
                for k in atmDICT["pattern"]:
                    notCapture_k = re.sub(notCapturePAT, "(?:", k)
                    if atmDICT["pattern"][k]["utterance"] == utteranceSTR:
                        substitutePAT = re.compile(notCapture_k.replace(f"{refDICT['var'][verbVarKey]}", replaceSRC_PAT, 1))
                        posSTR = refDICT["utterance"][utteranceSTR]["pos"]
                        oldV_TPL = [(p.group(1), p.start(1), p.end(1)) for p in substitutePAT.finditer(posSTR)][0]
                        newUttSTR = posTagPAT.sub(" ", f"{posSTR[:oldV_TPL[1]]}{v}{posSTR[oldV_TPL[2]:]}").replace("  ", " ").strip()

                        distributedLIST.append((utteranceSTR, v))

                #最後把結果輸出的 newIntentDICT 中對應 utterance 的 pattern 準備好
                newPat = refDICT["utterance"][utteranceSTR]["pattern"].replace(replaceSRC, v, 1)
                if newUttSTR == v:
                    pass
                else:
                    newIntentDICT[v].append((newUttSTR, newPat))
                #print(newIntentDICT)

    return newIntentDICT, distributedLIST

if __name__ == "__main__":
    refDIR = Path(f"{Path.cwd()}/Complementizer/ref/")
    excludeLIST = ["vague.ref", "unsolved.ref", "test.ref"]
    refLIST = [file for file in refDIR.glob("*.ref") if file.name not in excludeLIST]

    allIntentDICT = defaultdict(list)
    allDistributedLIST = []

    verbVarKey="CP_taking_Verb"
    for refFILE in refLIST:
        newIntentDICT, distributedLIST = main(refFILE, verbVarKey=verbVarKey, replaceSRC="{{CP_taking_Verb}}")

        for k, v in newIntentDICT.items():
            allIntentDICT[k].extend(v)

        allDistributedLIST.extend(distributedLIST)

    outputDIR = Path(f"{Path.cwd()}/Complementizer/optimized/{verbVarKey}")
    outputDIR.mkdir(parents=True, exist_ok=True)
    with open(file=f"{outputDIR}/newIntentDICT.json", mode="w", encoding="utf-8") as f:
        json.dump(allIntentDICT, f, ensure_ascii=False, indent=4)

    with open(file=f"{outputDIR}/distributedLIST.json", mode="w", encoding="utf-8") as f:
        json.dump(allDistributedLIST, f, ensure_ascii=False, indent=4)