#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from Relativizer.main import askLoki
from preLokiTool import udFilter

def main(inputSTR):
    """"""
    refDICT = {
        "REL": []
    }

    resultDICT = askLoki(inputSTR, refDICT=refDICT)
    return resultDICT

if __name__ == "__main__":
    inputSTR = "when ka see-LV they.GEN NOM star then PAST-joyful.AV NOM they OBL joy ka exceeding.AV great.AV"
    #wordLIST = inputSTR.split()
    #print(wordLIST)

    filterSTR = udFilter(inputSTR)
    resultDICT = main(filterSTR)
    print(resultDICT)