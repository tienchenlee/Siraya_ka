#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for V1_and_VP

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
import os
import re
from pathlib import Path
import sys

G_mainPath = Path(sys.argv[0]).resolve()
if G_mainPath.name in ["ka_testing.py", "ka_identifier.py"]:
    try:
        from Loki_and.Coordinator.intent.kaCaptureTool import kaCapture, getKaCharIdx, tmpAskLoki
    except:
        from .Loki_and.Coordinator.intent.kaCaptureTool import kaCapture, getKaCharIdx, tmpAskLoki
else:
    try:
        from kaCaptureTool import kaCapture, getKaCharIdx, tmpAskLoki
    except:
        from .kaCaptureTool import kaCapture, getKaCharIdx, tmpAskLoki

INTENT_NAME = "V1_and_VP"
CWD_PATH = os.path.dirname(os.path.abspath(__file__))
G_notVerbPAT = r"(?<=<UserDefined>)([a-zA-Z\-\.]{1,19})$"

with open(f"{CWD_PATH}/USER_DEFINED.json", "r", encoding="utf-8") as f:
    udDICT = json.load(f)

verbLIST = udDICT["_asVerb_"]
nounLIST = udDICT["ENTITY_noun"]

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

getResponse = getReply
def getResult(inputSTR, utterance, args, resultDICT, refDICT, pattern="", toolkitDICT={}):
    debugInfo(inputSTR, utterance)
    if utterance == "PAST- come .AV him -OBL NOM woman ka carry .AV OBL stone ka white .AV ka bottle ka have-ointment .AV ka huge .AV OBL worth ka PAST- pour .AV she .GEN NOM it":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PAST- have .AV NOM man ka PART Pharisee ka DET Nicodemus NOM name his":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PAST- lay -LV there NOM waterpot ka six ka PART stone because ka put.water -LV .IRR out.of manner OBL cleanse -PV OBL Jew ka each.one OBL those put -LV two three or OBL vessel OBL greatness ka metretes":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "come.near .AV me -OBL NOM people this OBL mouth their ka honor me -OBL OBL lips their":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)

                #<ka_capture_test>
                for i in range(0, len(args)):
                    if args[i] == "ka":
                        utterPat = re.compile(pattern)
                        kaIdx = getKaCharIdx(inputSTR=inputSTR, utterPat=utterPat, targetArgINT=i)
                        tmpInputSTR = inputSTR[:kaIdx]
                        tmpLokiResultLIST = tmpAskLoki(tmpInputSTR)
                        print(tmpInputSTR)
                        if any(tmpLokiDICT.get("results") for tmpLokiDICT in tmpLokiResultLIST):
                            if Cord:
                                resultDICT["and"].append({INTENT_NAME: True})
                                resultDICT["utterance"].append(utterance)
                        else:
                            pass
                #</ka_capture_test>

    if utterance == "greatly .AV PAST- marvel .AV NOM they ka PAST- say .AV":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "have-garden there LOC place OBL PAST- crucify -LV him -OBL ka LOC garden that NOM grave ka new .AV ka not yet PAST- place -LV NOM anyone":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "not .AV -IRR I .NOM PC. again .AV thirsty .AV ka not I .GEN come -PV .IRR":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "not we .EXCL .NOM Q good .AV OBL word ka Samaritan you .SG .NOM ka have-devil .AV you .SG .NOM":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "see -LV he .GEN NOM one ka small.tree -LV ka fig LOC side OBL road PAST- go .AV NOM he there ka not PAST- find he .GEN LOC small.tree that":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "sit .AV -IRR -PFV NOM son OBL man LOC seat OBL far.above OBL shine -PV OBL status his ka sit .AV -IRR also you .PL .NOM LOC one ten plus OBL two OBL seat":
        if CHATBOT:
            replySTR = getReply(utterance, args)
            if replySTR:
                resultDICT["response"] = replySTR
                resultDICT["source"] = "reply"
        else:
            checkLIST = []
            for arg in args:
                if not isinstance(arg, str):
                    continue

                m = re.search(G_notVerbPAT, arg)
                if m:
                    checkLIST.append(m.group(1))

            if all((word not in verbLIST) or (word in nounLIST) for word in checkLIST):
                Cord = kaCapture(args, pattern, inputSTR, resultDICT)
                if Cord:
                    resultDICT["and"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("greatly .AV PAST- marvel .AV NOM they ka PAST- say .AV", "greatly .AV PAST- marvel .AV NOM they ka PAST- say .AV", [], {}, {})
    pprint(resultDICT)