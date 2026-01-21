#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
from time import sleep

#from Loki_AND.Coordinator.main import askLoki as askLokiAND
from Loki_REL.Relativizer.main import askLoki as askLokiREL

def main():
    """"""
    return None


if __name__ == "__main__":
    attempts = 0
    success = False

    #with open("evaluation_data/kaLIST.json", encoding="utf-8") as kaFILE:
        #mixedLIST = json.load(kaFILE)

    testLIST = ["yet time OBL day OBL hour also that not understand .AV NOM anyone not also NOM angel ka LOC far.above OBL heaven only ka father my LOC one"]

    intentLIST = ["clausQ", "CP_Nominal_Predicate", "CP_taking_Verb", "CP_TP_and_V2", "Nominal_Predicate_RC6",
                  "Nominal_Predicate", "Phrase", "RC_and_VP", "TopNP_and_VP", "TopNP_CP", "TopNP_V1", "TopNP_V2",
                  "TP_and_V1", "TP_and_V2", "unsolved", "V1_and_VP_and_VP", "V1_and_VP", "V1_AV_RC2", "V1_AV_RC4",
                  "V1_AV", "V1_NAV_RC5", "V1_NAV", "V2_and_VP_and_VP", "V2_and_VP", "V2_AV_RC2", "V2_AV_RC3",
                  "V2_AV_RC4", "V2_AV_RC5", "V2_AV", "V2_NAV_RC3", "V2_NAV_RC4", "V2_NAV", "V3_AV", "V3_NAV"]

    refDICT = {"inputSTR":[], "ka_index":[], "utter_index":[], "COMP":[], "and":[], "REL":[]}
    for test_s in testLIST:
        attempts = 0
        success = False

        while attempts < 3 and not success:
            relResult = askLokiREL(test_s, filterLIST=["V2_AV"], refDICT=refDICT)
            sleep(0.8)

            if "msg" in relResult.keys():
                attempts += 1
                print(f"第 {attempts} 次嘗試，{relResult['msg']}: {relResult}")
                sleep(5)
            else:
                success = True
                print(relResult)

        #andResult = askLokiAND(ka_S, refDICT=refDICT)
        #relResult = askLokiREL(ka_S, refDICT=refDICT)


    print("REL:")
    #print(andResult)

    print("===")
    print(relResult)