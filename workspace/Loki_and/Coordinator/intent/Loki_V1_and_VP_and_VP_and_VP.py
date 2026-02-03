#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for V1_and_VP_and_VP_and_VP

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
        from Loki_and.Coordinator.intent.kaCaptureTool import kaCapture
    except:
        from .Loki_and.Coordinator.intent.kaCaptureTool import kaCapture
else:
    try:
        from kaCaptureTool import kaCapture
    except:
        from .kaCaptureTool import kaCapture

INTENT_NAME = "V1_and_VP_and_VP_and_VP"
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
    if utterance == "Come .AV -PFV NOM son OBL man ka eat .AV ka drink .AV ka say .PV they .GEN FOC see -LV .IRR NOM man ka gluttonous .AV ka alcoholist friend OBL tax.collector OBL sinner also":
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

    if utterance == "PAST- come.down .AV NOM torrential.rain ka PAST- come .AV NOM flood PAST- blow .AV NOM wind ka PAST- beat .AV OBL house that ka not PAST- fall .AV FOC":
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

    if utterance == "dark -LV .IRR NOM sun ka not clean .AV -IRR NOM moon ka move.down .AV -IRR from-heaven .AV NOM stars ka move -LV .IRR NOM power OBL far.above OBL heaven":
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

    if utterance == "dwell .AV you .PL .NOM me -OBL ka when dwell .AV you .PL -OBL NOM word my ka things ka want -LV .IRR you .PL .GEN ask -PV .IRR -PFV ka do -LV .IRR you .PL -OBL":
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

    if utterance == "many .AV NOM multitudes ka PAST- come .AV him -OBL ka PAST- cause.be.with .AV them -OBL OBL cripple .AV OBL blind .AV OBL dumb .AV OBL maimed .AV OBL other also ka many .AV OBL man ka PAST- throw .AV them -OBL at.front .AV LOC foot GEN Jesus ka PAST- heal -PV NOM they":
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

    if utterance == "tell .AV OBL disciple his ka must -PFV OBL leave -LV .IRR he .GEN go .AV LOC Jerusalem ka endure .AV -IRR OBL many .AV them -OBL ka elder OBL people ka chief ka priest ka scribe ka kill -PV .IRR ka cause.wake -LV .IRR also LOC third OBL day":
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

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("PAST- come.down .AV NOM torrential.rain ka PAST- come .AV NOM flood PAST- blow .AV NOM wind ka PAST- beat .AV OBL house that ka not PAST- fall .AV FOC", "PAST- come.down .AV NOM torrential.rain ka PAST- come .AV NOM flood PAST- blow .AV NOM wind ka PAST- beat .AV OBL house that ka not PAST- fall .AV FOC", [], {}, {})
    pprint(resultDICT)