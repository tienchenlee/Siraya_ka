#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for V2_and_VP_and_VP

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

INTENT_NAME = "V2_and_VP_and_VP"
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
    if utterance == "DET I NOM PAST- choose .AV you .PL -OBL ka PAST- order -PV I .GEN you .PL .NOM ka go -LV .IRR you ,PL .GEN bear.fruit .AV ka dwell .AV -IRR also NOM fruit your .PL":
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

    if utterance == "OBL two those NOM PAST- send.forth -PV GEN Jesus ka PAST- command .AV them -OBL say .PV not you .PL .NOM go .AV -IRR LOC road OBL heathen ka not you .PL .NOM enter .AV -IRR LOC cities OBL Samaritan":
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

    if utterance == "PAST- PC. all .AV eat .AV ka be.satisfied .AV -PFV ka PAST- take .PV they .GEN collect OBL PAST- PC. left.over .AV OBL PART fragments":
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

    if utterance == "PAST- PC. already .AV speak.end .AV OBL word this NOM DET Jesus ka PAST- leave .AV travel .AV LOC Galilea ka PAST- come .AV move.cross .AV OBL Jordan LOC border OBL Judea":
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

    if utterance == "PAST- pour.out -PV he .GEN NOM water LOC basin.for.foot.washing ka PAST- wash.foot .AV OBL foot OBL disciple ka PAST- dry .AV also OBL towel ka girdle -LV he .GEN":
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

    if utterance == "bind -PV they .GEN NOM burden ka heavy .AV ka not PC. able -PV carry .AV ka lay.on.shoulder -PV OBL man":
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

    if utterance == "break .AV -IRR NOM leather.bag ka let.shed -PV NOM wine ka perish .AV NOM leather.bag":
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

    if utterance == "have .AV NOM someone OBL man one hundred OBL sheep ka when go.astray .AV -PFV or OBL one OBL these not Q cause.stay -LV .IRR he .GEN NOM nine ten plus OBL nine ka when go.into.mountain .AV not Q seek .AV -IRR OBL go.astray .AV -PFV that":
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

    if utterance == "sell .AV -IRR OBL all.things your .SG ka give -LV .IRR -PFV OBL poor ka have .AV -IRR you .SG .NOM OBL treasure LOC far.above OBL heaven":
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

    if utterance == "send.forth .AV NOM other OBL servant ka PAST- say .AV tell -LV .IRR NOM PAST- drink.prepare -PV tell .AV see -LV .IRR PAST- prepare .PV I .GEN NOM dinner -PV .IRR my PAST- kill .PV NOM large.animal my ka PAST- castrate .PV OBL PAST- fatling .PV also ka large.animal ka PAST- PC. all .AV PC. already .AV prepare .AV":
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

    if utterance == "when PAST- take .PV he .GEN NOM seven OBL bread OBL fish also ka when PAST- preach.return -PV he .GEN OBL praise PAST- break.into.fragments .AV ka PAST- give -LV he .GEN OBL disciple":
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

    resultDICT = getResult("break .AV -IRR NOM leather.bag ka let.shed -PV NOM wine ka perish .AV NOM leather.bag", "break .AV -IRR NOM leather.bag ka let.shed -PV NOM wine ka perish .AV NOM leather.bag", [], {}, {})
    pprint(resultDICT)