#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from Loki_COMP.Complementizer.main import askLoki
#from preLokiTool import udFilter

def main(inputSTR, filterLIST, utterIdx):
    """"""
    refDICT = {
        "inputSTR": [inputSTR],
        "COMP": [],
        "ka_index": [],
        "utter_index": [utterIdx],
    }

    resultDICT = askLoki(inputSTR, filterLIST=filterLIST, refDICT=refDICT)

    return resultDICT

if __name__ == "__main__":
    #<單筆測試>
    inputSTR = "ka again -PV I .GEN you .PL .NOM speak .AV ka more .AV be.able NOM large.animal ka heavy .AV OBL back go.through .AV LOC hole OBL needle ka enter .AV -IRR NOM rich .AV LOC kingdom OBL God"

    filterSTR = udFilter(inputSTR)
    resultDICT = main(filterSTR, 0)  # 預設句子 index = 0
    print(resultDICT)
    #</單筆測試>