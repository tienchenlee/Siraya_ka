#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for V2

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
import logging
import json
import os
import re

INTENT_NAME = "V2"
CWD_PATH = os.path.dirname(os.path.abspath(__file__))

def import_from_path(module_name, file_path):
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

MODULE_DICT = {
    "Account": import_from_path("Coordinator_lib_Account", os.path.join(os.path.dirname(CWD_PATH), "lib/Account.py")),
    "LLM": import_from_path("Coordinator_lib_LLM", os.path.join(os.path.dirname(CWD_PATH), "lib/LLM.py"))
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
    if utterance == "anyone NOM swear .AV -IRR -PFV OBL PART gift ka PAST- put.on -PV ka debt -LV .IRR NOM he":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "anyone NOM swear .AV -IRR -PFV OBL word PC- temple .AV OBL worship -PV OBL God ka nothing NOM it":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "bind -PV they .GEN NOM burden ka heavy .AV ka not PC. able -PV carry .AV":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "cause.resemble -PV you .PL .NOM OBL graves ka whitewash -PV ka appear .AV beautiful .AV LOC surface":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "give.birth .AV -IRR OBL child ka man ka give.name -LV .IRR you .SG .GEN NOM name -IRR his Jesus":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "give.birth .AV -IRR OBL child ka man ka give.name .AV -IRR you .SG .NOM OBL name his Emmanuel":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "strain -PV you .PL .GEN NOM mosquito ka swallow -PV you .PL .GEN NOM large.animal ka camel":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "swear .AV -IRR -PFV OBL word NOM anyone OBL place OBL sacrifice -LV ka nothing NOM it":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "not PC. able -PV carry .AV ka lay.on.shoulder -PV OBL man":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "DET I NOM PAST- see .AV ka PAST- witness .AV I .NOM ka son OBL God NOM DET this FOC":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "bind -PV they .GEN NOM burden ka heavy .AV ka not PC. able -PV carry .AV ka lay.on.shoulder -PV OBL man":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0, 1]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "PAST- believe .AV we .EXCL .NOM ka PAST- understand .AV we .EXCL .NOM ka DET Christ you .SG .NOM son OBL God ka live .AV":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "PAST- PC. all .AV eat .AV ka be.satisfied .AV -PFV ka PAST- take .PV they .GEN collect OBL PAST- PC. left.over .AV OBL PART fragments":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0, 1]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "sell .AV -IRR OBL all.things your .SG ka give -LV .IRR -PFV OBL poor ka have .AV -IRR you .SG .NOM OBL treasure LOC far.above OBL heaven":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0, 1]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "PAST- PC. already .AV speak.end .AV OBL word this NOM DET Jesus ka PAST- leave .AV travel .AV LOC Galilea ka PAST- come .AV move.cross .AV OBL Jordan LOC border OBL Judea":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0, 1]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    if utterance == "when PAST- take .PV he .GEN NOM seven OBL bread OBL fish also ka when PAST- preach.return -PV he .GEN OBL praise PAST- break.into.fragments .AV ka PAST- give -LV he .GEN OBL disciple":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            targetArgLIST = [0, 1]     # 在 Loki 上為第幾個 arg
            coordinator = False

            for targetArgINT in targetArgLIST:
                if args[targetArgINT] == "ka":
                    utterPat = re.compile(pattern)
                    targetKaIdx = _getKaIdx(inputSTR, utterPat, targetArgINT)   # 找到 ka 在 inputSTR 的第幾個字
                    resultDICT["ka_index"].append(targetKaIdx)
                    coordinator = True

            if coordinator:
                resultDICT["and"].append({INTENT_NAME: True})

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("swear .AV -IRR -PFV OBL word NOM anyone OBL place OBL sacrifice -LV ka nothing NOM it", "swear .AV -IRR -PFV OBL word NOM anyone OBL place OBL sacrifice -LV ka nothing NOM it", [], {}, {})
    pprint(resultDICT)