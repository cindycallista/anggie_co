"""VMWriter: 輸出 VM 指令"""


class VMWriter:
    def __init__(self, path):
        self.out = open(path, "w", encoding="utf-8")

    def _w(self, line):
        self.out.write(line + "\n")

    def write_push(self, segment, index):
        self._w(f"push {segment} {index}")

    def write_pop(self, segment, index):
        self._w(f"pop {segment} {index}")

    def write_arithmetic(self, command):
        self._w(command)

    def write_label(self, label):
        self._w(f"label {label}")

    def write_goto(self, label):
        self._w(f"goto {label}")

    def write_if(self, label):
        self._w(f"if-goto {label}")

    def write_call(self, name, n_args):
        self._w(f"call {name} {n_args}")

    def write_function(self, name, n_locals):
        self._w(f"function {name} {n_locals}")

    def write_return(self):
        self._w("return")

    def close(self):
        self.out.close()
