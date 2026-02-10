#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for V1_AV

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
        from Loki_REL.Relativizer.intent.kaCaptureTool import kaCapture
    except:
        from .Loki_REL.Relativizer.intent.kaCaptureTool import kaCapture
else:
    try:
        from kaCaptureTool import kaCapture
    except:
        from .kaCaptureTool import kaCapture


INTENT_NAME = "V1_AV"
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

getResponse = getReply
def getResult(inputSTR, utterance, args, resultDICT, refDICT, pattern="", toolkitDICT={}):
    debugInfo(inputSTR, utterance)
    if utterance == "NOM DET Jesus walk .AV PC. top .AV OBL water ka LOC sea":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PAST- come .AV DET Jesus -OBL NOM scribe OBL Pharisee and ka PAST- from-Jerusalem .AV":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PAST- come .AV LOC land ka Gennesaret":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PAST- joyful .AV NOM they OBL joy ka exceeding .AV great .AV":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "again .AV speak -PV I .GEN you .PL .NOM if agree .AV OBL heart NOM two OBL man you .PL -OBL LOC earth because OBL anything ka request -PV .IRR they .GEN permit -LV .IRR them -OBL OBL father my ka LOC far.above OBL heaven":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "go .AV him -OBL NOM Jerusalem all-inclusive also NOM Judea all also OBL one region ka LOC vicinity OBL Jordan":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "many .AV OBL Jew ka come .AV -PFV DET Mary -OBL":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "what NOM PC. more .AV worthy .AV OBL status gold Q temple Q ka cause.distinct .AV OBL gold LOC worship -PV OBL God":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PAST- joyful .AV they OBL joy ka exceeding .AV great .AV":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "be.appearing .AV -IRR OBL man same .AV OBL fast .AV FOC OBL father .LV instead you .SG ka in.darkness .AV":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "come .AV NOM ruler ka chief you .SG -OBL be.on.back LOC youngling OBL large.animal ka female ka carry.on.back":
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
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("PAST- come .AV LOC land ka Gennesaret", "PAST- come .AV LOC land ka Gennesaret", [], {}, {})
    pprint(resultDICT)