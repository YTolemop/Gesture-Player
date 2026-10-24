# 手勢訓練器 · 新版三通道 GUI 學員版

這份是保留圖形介面的新版學員包，GitHub 專案為 [Gesture-Player](https://github.com/YTolemop/Gesture-Player)。與目前競技場、Demo、initial 使用相同的 `left`、`right`、`both` 輸出能力：左右手可同時操作，雙手合成成功時獨占輸出。技能冷卻、氣量、硬直和觸發規則完全由同一個競技場判定，使用 UI 不會少一個控制通道。

差別在操作方式：用按鈕選通道、錄製、訓練、測試及配對，不必手動執行每個流程。`student/` 仍是待完成的作業起點；本教學提供可整段複製的完整參考程式，沒有附帶別人的訓練資料或自訂手勢模型。請理解每一步，再使用自己的手勢收集資料。

你會依序完成：設定環境 → 確認鏡頭 → 收集資料 → 實作辨識 → 訓練與驗證 → 連線遊玩。先了解下方的專案架構，再依第 1～9 節操作。

## 專案架構與資料流程

`core/` 負責取得手部資料、管理資料與三通道模型，`student/` 是學員實作入口，`network/` 負責競技場通訊，`ui/` 提供圖形介面。`main.py` 將這些部分串起來。

```text
main.py                    操作入口：準備、檢查、GUI、訓練與測試
core/
  camera.py                讀取攝影機
  landmarks.py             呼叫 MediaPipe，取得手部關節
  types.py                 定義原始樣本、特徵與分類結果
  features.py              檢查原始樣本與特徵
  dataset.py               保存與讀取錄製批次
  channel_model.py         三通道訓練、模型載入與獨立測試
  channel_router.py        左右獨立、雙手優先與缺手清除
  resources.py             下載與驗證 MediaPipe 關節模型
student/
  normalization.py         學員實作：131 維特徵正規化
  knn.py                   學員實作：KNN 訓練與分類
  filtering.py             學員選做：時間濾波
ui/                        鏡頭、錄製、訓練、測試與配對介面
network/                   配對、指令傳送與網站鏡頭預覽
protocol/                  競技場通訊規格與範例封包
tests/                     工具與介面契約的測試
requirements-lock.txt      套件與固定版本
```

錄製、訓練與遊玩是三個不同階段：

```text
錄製：鏡頭 → MediaPipe → 原始關節 + 手動選擇的動作／通道／用途 → data/*.npz + *.json
訓練：train 批次 → 各通道特徵正規化 → 三個 KNN 分類器 → models/model.npz
測試：獨立 test 批次 → 同一套辨識流程 → models/evaluation.json
遊玩：鏡頭 → MediaPipe → 正規化 → KNN → 選做濾波 → 三通道輸出 → 競技場
```

兩種模型要分清楚：`assets/models/hand_landmarker.task` 是 MediaPipe 已訓練的手部關節偵測模型，只負責找出關節；`models/model.npz` 才是用自己的手勢資料建立的分類模型。`data/` 和 `models/` 會在錄製與訓練後產生，不一定出現在剛解壓縮的專案裡。預覽和錄製可先使用，辨識與訓練則需要完成 `student/` 中的正規化與 KNN。

## 1. 設定環境與開啟 GUI

需要 **Python 3.13**、攝影機、可開視窗的本機桌面環境，以及首次下載依賴與關節模型所需的網路。專案的 `pyproject.toml` 指定 Python `3.13.*`，請先確認版本再安裝套件。

在 [GitHub](https://github.com/YTolemop/Gesture-Player) 按 Code → Download ZIP，完整解壓縮。在 VS Code 選「檔案 → 開啟資料夾」，開啟內含 `main.py` 的專案資料夾，再選「終端機 → 新增終端機」。接下來的指令都在這個資料夾執行。

### 建立環境與安裝套件

依自己的系統選一組指令。`.venv` 是專案自己的 Python 環境；`requirements-lock.txt` 列出所需套件與固定版本。這一段只需在第一次使用或重建環境時執行。**第一行應顯示 `Python 3.13.x`；若找不到指令或版本不符，先安裝 Python 3.13，再繼續。**

Windows：使用 PowerShell。

```powershell
py -3.13 --version
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe main.py prepare
.\.venv\Scripts\python.exe main.py check
```

macOS：使用 Terminal 的 zsh 或 bash。M 系列晶片請使用原生 Apple Silicon 的 Python 與終端機環境。

```bash
python3.13 --version
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r requirements-lock.txt
./.venv/bin/python main.py prepare
./.venv/bin/python main.py check
```

Linux：使用本機桌面環境的 bash 或 zsh，先安裝 Python 3.13，以及與該版本相符的 Tk 和 venv 套件。以套件來源提供該版本的 Ubuntu／Debian 為例：

```bash
sudo apt update
sudo apt install python3.13-tk python3.13-venv
```

再建立環境：

```bash
python3.13 --version
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r requirements-lock.txt
./.venv/bin/python main.py prepare
./.venv/bin/python main.py check
```

若建立 `.venv` 時提示缺少 `venv` 或 `ensurepip`，先確認已安裝對應的 venv 套件，再重新建立。GUI 使用 Tkinter，Linux 必須有可用的 Tk；若提示缺少 `tkinter` 或 `_tkinter`，請確認安裝的 Tk 套件對應目前使用的 Python。

上面各行分別負責不同的事，若某一步失敗，先處理該步的錯誤：

| 指令部分 | 用途 |
| --- | --- |
| `--version` | 確認使用 Python 3.13 |
| `-m venv .venv` | 建立這個專案專用的 Python 環境 |
| `-m pip install -r requirements-lock.txt` | 用該環境的 Python 安裝指定套件 |
| `main.py prepare` | 下載並驗證 MediaPipe 關節模型；已有有效模型時直接驗證 |
| `main.py check` | 檢查套件、Tkinter 匯入、關節模型載入與資料夾寫入 |

`check` 成功時會輸出 JSON，包含 Python 版本、套件版本與 `"model_load": "PASS"`。`"camera": "NOT_RUN"` 表示尚未測試鏡頭；`"student_algorithms": "TODO"` 是這個檢查指令的固定標記，不會驗證你是否完成演算法。這一步通過後，仍需到 GUI 確認鏡頭並完成後續訓練與測試。

### 開啟 GUI 與後續使用

環境檢查通過後，執行自己的系統對應指令：

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe main.py gui
```

macOS／Linux：

```bash
./.venv/bin/python main.py gui
```

**之後每次開啟，回到專案資料夾執行上面的 GUI 指令即可。** 不必重新安裝套件、下載關節模型或建立環境。錄製、訓練、測試和配對都可在視窗內操作。

也可以先啟用環境，再使用 `python main.py gui`。每次重新開啟終端機都需要重新啟用：

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS／Linux：

```bash
source .venv/bin/activate
```

若 PowerShell 不允許執行啟用腳本，直接使用前面的 `.\.venv\Scripts\python.exe` 即可。macOS／Linux 也可直接使用 `./.venv/bin/python`。

在 VS Code 按 `Ctrl+Shift+P`（Mac 為 `Cmd+Shift+P`），搜尋 `Python: Select Interpreter`，選本專案 `.venv` 的 Python，讓編輯器也使用相同環境。在程式中改好算法後，保存檔案、關閉並重開工具，才會載入新版本。

### Linux／uv 的中文字型顯示異常

GUI 會從已安裝的字型中選擇中文字型，並套用到標題與一般控制項：Windows 可使用微軟正黑體，macOS 可使用蘋方繁體，Linux 可使用 Noto Sans CJK TC。不附帶或私下安裝字型。

Linux 的 uv Python 可能附帶不支援 Xft 的 Tk；此時**只安裝中文字型還不夠**，仍會呈現點陣、破碎或間距異常，參見 [上游問題](https://github.com/astral-sh/python-build-standalone/issues/740)。Ubuntu／Debian 可先確認 Python 所需的 Tk 版本：

```bash
./.venv/bin/python -c "import tkinter; print(tkinter.TkVersion)"
```

若顯示 `9.0`，安裝：

```bash
sudo apt update
sudo apt install fonts-noto-cjk fontconfig tk9.0
fc-cache -f
./.venv/bin/python main.py gui
```

若顯示 `8.6`，將安裝指令中的 `tk9.0` 改成 `tk8.6`。其他發行版請安裝對應套件；發行版必須提供與 Python 相同主、次版本的 Tk。

啟動 GUI 時，程式會先檢查中文字型能否使用；若不能，會在獨立程序驗證系統 Tk，確認版本相符且能讀取中文字型才採用。程式保留 Python 原本的 Tcl，不修改 uv 的 Python 安裝。Windows／macOS 不執行這項 Linux 修正。

若發行版沒有相符的 Tk，或仍無法正常顯示，可保留 uv 管理套件，改用系統 Python 3.13 與其 Tk。先安裝 Python 3.13 及對應的 Tk（例如 `python3.13-tk`），確認以下路徑存在，再建立另一個環境：

```bash
/usr/bin/python3.13 -m tkinter
uv venv --python /usr/bin/python3.13 .venv-linux
uv pip install --python .venv-linux/bin/python -r requirements-lock.txt
./.venv-linux/bin/python main.py prepare
./.venv-linux/bin/python main.py gui
```

之後使用最後一行開啟即可。這個環境與原本的 `.venv` 分開；Python 路徑依發行版調整，專案要求 3.13。uv 支援指定系統 Python，詳見 [Python 選擇說明](https://docs.astral.sh/uv/concepts/python-versions/)。

## 2. 先認識四個分頁

| 分頁 | 操作 | 成功時看到什麼 |
| --- | --- | --- |
| 1. 鏡頭與辨識 | 選攝影機索引、開鏡頭；切換「僅預覽鏡頭」或「辨識並傳送」 | 畫面有手部關節；下方列出左右側原分類、三欄安全輸出與 FPS |
| 2. 錄製與訓練 | 選通道、動作、用途，錄製後按訓練／測試／載入三通道模型 | 列表顯示類別、train/test、通道、筆數、時間 |
| 3. 連線遊戲 | 選玩法、填網址與自己的配對碼 | 配對狀態、準備檢查、三欄輸出和競技場執行回饋 |
| 4. 操作教學 | 查看流程；開啟本 README | 可複製的演算法完整範例和逐步操作 |

先開啟鏡頭並只伸出一隻手，確認左手、右手標示符合你使用的手。`swap_handedness` 控制這個對應；修改後須重新錄製／檢查資料並重新訓練。預覽模式只送中立遊戲指令，但配對後仍可把鏡頭和骨架傳到網站。

### 確認鏡頭與 MediaPipe 關節

1. 到「1. 鏡頭與辨識」，模式先選「僅預覽鏡頭」，鏡頭索引保留 `0`，按「開啟鏡頭」。
2. 將手完整放入畫面，確認能看見每隻手的 21 個關鍵點與連線；分別測左手、右手，再同時伸出雙手。
3. 若開到錯誤鏡頭，先按「停止鏡頭」，將索引改成 `1` 或其他可用值，再重新開啟。
4. 移開雙手，確認介面不再顯示有手；按「停止鏡頭」可結束預覽，關閉工具也會釋放攝影機。

這一步只確認鏡頭與關節偵測可用，尚未完成學員分類器時仍可預覽與錄製。MediaPipe 的左右手分類分數不是手勢辨識正確率，也不是關節座標精準度。

鏡頭權限：Windows 請允許桌面應用程式使用攝影機；macOS 請在「系統設定 → 隱私權與安全性 → 攝影機」允許 VS Code／Terminal，必要時重啟應用程式；Linux 請確認目前帳號可存取攝影機裝置。其他視訊程式若占用鏡頭，先關閉再試。

完成標準：鏡頭持續提供影格，手入鏡時可看見關鍵點，左右手對應正確，手移開時偵測回到無手。

## 3. 設計並收集手勢資料

先決定每個手勢的名稱、使用哪隻手，以及要對應哪個遊戲動作。

### 十個動作的錄製清單

需要錄製的十個遊戲動作如下：

| 序號 | 遊戲動作 | 對應指令 |
| --- | --- | --- |
| 1 | 向左移動 | `MOVE_LEFT` |
| 2 | 向右移動 | `MOVE_RIGHT` |
| 3 | 跳躍 | `JUMP` |
| 4 | 蹲下 | `CROUCH` |
| 5 | 防禦 | `BLOCK` |
| 6 | 普通攻擊 | `NORMAL_ATTACK` |
| 7 | 攻擊技能 | `ATTACK_SKILL` |
| 8 | 防禦技能 | `DEFENSE_SKILL` |
| 9 | 控制技能 | `CONTROL_SKILL` |
| 10 | 終極技能 | `ULTIMATE` |

### 標籤、通道與錄製範例

以下只是設計範例，請依自己的手勢調整：

| 通道 | 自訂手勢名稱 | 預計對應的指令 |
| --- | --- | --- |
| left | point_left | MOVE_LEFT |
| left | point_right | MOVE_RIGHT |
| right | fist | NORMAL_ATTACK |

自訂手勢名稱用來記錄自己的設計。本版 GUI 的「動作」直接選擇遊戲指令作為分類標籤，例如 `MOVE_LEFT`，不需另外輸入 `point_left`，也不需另外撰寫名稱到指令的映射。

「通道」表示這批資料預計用於 `left`、`right` 或 `both`，是你提供的標註；`left` 使用左手特徵、`right` 使用右手特徵，`both` 使用雙手特徵與相對位置。因此錄製單手通道時，相應的手必須完整入鏡；錄製 `both` 時，兩手都要完整入鏡。通道不是遊戲的紅方、藍方，同一隻手也可以設計多個不同姿勢。

介面選擇動作時會自動帶入建議通道，仍可依自己的設計修改。例如上表的向右移動也使用左手，選完 `MOVE_RIGHT` 後，將通道改成 `left` 即可。工具不會替你判斷錄製時是否做對手勢。

到「2. 錄製與訓練」，依自己的設計逐次錄製：

1. 選擇「動作」與「通道」，用途選 `train`。例如錄向左指時選 `MOVE_LEFT`、`left`。
2. 按「開始錄製」，在三秒倒數內擺好姿勢，透過即時預覽確認手部關節與有效筆數。
3. 保持約 10～15 秒，按「停止錄製」保存這批資料。
4. 換下一個手勢，重新選擇動作與通道，再錄一批。例如向右指選 `MOVE_RIGHT`、`left`；握拳選 `NORMAL_ATTACK`、`right`。

錄製資料保存到 `data/`，每次產生一組新的批次檔案：

| 檔案 | 用途 |
| --- | --- |
| `.npz` | 手部關節座標、手部存在標記與動作標籤，供訓練與測試使用 |
| 同名 `.json` | 通道、train／test 用途、擷取設定與逐筆樣本資訊 |

錄製不要求演算法先完成；有效筆數代表原始手部資料可採集，不代表正規化已寫好或分類已準確。每個手勢分多次錄製，適度改變位置、距離與角度。透過預覽確認姿勢，避免把切換姿勢或做錯動作的影格當成正確範例。

### 另外收集獨立測試資料

將用途改成 `test`，另外擺好同一個手勢重新錄一批，動作與通道要和原本的設計一致。其他類別也要收集測試資料。訓練只讀取 `train` 批次，獨立測試只讀取 `test` 批次；兩者都保存在 `data/`，由用途欄位區分。

不要把測試資料拿去訓練，也不要只將同一段錄製的相鄰影格隨機拆成訓練與測試，否則容易高估效果。辨識完成後，另外測試日常姿勢、手勢切換、左手移動與右手攻擊同時出現，以及單手或全部移出畫面的情境，檢查是否誤觸。

完成標準：上述十個動作各有多批可用訓練資料與另行錄製的獨立測試資料，標籤、通道和實際手勢一致，且已記下每個姿勢對應的遊戲指令。三個通道都要有訓練資料，每個通道的總訓練筆數至少要大於等於 `k`（預設 5）。

若是舊版沒有標通道的批次，先備份到另一個資料夾，再用新版 GUI 重錄；工具不會猜通道或自動將舊模型升級。

## 4. 完成固定 131 維的正規化

請將下面整段複製到 `student/normalization.py`，替換該檔原本的 TODO。工具會先整理左右手、檢查關節、再依通道傳入資料：left 只有左手、right 只有右手、both 需要兩手。它們都必須輸出同樣的 131 維向量。

| 索引 | 意義 |
| --- | --- |
| 0～62 | 左手 21 點的 xyz；缺手填 0 |
| 63～125 | 右手 21 點的 xyz；缺手填 0 |
| 126～127 | 左、右手存在標記；存在填 2 |
| 128～130 | 兩手腕相對位置；缺任一手填 0；z 固定為 0 |

先把 x、z 乘影像寬，y 乘影像高，換成一致的像素尺度；每隻手減去第 0 點手腕，再除以手腕到第 9 點中指根部的距離。這能處理位置與大小變化，仍保留方向；不保證不同旋轉角度完全相同。

兩手各自歸零會失去彼此距離，所以再加入右手腕減左手腕的相對 x、y。每隻手的 z 各有自己的參考原點，不能拿來計算兩手真實深度差。存在標記能區分缺手和全零特徵。

```python
import numpy as np
from core.types import RawHandSample, FeatureResult


class StudentNormalizer:
    def transform(self, sample: RawHandSample, config: dict) -> FeatureResult:
        features = np.zeros(131, dtype=np.float32)
        wrists = [None, None]
        sizes = [None, None]

        for slot, hand in enumerate((sample.left, sample.right)):
            if hand is None:
                continue
            points = np.array(hand, dtype=np.float64, copy=True)
            points *= np.array([sample.width, sample.height, sample.width])
            wrists[slot] = points[0].copy()
            centered = points - points[0]
            sizes[slot] = np.linalg.norm(centered[9])
            start = slot * 63
            features[start:start + 63] = (centered / sizes[slot]).reshape(63)
            features[126 + slot] = 2.0

        if wrists[0] is None and wrists[1] is None:
            return FeatureResult(
                valid=False, reason='無手',
                featureVersion=config['feature_version'],
            )
        if wrists[0] is not None and wrists[1] is not None:
            relative = (wrists[1] - wrists[0]) / ((sizes[0] + sizes[1]) / 2)
            relative[2] = 0.0  # 每隻手的z參考原點不同，只保留相對x、y。
            features[128:131] = relative

        return FeatureResult(
            valid=True, features=features,
            featureVersion=config['feature_version'],
        )

```

## 5. KNN：同一份實作，建立三個分類器

每個通道各建立一個 StudentKNN，分別訓練、預測；不把一個分類結果硬拆成三個，也不將左右兩個合法動作壓成一個。下面方法由工具呼叫，學員不用自己寫網路或模型檔讀寫。

### B. KNN：找出最相似的樣本，再投票

KNN的想法是：新手勢像哪些已錄製的手勢，就讓最相似的k筆樣本投票。例如k=5，最近五筆的類別是 `[2, 2, 3, 2, 3]`，類別2得到三票，得票比例為 `3 / 5 = 0.6`。

我們分兩個函式完成：`fit` 保存訓練資料與設定；`predict` 比較一筆新資料、找鄰居、投票並決定是否接受分類。

#### 第1步：在fit保存訓練資料與設定

工具會提供以下參數：

| 參數 | 內容 |
|---|---|
| `features` | `(N, 131)` 陣列，每列是一筆正規化後的手勢；N是樣本數 |
| `labels` | `(N,)` 整數陣列，每筆對應同一列手勢的類別編號0～9 |
| `config` | 包含k、投票門檻與距離門檻的設定 |

`features[0]` 和 `labels[0]` 分別是第一筆手勢與它的正確類別。保存方式如下：

```python
self.training_features = features.copy()
self.training_labels = labels.copy()
self.k = config.get('k', 5)
self.vote_threshold = config.get('vote_threshold', 0.6)
self.distance_threshold = config.get('distance_threshold', 1.0)
```

`self` 代表目前的分類器物件。資料存到 `self` 上，之後的 `predict` 才能取得；只寫區域變數 `training_features = ...`，不會保存成物件屬性。

`config.get('k', 5)` 表示取得k，若沒有這個欄位就使用5。`fit` 不分類，也不需要自己寫模型檔；函式結束時回傳None即可。

#### 第2步：在predict計算每筆樣本的距離

`predict` 收到的 `features` 是一筆新手勢，形狀 `(131,)`。讓每筆訓練特徵減去它，再算每一列的長度：

```python
differences = self.training_features - features
distances = np.linalg.norm(differences, axis=1)
```

相减後仍是 `(N, 131)`；`axis=1` 表示沿每一列的131個數值計算，得到N個距離。這就是歐氏距離：差異的平方相加，再開平方。距離越小，表示兩筆正規化特徵越接近。

#### 第3步：取最近的k筆樣本

```python
order = np.argsort(distances, kind='stable')
neighbor_indices = order[:self.k]
neighbor_labels = self.training_labels[neighbor_indices]
```

`argsort` 回傳的是由近到遠排列的「樣本索引」，不是距離本身。例如距離是 `[0.8, 0.2, 0.5]`，索引順序就是 `[1, 2, 0]`。`[:self.k]` 取前k個，再用這些索引取得鄰居的類別。

`kind='stable'` 讓距離相同的樣本維持原本順序，結果較容易重現。

#### 第4步：統計票數，選出類別

```python
counts = np.bincount(neighbor_labels, minlength=len(LABELS))
class_id = int(np.argmax(counts))
ratio = float(counts[class_id] / self.k)
```

`bincount` 計算每個類別有幾票；`argmax` 取得票數最多的類別編號。這個基本版本遇到同票時，選編號較小的類別，因為 `argmax` 會取第一個最大值。之後也可以改成以候選類別的距離決勝。

`ratio` 是鄰居投票比例，**不是辨識準確率，也不是校準後的機率**。

#### 第5步：太遠或票數不集中，就拒絕分類

即使是沒錄過的姿勢，也一定找得到最近的樣本。因此不能只看誰票數最多，還要設定接受條件：

```python
distance = float(distances[neighbor_indices[0]])
valid = (
    distance <= self.distance_threshold
    and ratio >= self.vote_threshold
)
label = LABELS[class_id] if valid else 'NONE'
```

這裡要求「最近樣本夠近」和「得票比例夠高」兩項都通過。`LABELS[class_id]` 把編號轉成標籤字串，例如類別2對應 `JUMP`。拒絕時使用 `NONE`，表示現在沒有可接受的分類。門檻只能協助拒絕，不能保證所有未知手勢都會被拒絕。

#### KNN完整實作

把以下內容放進 `student/knn.py` 對應的方法。**沿用原檔的類別名稱與函式簽名**；下面以 `StudentKNN` 示範類別結構：

```python
import numpy as np
from core.labels import LABELS
from core.types import Prediction


class StudentKNN:
    def fit(self, features, labels, config):
        self.training_features = features.copy()
        self.training_labels = labels.copy()
        self.k = int(config.get('k', 5))
        self.vote_threshold = float(config.get('vote_threshold', 0.6))
        self.distance_threshold = float(config.get('distance_threshold', 1.0))
        return None

    def predict(self, features):
        differences = self.training_features - features
        distances = np.linalg.norm(differences, axis=1)

        order = np.argsort(distances, kind='stable')
        neighbor_indices = order[:self.k]
        neighbor_labels = self.training_labels[neighbor_indices]

        counts = np.bincount(neighbor_labels, minlength=len(LABELS))
        class_id = int(np.argmax(counts))
        ratio = float(counts[class_id] / self.k)
        distance = float(distances[neighbor_indices[0]])

        valid = (
            distance <= self.distance_threshold
            and ratio >= self.vote_threshold
        )
        label = LABELS[class_id] if valid else 'NONE'
        return Prediction(
            label=label,
            valid=valid,
            nearest_distance=distance,
            vote_ratio=ratio,
        )
```


## 6. 時間濾波（選做，各通道獨立）

### C. 濾波：快速確認新手勢，略過短暫跳動（選做）

先保持濾波關閉，確認KNN能辨識後再做。假設連續結果是「JUMP、JUMP、BLOCK、JUMP」，中間短暫的BLOCK可能只是抖動；每次分類一變就輸出，角色也會跟著跳動。

但如果每次換手勢都要等很久，玩家會覺得動作慢半拍。這裡使用**短時間加上連續次數確認**：新手勢至少連續兩次一致，最近連續兩次的投票比例都達0.8時，使用20ms門檻；其他結果使用50ms門檻。已確認的手勢可以持續輸出，短暫跳到另一個有效類別時最多保留原動作50ms；未知分類或無手時立即停止。

20ms與50ms是濾波的確認門檻，不是整個系統的反應時間。程式要等下一筆分類到來才能確認；鏡頭更新率、關鍵點偵測和網路傳送都會影響實際速度。

#### 第1步：分清楚候選與穩定輸出

濾波每次收到的是KNN回傳的 `prediction`，不是21個座標：

| 資料 | 用途 |
|---|---|
| `prediction.label` | 這次分類的標籤，例如 `JUMP` |
| `prediction.valid` | KNN是否接受這次分類 |
| `prediction.vote_ratio` | 最近鄰投給勝出類別的比例，例如0.8表示八成；不是辨識正確率 |
| `timestamp` | 這次更新的單調遞增時鐘秒數，不是影格編號或日期 |

先在 `__init__` 設定三個門檻，再呼叫 `reset()` 初始化狀態：

```python
self.hold_seconds = 0.05
self.fast_hold_seconds = 0.02
self.strong_vote = 0.8
self.reset()
```

`hold_seconds` 是一般確認時間，也用來限制保留舊動作的時間；`fast_hold_seconds` 是高投票比例的確認時間；`strong_vote` 是使用快速確認的投票門檻。

在 `reset()` 保存以下資料，下一次更新才能接著判斷：

| 狀態 | 用途 |
|---|---|
| `candidate` | 正在確認的新標籤，初始為None |
| `start_time` | 第一次看到目前候選的時間，初始為None |
| `frames` | 目前候選連續出現幾次，初始為0 |
| `strong_frames` | 目前候選最近連續幾次達到投票門檻，初始為0 |
| `stable_label` | 已確認、可以輸出的標籤，初始為NONE |
| `transition_start` | 開始離開穩定標籤的時間，初始為None |
| `last_timestamp` | 上一筆更新時間，初始為None |

`candidate` 和 `stable_label` 分開保存。例如已確認JUMP，接著只收到一次BLOCK：BLOCK是候選，但還不能直接把穩定輸出改成BLOCK。

#### 第2步：無效分類立即停止，舊資料不接著算

```python
if not math.isfinite(timestamp) or not prediction.valid or prediction.label == 'NONE':
    self.reset()
    return 'NONE'
```

未知分類不能延續上一個攻擊，所以要清除候選與穩定輸出，立即回傳NONE。`math.isfinite` 也會擋下無效時間值，檔案開頭記得加入 `import math`。無手時，共用工具會直接停止輸出並重設濾波，不會等待確認時間。

另外，時間倒退、重複使用同一時間，或兩筆更新相隔超過0.5秒，都不能把前一筆資料當成連續證據：

```python
if self.last_timestamp is not None and (timestamp <= self.last_timestamp or timestamp - self.last_timestamp > 0.5):
    self.reset()
self.last_timestamp = timestamp
```

例如鏡頭暫停後重新送來JUMP，必須重新確認，不能直接沿用暫停前的JUMP。

#### 第3步：已確認的手勢，直接繼續輸出

```python
if prediction.label == self.stable_label:
    self.candidate = None
    self.transition_start = None
    return self.stable_label
```

第一次看到JUMP時還沒有穩定輸出，需要往下確認；確認後，只要仍收到有效的JUMP，就直接回傳JUMP，不必每筆再等一次。

如果上一筆短暫變成BLOCK，這一筆又回到穩定的JUMP，也會清掉BLOCK候選及切換計時。這樣單次分類跳動就不會把動作切開。

#### 第4步：計算候選連續次數與投票比例

```python
if prediction.label != self.candidate:
    self.candidate = prediction.label
    self.start_time = timestamp
    self.frames = 1
    self.strong_frames = int(prediction.vote_ratio >= self.strong_vote)
else:
    self.frames += 1
    self.strong_frames = self.strong_frames + 1 if prediction.vote_ratio >= self.strong_vote else 0
```

候選改變時，從第一次開始計數。`int(True)` 是1，`int(False)` 是0，因此第一筆達到0.8就把 `strong_frames` 設成1，否則設成0。

候選相同時，`frames` 加1；投票比例達到門檻，`strong_frames` 才繼續累加。只要某次投票比例不足，就把高投票比例的連續次數歸零，但仍保留同一候選的一般次數與開始時間。

例如JUMP的投票比例依序為「0.6、1.0」，雖然標籤連續一致，仍不能使用快速門檻，因為只有最近一次達到0.8。

#### 第5步：次數與時間都通過，才確認新手勢

```python
elapsed = timestamp - self.start_time
hold = self.fast_hold_seconds if self.strong_frames >= 2 else self.hold_seconds
if self.frames >= 2 and elapsed >= hold:
    self.stable_label = self.candidate
    self.transition_start = None
    return self.stable_label
```

這裡有兩個條件：**同一候選至少連續兩次，而且從候選開始到現在已達到確認時間。** 單筆結果就算投票比例是1.0，也不能直接通過。

假設鏡頭每秒更新30次，兩筆約相隔33ms：

| 時間 | 分類與投票比例 | 輸出 |
|---|---|---|
| 12.000秒 | JUMP，0.8 | NONE，先記錄候選 |
| 12.033秒 | JUMP，0.8 | JUMP，連續兩次且超過20ms |
| 12.066秒 | JUMP，0.8 | JUMP，已確認，直接延續 |

如果每筆的投票比例都是0.6，第二筆只有33ms，還沒達到一般50ms門檻；第三筆約66ms才會通過。更新率較高時，也可能需要超過兩筆才能累積20ms，所以不能只用影格數來代替時間。

#### 第6步：短暫跳動保留舊動作，但不能一直保留

新候選還沒確認時，如果之前已有穩定輸出，就給短暫跳動一個小空檔：

```python
if self.stable_label != 'NONE':
    if self.transition_start is None:
        self.transition_start = timestamp
    if timestamp - self.transition_start < self.hold_seconds:
        return self.stable_label
return 'NONE'
```

例如已確認JUMP，接著只有一次BLOCK，再回到JUMP：短暫的BLOCK期間先回傳原本的JUMP，回到JUMP後繼續輸出。若BLOCK連續出現並通過確認，就改成BLOCK。

`transition_start` 只在第一次離開穩定標籤時設定，不能每次候選改變就重算。否則候選一直在BLOCK、CROUCH、MOVE_RIGHT之間跳動，舊的MOVE_LEFT可能永遠停不下來。從開始切換滿50ms的那筆更新起，若仍沒確認新候選，就回NONE；沒有新更新時，共用輸出也會在0.5秒後失效。

這段只保留**有效分類之間的短暫跳動**。收到未知分類或手離開畫面，仍由第2步或共用工具立即停止，不會保留舊動作。

#### 濾波完整實作

以下整段放進 `student/filtering.py`，**沿用原有類別名稱與函式簽名**。不要在同一類別中留下兩份 `update` 或 `reset`：

```python
import math
from core.types import Prediction


class StudentFilter:
    def __init__(self):
        self.hold_seconds = 0.05
        self.fast_hold_seconds = 0.02
        self.strong_vote = 0.8
        self.reset()

    def reset(self):
        self.candidate = None
        self.start_time = None
        self.frames = 0
        self.strong_frames = 0
        self.stable_label = 'NONE'
        self.transition_start = None
        self.last_timestamp = None
        return None

    def update(self, prediction: Prediction, timestamp: float) -> str:
        if not math.isfinite(timestamp) or not prediction.valid or prediction.label == 'NONE':
            self.reset()
            return 'NONE'

        # 暫停或時間重設後，不能沿用舊影格的確認結果。
        if self.last_timestamp is not None and (timestamp <= self.last_timestamp or timestamp - self.last_timestamp > 0.5):
            self.reset()
        self.last_timestamp = timestamp

        if prediction.label == self.stable_label:
            self.candidate = None
            self.transition_start = None
            return self.stable_label

        if prediction.label != self.candidate:
            self.candidate = prediction.label
            self.start_time = timestamp
            self.frames = 1
            self.strong_frames = int(prediction.vote_ratio >= self.strong_vote)
        else:
            self.frames += 1
            self.strong_frames = self.strong_frames + 1 if prediction.vote_ratio >= self.strong_vote else 0

        elapsed = timestamp - self.start_time
        hold = self.fast_hold_seconds if self.strong_frames >= 2 else self.hold_seconds
        if self.frames >= 2 and elapsed >= hold:
            self.stable_label = self.candidate
            self.transition_start = None
            return self.stable_label

        # 短暫有效分類跳動時保留原動作，但切換計時不能一直重來。
        if self.stable_label != 'NONE':
            if self.transition_start is None:
                self.transition_start = timestamp
            if timestamp - self.transition_start < self.hold_seconds:
                return self.stable_label
        return 'NONE'
```

#### 實測與調整

保存後重開工具，勾選「使用學員濾波（選做）」，比較關閉與開啟時的反應。不需要重新訓練KNN，因為這次修改的是分類後的輸出流程。

先測固定手勢，再測快速切換、短暫分類跳動、未知手勢及手離開畫面。穩定動作應能持續輸出，新手勢確認後應切換，未知或無手時應立即停止。

如果動作仍慢，先看KNN的原始分類是否已經穩定，再調整 `hold_seconds` 或 `fast_hold_seconds`；如果常誤切換，可以增加確認時間，或提高 `strong_vote`。每次只改一個參數並記錄結果，保留至少連續兩次確認；也記得 `hold_seconds` 同時控制舊動作的保留時間。


## 7. 在 UI 訓練、測試、查看同時輸出

1. 完成正規化與 KNN 後保存檔案，重開工具。濾波先保持關閉。
2. 到「2. 錄製與訓練」按「訓練」。工具依批次通道建立三個 KNN 分類器，保存到 `models/model.npz`，並自動載入。
3. 按「測試」；只使用另錄的 test 批次，報告保存到 `models/evaluation.json`，分別列出各通道的樣本數、準確率與混淆矩陣。
4. 到「1. 鏡頭與辨識」，開鏡頭，切成「辨識並傳送」。這時還不必連線就能看三欄輸出。
5. 左手做 MOVE_LEFT、右手做 NORMAL_ATTACK，應看到 `left=MOVE_LEFT / right=NORMAL_ATTACK / both=NONE`。
6. 做雙手 BLOCK，應看到 `left=NONE / right=NONE / both=BLOCK`。雙手合成確認期間也不會偷跑單手動作。
7. 只移開左手，right 仍應維持可辨識的合法動作；全部無手時三欄都回 NONE。
8. 下次重開，只需按「載入三通道模型」。改變特徵或 KNN 設定後需要重訓，不能直接套用不相容舊模型。

進階驗證不只看模型分類：獨立測試會檢查最後的三欄路由；若單手被錯誤的雙手分類搶走，也會算錯。KNN 投票比例不是準確率，請另看 test 與真人操作。

## 8. 連上新版競技場

網站：[https://ga-game.codpy.org/](https://ga-game.codpy.org/)。先完成自己的算法、訓練模型、開鏡頭，切換到「辨識並傳送」；「連線遊戲」會顯示哪些步驟尚未完成。

### PVE 一命連戰／假人練習：不需要房號

1. 在網站選 PVE「一命連戰」或「假人練習」。
2. 控制來源選「手勢辨識器」，按「產生配對碼」。
3. 工具「3. 連線遊戲」選相同玩法；主機網址保留 `https://ga-game.codpy.org`，房號留空。
4. 輸入自己網頁當下顯示的六位數配對碼，例如 `012345`；保留開頭的 0，按「配對辨識器」。
5. 成功後按鈕變成「解除配對」。回網站按「確認準備」，選完技能後倒數開戰。
6. PVE 按「結束挑戰」會保存未完成紀錄並離開房間；再次遊玩時重新產生配對碼並配對。

### PVP 雙人對決：房號與配對碼不同

1. 一位玩家在網站建立「雙人對決」，把六位數字房號提供給朋友，例如 `123456`。
2. 朋友輸入房號、加入同一房間。每位手勢玩家各自在自己的網頁選「手勢辨識器」、產生自己的配對碼。
3. 工具選「PVP 雙人對決」，房號填網站的實際值，例如 `123456`（選填）；配對碼填自己的六位數值。
4. 兩位玩家使用同一房號，**各自使用不同的配對碼**，不要把朋友的配對碼填到自己的工具。
5. 雙方配對成功後，回網站各按「確認準備」，自動倒數、選技與開戰。觀戰者不必啟動辨識器。

房號只用來加入同一房間；配對碼用來連接自己的 Python 辨識器。網址不用加 `/controller`。配對碼過期、離開房間或解除配對後需重新產生。使用本地主機時，網站與工具都改用該主機的網址，例如 `http://127.0.0.1:3000` 或主機區網位址。

### 與 Demo／initial 相同的指令規則

- 每幀辨識三個通道；left、right 可同時送出，both 獨占。
- 指令變化（包含 NONE）立即傳送，相同狀態約每秒補送 10 次；不等待逐包 ACK 才繼續辨識。影像預覽約每 150ms 傳一次，沿用同一支攝影機。
- 開戰、重置、恢復或換關後先送中立狀態；缺手、低可信度或失聯時清除相關輸出。
- 移動、蹲下、防禦可持續；跳躍、普攻與技能在進入指令時觸發，需離開該手勢至少 0.1 秒才能再做，維持手勢不會連發。
- 冷卻、氣量、硬直、大招解鎖、左右相反移動抵銷等規則由同一伺服器判定，不因使用 GUI 而改變。
- 網站氣條下方有四個小型技能時鐘，鏡頭在技能列下方。收到指令不等於成功施放；工具與網站會顯示等待開戰、中立檢查、硬直、冷卻、氣量不足等原因。

## 9. 檔案、設定與檢查

| 位置 | 用途 | 學員是否需要改 |
| --- | --- | --- |
| student/normalization.py | 把一幀手部資料變成固定長度特徵 | 要，複製第 4 節範例後理解並調整 |
| student/knn.py | 單一分類器的 fit／predict；工具建立三個實例 | 要，第 5 節完整範例 |
| student/filtering.py | 每個通道各一份時間歷史 | 選做，第 6 節完整範例 |
| core/channel_model.py | 三個訓練銀行、載入與獨立測試 | 不用 |
| core/channel_router.py | 左右獨立、雙手優先、缺手清除 | 不用 |
| network/commands.py、arena_client.py、preview.py | 原子三欄輸出、配對、心跳、網站鏡頭 | 不用 |
| ui/app.py | 鏡頭、錄製、訓練及配對介面 | 不用 |
| data/、models/ | 自己的錄製資料和三通道模型 | 請自行備份，不上傳 GitHub |

`config.example.json` 的 k 預設 5、最近距離門檻 1.0、投票門檻 0.6，濾波預設關閉。可複製成 `config.json` 覆寫；本工具使用該檔的設定。修改正規化、左右手設定或 KNN 參數後，請重開工具、重訓並測試；只切換濾波不必重訓。

Windows 執行共用工具測試：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

`student` 的 TODO 測試顯示 skipped，表示尚未實作，不能當成算法通過。README 的範例也有測試，但測試不會把答案寫進 student 檔案。仍需使用自己的資料與真人操作驗證。

| 現象 | 檢查方式 |
| --- | --- |
| 找不到 Python 3.13 | 先安裝 Python 3.13；Windows 確認 `py -3.13 --version` 可用，macOS／Linux 確認 `python3.13 --version` 顯示 3.13.x |
| 缺少套件或裝好仍無法匯入 | 用專案 `.venv` 的 Python 重新安裝 `requirements-lock.txt`，確認安裝與啟動使用同一個環境 |
| 缺少關節模型或雜湊不符 | 執行 `main.py prepare`；若既有檔案損壞，移除 `assets/models/hand_landmarker.task` 後重新下載 |
| GUI 無法開啟或缺少 Tkinter | 確認使用本機桌面環境；Linux 安裝與所用 Python 相符的 Tk 套件，中文字型問題見第 1 節 |
| 鏡頭無法開啟 | 檢查系統攝影機權限、其他程式是否占用，並在停止鏡頭後更換鏡頭索引 |
| 鏡頭有畫面，卻一直說算法未完成 | 先完成 student 範例、保存並重開工具；錄製成功不代表算法已完成 |
| 某通道沒有訓練資料 | 選正確通道重新錄製；left 需左手、right 需右手、both 需兩手 |
| 顯示舊批次／舊模型 | 備份舊資料，使用新版 UI 另錄三通道資料並重訓；不會自動把舊單通道模型升級 |
| 模型已載入但一直 NONE | 確認選「辨識並傳送」、相應的手完整入鏡，並檢查 KNN 距離與投票門檻 |
| 已配對，網站不能準備 | 查看「連線遊戲」的鏡頭、模式、模型與算法狀態，先完成實作和訓練 |
| 有收到指令但沒有動作 | 查看執行回饋與網站冷卻時鐘，區分暫停、硬直、氣量不足或需要回中立 |
| 手勢維持著卻不連續攻擊 | 先離開該指令至少 0.1 秒，再做一次；這是所有玩家共同的觸發規則 |
| 右手被左手消失影響 | 新版左右通道獨立；檢查自己的 normalizer 是否錯把缺任一手當作全部無效 |
| 延遲或 FPS 偏低 | 先關閉不必要的攝影機程式；看工具底部 FPS／辨識耗時，並分別檢查分類穩定度與網路 |

UI 是完整新版功能的另一個入口，並非自動完成作業的辨識器；模型準確度仍取決於自己錄的資料和實作。

## 指令速查

所有指令都在含 `main.py` 的專案資料夾執行。下表以已啟用 `.venv` 的 `python` 為例；未啟用時，Windows 換成 `.\.venv\Scripts\python.exe`，macOS／Linux 換成 `./.venv/bin/python`。可用 `python main.py --help` 查看可用子命令。

| 指令 | 用途 |
| --- | --- |
| `python main.py prepare` | 下載並驗證 MediaPipe 關節模型 |
| `python main.py check` | 檢查依賴、關節模型載入與資料夾寫入，不開鏡頭 |
| `python main.py gui` | 開啟完整圖形介面 |
| `python main.py record` | 開啟同一個 GUI，直接選取「錄製與訓練」分頁 |
| `python main.py train` | 讀取 `data/` 的 train 批次，訓練並保存 `models/model.npz` |
| `python main.py test` | 讀取 `data/` 的 test 批次與已保存模型，在終端機輸出 JSON 報告；GUI 的「測試」按鈕另會保存 `models/evaluation.json` |

本版鏡頭預覽與遊戲配對都在 GUI 操作，沒有 initial 的 `camera`、`run` 子命令，也不接受其 `--label`、`--channel` 或 `--pair-code` 參數；請依第 2、3、8 節操作。

`data/`、`models/` 的輸出已由 `.gitignore` 排除，備份或交付時請另外確認；MediaPipe 關節模型可用 `prepare` 準備。配對後會將縮小的鏡頭影像與手部骨架送到同場網站預覽；錄製的完整關節資料保存在本機。
