#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一浏览器配置模块
支持 Windows / macOS / Linux
"""

import platform
import os
import shutil
import subprocess
from DrissionPage import ChromiumPage, ChromiumOptions


def _get_chrome_paths():
    """获取不同系统的Chrome路径"""
    system = platform.system()
    paths = {
        "Windows": [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            os.path.expanduser(r'~\AppData\Local\Google\Chrome\Application\chrome.exe')
        ],
        "Darwin": ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'],
        "Linux": ['google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium']
    }
    return paths.get(system, [])


def _save_chrome_path(path):
    """保存Chrome路径到环境变量"""
    try:
        system = platform.system()
        if system == "Windows":
            subprocess.run(f'setx CHROME_PATH "{path}"', shell=True, capture_output=True)
        os.environ['CHROME_PATH'] = path
    except Exception as e:
        print(f"⚠️ 保存路径失败: {e}")
        os.environ['CHROME_PATH'] = path


def find_chrome_path():
    """查找Chrome浏览器路径"""
    try:
        env_path = os.environ.get('CHROME_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
        
        system = platform.system()
        paths = _get_chrome_paths()
        
        for path in paths:
            if system == "Linux":
                found = shutil.which(path)
                if found:
                    _save_chrome_path(found)
                    return found
            elif os.path.exists(path):
                _save_chrome_path(path)
                return path
        
        print("❌ 未找到Chrome，请手动指定路径")
        user_path = input("Chrome路径: ").strip()
        if user_path and os.path.exists(user_path):
            _save_chrome_path(user_path)
            return user_path
        return None
            
    except Exception as e:
        print(f"❌ 查找Chrome失败: {e}")
        return None


def init_browser(headless=False, user_data_dir=None, debug_port=9222):
    """
    初始化浏览器（带远程调试）
    
    Args:
        headless: 是否无头模式，默认False（调试需要看到界面）
        user_data_dir: 用户数据目录
        debug_port: 远程调试端口，默认9222
    
    Returns:
        ChromiumPage 实例
    """
    try:
        co = ChromiumOptions()
        
        # Chrome 路径
        chrome_path = find_chrome_path()
        if chrome_path:
            co.set_browser_path(chrome_path)
            print(f"🌐 浏览器: {chrome_path}")
        
        # 无头模式
        if headless:
            co.headless(True)
            co.set_argument('--headless=new')
        
        # 远程调试（CDP 必需）
        co.set_argument(f'--remote-debugging-port={debug_port}')
        co.set_argument('--remote-allow-origins=*')
        
        # 通用参数
        args = [
            '--no-sandbox',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-extensions',
            '--disable-setuid-sandbox',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--window-size=1920,1080',
            '--force-device-scale-factor=1',
            '--auto-open-devtools-for-tabs'  # 自动打开开发者工具
        ]
        
        for arg in args:
            co.set_argument(arg)
        
        # Linux 特有参数
        if platform.system() == "Linux":
            for arg in ['--lang=zh-CN', '--locale=zh-CN', '--hide-scrollbars']:
                co.set_argument(arg)
        
        # 用户数据目录
        if user_data_dir is None:
            system = platform.system()
            if system == "Darwin":
                user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/LogprintProfile")
            elif system == "Windows":
                user_data_dir = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\LogprintProfile")
            else:
                user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
        
        co.set_argument(f'--user-data-dir={user_data_dir}')
        
        page = ChromiumPage(addr_or_opts=co)
        page.set.timeouts(page_load=60, script=60)
        print(f"✅ 浏览器初始化完成 (port={debug_port}, headless={headless})")
        return page
        
    except Exception as e:
        print(f"❌ 浏览器初始化失败: {e}")
        raise


if __name__ == "__main__":
    try:
        browser = init_browser()
        browser.get("https://www.baidu.com")
        print("测试成功！按回车退出...")
        input()
        browser.quit()
    except Exception as e:
        print(f"测试失败: {e}")
