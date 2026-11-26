#!/usr/bin/env python3
"""Jack 編譯器主程式
用法:
    python3 JackCompiler.py Main.jack     -> Main.vm
    python3 JackCompiler.py FolderName/   -> 資料夾內每個 X.jack 產生 X.vm
"""
import os
import sys

from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from CompilationEngine import CompilationEngine


def compile_file(path):
    out_path = os.path.splitext(path)[0] + ".vm"
    writer = VMWriter(out_path)
    try:
        CompilationEngine(JackTokenizer(path), writer).compile_class()
    finally:
        writer.close()
    print(f"已輸出 {out_path}")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    target = os.path.normpath(sys.argv[1])
    if os.path.isdir(target):
        files = sorted(os.path.join(target, f) for f in os.listdir(target) if f.endswith(".jack"))
    else:
        files = [target]
    if not files:
        sys.exit("找不到 .jack 檔案")
    try:
        for f in files:
            compile_file(f)
    except SyntaxError as e:
        sys.exit(f"編譯錯誤 ({f}) {e}")


if __name__ == "__main__":
    main()
