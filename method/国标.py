# 国标双拼 核心配置（所有方案相关内容均在此定义）
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
    "zh": "V", 
    "ch": "I", 
    "sh": "U",
    "r": "R", 
    "z": "Z", 
    "c": "C", 
    "s": "S",
    "y": "Y", 
    "w": "W"
}

# 2. 韵母表（长拼，需匹配拼音剩余部分）
YUNMU = {
    "iu": "Y", 
    "ei": "B", 
    "e": "E", 
    "uan": "W", 
    "ue": "X", 
    "un": "Z",
    "u": "U", 
    "i": "I",
    "o": "O", 
    "uo": "O", 
    "ie": "T", 
    "a": "A", 
    "ong": "S", 
    "iong": "S", 
    "ai": "K", 
    "en": "R",
    "eng": "H",
    "ang": "G",
    "an": "F",
    "uai": "Y",
    "ing": "J",
    "iang": "N",
    "uang": "N",
    "ou": "P",
    "ia": "Q",
    "ua": "Q",
    "ao": "C",
    "ui": "V",
    "v": "V",
    "in": "L",
    "iao": "M"
}

# 3. 零声母韵母（无生母时的独立韵母映射）
LING_SHENGMU = {
    "a": "AA", 
    "o": "AO", 
    "e": "AE", 
    "ai": "AK", 
    "ei": "AB",
    "ao": "AC", 
    "ou": "AP", 
    "an": "AF", 
    "en": "AR",
    "ang": "AG", 
    "eng": "AH", 
    "er": "AL"
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