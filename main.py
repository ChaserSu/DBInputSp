import sys
import importlib
import os
import signal
from pypinyin import lazy_pinyin, Style

# ===================== 新增：ANSI颜色/加粗控制码 =====================
# 样式说明：\033[1m 加粗 | \033[31m 红色 | \033[32m 绿色 | \033[34m 蓝色 | \033[0m 重置样式
COLOR_BLUE_BOLD = "\033[1;34m"   # 蓝色加粗（用户输入的中文）
COLOR_RED_BOLD = "\033[1;31m"    # 红色加粗（全拼）
COLOR_GREEN_BOLD = "\033[1;32m"  # 绿色加粗（双拼编码）
COLOR_BOLD = "\033[1m"           # 仅加粗（无颜色）
COLOR_RESET = "\033[0m"          # 重置样式

# ===================== 新增：全局变量 =====================
# 当前激活的双拼方案信息
CURRENT_SCHEME_NAME = ""
CURRENT_SCHEME_DATA = None  # 存储(声母表, 韵母表, 零声母表, 键位表, 反向映射表)
SCHEME_LIST = {}  # 存储从config.py读取的方案列表 {编号: 方案名}

# ===================== 新增：清屏函数 =====================
def clear_screen():
    """跨平台清屏函数（兼容Windows/Linux/Mac）"""
    # Windows使用cls，其他系统使用clear
    os.system('cls' if os.name == 'nt' else 'clear')

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

# ===================== 新增：读取config.py中的双拼方案列表 =====================
def load_scheme_list_from_config():
    """
    从config.py读取双拼方案列表（格式：编号 方案名）
    返回：方案字典 {编号: 方案名}，默认方案名
    """
    scheme_dict = {}
    default_scheme = ""
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
            
            # 按空格分割（支持多个空格）
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
            
            # 第一个有效方案作为默认方案
            if not default_scheme:
                default_scheme = scheme_name
        
        if not scheme_dict:
            print(f"❌ 错误：config.py中未找到有效双拼方案配置")
            sys.exit(1)
        
        print(f"✅ 成功读取双拼方案列表：{scheme_dict}")
        print(f"✅ 默认加载方案：{default_scheme}")
        return scheme_dict, default_scheme
    
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
        print(f"❌ 无效编号！可选方案：{SCHEME_LIST}")
        return False
    
    scheme_name = SCHEME_LIST[scheme_num]
    # 加载方案数据
    scheme_data = load_scheme(scheme_name)
    if scheme_data is None:
        return False
    
    # 更新全局变量（仅移除了成功提示的打印语句）
    CURRENT_SCHEME_NAME = scheme_name
    CURRENT_SCHEME_DATA = scheme_data
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
        print(f"🔍 自动切分编码：{split_code}")
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
    """判断输入文本是否为英文（仅字母和单引号）"""
    text = text.strip()
    if not text:
        return False
    for char in text:
        if not (char.isalpha() or char == "'"):
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
    """根据输入内容自动执行对应功能（支持：切换方案、清屏、正查、反查、查表）"""
    global CURRENT_SCHEME_DATA
    
    # 拆分输入为多个片段（按任意数量空格分割）
    input_segments = [seg.strip() for seg in input_content.split() if seg.strip()]
    
    # 空输入（空格/回车）：仅返回True，不执行任何操作（无空行）
    if not input_segments:
        return True
    
    # 新增：绝对匹配输入* → 清屏
    if input_content.strip() == "*":
        clear_screen()
        return True
    
    # 检查是否是方案切换指令（单个数字）
    if len(input_segments) == 1 and is_scheme_number(input_segments[0]):
        scheme_num = int(input_segments[0])
        switch_scheme(scheme_num)
        return True
    
    # 检查是否输入了数字0（绝对匹配）→ 查表
    if input_content.strip() == "0":
        # 输入0显示编码表（先换行，保持功能执行时的空行）
        print()
        func_name = "查表"
        shengmu, yunmu, ling_shengmu, key_map, reverse_map = CURRENT_SCHEME_DATA
        result = show_key_table(key_map)
        print(f"【{func_name}结果】（{CURRENT_SCHEME_NAME}）：\n{result}")
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
            # 格式化输出：中文(蓝粗) + 全拼(红粗) + 双拼(绿粗)
            print(f"🔎 {COLOR_BLUE_BOLD}{seg}{COLOR_RESET} {COLOR_RED_BOLD}{quangpin_str}{COLOR_RESET}【全拼 → 双拼】{COLOR_GREEN_BOLD}{doupin_code}{COLOR_RESET}")
        elif is_english(seg):
            # 片段是纯英文编码 → 反查全拼（添加颜色加粗）
            split_code, quangpin_result = reverse_convert_single(seg, shengmu, yunmu, ling_shengmu, reverse_map)
            # 格式化输出：双拼(绿粗) + 全拼(红粗)
            print(f"🔍 {COLOR_GREEN_BOLD}{split_code}{COLOR_RESET}【双拼 → 全拼】{COLOR_RED_BOLD}{quangpin_result}{COLOR_RESET}")
        else:
            # 无效片段（非中文/非纯编码/非方案编号）
            print(f"🔎 {seg}【提示】：非有效中文/双拼编码/方案编号，跳过处理")
    return True

