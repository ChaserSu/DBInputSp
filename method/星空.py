# 星空双拼 核心配置（所有方案相关内容均在此定义）
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
    "zh": "Z", 
    "ch": "C", 
    "sh": "S",
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
    "ue": "H", 
    "un": "Y",
    "u": "U", 
    "i": "I",
    "o": "O", 
    "uo": "O", 
    "ie": "X", 
    "a": "A", 
    "ong": "L", 
    "iong": "L", 
    "ai": "H", 
    "en": "N",
    "eng": "M",
    "ang": "P",
    "an": "J",
    "uai": "G",
    "ing": "G",
    "iang": "C",
    "uang": "C",
    "ou": "R",
    "ia": "S",
    "ua": "S",
    "ao": "K",
    "ui": "V",
    "v": "V",
    "in": "B",
    "iao": "D"
}

# 3. 零声母韵母（无生母时的独立韵母映射）
LING_SHENGMU = {
    "a": "VA", 
    "o": "VO", 
    "e": "VE", 
    "ai": "VH", 
    "ei": "VW",
    "ao": "VK", 
    "ou": "VR", 
    "an": "VJ", 
    "en": "VN",
    "ang": "VP", 
    "eng": "VM", 
    "er": "VU"
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