#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logprint 主程序
演示如何使用日志断点获取动态数据
"""

import time
import threading
from browser_config import init_browser
from LogPoint import LogPoint


class ConsoleMonitor:
    """控制台日志监控器"""
    
    def __init__(self, page):
        self.page = page
        self.running = False
        self.thread = None
    
    def start(self):
        """启动监控"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
        print("🧵 控制台监控已启动")
    
    def stop(self):
        """停止监控"""
        self.running = False
        print("🛑 控制台监控已停止")
    
    def _monitor(self):
        """监控线程"""
        self.page.console.start()
        try:
            while self.running:
                for msg in self.page.console.steps():
                    self._handle_message(msg)
                time.sleep(0.1)
        except Exception as e:
            print(f"❌ 监控异常: {e}")
    
    def _handle_message(self, msg):
        """处理控制台消息"""
        level = msg.level
        text = msg.text
        
        if level == 'error':
            print(f"🔴 [ERROR] {text}")
        elif level == 'warning':
            print(f"🟠 [WARN] {text}")
        elif '日志断点' in text or 'breakpoint' in text.lower():
            print(f"🔵 [BREAKPOINT] {text}")
        else:
            print(f"⚪ [LOG] {text}")


def list_scripts(page):
    """列出页面加载的所有脚本"""
    scripts = page.run_js("return Array.from(document.scripts).map(s => s.src).filter(s => s);")
    print("\n📜 页面脚本列表:")
    for i, script in enumerate(scripts, 1):
        print(f"   {i}. {script}")
    return scripts


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Logprint - 日志断点数据获取工具")
    print("=" * 60)
    
    # 初始化浏览器
    page = init_browser(headless=False, debug_port=9222)
    
    # 启动控制台监控
    monitor = ConsoleMonitor(page)
    monitor.start()
    
    try:
        # 打开目标页面
        target_url = "https://www.baidu.com"
        print(f"\n🌐 加载页面: {target_url}")
        page.get(target_url)
        page.wait.doc_loaded()
        print("✅ 页面加载完成")
        
        # 列出脚本
        scripts = list_scripts(page)
        
        # 设置日志断点示例
        # 注意：需要根据实际脚本调整 URL 和行号
        target_script = "https://pss.bdstatic.com/r/www/cache/static/protocol/https/amd_modules/@baidu/search-sug_7f8d4f1.js"
        
        if target_script in scripts:
            print(f"\n⚡ 目标脚本已加载: {target_script}")
            
            # 创建日志断点
            lp = LogPoint(debug_port=9222)
            lp.connect(target_url)
            
            # 设置断点（行号需要根据实际脚本调整）
            lp.set_breakpoint(
                js_url=target_script,
                line=1825,
                column=17,
                condition="console.log('🎯 日志断点触发:', dataArray.map(x=>x.value)) || false"
            )
            
            print("\n🎯 断点已设置，在搜索框输入内容触发...")
            print("   按 Ctrl+C 退出\n")
            
            # 监听断点
            lp.listen()
        else:
            print(f"\n⚠️ 目标脚本未加载: {target_script}")
            print("   请检查脚本 URL 或页面逻辑")
            print("\n按 Ctrl+C 退出...")
            
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n\n🛑 用户请求退出")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        monitor.stop()
        page.quit()
        print("👋 程序已退出")


if __name__ == "__main__":
    main()
