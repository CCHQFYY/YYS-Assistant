# -*- coding: utf-8 -*-
# 通用工具 + 业务动作基类：各任务在 tasks/*.py 单独实现并注册
import json
import random
import time

from maa.custom_action import CustomAction
from maa.context import Context


def read_count_param(argv: CustomAction.RunArg, key: str = "max_battles") -> int:
    """从 argv.custom_action_param（Maa 传来的 JSON 字符串）读整数配置，读不到回退 0"""
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
    v = raw.get(key) if isinstance(raw, dict) else raw
    try:
        return max(0, int(v))
    except Exception:
        return 0


def human_click(context: Context, box) -> None:
    """拟人点击 box 中心：反应延迟 + 正态分布落点 + 右偏按压时长 + 按压微滑，特征接近真人"""
    time.sleep(random.uniform(0.1, 0.3))  # 看到目标到点下的反应时间
    cx, cy = box[0] + box[2] // 2, box[1] + box[3] // 2
    dx = max(-10, min(10, random.gauss(0, 4)))  # 正态落点：中心密边缘稀，截断在 ±10
    dy = max(-8, min(8, random.gauss(0, 3)))
    x, y = int(cx + dx), int(cy + dy)
    hold = int(max(60, min(220, random.gauss(105, 30))))  # 多数 80~130ms，偶尔长按
    context.tasker.controller.post_swipe(
        x, y,
        x + random.randint(-4, 6), y + random.randint(-3, 4),  # 按压时手指微滑 2~8px
        hold,
    ).wait()


def click_node(context: Context, node: str, template: str, timeout: int = 10) -> bool:
    """通用操作：识别模板图并拟人点击，timeout 秒内每秒重试，命中返回 True"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        context.tasker.controller.post_screencap().wait()  # 先截一张新图
        detail = context.run_recognition(
            node,
            context.tasker.controller.cached_image,
            {node: {"recognition": "TemplateMatch", "template": template, "green_mask": True}},
        )
        if detail and detail.hit:
            human_click(context, detail.best_result.box)
            return True
        time.sleep(1)  # 未命中，1 秒后重试
    return False


def click_text(context: Context, node: str, text: str, timeout: int = 10) -> bool:
    """OCR 识别屏幕文字并拟人点击其中心，timeout 秒内每秒重试，命中返回 True"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        context.tasker.controller.post_screencap().wait()
        detail = context.run_recognition(
            node,
            context.tasker.controller.cached_image,
            {node: {"recognition": "OCR", "expected": text}},
        )
        if detail and detail.hit:
            human_click(context, detail.best_result.box)
            return True
        time.sleep(1)
    return False


class YYSAction(CustomAction):
    """业务动作基类：统一入口，子类实现 logic()"""

    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        print(f"[{argv.node_name}] 开始执行")
        result = self.logic(context, argv)
        print(f"[{argv.node_name}] 执行结束：{'成功' if result else '失败'}")
        return result

    def logic(self, context: Context, argv: CustomAction.RunArg) -> bool:
        raise NotImplementedError
