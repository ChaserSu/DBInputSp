#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合拼音处理功能，生成包含ü和v两个版本过滤表的nosensevoice.py
"""

# 声母表（来自小鹤双拼）
SHENGMU = ["b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j", "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w"]

# 韵母表（来自小鹤双拼）
YUNMU = ["iu", "ei", "e", "uan", "üan", "van", "ue", "üe", "ve", "un", "ün", "vn", "u", "i", "o", "uo", "ie", "a", "ong", "iong", "ai", "en", "eng", "ang", "an", "uai", "ing", "iang", "uang", "ou", "ia", "ua", "ao", "ui", "ü", "v"]

# 零声母韵母（来自小鹤双拼）
LING_SHENGMU = ["a", "o", "e", "ai", "ei", "ao", "ou", "an", "en", "ang", "eng", "er"]

# 有效拼音组合（基于普通话拼音规则）
# 参考：https://zh.wikipedia.org/wiki/%E6%99%AE%E9%80%9A%E8%AF%9D%E6%8B%BC%E9%9F%B3%E8%A1%A8
VALID_PINYIN = {
    # 声母b
    "ba", "bo", "bai", "bei", "bao", "ban", "ben", "bang", "beng", "bi", "bie", "biao", "bin", "bing",
    "bu",
    # 声母p
    "pa", "po", "pai", "pei", "pao", "pan", "pen", "pang", "peng", "pi", "pie", "piao", "pin", "ping",
    "pu",
    # 声母m
    "ma", "mo", "mai", "mei", "mao", "man", "men", "mang", "meng", "mi", "mie", "miao", "miu", "min", "ming",
    "mu",
    # 声母f
    "fa", "fo", "fei", "fou", "fan", "fen", "fang", "feng", "fu",
    # 声母d
    "da", "de", "dai", "dei", "dao", "dou", "dan", "den", "dang", "deng", "di", "die", "diao", "diu", "ding",
    "dong", "du", "duo", "dui", "dun", "duan", "dui", "dun", "duan", "duang",
    # 声母t
    "ta", "te", "tai", "tui", "tao", "tou", "tan", "tang", "teng", "ti", "tie", "tiao", "ting", "tong",
    "tu", "tuo", "tui", "tun", "tuan", "tuang",
    # 声母n
    "na", "ne", "nai", "nei", "nao", "nou", "nan", "nen", "nang", "neng", "ni", "nie", "niao", "niu", "nin", "ning",
    "nong", "nu", "nuo", "nü", "nüe", "nv", "nve",
    # 声母l
    "la", "le", "lai", "lei", "lao", "lou", "lan", "lang", "leng", "li", "lie", "liao", "liu", "lin", "ling",
    "long", "lu", "luo", "lv", "lve", "lü", "lüe", "luan", "l üan", "lüan", "lvan",
    # 声母g
    "ga", "ge", "gai", "gei", "gao", "gou", "gan", "gen", "gang", "geng", "gong", "gu", "guo", "gui", "gun", "guan", "guang",
    # 声母k
    "ka", "ke", "kai", "kei", "kao", "kou", "kan", "ken", "kang", "keng", "kong", "ku", "kuo", "kui", "kun", "kuan", "kuang",
    # 声母h
    "ha", "he", "hai", "hei", "hao", "hou", "han", "hen", "hang", "heng", "hong", "hu", "huo", "hui", "hun", "huan", "huang",
    # 声母j
    "ji", "jia", "jie", "jiao", "jiu", "jian", "jin", "jiang", "jing", "jiong", "ju", "juan", "jue", "jun", "jv", "jvan", "jve",
    # 声母q
    "qi", "qia", "qie", "qiao", "qiu", "qian", "qin", "qiang", "qing", "qiong", "qu", "quan", "que", "qun", "qv", "qvan", "qve",
    # 声母x
    "xi", "xia", "xie", "xiao", "xiu", "xian", "xin", "xiang", "xing", "xiong", "xu", "xuan", "xue", "xun", "xv", "xvan", "xve",
    # 声母zh
    "zha", "zhe", "zhai", "zhei", "zhao", "zhou", "zhan", "zhen", "zhang", "zheng", "zhi", "zhong", "zhu", "zhua", "zhuo", "zhuai", "zhui", "zhun", "zhuan", "zhuang",
    # 声母ch
    "cha", "che", "chai", "chei", "chao", "chou", "chan", "chen", "chang", "cheng", "chi", "chong", "chu", "chua", "chuo", "chuai", "chui", "chun", "chuan", "chuang",
    # 声母sh
    "sha", "she", "shai", "shei", "shao", "shou", "shan", "shen", "shang", "sheng", "shi", "shong", "shu", "shua", "shuo", "shuai", "shui", "shun", "shuan", "shuang",
    # 声母r
    "ra", "re", "rui", "rao", "rou", "ran", "ren", "rang", "reng", "ri", "rong", "ru", "ruo", "rui", "run", "ruan", "ruang",
    # 声母z
    "za", "ze", "zai", "zei", "zao", "zou", "zan", "zen", "zang", "zeng", "zi", "zong", "zu", "zuo", "zui", "zun", "zuan", "zuang",
    # 声母c
    "ca", "ce", "cai", "cao", "cou", "can", "cen", "cang", "ceng", "ci", "cong", "cu", "cuo", "cui", "cun", "cuan", "cuang",
    # 声母s
    "sa", "se", "sai", "sao", "sou", "san", "sen", "sang", "seng", "si", "song", "su", "suo", "sui", "sun", "suan", "suang",
    # 声母y
    "ya", "yo", "ye", "yai", "yao", "you", "yan", "yin", "yang", "ying", "yong", "yu", "yue", "yuan", "yun", "yv", "yve", "yvan",
    # 声母w
    "wa", "wo", "wai", "wei", "wan", "wen", "wang", "weng", "wu",
    # 零声母
    "a", "o", "e", "ai", "ei", "ao", "ou", "an", "en", "ang", "eng", "er", "yi", "ya", "ye", "yao", "you", "yan", "yin", "yang", "ying", "yong", "wu", "wa", "wo", "wai", "wei", "wan", "wen", "wang", "weng", "yu", "yue", "yuan", "yun", "yv", "yve", "yvan"
}


def normalize_pinyin(pinyin):
    """将拼音标准化，将ü转换为v，处理空格等"""
    pinyin = pinyin.strip().lower().replace("ü", "v").replace("  ", " ")
    # 处理l üan -> lvan
    if " " in pinyin:
        pinyin = pinyin.replace(" ", "")
    return pinyin


def generate_all_combinations():
    """生成所有可能的声母+韵母组合，以及零声母+韵母组合"""
    all_combinations = set()
    
    # 1. 声母 + 韵母组合
    for sheng in SHENGMU:
        for yun in YUNMU:
            # 转换为标准化拼音（v代替ü）
            pinyin = sheng + yun
            pinyin = normalize_pinyin(pinyin)
            all_combinations.add(pinyin)
    
    # 2. 零声母 + 韵母组合
    for yun in LING_SHENGMU:
        pinyin = normalize_pinyin(yun)
        all_combinations.add(pinyin)
    
    return all_combinations


def filter_nonsense_pinyin():
    """过滤出无效的拼音组合"""
    all_combinations = generate_all_combinations()
    valid_pinyin_normalized = {normalize_pinyin(py) for py in VALID_PINYIN}
    
    # 找出无效的组合
    nonsense_pinyin = all_combinations - valid_pinyin_normalized
    
    # 按声母分组排序
    grouped = {}
    for py in sorted(nonsense_pinyin):
        # 提取声母部分
        shengmu = ""
        if len(py) >= 2 and py[:2] in SHENGMU:
            shengmu = py[:2]
        elif len(py) >= 1 and py[0] in SHENGMU:
            shengmu = py[0]
        else:
            shengmu = "零声母"
        
        if shengmu not in grouped:
            grouped[shengmu] = []
        grouped[shengmu].append(py)
    
    return grouped


def generate_nonsense_tables():
    """生成包含v版本和ü版本的过滤表"""
    print("=== 开始生成无效拼音组合表 ===")
    
    # 获取无效拼音组合
    grouped_nonsense = filter_nonsense_pinyin()
    
    # 生成v版本和ü版本的过滤表
    v_table = []
    ü_table = []
    
    for shengmu, pinyin_list in grouped_nonsense.items():
        for py in pinyin_list:
            # v版本（已经是v格式）
            v_table.append(py)
            # ü版本（将v转换为ü）
            ü_py = py.replace("v", "ü")
            ü_table.append(ü_py)
    
    # 去重并排序
    v_table = sorted(list(set(v_table)))
    ü_table = sorted(list(set(ü_table)))
    
    print(f"生成完成！\n- v版本过滤项数量: {len(v_table)}\n- ü版本过滤项数量: {len(ü_table)}")
    
    return v_table, ü_table


def write_nonsensevoice_file(v_table, ü_table):
    """写入nosensevoice.py文件"""
    print("\n=== 写入nosensevoice.py文件 ===")
    
    # 生成文件内容
    content = [
        "# 过滤表：需要过滤掉的不存在的全拼组合（用于双拼转全拼时的结果过滤）",
        "# 生成时间: " + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
        "# 1. v版本过滤表（使用v代替ü）",
        "filter_table_v = ["
    ]
    
    # 添加v版本过滤表，按声母分组
    grouped_v = {}
    for item in v_table:
        # 提取声母
        shengmu = ""
        if len(item) >= 2 and (item[:2] == "zh" or item[:2] == "ch" or item[:2] == "sh"):
            shengmu = item[:2]
        elif len(item) >= 1:
            shengmu = item[0]
        else:
            shengmu = "零声母"
        
        if shengmu not in grouped_v:
            grouped_v[shengmu] = []
        grouped_v[shengmu].append(item)
    
    for shengmu in sorted(grouped_v.keys()):
        items = grouped_v[shengmu]
        content.append(f"    # 声母{shengmu} + 无对应韵母")
        for item in items:
            content.append(f"    \"{item}\",")
    
    content.append("]")
    content.append("")
    content.append("# 2. ü版本过滤表（使用ü）")
    content.append("filter_table_ü = [")
    
    # 添加ü版本过滤表，按声母分组
    grouped_ü = {}
    for item in ü_table:
        # 提取声母
        shengmu = ""
        if len(item) >= 2 and (item[:2] == "zh" or item[:2] == "ch" or item[:2] == "sh"):
            shengmu = item[:2]
        elif len(item) >= 1:
            shengmu = item[0]
        else:
            shengmu = "零声母"
        
        if shengmu not in grouped_ü:
            grouped_ü[shengmu] = []
        grouped_ü[shengmu].append(item)
    
    for shengmu in sorted(grouped_ü.keys()):
        items = grouped_ü[shengmu]
        content.append(f"    # 声母{shengmu} + 无对应韵母")
        for item in items:
            content.append(f"    \"{item}\",")
    
    content.append("]")
    
    # 写入文件
    with open("nosensevoice.py", "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    
    print("✅ 文件写入完成：nosensevoice.py")


def main():
    """主函数"""
    print("🚀 启动无效拼音组合表生成工具")
    print("=" * 50)
    
    # 生成过滤表
    v_table, ü_table = generate_nonsense_tables()
    
    # 写入文件
    write_nonsensevoice_file(v_table, ü_table)
    
    print("=" * 50)
    print("🎉 所有操作完成！")
    print(f"📋 生成的文件：nosensevoice.py")
    print(f"📊 包含两个表：")
    print(f"   - filter_table_v: v版本过滤表 ({len(v_table)}项)")
    print(f"   - filter_table_ü: ü版本过滤表 ({len(ü_table)}项)")


if __name__ == "__main__":
    main()
