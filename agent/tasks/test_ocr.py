# -*- coding: utf-8 -*-
# 测试任务：OCR 识别"挑战"二字（ROI 与组队房主一致），验证该区域能否识别成功；不点击，仅打印结果、置信度与区域全部文字
import json
import time

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from actions import YYSAction

ROI = [1028, 484, 252, 236]  # 与组队房主 ChallengeStart 的 ROI 一致（ImageCrapper amplified roi）
EXPECTED = "挑战"
ATTEMPTS = 10                # 识别次数，每秒一次


def _extract_ocr_info(detail):
    """从 OCR 识别结果提取命中文字、置信度、坐标，以及区域内识别到的全部文字"""
    d = getattr(detail, "detail", None)
    all_texts = []
    best = d.get("best") if isinstance(d, dict) else None
    if isinstance(best, dict):
        best = [best]
    filtered = d.get("filter") if isinstance(d, dict) else None
    if isinstance(d, dict):
        for item in d.get("all") or []:
            if isinstance(item, dict) and item.get("text"):
                all_texts.append(f"{item['text']!r}@{item.get('box')}")
    text, score, box = None, None, None
    src = (best if best else filtered) or []
    if isinstance(src, list) and src and isinstance(src[0], dict):
        text = src[0].get("text")
        score = src[0].get("score")
        box = src[0].get("box")
    br = getattr(detail, "best_result", None)
    if box is None:
        box = getattr(br, "box", None)
    return text, score, box, all_texts, d


@AgentServer.custom_action("TestOcr")
class TestOcr(YYSAction):
    """每秒截屏识别一次共 ATTEMPTS 次，打印每次命中情况、置信度与区域内全部文字，最后汇总。"""

    def logic(self, context: Context, argv: CustomAction.RunArg) -> bool:
        print(f"[TestOcr] 开始测试：OCR 识别'{EXPECTED}'，roi={ROI}，共 {ATTEMPTS} 次，不点击仅识别")
        hit_count = 0
        for i in range(1, ATTEMPTS + 1):
            if context.tasker.stopping:
                print(f"[TestOcr] 收到停止信号，提前结束（第 {i}/{ATTEMPTS} 次前）")
                break
            context.tasker.controller.post_screencap().wait()
            img = context.tasker.controller.cached_image

            if i == 1:  # 第一轮存一张原始帧到 debug，供离线分析
                try:
                    import cv2
                    cv2.imwrite("./debug/test_ocr_frame.png", img)
                    print(f"[TestOcr] 已保存运行时截图：debug/test_ocr_frame.png，尺寸={img.shape[1]}x{img.shape[0]}")
                except Exception as e:
                    print(f"[TestOcr] 保存截图失败：{e}")

            detail = context.run_recognition(
                "TestOcr", img,
                {"TestOcr": {"recognition": "OCR", "expected": EXPECTED, "roi": ROI}},
            )
            hit = bool(detail and detail.hit)
            hit_count += 1 if hit else 0
            text, score, box, all_texts, d = _extract_ocr_info(detail)
            print(f"[TestOcr] 第 {i}/{ATTEMPTS} 次：{'命中' if hit else '未命中'}，文字={text}，置信度={score}，box={box}")
            print(f"[TestOcr]   区域内全部文字：{all_texts if all_texts else '（无）'}")
            if not hit and d is not None:
                try:
                    print(f"[TestOcr]   完整 detail：{json.dumps(d, ensure_ascii=False, default=str)[:500]}")
                except Exception:
                    print(f"[TestOcr]   detail 原样：{d}")

            time.sleep(1)

        print(f"[TestOcr] 测试结束：{hit_count}/{ATTEMPTS} 次命中")
        return True
