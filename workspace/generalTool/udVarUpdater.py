#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
from requests import post
from pathlib import Path

accountPATH = Path.cwd().parent / "account.info"
with open(accountPATH, "r", encoding="utf-8") as f:
    accountDICT = json.load(f)

def updateRegexVar():
    """
    Align regex var in three projects (Relativizer, Complementizer, Coordinator).
    """
    varPATH = Path.cwd().parent.parent / "data" / "VARIABLE.json"
    with open(varPATH, "r", encoding="utf-8") as f:
        varDICT = json.load(f)

    url = "https://nlu.droidtown.co/Loki_EN/Call/"
    loki_keys = ["Complementizer", "Coordinator", "Relativizer"]
    for loki_key in loki_keys:
        payload = {
          "username": accountDICT["username"],
          "loki_key": accountDICT[loki_key],
          # Reset Var
          "func": "reset_var",
          "data": {},
          # Update var
          "func": "update_var",
          "data": {
              "var": varDICT
          }
        }

        resultDICT = post(url, json=payload).json()
        print(f"Update regex Var with {loki_key}:")
        print(resultDICT)
        print()

def updateUd():
    """
    Align ud in three projects (Relativizer, Complementizer, Coordinator).
    """
    udPATH = Path.cwd().parent.parent / "data" / "userDefined.json"
    with open(udPATH, "r", encoding="utf-8") as f:
        udDICT = json.load(f)

    url = "https://nlu.droidtown.co/Loki_EN/Call/"
    loki_keys = ["Complementizer", "Coordinator", "Relativizer"]
    for loki_key in loki_keys:

        payload = {
            "username": accountDICT["username"],
            "loki_key": accountDICT[loki_key],
            "func": "update_userdefined",
            "data": {
                "user_defined": udDICT
            }
        }

        resultDICT = post(url, json=payload).json()
        print(f"Update UD with {loki_key}:")
        print(resultDICT)
        print()

if __name__ == "__main__":
    updateRegexVar()
    updateUd()
    print(f"記得更新 ka 在不同 project 的 capturing group!")
