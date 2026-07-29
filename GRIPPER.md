# SO-ARM Gripper Voice Control / SO-ARM 爪夹语音控制

Control an SO-ARM follower arm gripper (open / close) by voice through the
Reachy Mini conversation app — **no changes to the upstream source code**,
using the app's built-in external-tool mechanism.

通过 Reachy Mini 对话应用用语音控制 SO-ARM 从臂爪夹的开合——**无需修改官方源码**，
使用应用内置的外部工具（external tools）机制。

## How it works / 工作原理

```
voice command 语音指令
  → gripper_control external tool (LLM function calling)  外部工具
  → subprocess: soarm_gripper.py open|close               子进程调用驱动脚本
  → lerobot SOFollower → /dev/ttyACM1                     驱动 SO-ARM 爪夹
```

Files added by this fork / 本 fork 新增的文件：

| File | Purpose |
| --- | --- |
| `soarm_gripper.py` | Gripper driver script (lerobot). 爪夹驱动脚本 |
| `external_content/external_tools/gripper_control.py` | External tool exposing open/close to the LLM. 暴露给 LLM 的外部工具 |
| `.gitignore` | Un-ignores the tool file so it can be committed. 让工具文件可被提交 |

## Prerequisites / 前置条件

1. Reachy Mini connected (`/dev/ttyACM0`) and its daemon running, app installed
   per the upstream README.
2. SO-ARM follower arm connected. This setup assumes it enumerates as
   `/dev/ttyACM1` — check with `ls /dev/ttyACM*` and adjust `PORT` in
   `soarm_gripper.py` if different.
3. A `lerobot` conda environment with `lerobot` installed (feetech support):
   ```bash
   conda create -n lerobot python=3.10
   conda activate lerobot
   pip install lerobot[feetech]
   ```
4. Arm calibration done once with lerobot (creates a file under
   `~/.cache/huggingface/lerobot/calibration/robots/so_follower/`).
   The script uses `ARM_ID = "my_awesome_follower_arm"` — match it to your
   calibration file name.

## Setup / 配置

Add these two lines to `.env` in the repo root (create it if missing).
在仓库根目录的 `.env` 中加入两行：

```bash
REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY=external_content/external_tools
AUTOLOAD_EXTERNAL_TOOLS=1
```

If your lerobot python lives elsewhere, also set (optional) / 如路径不同可加：

```bash
LEROBOT_PYTHON=/path/to/lerobot/env/bin/python
```

## Run / 运行

Start the app **from the repo root** so `.env` and the relative tools path
resolve correctly. 必须从仓库根目录启动：

```bash
cd reachy_mini_conversation_app
reachy-mini-conversation-app
```

If your shell exports a `socks://` proxy (e.g. clash), use the wrapper
instead — it strips `ALL_PROXY` before launching:
如 shell 里有 `socks://` 代理（如 clash），改用包装脚本启动——它会先去掉 `ALL_PROXY`：

```bash
./run_app.sh
```

Startup log should contain / 启动日志应出现：

```
AUTOLOAD_EXTERNAL_TOOLS enabled: added 1 external tool(s): ['gripper_control']
✓ Loaded external tool: gripper_control
```

## Voice commands / 语音指令

- "open the gripper" / "open the claw" / "release" / "let go"
- "close the gripper" / "close the claw" / "grab it" / "hold this"

## Manual test / 手动测试

Without the app, to verify hardware + calibration first.
不启动对话应用，先验证硬件和校准：

```bash
/home/ubuntu/miniconda3/envs/lerobot/bin/python soarm_gripper.py open
/home/ubuntu/miniconda3/envs/lerobot/bin/python soarm_gripper.py close
/home/ubuntu/miniconda3/envs/lerobot/bin/python soarm_gripper.py demo   # open+close twice
```

## Troubleshooting / 故障排除

**Backend failed to start: Unknown scheme for proxy URL `socks://...`**
后端启动失败：`socks://` 代理协议不受支持。

The app uses httpx, which does not accept the plain `socks://` scheme in
`ALL_PROXY` (only `http(s)://`, `socks5://`, `socks5h://`). If your shell
sets `ALL_PROXY=socks://...` (e.g. via clash), launch the app with it
removed — `HTTPS_PROXY=http://...` alone is enough:

app 使用 httpx，不支持 `ALL_PROXY` 中的 `socks://` 写法（只认
`http(s)://`、`socks5://`、`socks5h://`）。如果 shell 里（如 clash）
设置了 `ALL_PROXY=socks://...`，启动时去掉它即可，保留
`HTTPS_PROXY=http://...` 就够：

```bash
env -u ALL_PROXY -u all_proxy reachy-mini-conversation-app
```

Alternatively change the proxy variable to `socks5://127.0.0.1:PORT/`
(httpx accepts that scheme; `socksio` is required and already installed).
或者把代理变量改成 `socks5://127.0.0.1:端口/`（httpx 接受该写法，
需要 `socksio`，环境中已安装）。

## Tuning / 调整

In `soarm_gripper.py`:

- `OPEN_POS` / `CLOSE_POS` — gripper travel, normalized 0–100 (default 60 / 20).
- `PORT` — serial device of the follower arm.
- `ARM_ID` — calibration profile name.
