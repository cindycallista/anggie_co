
import sys
from pathlib import Path


COMP = {
    # a = 0
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    # a = 1 (same operations on M)
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
# Commutative forms are accepted too (e.g. A+D, M|D)
for _op in "+&|":
    for _r in "AM":
        COMP[f"{_r}{_op}D"] = COMP[f"D{_op}{_r}"]

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
    **{f"R{i}": i for i in range(16)},
}


class AsmError(Exception):
    pass


# --- Parsing ---------------------------------------------------------------

def clean(line: str) -> str:
    """Strip comments and all whitespace."""
    return "".join(line.split("//", 1)[0].split())


def encode_dest(dest: str) -> str:
    if any(c not in "ADM" for c in dest) or len(set(dest)) != len(dest):
        raise AsmError(f"invalid dest '{dest}'")
    return "".join("1" if c in dest else "0" for c in "ADM")


def encode_c(instr: str) -> str:
    dest, comp, jump = "", instr, ""
    if "=" in comp:
        dest, comp = comp.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    if comp not in COMP:
        raise AsmError(f"invalid comp '{comp}'")
    if jump not in JUMP:
        raise AsmError(f"invalid jump '{jump}'")
    return "111" + COMP[comp] + encode_dest(dest) + JUMP[jump]


# --- Assembler -------------------------------------------------------------

def assemble(lines):
    # Pass 1: strip, collect labels, record instruction addresses
    symbols = dict(PREDEFINED)
    program = []  # (source line number, instruction)
    for lineno, raw in enumerate(lines, 1):
        line = clean(raw)
        if not line:
            continue
        if line.startswith("("):
            if not line.endswith(")") or len(line) < 3:
                raise AsmError(f"line {lineno}: malformed label '{line}'")
            label = line[1:-1]
            if label in symbols:
                raise AsmError(f"line {lineno}: duplicate label '{label}'")
            symbols[label] = len(program)
        else:
            program.append((lineno, line))

    # Pass 2: translate, allocating variables from RAM[16]
    next_var = 16
    out = []
    for lineno, instr in program:
        try:
            if instr.startswith("@"):
                sym = instr[1:]
                if not sym:
                    raise AsmError("empty A-instruction")
                if sym.isdigit():
                    value = int(sym)
                else:
                    if sym[0].isdigit():
                        raise AsmError(f"invalid symbol '{sym}'")
                    if sym not in symbols:
                        symbols[sym] = next_var
                        next_var += 1
                    value = symbols[sym]
                if value > 32767:
                    raise AsmError(f"address {value} out of range (max 32767)")
                out.append(f"0{value:015b}")
            else:
                out.append(encode_c(instr))
        except AsmError as e:
            raise AsmError(f"line {lineno}: {e}") from None
    return out


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) == 3 else src.with_suffix(".hack")
    try:
        code = assemble(src.read_text().splitlines())
    except (AsmError, OSError) as e:
        sys.exit(f"Error: {e}")
    dst.write_text("\n".join(code) + "\n")
    print(f"Wrote {len(code)} instructions to {dst}")


if __name__ == "__main__":
    main()
