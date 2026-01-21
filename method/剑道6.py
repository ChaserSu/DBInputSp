# 键道双拼6 核心配置（所有方案相关内容均在此定义）
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
    "iu": "Q", 
    "ei": "W", 
    "e": "E", 
    "uan": "T", 
    "üan": "T", 
    "van": "T", 
    "ue": "H", 
    "üe": "H",
    "ve": "H",
    "un": "W",
    "ün": "W",
    "vn": "W",
    "u": "J", 
    "i": "K",
    "o": "L", 
    "uo": "L", 
    "ie": "D", 
    "a": "S", 
    "ong": "Y", 
    "iong": "Y", 
    "ai": "H", 
    "en": "N",
    "eng": "R",
    "ang": "P",
    "an": "F",
    "uai": "G",
    "ing": "G",
    "iang": "X",
    "uang": "X",
    "ou": "D",
    "ia": "S",
    "ua": "Q",
    "ao": "Z",
    "ui": "B",
    "ü": "L",
    "v": "L",
    "in": "B",
    "iao": "C"
}

# 3. 零声母韵母（无生母时的独立韵母映射）
LING_SHENGMU = {
    "a": "XS", 
    "o": "XL", 
    "e": "XE", 
    "ai": "XH", 
    "ei": "XW",
    "ao": "XZ", 
    "ou": "XD", 
    "an": "XF", 
    "en": "XN",
    "ang": "XP", 
    "eng": "XR", 
    "er": "XJ"
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