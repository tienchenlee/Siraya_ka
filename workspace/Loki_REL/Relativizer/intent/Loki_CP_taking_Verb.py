#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for CP_taking_Verb

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


INTENT_NAME = "CP_taking_Verb"
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
    if utterance == "PAST- say .AV NOM DET Jesus him -OBL Love .AV -IRR you .SG .NOM OBL lord ka God your .SG LOC heart your .SG ka all LOC soul your .SG ka all LOC all also OBL understand -PV your .SG think .AV":
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

    if utterance == "PAST- send.forth .AV NOM lord ka sell -IV .IRR NOM he NOM wife his NOM children his OBL all.things also ka his LOC return -PV PC. true .AV pay .AV OBL debt that":
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

    if utterance == "good .AV ka take.away -LV .IRR NOM bread OBL children throw -IV .IRR give .AV OBL it LOC dogs -LV ka little.ones":
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

    if utterance == "know -LV -we .EXCL .GEN ka righteous .AV you .SG .NOM OBL word ka teach .AV you .SG .NOM OBL road OBL God LOC truth ka what -PV .IRR you .SG .GEN NOM anyone ka people":
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

    if utterance == "not I .NOM great -PV OBL status ka enter .AV -IRR you .SG .NOM OBL roof my however PC. only .AV -IRR let.out.word .AV OBL word ka one":
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

    if utterance == "one OBL woman ka from.city .AV LOC Canaan NOM PAST- call .AV cry.out .AV him -OBL say .AV lord ka DET son GEN David compassionate .PV -IMP I .NOM":
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

    if utterance == "reply .AV -IRR NOM ruler ka chief speak.so .AV them -OBL truly .AV say .PV I .GEN you .PL .NOM insofar -LV you .PL .GEN do .AV NOM these OBL one OBL brother my these ka smallest .AV":
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

    if utterance == "reply .AV -IRR him -OBL NOM righteous .AV ka say .AV -IRR lord PAST- see -LV -we .EXCL .GEN ka when you .SG -OBL ka hungry .AV you .SG .NOM":
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

    if utterance == "PAST- send.forth .AV NOM lord ka sell -IV .IRR GEN he NOM wife his NOM children his OBL all.things also ka his LOC return -PV PC. true .AV pay .AV OBL debt that":
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

    if utterance == "urge .AV you .SG -OBL OBL God ka live .AV ka tell .AV -IRR you .SG .NOM us .EXCL -OBL whether ka DET Christ you .SG .NOM ka son OBL God":
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

    if utterance == "say .PV I .GEN you .PL .NOM FOC ka tax.collector OBL women also ka fornicate .AV PC. first .AV -IRR go .AV you .PL -OBL LOC kingdom OBL God":
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

    if utterance == "say .PV I .GEN you .PL .NOM FOC have .AV NOM some.people OBL stand .AV here ka not taste .AV -IRR OBL death LOC time until that ka see -LV .IRR -PFV they .GEN NOM son OBL man":
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

    return resultDICT


if __name__ == "__main__":
    from pprint import pprint

    resultDICT = getResult("same .AV ka cause.collect -PV NOM herb ka not good .AV", "same .AV ka cause.collect -PV NOM herb ka not good .AV", [], {}, {})
    pprint(resultDICT)