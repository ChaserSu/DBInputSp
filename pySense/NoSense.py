# 过滤表：需要过滤掉的不存在的全拼组合（用于双拼转全拼时的结果过滤）
# 格式：每行一个拼音组合，支持u和ü（或v代替ü）的不同写法
filter_table = [
    # 声母b + 无对应韵母
    "bü", "bua", "buo", "biai", "biu", "buan", "büan", "biong",
    "beng", "bing", "bvang", "bve", "bvn", "büe", "bün",
    
    # 声母p + 无对应韵母
    "pü", "pua", "puo", "piai", "piu", "puan", "püan", "piong",
    "pve", "pvn", "püe", "pün",
    
    # 声母m + 无对应韵母
    "mü", "mua", "muo", "miai", "miu", "muan", "müan", "miong",
    "mve", "mvn", "müe", "mün", "mvang",
    
    # 声母f + 无对应韵母
    "fü", "fua", "fuo", "fiai", "fiu", "fuan", "füan", "fiong",
    "fve", "fvn", "füe", "fün", "fvang", "fiang", "fiao", "fie",
    "fing", "fong", "fou", "fua", "fui", "fuo", "fvan", "fve",
    "fx", "fy", "fz",
    
    # 声母d + 无对应韵母
    "dü", "diai", "diu", "düan", "diong", "dve", "dvn", "düe",
    "dün", "dv", "dü", "dvang", "diang",
    
    # 声母t + 无对应韵母
    "tü", "tiai", "tiu", "tüan", "tiong", "tve", "tvn", "tüe",
    "tün", "tv", "tü", "tvang", "tviang",
    
    # 声母n + 无对应韵母
    "nua", "nuan", "nüan", "nvan", "nve", "nv", "nüe", "nü",
    "nvn", "nün", "nvang", "niang", "niong",
    
    # 声母l + 无对应韵母
    "lua", "luan", "lüan", "lvan", "lve", "lv", "lüe", "lü",
    "lvn", "lün", "lvang", "liang", "liong",
    
    # 声母g + 无对应韵母
    "gü", "gua", "guo", "giai", "giu", "güan", "giong", "gie",
    "ging", "güe", "gün", "giong", "gve", "gvn", "gü",
    "gvang", "gviang", "giao", "gie", "ging", "giong", "gou",
    "gua", "gui", "guo", "gvan", "gve", "gx", "gy", "gz",
    
    # 声母k + 无对应韵母
    "kü", "kua", "kuo", "kiai", "kiu", "küan", "kiong", "kie",
    "king", "küe", "kün", "kiong", "kve", "kvn", "kü",
    "kvang", "kviang", "kiao", "kie", "king", "kiong", "kou",
    "kua", "kui", "kuo", "kvan", "kve", "kx", "ky", "kz",
    
    # 声母h + 无对应韵母
    "hü", "hua", "huo", "hiai", "hiu", "hüan", "hiong", "hie",
    "hing", "hüe", "hün", "hiong", "hve", "hvn", "hü",
    "hvang", "hviang", "hiao", "hie", "hing", "hiong", "hou",
    "hua", "hui", "huo", "hvan", "hve", "hx", "hy", "hz",
    
    # 声母j + 无对应韵母
    "ju", "jo", "jua", "jua", "juan", "jv", "jü", "jve",
    "jvn", "jüe", "jün", "jvang", "jv", "jü", "jua", "juo",
    "jiai", "jio", "jong", "jua", "jui", "jvan", "jve", "jx",
    "jy", "jz", "jeng", "jng", "jeng", "jng",
    
    # 声母q + 无对应韵母
    "qu", "qo", "qua", "qua", "quan", "qv", "qü", "qve",
    "qvn", "qüe", "qün", "qvang", "qv", "qü", "qua", "quo",
    "qiai", "qio", "qong", "qua", "qui", "qvan", "qve", "qx",
    "qy", "qz", "qeng", "qng", "qeng", "qng",
    
    # 声母x + 无对应韵母
    "xu", "xo", "xua", "xua", "xuan", "xv", "xü", "xve",
    "xvn", "xüe", "xün", "xvang", "xv", "xü", "xua", "xuo",
    "xiai", "xio", "xong", "xua", "xui", "xvan", "xve", "xx",
    "xy", "xz", "xeng", "xng", "xeng", "xng",
    
    # 声母zh + 无对应韵母
    "zhü", "zhua", "zhuo", "zhiai", "zhiu", "zhüan", "zhiong", "zhie",
    "zhing", "zhüe", "zhün", "zhiong", "zhve", "zhvn", "zhü",
    "zhvang", "zhviang", "zhiao", "zhie", "zhing", "zhiong", "zhou",
    "zhua", "zhui", "zhuo", "zhvan", "zhve", "zhx", "zhy", "zhz",
    
    # 声母ch + 无对应韵母
    "chü", "chua", "chuo", "chiai", "chiu", "chüan", "chiong", "chie",
    "ching", "chüe", "chün", "chiong", "chve", "chvn", "chü",
    "chvang", "chviang", "chiao", "chie", "ching", "chiong", "chou",
    "chua", "chui", "chuo", "chvan", "chve", "chx", "chy", "chz",
    
    # 声母sh + 无对应韵母
    "shü", "shua", "shuo", "shiai", "shiu", "shüan", "shiong", "shie",
    "shing", "shüe", "shün", "shiong", "shve", "shvn", "shü",
    "shvang", "shviang", "shiao", "shie", "shing", "shiong", "shou",
    "shua", "shui", "shuo", "shvan", "shve", "shx", "shy", "shz",
    
    # 声母r + 无对应韵母
    "rü", "rua", "ruo", "riai", "riu", "rüan", "riong", "rie",
    "ring", "rüe", "rün", "riong", "rve", "rvn", "rü",
    "rvang", "rviang", "rao", "rie", "ring", "rong", "rou",
    "rua", "rui", "ruo", "rvan", "rve", "rx", "ry", "rz",
    
    # 声母z + 无对应韵母
    "zü", "zua", "zuo", "ziai", "ziu", "züan", "ziong", "zie",
    "zing", "züe", "zün", "ziong", "zve", "zvn", "zü",
    "zvang", "zviang", "ziao", "zie", "zing", "ziong", "zou",
    "zua", "zui", "zuo", "zvan", "zve", "zx", "zy", "zz",
    
    # 声母c + 无对应韵母
    "cü", "cua", "cuo", "ciai", "ciu", "cüan", "ciong", "cie",
    "cing", "cüe", "cün", "ciong", "cve", "cvn", "cü",
    "cvang", "cviang", "ciao", "cie", "cing", "ciong", "cou",
    "cua", "cui", "cuo", "cvan", "cve", "cx", "cy", "cz",
    
    # 声母s + 无对应韵母
    "sü", "sua", "suo", "siai", "siu", "süan", "siong", "sie",
    "sing", "süe", "sün", "siong", "sve", "svn", "sü",
    "svang", "sviang", "siao", "sie", "sing", "siong", "sou",
    "sua", "sui", "suo", "svan", "sve", "sx", "sy", "sz",
    
    # 声母y + 无对应韵母
    "yü", "yua", "yuo", "yiai", "yiu", "yüan", "yiong", "yie",
    "ying", "yüe", "yün", "yiong", "yve", "yvn", "yü",
    "yvang", "yviang", "yiao", "yie", "ying", "yiong", "you",
    "yua", "yui", "yuo", "yvan", "yve", "yx", "yy", "yz",
    "yang", "yan", "ye", "yi", "yo", "yong", "yu", "yuan",
    "yue", "yun", "yun",
    
    # 声母w + 无对应韵母
    "wü", "wua", "wuo", "wiai", "wiu", "wüan", "wiong", "wie",
    "wing", "wüe", "wün", "wiong", "wve", "wvn", "wü",
    "wvang", "wviang", "wiao", "wie", "wing", "wiong", "wou",
    "wua", "wui", "wuo", "wvan", "wve", "wx", "wy", "wz",
    "wang", "wan", "we", "wei", "wo", "wu",
    
    # 零声母 + 无对应韵母
    "v", "ü", "ve", "vn", "üe", "ün", "vang", "viang",
    "viao", "vie", "ving", "viong", "vou", "vua", "vui", "vuo",
    "van", "ve", "vx", "vy", "vz"
]