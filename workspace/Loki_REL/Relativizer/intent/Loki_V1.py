#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for V1

    Input:
        inputSTR      str,
        utterance     str,
        args          str[],
        resultDICT    dict,
        refDICT       dict,
        pattern       str

    Output:
        resultDICT    dict
"""

from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from random import sample
import json
import logging
import os
import re

INTENT_NAME = "V1"
CWD_PATH = os.path.dirname(os.path.abspath(__file__))

def import_from_path(module_name, file_path):
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

MODULE_DICT = {
    "Account": import_from_path("Relativizer_lib_Account", os.path.join(os.path.dirname(CWD_PATH), "lib/Account.py")),
    "LLM": import_from_path("Relativizer_lib_LLM", os.path.join(os.path.dirname(CWD_PATH), "lib/LLM.py"))
}
"""
Account Variables
[Variable] BASE_PATH         => path of root
[Variable] LIB_PATH          => path of lib folder
[Variable] INTENT_PATH       => path of intent folder
[Variable] REPLY_PATH        => path of reply folder
[Variable] ACCOUNT_DICT      => account.info
[Variable] ARTICUT           => ArticutAPI (Usage: ARTICUT.parse()。 #ArticutAPI Required.)
[Variable] USER_DEFINED_FILE => path of UserDefined
[Variable] USER_DEFINED_DICT => UserDefined data
"""
REPLY_PATH = MODULE_DICT["Account"].REPLY_PATH
ACCOUNT_DICT = MODULE_DICT["Account"].ACCOUNT_DICT
ARTICUT = MODULE_DICT["Account"].ARTICUT
USER_DEFINED_FILE = MODULE_DICT["Account"].USER_DEFINED_FILE
USER_DEFINED_DICT = MODULE_DICT["Account"].USER_DEFINED_DICT
getLLM = MODULE_DICT["LLM"].getLLM

# userDefinedDICT (Deprecated)
# Replace with USER_DEFINED_DICT of Account variable.
#userDefinedDICT = {}
#try:
#    userDefinedDICT = json.load(open(os.path.join(CWD_PATH, "USER_DEFINED.json"), encoding="utf-8"))
#except:
#    pass

replyDICT = {}
replyPathSTR = os.path.join(REPLY_PATH, "reply_{}.json".format(INTENT_NAME))
if os.path.exists(replyPathSTR):
    try:
        replyDICT = json.load(open(replyPathSTR, encoding="utf-8"))
    except Exception as e:
        print("[ERROR] reply_{}.json => {}".format(INTENT_NAME, str(e)))
CHATBOT = True if replyDICT else False

# Debug message
def debugInfo(inputSTR, utterance):
    if ACCOUNT_DICT["debug"]:
        print("[{}] {} ===> {}".format(INTENT_NAME, inputSTR, utterance))

def getReply(utterance, args):
    replySTR = ""
    try:
        replySTR = sample(replyDICT[utterance], 1)[0]
        if args:
            replySTR = replySTR.format(*args)
    except:
        pass

    return replySTR

def _getKaIdx(inputSTR, utterPat, targetArgINT):
    """
    1. Articut inputSTR
    2. Get the string that before the target 'ka'
    3. Count the index of 'ka'
    4. Return the index
    """
    engArticut = ARTICUT.parse(inputSTR, USER_DEFINED_FILE)
    if engArticut["status"] == True:
        inputPosSTR = engArticut["result_pos"][0].replace(" ", "")

    kaIdxLIST = []

    for k_t in [(k.start(targetArgINT+1), k.end(targetArgINT+1), k.group(targetArgINT+1)) for k in utterPat.finditer(inputPosSTR)]:
        kaIdxLIST.append(k_t)

    if kaIdxLIST:
        targetKaIdx = inputPosSTR[:kaIdxLIST[0][0]].count("</")
        # 一個字會被 articut 切成兩個字
        if re.search(r"<MODAL>do</MODAL><FUNC_negation>not</FUNC_negation>.*?<UserDefined>ka</UserDefined>", inputPosSTR):
            targetKaIdx -= 1
    else:
        logging.error(f"找不到 kaIdxLIST: {inputSTR}")
        return -1

    return targetKaIdx

getResponse = getReply
def getResult(inputSTR, utterance, args, resultDICT, refDICT, pattern="", toolkitDICT={}):
    debugInfo(inputSTR, utterance)
    if utterance == "PAST- fulfill .PV NOM word ka PART preaching OBL prophet ka DET Jeremy":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [2]     # 在 Loki 上為第幾個 arg
            REL = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    REL = True

            if REL:
                resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "PAST- joyful .AV NOM they OBL joy ka exceeding .AV great .AV":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [2, 3]     # 在 Loki 上為第幾個 arg
            REL = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    REL = True

            if REL:
                resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "he NOM DET this ka PAST- speak -PV OBL prophecy":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [1, 3, 4]     # 在 Loki 上為第幾個 arg
            REL = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    REL = True

            if REL:
                resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "many .AV OBL Jew ka come .AV -PFV DET Mary -OBL":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [2]     # 在 Loki 上為第幾個 arg
            REL = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    REL = True

            if REL:
                resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "PAST- come .AV DET Jesus -OBL NOM scribe OBL Pharisee and ka PAST- from-Jerusalem .AV":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [2]     # 在 Loki 上為第幾個 arg
            REL = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    REL = True

            if REL:
                resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "you .PL ka different -PV OBL heart OBL word good .AV NOM PAST- prophesize -PV DET Isaiah you .PL -OBL":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [1]     # 在 Loki 上為第幾個 arg
            REL = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    REL = True

            if REL:
                resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "PAST- come .AV LOC land ka Gennesaret":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [1]     # 在 Loki 上為第幾個 arg
            REL = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    REL = True

            if REL:
                resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "they FOC ka in.boat .AV PAST- come .AV worship .AV him -OBL":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [1]     # 在 Loki 上為第幾個 arg
            REL = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    REL = True

            if REL:
                resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "he ka sow .AV OBL seed ka good .AV he NOM son OBL man":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [1, 2]     # 在 Loki 上為第幾個 arg
            REL = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    REL = True

            if REL:
                resultDICT["REL"].append({INTENT_NAME: True})

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("he NOM DET this ka PAST- speak -PV OBL prophecy", "he NOM DET this ka PAST- speak -PV OBL prophecy", [], {}, {})
    pprint(resultDICT)