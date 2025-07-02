from DrissionPage import ChromiumPage, ChromiumOptions
from LogPoint import set_log_breakpoint
import time
import threading

co = ChromiumOptions()
co.set_browser_path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
co.set_argument('--remote-debugging-port=9222')
co.set_argument('--user-data-dir=/Users/scan/Library/Application Support/Google/Chrome/Default')
co.set_argument('--auto-open-devtools-for-tabs')
co.set_argument('--remote-allow-origins=*')
page = ChromiumPage(addr_or_opts=co)

def console_monitor():
    page.console.start()
    try:
        while True:
            for msg in page.console.steps():
                # 分级显示不同日志类型
                if msg.level == 'error':
                    print(f"🔴 [ERROR] {msg.text}")
                elif msg.level == 'warning':
                    print(f"🟠 [WARNING] {msg.text}")
                elif '日志断点触发' in msg.text:
                    print(f"🔵 [BREAKPOINT] {msg.text}")
                else:
                    print(f"⚪ [LOG] {msg.text}")
            time.sleep(0.1)
    except Exception as e:
        print(f"❌ 监控线程异常: {str(e)}")
    finally:
        print("🛑 控制台监听器已停止")

def main():

    # 启动监控线程（带状态提示）
    print("🧵 正在启动监控线程...")
    monitor_thread = threading.Thread(target=console_monitor, daemon=True)
    monitor_thread.start()
    print("✅ 监控线程已启动")
    # 打开目标页面（带加载进度）
    print("🌐 正在加载页面 https://www.baidu.com ...")
    page.get("https://www.baidu.com/")
    page.wait.doc_loaded()
    print("✅ 页面加载完成")
    # 在 main() 中添加：
    page.get("https://www.baidu.com")
    page.wait.doc_loaded()

    # 打印所有加载的脚本
    scripts = page.run_js("return Array.from(document.scripts).map(s => s.src);")
    print("📜 页面加载的脚本列表:", scripts)

    # 确认目标脚本是否在列表中
    target_script = "https://pss.bdstatic.com/r/www/cache/static/protocol/https/amd_modules/@baidu/search-sug_7f8d4f1.js"
    if target_script not in scripts:
        print("❌ 目标脚本未加载，请检查URL或页面逻辑")
    # 设置日志断点（带详细状态报告）
    print("⏳ 正在设置日志断点...")
    try:
        set_log_breakpoint(
            js_url="https://pss.bdstatic.com/r/www/cache/static/protocol/https/amd_modules/@baidu/search-sug_7f8d4f1.js",
            line=1825,
            column=17,
            condition="console.log('日志断点触发:', dataArray.map(x=>x.value)) || false",
            target_page_url="https://www.baidu.com/"
        )
        print("✅ 日志断点设置成功")
    except Exception as e:
        print(f"❌ 断点设置失败: {str(e)}")
    # 主线程保持运行（带退出提示）
    print("🚀 程序已进入监控状态，按Ctrl+C退出...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 用户请求终止程序")
    finally:
        page.close()
if __name__ == "__main__":
    main()