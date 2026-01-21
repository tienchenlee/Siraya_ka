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
from pathlib import Path
import sys

G_mainPath = Path(sys.argv[0]).resolve()
if G_mainPath.name == "ka_testing.py":
    try:
        from Loki_REL.Relativizer.intent.kaCaptureTool import kaCapture
    except:
        from .Loki_REL.Relativizer.intent.kaCaptureTool import kaCapture
else:
    try:
        from kaCaptureTool import kaCapture
    except:
        from .kaCaptureTool import kaCapture


INTENT_NAME = "V1_and_VP"
CWD_PATH = os.path.dirname(os.path.abspath(__file__))
G_notVerbPAT = r"(?<=<UserDefined>)([a-zA-Z\-\.]{1,19})$"

with open(f"{CWD_PATH}/USER_DEFINED.json", "r", encoding="utf-8") as f:
    udDICT = json.load(f)

verbLIST = udDICT["_asVerb_"]

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
    if utterance == "PAST- come .AV NOM man ka new ka they ka PAST- prepare PAST- be.together him -OBL enter .AV":
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

            if checkLIST and all(word not in verbLIST for word in checkLIST):
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "PAST- fall .AV NOM some LOC stony.place ka PC. few .AV have.soil .AV ka PAST- spring.up .AV NOM those grow .AV because ka not.have OBL deep .AV ka earth FOC":
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

            if checkLIST and all(word not in verbLIST for word in checkLIST):
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "PAST- marvel .AV FOC ka PAST- say .AV them -OBL ka follow .AV him -OBL":
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

            if checkLIST and all(word not in verbLIST for word in checkLIST):
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "cry .AV -IRR while that NOM all.inclusive OBL tribes OBL earth ka see .AV -IRR OBL son OBL man while come .AV LOC clouds OBL heaven LOC power OBL greatness OBL status ka huge .AV":
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

            if checkLIST and all(word not in verbLIST for word in checkLIST):
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "he ka PAST- PC. five .AV OBL talent PAST- come .AV bring .AV OBL five still ka other OBL talent ka PAST- say .PV he .GEN lord five OBL talent ka PAST- give -PV you .SG .GEN me -OBL see -LV .IRR five still ka other OBL talent ka PAST- PC. more .PV I .NOM make.profit .AV OBL it":
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

            if checkLIST and all(word not in verbLIST for word in checkLIST):
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "many .AV NOM multitudes ka PAST- come .AV him -OBL ka PAST- cause.be.with .AV them -OBL OBL cripple .AV OBL blind .AV OBL dumb .AV OBL maimed .AV OBL other also ka many .AV OBL man":
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

            if checkLIST and all(word not in verbLIST for word in checkLIST):
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    if utterance == "rise .AV -IRR NOM many .AV ka false-Christ ka false-prophet ka do .AV -IRR OBL sign ka great .AV OBL DET PART also OBL marvel -PV":
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

            if checkLIST and all(word not in verbLIST for word in checkLIST):
                REL = kaCapture(args, pattern, inputSTR, resultDICT)
                if REL:
                    resultDICT["REL"].append({INTENT_NAME: True})

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("PAST- marvel .AV FOC ka PAST- say .AV them -OBL ka follow .AV him -OBL", "PAST- marvel .AV FOC ka PAST- say .AV them -OBL ka follow .AV him -OBL", [], {}, {})
    pprint(resultDICT)