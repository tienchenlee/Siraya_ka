#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import json
from pathlib import Path

G_udPat = re.compile(r"<\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>([^<]+)</\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>")

def main(inputSTR):
    """
    刪減 "|ENTITY_(nounHead|nouny?|oov))", "|VerbP)", "|ModifierP)"、
    加上捕獲和非捕獲組。

    參數：
    - inputSTR (str): 輸入字串 (patterns from Loki)。

    回傳：
    - outputSTR (str): 處理後的輸出字串。
    """

    outputSTR = inputSTR

    udPATH = Path.cwd().parent.parent / "data" / "userDefined.json"
    with open(udPATH, "r", encoding="utf-8") as f:
        udDICT = json.load(f)

    #udLIST = ["ENTITY_person", "LOCATION", "ENTITY_noun", "CLAUSE_particle", "TIME_holiday", "TIME_month", "_asVerb_"]
    #udSET = set()
    #markerSET = set()
    #for keySTR, valueLIST in udDICT.items():
        #if keySTR in udLIST:
            #udSET.update(valueLIST)
        #else:
            #markerSET.update(valueLIST)

    udSET = set()
    for keySTR, valueLIST in udDICT.items():
        if keySTR != "_ka_":
            udSET.update(valueLIST)

    def replace(m):
        wordSTR = m.group(1)
        if wordSTR == "ka": # capture wordSTR
            return f"<UserDefined>({wordSTR})</UserDefined>"
        elif wordSTR in udSET: # do not capture wordSTR
            return f"<UserDefined>{wordSTR}</UserDefined>"
        else:
            return f"<ENTITY_[^>]+>{wordSTR}</ENTITY_[^>]+>"

    outputSTR = re.sub(G_udPat, replace, outputSTR)

    outputSTR = outputSTR.replace("|VerbP)", "").replace("(ACTION_verb", "ACTION_verb")
    outputSTR = outputSTR.replace("|ModifierP)", "").replace("(MODIFIER", "MODIFIER")
    outputSTR = outputSTR.replace("(<", "(?:<")
    outputSTR = outputSTR.replace("_(", "_(?:")

    return outputSTR


if __name__ == "__main__":
    # example:
    print(f"loki 句型：")
    inputSTR ="<(UserDefined|ENTITY_(nounHead|nouny?|oov))>ka</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>go.around</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>.AV</(UserDefined|ENTITY_(nounHead|nouny?|oov))>(<ENTITY_pronoun>[^<]+</ENTITY_pronoun>)?<(UserDefined|ENTITY_(nounHead|nouny?|oov))>.PL</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>.NOM</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>OBL</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>sea</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>OBL</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(ACTION_verb|VerbP)>land</(ACTION_verb|VerbP)><(UserDefined|ENTITY_(nounHead|nouny?|oov))>convert</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>.AV</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>OBL</(UserDefined|ENTITY_(nounHead|nouny?|oov))>(<(MODIFIER|ModifierP)>[^<]+</(MODIFIER|ModifierP)>)?<(UserDefined|ENTITY_(nounHead|nouny?|oov))>ka</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>Jew</(UserDefined|ENTITY_(nounHead|nouny?|oov))>"
    print(inputSTR)
    print()
    outputSTR = main(inputSTR)
    print(f"後處理：")
    print(outputSTR)