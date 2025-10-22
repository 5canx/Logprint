# Logprint

获取日志断点、实时流式的动态数据工具

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式1：使用上下文管理器（推荐）

```python
from logprint import Logprint

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
    lp.wait()  # 无限等待，按Ctrl+C退出
```

### 方式2：手动管理

```python
from logprint import Logprint

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
lp.wait(10)  # 等待10秒
lp.stop()
```

### 方式3：使用便捷函数

```python
from logprint import create_session, set_breakpoint

lp = create_session()
lp.start()
lp.start_monitor()
lp.navigate("https://www.baidu.com/")

set_breakpoint(
    lp,
    js_url="https://pss.bdstatic.com/static/superman/js/lib/jquery-1-edb203c114.10.2.js",
    line=200,
    column=238,
    condition="console.log(elem.innerText)",
    target_page_url="https://www.baidu.com/"
)

lp.wait(10)
lp.stop()
```

## 快速开始

```python
# 最简单的使用方式
from logprint import Logprint

with Logprint() as lp:
    lp.start_monitor()
    lp.navigate("https://example.com")
    lp.set_breakpoint(
        js_url="https://example.com/script.js",
        line=100,
        column=50,
        condition="console.log('断点触发')",
        target_page_url="https://example.com"
    )
    lp.wait(30)  # 监控30秒
```

## API参考

### Logprint类

#### 方法

- `start()`: 启动浏览器
- `start_monitor()`: 启动控制台监控
- `navigate(url)`: 导航到指定URL
- `set_breakpoint(js_url, line, column, condition, target_page_url)`: 设置断点
- `wait(seconds=None)`: 等待（None表示无限等待）
- `stop()`: 停止Logprint

#### 便捷函数

- `create_session(browser_path=None, user_data_dir=None)`: 创建会话
- `set_breakpoint(logprint_instance, js_url, line, column, condition, target_page_url)`: 设置断点

## 特性

- ✅ 跨平台支持（Windows/macOS/Linux）
- ✅ 自动检测浏览器路径
- ✅ 实时控制台监控
- ✅ JavaScript断点设置
- ✅ 上下文管理器支持
- ✅ 异常处理和资源清理

## 注意事项

- 需要安装Chrome浏览器
- 支持DrissionPage库
- 断点设置使用JavaScript注入方式，不依赖调试端口
- 支持Windows/macOS/Linux跨平台
- 自动检测浏览器路径

## 更新日志

### v2.0.0 (2025-01-20)
- ✅ 重构为单一库文件，类似requests的API设计
- ✅ 移除调试端口依赖，解决Windows兼容性问题
- ✅ 使用JavaScript注入方式设置断点，更稳定
- ✅ 支持上下文管理器，自动资源清理
- ✅ 跨平台浏览器路径自动检测
- ✅ 优化异常处理和错误提示