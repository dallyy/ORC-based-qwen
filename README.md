# 截图OCR工具 - 使用说明

## 文件说明

- `screenshot_ocr.py` - 主程序，实现截图OCR识别功能
- `requirements.txt` - Python依赖包列表
- `config.json` - API密钥配置文件（需自行创建）
- `logs/` - 日志文件目录（自动生成）

## 快速开始

### 1. 安装依赖

首次使用前，确保安装了Python依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

在项目目录下创建 `config.json` 文件，添加API密钥：

```json
{
  "OPENAI_API_KEY": "your_api_key_here",
  "ALIYUN_DASHSCOPE_API_KEY": "your_dashscope_api_key"
}
```

或设置环境变量：
- `OPENAI_API_KEY`
- `ALIYUN_DASHSCOPE_API_KEY`

### 3. 运行程序

```bash
python screenshot_ocr.py
```

## 开机自动启动

### 启用开机自启动

```bash
python screenshot_ocr.py --enable-autostart
```

**功能特点：**
- 自动延迟30秒启动，避免与系统启动冲突
- 程序启动后自动隐藏到后台
- 无需管理员权限
- 使用PowerShell创建快捷方式，更加稳定可靠

### 禁用开机自启动

```bash
python screenshot_ocr.py --disable-autostart
```

### 检查启动状态

```bash
python screenshot_ocr.py --check-autostart
```

### 测试延迟启动

```bash
# 测试5秒延迟启动
python screenshot_ocr.py --delay 5

# 不延迟启动（立即启动）
python screenshot_ocr.py --no-delay
```

### 启动位置

开机启动快捷方式创建在：
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Screenshot_OCR.lnk
```

## 使用快捷键

程序在后台运行时，使用以下快捷键：

- `Ctrl+Alt+A` - 触发截图OCR识别
- `Ctrl+Alt+Q` - 退出程序

## 功能特性

### 核心功能

- 🖼️ **截图OCR识别** - 自由选择屏幕区域进行文字识别
- 📋 **自动复制到剪贴板** - 识别结果自动复制，方便粘贴使用
- 🔄 **JSON响应解析** - 使用标准JSON解析，准确提取识别结果
- 📝 **详细日志记录** - 记录所有操作和API调用过程

### 开机启动特性

- ✅ **安全可靠** - 使用Windows启动文件夹，用户完全可控
- ✅ **无需管理员权限** - 普通用户即可启用
- ✅ **命令行管理** - 简单的命令行参数控制
- ✅ **自动隐藏窗口** - 开机启动后自动隐藏到后台
- ✅ **延迟启动** - 默认延迟30秒，避免系统启动冲突
- ✅ **易于管理** - 可随时启用/禁用，支持手动删除
- 🔧 **PowerShell创建** - 使用PowerShell创建快捷方式，比VBS更稳定
- 🐛 **修复编码问题** - 使用ASCII字符，避免中文乱码
- 🔍 **配置验证** - 自动验证快捷方式配置是否正确

## 使用场景

### 场景1：日常使用

1. 运行程序：`python screenshot_ocr.py`
2. 按 `Ctrl+Alt+A` 进行截图
3. 选择要识别的区域
4. 识别结果自动复制到剪贴板
5. 在任意地方粘贴使用

### 场景2：开机自动启动

1. 启用开机启动：`python screenshot_ocr.py --enable-autostart`
2. 重启电脑
3. 等待30秒（程序延迟启动，避免系统启动冲突）
4. 程序自动启动并隐藏到后台
5. 直接按 `Ctrl+Alt+A` 使用截图功能

**注意：** 开机启动后会延迟30秒激活快捷键，给系统足够时间完成启动过程。

### 场景3：查看日志

```bash
# 查看今天的日志
type logs\screenshot_ocr_20260117.log

# 查看最近的错误
findstr /i "error" logs\screenshot_ocr_20260117.log
```

### 场景4：测试开机启动

```bash
# 测试延迟启动功能
python screenshot_ocr.py --delay 5

# 查看倒计时和快捷键激活过程
python screenshot_ocr.py --delay 5 --no-hide
```

## 命令行参数

```bash
python screenshot_ocr.py [参数]

