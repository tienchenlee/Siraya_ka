#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import exrex
import json
import re

from collections import defaultdict
from pathlib import Path

G_posTagPAT = re.compile("</?[a-zA-Z]+(_[a-zA-Z]+)?>")
G_notCapturePAT = re.compile(fr"\((?!\?)")

def optimizeVar(refFILE, verbVarKey, replaceSRC):
    """"""
    refDICT = json.load(open(refFILE, encoding="utf-8"))
    atmDICT = json.load(open(str(refFILE).replace("ref", "atm"), encoding="utf-8"))
    verbLIST = list(exrex.generate(refDICT["var"][verbVarKey]))

    newIntentDICT = {}
    distributedLIST = []
    noV2LIST = []

    for utteranceSTR in refDICT["utterance"]:
        patternSTR = refDICT["utterance"][utteranceSTR]["pattern"]
        if replaceSRC in patternSTR: # 如果 V2 在 pattern 裡面
            for v in verbLIST:
                #先處理結果輸出的 newIntentDICT 資料結構
                if v in newIntentDICT:
                    pass
                else:
                    newIntentDICT[v] = []

                #再處理結果輸出的 newIntentDICT 中的 utterance，以便後續可以 insert 到新的 project 裡。
                replaceSRC_PAT = fr"({refDICT['var'][verbVarKey]})"
                for k in atmDICT["pattern"]:
                    notCapture_k = re.sub(G_notCapturePAT, "(?:", k)
                    if atmDICT["pattern"][k]["utterance"] == utteranceSTR:
                        substitutePAT = re.compile(notCapture_k.replace(f"{refDICT['var'][verbVarKey]}", replaceSRC_PAT, 1))
                        posSTR = refDICT["utterance"][utteranceSTR]["pos"]
                        oldV_TPL = [(p.group(1), p.start(1), p.end(1)) for p in substitutePAT.finditer(posSTR)][0]
                        newUttSTR = G_posTagPAT.sub(" ", f"{posSTR[:oldV_TPL[1]]}{v}{posSTR[oldV_TPL[2]:]}").replace("  ", " ").strip()

                        distributedLIST.append((utteranceSTR, v))

                #最後把結果輸出的 newIntentDICT 中對應 utterance 的 pattern 準備好
                newPat = patternSTR.replace(replaceSRC, v, 1)
                if newUttSTR == v:
                    pass
                else:
                    newIntentDICT[v].append((newUttSTR, newPat))
                #print(newIntentDICT)

        else: # 如果 V2 不在 pattern 裡面
            noV2LIST.append((utteranceSTR, patternSTR))

    return newIntentDICT, distributedLIST, noV2LIST

def main():
    projectLIST = ["Coordinator", "Relativizer"]
    excludeLIST = ["vague.ref", "unsolved.ref", "test.ref"]

    #verbVarKeyDICT = {
        #"CP_taking_Verb": "{{CP_taking_Verb}}",
        #"V1": "{{V1}}",
        #"V2": "{{V2}}",
        #"V3": "{{V3}}"
    #}

    for projectSTR in projectLIST:
        refDIR = Path(f"{Path.cwd()}/{projectSTR}/ref/")
        refLIST = [file for file in refDIR.glob("*.ref") if file.name not in excludeLIST]

        #for keySTR, valueSTR in verbVarKeyDICT.items():
        allIntentDICT = defaultdict(list)
        allDistributedLIST = []
        allNoV2LIST = []

        for refFILE in refLIST:
            newIntentDICT, distributedLIST, noV2LIST = optimizeVar(refFILE, verbVarKey="V2", replaceSRC="{{V2}}")

            for k, v in newIntentDICT.items():
                allIntentDICT[k].extend(v)

            allDistributedLIST.extend(distributedLIST)
            allNoV2LIST.extend(noV2LIST)

        if allDistributedLIST:
            outputDIR = Path(f"{Path.cwd()}/{projectSTR}/optimized/V2")
            outputDIR.mkdir(parents=True, exist_ok=True)
            with open(file=f"{outputDIR}/newIntentDICT.json", mode="w", encoding="utf-8") as f:
                json.dump(allIntentDICT, f, ensure_ascii=False, indent=4)

            with open(file=f"{outputDIR}/distributedLIST.json", mode="w", encoding="utf-8") as f:
                json.dump(allDistributedLIST, f, ensure_ascii=False, indent=4)

            with open(file=f"{outputDIR}/noV2LIST.json", mode="w", encoding="utf-8") as f:
                json.dump(allNoV2LIST, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()