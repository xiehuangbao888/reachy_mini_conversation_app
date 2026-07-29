"""Control the SO-ARM follower arm gripper (/dev/ttyACM1): open / close / demo.

Must be run with the lerobot environment python:
    /home/ubuntu/miniconda3/envs/lerobot/bin/python soarm_gripper.py open
    /home/ubuntu/miniconda3/envs/lerobot/bin/python soarm_gripper.py close
    /home/ubuntu/miniconda3/envs/lerobot/bin/python soarm_gripper.py demo
"""

import sys
import time

from lerobot.robots.so_follower import SOFollower, SOFollowerRobotConfig

# Non-interactive environment (invoked as a subprocess by the conversation
# app): answer the calibration prompt with Enter, i.e. reuse the existing
# calibration file.
import builtins

_original_input = builtins.input
builtins.input = lambda *args, **kwargs: ""

PORT = "/dev/ttyACM1"  # SO-ARM follower arm (ttyACM0 is the Reachy Mini)
ARM_ID = "my_awesome_follower_arm"  # calibration file under ~/.cache/huggingface/lerobot/calibration/robots/so_follower/

OPEN_POS = 60.0   # gripper open (0-100 normalized)
CLOSE_POS = 20.0  # gripper closed


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "demo"

    robot = SOFollower(SOFollowerRobotConfig(port=PORT, id=ARM_ID))
    robot.connect()
    try:
        if action == "demo":
            for _ in range(2):
                robot.send_action({"gripper.pos": OPEN_POS})
                time.sleep(1.0)
                robot.send_action({"gripper.pos": CLOSE_POS})
                time.sleep(1.0)
            print("Gripper demo done (opened and closed twice)")
        else:
            target = OPEN_POS if action == "open" else CLOSE_POS
            robot.send_action({"gripper.pos": target})
            time.sleep(1.0)  # wait for the gripper to reach the position
            print(f"Gripper {'opened' if action == 'open' else 'closed'}")
    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
