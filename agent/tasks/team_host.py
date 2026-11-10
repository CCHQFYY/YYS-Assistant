# -*- coding: utf-8 -*-
# 组队房主：组队副本作为房主循环挑战，模板识别"开始挑战"按钮并点击，点一次算一次，达到设定次数立刻停止
import random
import time

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from actions import YYSAction, human_click, read_count_param


@AgentServer.custom_action("TeamHost")
class TeamHost(YYSAction):
    """计数口径：点中"开始挑战"按钮瞬间 battles += 1；如 battles >= max_battles 立刻停止。"""

    def logic(self, context: Context, argv: CustomAction.RunArg) -> bool:
        targets = [
            # 模板图：resource/image/team_host/challenge_start.png（ImageCrapper 从红框裁剪）
            # ROI 为放大后的搜索区域（ImageCrapper amplified roi）
            ("ChallengeStart", {"recognition": "TemplateMatch", "template": "team_host/challenge_start.png", "green_mask": True, "roi": [1028, 484, 252, 236]}),
            ("TapToContinue", {"recognition": "TemplateMatch", "template": "common/TapToContinue.png", "green_mask": True, "roi": [535, 665, 216, 55]}),
        ]
        battles = 0         # 已点击开始挑战的次数（= 完成次数）
        last_count_time = 0.0  # 上次计数时间，2 秒内不重复计数
        max_battles = read_count_param(argv)

        if max_battles > 0:
            print(f"[TeamHost] 任务启动：设定最大挑战次数 = {max_battles}，点到第 {max_battles} 次挑战后立刻停止")
        else:
            print("[TeamHost] 任务启动：无限循环模式，点停止按钮退出")

        while not context.tasker.stopping:
            context.tasker.controller.post_screencap().wait()
            img = context.tasker.controller.cached_image
            hits = {}
            for node, spec in targets:
                detail = context.run_recognition(node, img, {node: spec})
                if detail and detail.hit:
                    hits[node] = detail.best_result.box

            if "ChallengeStart" in hits:
                human_click(context, hits["ChallengeStart"])
                if time.time() - last_count_time >= 2:  # 2 秒冷却内只点不计，防画面切换慢导致重复计数
                    battles += 1
                    last_count_time = time.time()
                    if max_battles > 0:
                        print(f"[TeamHost] 第 {battles}/{max_battles} 次")
                        if battles >= max_battles:
                            print(f"[TeamHost] 已达到设定上限 {max_battles} 次，停止任务")
                            break
                    else:
                        print(f"[TeamHost] 第 {battles} 次")

            elif "TapToContinue" in hits:
                human_click(context, hits["TapToContinue"])

            time.sleep(random.uniform(0.45, 0.6))  # 帧周期加抖动，避免等间隔脉冲特征

        cap_str = f"{battles}/{max_battles}" if max_battles > 0 else f"{battles}（无限模式）"
        print(f"[TeamHost] 已停止：共挑战 {cap_str} 次")
        return True

