"""JackTokenizer: 把 .jack 原始碼切成 token（自動略過註解與空白）"""
import re

KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST = (
    "keyword", "symbol", "identifier", "integerConstant", "stringConstant")

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static", "var",
    "int", "char", "boolean", "void", "true", "false", "null", "this",
    "let", "do", "if", "else", "while", "return",
}

# 順序很重要：註解必須在 symbol 的 "/" 之前比對
_TOKEN = re.compile(r'''
    (?P<ws>\s+|//[^\n]*|/\*.*?\*/)
  | (?P<string>"[^"\n]*")
  | (?P<int>\d+)
  | (?P<ident>[A-Za-z_][A-Za-z_0-9]*)
  | (?P<symbol>[{}()\[\].,;+\-*/&|<>=~])
''', re.S | re.X)


def tokenize(src):
    """回傳 [(type, value, line), ...]"""
    tokens, pos, line = [], 0, 1
    while pos < len(src):
        m = _TOKEN.match(src, pos)
        if not m:
            raise SyntaxError(f"第 {line} 行: 無法辨識的字元 {src[pos]!r}")
        text, kind = m.group(), m.lastgroup
        if kind != "ws":
            if kind == "string":
                tokens.append((STRING_CONST, text[1:-1], line))
            elif kind == "int":
                value = int(text)
                if value > 32767:
                    raise SyntaxError(f"第 {line} 行: 整數 {value} 超過 32767")
                tokens.append((INT_CONST, value, line))
            elif kind == "ident":
                tokens.append((KEYWORD if text in KEYWORDS else IDENTIFIER, text, line))
            else:
                tokens.append((SYMBOL, text, line))
        line += text.count("\n")
        pos = m.end()
    return tokens


class JackTokenizer:
    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            self.tokens = tokenize(f.read())
        self.i = 0

    def has_more_tokens(self):
        return self.i < len(self.tokens)

    def peek(self, k=0):
        idx = self.i + k
        if idx < len(self.tokens):
            return self.tokens[idx]
        last_line = self.tokens[-1][2] if self.tokens else 0
        return (None, None, last_line)

    def advance(self):
        tok = self.tokens[self.i]
        self.i += 1
        return tok
