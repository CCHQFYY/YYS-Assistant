# -*- coding: utf-8 -*-
# 自定义识别：内置识别算法（模板/OCR）不好实现的复杂判断在这里用 Python 实现
from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_recognition import CustomRecognition


@AgentServer.custom_recognition("ExampleRecognition")
class ExampleRecognition(CustomRecognition):
    """示例识别：在 Pipeline 中用 "recognition": "Custom", "custom_recognition": "ExampleRecognition" 引用"""

    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg):
        # TODO: 写识别逻辑，例如 OCR 读体力数字、判断庭院/战斗界面
        # 命中时返回 AnalyzeResult(box=(x, y, w, h), detail=...)；未命中返回 None
        return None
