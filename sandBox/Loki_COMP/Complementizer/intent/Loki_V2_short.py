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
import json
import os
import re
from pathlib import Path
import sys

G_mainPath = Path(sys.argv[0]).resolve()
if G_mainPath.name in ["ka_testing.py", "ka_identifier.py"]:
    try:
        from Loki_COMP.Complementizer.intent.kaCaptureTool import kaCapture
    except:
        from .Loki_COMP.Complementizer.intent.kaCaptureTool import kaCapture
else:
    try:
        from kaCaptureTool import kaCapture
    except:
        from .kaCaptureTool import kaCapture

INTENT_NAME = "V2_short"
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
    "Account": import_from_path("Complementizer_lib_Account", os.path.join(os.path.dirname(CWD_PATH), "lib/Account.py")),
    "LLM": import_from_path("Complementizer_lib_LLM", os.path.join(os.path.dirname(CWD_PATH), "lib/LLM.py"))
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
    if utterance == "PAST- allow -PV you .PL .NOM GEN Moses because OBL hardness your OBL heart ka cause.leave .AV -IRR you .PL .NOM OBL wife your .PL":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PAST- hear .AV NOM DET Jesus ka PAST- deliver .PV cause.in.prison NOM DET John PAST- return .AV be.destined .AV go .AV LOC Galilee":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "careful .AV -IRR ka not you .PL .NOM give.mercy .AV OBL merciful -PV -your .PL PC. public OBL man LOC see -PV they .GEN":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "not I .GEN you .SG .NOM Q PAST- see -LV LOC garden ka be.together .AV you .SG .NOM him -OBL":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "speak.so .AV OBL word NOM you .PL ka PAST- come .AV ka night -LV NOM disciple his":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "testify .AV you .PL .NOM PC. against .AV you .PL -OBL self .AV ka DET children you .PL .NOM their ka PAST- kill .AV OBL PART prophet":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "think .AV PC. heart .AV ka come .AV -PFV I .NOM OBL bring -PV .IRR I .GEN NOM peace LOC earth":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "understand -LV DET Jesus PC. self .AV him -OBL ka murmur .AV because OBL this NOM disciple his":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "want .AV you .PL .NOM Q ka release -PV .IRR I .GEN you .PL .NOM NOM ruler ka chief OBL Jew":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "who NOM PAST- understand .AV accept .AV OBL testify -PV he .GEN PAST- seal .PV PC. surely .AV ka true .AV OBL word NOM God":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "see -LV GEN Herod ka PAST- deceive .AV him -OBL NOM wise observe":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "know -PV I .GEN ka life ka always .AV be.lasting .AV NOM command -PV he .GEN":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "So.much.so .AV ka PAST- marvel .AV NOM multitudes while see -LV they .GEN ka speak .AV NOM dumb .AV":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    if utterance == "PAST- allow -PV you .PL GEN Moses because OBL hardness your OBL heart ka cause.leave .AV -IRR you .PL .NOM OBL wife your .PL":
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
                COMP = kaCapture(args, pattern, inputSTR, resultDICT)
                if COMP:
                    resultDICT["COMP"].append({INTENT_NAME: True})
                    resultDICT["utterance"].append(utterance)

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("speak.truly you .SG .NOM ka king I .NOM ka chief", "speak.truly you .SG .NOM ka king I .NOM ka chief", [], {}, {})
    pprint(resultDICT)