参数：
  --enable-autostart   启用开机自动启动（默认延迟30秒）
  --disable-autostart  禁用开机自动启动
  --check-autostart    检查开机自动启动状态
  --no-hide            不隐藏控制台窗口（调试用）
  --no-delay           不延迟启动（立即启动）
  --delay <秒数>       自定义延迟启动时间（默认30秒）

示例：
  python screenshot_ocr.py --enable-autostart    # 启用开机启动
  python screenshot_ocr.py --delay 5              # 延迟5秒启动
  python screenshot_ocr.py --no-delay             # 立即启动
  python screenshot_ocr.py --no-hide              # 显示控制台窗口
```

## 日志系统

### 日志位置

日志文件保存在 `logs/` 目录中，按日期命名：
```
logs/screenshot_ocr_20260117.log
```

### 日志内容

- 🚀 程序启动信息
- 🔑 API密钥加载状态
- 📡 API调用过程和响应
- 🔍 文字识别结果
- 📋 剪贴板复制状态
- ❌ 错误和异常信息

### 调试技巧

1. **显示控制台窗口**：
   ```bash
   python screenshot_ocr.py --no-hide
   ```

2. **查看详细日志**：
   ```bash
   type logs\screenshot_ocr_*.log
   ```

3. **检查API响应**：
   在日志中搜索 "API响应" 关键字

## 故障排除

### 程序无法启动

- ✅ 检查Python是否正确安装：`python --version`
- ✅ 安装依赖：`pip install -r requirements.txt`
- ✅ 检查API密钥是否配置正确
- ✅ 查看日志文件了解详细错误

### 识别结果无法粘贴

- ✅ 检查日志中的 "复制到剪贴板" 状态
- ✅ 确认API调用成功（查看日志中的 "识别结果"）
- ✅ 检查是否有其他程序占用剪贴板
- ✅ 尝试手动复制识别结果

### 开机自启动无效

- ✅ 检查启动状态：`python screenshot_ocr.py --check-autostart`
- ✅ 确认快捷方式存在：检查启动文件夹
- ✅ 检查快捷方式配置是否正确（TargetPath应指向python.exe）
- ✅ 确认开机后等待30秒（延迟启动）
- ✅ 检查杀毒软件是否拦截
- ✅ 查看日志中的创建快捷方式记录
- ✅ 验证快捷方式属性：`powershell`查看TargetPath和Arguments

**快捷方式配置示例：**
- TargetPath: `C:\Users\你的用户名\AppData\Local\Programs\Python\Python312\python.exe`
- Arguments: `"C:\ORC_project\screenshot_ocr.py" --delay 30`
- WorkingDirectory: `C:\ORC_project`

### 快捷键无响应

- ✅ 确认程序正在运行（检查任务管理器）
- ✅ 如果是开机启动，确认已等待30秒（延迟启动）
- ✅ 检查日志中的"延迟结束，快捷键已激活"消息
- ✅ 重新启动程序
- ✅ 检查是否有其他程序占用相同快捷键
- ✅ 使用 `--no-hide` 参数启动，查看控制台输出

**开机启动后：**
- 程序会显示倒计时（30秒）
- 倒计时结束后快捷键才激活
- 如需立即激活，使用 `--no-delay` 参数

### API调用失败

- ✅ 检查网络连接
- ✅ 验证API密钥是否正确
- ✅ 查看日志中的详细错误信息
- ✅ 检查API服务商状态

### 延迟启动相关问题

**Q: 为什么开机后要等30秒才能使用快捷键？**
A: 延迟启动是为了避免与Windows系统启动过程冲突，确保系统完全加载后再激活快捷键。

**Q: 如何缩短或取消延迟时间？**
A: 使用 `--no-delay` 参数立即启动，或使用 `--delay <秒数>` 自定义延迟时间。

**Q: 开机启动后程序是否在运行？**
A: 是的，程序会启动并在后台运行。查看任务管理器中的python.exe进程。

**Q: 如何修改已有的开机启动延迟时间？**
A: 禁用后再重新启用开机启动：`python screenshot_ocr.py --disable-autostart` 然后 `python screenshot_ocr.py --enable-autostart`

## 手动管理开机启动

### 方法1：启动文件夹

1. 按 `Win + R` 打开运行对话框
2. 输入 `shell:startup` 并回车
3. 查看/删除 `Screenshot_OCR.lnk` 快捷方式

### 方法2：命令行

```bash
# 启用
python screenshot_ocr.py --enable-autostart

