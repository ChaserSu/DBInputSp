#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
构建脚本 - 用于生成DBInputSp可执行文件
"""

import subprocess
import sys
import os

def main():
    """主函数，执行构建命令"""
    print("开始构建DBInputSp可执行文件...")
    
    # 构建命令 - 直接调用系统pyinstaller命令
    build_cmd = [
        "pyinstaller",
        "-F", "-n", "DBInputSp",
        "main.py"
    ]
    
    try:
        # 执行构建命令
        result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
        
        print("构建成功！")
        print("输出信息：")
        print(result.stdout)
        
        # 显示构建产物位置
        dist_dir = os.path.join(os.getcwd(), "dist")
        exe_path = os.path.join(dist_dir, "DBInputSp.exe")
        if os.path.exists(exe_path):
            print(f"\n可执行文件已生成：{exe_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败！返回码：{e.returncode}")
        print("错误信息：")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"构建过程中发生意外错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()