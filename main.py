import sys
import importlib
import os
import signal
import re
import webbrowser
from datetime import datetime
from pypinyin import lazy_pinyin, Style

# ===================== 修复：ANSI颜色/加粗控制码（核心修正COLOR_RED_BOLD） =====================
# 样式说明：\033[1m 加粗 | \033[31m 红色 | \033[32m 绿色 | \033[34m 蓝色 | \033[0m 重置样式
COLOR_BLUE_BOLD = "\033[1;34m"   # 蓝色加粗（用户输入的中文）
COLOR_RED_BOLD = "\033[1;31m"    # 修复：原错误写法是"\033[1m;31m"，多了一个分号导致乱码
COLOR_GREEN_BOLD = "\033[1;32m"  # 绿色加粗（双拼编码/对勾）
COLOR_BOLD = "\033[1m"           # 仅加粗（无颜色）
COLOR_RESET = "\033[0m"          # 重置样式

# ===================== 新增：全局变量 =====================
# 当前激活的双拼方案信息
CURRENT_SCHEME_NAME = ""
CURRENT_SCHEME_DATA = None  # 存储(声母表, 韵母表, 零声母表, 键位表, 反向映射表)
SCHEME_LIST = {}  # 存储从config.py读取的方案列表 {编号: 方案名}
DEFAULT_SCHEME_NUM = 1  # 新增：默认方案编号（从config读取）
HISTORY_ENABLE = 0  # 新增：历史记录开关（0/1）
CLRHIS_LINE_NUM = 0  # 新增：历史记录清除阈值行数
HISTORY_FILE_PATH = ""  # 新增：历史记录文件路径

# ===================== 新增：清屏函数 =====================
def clear_screen():
    """跨平台清屏函数（兼容Windows/Linux/Mac）"""
    # Windows使用cls，其他系统使用clear
    os.system('cls' if os.name == 'nt' else 'clear')

# ===================== 新增：历史记录相关函数 =====================
def count_file_lines(file_path):
    """统计文件行数（静默执行，异常返回0）"""
    try:
        if not os.path.exists(file_path):
            return 0
        with open(file_path, "r", encoding="utf-8") as f:
            return len(f.readlines())
    except Exception:
        return 0

