import os
import subprocess
import sys
import base64
import io
import json
import re
import argparse
import tkinter as tk
from PIL import Image, ImageGrab
import pyperclip
import ctypes
import logging
from datetime import datetime


def install_dependencies():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        print("检查依赖...")
        with open(requirements_path, "r") as f:
            packages = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]

        missing = []
        for package in packages:
            # 从包名中提取基本名称（去除版本说明符如>=, ==, <=等）
            # 例如: "openai>=1.0.0" -> "openai"
            import re

            base_package = re.split(r"[><=~!]", package)[0].strip()
            try:
                __import__(
                    base_package.lower() if base_package.lower() != "pillow" else "pil"
                )
            except ImportError:
                missing.append(package)

        if missing:
            print(f"安装缺失的依赖: {', '.join(missing)}")
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)


install_dependencies()

# 检查OpenAI版本兼容性
try:
    import openai

    # 检查OpenAI版本是否为1.0+系列（新版API）
    if hasattr(openai, "__version__"):
        version = openai.__version__
        # 新版API v1.0+ 应该与AliYun DashScope API兼容
        if version.startswith("0."):
            print(f"[WARNING] 警告: OpenAI版本 {version} 是旧版API (v0.x)")
            print("  建议升级到 v1.0+：pip install --upgrade openai")
            print(
                "  或参考迁移指南: https://github.com/openai/openai-python/discussions/742"
            )
        else:
            # v1.0+ 版本
            print(f"[OK] OpenAI版本兼容: {version} (v1.0+ API)")
    else:
        print("[WARNING] 无法检测OpenAI版本，可能不兼容")
except ImportError:
    print("[ERROR] OpenAI未安装，请运行: pip install openai")
    sys.exit(1)


# 设置日志
def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir, f"screenshot_ocr_{datetime.now().strftime('%Y%m%d')}.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Screenshot OCR 工具启动")
    logger.info(f"日志文件: {log_file}")
    logger.info("=" * 50)

    return logger


logger = setup_logging()


def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


# DPI awareness for Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


