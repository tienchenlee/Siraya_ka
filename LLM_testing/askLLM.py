#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import re
from google import genai
from google.genai.types import GenerateContentConfig
from pathlib import Path
from requests import post
from time import sleep

G_jsonPAT = re.compile(r"\{.*\}", re.DOTALL)

with open(f"{Path.cwd()}/account.info", "r", encoding="utf-8") as f:
    G_accountDICT = json.load(f)

with open(f"{Path.cwd().parent}/data/kaLIST_eval.json") as f:
    G_testLIST = json.load(f)

def _getInfo(loki_key):
    """"""
    print("[Get Info]")

    url = "https://nlu.droidtown.co/Loki_EN/Call/"

    payload = {
        "username" : G_accountDICT["username"],
        "loki_key": loki_key,
        "func": "get_info",
        "data": {}
    }

    response = post(url, json=payload)
    print(f"status of getting info:{response.status_code}")
    print()

    try:
        resultDICT = response.json()
        return resultDICT
    except:
        print(response.status_code)
        print(response.text)

def _getUtter():
    """
    拿到 Loki 上的所有 utterance，給 LLM 做為參考。
    """
    utteranceLIST = []
    projectLIST = ["Relativizer", "Complementizer", "Coordinator"]

    for projectSTR in projectLIST:
        print(f"[Project]: {projectSTR}")
        resultDICT = _getInfo(loki_key=G_accountDICT[projectSTR])
        intentDICT = resultDICT["result"]["intent"]

        for valueLIST in intentDICT.values():
            utteranceLIST.extend(valueLIST)

    print(f"Loki 建模句子數量：{len(utteranceLIST)}")
    return utteranceLIST

def _askLLM(promptSTR):
    client = genai.Client(api_key=G_accountDICT["gemini_api_key"])

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=promptSTR,
        config=GenerateContentConfig(
            system_instruction="You are a syntactician."
        )
    )

    print(f"回覆：")
    print(response.text)

    return response.text

