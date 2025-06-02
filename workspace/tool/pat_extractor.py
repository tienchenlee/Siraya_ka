#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import json

udPAT = re.compile(r"<\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>([A-Z\-\.]+|ka)</\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>")
nounPAT = re.compile(r"<\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>([a-z]+|[A-Z][a-z]+)</\(UserDefined\|ENTITY_\(nounHead\|nouny\?\|oov\)\)>")

def main(udDICT, inputSTR):
    """
    刪減 "ka" 或是全大寫字 (e.g. "OBL") 的 tags (e.g. "|ENTITY_(nounHead|nouny?|oov))", "|VerbP)")。
    
    參數：
    - inputSTR (str): 輸入字串 (patterns from Loki)。
    
    回傳：
    - outputSTR (str): 處理後的輸出字串。
    """
    
    outputSTR = inputSTR            
    if re.search(udPAT, inputSTR):
        # 刪減 ENTITY & VerbP & ModifierP
        outputSTR = re.sub(udPAT, r"<UserDefined>(\1)</UserDefined>", outputSTR)
        outputSTR = outputSTR.replace("|VerbP)", "").replace("(ACTION_verb", "ACTION_verb")
        outputSTR = outputSTR.replace("|ModifierP)", "").replace("(MODIFIER", "MODIFIER")
        
    for verbSTR in udDICT["_asVerb_"]:
        if verbSTR in outputSTR:
            outputSTR = outputSTR.replace("(UserDefined|ENTITY_(nounHead|nouny?|oov))", "UserDefined").replace("/(UserDefined|ENTITY_(nounHead|nouny?|oov))", "/UserDefined")
        
    if re.search(nounPAT, inputSTR):
        outputSTR = re.sub(nounPAT, r"<ENTITY_[^>]+>\1</ENTITY_[^>]+>", outputSTR)
        
            
    
    return outputSTR


if __name__ == "__main__":
    udDICT = "../../corpus/USER_DEFINED.json"
    with open(udDICT, "r", encoding="utf-8") as f:
        udDICT = json.load(f)
    
    inputSTR = "<(UserDefined|ENTITY_(nounHead|nouny?|oov))>PAST-</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(ACTION_verb|VerbP)>hear</(ACTION_verb|VerbP)><(UserDefined|ENTITY_(nounHead|nouny?|oov))>-PV</(UserDefined|ENTITY_(nounHead|nouny?|oov))>(<ENTITY_pronoun>[^<]+</ENTITY_pronoun>)?<(UserDefined|ENTITY_(nounHead|nouny?|oov))>PL</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>GEN</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>ka</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>PAST-</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(ACTION_verb|VerbP)>cause.appear</(ACTION_verb|VerbP)><(UserDefined|ENTITY_(nounHead|nouny?|oov))>-LV</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>OBL</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>word</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(UserDefined|ENTITY_(nounHead|nouny?|oov))>OBL</(UserDefined|ENTITY_(nounHead|nouny?|oov))><(ACTION_verb|VerbP)>PART</(ACTION_verb|VerbP)>(<(MODIFIER|ModifierP)>[^<]+</(MODIFIER|ModifierP)>)?<(UserDefined|ENTITY_(nounHead|nouny?|oov))>-LV</(UserDefined|ENTITY_(nounHead|nouny?|oov))>"
    outputSTR = main(udDICT, inputSTR)
    print(outputSTR)