# 配置读取：从 config.json 读取 API Key
def load_api_key():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        logger.info(f"尝试从配置文件加载API密钥: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            key = cfg.get("OPENAI_API_KEY") or cfg.get("ALIYUN_DASHSCOPE_API_KEY")
            if key:
                logger.info("从配置文件成功加载API密钥")
                return key.strip()
    except Exception as e:
        logger.warning(f"从配置文件加载API密钥失败: {e}")

    # 尝试从环境变量加载
    env_key = os.getenv("ALIYUN_DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if env_key:
        logger.info("从环境变量成功加载API密钥")
        return env_key

    logger.error("无法从配置文件或环境变量加载API密钥")
    return None


API_KEY = load_api_key()
if API_KEY:
    logger.info(
        f"API密钥已设置，前10位: {API_KEY[:10] + '...' if len(API_KEY) > 10 else API_KEY}"
    )
else:
    logger.warning("API密钥未设置，OCR功能将无法使用")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen3-vl-plus"


class ScreenshotTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-alpha", 0.3)  # 设置透明度
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.config(cursor="cross")

        # 解决Windows下缩放问题
        try:
            self.root.tk.call("tk", "scaling", 1.0)
        except tk.TclError:
            pass

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey")
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, 1, 1, outline="red", width=2
        )

    def on_move_press(self, event):
        if (
            self.start_x is not None
            and self.start_y is not None
            and self.rect is not None
        ):
            cur_x, cur_y = (event.x, event.y)
            self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        if self.start_x is None or self.start_y is None:
            return
        end_x, end_y = (event.x, event.y)
        self.root.destroy()

        # 确定坐标顺序
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        if x2 - x1 > 5 and y2 - y1 > 5:
            self.take_screenshot(x1, y1, x2, y2)

    def take_screenshot(self, x1, y1, x2, y2):
        # 截取选定区域
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2), all_screens=True)
        self.process_image(img)

    def process_image(self, img):
        # 将图片转换为base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        self.call_ocr_api(img_base64)

    def call_ocr_api(self, img_base64):
        import json  # 确保json模块在函数作用域内

        logger.info("开始调用OCR API进行文字识别")
        print("正在识别文字...")
        if not API_KEY:
            logger.error("API密钥未设置，跳过OCR调用")
            print(
                "未设置 ALIYUN_DASHSCOPE_API_KEY，跳过 OCR 调用。请在环境变量中配置。"
            )
            return
        try:
            logger.info(f"使用OpenAI兼容模式调用API: {BASE_URL}")
            logger.info(f"使用模型: {MODEL_NAME}")
            from openai import OpenAI

            # 初始化OpenAI客户端（新版API v1.0+）
            client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

            logger.info("开始发送API请求...")
            # 使用新版ChatCompletion API
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                },
                            },
                            {
                                "type": "text",
                                "text": "请识别图中的所有文字，并直接输出文字内容，不要包含任何解释或Markdown格式。",
                            },
                        ],
                    }
                ],
                timeout=60,
            )

            # 新版API响应直接是结构化对象
            logger.info(f"API响应类型: {type(completion)}")
            logger.info(f"API响应内容: {str(completion)[:200]}...")

            try:
                logger.info("解析新版API响应对象")

                # 新版API返回结构化对象，可以直接访问属性
                logger.info(f"响应对象属性: {dir(completion)[:20]}...")

                # 检查choices是否存在
                if hasattr(completion, "choices") and completion.choices:
                    choice = completion.choices[0]
                    logger.info(f"找到choices，第一个choice类型: {type(choice)}")

                    # 检查message是否存在
                    if hasattr(choice, "message"):
                        message = choice.message
                        logger.info(f"找到message，message类型: {type(message)}")

                        # 检查content是否存在
                        if hasattr(message, "content") and message.content:
                            actual_result = message.content.strip()
                            logger.info(
                                f"成功提取识别结果，长度: {len(actual_result)} 字符"
                            )
                            logger.info(f"识别结果: {actual_result}")
                            print(f"识别结果: \n{actual_result}")
                            if actual_result:
                                try:
                                    pyperclip.copy(actual_result)
                                    logger.info("成功复制识别结果到剪贴板")
                                    print("\n结果已自动复制到剪贴板。")
                                except Exception as copy_error:
                                    logger.error(f"复制到剪贴板失败: {copy_error}")
                                    print("\n复制到剪贴板失败，请手动复制。")
                            else:
                                logger.warning("识别结果为空，跳过复制")
                                print("\n识别结果为空，未复制。")
                            return  # 成功处理，直接返回
                        else:
                            logger.error("message.content属性不存在或为空")
                            logger.info(
                                f"message.content存在: {hasattr(message, 'content')}"
                            )
                            if hasattr(message, "content"):
                                logger.info(f"message.content值: {message.content}")
                    else:
                        logger.error("choice.message属性不存在")
                        logger.info(
                            f"choice属性: {[attr for attr in dir(choice) if not attr.startswith('_')][:20]}"
                        )
                else:
                    logger.error("completion.choices不存在或为空")
                    logger.info(
                        f"completion.choices存在: {hasattr(completion, 'choices')}"
                    )
                    if hasattr(completion, "choices"):
                        logger.info(f"completion.choices内容: {completion.choices}")

                # 如果直接属性访问失败，尝试JSON解析作为回退
                logger.info("尝试JSON解析作为回退")
                import json

                response_str = str(completion)
                logger.info(f"响应字符串前500字符: {response_str[:500]}...")

                response_dict = json.loads(response_str)
                logger.info("成功将响应解析为JSON对象")
                logger.info(
                    f"JSON结构: {list(response_dict.keys()) if isinstance(response_dict, dict) else 'Not a dict'}"
                )

                # 标准OpenAI API响应结构解析
                if "choices" in response_dict and len(response_dict["choices"]) > 0:
                    choice = response_dict["choices"][0]
                    logger.info(
                        f"找到choices，第一个choice结构: {list(choice.keys()) if isinstance(choice, dict) else 'Not a dict'}"
                    )

                    if (
                        "message" in choice
                        and isinstance(choice["message"], dict)
                        and "content" in choice["message"]
                    ):
                        actual_result = choice["message"]["content"].strip()
                        logger.info(
                            f"通过JSON解析成功提取识别结果，长度: {len(actual_result)} 字符"
                        )
                        logger.info(f"识别结果: {actual_result}")
                        print(f"识别结果: \n{actual_result}")
                        if actual_result:
                            try:
                                pyperclip.copy(actual_result)
                                logger.info("成功复制识别结果到剪贴板")
                                print("\n结果已自动复制到剪贴板。")
                            except Exception as copy_error:
                                logger.error(f"复制到剪贴板失败: {copy_error}")
                                print("\n复制到剪贴板失败，请手动复制。")
                        else:
                            logger.warning("识别结果为空，跳过复制")
                            print("\n识别结果为空，未复制。")
                        return  # 成功处理，直接返回
                    else:
                        logger.error("JSON中缺少message.content字段")
                        logger.info(f"choice['message']存在: {'message' in choice}")
                        if "message" in choice:
                            logger.info(
                                f"choice['message']类型: {type(choice['message'])}"
                            )
                            logger.info(f"choice['message']内容: {choice['message']}")
                else:
                    logger.error("JSON中缺少choices字段或choices为空")
                    logger.info(f"'choices'存在: {'choices' in response_dict}")
                    if "choices" in response_dict:
                        logger.info(f"choices内容: {response_dict['choices']}")
                    logger.info(f"完整JSON结构: {response_dict}")

            except json.JSONDecodeError as je:
                logger.error(f"JSON解析失败: {je}")
                logger.info(f"原始响应字符串: {str(completion)[:1000]}...")
            except Exception as e:
                logger.error(f"响应解析过程出错: {e}", exc_info=True)

            # JSON解析失败的最终回退
            logger.error("响应解析失败，无法提取识别结果")
            print("无法从API响应中提取识别结果")
            final_response = str(completion)
            print(f"完整响应前1000字符: {final_response[:1000]}...")
            logger.debug(f"完整响应: {final_response}")

        except Exception as e:
            logger.error(f"调用OpenAI兼容API发生错误: {e}", exc_info=True)
            print(f"调用API发生错误: {e}")
            # 提供更详细的错误信息
            print(
                f"API Key前10位: {API_KEY[:10] + '...' if API_KEY and len(API_KEY) > 10 else '未设置'}"
            )
            print(f"Base URL: {BASE_URL}")
            print(f"Model: {MODEL_NAME}")

            # 如果OpenAI兼容模式失败，建议用户检查配置
            logger.error("API调用失败，建议用户检查配置")
            print("建议:")
            print("1. 检查网络连接")
            print("2. 验证API密钥")
            print("3. 运行test_api.py进行详细诊断")


