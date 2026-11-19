#!/usr/bin/env python3
"""nand2tetris VM translator (Project 7 + 8)

    python3 VMTranslator.py Foo.vm          -> Foo.asm（不加 bootstrap）
    python3 VMTranslator.py FolderName/     -> FolderName/FolderName.asm（加 bootstrap）
"""
import os
import sys

SEGMENTS = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}


class CodeWriter:
    def __init__(self, out):
        self.out = out
        self.file_name = ""
        self.func = ""
        self.label_id = 0
        self.call_id = 0

    def emit(self, *lines):
        for line in lines:
            self.out.write(line + "\n")

    def set_file(self, name):
        self.file_name = name

    # ---------- bootstrap ----------
    def write_init(self):
        self.emit("// bootstrap", "@256", "D=A", "@SP", "M=D")
        self.write_call("Sys.init", 0)

    # ---------- 算術 / 邏輯 ----------
    def write_arithmetic(self, cmd):
        self.emit(f"// {cmd}")
        if cmd in ("add", "sub", "and", "or"):
            op = {"add": "+", "sub": "-", "and": "&", "or": "|"}[cmd]
            self.emit("@SP", "AM=M-1", "D=M", "A=A-1", f"M=M{op}D")
        elif cmd in ("neg", "not"):
            op = "-" if cmd == "neg" else "!"
            self.emit("@SP", "A=M-1", f"M={op}M")
        elif cmd in ("eq", "gt", "lt"):
            jmp = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[cmd]
            n = self.label_id
            self.label_id += 1
            self.emit(
                "@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D",
                f"@TRUE{n}", f"D;{jmp}",
                "@SP", "A=M-1", "M=0",
                f"@END{n}", "0;JMP",
                f"(TRUE{n})", "@SP", "A=M-1", "M=-1",
                f"(END{n})",
            )
        else:
            raise ValueError(f"未知的算術指令: {cmd}")

    # ---------- push / pop ----------
    def _push_d(self):
        self.emit("@SP", "A=M", "M=D", "@SP", "M=M+1")

    def write_push_pop(self, cmd, seg, i):
        self.emit(f"// {cmd} {seg} {i}")
        if cmd == "push":
            if seg == "constant":
                self.emit(f"@{i}", "D=A")
            elif seg in SEGMENTS:
                self.emit(f"@{i}", "D=A", f"@{SEGMENTS[seg]}", "A=D+M", "D=M")
            elif seg == "temp":
                self.emit(f"@{5 + int(i)}", "D=M")
            elif seg == "pointer":
                self.emit(f"@{3 + int(i)}", "D=M")
            elif seg == "static":
                self.emit(f"@{self.file_name}.{i}", "D=M")
            else:
                raise ValueError(f"未知的 segment: {seg}")
            self._push_d()
        else:  # pop
            if seg in SEGMENTS:
                self.emit(f"@{i}", "D=A", f"@{SEGMENTS[seg]}", "D=D+M",
                          "@R13", "M=D",
                          "@SP", "AM=M-1", "D=M",
                          "@R13", "A=M", "M=D")
            else:
                if seg == "temp":
                    addr = f"@{5 + int(i)}"
                elif seg == "pointer":
                    addr = f"@{3 + int(i)}"
                elif seg == "static":
                    addr = f"@{self.file_name}.{i}"
                else:
                    raise ValueError(f"無法 pop 到 segment: {seg}")
                self.emit("@SP", "AM=M-1", "D=M", addr, "M=D")

    # ---------- 分支 ----------
    def _label(self, name):
        return f"{self.func}${name}" if self.func else name

    def write_label(self, name):
        self.emit(f"// label {name}", f"({self._label(name)})")

    def write_goto(self, name):
        self.emit(f"// goto {name}", f"@{self._label(name)}", "0;JMP")

    def write_if(self, name):
        self.emit(f"// if-goto {name}", "@SP", "AM=M-1", "D=M",
                  f"@{self._label(name)}", "D;JNE")

    # ---------- 函式 ----------
    def write_function(self, name, n_vars):
        self.func = name
        self.emit(f"// function {name} {n_vars}", f"({name})")
        for _ in range(int(n_vars)):
            self.emit("@SP", "A=M", "M=0", "@SP", "M=M+1")

    def write_call(self, name, n_args):
        ret = f"{name}$ret.{self.call_id}"
        self.call_id += 1
        self.emit(f"// call {name} {n_args}")
        self.emit(f"@{ret}", "D=A")
        self._push_d()
        for reg in ("LCL", "ARG", "THIS", "THAT"):
            self.emit(f"@{reg}", "D=M")
            self._push_d()
        self.emit("@SP", "D=M", f"@{int(n_args) + 5}", "D=D-A", "@ARG", "M=D")
        self.emit("@SP", "D=M", "@LCL", "M=D")
        self.emit(f"@{name}", "0;JMP", f"({ret})")

    def write_return(self):
        self.emit("// return")
        self.emit("@LCL", "D=M", "@R13", "M=D")            # frame = LCL
        self.emit("@5", "A=D-A", "D=M", "@R14", "M=D")     # retAddr = *(frame-5)
        self.emit("@SP", "AM=M-1", "D=M", "@ARG", "A=M", "M=D")  # *ARG = pop()
        self.emit("@ARG", "D=M+1", "@SP", "M=D")           # SP = ARG+1
        for reg in ("THAT", "THIS", "ARG", "LCL"):         # 還原 caller 狀態
            self.emit("@R13", "AM=M-1", "D=M", f"@{reg}", "M=D")
        self.emit("@R14", "A=M", "0;JMP")                  # goto retAddr


def parse(path):
    """產生 (指令, 參數...) tuple，已去除註解與空白。"""
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("//")[0].strip()
            if line:
                yield line.split()


def translate_file(vm_path, cw):
    cw.set_file(os.path.splitext(os.path.basename(vm_path))[0])
    for parts in parse(vm_path):
        cmd = parts[0]
        if cmd in ("push", "pop"):
            cw.write_push_pop(cmd, parts[1], parts[2])
        elif cmd == "label":
            cw.write_label(parts[1])
        elif cmd == "goto":
            cw.write_goto(parts[1])
        elif cmd == "if-goto":
            cw.write_if(parts[1])
        elif cmd == "function":
            cw.write_function(parts[1], parts[2])
        elif cmd == "call":
            cw.write_call(parts[1], parts[2])
        elif cmd == "return":
            cw.write_return()
        else:
            cw.write_arithmetic(cmd)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    target = os.path.normpath(sys.argv[1])
    if os.path.isdir(target):
        vm_files = sorted(
            os.path.join(target, f) for f in os.listdir(target) if f.endswith(".vm")
        )
        out_path = os.path.join(target, os.path.basename(target) + ".asm")
        bootstrap = True
    else:
        vm_files = [target]
        out_path = os.path.splitext(target)[0] + ".asm"
        bootstrap = False

    if not vm_files:
        sys.exit("找不到 .vm 檔案")

    with open(out_path, "w", encoding="utf-8") as out:
        cw = CodeWriter(out)
        if bootstrap:
            cw.write_init()
        for vm in vm_files:
            translate_file(vm, cw)
    print(f"已輸出 {out_path}")


if __name__ == "__main__":
    main()