def main(phase=None):
    """
    Test LLM in three phases.
    Phase1: prompt engineering
    Phase2: context engineering
    Phase3: agent skills
    """
    # Phase 1
    PROMPT_PHASE1 = """The multifunctional ka in Siraya serves a broad range of syntactic functions, which introduces relative clauses, complement clauses, and coordinating clauses.
    Your task is to identify the function of ka in Siraya in the following sentence.
    Return ONLY valid JSON with the following schema: {{"inputSTR": {jsonTestSTR}, "status": "Succeeded", "REL": [], "COMP": [], "and": []}}.
    The values in the JSON should be the 0-based word index of 'ka' (split by spaces).
    The abbreviations used in the sentence: AV: actor voice; COMP: complementizer; DET: determiner; EXCL: exclusive; FOC: focus marker; GEN: genitive; IRR: irrealis mood; IV: instrument voice; LOC: locative case; LV: locative voice; NOM: nominative case; OBL: oblique case; PART: partitive case; PAST: past tense; PC: prefix concord; PFV: perfective; PL: plural; PRES: present; PTP: participle; PV: patient voice; REL: relativizer marker; SG: singular.
    Now identify the function of ka in following sentence: {testSTR}"""

    # Phase 2
    PROMPT_PHASE2 = """The multifunctional ka in Siraya serves a broad range of syntactic functions, which introduces relative clauses, complement clauses, and coordinating clauses.
    Below are the example sentences: {utteranceLIST}.
    Your task is to identify the function of ka in Siraya in the following sentence.
    Return ONLY valid JSON with the following schema: {{"inputSTR": {jsonTestSTR}, "status": "Succeeded", "REL": [], "COMP": [], "and": []}}.
    The values in the JSON should be the 0-based word index of 'ka' (split by spaces).
    The abbreviations used in the sentence: AV: actor voice; COMP: complementizer; DET: determiner; EXCL: exclusive; FOC: focus marker; GEN: genitive; IRR: irrealis mood; IV: instrument voice; LOC: locative case; LV: locative voice; NOM: nominative case; OBL: oblique case; PART: partitive case; PAST: past tense; PC: prefix concord; PFV: perfective; PL: plural; PRES: present; PTP: participle; PV: patient voice; REL: relativizer marker; SG: singular.
    Now identify the function of ka in following sentence: {testSTR}"""

    # Phase 3
    PROMPT_PHASE3 = """The multifunctional ka in Siraya serves a broad range of syntactic functions, which introduces relative clauses, complement clauses, and coordinating clauses.
    Below are three skills describing in different functions of 'ka':
    {REL_skill}
    {COMP_skill}
    {and_skill}
    Your task is to identify the function of 'ka' in the following sentence and determine which skill to apply.
    Return ONLY valid JSON with the following schema: {{"inputSTR": {jsonTestSTR}, "status": "Succeeded", "REL": [], "COMP": [], "and": []}}.
    The values in the JSON should be the 0-based word index of 'ka' (split by spaces).
    The abbreviations used in the sentence: AV: actor voice; COMP: complementizer; DET: determiner; EXCL: exclusive; FOC: focus marker; GEN: genitive; IRR: irrealis mood; IV: instrument voice; LOC: locative case; LV: locative voice; NOM: nominative case; OBL: oblique case; PART: partitive case; PAST: past tense; PC: prefix concord; PFV: perfective; PL: plural; PRES: present; PTP: participle; PV: patient voice; REL: relativizer marker; SG: singular.
    Now identify the function of ka in following sentence: {testSTR}"""

    if phase == 2:
        utteranceLIST = _getUtter()

    if phase == 3:
        with open(f"{Path.cwd()}/skills/REL.md", "r", encoding="utf-8") as f:
            REL_skill = f.read()
        with open(f"{Path.cwd()}/skills/COMP.md", "r", encoding="utf-8") as f:
            COMP_skill = f.read()
        with open(f"{Path.cwd()}/skills/and.md", "r", encoding="utf-8") as f:
            and_skill = f.read()

    resultLIST = []
    max_retries = 3

    for testSTR in G_testLIST:
        if phase == 1:
            promptSTR = PROMPT_PHASE1.format(
                jsonTestSTR=json.dumps(testSTR),
                testSTR=testSTR
            )

        elif phase == 2:
            promptSTR = PROMPT_PHASE2.format(
                utteranceLIST=utteranceLIST,
                jsonTestSTR=json.dumps(testSTR),
                testSTR=testSTR
            )

        elif phase == 3:
            promptSTR = PROMPT_PHASE3.format(
                REL_skill=REL_skill,
                COMP_skill=COMP_skill,
                and_skill=and_skill,
                jsonTestSTR=json.dumps(testSTR),
                testSTR=testSTR
            )

        attempt = 0
        match = None
        success = False
        while attempt < max_retries:
            try:
                responseSTR = _askLLM(promptSTR)
                sleep(5)
                match = re.search(G_jsonPAT, responseSTR)

                if not match:
                    attempt += 1
                    continue

                jsonSTR = match.group()

                try:
                    dataDICT = json.loads(jsonSTR)
                    if (
                        dataDICT.get("status") == "Succeeded" and
                        not dataDICT.get("REL") and
                        not dataDICT.get("COMP") and
                        not dataDICT.get("and")
                    ):
                        print("Empty result, retrying...")
                        attempt += 1
                        continue

                    resultLIST.append(dataDICT)
                    success = True
                    break

                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    attempt += 1
                    continue

            except Exception as e:
                print(f"API error: {e}")
                attempt += 1
                sleep(30)
                continue

        if not success:
            dataDICT = {
                "inputSTR": testSTR,
                "status": "LLM failed to return JSON after 3 retries.",
                "REL": [],
                "COMP": [],
                "and": []
            }

            resultLIST.append(dataDICT)

    resultDIR = Path(f"{Path.cwd()}/results")
    resultDIR.mkdir(exist_ok=True, parents=True)
    with open(f"{resultDIR}/phase_{phase}.json", "w", encoding="utf-8") as f:
        json.dump(resultLIST, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main(phase=2)