# 禁用
python screenshot_ocr.py --disable-autostart

# 检查状态
python screenshot_ocr.py --check-autostart
```

## 技术细节

### 依赖包

- `openai` - OpenAI API客户端
- `pyperclip` - 剪贴板操作
- `Pillow` - 图像处理
- `keyboard` - 全局快捷键

### API配置

支持两种API：
- OpenAI API (`OPENAI_API_KEY`)
- 阿里云DashScope API (`ALIYUN_DASHSCOPE_API_KEY`)

### 响应解析

使用标准JSON解析API响应：
```json
{
  "choices": [
    {
      "message": {
        "content": "识别的文字内容"
      }
    }
  ]
}
```

### 开机启动实现

使用PowerShell创建Windows快捷方式：
- 快捷方式位置：`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Screenshot_OCR.lnk`
- 启动方式：Python解释器 + 脚本路径 + 延迟参数
- 延迟机制：脚本启动后倒计时，激活快捷键

**快捷方式配置：**
```powershell
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut("快捷方式路径")
$s.TargetPath = "python.exe路径"
$s.Arguments = '"脚本路径" --delay 30'
$s.WorkingDirectory = "工作目录"
$s.WindowStyle = 0  # 隐藏窗口
$s.Save()
```

## 版本历史

### v2.1 (2026-01-17)
- ✨ 新增延迟启动功能（默认30秒）
- 🔧 修复快捷方式创建逻辑（使用PowerShell替代VBS）
- 🔧 修复Unicode编码问题（使用ASCII字符）
- ✨ 新增 `--delay` 和 `--no-delay` 参数
- ✨ 增强开机启动配置验证
- 🐛 修复开机启动后快捷键不生效的问题
- 🔧 改进错误处理和日志记录
- ✨ 自动检测Python解释器路径

### v2.0
- ✨ 新增开机自动启动功能
- ✨ 命令行参数管理
- ✨ 详细日志系统
- 🐛 修复JSON解析问题
- 🔧 改进错误处理

### v1.0
- 🎉 初始版本
- 🖼️ 截图OCR功能
- 📋 自动复制到剪贴板

## 许可证

本项目仅供学习和个人使用。

## 联系方式

如有问题或建议，请查看日志文件或提交Issue。

## 常见问题 FAQ

**Q: 快捷键与其他软件冲突怎么办？**
A: 可以修改代码中的快捷键设置，找到 `keyboard.add_hotkey` 行修改快捷键组合。

**Q: 如何查看程序是否正在运行？**
A: 打开任务管理器，查找 `python.exe` 进程。使用 `--no-hide` 参数可以看到控制台窗口。

**Q: 开机启动后如何手动退出？**
A: 按 `Ctrl+Alt+Q` 或在任务管理器中结束 `python.exe` 进程。

**Q: 日志文件会自动清理吗？**
A: 目前不会自动清理，建议定期清理 `logs/` 目录中的旧日志文件。

**Q: 支持其他语言吗？**
A: 支持，API会自动识别图片中的文字语言，包括中文、英文等。

**Q: 识别准确率如何？**
A: 识别准确率取决于图片清晰度和文字质量，一般来说清晰图片的识别准确率很高。

## 更新日志

### 最新改进 (v2.1)
- 🚀 修复开机启动后快捷键无法使用的问题
- 🔧 使用PowerShell创建快捷方式，提高稳定性
- ✨ 添加延迟启动功能，避免系统启动冲突
- 🐛 修复中文编码问题，避免乱码
- 📝 改进日志记录和错误提示

### 已知问题
- 某些杀毒软件可能会拦截开机启动，需要添加到白名单
- 低分辨率电脑上的OCR识别准确率可能较低