# ===================== 7. 信号处理：Ctrl+C退出 =====================
def signal_handler(sig, frame):
    """捕获Ctrl+C信号，优雅退出"""
    print("\n\n👋 程序已退出")
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
            print(f"\n📄 读取文件内容：\n{input_content}\n")
            auto_run(input_content)
        except Exception as e:
            print(f"❌ 读取文件失败：{e}")
        return

    # 打印欢迎信息
    print(f"{COLOR_BOLD}===== 双拼转换工具 v0.0.15（支持清屏+多方案切换）====={COLOR_RESET}")
    print(f"{COLOR_BOLD}【参与开发】{COLOR_RESET}苏鱼鱼、小川、豆包（doubao.com）")
    print(f"{COLOR_BOLD}【GitHub】{COLOR_RESET}https://github.com/ChaserSu/DBInputSp")
    print(f"{COLOR_BOLD}【可用方案】{COLOR_RESET}")
    for num, name in sorted(SCHEME_LIST.items()):
        is_current = " ✅" if name == CURRENT_SCHEME_NAME else ""
        print(f"  {num} → {name}{is_current}")
    print(f"{COLOR_BOLD}【使用指南】{COLOR_RESET}")
    print(f"🔢 输入数字 → 切换对应双拼方案")
    print(f"🔎 {COLOR_BLUE_BOLD}输入中文{COLOR_RESET} → {COLOR_GREEN_BOLD}正查双拼{COLOR_RESET}")
    print(f"🔍 {COLOR_GREEN_BOLD}输入编码{COLOR_RESET} → {COLOR_RED_BOLD}反查全拼{COLOR_RESET}")
    print("🔀 混合输入 → 分别处理")
    print("📋 输入“0”回车 → 查当前方案编码表")
    print("🧹 输入“*”回车 → 清空屏幕")  # 新增：清屏功能说明
    print("🚶 Ctrl+C → 退出程序")
    
    # 初始化输入提示前缀（无前置换行）
    prompt_prefix = ""
    while True:
        try:
            # 动态显示当前激活的方案名
            prompt = f"{prompt_prefix}{COLOR_BOLD}请输入内容（{CURRENT_SCHEME_NAME}）：{COLOR_RESET}"
            input_content = input(prompt).strip()
            # 执行功能
            auto_run(input_content)
            
            # 重置前缀：空输入时无前置换行，非空输入后下次提示加换行
            prompt_prefix = "\n" if input_content.strip() else ""
        except KeyboardInterrupt:
            # 兼容Ctrl+C捕获
            signal_handler(signal.SIGINT, None)

# ===================== 9. 程序入口 =====================
if __name__ == "__main__":
    # 第一步：读取config.py中的方案列表
    SCHEME_LIST, default_scheme_name = load_scheme_list_from_config()
    
    # 第二步：加载默认方案（第一行有效方案）
    print(f"{COLOR_BOLD}✅ 正在加载默认方案：{COLOR_RESET}{default_scheme_name}")
    default_scheme_data = load_scheme(default_scheme_name)
    if default_scheme_data is None:
        print(f"❌ 加载默认方案 {default_scheme_name} 失败")
        sys.exit(1)
    
    # 初始化全局变量
    CURRENT_SCHEME_NAME = default_scheme_name
    CURRENT_SCHEME_DATA = default_scheme_data
    
    # 调试信息（可删除）
    print(f"{COLOR_BOLD}✅ 当前config目录：{COLOR_RESET}{ROOT_PATH}")
    print(f"{COLOR_BOLD}✅ 当前method目录：{COLOR_RESET}{METHOD_DIR}")

    # 判断执行方式：文件拖放 or 手动输入
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            print(f"📂 检测到拖放文件：{file_path}")
        else:
            print(f"❌ 无效文件路径：{file_path}")
            sys.exit(1)

    # 启动主循环
    main_loop(file_path)