def clear_history_file():
    """清空历史记录文件（静默执行）"""
    try:
        with open(HISTORY_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("")
    except Exception:
        pass

def filter_ansi_chars(text):
    """过滤ANSI控制字符和表情符号"""
    # 移除ANSI控制码
    ansi_pattern = re.compile(r'\033\[[0-9;]*m')
    text = ansi_pattern.sub('', text)
    # 移除指定表情符号，添加🔴到列表中
    emoji_pattern = re.compile(r'[🔎🔍🔀📋🎯🔖🔢⏮️🔽🔼⏭️▶️🧹❓🗑️🚶🕒📂🗂️⭐🔴]')
    text = emoji_pattern.sub('', text)
    # 去除首尾空格
    return text.strip()


def get_formatted_datetime():
    """获取格式化的时间字符串：26-01-20 08:47:22（年取后两位，月日补零）"""
    now = datetime.now()
    return now.strftime("%y-%m-%d %H:%M:%S")

def write_history(content, is_input=False, is_output=False):
    """
    写入历史记录（静默执行）
    :param content: 内容
    :param is_input: 是否为用户输入
    :param is_output: 是否为终端输出
    """
    if HISTORY_ENABLE != 1:
        return
    
    # 过滤空输入/回车的记录
    if is_input and content.strip() in ["用户输入：", "用户输入： "]:
        return
    
    # 过滤非编码/解码相关内容（仅保留双拼/编码解码输入输出）
    exclude_keywords = [
        "显示完整使用指南", "显示可用方案列表", "切换方案到", "执行清屏操作",
        "显示当前方案信息", "历史记录文件已清空", "用户输入：/", "用户输入：+",
        "用户输入：-", "用户输入：\\", "用户输入：*", "用户输入：.", "用户输入：?",
        "用户输入：？", "用户输入：!", "用户输入：！", "用户输入：@", "用户输入：>",
        "用户输入：0", "程序启动", "👋 程序已退出", "📄 读取文件内容",
        "用户输入：%", "用户输入：#", "用户输入：$",
        # 过滤数字切换方案的输入
        "用户输入：1", "用户输入：2", "用户输入：3", "用户输入：4", "用户输入：5",
        "用户输入：6", "用户输入：7", "用户输入：8", "用户输入：9"
    ]
    for keyword in exclude_keywords:
        if keyword in content:
            return
    
    try:
        # 检测行数并清空
        if CLRHIS_LINE_NUM > 0:
            line_count = count_file_lines(HISTORY_FILE_PATH)
            if line_count > CLRHIS_LINE_NUM:
                clear_history_file()
        
        # 过滤特殊字符
        filtered_content = filter_ansi_chars(content)
        if not filtered_content:
            return
        
        # 格式化时间和前缀（修复：输出内容前面去掉多余的>）
        dt_str = get_formatted_datetime()
        if is_input:
            # 修复：去掉"用户输入："前缀，直接保留输入内容
            filtered_content = filtered_content.replace("用户输入：", "").strip()
            log_line = f"[< {dt_str}]  {filtered_content}"
        elif is_output:
            log_line = f"[> {dt_str}]  {filtered_content}"
        else:
            # 非输入输出类内容不记录
            return
        
        # 追加内容
        with open(HISTORY_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(f"{log_line}\n")
    except Exception:
        pass

# ===================== 新增：修改历史记录开关配置 =====================
def toggle_history_switch():
    """切换历史记录开关（修改config.py中的history值）"""
    global HISTORY_ENABLE
    config_path = os.path.join(ROOT_PATH, "config.py")
    
    try:
        # 读取原有配置
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 修改history行
        new_lines = []
        history_updated = False
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("history="):
                # 切换值
                current_val = stripped_line.split("=")[1].strip()
                new_val = "0" if current_val == "1" else "1"
                new_lines.append(f"history={new_val}\n")
                HISTORY_ENABLE = int(new_val)
                history_updated = True
            else:
                new_lines.append(line)
        
        # 如果没有找到history行，追加一行
        if not history_updated:
            new_lines.append(f"history={1 if HISTORY_ENABLE == 0 else 0}\n")
            HISTORY_ENABLE = 1 if HISTORY_ENABLE == 0 else 0
        
        # 写入修改后的配置
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        
        # 提示信息
        status = "开启" if HISTORY_ENABLE == 1 else "关闭"
        tip_msg = f"🕒 历史记录功能已{status}（config.py中history={HISTORY_ENABLE}）"
        print(tip_msg)
        print()  # 单行空行
        write_history(tip_msg)
        return True
    except Exception as e:
        err_msg = f"❌ 修改历史记录开关失败：{e}"
        print(err_msg)
        write_history(err_msg)
        return False

# ===================== 新增：打开目录函数 =====================
def open_directory(dir_path):
    """使用Windows资源管理器打开指定目录"""
    try:
        if os.name == 'nt' and os.path.exists(dir_path):
            os.startfile(dir_path)  # Windows特有
            if dir_path == ROOT_PATH:
                tip_msg = f"📂 已打开config目录：{dir_path}"
            elif dir_path == METHOD_DIR:
                tip_msg = f"🗂️ 已打开method目录：{dir_path}"
            else:
                tip_msg = f"📂 已打开目录：{dir_path}"
            print(tip_msg)
        else:
            if dir_path == ROOT_PATH:
                tip_msg = f"⚠️  仅支持Windows系统打开config目录"
            elif dir_path == METHOD_DIR:
                tip_msg = f"⚠️  仅支持Windows系统打开method目录"
            else:
                tip_msg = f"⚠️  仅支持Windows系统打开目录"
            print(tip_msg)
        print()  # 单行空行
        write_history(tip_msg)
    except Exception as e:
        err_msg = f"❌ 打开目录失败：{e}"
        print(err_msg)
        write_history(err_msg)

# ===================== 新增：打印使用指南函数 =====================
def print_usage_guide():
    """打印完整的使用指南（包含当前激活方案的对勾标记）"""
    # 核心修改：动态获取最小/最大方案编号
    sorted_nums = sorted(SCHEME_LIST.keys())
    min_scheme_num = sorted_nums[0] if sorted_nums else 1
    max_scheme_num = sorted_nums[-1] if sorted_nums else 1
    num_range = f"{min_scheme_num}-{max_scheme_num}" if len(sorted_nums) > 1 else f"{min_scheme_num}"
    
    # 获取默认方案名称
    default_scheme_name = SCHEME_LIST.get(DEFAULT_SCHEME_NUM, "")
    
    # 获取历史记录当前状态
    history_status = "已开启" if HISTORY_ENABLE == 1 else "已关闭"
    
    # 获取history.txt行数和clrhis值
    history_line_count = count_file_lines(HISTORY_FILE_PATH)
    clrhis_value = CLRHIS_LINE_NUM
    
    # 核心还原：移除标题上方的空行，输入?时无多余空行
    print(f"{COLOR_BOLD}===== 双拼转换工具 v0.0.19（支持清屏+多方案切换+帮助查询）====={COLOR_RESET}")
    print(f"{COLOR_BOLD}【参与开发】{COLOR_RESET}苏鱼鱼、小川、豆包（doubao.com）")
    print(f"{COLOR_BOLD}【GitHub】{COLOR_RESET}https://github.com/ChaserSu/DBInputSp")
    print(f"{COLOR_BOLD}【可用方案】{COLOR_RESET}")
    for num, name in sorted(SCHEME_LIST.items()):
        # 核心修改：对当前激活的方案显示绿色对勾且整行加粗
        is_current = f"{COLOR_GREEN_BOLD} ✅{COLOR_RESET}" if name == CURRENT_SCHEME_NAME else ""
        if name == CURRENT_SCHEME_NAME:
            print(f"{COLOR_BOLD}  {num} → {name}{is_current}{COLOR_RESET}")
        else:
            print(f"  {num} → {name}{is_current}")
    print(f"{COLOR_BOLD}【双拼转换】{COLOR_RESET}")  # 修改：【输入内容】替换为【双拼转换】
    print(f"🔎 {COLOR_BLUE_BOLD}输入中文回车{COLOR_RESET} → {COLOR_GREEN_BOLD}正查双拼{COLOR_RESET}")
    print(f"🔍 {COLOR_GREEN_BOLD}输入编码回车{COLOR_RESET} → {COLOR_RED_BOLD}反查全拼{COLOR_RESET}")
    print("🔀 混合输入回车 → 分行处理")
    print(f"{COLOR_BOLD}【切换方案】{COLOR_RESET}")
    print(f"📋 输入“@”回车 → 显示可用方案")
    print(f"🎯 输入“@方案名”回车，例如“@{default_scheme_name}”回车 → 切换对应方案")  # 修改：XXX替换为默认方案名
    print(f"🔖 输入“!”或“！”回车 → 显示当前方案序号及名称")
    print(f"📋 输入“0”回车 → 查当前方案编码表")
    print(f"🔢 输入数字{num_range}回车 → 切换对应方案")
    print(f"⏮️ 输入“/”回车 → 切换序号为{min_scheme_num}的方案（首个）")  # emoji与文字间一个空格
    print(f"🔽 输入“+”回车 → 切换下一个方案（循环）")
    print(f"🔼 输入“-”回车 → 切换上一个方案（循环）")
    print(f"⏭️ 输入“\\”回车 → 切换序号为{max_scheme_num}的方案（末个）")  # emoji与文字间一个空格
    print(f"⭐ 输入“*”回车 → 切换序号为{DEFAULT_SCHEME_NUM}的方案（默认）")  # emoji与文字间一个空格
    print(f"{COLOR_BOLD}【其他操作】{COLOR_RESET}")
    print("🧹 输入“.”回车 → 清空屏幕")
    print(f"🕒 输入“%”回车 → 开/关历史（当前{history_status}）")  # 修改：增加历史状态备注
    print(f"🗑️ 输入“>”回车 → 手动清空历史（当前history.txt有{history_line_count}条，达到{clrhis_value}条后自动清空）")  # 修改：增加历史文件行数和clrhis备注
    print("📂 输入“#”回车 → 打开当前config目录")
    print("🗂️ 输入“$”回车 → 打开当前method目录")
    print("🌐 输入“=”回车 → 打开双拼键位表和练习页面（来自 https://github.com/BlueSky-07/Shuang）")
    print("❓ 输入“?”或“？”回车 → 显示本指南")
    print("🚶 Ctrl+C → 退出程序")
    # 核心新增：在使用指南最后一行后添加空行（分隔输入提示符）
    print()
    # 写入历史记录（非编码相关，会被过滤）
    write_history(f"显示完整使用指南")

def print_scheme_only():
    """仅显示可用方案列表（标记当前方案）"""
    print(f"{COLOR_BOLD}【可用方案】{COLOR_RESET}")
    for num, name in sorted(SCHEME_LIST.items()):
        is_current = f"{COLOR_GREEN_BOLD} ✅{COLOR_RESET}" if name == CURRENT_SCHEME_NAME else ""
        # 核心修改：当前方案行加粗
        if name == CURRENT_SCHEME_NAME:
            print(f"{COLOR_BOLD}  {num} → {name}{is_current}{COLOR_RESET}")
        else:
            print(f"  {num} → {name}{is_current}")
    # 添加Tips文字
    sorted_nums = sorted(SCHEME_LIST.keys())
    min_scheme_num = sorted_nums[0] if sorted_nums else 1
    max_scheme_num = sorted_nums[-1] if sorted_nums else 1
    num_range = f"{min_scheme_num}-{max_scheme_num}" if len(sorted_nums) > 1 else f"{min_scheme_num}"
    # 获取默认方案名称
    default_scheme_name = SCHEME_LIST.get(DEFAULT_SCHEME_NUM, "")
    print(f"🔢 输入数字{num_range}回车 → 切换对应方案")
    print(f"🎯 输入“@方案名”回车，例如“@{default_scheme_name}”回车 → 切换对应方案")  # 修改：XXX替换为默认方案名
    print()  # 单行空行
    # 写入历史记录（非编码相关，会被过滤）
    write_history("显示可用方案列表")

# ===================== 新增：获取当前方案编号 =====================
def get_current_scheme_num():
    """获取当前激活方案对应的编号"""
    for num, name in SCHEME_LIST.items():
        if name == CURRENT_SCHEME_NAME:
            return num
    # 未找到时返回第一个方案编号
    return sorted(SCHEME_LIST.keys())[0]

# ===================== 新增：切换方案辅助函数 =====================
def switch_to_next_scheme():
    """切换到下一个方案（循环）"""
    current_num = get_current_scheme_num()
    sorted_nums = sorted(SCHEME_LIST.keys())
    current_idx = sorted_nums.index(current_num)
    # 计算下一个索引，循环处理
    next_idx = (current_idx + 1) % len(sorted_nums)
    next_num = sorted_nums[next_idx]
    return switch_scheme(next_num)

def switch_to_prev_scheme():
    """切换到上一个方案（循环）"""
    current_num = get_current_scheme_num()
    sorted_nums = sorted(SCHEME_LIST.keys())
    current_idx = sorted_nums.index(current_num)
    # 计算上一个索引，循环处理
    prev_idx = (current_idx - 1) % len(sorted_nums)
    prev_num = sorted_nums[prev_idx]
    return switch_scheme(prev_num)

def switch_to_first_scheme():
    """切换到第一个方案（序号最小的方案）"""
    first_num = sorted(SCHEME_LIST.keys())[0]
    return switch_scheme(first_num)

def switch_to_last_scheme():
    """切换到最后一个方案（序号最大的方案）"""
    last_num = sorted(SCHEME_LIST.keys())[-1]
    return switch_scheme(last_num)

def switch_to_default_scheme():
    """切换到默认编号的方案"""
    return switch_scheme(DEFAULT_SCHEME_NUM)

def switch_scheme_by_name(scheme_name):
    """根据方案名切换方案（绝对匹配）"""
    global CURRENT_SCHEME_NAME, CURRENT_SCHEME_DATA
    # 查找方案名对应的编号
    target_num = None
    for num, name in SCHEME_LIST.items():
        if name == scheme_name:
            target_num = num
            break
    if target_num is None:
        err_msg = f"❌ 错误：未找到名为“{scheme_name}”的方案，请检查config.py中的配置"
        print(err_msg)
        print()  # 错误提示后换行
        print_scheme_only()  # 打印可用方案列表
        write_history(err_msg)
        return False
    # 调用原有切换函数
    return switch_scheme(target_num)

# ===================== 新增：获取程序根路径（核心修改） =====================
def get_root_path():
    """
    获取程序运行的根路径：
    - 源码运行：返回当前文件所在目录
    - exe运行：返回exe文件所在目录
    """
    if getattr(sys, 'frozen', False):
        # exe 打包运行模式
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 源码运行模式
        return os.path.dirname(os.path.abspath(__file__))

# ===================== 关键修改：将根路径加入模块搜索路径 =====================
ROOT_PATH = get_root_path()
# 将程序根目录加入sys.path，才能动态导入根目录下的config.py
sys.path.append(ROOT_PATH)

# 拼接 method 目录路径，并加入系统模块搜索路径
METHOD_DIR = os.path.join(ROOT_PATH, "method")
sys.path.append(METHOD_DIR)

# 初始化历史记录文件路径
HISTORY_FILE_PATH = os.path.join(ROOT_PATH, "history.txt")

# ===================== 新增：读取config.py中的配置项 =====================
def load_config():
    """读取config.py中的方案列表、default、history、clrhis配置"""
    scheme_dict = {}
    default_num = 1
    history = 0
    clrhis = 0
    config_path = os.path.join(ROOT_PATH, "config.py")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 解析每一行，过滤注释和空行
        for line in lines:
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith("#"):
                continue
            
            # 解析default配置
            if line.startswith("default="):
                try:
                    default_num = int(line.split("=")[1].strip())
                except (ValueError, IndexError):
                    print(f"⚠️  警告：config.py中default配置无效，使用默认值1")
                    default_num = 1
                continue
            
            # 解析history配置
            if line.startswith("history="):
                try:
                    history = int(line.split("=")[1].strip())
                    history = 1 if history == 1 else 0
                except (ValueError, IndexError):
                    print(f"⚠️  警告：config.py中history配置无效，使用默认值0")
                    history = 0
                continue
            
            # 解析clrhis配置
            if line.startswith("clrhis="):
                try:
                    clrhis = int(line.split("=")[1].strip())
                    clrhis = clrhis if clrhis >= 0 else 0
                except (ValueError, IndexError):
                    print(f"⚠️  警告：config.py中clrhis配置无效，使用默认值0")
                    clrhis = 0
                continue
            
            # 解析方案列表（格式：编号 方案名）
            parts = line.split()
            if len(parts) != 2:
                print(f"⚠️  警告：config.py中无效行 '{line}'，格式应为 编号 方案名")
                continue
            
            # 检查编号是否为≥1的正整数
            try:
                num = int(parts[0])
                if num < 1:
                    print(f"⚠️  警告：config.py中编号 '{num}' 无效，必须≥1")
                    continue
            except ValueError:
                print(f"⚠️  警告：config.py中 '{parts[0]}' 不是有效数字")
                continue
            
            scheme_name = parts[1]
            scheme_dict[num] = scheme_name
        
        if not scheme_dict:
            print(f"❌ 错误：config.py中未找到有效双拼方案配置")
            sys.exit(1)
        
        # 验证default_num是否在方案列表中
        if default_num not in scheme_dict:
            print(f"⚠️  警告：default={default_num} 不在有效方案编号中，使用第一个方案编号")
            default_num = sorted(scheme_dict.keys())[0]
        
        return scheme_dict, default_num, history, clrhis
    
    except FileNotFoundError:
        print(f"❌ 错误：未找到 config.py 文件，请检查 {config_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 读取config.py失败：{e}")
        sys.exit(1)

# ===================== 修改：加载指定双拼方案 =====================
def load_scheme(scheme_name):
    """
    从exe所在目录的method文件夹加载双拼方案
    返回：声母表、韵母表、零声母表、键位表、反向映射表
    """
    try:
        # 直接导入模块（已将method目录加入sys.path）
        scheme_module = importlib.import_module(scheme_name)
        return (
            scheme_module.SHENGMU,
            scheme_module.YUNMU,
            scheme_module.LING_SHENGMU,
            scheme_module.KEY_MAP,
            scheme_module.REVERSE_MAP
        )
    except ModuleNotFoundError:
        print(f"❌ 错误：未找到 {scheme_name} 方案，请检查 {METHOD_DIR}/{scheme_name}.py")
        return None
    except AttributeError as e:
        print(f"❌ 错误：{scheme_name}.py 缺少配置项 {e}")
        return None

# ===================== 新增：切换双拼方案（核心修改：移除成功提示） =====================
def switch_scheme(scheme_num):
    """
    根据编号切换双拼方案（静默切换，无成功提示）
    :param scheme_num: 方案编号（整数）
    :return: 是否切换成功
    """
    global CURRENT_SCHEME_NAME, CURRENT_SCHEME_DATA
    
    # 检查编号是否有效
    if scheme_num not in SCHEME_LIST:
        err_msg = f"❌ 无效编号！可选方案：{SCHEME_LIST}"
        print(err_msg)
        write_history(err_msg)
        return False
    
    scheme_name = SCHEME_LIST[scheme_num]
    # 加载方案数据
    scheme_data = load_scheme(scheme_name)
    if scheme_data is None:
        return False
    
    # 更新全局变量（仅移除了成功提示的打印语句）
    CURRENT_SCHEME_NAME = scheme_name
    CURRENT_SCHEME_DATA = scheme_data
    # 写入历史记录（非编码相关，会被过滤）
    write_history(f"切换方案到：{scheme_num} → {scheme_name}")
    return True

# ===================== 2. 全拼处理工具（基于pypinyin，添加零声母支持） =====================
def chinese_to_quangpin_list(chinese_str):
    """将中文转换为不带声调的全拼列表"""
    return lazy_pinyin(chinese_str, style=Style.NORMAL)

def split_quangpin_to_shengmu_yunmu(quangpin, shengmu_map, yunmu_map, ling_shengmu_map):
    """
    根据双拼方案拆分全拼为 声母+韵母，优先处理零声母
    :param quangpin: 单个全拼（如 xiao, ao）
    :param shengmu_map: 声母表
    :param yunmu_map: 韵母表
    :param ling_shengmu_map: 零声母表
    :return: (声母键位, 韵母键位)
    """
    shengmu = ""
    yunmu_part = quangpin
    # 步骤1：匹配最长声母（如 zh 优先于 z）
    for sm in sorted(shengmu_map.keys(), key=lambda x: len(x), reverse=True):
        if quangpin.startswith(sm):
            shengmu = sm
            yunmu_part = quangpin[len(sm):]
            break

    # 步骤2：优先处理零声母（无声母时，优先用零声母表）
    if not shengmu:
        return "", ling_shengmu_map.get(quangpin, yunmu_map.get(quangpin, quangpin.upper()))
    else:
        # 有生母，取声母键位 + 韵母键位
        shengmu_key = shengmu_map[shengmu]
        yunmu_key = yunmu_map.get(yunmu_part, yunmu_part.upper())
        return shengmu_key, yunmu_key

# ===================== 新增：无分隔符双拼编码切分函数（修复oo/aa/ee切分） =====================
def split_doupin_code(code_str, shengmu_map, ling_shengmu_map):
    """
    无分隔符双拼编码智能切分：将连续字符串拆分为双拼编码列表（带'分隔）
    新增：优先处理oo/aa/ee为单个编码
    :param code_str: 无分隔符双拼编码（如 yzhfyi）
    :param shengmu_map: 声母表（值为键位）
    :param ling_shengmu_map: 零声母表（值为键位）
    :return: 带分隔符的编码字符串（如 yz'hf'yi）
    """
    # 新增：零声母重复字母规则（优先处理）
    zero_duplicate_list = ['oo', 'aa', 'ee']
    code_str = code_str.lower().strip()
    split_result = []
    idx = 0
    length = len(code_str)
    
    while idx < length:
        # 步骤0：优先匹配oo/aa/ee（核心修复）
        if idx + 1 < length and code_str[idx:idx+2] in zero_duplicate_list:
            split_result.append(code_str[idx:idx+2])
            idx += 2
        # 步骤1：尝试匹配零声母（单字符）
        elif code_str[idx].upper() in [v.upper() for v in ling_shengmu_map.values()]:
            split_result.append(code_str[idx])
            idx += 1
        # 步骤2：尝试匹配「声母+韵母」双字符
        elif idx + 1 < length and code_str[idx].upper() in [v.upper() for v in shengmu_map.values()]:
            split_result.append(code_str[idx:idx+2])
            idx += 2
        # 步骤3：无法匹配，保留原字符并后移
        else:
            split_result.append(code_str[idx])
            idx += 1
    
    # 拼接为带'分隔的字符串
    return "'".join(split_result).lower()

# ===================== 3. 三大核心功能（正查添加零声母参数） =====================
def forward_convert(chinese_str, shengmu_map, yunmu_map, ling_shengmu_map):
    """正查：中文 → 双拼编码（核心修改：传入零声母表，结果转小写）"""
    if not chinese_str.strip():
        return "输入不能为空"
    quangpin_list = chinese_to_quangpin_list(chinese_str)
    code_list = []
    for quangpin in quangpin_list:
        # 传入零声母表，实现零声母优先匹配
        sm_key, ym_key = split_quangpin_to_shengmu_yunmu(quangpin, shengmu_map, yunmu_map, ling_shengmu_map)
        code = f"{sm_key}{ym_key}".strip()
        code_list.append(code)
    # 结果转小写
    return "'".join(code_list).lower()

def reverse_convert_single(code_str, shengmu_map, yunmu_map, ling_shengmu_map, reverse_map):
    """
    反查单个双拼编码 → 全拼（修复：oo/aa/ee整串解析+结果列表追加+v→ü/ui完整映射）
    :param code_str: 单个双拼编码字符串（带'或无分隔符）
    :param shengmu_map: 声母表
    :param yunmu_map: 韵母表
    :param ling_shengmu_map: 零声母表
    :param reverse_map: 反向映射表
    :return: (切分后的编码, 反查结果)
    """
    if not code_str.strip():
        return "", "输入不能为空"
    
    # 核心修复：优先处理整串输入的oo/aa/ee（按单个字解析）
    zero_duplicate_map = {'oo': 'o', 'aa': 'a', 'ee': 'e'}
    code_lower = code_str.lower().strip()
    if code_lower in zero_duplicate_map:
        return code_lower, zero_duplicate_map[code_lower]
    
    split_code = code_str
    # 步骤1：判断是否为无分隔符编码（无'且长度>1）
    if "'" not in code_str and len(code_str.strip()) > 1:
        split_code = split_doupin_code(code_str, shengmu_map, ling_shengmu_map)
    
    # 步骤2：构建反向映射
    sm_key_to_py = {v.lower(): k for k, v in shengmu_map.items()}  # 键位→声母
    ym_key_to_py = {v.lower(): k for k, v in yunmu_map.items()}    # 键位→韵母
    ling_key_to_py = {v.lower(): k for k, v in ling_shengmu_map.items()}  # 键位→零声母韵母

    code_list = split_code.split("'")
    quangpin_list = []

    for code in code_list:
        code_item = code.lower().strip()
        if not code_item:
            continue
        full_py = ""

        # 匹配零声母重复字母（片段级）
        if code_item in zero_duplicate_map:
            full_py = zero_duplicate_map[code_item]
        # 其次匹配零声母编码（单字符）
        elif code_item in ling_key_to_py:
            full_py = ling_key_to_py[code_item]
        # 匹配普通2位双拼编码（声母键+韵母键）
        elif len(code_item) == 2:
            sm_key = code_item[0]
            ym_key = code_item[1]
            
            # 获取声母（如 u→sh、d→d、j→j、n→n）
            sm_py = sm_key_to_py.get(sm_key, sm_key)
            # 完整的v韵母映射规则
            if ym_key == 'v':
                # 场景1：n/l/j/q/x + v → 对应ü（如 nv→nü、jv→jü、qv→qü、xv→xü）
                if sm_py in ['n', 'l', 'j', 'q', 'x']:
                    ym_py = 'ü'
                # 场景2：其他声母 + v → 对应ui（如 dv→dui、uv→shui）
                else:
                    ym_py = 'ui'
            else:
                # 非v韵母，正常映射
                ym_py = ym_key_to_py.get(ym_key, ym_key)
            
            full_py = sm_py + ym_py
        # 单字符非零声母（兜底）
        else:
            # 单字符v → 默认ui
            if code_item == 'v':
                full_py = 'ui'
            else:
                full_py = ym_key_to_py.get(code_item, sm_key_to_py.get(code_item, code_item))
        
        # 核心修复：将解析后的全拼追加到结果列表
        quangpin_list.append(full_py)

    # 拼接全拼结果并返回
    final_quangpin = "'".join(quangpin_list).lower()
    return split_code, final_quangpin

def reverse_convert(code_str, shengmu_map, yunmu_map, ling_shengmu_map, reverse_map):
    """兼容多编码的反查入口（兼容原有逻辑）"""
    split_code, result = reverse_convert_single(code_str, shengmu_map, yunmu_map, ling_shengmu_map, reverse_map)
    if "'" not in code_str and len(code_str.strip()) > 1:
        tip_msg = f"🔍 自动切分编码：{split_code}"
        print(tip_msg)
        write_history(tip_msg)
    return result

def show_key_table(key_map):
    """查表：生成键位对照表"""
    key_group = {}
    for quangpin, key in key_map.items():
        if key not in key_group:
            key_group[key] = []
        key_group[key].append(quangpin)
    table_lines = []
    for key in sorted(key_group.keys()):
        quangpins = "; ".join(key_group[key])
        table_lines.append(f"{key} = {quangpins}")
    return "\n".join(table_lines)

# ===================== 5. 辅助函数：判断输入内容类型 =====================
def is_chinese(text):
    """判断输入文本是否包含中文"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def is_english(text):
    """判断输入文本是否为英文（仅ASCII字母、单引号和分号）"""
    text = text.strip()
    if not text:
        return False
    for char in text:
        # 仅允许ASCII字母、单引号和分号（分号在某些双拼方案中用于编码）
        if not ((65 <= ord(char) <= 90 or 97 <= ord(char) <= 122) or char == "'" or char == ";"):
            return False
    return True

def is_scheme_number(text):
    """判断输入是否为方案切换编号（纯数字）"""
    text = text.strip()
    if not text:
        return False
    try:
        num = int(text)
        return num in SCHEME_LIST
    except ValueError:
        return False

# ===================== 6. 新功能执行逻辑（核心修改：支持混合输入中文+双拼） =====================
def auto_run(input_content):
    """根据输入内容自动执行对应功能（支持：切换方案、清屏、显示帮助、正查、反查、查表）"""
    global CURRENT_SCHEME_DATA
    
    # 写入输入内容到历史记录（标记为用户输入）
    write_history(f"用户输入：{input_content}", is_input=True)
    
    # 拆分输入为多个片段（按任意数量空格分割）
    input_segments = [seg.strip() for seg in input_content.split() if seg.strip()]
    
    # 空输入（空格/回车）：仅返回True，不执行任何操作（无空行）
    if not input_segments:
        return True
    
    # 处理@方案名切换逻辑
    if input_content.strip().startswith("@") and len(input_content.strip()) > 1:
        scheme_name = input_content.strip()[1:]
        switch_scheme_by_name(scheme_name)
        return True
    
    # 新增：绝对匹配输入/ → 切换到序号最小的方案
    if input_content.strip() == "/":
        switch_to_first_scheme()
        return True
    
    # 新增：绝对匹配输入+ → 切换到下一个方案（循环）
    if input_content.strip() == "+":
        switch_to_next_scheme()
        return True
    
    # 新增：绝对匹配输入- → 切换到上一个方案（循环）
    if input_content.strip() == "-":
        switch_to_prev_scheme()
        return True
    
    # 修改：输入\回车切换最后一个方案（原*）
    if input_content.strip() == "\\":
        switch_to_last_scheme()
        return True
    
    # 修改：输入*回车切换到默认编号方案
    if input_content.strip() == "*":
        switch_to_default_scheme()
        return True
    
    # 修改：清屏指令改为.（原*）
    if input_content.strip() == ".":
        clear_screen()
        write_history("执行清屏操作")
        return True
    
    # 核心还原：输入?/？时无任何前置空行，直接显示使用指南
    if input_content.strip() in ['?', '？']:
        print_usage_guide()
        return True
    
    # 交换功能：输入!或！显示当前方案信息
    if input_content.strip() in ['!', '！']:
        current_num = get_current_scheme_num()
        current_info = f"{current_num} → {CURRENT_SCHEME_NAME}"
        print(f"🔖 当前双拼方案：{current_info}")
        print()  # 单行空行
        write_history(f"显示当前方案信息：{current_info}")
        return True
    
    # 交换功能：输入@显示可用方案列表
    if input_content.strip() == "@":
        print_scheme_only()
        return True
    
    # 新增：输入>清空历史记录
    if input_content.strip() == ">":
        clear_history_file()
        tip_msg = "🗑️ 历史记录已清空（若不存在“history.txt”则创建空文件）"
        print(tip_msg)
        print()  # 单行空行
        write_history(tip_msg)
        return True
    
    # 新增：输入%切换历史记录开关
    if input_content.strip() == "%":
        toggle_history_switch()
        return True
    
    # 新增：输入#打开config目录
    if input_content.strip() == "#":
        open_directory(ROOT_PATH)
        return True
    
    # 新增：输入$打开method目录
    if input_content.strip() == "$":
        open_directory(METHOD_DIR)
        return True
    
    # 新增：输入=唤起浏览器打开双拼练习页面
    if input_content.strip() == "=":
        html_path = os.path.join(ROOT_PATH, "Shuang_6.0", "index.html")
        # 转换为file://协议格式以便浏览器打开
        file_url = f"file:///{html_path.replace(os.sep, '/')}"
        try:
            webbrowser.open(file_url)
            tip_msg = f"🌐 已在浏览器中打开：{html_path}（来自 https://github.com/BlueSky-07/Shuang）"
            print(tip_msg)
            print()  # 单行空行
            write_history(tip_msg)
        except Exception as e:
            err_msg = f"❌ 打开浏览器失败：{e}"
            print(err_msg)
            write_history(err_msg)
        return True
    
    # 检查是否是方案切换指令（单个数字）
    if len(input_segments) == 1 and is_scheme_number(input_segments[0]):
        scheme_num = int(input_segments[0])
        switch_scheme(scheme_num)
        return True
    
    # 检查是否输入了数字0（绝对匹配）→ 查表
    if input_content.strip() == "0":
        # 输入0显示编码表（无前置空行）
        func_name = "查表"
        shengmu, yunmu, ling_shengmu, key_map, reverse_map = CURRENT_SCHEME_DATA
        result = show_key_table(key_map)
        table_msg = f"【{CURRENT_SCHEME_NAME}编码表】\n{result}"
        print(table_msg)
        write_history(table_msg)
        return True
    
    # 执行转换功能
    shengmu, yunmu, ling_shengmu, key_map, reverse_map = CURRENT_SCHEME_DATA
    for seg in input_segments:
        if is_chinese(seg):
            # 片段包含中文 → 正查双拼（添加颜色加粗）
            doupin_code = forward_convert(seg, shengmu, yunmu, ling_shengmu)
            quangpin_list = chinese_to_quangpin_list(seg)
            # 核心修复：将全拼中的v替换为ü，保证显示规范
            quangpin_list_corrected = [py.replace('v', 'ü') for py in quangpin_list]
            quangpin_str = "'".join(quangpin_list_corrected).lower()
            # 核心修改：替换双拼为当前方案名
            forward_msg = f"🔎 {COLOR_BLUE_BOLD}{seg}{COLOR_RESET} {COLOR_RED_BOLD}{quangpin_str}{COLOR_RESET}【全拼 → {CURRENT_SCHEME_NAME}】{COLOR_GREEN_BOLD}{doupin_code}{COLOR_RESET}"
            print(forward_msg)
            # 写入历史记录（标记为输出）
            write_history(forward_msg, is_output=True)
        elif is_english(seg):
            # 片段是纯英文编码 → 反查全拼（添加颜色加粗）
            split_code, quangpin_result = reverse_convert_single(seg, shengmu, yunmu, ling_shengmu, reverse_map)
            # 核心修改：替换双拼为当前方案名
            reverse_msg = f"🔍 {COLOR_GREEN_BOLD}{split_code}{COLOR_RESET}【{CURRENT_SCHEME_NAME} → 全拼】{COLOR_RED_BOLD}{quangpin_result}{COLOR_RESET}"
            print(reverse_msg)
            # 写入历史记录（标记为输出）
            write_history(reverse_msg, is_output=True)
        else:
            # 无效片段（非中文/非纯编码/非方案编号）
            invalid_msg = f"❌ 错误：内容“{seg}”不属于有效中文/编码/指令，请输入“?”或“？”回车查看指南"
            print(invalid_msg)
            write_history(invalid_msg)
    return True

# ===================== 7. 信号处理：Ctrl+C退出 =====================
def signal_handler(sig, frame):
    """捕获Ctrl+C信号，优雅退出"""
    exit_msg = "\n\n👋 程序已退出"
    print(exit_msg)
    write_history(exit_msg)
    sys.exit(0)

# ===================== 8. 主循环（核心修改：自动判断输入类型） =====================
def main_loop(file_path=None):
    """程序主循环：自动根据输入类型执行功能"""
    # 注册Ctrl+C信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    if file_path:
        # 拖放文件模式：读取文件内容并自动判断执行
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                input_content = f.read().strip()
            file_msg = f"\n📄 读取文件内容：\n{input_content}\n"
            print(file_msg)
            write_history(file_msg)
            auto_run(input_content)
        except Exception as e:
            err_msg = f"❌ 读取文件失败：{e}"
            print(err_msg)
            write_history(err_msg)
        return

    # 初始化配置
    global SCHEME_LIST, DEFAULT_SCHEME_NUM, HISTORY_ENABLE, CLRHIS_LINE_NUM
    SCHEME_LIST, DEFAULT_SCHEME_NUM, HISTORY_ENABLE, CLRHIS_LINE_NUM = load_config()

    # 加载默认方案
    switch_scheme(DEFAULT_SCHEME_NUM)

    # 程序启动提示
    start_msg = "🚀 双拼转换工具 v0.0.19（首次使用请输入“?”或“？”回车查看指南）"
    print(start_msg)
    write_history("程序启动")

    # 主循环
    while True:
        try:
            # 输入提示符修改为 [方案名] > 且保持加粗
            user_input = input(f"{COLOR_BOLD}[{CURRENT_SCHEME_NAME}] >{COLOR_RESET} ")
            # 执行自动处理逻辑
            auto_run(user_input)
        except Exception as e:
            err_msg = f"❌ 程序运行出错：{e}"
            print(err_msg)
            write_history(err_msg)

# 程序入口
if __name__ == "__main__":
    # 处理命令行参数（拖放文件）
    if len(sys.argv) > 1:
        main_loop(sys.argv[1])
    else:
        main_loop()