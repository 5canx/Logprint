#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome DevTools Protocol (CDP) 日志断点工具
通过 WebSocket 连接 Chrome 调试端口，设置条件断点并监听触发
"""

import json
import requests
from websocket import create_connection


class LogPoint:
    """日志断点管理器"""
    
    def __init__(self, debug_port=9222):
        """
        初始化
        
        Args:
            debug_port: Chrome 远程调试端口，默认 9222
        """
        self.debug_port = debug_port
        self.base_url = f"http://localhost:{debug_port}"
        self.ws = None
        self.msg_id = 0
    
    def get_targets(self):
        """获取所有调试目标"""
        try:
            resp = requests.get(f"{self.base_url}/json", timeout=5)
            return resp.json()
        except Exception as e:
            raise Exception(f"无法连接调试端口 {self.debug_port}: {e}")
    
    def get_target_ws_url(self, target_page_url):
        """
        获取目标页面的 WebSocket 调试地址
        
        Args:
            target_page_url: 目标页面 URL（前缀匹配）
        
        Returns:
            WebSocket URL
        """
        targets = self.get_targets()
        for t in targets:
            if t.get('url', '').startswith(target_page_url):
                return t.get('webSocketDebuggerUrl')
        
        # 打印可用目标帮助调试
        print("📋 可用的调试目标:")
        for t in targets:
            print(f"   - {t.get('type', 'unknown')}: {t.get('url', 'N/A')}")
        
        raise Exception(f"未找到匹配页面: {target_page_url}")
    
    def _next_id(self):
        """获取下一个消息 ID"""
        self.msg_id += 1
        return self.msg_id
    
    def _send(self, method, params=None):
        """发送 CDP 命令"""
        msg_id = self._next_id()
        msg = {"id": msg_id, "method": method}
        if params:
            msg["params"] = params
        self.ws.send(json.dumps(msg))
        return msg_id
    
    def _wait_for_id(self, expect_id, timeout=30):
        """等待指定 ID 的响应"""
        self.ws.settimeout(timeout)
        while True:
            try:
                msg = json.loads(self.ws.recv())
                if msg.get("id") == expect_id:
                    return msg
            except Exception as e:
                raise Exception(f"等待响应超时: {e}")
    
    def connect(self, target_page_url):
        """
        连接到目标页面
        
        Args:
            target_page_url: 目标页面 URL
        """
        ws_url = self.get_target_ws_url(target_page_url)
        print(f"🔗 连接 WebSocket: {ws_url}")
        self.ws = create_connection(ws_url)
        
        # 启用 Debugger
        msg_id = self._send("Debugger.enable")
        resp = self._wait_for_id(msg_id)
        if "error" in resp:
            raise Exception(f"启用 Debugger 失败: {resp['error']}")
        print("✅ Debugger 已启用")
    
    def set_breakpoint(self, js_url, line, column=0, condition=""):
        """
        设置日志断点
        
        Args:
            js_url: JavaScript 文件 URL
            line: 行号（从 0 开始）
            column: 列号，默认 0
            condition: 条件表达式（用于日志输出）
        
        Returns:
            断点 ID
        """
        print(f"⚡ 设置断点: {js_url}:{line}")
        
        msg_id = self._send("Debugger.setBreakpointByUrl", {
            "url": js_url,
            "lineNumber": line,
            "columnNumber": column,
            "condition": condition
        })
        
        resp = self._wait_for_id(msg_id)
        if "error" in resp:
            raise Exception(f"断点设置失败: {resp['error']}")
        
        breakpoint_id = resp['result']['breakpointId']
        locations = resp['result'].get('locations', [])
        print(f"✅ 断点已激活 (ID: {breakpoint_id}, 位置: {len(locations)})")
        return breakpoint_id
    
    def remove_breakpoint(self, breakpoint_id):
        """移除断点"""
        msg_id = self._send("Debugger.removeBreakpoint", {
            "breakpointId": breakpoint_id
        })
        self._wait_for_id(msg_id)
        print(f"🗑️ 断点已移除: {breakpoint_id}")
    
    def listen(self, on_hit=None, auto_resume=True):
        """
        监听断点触发
        
        Args:
            on_hit: 断点命中回调函数，接收 paused 事件数据
            auto_resume: 是否自动恢复执行，默认 True
        """
        print("👂 开始监听断点触发...")
        
        while True:
            try:
                msg = json.loads(self.ws.recv())
                method = msg.get("method")
                
                if method == "Debugger.paused":
                    print("🔥 断点命中!")
                    
                    if on_hit:
                        on_hit(msg.get("params", {}))
                    
                    if auto_resume:
                        self._send("Debugger.resume")
                        
                elif method == "Debugger.resumed":
                    pass  # 静默处理恢复事件
                    
                elif method == "Debugger.scriptParsed":
                    # 脚本加载事件，可用于调试
                    script_url = msg.get("params", {}).get("url", "")
                    if script_url:
                        print(f"📜 脚本加载: {script_url[:80]}...")
                        
            except KeyboardInterrupt:
                print("\n🛑 用户中断监听")
                break
            except Exception as e:
                print(f"❌ 监听异常: {e}")
                break
    
    def close(self):
        """关闭连接"""
        if self.ws:
            self.ws.close()
            print("🔌 WebSocket 已断开")


# 兼容旧版 API
def get_target_ws_url(target_page_url, debug_port=9222):
    """获取目标页面的 WebSocket 调试地址（兼容旧版）"""
    lp = LogPoint(debug_port)
    return lp.get_target_ws_url(target_page_url)


def set_log_breakpoint(js_url, line, column, condition, target_page_url, debug_port=9222):
    """设置日志断点并监听（兼容旧版）"""
    lp = LogPoint(debug_port)
    lp.connect(target_page_url)
    lp.set_breakpoint(js_url, line, column, condition)
    lp.listen()
