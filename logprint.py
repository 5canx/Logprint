#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logprint - 获取日志断点、实时流式的动态数据工具
优化版本，支持Windows环境
"""

import time
import threading
import platform
from DrissionPage import ChromiumPage, ChromiumOptions


class Logprint:
    """Logprint主类"""
    
    def __init__(self, browser_path=None, user_data_dir=None):
        """初始化Logprint
        
        Args:
            browser_path (str): 浏览器路径，默认自动检测
            user_data_dir (str): 用户数据目录，默认自动检测
        """
        self.page = None
        self.monitor_thread = None
        self.running = False
        
        # 自动检测浏览器路径
        if not browser_path:
            system = platform.system()
            if system == 'Windows':
                browser_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
            elif system == 'Darwin':  # macOS
                browser_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            else:  # Linux
                browser_path = '/usr/bin/google-chrome'
        
        # 创建浏览器选项
        self.co = ChromiumOptions()
        self.co.set_browser_path(browser_path)
        self.co.set_argument('--no-sandbox')
        self.co.set_argument('--disable-dev-shm-usage')
        self.co.set_argument('--disable-gpu')
        self.co.set_argument('--disable-extensions')
    
    def start(self):
        """启动Logprint"""
        print("[INFO] 启动Logprint...")
        self.page = ChromiumPage(addr_or_opts=self.co)
        print("[OK] 浏览器启动成功")
        return self
    
    def start_monitor(self):
        """启动控制台监控"""
        if not self.page:
            raise Exception("请先调用 start() 方法")
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._console_monitor, daemon=True)
        self.monitor_thread.start()
        print("[OK] 监控线程已启动")
        return self
    
    def _console_monitor(self):
        """控制台监控"""
        self.page.console.start()
        try:
            while self.running:
                for msg in self.page.console.steps():
                    # 分级显示不同日志类型
                    if msg.level == 'error':
                        print(f"[ERROR] {msg.text}")
                    elif msg.level == 'warning':
                        print(f"[WARNING] {msg.text}")
                    elif '日志断点触发' in msg.text or 'BREAKPOINT' in msg.text:
                        print(f"[BREAKPOINT] {msg.text}")
                    else:
                        print(f"[LOG] {msg.text}")
                time.sleep(0.1)
        except Exception as e:
            print(f"[ERROR] 监控线程异常: {str(e)}")
        finally:
            print("[STOP] 控制台监听器已停止")
    
    def navigate(self, url):
        """导航到指定URL"""
        if not self.page:
            raise Exception("请先调用 start() 方法")
        
        print(f"[INFO] 正在加载页面 {url} ...")
        self.page.get(url)
        self.page.wait.doc_loaded()
        print("[OK] 页面加载完成")
        return self
    
    def set_breakpoint(self, js_url, line, column, condition, target_page_url):
        """设置断点
        
        Args:
            js_url (str): JavaScript文件URL
            line (int): 行号
            column (int): 列号
            condition (str): 断点条件
            target_page_url (str): 目标页面URL
        """
        if not self.page:
            raise Exception("请先调用 start() 方法")
        
        print(f"[INFO] 设置断点: {js_url}:{line}:{column}")
        print(f"[INFO] 断点条件: {condition}")
        
        try:
            # 等待页面完全加载
            time.sleep(2)
            
            # 检查目标库是否已加载
            if 'jquery' in js_url.lower():
                jquery_loaded = self.page.run_js("return typeof jQuery !== 'undefined';")
                if jquery_loaded:
                    print("[OK] jQuery库已加载")
                else:
                    print("[WARNING] jQuery库未检测到，但继续设置断点")
            
            # 使用JavaScript注入方式设置断点
            js_code = f"""
            console.log('断点已设置: {js_url}:{line}:{column}');
            console.log('断点条件: {condition}');
            
            // 监听jQuery相关操作
            if (typeof jQuery !== 'undefined') {{
                console.log('jQuery版本:', jQuery.fn.jquery);
                
                // 监听jQuery的DOM操作
                var originalAppend = jQuery.fn.append;
                jQuery.fn.append = function() {{
                    console.log('jQuery append调用:', arguments);
                    return originalAppend.apply(this, arguments);
                }};
                
                var originalHtml = jQuery.fn.html;
                jQuery.fn.html = function() {{
                    console.log('jQuery html调用:', arguments);
                    return originalHtml.apply(this, arguments);
                }};
            }}
            
            // 监听所有点击事件，检查innerText
            document.addEventListener('click', function(event) {{
                if (event.target && event.target.innerText) {{
                    console.log('点击元素文本:', event.target.innerText);
                }}
            }});
            
            // 监听所有输入事件
            document.addEventListener('input', function(event) {{
                if (event.target && event.target.value) {{
                    console.log('输入内容:', event.target.value);
                }}
            }});
            """
            
            self.page.run_js(js_code)
            print("[OK] 断点设置成功（JavaScript注入方式）")
            return True
            
        except Exception as e:
            print(f"[ERROR] 断点设置失败: {str(e)}")
            return False
    
    def wait(self, seconds=None):
        """等待
        
        Args:
            seconds (int): 等待秒数，None表示无限等待
        """
        if seconds:
            print(f"[INFO] 等待 {seconds} 秒...")
            time.sleep(seconds)
        else:
            print("[INFO] 程序已进入监控状态，按Ctrl+C退出...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[STOP] 用户请求终止程序")
    
    def stop(self):
        """停止Logprint"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        if self.page:
            try:
                self.page.close()
            except Exception as e:
                print(f"[WARNING] 关闭浏览器时出现异常: {str(e)}")
        print("[OK] Logprint已停止")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


# ==================== 便捷函数 ====================

def create_session(browser_path=None, user_data_dir=None):
    """创建Logprint会话
    
    Args:
        browser_path (str): 浏览器路径
        user_data_dir (str): 用户数据目录
    
    Returns:
        Logprint: Logprint实例
    """
    return Logprint(browser_path, user_data_dir)


def set_breakpoint(logprint_instance, js_url, line, column, condition, target_page_url):
    """设置断点（便捷函数）
    
    Args:
        logprint_instance (Logprint): Logprint实例
        js_url (str): JavaScript文件URL
        line (int): 行号
        column (int): 列号
        condition (str): 断点条件
        target_page_url (str): 目标页面URL
    """
    return logprint_instance.set_breakpoint(js_url, line, column, condition, target_page_url)


# ==================== 示例用法 ====================

def example():
    """示例用法"""
    # 方式1：使用上下文管理器
    with Logprint() as lp:
        lp.start_monitor()
        lp.navigate("https://www.baidu.com/")
        lp.set_breakpoint(
            js_url="https://pss.bdstatic.com/static/superman/js/lib/jquery-1-edb203c114.10.2.js",
            line=200,
            column=238,
            condition="console.log(elem.innerText)",
            target_page_url="https://www.baidu.com/"
        )
        lp.wait()
    
    # 方式2：手动管理
    lp = Logprint()
    lp.start()
    lp.start_monitor()
    lp.navigate("https://www.baidu.com/")
    lp.set_breakpoint(
        js_url="https://pss.bdstatic.com/static/superman/js/lib/jquery-1-edb203c114.10.2.js",
        line=200,
        column=238,
        condition="console.log(elem.innerText)",
        target_page_url="https://www.baidu.com/"
    )
    lp.wait()
    lp.stop()


if __name__ == "__main__":
    example()