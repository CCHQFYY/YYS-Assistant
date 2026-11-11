# -*- coding: utf-8 -*-
# 组队队员：作为队员加入组队副本，仅识别"点击继续"结算画面并点击，点一次算一次，达到设定次数立刻停止
import random
import time

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from actions import YYSAction, human_click, read_count_param


@AgentServer.custom_action("TeamMember")
class TeamMember(YYSAction):
    """计数口径：点中"点击继续"瞬间 battles += 1；如 battles >= max_battles 立刻停止。"""

    def logic(self, context: Context, argv: CustomAction.RunArg) -> bool:
        targets = [
            ("TapToContinue", {"recognition": "TemplateMatch", "template": "common/TapToContinue.png", "green_mask": True, "roi": [535, 644, 216, 76]}),
        ]
        battles = 0         # 已点击继续的次数（= 完成次数）
        last_count_time = 0.0  # 上次计数时间，8 秒内不重复计数
        max_battles = read_count_param(argv)

        if max_battles > 0:
            print(f"[TeamMember] 任务启动：设定最大次数 = {max_battles}，点到第 {max_battles} 次后立刻停止")
        else:
            print("[TeamMember] 任务启动：无限循环模式，点停止按钮退出")

        while not context.tasker.stopping:
            context.tasker.controller.post_screencap().wait()
            img = context.tasker.controller.cached_image
            hits = {}
            for node, spec in targets:
                detail = context.run_recognition(node, img, {node: spec})
                if detail and detail.hit:
                    hits[node] = detail.best_result.box

            if "TapToContinue" in hits:
                human_click(context, hits["TapToContinue"])
                if time.time() - last_count_time >= 8:  # 8 秒冷却内只点不计，防画面停留导致重复计数
                    battles += 1
                    last_count_time = time.time()
                    if max_battles > 0:
                        print(f"[TeamMember] 第 {battles}/{max_battles} 次")
                        if battles >= max_battles:
                            print(f"[TeamMember] 已达到设定上限 {max_battles} 次，停止任务")
                            break
                    else:
                        print(f"[TeamMember] 第 {battles} 次")

            time.sleep(random.uniform(0.45, 0.6))  # 帧周期加抖动，避免等间隔脉冲特征

        cap_str = f"{battles}/{max_battles}" if max_battles > 0 else f"{battles}（无限模式）"
        print(f"[TeamMember] 已停止：共点击继续 {cap_str} 次")
        return True
