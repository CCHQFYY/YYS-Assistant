# -*- coding: utf-8 -*-
# 困28：探索副本第28章困难，章节页↔探索图↔战斗 循环刷小怪
import json
import random
import time

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from actions import YYSAction, human_click


@AgentServer.custom_action("Kun28")
class Kun28(YYSAction):
    """计数口径：点中小怪瞬间 battles += 1；如 battles >= max_battles 立刻停止。"""

    @staticmethod
    def _read_max_battles(argv: CustomAction.RunArg) -> int:
        """从 argv.custom_action_param 读取 max_battles（Maa 传过来的是 JSON 字符串）。
        返回 int，0 表示无限，读不到则回退 0。"""
        raw = getattr(argv, "custom_action_param", None)
        if raw is None:
            return 0
        if isinstance(raw, str):
            s = raw.strip()
            if not s or s in {"null", "None"}:
                return 0
            try:
                raw = json.loads(s)
            except Exception:
                try:
                    return max(0, int(s))
                except Exception:
                    return 0
        if isinstance(raw, dict):
            v = raw.get("max_battles")
        else:
            v = raw
        try:
            return max(0, int(v))
        except Exception:
            return 0

    def logic(self, context: Context, argv: CustomAction.RunArg) -> bool:
        targets = [
            ("ConfirmExit", {"recognition": "TemplateMatch", "template": "kun28/ConfirmExit.png", "green_mask": True, "roi": [692, 378, 167, 52]}),
            ("TapToContinue", {"recognition": "TemplateMatch", "template": "common/TapToContinue.png", "green_mask": True, "roi": [535, 665, 216, 55]}),
            ("MonsterTarget", {"recognition": "TemplateMatch", "template": "kun28/monster_target.png", "green_mask": True, "roi": [57, 122, 1223, 504]}),
            ("ExploreButton", {"recognition": "TemplateMatch", "template": "kun28/explore_button.png", "green_mask": True, "roi": [1032, 543, 200, 161]}),
            ("SeekForward", {"recognition": "TemplateMatch", "template": "kun28/seek_forward.png", "green_mask": True, "roi": [637, 527, 269, 193]}),
        ]
        last_swipe_time = 0.0
        seek_since = None  # 有前进箭头但无小怪的连续起始时间
        battles = 0       # 已点中小怪次数（= 完成次数）
        max_battles = Kun28._read_max_battles(argv)

        def click_box(box):
            human_click(context, box)

        if max_battles > 0:
            print(f"[Kun28] 任务启动：设定最大战斗次数 = {max_battles}，点到第 {max_battles} 只小怪后立刻停止")
        else:
            print("[Kun28] 任务启动：无限循环模式，点停止按钮退出")

        while not context.tasker.stopping:
            context.tasker.controller.post_screencap().wait()
            img = context.tasker.controller.cached_image
            hits = {}
            for node, spec in targets:
                detail = context.run_recognition(node, img, {node: spec})
                if detail and detail.hit:
                    hits[node] = detail.best_result.box

            if "ConfirmExit" in hits:
                click_box(hits["ConfirmExit"])

            elif "TapToContinue" in hits:
                click_box(hits["TapToContinue"])

            elif "MonsterTarget" in hits:
                click_box(hits["MonsterTarget"])
                battles += 1
                if max_battles > 0:
                    print(f"[Kun28] 第 {battles}/{max_battles} 次")
                    if battles >= max_battles:
                        print(f"[Kun28] 已达到设定上限 {max_battles} 次，停止任务")
                        break
                else:
                    print(f"[Kun28] 第 {battles} 次")

            elif "ExploreButton" in hits:
                click_box(hits["ExploreButton"])

            else:
                if "SeekForward" in hits:
                    if seek_since is None:
                        seek_since = time.time()
                    if time.time() - seek_since >= 2:
                        detail = context.run_recognition(
                            "ExitButton", img,
                            {"ExitButton": {"recognition": "TemplateMatch", "template": "kun28/exit_button.png", "green_mask": True, "roi": [24, 8, 57, 57]}},
                        )
                        if detail and detail.hit:
                            click_box(detail.best_result.box)
                            seek_since = None
                else:
                    seek_since = None
                if "SeekForward" in hits and time.time() - last_swipe_time >= 2:
                    context.tasker.controller.post_swipe(  # 滑屏坐标与时长加抖动，避免固定轨迹特征
                        1100 + random.randint(-30, 30), 400 + random.randint(-20, 20),
                        150 + random.randint(-30, 30), 400 + random.randint(-20, 20),
                        random.randint(300, 500),
                    ).wait()
                    last_swipe_time = time.time()
            time.sleep(random.uniform(0.9, 1.15))  # 帧周期加抖动，避免等间隔脉冲特征

        cap_str = f"{battles}/{max_battles}" if max_battles > 0 else f"{battles}（无限模式）"
        print(f"[Kun28] 已停止：共点击小怪 {cap_str} 次")
        return True
