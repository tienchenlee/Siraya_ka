#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki 4.0 Template For Python3

    [URL] https://nlu.droidtown.co/Loki_EN/BulkAPI/

    Request:
        {
            "username": "your_username",
            "input_list": ["your_input_1", "your_input_2"],
            "loki_key": "your_loki_key",
            "filter_list": ["intent_filter_list"] # optional
        }

    Response:
        {
            "status": True,
            "msg": "Success!",
            "version": "v223",
            "result_list": [
                {
                    "status": True,
                    "msg": "Success!",
                    "results": [
                        {
                            "intent": "intentName",
                            "pattern": "matchPattern",
                            "utterance": "matchUtterance",
                            "argument": ["arg1", "arg2", ... "argN"]
                        },
                        ...
                    ]
                },
                {
                    "status": False,
                    "msg": "No matching intent."
                }
            ]
        }
"""

from copy import deepcopy
from glob import glob
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from pathlib import Path
from requests import codes
from requests import get
from requests import post
import math
import os
import re

def import_from_path(module_name, file_path):
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

PROJECT_NAME = "Relativizer"
CWD_PATH = os.path.dirname(os.path.abspath(__file__))
MODULE_DICT = {
    "Account": import_from_path("{}_lib_Account".format(PROJECT_NAME), os.path.join(CWD_PATH, "Account.py")),
    "ChatbotMaker": import_from_path("{}_lib_ChatbotMaker".format(PROJECT_NAME), os.path.join(CWD_PATH, "ChatbotMaker.py")),
    "LLM": import_from_path("{}_lib_LLM".format(PROJECT_NAME), os.path.join(CWD_PATH, "LLM.py")),
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
INTENT_PATH = MODULE_DICT["Account"].INTENT_PATH
ACCOUNT_DICT = MODULE_DICT["Account"].ACCOUNT_DICT
ARTICUT = MODULE_DICT["Account"].ARTICUT
USER_DEFINED_FILE = MODULE_DICT["Account"].USER_DEFINED_FILE
USER_DEFINED_DICT = MODULE_DICT["Account"].USER_DEFINED_DICT
COLOR_DICT = MODULE_DICT["ChatbotMaker"].COLOR_DICT
setColor = MODULE_DICT["ChatbotMaker"].setColor
callLLM = MODULE_DICT["LLM"].callLLM
getCosineSimilarityUtterance = MODULE_DICT["LLM"].getCosineSimilarityUtterance

lokiIntentDICT = {}
for modulePath in glob("{}/Loki_*.py".format(INTENT_PATH)):
    moduleNameSTR = Path(modulePath).stem[5:]
    lokiIntentDICT[moduleNameSTR] = import_from_path("{}_intent_{}".format(PROJECT_NAME, moduleNameSTR), modulePath)

# Filter descrption
# INTENT_FILTER = []        => All intents (Default)
# INTENT_FILTER = [intentN] => Only use intent of INTENT_FILTER
INTENT_FILTER = []
INPUT_LIMIT = 20


class LokiResult():
    status = False
    message = ""
    version = ""
    balance = -1
    lokiResultLIST = []

    def __init__(self, inputLIST, filterLIST):
        self.status = False
        self.message = ""
        self.version = ""
        self.balance = -1
        self.lokiResultLIST = []
        # Default: INTENT_FILTER
        if filterLIST == []:
            filterLIST = INTENT_FILTER

        try:
            url = "{}/Loki_EN/BulkAPI/".format(ACCOUNT_DICT["server"])
            if url == "https://nlu.droidtown.co":
                result = post(url, json={
                    "username": ACCOUNT_DICT["username"],
                    "input_list": inputLIST,
                    "loki_key": ACCOUNT_DICT["loki_key"],
                    "filter_list": filterLIST
                })
            else:
                result = post(url, json={
                                "username": ACCOUNT_DICT["username"],
                                "input_list": inputLIST,
                                "loki_key": ACCOUNT_DICT["loki_key"],
                                "project": ACCOUNT_DICT["loki_project"],
                                "user_defined_dict_file": USER_DEFINED_DICT,
                                "filter_list": filterLIST
                            })

            if result.status_code == codes.ok:
                result = result.json()
                self.status = result["status"]
                self.message = result["msg"]
                if result["status"]:
                    self.version = result["version"]
                    if "word_count_balance" in result:
                        self.balance = result["word_count_balance"]
                    self.lokiResultLIST = result["result_list"]
            else:
                self.message = "{} Connection failed.".format(result.status_code)
        except Exception as e:
            self.message = str(e)

    def getStatus(self):
        return self.status

    def getMessage(self):
        return self.message

    def getVersion(self):
        return self.version

    def getBalance(self):
        return self.balance

    def getLokiStatus(self, index):
        rst = False
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["status"]
        return rst

    def getLokiMessage(self, index):
        rst = ""
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["msg"]
        return rst

    def getLokiLen(self, index):
        rst = 0
        if index < len(self.lokiResultLIST):
            if self.lokiResultLIST[index]["status"]:
                rst = len(self.lokiResultLIST[index]["results"])
        return rst

    def getLokiResult(self, index, resultIndex):
        lokiResultDICT = None
        if resultIndex < self.getLokiLen(index):
            lokiResultDICT = self.lokiResultLIST[index]["results"][resultIndex]
        return lokiResultDICT

    def getIntent(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["intent"]
        return rst

    def getPattern(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["pattern"]
        return rst

    def getUtterance(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["utterance"]
        return rst

    def getArgs(self, index, resultIndex):
        rst = []
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["argument"]
        return rst

def runLoki(inputLIST, filterLIST=[], refDICT={}, toolkitDICT={}):
    resultDICT = deepcopy(refDICT)
    lokiRst = LokiResult(inputLIST, filterLIST)
    if lokiRst.getStatus():
        for index, key in enumerate(inputLIST):
            lokiResultDICT = {k: [] for k in refDICT}
            for resultIndex in range(0, lokiRst.getLokiLen(index)):
                if lokiRst.getIntent(index, resultIndex) in lokiIntentDICT:
                    lokiResultDICT = lokiIntentDICT[lokiRst.getIntent(index, resultIndex)].getResult(
                        key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex),
                        lokiResultDICT, refDICT, pattern=lokiRst.getPattern(index, resultIndex), toolkitDICT=toolkitDICT)

            # save lokiResultDICT to resultDICT
            for k in lokiResultDICT:
                if k not in resultDICT:
                    resultDICT[k] = []
                if type(resultDICT[k]) != list:
                    resultDICT[k] = [resultDICT[k]] if resultDICT[k] else []
                if type(lokiResultDICT[k]) == list:
                    resultDICT[k].extend(lokiResultDICT[k])
                else:
                    resultDICT[k].append(lokiResultDICT[k])
    else:
        resultDICT["msg"] = lokiRst.getMessage()
    return resultDICT

def execLoki(content, filterLIST=[], splitLIST=[], refDICT={}, toolkitDICT={}):
    resultDICT = deepcopy(refDICT)
    if resultDICT is None:
        resultDICT = {}

    contentLIST = []
    if type(content) == str:
        contentLIST = [content]
    if type(content) == list:
        contentLIST = content

    if contentLIST:
        if splitLIST:
            # split by splitLIST
            splitPAT = re.compile("[{}]".format("".join(splitLIST)))
            inputLIST = []
            for c in contentLIST:
                tmpLIST = splitPAT.split(c)
                inputLIST.extend(tmpLIST)
            # remove empty
            while "" in inputLIST:
                inputLIST.remove("")
        else:
            # don't split
            inputLIST = contentLIST

        # batch with limitation of INPUT_LIMIT
        for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
            resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST=filterLIST, refDICT=resultDICT, toolkitDICT=toolkitDICT)
            if "msg" in resultDICT:
                break

    if ACCOUNT_DICT["chatbot_mode"]:
        if "response" not in resultDICT:
            resultDICT["response"] = []
        if "source" not in resultDICT:
            resultDICT["source"] = []

        for i, content in enumerate(contentLIST):
            if i < len(resultDICT["response"]) and resultDICT["response"][i]:
                responseSTR = resultDICT["response"][i]
                sourceSTR = "reply"
            else:
                responseSTR = ""
                if ACCOUNT_DICT["utterance_count"]:
                    scoreDICT = getCosineSimilarityUtterance(content, ACCOUNT_DICT["utterance_count"])
                    if scoreDICT["utterance"] and scoreDICT["score"] >= ACCOUNT_DICT["utterance_threshold"]:
                        responseSTR = lokiIntentDICT[scoreDICT["intent"]].getReply(scoreDICT["utterance"], [])
                        if responseSTR:
                            responseSTR = "Do you mean「{}」?\n{}".format(scoreDICT["utterance"], responseSTR)
                            sourceSTR = "SIM_reply"

                if not responseSTR:
                    responseSTR, sourceSTR = callLLM(content)

            if i < len(resultDICT["response"]):
                resultDICT["response"][i] = responseSTR
            else:
                resultDICT["response"].append(responseSTR)

            if i < len(resultDICT["source"]):
                resultDICT["source"][i] = sourceSTR
            else:
                resultDICT["source"].append(sourceSTR)

    return resultDICT

def cosSimilarLoki(content, splitLIST=[], featureLIST=[]):
    resultDICT = {}

    contentLIST = []
    if type(content) == str:
        contentLIST = [content]
    if type(content) == list:
        contentLIST = content

    if not featureLIST:
        featureLIST = ACCOUNT_DICT["utterance_feature"]

    if contentLIST:
        inputLIST = []
        if splitLIST:
            # split by splitLIST
            splitPAT = re.compile("[{}]".format("".join(splitLIST)))
            for c in contentLIST:
                tmpLIST = splitPAT.split(c)
                inputLIST.extend(tmpLIST)
            # remove empty
            while "" in inputLIST:
                inputLIST.remove("")
        else:
            # don't split
            inputLIST = contentLIST

        for inputSTR in inputLIST:
            inputSTR = inputSTR.strip()
            scoreDICT = getCosineSimilarityUtterance(inputSTR, ACCOUNT_DICT["utterance_count"])
            if scoreDICT["intent"] and scoreDICT["score"] >= ACCOUNT_DICT["utterance_threshold"]:
                if scoreDICT["intent"] not in resultDICT:
                    resultDICT[scoreDICT["intent"]] = {}
                resultDICT[scoreDICT["intent"]][inputSTR] = {
                    "utterance": scoreDICT["utterance"],
                    "score": scoreDICT["score"]
                }

    return resultDICT

def testLoki(inputLIST, filterLIST):
    for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
        resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST)

    return resultDICT

def testIntent():
    from pprint import pprint

    # Phrase
    print("[TEST] Phrase")
    inputLIST = ['woe OBL man ka cause.come .AV OBL offend -PV cause.sin','woe you .PL ka scribe OBL Pharisees also ka different -PV OBL heart OBL word','woe you .PL ka scribe OBL Pharisee also ka different -PV OBL heart OBL word give you .PL .NOM OBL part ka one ten OBL mint OBL dill OBL cumin also']
    pprint(testLoki(inputLIST, ['Phrase']))
    print("")

    # V1_AV_RC4
    print("[TEST] V1_AV_RC4")
    inputLIST = ['LOC time until that ka go.past .AV -IRR NOM heaven OBL earth not go.past .AV -IRR NOM jot ka one OBL tittle also ka one OBL law LOC time until that ka PC. already -PV .IRR do NOM all OBL things FOC','speak.so .AV .IRR .also OBL word them -OBL ka at.left .AV depart .AV -IRR me -OBL you .PL ka PAST- curse -PV go .AV LOC fire ka always .AV be.lasting .AV ka PAST- prepare -PV OBL belong-devil .AV -IRR OBL angel also his','speak.so .AV .IRR .also OBL word NOM ruler ka chief them -OBL ka at .AV LOC right his come .AV here NOM you .PL ka PAST- bless -PV you .PL .NOM OBL word OBL father my inherit .AV -PFV OBL kingdom ka PAST- prepare -PV you .PL -OBL from time OBL PAST- put.foundation -PV NOM basis OBL world']
    pprint(testLoki(inputLIST, ['V1_AV_RC4']))
    print("")

    # TopNP_V1
    print("[TEST] TopNP_V1")
    inputLIST = ['anyone NOM swear .AV -IRR -PFV PC- gold .AV ka LOC temple','they FOC ka in.boat .AV PAST- come .AV worship .AV him -OBL','they ka PAST- sit .AV LOC land LOC shadow also OBL death PAST- rise -LV OBL light them .OBL','you .PL ka different -PV OBL heart OBL word good .AV NOM PAST- prophesize -PV DET Isaiah you .PL -OBL']
    pprint(testLoki(inputLIST, ['TopNP_V1']))
    print("")

    # clauseQ
    print("[TEST] clauseQ")
    inputLIST = ['what NOM word ka commandment OBL great -PV LOC law','what -IRR we .EXCL you .SG also Jesus ka son OBL God','where NOM PAST- give.birth .PV ka chief ka ruler OBL Jew']
    pprint(testLoki(inputLIST, ['clauseQ']))
    print("")

    # Nominal_Predicate_RC6
    print("[TEST] Nominal_Predicate_RC6")
    inputLIST = ['he NOM DET John ka PAST- have .AV OBL clothing his ka PART hair OBL large.animal ka have.back .AV ka camel call .AV OBL girdle also ka PART leather ka PAST- gird .AV OBL loins his']
    pprint(testLoki(inputLIST, ['Nominal_Predicate_RC6']))
    print("")

    # V3_NAV
    print("[TEST] V3_NAV")
    inputLIST = ['speak -LV .IRR I .GEN OBL man ka harvest .AV -IRR','PAST- bring .PV they .GEN cause.come .AV him -OBL NOM all ka sick .AV','PAST- bring .PV they .GEN him -OBL NOM gift ka gold scent ka incense scent also ka myrrh','two you .SG .NOM OBL hand or both OBL foot or cast -IV .IRR -PFV cast.into .AV LOC fire ka always .AV be.lasting .AV']
    pprint(testLoki(inputLIST, ['V3_NAV']))
    print("")

    # V1_and_VP_and_VP
    print("[TEST] V1_and_VP_and_VP")
    inputLIST = ['many .AV NOM come .AV -IRR LOC name my ka say .AV -IRR DET I NOM DET Christ ka deceive -PV .IRR they .GEN NOM people ka many .AV','shine -PV .IRR so .AV NOM light your .PL LOC openness OBL people ka see .AV -IRR OBL PART work your .PL ka good .AV ka make.great .AV -IRR also OBL status OBL father your .PL ka LOC far.above OBL heaven']
    pprint(testLoki(inputLIST, ['V1_and_VP_and_VP']))
    print("")

    # Nominal_Predicate
    print("[TEST] Nominal_Predicate")
    inputLIST = ['one NOM master you .PL -OBL ka DET Christ','he NOM DET this ka PAST- speak -PV OBL prophecy','he ka sow .AV OBL seed ka good .AV he NOM son OBL man']
    pprint(testLoki(inputLIST, ['Nominal_Predicate']))
    print("")

    # V1_NAV
    print("[TEST] V1_NAV")
    inputLIST = ['they ka PAST- eat .AV PART four -PFV thousand OBL young.men','PAST- fulfill .PV NOM word ka PART preaching OBL prophet ka DET Jeremy','what PC. more .AV PART great -PV OBL status PART gift Q place Q OBL cause.sacrifice -LV ka cause.distinct .AV OBL PART gift LOC worship -PV OBL God']
    pprint(testLoki(inputLIST, ['V1_NAV']))
    print("")

    # V2_AV_RC2
    print("[TEST] V2_AV_RC2")
    inputLIST = ['same .AV -IRR NOM kingdom OBL farabove OBL heaven OBL one ten OBL girls ka when PAST- take .PV they .GEN NOM lamp their PAST- go.out .AV meet .AV OBL man ka new','PAST- say .AV NOM ruler ka chief OBL servant his bind.hand -LV .IRR bind.foot -LV .IRR take -PV .IRR throw -IV .IRR him -OBL LOC darkness ka most .AV far.away .AV','not you .PL .NOM see .AV -IRR me -OBL after .AV OBL time now LOC time until that ka speak -LV .IRR you .PL .GEN bless -LV .IRR praise .AV NOM he that ka come .AV LOC name OBL lord']
    pprint(testLoki(inputLIST, ['V2_AV_RC2']))
    print("")

    # V2_NAV_RC4
    print("[TEST] V2_NAV_RC4")
    inputLIST = ['PAST- give.birth .PV NOM DET Jesus LOC Bethlehem ka at Judaea LOC day OBL ruler ka chief ka DET Herod see -LV .IRR PAST- travel .AV NOM wise observe ka PAST- from.east .AV come .AV LOC Jerusalem']
    pprint(testLoki(inputLIST, ['V2_NAV_RC4']))
    print("")

    # V2_NAV_RC3
    print("[TEST] V2_NAV_RC3")
    inputLIST = ['PAST- bring .PV they .GEN him -OBL NOM gift ka gold scent ka incense scent also ka myrrh','PAST- see -LV he .GEN NOM two OBL be.brothers .AV NOM DET Simon ka Petrus OBL nickname .AV DET Andrew also ka brother his ka cast.into.sea .AV OBL net','see -LV .IRR you .PL .GEN NOM horror OBL PAST- destroy -PV ka PAST- speak -PV DET Daniel ka PART prophet LOC place ka PAST- separate .PV LOC worship -PV OBL God then know -LV .IRR -PFV OBL reader']
    pprint(testLoki(inputLIST, ['V2_NAV_RC3']))
    print("")

    # V2_NAV
    print("[TEST] V2_NAV")
    inputLIST = ['call.name -LV .IRR NOM he ka Nazarene','he .GEN PAST- do .PV many OBL might ka work LOC there','PAST- hear .PV NOM this OBL ruler ka chief ka DET Herod','NOM greet -PV also LOC public.place ka gather .PV he .GEN','have -LV .IRR I .GEN OBL life ka always .AV be.lasting .AV','PAST- look -LV he .GEN NOM two OBL be.brothers .AV ka other','obtain -LV .IRR you .PL .GEN NOM more heavy .AV ka judge -PV','swear -PV he .GEN OBL it anything also ka at.top -PV -PFV there','PAST- gather .PV he .GEN all NOM priest ka chief OBL scribe also OBL people','anyone also ka would enter .PV not you .PL .GEN allow -PV let.enter .AV NOM they','explain .LV -IMP we .EXCL .NOM OBL parable OBL herbs ka not good .AV LOC farmland','Truly .AV say .PV I .GEN you .PL .NOM not leave.behind -LV .IRR here NOM even.one ka stone PC. surface OBL stone ka other ka not break.off -PV .IRR']
    pprint(testLoki(inputLIST, ['V2_NAV']))
    print("")

    # V2_AV_RC5
    print("[TEST] V2_AV_RC5")
    inputLIST = ['come.upon .AV -IRR you .PL -OBL NOM all OBL PART blood ka righteous .AV ka PAST- pour -PV LOC earth PART blood GEN Abel ka PART righteous .AV LOC time until OBL PART blood GEN Zacharias ka DET son GEN Barachias ka PAST- murder -PV -you .PL .GEN LOC middle OBL temple OBL worship -PV OBL God OBL place OBL sacrifice -LV']
    pprint(testLoki(inputLIST, ['V2_AV_RC5']))
    print("")

    # CP_TP_and_V2
    print("[TEST] CP_TP_and_V2")
    inputLIST = ['see -LV GEN Herod ka PAST- deceive .AV him -OBL NOM wise observe then exceeding .AV angry .AV NOM he ka when PAST- send.forth .AV PAST- kill .AV OBL all OBL boys ka LOC Bethlehem LOC all-also OBL borders its ka from.two .AV OBL year ka under .AV also PART obey -LV OBL time ka PAST- ask .AV OBL wise cause.see those']
    pprint(testLoki(inputLIST, ['CP_TP_and_V2']))
    print("")

    # RC_and_VP
    print("[TEST] RC_and_VP")
    inputLIST = ['whatever ka from-mouth .AV go.out .AV from-heart .AV ka that instead NOM cause.rotten .AV contaminate .AV OBL man','not yet you ,PL .GEN understand -LV whatever ka go.into.mouth .AV ka go.into.belly .AV ka throw .PV LOC draught NOM it']
    pprint(testLoki(inputLIST, ['RC_and_VP']))
    print("")

    # TP_and_V1
    print("[TEST] TP_and_V1")
    inputLIST = ['leave .AV -IRR NOM human OBL father OBL mother ka join .AV -IRR OBL wife his ka two ka those one -IRR OBL flesh','sit .AV -IRR -PFV NOM son OBL man LOC seat OBL far.above OBL shine -PV OBL status his ka sit .AV -IRR also you .PL .NOM LOC one ten plus OBL two OBL seat ka far.above','take -PV .IRR NOM child with.together -PV .IRR DET mother his ka travel .AV -IRR go .AV LOC land OBL Israel for PAST- die .AV NOM they ka PAST- seek .PV they .GEN NOM soul OBL child']
    pprint(testLoki(inputLIST, ['TP_and_V1']))
    print("")

    # V2_AV_RC4
    print("[TEST] V2_AV_RC4")
    inputLIST = ['speak.good .AV -IRR them -OBL ka curse .AV you .PL -OBL FOC good -LV .IRR them -OBL ka hate .AV you .PL -OBL Pray .AV -IRR because they -OBL ka damage .AV ka persecute .AV you .PL -OBL FOC','hear .AV OBL ruler ka chief PAST- leave .AV -PFV FOC ka see -LV .IRR NOM star ka PAST- see .PV they .GEN at.east .AV PAST- PC. front .AV go.along .AV them -OBL LOC extent until ka it ka PAST- go.along .AV']
    pprint(testLoki(inputLIST, ['V2_AV_RC4']))
    print("")

    # V3_AV
    print("[TEST] V3_AV")
    inputLIST = ['they also ka disciple PAST- hand.over .AV OBL multitudes','he however not PAST- answer .AV her -OBL OBL even.one ka word','PAST- give .AV NOM DET Moses you .PL -OBL OBL bread ka from-heaven .AV']
    pprint(testLoki(inputLIST, ['V3_AV']))
    print("")

    # TP_and_V2
    print("[TEST] TP_and_V2")
    inputLIST = ['he NOM PC. return .AV -IRR take .AV OBL one hundred ka inherit .AV -IRR also OBL life ka always .AV be.lasting .AV']
    pprint(testLoki(inputLIST, ['TP_and_V2']))
    print("")

    # V2_and_VP_and_VP
    print("[TEST] V2_and_VP_and_VP")
    inputLIST = ['eat .AV ka be.satisfied .AV -PFV ka PAST- take .PV they .GEN collect OBL PAST- PC. left.over .AV OBL PART fragments seven ka basket -LV ka full .AV however','PAST- bring .AV him -OBL OBL many .AV ka PAST- possessed.by.devil ka PAST- drive.out -PV he .GEN OBL word NOM spirit ka evil .AV ka PAST- make.well .AV all them -OBL ka not good .AV OBL body']
    pprint(testLoki(inputLIST, ['V2_and_VP_and_VP']))
    print("")

    # V2_and_VP
    print("[TEST] V2_and_VP")
    inputLIST = ['DET John ka PART baptist NOM DET this PAST- cause.rise -PV NOM he OBL death ka because OBL this do -PV him -OBL NOM power ka work','PAST- send.forth .AV LOC surrounding OBL all OBL land ka LOC vicinity there ka PAST- bring .PV they .GEN cause.come .AV him -OBL NOM all ka sick .AV','cause.rise -PV he .GEN NOM sun them -OBL ka not good .AV them -OBL also ka good .AV OBL heart ka cause.rain -PV he .GEN them -OBL ka righteous .AV them -OBL also ka not righteous .AV','hear .AV OBL this NOM ruler ka chief PAST- furious .AV NOM he ka when PAST- send.forth -PV he .GEN NOM many -LV OBL people ka fight .AV PAST- destroy .AV he .GEN NOM killer those ka PAST cause.burn .PV he .GEN OBL fire NOM city their','he .GEN send.forth .AV NOM other OBL servant ka PAST- say .AV tell -LV .IRR NOM PAST- drink.prepare -PV tell .AV see -LV .IRR PAST- prepare .PV I .GEN NOM dinner -PV .IRR my PAST- kill .PV NOM large.animal my ka PAST- castrate .PV OBL PAST- fatling .PV also ka large.animal']
    pprint(testLoki(inputLIST, ['V2_and_VP']))
    print("")

    # CP_taking_Verb
    print("[TEST] CP_taking_Verb")
    inputLIST = ['same .AV ka cause.collect -PV NOM herb ka not good .AV','speak -PV I .GEN you .PL .NOM FOC ka many .AV NOM come .AV -IRR ka from-east .AV OBL from-west .AV','good .AV ka take.away -LV .IRR NOM bread OBL children throw -IV .IRR give .AV OBL it LOC dogs -LV ka little.ones','speak -PV I .GEN you .PL .NOM ka always .AV see .AV NOM angel their OBL face OBL father my ka LOC far.above OBL heaven','not I .NOM great -PV OBL status ka enter .AV -IRR you .SG .NOM OBL roof my however PC. only .AV -IRR let.out.word .AV OBL word ka one','reply .AV -IRR him -OBL NOM righteous .AV ka say .AV -IRR lord PAST- see -LV -we .EXCL .GEN ka when you .SG -OBL ka hungry .AV you .SG .NOM','one OBL woman ka from.city .AV LOC Canaan NOM PAST- call .AV cry.out .AV him -OBL say .AV lord ka DET son GEN David compassionate .PV -IMP I .NOM','PAST- send.forth .AV NOM lord ka sell -IV .IRR NOM he NOM wife his NOM children his OBL all.things also ka his LOC return -PV PC. true .AV pay .AV OBL debt that','know -LV -we .EXCL .GEN ka righteous .AV you .SG .NOM OBL word ka teach .AV you .SG .NOM OBL road OBL God LOC truth ka what -PV .IRR you .SG .GEN NOM anyone ka people','reply .AV -IRR NOM ruler ka chief speak.so .AV them -OBL truly .AV say .PV I .GEN you .PL .NOM insofar -LV you .PL .GEN do .AV NOM these OBL one OBL brother my these ka smallest .AV','PAST- say .AV NOM DET Jesus him -OBL Love .AV -IRR you .SG .NOM OBL lord ka God your .SG LOC heart your .SG ka all LOC soul your .SG ka all LOC all also OBL understand -PV your .SG think .AV']
    pprint(testLoki(inputLIST, ['CP_taking_Verb']))
    print("")

    # V2_AV_RC3
    print("[TEST] V2_AV_RC3")
    inputLIST = ['be.like .AV NOM kingdom OBL far.above OBL heaven OBL man ka chief ruler ka PAST- think.prepare .AV OBL child his ka man OBL celebration OBL marriage']
    pprint(testLoki(inputLIST, ['V2_AV_RC3']))
    print("")

    # TopNP_and_VP
    print("[TEST] TopNP_and_VP")
    inputLIST = ['ought ka fulfill -PV .IRR NOM this ka NEG not.willing -LV .IRR NOM that','he ka PAST- sow .PV LOC earth ka good .AV he NOM DET this.person ka while hear .AV OBL word ka understand .AV OBL it ka bear.fruit .AV','he ka PAST- sow .PV LOC stony.place ka mix .AV OBL dirt he NOM DET that ka hear .AV OBL word ka PC. quick .AV PC. joyful .AV OBL it accept .AV']
    pprint(testLoki(inputLIST, ['TopNP_and_VP']))
    print("")

    # CP_Nominal_Predicate
    print("[TEST] CP_Nominal_Predicate")
    inputLIST = ['not you .PL .GEN or PAST- read .PV ka he ka PAST- make .AV OBL man LOC beginning ka PAST- make .PV he .GEN them -OBL NOM man NOM woman']
    pprint(testLoki(inputLIST, ['CP_Nominal_Predicate']))
    print("")

    # V1_AV
    print("[TEST] V1_AV")
    inputLIST = ['PAST- come .AV LOC land ka Gennesaret','many .AV OBL Jew ka come .AV -PFV DET Mary -OBL','NOM DET Jesus walk .AV PC. top .AV OBL water ka LOC sea','PAST- joyful .AV NOM they OBL joy ka exceeding .AV great .AV','PAST- come .AV DET Jesus -OBL NOM scribe OBL Pharisee and ka PAST- from-Jerusalem .AV','go .AV him -OBL NOM Jerusalem all-inclusive also NOM Judea all also OBL one region ka LOC vicinity OBL Jordan','what NOM PC. more .AV worthy .AV OBL status gold Q temple Q ka cause.distinct .AV OBL gold LOC worship -PV OBL God','again .AV speak -PV I .GEN you .PL .NOM if agree .AV OBL heart NOM two OBL man you .PL -OBL LOC earth because OBL anything ka request -PV .IRR they .GEN permit -LV .IRR them -OBL OBL father my ka LOC far.above OBL heaven']
    pprint(testLoki(inputLIST, ['V1_AV']))
    print("")

    # V2_AV
    print("[TEST] V2_AV")
    inputLIST = ['teach .AV OBL doctrine ka PART commandment OBL man','PAST- follow .AV him -OBL NOM multitudes ka many .AV','accept .AV OBL word this only them -OBL ka PAST- give -LV -PFV .','PAST- see .AV NOM DET Jesus DET Nathanael -OBL ka go .AV him -OBL','swear do.not PC. heaven .AV because ka greatness that ka seat OBL God','you .SG .GEN Q have.mercy -IRR NOM servant ka PART companion your .SG','understand .AV NOM anyone not also NOM angel ka LOC far.above OBL heaven','PAST- hear .AV NOM DET Herod ka one OBL man OBL four OBL ruler OBL land OBL rumor GEN Jesus','NOM cause.live .AV OBL man rather LOC all-instead OBL word ka originate .AV appear .AV LOC mouth OBL God']
    pprint(testLoki(inputLIST, ['V2_AV']))
    print("")

    # V1_and_VP
    print("[TEST] V1_and_VP")
    inputLIST = ['PAST- marvel .AV FOC ka PAST- say .AV them -OBL ka follow .AV him -OBL','PAST- come .AV NOM man ka new ka they ka PAST- prepare PAST- be.together him -OBL enter .AV','rise .AV -IRR NOM many .AV ka false-Christ ka false-prophet ka do .AV -IRR OBL sign ka great .AV OBL DET PART also OBL marvel -PV','PAST- fall .AV NOM some LOC stony.place ka PC. few .AV have.soil .AV ka PAST- spring.up .AV NOM those grow .AV because ka not.have OBL deep .AV ka earth FOC','cry .AV -IRR while that NOM all.inclusive OBL tribes OBL earth ka see .AV -IRR OBL son OBL man while come .AV LOC clouds OBL heaven LOC power OBL greatness OBL status ka huge .AV','many .AV NOM multitudes ka PAST- come .AV him -OBL ka PAST- cause.be.with .AV them -OBL OBL cripple .AV OBL blind .AV OBL dumb .AV OBL maimed .AV OBL other also ka many .AV OBL man','he ka PAST- PC. five .AV OBL talent PAST- come .AV bring .AV OBL five still ka other OBL talent ka PAST- say .PV he .GEN lord five OBL talent ka PAST- give -PV you .SG .GEN me -OBL see -LV .IRR five still ka other OBL talent ka PAST- PC. more .PV I .NOM make.profit .AV OBL it']
    pprint(testLoki(inputLIST, ['V1_and_VP']))
    print("")

    # TopNP_CP
    print("[TEST] TopNP_CP")
    inputLIST = ['servant ka evil .AV ka lazy .AV know -PV you .SG .GEN ka harvest .AV I .NOM LOC not I .GEN PAST sow']
    pprint(testLoki(inputLIST, ['TopNP_CP']))
    print("")

    # V1_AV_RC2
    print("[TEST] V1_AV_RC2")
    inputLIST = ['PAST- enter .AV NOM ruler ka chief LOC see -LV .IRR he .GEN NOM guest PAST- see -LV he .GEN NOM people ka not wear .AV LOC celebration OBL marriage','let.grow .AV LOC harvest -LV .IRR ka LOC time OBL harvest -PV speak -LV .IRR I .GEN OBL man ka harvest .AV -IRR First .AV -IRR collect OBL herb ka not good .AV','come .AV NOM he ka PAST- PC. two OBL talent PAST- say .PV he .GEN lord two OBL talent NOM PAST- give -PV you .SG .GEN me -OBL see -LV .IRR two still OBL other OBL talent ka PAST- PC. more .PV I .NOM make.profit .AV']
    pprint(testLoki(inputLIST, ['V1_AV_RC2']))
    print("")

    # TopNP_V2
    print("[TEST] TopNP_V2")
    inputLIST = ['they ka children OBL kingdom cast.outside -IV .IRR LOC darkness','anyone also NOM take .AV receive.at.home .AV OBL child ka such .AV LOC name my','whatever ka bind -PV .IRR you .PL .GEN LOC earth bind -LV .IRR NOM it LOC far.above OBL heaven','you .PL ka serpent ka PAST- brood OBL viper escape .AV -IRR you .PL .NOM how OBL curse OBL hell','guide ka blind .AV strain -PV you .PL .GEN NOM mosquito ka swallow -PV you .PL .GEN NOM large.animal ka camel']
    pprint(testLoki(inputLIST, ['TopNP_V2']))
    print("")

    # unsolved
    print("[TEST] unsolved")
    inputLIST = ['you .PL ka foolish .AV ka blind .AV','PART write.on.surface also ka inscription','ka most .AV small .AV NOM it OBL all OBL seed','from.where .AV ka have-herb .AV ka not good .AV','Jerusalem Jerusalem, ka kill you .SG .NOM OBL prophet','yet they ka righteous .AV LOC life ka always .AV be.lasting .AV','for truly .AV say .PV I .GEN you .PL .NOM FOC ka many .AV OBL PART prophet OBL PART righteous .AV also NOM PAST- want .AV see .AV ka see -LV you .PL .GEN yet not they .GEN PAST- see -LV','Truly .AV say .PV I .GEN you .PL .NOM FOC not you .SG .NOM come.out .AV -IRR there LOC time until that ka PC. already you .SG .NOM give.finish .AV -IRR OBL most .AV ka small .AV OBL price ka small.coin','when ka PAST- move.on .AV NOM he from .AV there PAST- look -LV he .GEN NOM two OBL be.brothers .AV ka other NOM DET Jakobus REL-child GEN Zebedeus DET John also ka brother his be.together .AV DET father their ka DET Zebedee LOC ship mend .AV OBL dragnet their ka PAST- call .PV he .GEN NOM he']
    pprint(testLoki(inputLIST, ['unsolved']))
    print("")

    # V1_NAV_RC5
    print("[TEST] V1_NAV_RC5")
    inputLIST = ['PAST- spread.everywhere -LV NOM hear -PV OBL name his LOC all OBL Siria ka PAST- bring .PV they .GEN him -OBL all them -OBL ka not good .AV OBL body ka different .AV OBL disease .AV OBL torment -PV ka exceed -PV OBL devil ka PC. moon .AV outburst .AV ka palsy -PV OBL body']
    pprint(testLoki(inputLIST, ['V1_NAV_RC5']))
    print("")


def COMM_TEST(inputSTR):
    if not inputSTR and "utterance_count" in ACCOUNT_DICT and ACCOUNT_DICT["utterance_count"]:
        intentSTR = list(ACCOUNT_DICT["utterance_count"])[0]
        inputSTR = list(ACCOUNT_DICT["utterance_count"][intentSTR])[0]
        inputSTR = re.sub("[\[\]]", "", inputSTR)

    print(setColor("========== COMM_TEST Start ==========", COLOR_DICT["PURPLE"]))

    # Input
    print("\nInput: {}".format(inputSTR))

    # Server
    print(setColor("\nTest Server", COLOR_DICT["CYAN"]))
    print("Server: {}".format(ACCOUNT_DICT["server"]))
    try:
        r = get(ACCOUNT_DICT["server"])
        if r.status_code == 200:
            print("[Status] {}".format(setColor("Connection test successful.", COLOR_DICT["GREEN"])))
        else:
            print("[Status] {}".format(setColor("Connection test failed.", COLOR_DICT["RED"])))
            print("[Hint] {}".format(setColor("Please check if the server field in account.info is a valid URL.", COLOR_DICT["YELLOW"])))
            return
    except:
        print("[Status] {}".format(setColor("Connection test failed.", COLOR_DICT["RED"])))
        print("[Hint] {}".format(setColor("Please check if the server field in account.info is a valid URL.", COLOR_DICT["YELLOW"])))
        return

    # Articut
    print(setColor("\nTest Articut", COLOR_DICT["CYAN"]))
    print("Username: {}".format(ACCOUNT_DICT["username"]))
    print("API Key: {}".format(ACCOUNT_DICT["api_key"]))
    atkResult = ARTICUT.parse(inputSTR, userDefinedDictFILE=USER_DEFINED_FILE)
    if atkResult["status"]:
        print("[Status] {}".format(setColor("Connection test successful.", COLOR_DICT["GREEN"])))
    else:
        print("[Status] {}".format(setColor("Connection test failed.", COLOR_DICT["RED"])))
        if atkResult["msg"] == "Insufficient quota.":
            print("[Hint] {}".format(setColor("Insufficient quota of Articut. Please purchase Articut from the official website.", COLOR_DICT["YELLOW"])))
        else:
            print("[Hint] {}".format(setColor("Please check if the username and api_key fields in account.info are correct.", COLOR_DICT["YELLOW"])))

    # Loki
    print(setColor("\nTest Loki", COLOR_DICT["CYAN"]))
    print("Username: {}".format(ACCOUNT_DICT["username"]))
    print("Loki Key: {}".format(ACCOUNT_DICT["loki_key"]))
    lokiResult = LokiResult([inputSTR], [])
    if lokiResult.getStatus():
        print("[Status] {}".format(setColor("Connection test successful.", COLOR_DICT["GREEN"])))
    else:
        print("[Status] {}".format(setColor("Connection test failed.", COLOR_DICT["RED"])))
        if lokiResult.getMessage() == "Insufficient quota.":
            print("[Hint] {}".format(setColor("Insufficient quota of Loki. Please purchase Loki from the official website.", COLOR_DICT["YELLOW"])))
        else:
            print("[Hint] {}".format(setColor("Please check if the username and api_key fields in account.info are correct.", COLOR_DICT["YELLOW"])))
            print("[Hint] {}".format(setColor("Please check if the Loki model has been deployed.", COLOR_DICT["YELLOW"])))

    print(setColor("\n========== COMM_TEST End ==========", COLOR_DICT["PURPLE"]))


if __name__ == "__main__":
    from pprint import pprint

    # Test all intents
    #testIntent()

    # Test sentence
    contentSTR = ""
    if not contentSTR and "utterance_count" in ACCOUNT_DICT and ACCOUNT_DICT["utterance_count"]:
        intentSTR = list(ACCOUNT_DICT["utterance_count"])[0]
        contentSTR = list(ACCOUNT_DICT["utterance_count"][intentSTR])[0]
        contentSTR = re.sub("[\[\]]", "", contentSTR)

    filterLIST = []
    splitLIST = ["!", ",", ".", "\n", "\u3000", ";"]
    # set references
    refDICT = { # value is a list
        #"key": []
    }

    # Run Loki
    resultDICT = execLoki(contentSTR, filterLIST=filterLIST, splitLIST=splitLIST, refDICT=refDICT)
    pprint(resultDICT)