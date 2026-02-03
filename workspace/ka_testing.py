#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
from pathlib import Path
from time import sleep

#from Loki_AND.Coordinator.main import askLoki as askLokiAND
#from Loki_REL.Relativizer.main import askLoki as askLokiREL
from Loki_COMP.Complementizer.main import askLoki as askLokiCOMP


def main():
    """"""
    return None


if __name__ == "__main__":
    attempts = 0
    success = False
    testLIST = []

    kaPATH = Path.cwd().parent / "data" / "kaLIST.json"
    with open(kaPATH, "r", encoding="utf-8") as f:
        kaLIST = json.load(f)

    toDoLIST = [1582]
    for utterINT in toDoLIST:
        testDICT = {utterINT: kaLIST[utterINT]}
        #testDICT = {utterINT: "angry .AV Q you .PL .NOM me -OBL ka PAST- PC. entire .PV I .GEN cure .AV NOM man LOC day OBL sabbath"}
        print(f"Loki 測試句：")
        print(kaLIST[utterINT])
        print()
        #testLIST.append(kaLIST[utterINT])

    for key_s, test_s in testDICT.items():
        originalSTR = test_s.replace(" -", "-").replace("- ", "-").replace(" .", ".").replace(". ", ".").replace(" ,", ",")
        print(f"VS Code 原句：")
        print(originalSTR)
        print()

    #RELintentLIST = ["clauseQ", "clauseQ_and_VP",
                  #"CP_Nominal_Predicate", "CP_taking_Verb", "CP_taking_Verb_short", "CP_TP_and_V2", "CP_V1_and_VP",
                  #"Nominal_Predicate_RC6", "Nominal_Predicate",
                  #"Phrase", "RC_and_VP", "unsolved", "vague",
                  #"TopNP_and_VP", "TopNP_CP", "TopNP_V1", "TopNP_V1_short", "TopNP_V2", "TopNP_V2_short", "TopNP_V3"
                  #"TP_and_V1", "TP_and_V2",
                  #"V1_and_VP_and_VP_and_VP_and_VP", "V1_and_VP_and_VP", "V1_and_VP",
                  #"V1_AV_RC2", "V1_AV_RC3", "V1_AV_RC4", "V1_AV_RC5", "V1_AV", "V1_AV_short",
                  #"V1_NAV_RC5", "V1_NAV",
                  #"V2_and_VP_and_VP", "V2_and_VP", "V2",
                  #"V2_AV_RC2", "V2_AV_RC3", "V2_AV_RC4", "V2_AV_RC5", "V2_AV", "V2_AV_short",
                  #"V2_NAV_RC3", "V2_NAV_RC4", "V2_NAV", "V2_NAV_short",
                  #"V3_AV", "V3_NAV"]

    COMPintentLIST = ["V2_short", "V2", "V3", "Left_Periphery", "nominalComplement", "unsolved", "vague"]

    refDICT = {"inputSTR":[], "ka_index":[], "utter_index":[], "COMP":[], "and":[], "REL":[]}
    fewIntentLIST = ["nominalComplement", "overlap", "V3", "V2_short", "V2", "or", "Left_Periphery"]
    for key_s, test_s in testDICT.items():
        resultLIST = []

        for intent_s in fewIntentLIST:
            attempts = 0
            success = False

            while attempts < 3 and not success:
                print(intent_s)
                lokiResultDICT = askLokiCOMP(test_s, filterLIST=[intent_s] ,refDICT=refDICT)
                sleep(0.8)

                if "msg" in lokiResultDICT.keys():
                    attempts += 1
                    print(f"第 {attempts} 次嘗試，{lokiResultDICT['msg']}: {lokiResultDICT}")
                    sleep(5)
                else:
                    success = True
                    resultLIST.append(lokiResultDICT)   # 跑單一 project、each intent
                    print(lokiResultDICT)
                    print()

        #kaLIST = []
        #matchIntentLIST=[]
        #for result_d in resultLIST:
            #if result_d["ka_index"]:
                #kaLIST.append(result_d["ka_index"])
                #matchIntentLIST.append(result_d["REL"])
                #allInetentResultDICT = {
                    #"inputSTR":[test_s],
                    #"ka_index": list(set(kaLIST)),
                    #"utter_index":[key_s],
                    #"COMP":[],
                    #"and":[],
                    #"REL":matchIntentLIST
                    # }

        #print(resultLIST)
        #print(allInetentResultDICT)