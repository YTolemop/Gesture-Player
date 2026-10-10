# 手勢訓練器：從第一筆資料到控制競技場

你會用自己的右手，教電腦認識十種姿勢，再用它們控制遊戲。

**第一次使用，照順序做就好：下載 → 安裝 → 錄手勢 → 寫算法 → 訓練與測試 → 配對。**

先記住兩件事：只用右手，左手要離開畫面；錄製保存的是手部關鍵點，不是影片。算法還沒寫好也能先錄資料。

## 你現在要做哪一步？

- [1. 下載專案，用VS Code開啟](#step-1)
- [2. 安裝Python與套件](#step-2)
- [3. 開啟工具，確認鏡頭](#step-3)
- [4. 錄下十種手勢](#step-4)
- [5. 完成正規化、KNN與選做濾波](#step-5)
- [6. 訓練並試試辨識效果](#step-6)
- [7. 連上競技場](#step-7)
- [遇到問題時看這裡](#help)

<a id="step-1"></a>
## 1. 下載專案，用VS Code開啟

1. 開啟 [GitHub專案](https://github.com/YTolemop/Gesture-Player)，按 **Code → Download ZIP**。
2. 完整解壓縮到自己的資料夾，不要在壓縮檔裡直接執行。
3. 安裝並開啟 [VS Code](https://code.visualstudio.com/)。選「檔案 → 開啟資料夾」，開啟解壓後的 **Gesture-Player-main** 資料夾（直接包含main.py）。
4. 在VS Code的擴充套件頁搜尋 **Python**，安裝發布者為 **Microsoft** 的版本。
5. 選「終端機 → 新增終端機」。接下來的命令都在這裡輸入。

**完成時：** 左側看得到 `main.py`、`student`、`README.md`，下方有終端機。Windows用PowerShell，Mac／Linux用zsh或bash。如果看不到GitHub專案，請老師確認你的帳號有存取權限。

<details>
<summary>已經會使用Git？也可以這樣下載</summary>

```bash
git clone https://github.com/YTolemop/Gesture-Player.git
cd Gesture-Player
```

再用VS Code開啟Gesture-Player即可。

</details>

<a id="step-2"></a>
## 2. 安裝Python與套件

VS Code是寫程式的工具；Python負責執行程式，所以兩者都需要安裝。

### 先選你的電腦

| 你的系統 | 要準備什麼 |
|---|---|
| Windows x64 | [Python 3.13.2](https://www.python.org/downloads/release/python-3132/) 的Windows 64-bit installer；安裝時勾 **Add python.exe to PATH** |
| Mac（M系列晶片） | 同一官方頁面的macOS installer；使用原生Apple Silicon環境 |
| Linux x86_64 | 請老師先協助安裝Python 3.13.2、venv與Tk；下方有Linux補充 |

目前Windows已實機驗證；Mac與Linux仍需課前實機確認。Intel Mac與Linux ARM目前缺少鎖定版本的[MediaPipe安裝包](https://pypi.org/project/mediapipe/0.10.32/#files)，使用這些設備請先找老師，不要做到安裝一半才換版本。

### 在終端機建立環境

**只使用自己系統那一組命令，一行一行執行。** 遇到錯誤先停下來，把終端訊息給老師看。

Windows先確認版本，再建立環境：

```powershell
python --version
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-lock.txt
& '.\.venv\Scripts\python.exe' main.py prepare
& '.\.venv\Scripts\python.exe' main.py check
```

Mac／Linux使用：

```bash
python3.13 --version
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r requirements-lock.txt
./.venv/bin/python main.py prepare
./.venv/bin/python main.py check
```

第一行應顯示 **Python 3.13.2**。`.venv` 就是本專案自己的Python環境；`requirements-lock.txt` 列出要安裝的套件與版本。只在第一次使用或重建環境時做這一段，不需要每次開工具都重做。

**完成時：** 左側多出`.venv`，最後的檢查顯示 `model_load: PASS`。`camera: NOT_RUN`只是還沒開鏡頭；`student_algorithms: TODO`表示算法等你完成，都不是安裝失敗。

### 讓VS Code選對Python

按 **Ctrl+Shift+P**（Mac為 **Cmd+Shift+P**），搜尋 **Python: Select Interpreter**，選本專案的.venv。找不到時用 **Enter interpreter path** 指定：

| 系統 | 解譯器位置 |
|---|---|
| Windows | `.venv\Scripts\python.exe` |
| Mac／Linux | `.venv/bin/python` |

本文件直接指定.venv的Python，不需要另外Activate，也不需要修改PowerShell執行政策。每台電腦自行建立.venv，不複製別人的環境。

<details>
<summary>Linux安裝補充（可請老師協助）</summary>

使用有桌面的本機環境，Linux x86_64需glibc至少2.28。若使用pyenv，先依[官方建置需求](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)安裝編譯與Tk開發套件，再建立Python。已安裝pyenv時：

```bash
pyenv install 3.13.2
pyenv local 3.13.2
```

Ubuntu／Debian常見的GUI、影像與音訊元件如下；不是完整的Python編譯依賴清單，其他發行版名稱不同：

```bash
sudo apt update
sudo apt install tk-dev python3-tk libgl1 libglib2.0-0 libportaudio2
```

若pyenv只提供python命令，確認`python --version`是3.13.2，再用`python -m venv .venv`。Tk建置缺失時，要修正所用Python，不能只在.venv用pip補裝。

</details>

<a id="step-3"></a>
## 3. 開啟工具，確認鏡頭

之後每次開啟，只要用這一行。

**Windows PowerShell**

```powershell
& '.\.venv\Scripts\python.exe' main.py gui
```

**Mac／Linux**

```bash
./.venv/bin/python main.py gui
```

1. 在「即時辨識」頁，模式先保持 **preview**（預覽）。
2. 鏡頭索引先選0，按「開啟鏡頭」。
3. 把右手完整放進畫面，確認手上有點與連線。
4. 看右側採集頁的偵測文字，確認自己的右手被標為右手。

**完成時：** 鏡頭畫面會更新，右手有關鍵點。此時NONE正常，因為還沒完成分類算法。

想換鏡頭：先按「停止鏡頭」，再試索引1、2、3，然後重新開啟。左右手標籤反轉或黑畫面，先看[排錯表](#help)，確認好再錄資料。

<a id="step-4"></a>
## 4. 錄下十種手勢

先為每一類想一個**不同的右手固定姿勢**，把對應記下來。例如張開五指代表移動、握拳代表蹲下；這只是例子，你可以自行設計。

| 類別編號 | 標籤 | 遊戲動作 |
|---|---|---|
| 0 | MOVE_LEFT | 向左移動 |
| 1 | MOVE_RIGHT | 向右移動 |
| 2 | JUMP | 跳躍 |
| 3 | CROUCH | 蹲下 |
| 4 | BLOCK | 格擋 |
| 5 | NORMAL_ATTACK | 普通攻擊 |
| 6 | ATTACK_SKILL | 攻擊技能 |
| 7 | DEFENSE_SKILL | 防禦技能 |
| 8 | CONTROL_SKILL | 控制技能 |
| 9 | ULTIMATE | 大招 |

`JUMP`和`CROUCH`是遊戲動作，不需要你本人跳起來或蹲下。錄製時保持姿勢，不要揮手。只把相同姿勢移到畫面左右或改變遠近，不適合當不同類；我們之後會消除這些差異。

### 先完成一個類別，再換下一個

1. 到「採集/訓練」，選一個「錄製類別」，用途選 **train**。
2. 按「開始錄製」，倒數三秒期間擺好右手。
3. 保持姿勢約10～15秒，可以輕微改變位置、距離；確認「有效」筆數增加。
4. 按「停止錄製」，資料會自動保存，列表出現類別、用途、筆數與時間。
5. 同一類改成 **test**，先放下手，再重新擺出姿勢錄一次並保存。
6. 換下一類，直到十類都有train與test。

**train是讓模型學習的資料；test是考它是否學會的新資料。** 兩次分開錄，不要把同一段連續影格拆成兩份，否則分數容易看起來很好，實際卻認不準。

**完成時：** 資料列表中，每一類至少有一筆train和一筆test。筆數不是準確率保證，可以等測試後再補錄。需重錄時選對那列，按「刪除所選資料」。

保存位置是`data/`，每次有一個.npz（關鍵點、類別）和同名.json（用途等資訊）。這時不用按訓練，先完成下一步的算法。

<a id="step-5"></a>
## 5. 完成三個算法

你要接手的是這段流程：

```text
右手21個點 → 正規化成63個數值 → KNN判斷手勢 → 可選濾波 → 競技場
```

只修改下面三個檔案。保留已有的類別、函式名稱與參數，將`raise NotImplementedError(...)`換成你的實作；不需要另寫main或自己呼叫鏡頭、資料讀取與網路。

| 順序 | 檔案與函式 | 你要做的事 | 完成後交回什麼 |
|---|---|---|---|
| 先寫 | `student/normalization.py` 的transform | 消除位置與大小差異，保留方向 | `FeatureResult`，含63個float32數值 |
| 再寫 | `student/knn.py` 的fit、predict | 保存資料，找相似樣本並分類 | fit回None；predict回`Prediction` |
| 選做 | `student/filtering.py` 的update、reset | 減少標籤跳動，清除舊狀態 | update回標籤字串；reset回None |

**資料已經透過參數送進函式。** 正規化用sample，KNN用features／labels，濾波用prediction。你不用自己打開data檔案，也不用把結果傳到競技場；工具會接住return的結果。

### A. 正規化：先知道去哪裡拿座標

最重要的資料是`sample.right`，它是一張21列、3欄的數值表，每一列是一個點的xyz。

```python
hand = sample.right
wrist = hand[0]
middle_mcp = hand[9]
width = sample.width
height = sample.height
```

`np.asarray(sample.right, dtype=np.float64)`只是把資料轉成指定格式方便計算，**不是讀檔，而且不一定要用這個寫法**。算法要解決的問題是：同一姿勢移到別處、靠近鏡頭變大，仍然能比較。

<details>
<summary>開始寫正規化時，展開看資料欄位、NumPy用法與return格式</summary>

#### 正規化：取得右手資料，回傳特徵

檔案：`student/normalization.py`。

```python
from core.types import RawHandSample, FeatureResult
import numpy as np

class StudentNormalizer:
    def transform(self, sample: RawHandSample, config: dict) -> FeatureResult:
        # Read sample, compute features, then return the result.
        raise NotImplementedError('Implement normalization')
```

`sample` 是工具已經傳進來的「一筆手部資料」，不是檔名。冒號後的 `RawHandSample` 是型別提示；`-> FeatureResult` 說明預期回傳型別，不會自動替你計算。工具已確認只有右手、尺寸有效、21點為有限值、手掌尺度至少10px，因此不需要在學員算法內重複這些檢查。

| 想取得什麼 | 寫法 | 資料意思 |
|---|---|---|
| 右手全部關鍵點 | `sample.right` | NumPy 陣列，形狀 `(21, 3)` |
| 畫面寬、高 | `sample.width`、`sample.height` | 像素數，例如640、480 |
| 手腕的xyz | `sample.right[0]` | 第0點，形狀 `(3,)` |
| 中指根部的xyz | `sample.right[9]` | 第9點，形狀 `(3,)` |
| 全部點的x | `sample.right[:, 0]` | 21個x；`:` 代表全部列 |
| 全部點的y或z | `sample.right[:, 1]`、`sample.right[:, 2]` | 第1、2欄 |
| 特徵版本 | `config['feature_version']` | 回傳時原樣帶回，勿另寫版本字串 |

`sample.right` 本來就能計算，**不一定要寫 `np.asarray`**。如果希望指定計算精度，可用：

```python
points = np.asarray(sample.right, dtype=np.float64)
```

這行只是「將右手資料當成 NumPy 陣列，使用64位元浮點數計算」，不是讀取錄製檔案，也不是呼叫 MediaPipe。`np` 來自 `import numpy as np`；`sample.right` 來自函式參數。不要直接修改輸入座標，需要獨立副本時使用 `sample.right.copy()`。

原始x、y是畫面比例；z使用寬度尺度。正規化的目標是：換成一致單位、消除手的位置與大小影響、保留手勢方向，最後整理成63個值。以下是可使用的工具，不限定你必須使用哪一種寫法：

| 用途 | Python / NumPy 寫法 |
|---|---|
| 建立數值陣列 | `np.array([a, b, c])` |
| 所有點減同一個xyz | `points - origin`，其中origin形狀為 `(3,)` |
| 向量長度 | `np.linalg.norm(vector)` |
| 全部數值除以同一尺度 | `points / scale` |
| 21×3攤平 | `points.reshape(63)` 或 `points.reshape(-1)` |
| 轉成接口要求的格式 | `values.astype(np.float32)` |
| 查看形狀、數值格式 | `values.shape`、`values.dtype` |

完成計算後，假設你的結果變數叫 `features`，回傳：

```python
return FeatureResult(
    valid=True,
    features=features,  # Finite float32 array, shape (63,)
    featureVersion=config['feature_version'],
)
```

若你自行設計的算法決定拒絕某筆資料，可回傳：

```python
return FeatureResult(
    valid=False,
    features=None,
    reason='Reason for rejection',
    featureVersion=config['feature_version'],
)
```

工具取用 `result.features`；只 `print(features)`、回傳普通list或只回傳陣列，都不符合接口。

</details>

### B. KNN：先保存，再比較

`fit`收到所有訓練特徵與正確類別；`predict`收到一筆新特徵。兩者透過`self`共用你保存的資料。

```python
self.training_features = features.copy()
self.training_labels = labels.copy()
```

屬性名稱由你決定，前後使用一致即可。接著自行設計距離、最近鄰居、投票、同票規則與拒絕未知手勢的條件。`NONE`代表現在沒有可接受的分類，不要硬把所有姿勢塞進十類。

<details>
<summary>開始寫KNN時，展開看資料形狀、常用操作與Prediction格式</summary>

#### KNN：保存訓練特徵，再判斷一筆新特徵

檔案：`student/knn.py`。需要 `import numpy as np`、`from core.labels import LABELS`、`from core.types import Prediction`。

`fit(self, features, labels, config)` 的參數已由工具提供，不要自行讀 data：

| 參數 | 內容 | 讀取示例 |
|---|---|---|
| `features` | float32 `(N, 63)`，N是訓練樣本數 | `features[0]` 是第一筆；`features.shape[0]` 是筆數 |
| `labels` | 整數 `(N,)`，每筆對應類別0～9 | `labels[0]` 是第一筆的正確類別 |
| `config` | KNN設定 | `config.get('k', 5)`：讀k，未設定則用5 |

`fit` 和 `predict` 是同一個物件的不同方法。若要讓 `predict` 之後拿得到訓練資料，需要存在 `self` 上。例如：

```python
self.training_features = features.copy()
self.training_labels = labels.copy()
```

這兩個屬性名稱由你決定，但 `predict` 必須用相同名稱。只寫 `training_features = ...` 是區域變數，函式結束後其他方法無法透過 `self` 取得。`fit` 完成後不需回傳分類，也不用自己存模型檔；回傳值為 None。

`predict(self, features)` 收到的是**一筆**新特徵，形狀 `(63,)`，不是fit的整張資料表。你的工作是比較距離、選鄰居、投票，並決定是否拒絕未知姿勢。

| 想做什麼 | 可用寫法 |
|---|---|
| 每筆訓練資料與新特徵相減 | `self.training_features - features` |
| 每列向量的長度 | `np.linalg.norm(differences, axis=1)` |
| 由小到大取得索引 | `np.argsort(distances, kind='stable')` |
| 取前k個索引 | `indices[:k]` |
| 按索引取類別 | `self.training_labels[indices]` |
| 統計各編號票數 | `np.bincount(neighbor_labels, minlength=10)` |
| 類別編號轉成標籤字串 | `LABELS[class_id]`，例如0對應MOVE_LEFT |

以上 `differences`、`distances`、`indices`、`k` 等都要先由你計算或定義。距離、同票規則與拒絕門檻由你設計。設定中可讀 `distance_threshold`、`vote_threshold`；門檻不等於準確率保證。

最後必須回傳 `Prediction`，假設你已算出對應變數：

```python
return Prediction(
    label=label,                    # A label from LABELS, or NONE
    valid=valid,                    # True to accept, False to reject
    nearest_distance=distance,      # Non-negative finite distance, or None
    vote_ratio=ratio,               # Vote ratio from 0 to 1
)
```

若拒絕未知姿勢，可用 `Prediction(label='NONE', valid=False, nearest_distance=distance, vote_ratio=ratio)`。不能只回傳編號或字串。工具使用這個結果做評估，再傳入濾波或輸出。

</details>

### C. 濾波：辨識可以用之後再做

先保持濾波關閉。當KNN已能辨識，再思考怎麼讓結果穩定：例如某分類要持續一段時間才輸出。濾波收到的是分類結果，不是手部座標。

<details>
<summary>選做濾波時，展開看時間、歷史狀態與return格式</summary>

#### 濾波：讀取分類結果，回傳穩定標籤

檔案：`student/filtering.py`。需要 `from core.types import Prediction`。濾波啟用時，工具才呼叫 `update(self, prediction, timestamp)`。

| 想取得什麼 | 寫法 |
|---|---|
| KNN的分類 | `prediction.label`，例如'MOVE_LEFT' |
| KNN是否接受結果 | `prediction.valid` |
| 最近距離、投票比例 | `prediction.nearest_distance`、`prediction.vote_ratio` |
| 這次更新時間 | `timestamp`，本機monotonic秒數，不是影格編號 |
| 經過多久 | `timestamp - self.start_time`，開始時間要先自行保存 |

你不需要重新計算關鍵點或呼叫KNN。這個函式只決定「現在要輸出哪個標籤」。跨次更新的歷史必須保存在 `self` 上，可以是候選標籤、開始時間或其他狀態，名稱由你決定。

`reset(self)` 要把你用到的歷史清空，回傳 None；可在 `__init__` 呼叫 `self.reset()` 完成初始化。`update` 最後回傳**標籤字串**，例如 `return prediction.label` 或 `return 'NONE'`，不回傳 Prediction、FeatureResult或編號。這些只是回傳格式示例，不是完整濾波策略。

可自行設計持續時間或投票窗口，但未知分類需停止輸出，重設後不能保留舊攻擊。無手與超過0.5秒沒有新結果的安全輸出由共用工具負責。

</details>

### 寫完後，先跑接口測試

「接口」就是輸入和輸出的約定。測試幫你確認工具接得住結果，不代表真人準確率已通過。

**Windows PowerShell**

```powershell
& '.\.venv\Scripts\python.exe' -m pytest tests/test_student_contracts.py
```

**Mac／Linux**

```bash
./.venv/bin/python -m pytest tests/test_student_contracts.py
```

看到`passed`表示該項通過；`skipped`表示算法可能還是TODO。濾波選做，沒有啟用時可以暫時跳過；正規化與KNN必須完成。看到failed就先修正錯誤，再繼續。

<a id="step-6"></a>
## 6. 訓練並試試辨識效果

1. 保存程式，關閉工具再重新開啟，讓它載入新程式。
2. 在「採集/訓練」按 **訓練**。工具只使用train資料，成功後會自動載入模型。
3. 按 **測試**，使用test檢查模型。報告會存成`models/evaluation.json`。
4. 到「即時辨識」，開鏡頭，把preview改成 **recognize**（辨識）。
5. 逐一做十個姿勢，再把手移出畫面，確認停止輸出。

**完成時：** `models/`出現`knn.npz`和`knn.json`，即時畫面能顯示分類。下次重開工具，要先按「載入KNN模型」，不必每次重新訓練。

報告中的混淆矩陣是「正確答案和模型回答」的對照：列是正確類別，欄是預測類別，最後一欄是NONE。若分不清兩類，先確認姿勢是否太相似、標籤是否錄錯，再補資料或調參數。

選做濾波完成後，才勾「使用學員濾波」，比較穩定度與延遲。修改程式要重開工具；補錄、刪資料或改分類設定後要重新訓練。

<a id="step-7"></a>
## 7. 連上競技場

先向老師取得競技場網址。同一台電腦可用`http://localhost:3000`；學員自己的筆電要使用老師主機的區網IP，例如`http://192.168.1.100:3000`。

1. 網站進「假人練習」，控制來源選「手勢辨識器」，按「產生配對碼」。
2. Python工具載入模型、開鏡頭、切recognize，先做一個手勢確認分類可用。
3. 到「配對」填主機網址和配對碼；單人練習房間碼留空。
4. 按「配對」。成功後按鈕會變成「解除配對」。
5. 網站顯示辨識器已連線、算法可用後，按「確認準備」，選技能並等待倒數。
6. 試左右移動、普通攻擊與技能；最後把手移開，確認角色停止接收動作。

**完成時：** 你能用右手姿勢操作角色。相機影像與採集資料留在本機，送到競技場的是分類標籤。

## 想改善辨識？再調整KNN參數

學員可以調整 `k`、`vote_threshold`、`distance_threshold`。先將 `config.example.json` 複製成同一資料夾內的 `config.json`，再修改個人設定；程式有config.json時優先讀它，否則使用範例設定。JSON數值不要加引號，並保留正確逗號格式。

| 參數 | 預設值 | 允許範圍與用途 |
|---|---|---|
| `k` | 5 | 正整數，不可超過實際可用的訓練樣本數；決定取幾個最近鄰居投票 |
| `vote_threshold` | 0.6 | 0～1；最低得票比例，越高越要求鄰居分類一致，可能增加NONE |
| `distance_threshold` | 1.0 | 非負有限數值；最近距離的拒絕門檻，越小越嚴格，可能增加NONE。單位是正規化特徵距離，不是像素或公分 |

例如k=5、vote_threshold=0.6時，至少3個鄰居投同一類才符合投票條件；是否接受分類仍取決於你實作的距離拒絕規則。不要把投票比例當成實際辨識準確率。

**設定不會自動替你實作算法。** 你的 `fit` 必須讀取設定並存到self，`predict` 必須實際使用它們。可用的讀取方式：

```python
config.get('k', 5)
config.get('vote_threshold', 0.6)
config.get('distance_threshold', 1.0)
```

`get` 的第二個參數是欄位缺少時的預設值；只有呼叫get而沒有保存、使用結果，不會改變分類行為。若在算法中把k或門檻寫死，修改JSON也不會生效。

修改後依序：

1. 保存config.json，關閉並重開工具，讓設定重新載入。
2. 按「訓練」，以新設定重新建立並載入模型；目前模型相容檢查包含這些參數，舊模型不能直接用新設定載入。
3. 按「測試」，比較獨立test結果，再做即時辨識。

建議每次只改一個參數並記錄結果。只調KNN參數通常不用重新採集；修改正規化特徵定義則需要重新計算特徵並訓練。右手單手規則仍固定，不能透過修改hand_mode或single_hand改變。

<a id="help"></a>
## 遇到問題時看這裡

| 你看到的情況 | 先試這件事 |
|---|---|
| 終端找不到main.py | 確認VS Code開的是包含main.py的Gesture-Player資料夾；Windows用Get-Location，Mac／Linux用pwd檢查路徑 |
| 找不到Python或版本不對 | 安裝3.13.2後重開VS Code，確認第一行版本檢查再建立.venv |
| 找不到numpy、mediapipe等套件 | 確認安裝完成，且命令／VS Code解譯器都使用本專案.venv |
| 無法安裝MediaPipe | 先核對系統與晶片是否在步驟2支援表中，再把完整錯誤給老師 |
| 視窗開不了，出現_tkinter錯誤 | 請老師確認所用Python有Tk支援；可執行下方Tk測試 |
| 鏡頭黑畫面 | 關閉其他使用鏡頭的程式、換索引，確認系統攝影機權限 |
| 偵測左右手反了 | 關閉工具，複製config.example.json成config.json，切換swap_handedness的true／false，重開確認；校正後才錄 |
| 有效筆數一直是0 | 看右側採集原因；只放右手、全手入鏡，等倒數結束再觀察 |
| 資料列表沒有新資料 | 要按停止錄製才保存；0筆時不會保存 |
| 模型無法載入 | 檢查算法是否完成、設定是否改過；保留data，重新訓練 |
| 訓練按下去沒有明顯結果 | 看models是否生成；使用下方終端命令查看詳細錯誤 |
| 網站確認準備不能按 | 先載入模型，切recognize做手勢，再配對；濾波啟用時也要完成 |
| 配對失敗 | 向老師核對網址，網站重新產生配對碼；別把另一台主機填成localhost |

鏡頭權限：Windows在設定的攝影機隱私權允許桌面應用程式；Mac在「系統設定 → 隱私權與安全性 → 攝影機」允許VS Code／Terminal後重啟；Linux需本機桌面與攝影機裝置的存取權限，必要時請管理員協助。請在本機桌面操作，不在WSL或無桌面遠端終端開啟鏡頭GUI。

<details>
<summary>終端指令補充：Tk檢查、訓練、測試與共用工具檢查</summary>

每次只執行需要的那一行。Tk測試會開小視窗，關閉後才回到終端。

**Windows PowerShell**

```powershell
& '.\.venv\Scripts\python.exe' -m tkinter
& '.\.venv\Scripts\python.exe' main.py train
& '.\.venv\Scripts\python.exe' main.py test
& '.\.venv\Scripts\python.exe' -m pytest tests/test_tools.py
```

**Mac／Linux**

```bash
./.venv/bin/python -m tkinter
./.venv/bin/python main.py train
./.venv/bin/python main.py test
./.venv/bin/python -m pytest tests/test_tools.py
```

</details>

<details>
<summary>各個資料夾與設定檔在做什麼？</summary>

| 位置 | 用途 | 學員要改嗎？ |
|---|---|---|
| student | 正規化、KNN、濾波算法 | 要，濾波選做 |
| data | 錄製後生成的原始關鍵點與用途 | 用介面管理 |
| models | 訓練後生成的個人模型、測試報告 | 不手改 |
| .venv | 本機Python與套件，每台電腦自行建立 | 不手改 |
| .vscode | 編輯器解譯器與測試設定 | 通常不用 |
| assets | MediaPipe關鍵點模型，不是個人KNN模型 | 不用 |
| core、ui、network | 鏡頭、資料讀寫、介面、安全檢查、配對 | 不用 |
| protocol | 與競技場共用的標籤與訊息格式 | 不用 |
| tests | 接口與共用工具測試 | 執行即可 |
| requirements-lock.txt | 固定套件版本，含間接依賴 | 不用 |
| pyproject.toml | 專案與pytest設定 | 不用 |
| config.example.json | 預設設定，個人調整先複製成config.json | 需要時再調 |
| .gitignore | 避免把環境、個人資料與模型加入Git | 不用 |

套件損壞時可重新安裝requirements-lock，必要時重建.venv；保留student、data、models與config.json。不要任意升級套件。

</details>

<details>
<summary>工具怎麼呼叫我的算法？</summary>

| 你的函式 | 共用工具入口 | 結果去向 |
|---|---|---|
| transform | core/features.py的feature | 檢查後交給訓練或分類 |
| fit | core/model_io.py的訓練、載入 | 保存資料／重建分類器 |
| predict | ui/app.py即時辨識、core/model_io.py測試 | 評估、濾波或直接輸出 |
| update、reset | core/features.py的OutputRouter | 控制輸出與清除歷史 |

訓練只讀train，測試只讀test；共用工具先驗證右手、尺寸、數值與手掌尺度，再呼叫正規化。你只要使用參數、計算並return。正規化定義改變後需要重算特徵、重新訓練；目前特徵版本由main.py固定，如要新增版本由老師維護。

</details>

<details>
<summary>第三方資源與授權</summary>


本工具只使用 Hand Landmarker，不使用 Gesture Recognizer。

模型保存位置：`assets/models/hand_landmarker.task`。
來源：https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
SHA-256：`fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1`。
MediaPipe 原始碼採 Apache-2.0；官方模型依官方模型資源與使用條款使用。官方指南：https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python 。部署前確認組織適用條款。

OpenCV（Apache-2.0）、NumPy（BSD-3-Clause）、python-socketio（MIT）、Pillow（HPND）、pytest（MIT）及其依賴的授權隨安裝套件保存；完整版本在 requirements-lock.txt。
安裝時可下載，活動執行不下載模型。未提供離線套件安裝包，不複製 .venv 到其他電腦。

</details>