def take_screenshot_hotkey():
    tool = ScreenshotTool()
    tool.root.mainloop()


def quit_app():
    sys.exit(0)


def get_startup_folder():
    """获取Windows启动文件夹路径"""
    try:
        appdata = os.getenv("APPDATA")
        if not appdata:
            logger.error("无法获取APPDATA环境变量")
            return None

        startup_folder = os.path.join(
            appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
        )
        return startup_folder
    except Exception as e:
        logger.error(f"获取启动文件夹失败: {e}")
        return None


def get_script_path():
    """获取当前脚本的完整路径"""
    try:
        script_path = os.path.abspath(sys.argv[0])
        return script_path
    except Exception as e:
        logger.error(f"获取脚本路径失败: {e}")
        return os.path.abspath(__file__)


def get_python_executable():
    """获取Python解释器路径"""
    try:
        return sys.executable
    except Exception as e:
        logger.error(f"获取Python解释器路径失败: {e}")
        return "python"


def create_startup_shortcut():
    """创建开机启动快捷方式"""
    try:
        startup_folder = get_startup_folder()
        if not startup_folder:
            logger.error("启动文件夹路径为空")
            return False

        script_path = get_script_path()
        if not script_path:
            logger.error("脚本路径为空")
            return False

        python_executable = get_python_executable()
        if not python_executable:
            logger.error("Python解释器路径为空")
            return False

        shortcut_path = os.path.join(startup_folder, "Screenshot_OCR.lnk")
        working_dir = (
            os.path.dirname(script_path)
            if os.path.dirname(script_path)
            else startup_folder
        )

        # 使用PowerShell创建快捷方式（比VBS更可靠）
        ps_script = f'''$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut("{shortcut_path}")
$s.TargetPath = "{python_executable}"
$s.Arguments = '"{script_path}" --delay 1'
$s.WorkingDirectory = "{working_dir}"
$s.Description = "Screenshot OCR Tool - Auto start with 1s delay"
$s.WindowStyle = 0
$s.Save()
'''

        logger.info(f"创建快捷方式配置:")
        logger.info(f"  TargetPath: {python_executable}")
        logger.info(f'  Arguments: "{script_path}" --delay 1')
        logger.info(f"  WorkingDirectory: {working_dir}")
        logger.info(f"  OutputPath: {shortcut_path}")

        logger.debug(f"PowerShell脚本内容:\n{ps_script}")

        # 运行PowerShell脚本创建快捷方式
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            shell=False,
        )

        if result.stderr:
            logger.warning(f"PowerShell标准错误输出: {result.stderr}")

        if result.returncode == 0:
            if os.path.exists(shortcut_path):
                logger.info(f"成功创建开机启动快捷方式: {shortcut_path}")
                return True
            else:
                logger.error(f"PowerShell执行成功但快捷方式文件不存在: {shortcut_path}")
                return False
        else:
            logger.error(f"创建快捷方式失败，返回码: {result.returncode}")
            logger.error(f"标准错误: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"创建开机启动快捷方式失败: {e}", exc_info=True)
        return False


def remove_startup_shortcut():
    """删除开机启动快捷方式"""
    try:
        startup_folder = get_startup_folder()
        if not startup_folder:
            return False

        shortcut_path = os.path.join(startup_folder, "Screenshot_OCR.lnk")

        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            logger.info(f"成功删除开机启动快捷方式: {shortcut_path}")
            return True
        else:
            logger.info("开机启动快捷方式不存在")
            return False

    except Exception as e:
        logger.error(f"删除开机启动快捷方式失败: {e}", exc_info=True)
        return False


def check_startup_status():
    """检查开机启动状态"""
    try:
        startup_folder = get_startup_folder()
        if not startup_folder:
            return False

        shortcut_path = os.path.join(startup_folder, "Screenshot_OCR.lnk")
        exists = os.path.exists(shortcut_path)

        if exists:
            logger.info(f"开机启动已启用: {shortcut_path}")
            # 尝试验证快捷方式的Python解释器路径
            try:
                python_executable = get_python_executable()
                script_path = get_script_path()
                expected_target = python_executable
                expected_args = f'"{script_path}" --delay 1'
                logger.info(f"预期快捷方式配置:")
                logger.info(f"  TargetPath: {expected_target}")
                logger.info(f"  Arguments: {expected_args}")
            except Exception as verify_error:
                logger.warning(f"验证快捷方式配置时出错: {verify_error}")
        else:
            logger.info("开机启动未启用")

        return exists

    except Exception as e:
        logger.error(f"检查开机启动状态失败: {e}", exc_info=True)
        return False


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="屏幕截图OCR工具 - 自动识别截图中的文字"
    )
    parser.add_argument(
        "--enable-autostart", action="store_true", help="启用开机自动启动"
    )
    parser.add_argument(
        "--disable-autostart", action="store_true", help="禁用开机自动启动"
    )
    parser.add_argument(
        "--check-autostart", action="store_true", help="检查开机自动启动状态"
    )
    parser.add_argument("--no-hide", action="store_true", help="不隐藏控制台窗口")
    parser.add_argument(
        "--no-delay", action="store_true", help="不延迟启动（默认延迟1秒）"
    )
    parser.add_argument("--delay", type=int, default=1, help="启动延迟秒数（默认1秒）")

    args = parser.parse_args()

    # 处理开机启动相关参数
    if args.enable_autostart:
        if create_startup_shortcut():
            print("[OK] 开机自动启动已启用")
            print("  快捷方式已创建到启动文件夹")
        else:
            print("[ERROR] 启用开机自动启动失败")
        return

    if args.disable_autostart:
        if remove_startup_shortcut():
            print("[OK] 开机自动启动已禁用")
        else:
            print("[ERROR] 禁用开机自动启动失败")
        return

    if args.check_autostart:
        is_enabled = check_startup_status()
        if is_enabled:
            print("[OK] 开机自动启动已启用")
        else:
            print("[NOT ENABLED] 开机自动启动未启用")
        return

    # 正常运行模式
    print("屏幕截图OCR工具已启动")
    print("快捷键:")
    print("  Ctrl+Alt+A - 截图OCR")
    print("  Ctrl+Alt+Q - 退出程序")
    print("开机启动管理:")
    print("  python screenshot_ocr.py --enable-autostart   # 启用开机启动")
    print("  python screenshot_ocr.py --disable-autostart  # 禁用开机启动")
    print("  python screenshot_ocr.py --check-autostart   # 检查启动状态")
    print("\n程序已隐藏到后台运行...")

    # 延迟启动功能（默认1秒，可通过--no-disable或--delay参数控制）
    if not args.no_delay and args.delay > 0:
        delay_seconds = args.delay
        logger.info(f"延迟 {delay_seconds} 秒后激活快捷键...")
        print(f"延迟 {delay_seconds} 秒后激活快捷键...")

        import time

        for i in range(delay_seconds, 0, -1):
            if i % 5 == 0 or i <= 5:  # 每5秒或最后5秒显示一次
                print(f"  倒计时: {i} 秒")
            time.sleep(1)

        print("  快捷键已激活!")
        logger.info("延迟结束，快捷键已激活")

    if not args.no_hide:
        hide_console()

    import keyboard

    keyboard.add_hotkey("ctrl+alt+a", take_screenshot_hotkey)
    keyboard.add_hotkey("ctrl+alt+q", quit_app)
    keyboard.wait()


if __name__ == "__main__":
    main()
