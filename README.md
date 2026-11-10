# MAAYYS — MAA 阴阳师助手

基于 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) 与 MXU 客户端的《阴阳师》自动化脚本项目，通过 ADB 连接安卓模拟器，用模板匹配与 OCR 识别游戏界面并模拟点击，实现副本循环挑战。

- 项目名称：MAAYYS（`interface.json` 中 `name`）
- 显示名称：MAA阴阳师助手
- 当前版本：0.1.0

> 本项目仅用于学习与交流，详见文末「免责声明」。

## 功能与任务

所有任务在 MXU 中逐个勾选运行，均支持「最大次数」参数：填 `0` 表示无限循环（需手动停止），填正整数则达到次数后立即结束任务。

| 任务 | Pipeline 入口 | 适用场景 | 计数口径 |
| --- | --- | --- | --- |
| 困28 | `Kun28` | 探索副本第 28 章困难模式，自动进图、找小怪循环刷 | 每点中一只小怪计 1 次 |
| 活动 | `Event` | 活动副本自动挑战与结算 | 每点一次「挑战开始」计 1 次 |
| 通用 | `General` | 任意带「挑战」按钮的副本，OCR 识别文字后点击 | 每点一次「挑战」计 1 次 |
| 组队房主 | `TeamHost` | 组队副本中作为房主自动开始挑战与结算 | 每点一次「开始挑战」计 1 次 |
| 组队队员 | `TeamMember` | 组队副本中作为队员挂机，只处理结算 | 每点一次「点击继续」计 1 次 |
| 测试识别 | `TestOcr` | 调试用：OCR 识别「挑战」二字，不点击 | 识别 10 次后结束 |

各任务的识别方式：

- 困28：模板匹配 `ConfirmExit`、`TapToContinue`、`monster_target`、`explore_button`、`seek_forward`、`exit_button`，并在无小怪时定期滑屏找怪。
- 活动：模板匹配活动界面的「挑战开始」按钮。
- 通用：OCR 识别「挑战」二字（搜索区域 `[643, 441, 637, 279]`）。
- 组队房主 / 测试识别：模板匹配 / OCR 搜索区域均为 `[1028, 484, 252, 236]`。
- 组队队员：仅模板匹配「点击继续」。

点击均由 `human_click()` 完成，带随机反应延迟、落点偏移、按压时长与轻微滑动。

## 运行前提

1. **Windows x64**：仓库内 `mxu.exe`、`maafw/*.dll`、`runtime/*.dll` 均为 Windows x64 构建。
2. **WebView2 运行时**：MXU 界面基于 WebView2。Windows 11 通常已内置；Windows 10 若界面空白，请安装 [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/)。
3. **安卓模拟器**，推荐 MuMu 模拟器等支持 ADB 的模拟器，并满足：
   - 游戏分辨率 **1280×720（720p）**。`interface.json` 中控制器 `display_short_side` 为 `720`，模板图与所有 ROI 坐标均按 720p 采集，分辨率不一致会识别失败。
   - 已开启 ADB 调试，MXU 能连接到模拟器的 ADB 地址（如 `127.0.0.1:16384`）。
4. **游戏账号与进度自备**：脚本只做界面点击，不修改游戏数据。

## 如何启动

### 方式一：下载发布包（推荐给普通用户）

