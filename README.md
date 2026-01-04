# Logprint

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="license">
  <img src="https://img.shields.io/badge/CDP-Chrome%20DevTools%20Protocol-orange.svg" alt="cdp">
</p>

基于 Chrome DevTools Protocol (CDP) 的日志断点工具，用于获取网页中的实时动态数据流。

## ✨ 功能特性

- 🔍 **日志断点** - 在 JS 代码中设置条件断点，输出变量值
- 📡 **实时监听** - 通过 WebSocket 实时接收断点触发事件
- 🖥️ **控制台监控** - 同步监控页面 console 输出
- 🌐 **跨平台** - 支持 Windows / macOS / Linux
- 🔧 **自动配置** - 自动检测 Chrome 路径

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/5canx/Logprint.git
cd Logprint

# 安装依赖
pip install DrissionPage websocket-client requests
```

## 🚀 快速开始

### 1. 基础用法

```python
from browser_config import init_browser
from LogPoint import LogPoint

# 初始化浏览器（自动开启远程调试）
page = init_browser(headless=False)
page.get("https://example.com")

# 创建日志断点
lp = LogPoint(debug_port=9222)
lp.connect("https://example.com")

# 设置断点
lp.set_breakpoint(
    js_url="https://example.com/app.js",
    line=100,
    condition="console.log('数据:', myData) || false"
)

# 监听断点触发
lp.listen()
```

### 2. 运行示例

```bash
python main.py
```

## 📖 API 文档

### LogPoint 类

```python
from LogPoint import LogPoint

lp = LogPoint(debug_port=9222)
```

#### 方法

| 方法 | 说明 |
|------|------|
| `get_targets()` | 获取所有调试目标 |
| `connect(url)` | 连接到目标页面 |
| `set_breakpoint(js_url, line, column, condition)` | 设置断点 |
| `remove_breakpoint(id)` | 移除断点 |
| `listen(on_hit, auto_resume)` | 监听断点触发 |
| `close()` | 关闭连接 |

### browser_config 模块

```python
from browser_config import init_browser, find_chrome_path

# 初始化浏览器
page = init_browser(
    headless=False,      # 是否无头模式
    user_data_dir=None,  # 用户数据目录
    debug_port=9222      # 调试端口
)

# 查找 Chrome 路径
chrome_path = find_chrome_path()
```

## 🔧 工作原理

```
┌─────────────┐     WebSocket      ┌─────────────┐
│   Python    │ ◄───────────────► │   Chrome    │
│   Script    │    CDP Protocol    │   Browser   │
└─────────────┘                    └─────────────┘
      │                                   │
      │  1. Debugger.enable               │
      │  2. setBreakpointByUrl            │
      │  3. Debugger.paused (event)       │
      │  4. Debugger.resume               │
      ▼                                   ▼
```

1. **启动浏览器** - 开启远程调试端口 (9222)
2. **WebSocket 连接** - 通过 CDP 协议连接浏览器
3. **设置断点** - 在指定 JS 文件的指定行设置条件断点
4. **监听事件** - 接收 `Debugger.paused` 事件
5. **获取数据** - 通过 condition 中的 console.log 输出数据

## 📝 使用场景

- 🔐 获取加密前的明文数据
- 📊 抓取动态渲染的数据
- 🐛 调试复杂的前端逻辑
- 📈 监控 API 请求参数
- 🎯 分析搜索建议等实时数据

## ⚠️ 注意事项

1. **调试端口** - 确保 9222 端口未被占用
2. **脚本 URL** - 需要精确匹配 JS 文件 URL
3. **行号列号** - 需要在浏览器 DevTools 中确认
4. **条件表达式** - 必须返回 `false` 才能继续执行

## 📁 项目结构

```
Logprint/
├── browser_config.py   # 浏览器配置模块
├── LogPoint.py         # CDP 日志断点核心
├── main.py             # 示例程序
└── README.md
```

## 🔗 相关链接

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [DrissionPage 文档](https://drissionpage.cn/)
- [博客教程](https://scan.work/posts/cdp/)

## 📄 许可证

[MIT License](LICENSE)

---

> ⚠️ **免责声明**: 本工具仅供学习交流使用，请勿用于非法用途。

<p align="center">Made with ❤️ by <a href="https://github.com/5canx">Scan</a></p>
