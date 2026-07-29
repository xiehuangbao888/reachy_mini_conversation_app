"""External tool: control the SO-ARM robot arm gripper (open/close) by voice.

Loads automatically when REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY points at this
directory and AUTOLOAD_EXTERNAL_TOOLS=1. See GRIPPER.md for setup.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
LEROBOT_PYTHON = os.getenv("LEROBOT_PYTHON", "/home/ubuntu/miniconda3/envs/lerobot/bin/python")
GRIPPER_SCRIPT = os.getenv("SOARM_GRIPPER_SCRIPT", str(REPO_ROOT / "soarm_gripper.py"))


class GripperControl(Tool):
    """Open or close the SO-ARM robot arm gripper."""

    name = "gripper_control"
    description = (
        "Open or close the robot arm's gripper (claw). Call this directly when the user asks to "
        "open the gripper, open the claw, release, let go, close the gripper, close the claw, "
        "grab, grip, pinch, clamp or hold something."
    )
    needs_response = True
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["open", "close"],
                "description": "open = release/spread the gripper, close = grab/clamp",
            },
        },
        "required": ["action"],
    }

    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> Dict[str, Any]:
        """Run the gripper driver script as a subprocess."""
        action = kwargs.get("action", "open")
        if action not in ("open", "close"):
            return {"error": f"unknown action: {action}, expected 'open' or 'close'"}

        cmd = [LEROBOT_PYTHON, GRIPPER_SCRIPT, action]
        logger.info("Tool call: gripper_control %s -> %s", action, cmd)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            try:
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return {"error": "gripper command timed out (60s), killed"}

            output = stdout.decode(errors="replace")[-500:]
            if proc.returncode != 0:
                return {"error": f"gripper script exit code {proc.returncode}", "output": output}
            return {"status": f"gripper {action} done", "output": output}

        except Exception as e:
            logger.error("gripper_control failed")
            return {"error": f"gripper_control failed: {type(e).__name__}: {e}"}
