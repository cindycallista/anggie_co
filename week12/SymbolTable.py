"""SymbolTable: class 層級 (static/field) 與 subroutine 層級 (arg/var) 的符號表"""


class SymbolTable:
    def __init__(self):
        self.class_scope = {}
        self.sub_scope = {}
        self.counts = {"static": 0, "field": 0, "arg": 0, "var": 0}

    def start_subroutine(self):
        self.sub_scope = {}
        self.counts["arg"] = 0
        self.counts["var"] = 0

    def define(self, name, typ, kind):
        idx = self.counts[kind]
        self.counts[kind] += 1
        scope = self.class_scope if kind in ("static", "field") else self.sub_scope
        scope[name] = (typ, kind, idx)

    def var_count(self, kind):
        return self.counts[kind]

    def _get(self, name):
        return self.sub_scope.get(name) or self.class_scope.get(name)

    def kind_of(self, name):
        e = self._get(name)
        return e[1] if e else None

    def type_of(self, name):
        e = self._get(name)
        return e[0] if e else None

    def index_of(self, name):
        e = self._get(name)
        return e[2] if e else None
