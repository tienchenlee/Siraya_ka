# Table of Contents

1. Siraya_ka 模型部署
2. askLoki
3. 計算覆蓋率

- - - 

# 1. Siraya_ka 模型部署  
## 1.1 Loki pattern 調整
 - 調整 utterance，部署該 intent。(不需做 1.2)
 - 新增 utterance，部署該 intent，將該句 utterance 加進 intent.py。(不需做 1.2)
 - 調整 ud/var，需要部署所有 intent，並將 ud 下載，更新到 `workspace/Loki_and/Coordinator/intent`, `workspace/Loki_REL/Relativizer/intent`, `workspace/Loki_COMP/Complementizer/intent`。
 - 調整 var 時，如果 var 有使用 trie 加速，利用 `workspace/generalTool/regex_speedup_tools.py` 在相對應的 var 增減內容，並執行程式碼，拿到 trie 結果，更新至 Loki 介面。

## 1.2 三個專案同步更新 ud/var
ud/var 會是三個 Project 共用，一次調整好某一個 Project 的 ud/var 後，要將三個專案同步更新。  

#### 1.2.1 檔案更新 
下載 ud/var，更新到 `data/userDefined.json` 和 `data/VARIABLE.json` 。  
#### 1.2.2 執行 udVarUpdater.py 工具
執行 `workspace/generalTool/udVarUpdater.py` 將 ud/var 更新至三個 Project。
`workspace/account.info` 需要包含三個 Project 的 loki_key。
#### 1.2.3 Loki 介面調整
在 Loki 介面調整 ka 的捕獲組，並部署所有 intent。  

- Complementizer 專案的 CP 中要抓 (ka)，RC 不抓 ka
- Relativizer 專案的 RC 中要抓 (ka)，CP 不抓 ka
- Coordinator 則是 CP 和 RC 都不抓 ka。

## 1.3 github 更新
將本機更動 git push。
## 1.4 atm 更新
下載 Loki_bk 將 atm 更新到遠端主機，git pull 所有更動後，確認 Loki Project 的 account.info 中 server 是遠端主機，即部署完成。

# 2. askLoki
1. 使用 `workspace/ka_identifier.py` 進行模型測試。  
2. 根據此次測試專案類別，在 133-135 行擇一進行測試。  
3. 188 行可更改測資。
4. 結果產生至 `data/training/predictionLIST.json`

# 3. 計算覆蓋率
使用 `workspace/generalTool/evaluation.py` ，分別針對測資產生正解及預測檔案至 `data/answer/`, `data/prediction/`。False Negative 記錄在 `data/training`。