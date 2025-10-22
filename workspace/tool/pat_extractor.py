#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import json
from pathlib import Path

G_markerPat = re.compile(r"<\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>([A-Z\-\.]+|ka)</\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>")
G_notMarkerPat = re.compile(r"<\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>([A-Z][a-z]+|(?!ka)[a-z]+)</\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>")
G_nounPat = re.compile(r"<\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>([a-z]+|[A-Z][a-z]+)</\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>")

def main(udDICT, inputSTR):
    """
    刪減 "ka" 或是全大寫字 (e.g. "OBL") 的 tags (e.g. "|ENTITY_(nounHead|nouny?|oov))", "|VerbP)")。

    參數：
    - inputSTR (str): 輸入字串 (patterns from Loki)。

    回傳：
    - outputSTR (str): 處理後的輸出字串。
    """

    outputSTR = inputSTR

    #dictPATH = Path.cwd().parent.parent / "corpus" / "USER_DEFINED.json"
    #with open(dictPATH, "r", encoding="utf-8") as f:
        #udDICT = json.load(f)

    #tagLIST = ["ENTITY_person", "LOCATION", "ENTITY_noun", "CLAUSE_particle", "TIME_holiday", "TIME_month"]
    #for keySTR, valueLIST in udDICT.items():
        #if keySTR in tagLIST:

            #def replace(m):
                #wordSTR = m.group(1)
                #if wordSTR in valueLIST:
                    #return f"<{keySTR}>{wordSTR}</{keySTR}>"
                #else:
                    #return m.group(0)

            #outputSTR = re.sub(G_notMarkerPat, replace, outputSTR)



    if re.search(G_markerPat, inputSTR):
        # 刪減 ENTITY & VerbP & ModifierP
        outputSTR = re.sub(G_markerPat, r"<UserDefined>(\1)</UserDefined>", outputSTR)
        outputSTR = outputSTR.replace("|VerbP)", "").replace("(ACTION_verb", "ACTION_verb")
        outputSTR = outputSTR.replace("|ModifierP)", "").replace("(MODIFIER", "MODIFIER")

    for verbSTR in udDICT["_asVerb_"]:
        if verbSTR in outputSTR:
            outputSTR = outputSTR.replace("(UserDefined|ENTITY_(nounHead|nouny?|oov))", "UserDefined").replace("/(UserDefined|ENTITY_(nounHead|nouny?|oov))", "/UserDefined")

    if re.search(G_notMarkerPat, inputSTR):
        outputSTR = re.sub(G_notMarkerPat, r"<ENTITY_[^>]+>\1</ENTITY_[^>]+>", outputSTR)



    return outputSTR


if __name__ == "__main__":
    udDICT = "../../corpus/USER_DEFINED.json"
    with open(udDICT, "r", encoding="utf-8") as f:
        udDICT = json.load(f)

    inputSTR = "<(UserDefined|ENTITY_(nounHead|nouny?|oov))>PAST-</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(ACTION_verb|VerbP)>leave</(ACTION_verb|VerbP)><(UserDefined|ENTITY_(nounHead|nouny?|oov))>.AV</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>NOM</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>DET</(UserDefined|ENTITY_(nounHead|nouny?|oov))><ENTITY_person>Jesus</ENTITY_person><(ACTION_verb|VerbP)>go.across</(ACTION_verb|VerbP)><(UserDefined|ENTITY_(nounHead|nouny?|oov))>.AV</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>OBL</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>sea</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>ka</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>LOC</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>Galilee</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>ka</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>sea</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>OBL</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>Tiberias</(UserDefined|ENTITY_(nounHead|nouny?|oov))>"
    outputSTR = main(udDICT, inputSTR)
    print(outputSTR)