# 键道双拼3 核心配置（所有方案相关内容均在此定义）
# 1. 声母表（短拼，优先级高于韵母）
SHENGMU = {
    "b": "B", 
    "p": "P", 
    "m": "M", 
    "f": "F",
    "d": "D", 
    "t": "T", 
    "n": "N", 
    "l": "L",
    "g": "G", 
    "k": "K", 
    "h": "H",
    "j": "J", 
    "q": "Q", 
    "x": "X",
    "zh": "F", 
    "ch": "J", 
    "sh": "E",
    "r": "R", 
    "z": "Z", 
    "c": "C", 
    "s": "S",
    "y": "Y", 
    "w": "W"
}

# 2. 韵母表（长拼，需匹配拼音剩余部分）
YUNMU = {
    "iu": "S", 
    "ei": "W", 
    "e": "J", 
    "uan": "R", 
    "üan": "R", 
    "van": "R", 
    "ue": "F", 
    "üe": "F",
    "ve": "F",
    "un": "W",
    "ün": "W",
    "vn": "W",
    "u": "M", 
    "i": "K",
    "o": "L", 
    "uo": "L", 
    "ie": "C", 
    "a": "P", 
    "ong": "Y", 
    "iong": "Y", 
    "ai": "F", 
    "en": "N",
    "eng": "T",
    "ang": "H",
    "an": "E",
    "uai": "D",
    "ing": "G",
    "iang": "X",
    "uang": "X",
    "ou": "S",
    "ia": "P",
    "ua": "C",
    "ao": "Z",
    "ui": "B",
    "ü": "L",
    "v": "L",
    "in": "B",
    "iao": "Q"
}

# 3. 零声母韵母（无生母时的独立韵母映射）
LING_SHENGMU = {
    "a": "XP", 
    "o": "XL", 
    "e": "XJ", 
    "ai": "XF", 
    "ei": "XW",
    "ao": "XZ", 
    "ou": "XS", 
    "an": "XE", 
    "en": "XN",
    "ang": "XH", 
    "eng": "XT", 
    "er": "XM"
}

# 4. 完整键位映射表（用于查表功能，合并声母+韵母+零声母）
KEY_MAP = {}
KEY_MAP.update(SHENGMU)
KEY_MAP.update(YUNMU)
KEY_MAP.update(LING_SHENGMU)

# 5. 反向映射表（用于反查：键位→拼音，一个键位可能对应多个拼音）
REVERSE_MAP = {}
for pinyin, key in KEY_MAP.items():
    if key not in REVERSE_MAP:
        REVERSE_MAP[key] = []
    REVERSE_MAP[key].append(pinyin)