1. 在本仓库的 **Releases** 页面下载最新压缩包（如 `MAAYYS-0.1.0-win-x64.zip`）。
2. 解压到任意目录，确保解压后结构为 `MAAYYS\mxu.exe`、`MAAYYS\agent\`、`MAAYYS\runtime\` 等。
3. 双击 `MAAYYS\mxu.exe` 启动。
4. 首次启动会在同目录自动生成 `config/`、`cache/`、`debug/`，属正常现象。

### 方式二：从仓库克隆

本仓库为完整可运行备份，克隆后无需额外安装依赖。

```bash
git clone <本仓库地址> MAAYYS
cd MAAYYS
```

随后同样双击 `mxu.exe` 启动。仓库体积约 247 MB，其中主要是 `runtime/`（内嵌 Python 3.11）与 `maafw/`（MaaFramework 运行库）。

### 在 MXU 中开始运行

1. 启动模拟器并进入游戏。
2. 在 MXU 中新建实例，控制器选择「模拟器（Emulator）」，连接模拟器的 ADB 地址。
3. 勾选需要的任务，按需修改该任务的「最大次数」。
4. 启动任务；需要提前结束时点击停止。

## 目录结构

```text
MAAYYS/
├─ mxu.exe                     MXU 客户端（Windows x64）
├─ interface.json              项目声明：控制器、资源、任务与参数
├─ agent/                      Python 自动化逻辑（由 runtime 内的 Python 执行）
│  ├─ main.py                  入口：启动 AgentServer
│  ├─ actions.py               通用动作与基类（human_click 等）
│  ├─ recognitions.py          自定义识别示例（未启用）
│  ├─ requirements.txt         Python 依赖声明（MaaFw>=5.12.3）
│  └─ tasks/                   各任务的 CustomAction 实现
│     ├─ kun28.py  event.py  general.py
│     └─ team_host.py  team_member.py  test_ocr.py
├─ resource/                   MaaFramework 资源
│  ├─ pipeline/main.json       任务入口节点定义
│  ├─ image/                   模板图（按任务分目录）
│  │  ├─ common/TapToContinue.png
│  │  ├─ event/challenge_start.png
│  │  ├─ kun28/*.png
│  │  └─ team_host/challenge_start.png
│  └─ model/ocr/               OCR 模型（det.onnx、rec.onnx、keys.txt）
├─ maafw/                      MaaFramework 运行库与 MaaPiCli
└─ runtime/                    内嵌 Python 3.11.9 及 site-packages（maa、numpy 等）
```

运行时生成、不纳入仓库的内容：

- `config/`：MXU 配置（`mxu-MAAYYS.json`、`maa_option.json`），含本地设备与实例信息。
- `cache/`：WebView 数据与配置滚动备份。
- `debug/`：运行日志与调试截图。
- `__pycache__/`、`*.pyc`：Python 字节码缓存。

## 任务参数

`interface.json` 中为每个任务定义了一个整数输入参数，默认值 `0`：

- `Kun28_MaxBattles` — 困28 最大战斗次数
- `Event_MaxBattles` — 活动最大挑战次数
- `General_MaxBattles` — 通用最大挑战次数
- `TeamHost_MaxBattles` — 组队房主最大挑战次数
- `TeamMember_MaxBattles` — 组队队员最大结算次数

参数 `0` 表示无限循环。计数都发生在「点击成功的一瞬间」，并带有冷却（活动/通用/组队房主为 2 秒，组队队员为 8 秒），避免画面切换慢导致重复计数。进度会打印在 MXU 的运行日志中，例如 `[Event] 第 3/10 次`。

## 日志与排查

- `debug/maafw.log`：MaaFramework 运行日志（含识别、控制器调用细节）。
- `debug/<日期>-<序号>.log`：MXU 客户端日志（配置加载、设备扫描、任务调度）。
- `agent/main.py` 在每次启动时会清理 `debug/` 中超过 10 MB 的 `maafw.log` 与过期的日期日志。

## 常见问题

**Q：任务一直不动，日志显示未命中？**

先确认模拟器分辨率为 1280×720，且游戏画面处于任务所需界面。模板图与 ROI 均按 720p 坐标写死，缩放、全面屏比例、画质设置都会导致匹配失败。

**Q：MXU 里找不到设备 / 连接失败？**

确认模拟器已启动并开启 ADB 调试，再填写正确的 ADB 地址与端口（不同模拟器官网默认端口不同）。部分模拟器需要先启动游戏进程才会暴露 ADB 端口。

**Q：界面白屏或无法打开窗口？**

多为缺少 WebView2 运行时，安装后重试；也可尝试删除 `cache/webview_data` 后重新启动。

**Q：为什么第一次运行多出 config、cache、debug 目录？**

这是 MXU 自动生成的本地配置、缓存与日志，已在 `.gitignore` 中忽略，删除后下次启动会重新生成。

**Q：可以自己加任务吗？**

可以。在 `agent/tasks/` 下实现 `CustomAction` 并用 `@AgentServer.custom_action("名称")` 注册，在 `agent/main.py` 中 `import` 使其生效，同时在 `resource/pipeline/main.json` 与 `interface.json` 中登记入口与参数。

**Q：更换或新增模板图有什么要求？**

模板图需按 720p 截取，放在 `resource/image/<任务名>/` 下，并在对应任务代码的 `targets` 中以相对 `resource/image/` 的路径引用。

## 第三方组件

本仓库为「可直接运行」的完整备份，因此包含以下第三方二进制/库，它们各自遵循其原始许可证，许可证文件随包保留在对应目录中：

- **MaaFramework**（`maafw/`、`runtime/Lib/site-packages/maa/`、`runtime/Lib/site-packages/maafw-*.dist-info/`）：MaaXYZ 出品，见 `runtime/Lib/site-packages/maafw-5.12.3.dist-info/licenses/LICENSE.md`。
- **Python 3.11**（`runtime/`）：PSF License，见 `runtime/LICENSE.txt`。
- **OpenCV**（`opencv_world4_maa.dll`）：Apache-2.0。
- **ONNX Runtime**（`onnxruntime_maa.dll`）：MIT。
- **DirectML**（`DirectML.dll`）：Microsoft。
- **NumPy**（`runtime/Lib/site-packages/numpy/`）：BSD-3-Clause，见同目录 `LICENSE.txt`。
- **MXU 客户端**（`mxu.exe`）：由 misteo 开发，版权归原作者所有。

游戏《阴阳师》的名称、界面素材、角色形象等知识产权归网易及其关联方所有。本仓库 `resource/image/` 中的模板图取自游戏画面，仅用于界面识别，不构成对游戏素材的再授权。

## 免责声明

1. 本项目仅供**学习与交流**使用，不提供任何形式的担保，使用风险自负。
2. 本项目不修改游戏客户端、不注入进程、不读写游戏内存，仅通过 ADB 截屏与模拟点击操作界面。
3. 使用第三方工具可能违反游戏用户协议，存在账号被处罚的风险，请自行评估并承担后果。
4. 请勿将本项目用于商业用途或任何盈利性场景。
5. 如有侵权，请联系删除。
