"""CompilationEngine: 遞迴下降語法分析，同時直接產生 VM 程式碼"""
from JackTokenizer import KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST
from SymbolTable import SymbolTable

SEGMENT = {"static": "static", "field": "this", "arg": "argument", "var": "local"}
BINARY_OPS = {"+": "add", "-": "sub", "&": "and", "|": "or",
              "<": "lt", ">": "gt", "=": "eq"}


class CompilationEngine:
    def __init__(self, tokenizer, writer):
        self.t = tokenizer
        self.w = writer
        self.st = SymbolTable()
        self.class_name = ""
        self.label_n = 0

    # ---------- 小工具 ----------
    def _error(self, msg):
        raise SyntaxError(f"第 {self.t.peek()[2]} 行: {msg}")

    def _is(self, *vals, k=0):
        tok = self.t.peek(k)
        return tok[0] in (KEYWORD, SYMBOL) and tok[1] in vals

    def _eat(self, *vals):
        if not self._is(*vals):
            self._error(f"預期 {' 或 '.join(vals)}，但得到 {self.t.peek()[1]!r}")
        return self.t.advance()[1]

    def _ident(self):
        if self.t.peek()[0] != IDENTIFIER:
            self._error(f"預期識別字，但得到 {self.t.peek()[1]!r}")
        return self.t.advance()[1]

    def _type(self):
        if self._is("int", "char", "boolean"):
            return self.t.advance()[1]
        return self._ident()

    def _lookup(self, name):
        kind = self.st.kind_of(name)
        if kind is None:
            self._error(f"未宣告的變數 {name}")
        return SEGMENT[kind], self.st.index_of(name)

    def _new_label(self, prefix):
        label = f"{prefix}{self.label_n}"
        self.label_n += 1
        return label

    # ---------- 程式結構 ----------
    def compile_class(self):
        self._eat("class")
        self.class_name = self._ident()
        self._eat("{")
        while self._is("static", "field"):
            self.compile_class_var_dec()
        while self._is("constructor", "function", "method"):
            self.compile_subroutine()
        self._eat("}")

    def compile_class_var_dec(self):
        kind = self._eat("static", "field")
        typ = self._type()
        self.st.define(self._ident(), typ, kind)
        while self._is(","):
            self._eat(",")
            self.st.define(self._ident(), typ, kind)
        self._eat(";")

    def compile_subroutine(self):
        sub_kind = self._eat("constructor", "function", "method")
        if self._is("void"):
            self._eat("void")
        else:
            self._type()
        name = self._ident()
        self.st.start_subroutine()
        if sub_kind == "method":
            self.st.define("this", self.class_name, "arg")
        self._eat("(")
        self.compile_parameter_list()
        self._eat(")")
        self._eat("{")
        while self._is("var"):
            self.compile_var_dec()
        # 必須等 var 宣告完才知道 local 數量
        self.w.write_function(f"{self.class_name}.{name}", self.st.var_count("var"))
        if sub_kind == "constructor":
            self.w.write_push("constant", self.st.var_count("field"))
            self.w.write_call("Memory.alloc", 1)
            self.w.write_pop("pointer", 0)
        elif sub_kind == "method":
            self.w.write_push("argument", 0)
            self.w.write_pop("pointer", 0)
        self.compile_statements()
        self._eat("}")

    def compile_parameter_list(self):
        if self._is(")"):
            return
        while True:
            typ = self._type()
            self.st.define(self._ident(), typ, "arg")
            if self._is(","):
                self._eat(",")
            else:
                break

    def compile_var_dec(self):
        self._eat("var")
        typ = self._type()
        self.st.define(self._ident(), typ, "var")
        while self._is(","):
            self._eat(",")
            self.st.define(self._ident(), typ, "var")
        self._eat(";")

    # ---------- 陳述式 ----------
    def compile_statements(self):
        while self._is("let", "if", "while", "do", "return"):
            {"let": self.compile_let, "if": self.compile_if,
             "while": self.compile_while, "do": self.compile_do,
             "return": self.compile_return}[self.t.peek()[1]]()

    def compile_let(self):
        self._eat("let")
        name = self._ident()
        if self._is("["):
            seg, idx = self._lookup(name)
            self._eat("[")
            self.w.write_push(seg, idx)
            self.compile_expression()
            self._eat("]")
            self.w.write_arithmetic("add")          # 目標位址
            self._eat("=")
            self.compile_expression()
            self._eat(";")
            self.w.write_pop("temp", 0)             # 先暫存右式的值
            self.w.write_pop("pointer", 1)          # THAT = 目標位址
            self.w.write_push("temp", 0)
            self.w.write_pop("that", 0)
        else:
            self._eat("=")
            self.compile_expression()
            self._eat(";")
            seg, idx = self._lookup(name)
            self.w.write_pop(seg, idx)

    def compile_if(self):
        l_else = self._new_label("IF_ELSE")
        l_end = self._new_label("IF_END")
        self._eat("if")
        self._eat("(")
        self.compile_expression()
        self._eat(")")
        self.w.write_arithmetic("not")
        self.w.write_if(l_else)
        self._eat("{")
        self.compile_statements()
        self._eat("}")
        if self._is("else"):
            self.w.write_goto(l_end)
            self.w.write_label(l_else)
            self._eat("else")
            self._eat("{")
            self.compile_statements()
            self._eat("}")
            self.w.write_label(l_end)
        else:
            self.w.write_label(l_else)

    def compile_while(self):
        l_top = self._new_label("WHILE_EXP")
        l_end = self._new_label("WHILE_END")
        self._eat("while")
        self.w.write_label(l_top)
        self._eat("(")
        self.compile_expression()
        self._eat(")")
        self.w.write_arithmetic("not")
        self.w.write_if(l_end)
        self._eat("{")
        self.compile_statements()
        self._eat("}")
        self.w.write_goto(l_top)
        self.w.write_label(l_end)

    def compile_do(self):
        self._eat("do")
        name = self._ident()
        self._subroutine_call(name)
        self._eat(";")
        self.w.write_pop("temp", 0)                 # 丟棄回傳值

    def compile_return(self):
        self._eat("return")
        if self._is(";"):
            self.w.write_push("constant", 0)        # void 函式也要回傳 0
        else:
            self.compile_expression()
        self._eat(";")
        self.w.write_return()

    # ---------- 運算式 ----------
    def compile_expression(self):
        self.compile_term()
        while self._is("+", "-", "*", "/", "&", "|", "<", ">", "="):
            op = self.t.advance()[1]
            self.compile_term()
            if op == "*":
                self.w.write_call("Math.multiply", 2)
            elif op == "/":
                self.w.write_call("Math.divide", 2)
            else:
                self.w.write_arithmetic(BINARY_OPS[op])

    def compile_term(self):
        kind, val, _ = self.t.peek()
        if kind == INT_CONST:
            self.t.advance()
            self.w.write_push("constant", val)
        elif kind == STRING_CONST:
            self.t.advance()
            self.w.write_push("constant", len(val))
            self.w.write_call("String.new", 1)
            for ch in val:
                self.w.write_push("constant", ord(ch))
                self.w.write_call("String.appendChar", 2)
        elif kind == KEYWORD and val in ("true", "false", "null", "this"):
            self.t.advance()
            if val == "this":
                self.w.write_push("pointer", 0)
            else:
                self.w.write_push("constant", 0)
                if val == "true":
                    self.w.write_arithmetic("not")  # true = -1
        elif kind == IDENTIFIER:
            if self._is("[", k=1):
                name = self._ident()
                seg, idx = self._lookup(name)
                self._eat("[")
                self.w.write_push(seg, idx)
                self.compile_expression()
                self._eat("]")
                self.w.write_arithmetic("add")
                self.w.write_pop("pointer", 1)
                self.w.write_push("that", 0)
            elif self._is("(", ".", k=1):
                self._subroutine_call(self._ident())
            else:
                seg, idx = self._lookup(self._ident())
                self.w.write_push(seg, idx)
        elif self._is("("):
            self._eat("(")
            self.compile_expression()
            self._eat(")")
        elif self._is("-", "~"):
            op = self.t.advance()[1]
            self.compile_term()
            self.w.write_arithmetic("neg" if op == "-" else "not")
        else:
            self._error(f"無效的運算式，遇到 {val!r}")

    def _subroutine_call(self, name):
        """name 已被讀取；處理 name(...) 與 name.sub(...)"""
        n_args = 0
        if self._is("."):
            self._eat(".")
            sub = self._ident()
            if self.st.kind_of(name) is not None:     # 變數 → method 呼叫
                seg, idx = self._lookup(name)
                self.w.write_push(seg, idx)
                target = f"{self.st.type_of(name)}.{sub}"
                n_args = 1
            else:                                      # 類別名 → function/constructor
                target = f"{name}.{sub}"
        else:                                          # 省略物件 → 對 this 呼叫 method
            target = f"{self.class_name}.{name}"
            self.w.write_push("pointer", 0)
            n_args = 1
        self._eat("(")
        n_args += self.compile_expression_list()
        self._eat(")")
        self.w.write_call(target, n_args)

    def compile_expression_list(self):
        if self._is(")"):
            return 0
        count = 1
        self.compile_expression()
        while self._is(","):
            self._eat(",")
            self.compile_expression()
            count += 1
        return count
