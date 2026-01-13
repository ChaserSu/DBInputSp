import sys
import importlib
import os
from config import current_scheme
from pypinyin import lazy_pinyin, Style

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

# 拼接 method 目录路径，并加入系统模块搜索路径
ROOT_PATH = get_root_path()
METHOD_DIR = os.path.join(ROOT_PATH, "method")
sys.path.append(METHOD_DIR)

# ===================== 1. 动态加载双拼方案（修改导入逻辑） =====================
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
        print(f"错误：未找到 {scheme_name} 方案，请检查 {METHOD_DIR}/{scheme_name}.py")
        print(f"当前程序根路径：{ROOT_PATH}")  # 调试用，可删除
        sys.exit(1)
    except AttributeError as e:
        print(f"错误：{scheme_name}.py 缺少配置项 {e}")
        sys.exit(1)

# ===================== 2. 拼音处理工具（基于pypinyin，添加零声母支持） =====================
def chinese_to_pinyin_list(chinese_str):
    """将中文转换为不带声调的拼音列表"""
    return lazy_pinyin(chinese_str, style=Style.NORMAL)

def split_pinyin_to_shengmu_yunmu(pinyin, shengmu_map, yunmu_map, ling_shengmu_map):
    """
    根据双拼方案拆分拼音为 声母+韵母，优先处理零声母
    :param pinyin: 单个拼音（如 xiao, ao）
    :param shengmu_map: 声母表
    :param yunmu_map: 韵母表
    :param ling_shengmu_map: 零声母表
    :return: (声母键位, 韵母键位)
    """
    shengmu = ""
    yunmu_part = pinyin
    # 步骤1：匹配最长声母（如 zh 优先于 z）
    for sm in sorted(shengmu_map.keys(), key=lambda x: len(x), reverse=True):
        if pinyin.startswith(sm):
            shengmu = sm
            yunmu_part = pinyin[len(sm):]
            break

    # 步骤2：优先处理零声母（无声母时，优先用零声母表）
    if not shengmu:
        return "", ling_shengmu_map.get(pinyin, yunmu_map.get(pinyin, pinyin.upper()))
    else:
        # 有生母，取声母键位 + 韵母键位
        shengmu_key = shengmu_map[shengmu]
        yunmu_key = yunmu_map.get(yunmu_part, yunmu_part.upper())
        return shengmu_key, yunmu_key

# ===================== 3. 三大核心功能（正查添加零声母参数） =====================
def forward_convert(chinese_str, shengmu_map, yunmu_map, ling_shengmu_map):
    """正查：中文 → 双拼编码（核心修改：传入零声母表，结果转小写）"""
    if not chinese_str.strip():
        return "输入不能为空"
    pinyin_list = chinese_to_pinyin_list(chinese_str)
    code_list = []
    for pinyin in pinyin_list:
        # 传入零声母表，实现零声母优先匹配
        sm_key, ym_key = split_pinyin_to_shengmu_yunmu(pinyin, shengmu_map, yunmu_map, ling_shengmu_map)
        code = f"{sm_key}{ym_key}".strip()
        code_list.append(code)
    # 结果转小写
    return "'".join(code_list).lower()

def reverse_convert(code_str, shengmu_map, yunmu_map, ling_shengmu_map, reverse_map):
    """
    反查：双拼编码 → 全拼（支持零声母编码）
    :param code_str: 双拼编码字符串
    :param shengmu_map: 声母表
    :param yunmu_map: 韵母表
    :param ling_shengmu_map: 零声母表
    :param reverse_map: 反向映射表
    :return: 完整拼音字符串
    """
    if not code_str.strip():
        return "输入不能为空"
    
    # 构建各类映射表
    sm_key_to_py = {v.upper(): k for k, v in shengmu_map.items()}  # 声母键→拼音
    ym_key_to_py = {v.upper(): k for k, v in yunmu_map.items()}    # 韵母键→拼音
    # 零声母键→拼音（反转零声母表）
    ling_key_to_py = {v.upper(): k for k, v in ling_shengmu_map.items()}

    code_list = code_str.split("'")
    pinyin_list = []

    for code in code_list:
        code_upper = code.upper().strip()
        full_py = ""

        # 优先匹配零声母编码
        if code_upper in ling_key_to_py:
            full_py = ling_key_to_py[code_upper]
        # 匹配普通2位双拼编码（声母+韵母）
        elif len(code_upper) == 2:
            sm_key = code_upper[0]
            ym_key = code_upper[1]
            sm_py = sm_key_to_py.get(sm_key, "")
            ym_py = ym_key_to_py.get(ym_key, "")
            full_py = sm_py + ym_py
        # 兜底：匹配不到返回原编码
        else:
            full_py = code

        pinyin_list.append(full_py if full_py else code)
    
    return "'".join(pinyin_list)

