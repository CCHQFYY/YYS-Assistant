# -*- coding: utf-8 -*-
# Agent 入口：启动 AgentServer，与 MXU/MaaFramework 通信
import sys
import os
import glob
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # embed python 隔离模式不加脚本目录，手动补上

from maa.agent.agent_server import AgentServer
from maa.tasker import Tasker

import actions       # noqa: F401  导入通用工具与基类
import recognitions  # noqa: F401  导入即注册自定义识别
from tasks.kun28 import Kun28  # noqa: F401  导入即注册困28任务 CustomAction
from tasks.event import Event      # noqa: F401  导入即注册活动任务 CustomAction
from tasks.general import General      # noqa: F401  导入即注册通用任务 CustomAction
from tasks.team_host import TeamHost    # noqa: F401  导入即注册组队房主任务 CustomAction
from tasks.team_member import TeamMember  # noqa: F401  导入即注册组队队员任务 CustomAction
from tasks.test_ocr import TestOcr      # noqa: F401  导入即注册测试识别任务 CustomAction


def cleanup_logs():
    """启动时清理旧日志：maafw.log 超 10MB 清空（被占用则跳过），历史 agent 日志与过期日期日志删除"""
    log_dir = "./debug"
    maafw_log = os.path.join(log_dir, "maafw.log")
    try:
        if os.path.exists(maafw_log) and os.path.getsize(maafw_log) > 10 * 1024 * 1024:
            with open(maafw_log, "r+b") as f:
                f.truncate(0)  # 共享写模式下截断生效；被独占时抛异常走 except
            print("[Agent] maafw.log 已超过 10MB，启动时清空")
    except Exception:
        pass
    try:
        for p in glob.glob(os.path.join(log_dir, "mxu-agent-*.log")):  # 历史 agent 日志，正被占用的自动跳过
            try:
                os.remove(p)
            except OSError:
                pass
        today = time.strftime("%Y-%m-%d")
        for p in glob.glob(os.path.join(log_dir, "20*.log")):  # 过期 MXU 日期日志，保留今天的
            if os.path.basename(p)[:10] < today:
                try:
                    os.remove(p)
                except OSError:
                    pass
    except Exception:
        pass


def main():
    cleanup_logs()  # 先清旧日志再初始化，防 debug 目录无限膨胀
    Tasker.set_log_dir("./debug")  # 日志目录，CWD 为 interface.json 所在目录

    if len(sys.argv) < 2:
        print("Usage: python main.py <socket_id>")
        exit(1)

    socket_id = sys.argv[-1]  # 由 Client 启动时自动传入

    AgentServer.start_up(socket_id)
    AgentServer.join()
    AgentServer.shut_down()


if __name__ == "__main__":
    main()
