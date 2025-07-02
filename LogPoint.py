import json
import requests
from websocket import create_connection


def get_target_ws_url(target_page_url: str) -> str:
    """获取目标页面的WebSocket调试地址"""
    targets = requests.get('http://localhost:9222/json').json()
    for t in targets:
        if t['url'].startswith(target_page_url):
            return t['webSocketDebuggerUrl']
    raise Exception(f"未找到匹配页面: {target_page_url}")


def set_log_breakpoint(js_url: str, line: int, column: int, condition: str, target_page_url: str):
    """同步即时设置断点（无需等待脚本加载）"""
    ws_url = get_target_ws_url(target_page_url)
    ws = create_connection(ws_url)
    msg_id = 1

    # 1. 启用Debugger
    ws.send(json.dumps({
        "id": msg_id,
        "method": "Debugger.enable"
    }))
    _wait_for_id(ws, msg_id)
    msg_id += 1

    # 2. 直接设置断点（关键修改点）
    print(f"⚡ 直接设置断点: {js_url}:{line}")
    ws.send(json.dumps({
        "id": msg_id,
        "method": "Debugger.setBreakpointByUrl",
        "params": {
            "url": js_url,
            "lineNumber": line,
            "columnNumber": column,
            "condition": condition
        }
    }))

    # 3. 获取设置结果
    resp = _wait_for_id(ws, msg_id)
    if "error" in resp:
        raise Exception(f"断点设置失败: {resp['error']}")
    print(f"✅ 断点已激活 (ID: {resp['result']['breakpointId']})")

    # 4. 保持连接监听断点触发
    while True:
        msg = json.loads(ws.recv())
        if msg.get("method") == "Debugger.paused":
            print("🔥 断点命中!")
            # 可在此处添加断点命中后的处理逻辑
            ws.send(json.dumps({
                "id": msg_id + 1,
                "method": "Debugger.resume"
            }))


def _wait_for_id(ws, expect_id):
    """等待指定ID的响应"""
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == expect_id:
            return msg