def show_key_table(key_map):
    """查表：生成键位对照表"""
    key_group = {}
    for pinyin, key in key_map.items():
        if key not in key_group:
            key_group[key] = []
        key_group[key].append(pinyin)
    table_lines = []
    for key in sorted(key_group.keys()):
        pinyins = "; ".join(key_group[key])
        table_lines.append(f"{key} = {pinyins}")
    return "\n".join(table_lines)

# ===================== 4. 结果保存功能（修改保存路径为根路径） =====================
def save_result(result, file_path=None, func_name=""):
    """
    保存处理结果到文件：
    - exe运行：保存到exe所在目录
    - 源码运行：保存到源码所在目录
    :param result: 要保存的内容
    :param func_name: 功能名称（正查/反查/查表）
    """
    if file_path:
        # 拖放文件模式：保存到原文件目录
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path).split(".")[0]
        save_name = f"{file_name}_{func_name}.txt"
        save_path = os.path.join(dir_name, save_name)
    else:
        # 手动输入模式：保存到程序根路径
        save_path = os.path.join(ROOT_PATH, f"{func_name}_结果.txt")
    
    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ 结果已保存到：{save_path}")
    except Exception as e:
        print(f"❌ 保存失败：{e}")

# ===================== 5. 功能执行逻辑（添加零声母参数传参） =====================
def run_function(choice, shengmu, yunmu, ling_shengmu, key_map, reverse_map, file_path=None):
    """
    执行选择的功能，处理输入和保存
    :param choice: 功能选择（1/2/3）
    :param ling_shengmu: 零声母表
    :param file_path: 拖放的文件路径（None表示手动输入）
    :return: 是否继续运行
    """
    func_name = ""
    result = ""
    input_content = ""

    # 1. 读取输入内容（文件拖放 / 手动输入）
    if file_path:
        # 拖放文件模式：读取文件内容
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                input_content = f.read().strip()
            print(f"\n📄 读取文件内容：\n{input_content}\n")
        except Exception as e:
            print(f"❌ 读取文件失败：{e}")
            return True

    # 2. 执行对应功能
    if choice == "1":
        func_name = "正查"
        # 获取输入内容
        if not input_content:
            input_content = input("请输入要转换的中文：").strip()
        # 执行转换：传入零声母表
        result = forward_convert(input_content, shengmu, yunmu, ling_shengmu)
        print(f"\n【{func_name}结果】：\n{result}")

    elif choice == "2":
        func_name = "反查"
        if not input_content:
            input_content = input("请输入要转换的双拼编码（用'分隔）：").strip()
        # 传入 ling_shengmu 参数
        result = reverse_convert(input_content, shengmu, yunmu, ling_shengmu, reverse_map)
        print(f"\n【{func_name}结果】：\n{result}")

    elif choice == "3":
        func_name = "查表"
        result = show_key_table(key_map)
        print(f"\n【{func_name}结果】：\n{result}")

    # 3. 选择是否保存结果
    if result and result != "输入不能为空":
        if file_path:
            # 拖放文件：默认保存
            save_choice = input(f"\n是否保存{func_name}结果？（默认是，输入n取消）：").strip().lower()
            if save_choice != "n":
                save_result(result, file_path, func_name)
        else:
            # 手动输入：默认不保存
            save_choice = input(f"\n是否保存{func_name}结果？（默认否，输入y保存）：").strip().lower()
            if save_choice == "y":
                save_result(result, func_name=func_name)
    
    # 4. 返回功能首页
    return True

# ===================== 6. 主循环（添加零声母参数传参） =====================
def main_loop(shengmu, yunmu, ling_shengmu, key_map, reverse_map, file_path=None):
    """程序主循环：持续显示功能菜单"""
    while True:
        print("\n===== 双拼转换工具 ======")
        print("1. 正查（中文 → 双拼编码）")
        print("2. 反查（双拼编码 → 全拼）")
        print("3. 查表（查看键位对照表）")
        print("0. 退出程序")
        choice = input("\n请选择功能（0-3）：").strip()

        if choice == "0":
            print("👋 程序已退出")
            break
        elif choice in ["1", "2", "3"]:
            # 调用run_function时传入零声母表
            run_function(choice, shengmu, yunmu, ling_shengmu, key_map, reverse_map, file_path)
        else:
            print("❌ 无效选择，请输入 0-3 之间的数字")

# ===================== 7. 程序入口 =====================
if __name__ == "__main__":
    # 加载双拼方案
    shengmu, yunmu, ling_shengmu, key_map, reverse_map = load_scheme(current_scheme)
    print(f"✅ 成功加载双拼方案：{current_scheme}")
    print(f"✅ 当前配置文件目录：{METHOD_DIR}") # 调试用，可删除

    # 判断执行方式：文件拖放 or 手动输入
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            print(f"📂 检测到拖放文件：{file_path}")
        else:
            print(f"❌ 无效文件路径：{file_path}")
            sys.exit(1)

    # 启动主循环：传入零声母表
    main_loop(shengmu, yunmu, ling_shengmu, key_map, reverse_map, file_path)