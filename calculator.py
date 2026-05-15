"""
╔══════════════════════════════════════════════════════════════╗
║               🧮  CALCMATE — SMART CALCULATOR  🧮           ║
║          More than just numbers — it understands you         ║
║                     by Chaitanya Tandel                      ║
╚══════════════════════════════════════════════════════════════╝

Features:
  • Basic arithmetic  (+, -, *, /)
  • Advanced math     (power, sqrt, log, trig, factorial)
  • Expression parser (type "2 + 3 * sin(45)")
  • History with undo
  • Unit converter    (km↔miles, °C↔°F, kg↔lbs)
  • Constants         (π, e, golden ratio)
  • Memory store (M+, M-, MR, MC)
"""

import os
import sys
import math
import time

# ── Colour helpers ────────────────────────────────────────────────────────────
def supports_color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

class C:
    R    = "\033[0m"   if supports_color() else ""
    BOLD = "\033[1m"   if supports_color() else ""
    RED  = "\033[91m"  if supports_color() else ""
    GRN  = "\033[92m"  if supports_color() else ""
    YLW  = "\033[93m"  if supports_color() else ""
    CYN  = "\033[96m"  if supports_color() else ""
    PUR  = "\033[95m"  if supports_color() else ""
    DIM  = "\033[2m"   if supports_color() else ""
    WHT  = "\033[97m"  if supports_color() else ""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    clear()
    print(f"\n{C.CYN}{C.BOLD}╔{'═'*56}╗")
    print(f"║{'🧮  C A L C M A T E  —  Smart Calculator'.center(56)}║")
    print(f"╚{'═'*56}╝{C.R}\n")

def divider():
    print(f"{C.DIM}{'─'*58}{C.R}")

# ── State ─────────────────────────────────────────────────────────────────────
history   = []   # list of (expression_str, result)
memory    = 0.0  # M register
last_ans  = 0.0  # ANS register

# ── Safe expression evaluator ─────────────────────────────────────────────────
SAFE_NAMES = {
    # constants
    "pi": math.pi, "e": math.e, "phi": (1 + math.sqrt(5)) / 2,
    "inf": math.inf, "ans": 0,
    # functions
    "sin":   lambda x: math.sin(math.radians(x)),
    "cos":   lambda x: math.cos(math.radians(x)),
    "tan":   lambda x: math.tan(math.radians(x)),
    "asin":  lambda x: math.degrees(math.asin(x)),
    "acos":  lambda x: math.degrees(math.acos(x)),
    "atan":  lambda x: math.degrees(math.atan(x)),
    "sqrt":  math.sqrt,
    "cbrt":  lambda x: x ** (1/3) if x >= 0 else -((-x) ** (1/3)),
    "log":   math.log10,
    "ln":    math.log,
    "log2":  math.log2,
    "abs":   abs,
    "ceil":  math.ceil,
    "floor": math.floor,
    "round": round,
    "fact":  math.factorial,
    "pow":   pow,
    "exp":   math.exp,
    "gcd":   math.gcd,
}

def safe_eval(expr: str) -> float:
    """Safely evaluate a math expression string."""
    global last_ans
    SAFE_NAMES["ans"] = last_ans

    # Allow ** and ^ for power
    expr = expr.replace("^", "**")
    # Allow implicit multiplication: 2pi → 2*pi, 3sqrt(4) → 3*sqrt(4)
    import re
    expr = re.sub(r'(\d)(pi|e\b|phi)', r'\1*\2', expr)

    try:
        result = eval(expr, {"__builtins__": {}}, SAFE_NAMES)
        return float(result)
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero ÷")
    except OverflowError:
        raise ValueError("Result is too large to compute")
    except Exception:
        raise ValueError(f"Could not parse expression: '{expr}'")

# ── Result display ────────────────────────────────────────────────────────────
def format_result(value: float) -> str:
    """Pretty-format a float: int if whole, else up to 10 sig figs."""
    if value == math.inf:
        return "∞"
    if value == -math.inf:
        return "-∞"
    if math.isnan(value):
        return "undefined"
    if value == int(value) and abs(value) < 1e15:
        return f"{int(value):,}"
    # Significant figures
    formatted = f"{value:.10g}"
    # Add thousands separator for large floats
    parts = formatted.split(".")
    try:
        parts[0] = f"{int(parts[0]):,}"
    except ValueError:
        pass
    return ".".join(parts)

def show_result(expr: str, result: float):
    print(f"\n  {C.DIM}{expr}{C.R}")
    print(f"  {C.CYN}{'─'*40}{C.R}")
    print(f"  {C.GRN}{C.BOLD}  = {format_result(result)}{C.R}\n")

# ── History ───────────────────────────────────────────────────────────────────
def show_history():
    if not history:
        print(f"\n  {C.YLW}No history yet.{C.R}")
        return
    print(f"\n  {C.BOLD}📜 Calculation History{C.R}\n")
    for i, (expr, res) in enumerate(history[-15:], 1):
        print(f"  {C.DIM}{i:>3}.{C.R}  {expr:<35}  {C.CYN}= {format_result(res)}{C.R}")

# ── Unit Converter ────────────────────────────────────────────────────────────
CONVERSIONS = {
    "Length": [
        ("km → miles",  lambda x: x * 0.621371),
        ("miles → km",  lambda x: x / 0.621371),
        ("m → feet",    lambda x: x * 3.28084),
        ("feet → m",    lambda x: x / 3.28084),
        ("cm → inches", lambda x: x * 0.393701),
        ("inches → cm", lambda x: x / 0.393701),
    ],
    "Temperature": [
        ("°C → °F",  lambda x: x * 9/5 + 32),
        ("°F → °C",  lambda x: (x - 32) * 5/9),
        ("°C → K",   lambda x: x + 273.15),
        ("K → °C",   lambda x: x - 273.15),
    ],
    "Weight": [
        ("kg → lbs",  lambda x: x * 2.20462),
        ("lbs → kg",  lambda x: x / 2.20462),
        ("g → oz",    lambda x: x * 0.035274),
        ("oz → g",    lambda x: x / 0.035274),
    ],
    "Speed": [
        ("km/h → mph",   lambda x: x * 0.621371),
        ("mph → km/h",   lambda x: x / 0.621371),
        ("m/s → km/h",   lambda x: x * 3.6),
        ("km/h → m/s",   lambda x: x / 3.6),
    ],
}

def unit_converter():
    clear()
    banner()
    print(f"  {C.BOLD}🔄 Unit Converter{C.R}\n")
    cats = list(CONVERSIONS.keys())
    for i, c in enumerate(cats, 1):
        print(f"  {C.CYN}[{i}]{C.R}  {c}")
    c_choice = input(f"\n  {C.YLW}Category: {C.R}").strip()
    if not c_choice.isdigit() or not (1 <= int(c_choice) <= len(cats)):
        return
    cat = cats[int(c_choice) - 1]
    convs = CONVERSIONS[cat]
    print(f"\n  {C.BOLD}{cat} conversions:{C.R}\n")
    for i, (label, _) in enumerate(convs, 1):
        print(f"  {C.CYN}[{i}]{C.R}  {label}")
    conv_choice = input(f"\n  {C.YLW}Conversion: {C.R}").strip()
    if not conv_choice.isdigit() or not (1 <= int(conv_choice) <= len(convs)):
        return
    label, fn = convs[int(conv_choice) - 1]
    try:
        val = float(input(f"  {C.YLW}Enter value: {C.R}"))
        result = fn(val)
        print(f"\n  {C.GRN}{C.BOLD}  {val} {label.split('→')[0].strip()}  =  {format_result(result)} {label.split('→')[1].strip()}{C.R}\n")
    except ValueError:
        print(f"  {C.RED}Invalid number.{C.R}")

# ── Memory operations ─────────────────────────────────────────────────────────
def memory_ops():
    global memory, last_ans
    print(f"\n  {C.BOLD}💾 Memory: {C.CYN}{format_result(memory)}{C.R}\n")
    print(f"  {C.CYN}[1]{C.R}  M+ (add ANS to memory)")
    print(f"  {C.CYN}[2]{C.R}  M- (subtract ANS from memory)")
    print(f"  {C.CYN}[3]{C.R}  MR (recall memory → use as ANS)")
    print(f"  {C.CYN}[4]{C.R}  MC (clear memory)")
    ch = input(f"\n  {C.YLW}Choice: {C.R}").strip()
    if ch == "1":
        memory += last_ans
        print(f"  {C.GRN}M+ → Memory = {format_result(memory)}{C.R}")
    elif ch == "2":
        memory -= last_ans
        print(f"  {C.GRN}M- → Memory = {format_result(memory)}{C.R}")
    elif ch == "3":
        last_ans = memory
        print(f"  {C.GRN}MR → ANS = {format_result(last_ans)}{C.R}")
    elif ch == "4":
        memory = 0.0
        print(f"  {C.GRN}MC → Memory cleared.{C.R}")

# ── Help / cheat sheet ────────────────────────────────────────────────────────
def show_help():
    clear()
    banner()
    print(f"  {C.BOLD}📖 CalcMate Cheat Sheet{C.R}\n")
    topics = [
        ("Arithmetic",    "2 + 3    5 - 1    4 * 6    10 / 2    2 ** 8    10 % 3"),
        ("Trig (degrees)", "sin(30)  cos(60)  tan(45)  asin(0.5)  acos(1)  atan(1)"),
        ("Roots & Logs",  "sqrt(16)  cbrt(27)  log(100)  ln(e)  log2(8)"),
        ("Rounding",      "floor(3.7)  ceil(3.2)  round(3.567, 2)  abs(-5)"),
        ("Constants",     "pi  e  phi  inf  ans  (ans = last result)"),
        ("Special",       "fact(5)  gcd(12,8)  exp(2)  pow(2,10)"),
        ("Memory",        "Press M in menu  →  M+  M-  MR  MC"),
        ("Tip",           "You can chain: sqrt(2**8 + sin(45) * pi)"),
    ]
    for label, examples in topics:
        print(f"  {C.YLW}{C.BOLD}{label:<18}{C.R}  {C.DIM}{examples}{C.R}")
    print()

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    global last_ans, memory

    banner()
    print(f"  {C.DIM}Type a math expression and press Enter.{C.R}")
    print(f"  {C.DIM}Commands: H=help  HI=history  U=units  M=memory  C=clear  Q=quit{C.R}\n")

    while True:
        divider()
        mem_hint = f"  {C.DIM}MEM={format_result(memory)}  ANS={format_result(last_ans)}{C.R}" if memory != 0 or last_ans != 0 else ""
        if mem_hint:
            print(mem_hint)

        try:
            raw = input(f"\n  {C.CYN}calc >{C.R} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  {C.CYN}👋 CalcMate signing off. See you next time!{C.R}\n")
            break

        if not raw:
            continue

        cmd = raw.upper()
        if cmd in ("Q", "QUIT", "EXIT"):
            print(f"\n  {C.CYN}👋 CalcMate signing off. See you next time!{C.R}\n")
            break
        elif cmd in ("H", "HELP"):
            show_help()
            input(f"  {C.DIM}Press Enter to continue...{C.R}")
            banner()
            continue
        elif cmd in ("HI", "HISTORY"):
            show_history()
            continue
        elif cmd in ("U", "UNITS"):
            unit_converter()
            banner()
            continue
        elif cmd == "M":
            memory_ops()
            continue
        elif cmd in ("C", "CLS"):
            banner()
            continue
        elif cmd == "CLEAR HISTORY":
            history.clear()
            print(f"  {C.GRN}History cleared.{C.R}")
            continue

        try:
            result = safe_eval(raw)
            show_result(raw, result)
            history.append((raw, result))
            last_ans = result
        except ValueError as err:
            print(f"\n  {C.RED}⚠  {err}{C.R}\n")
        except Exception as err:
            print(f"\n  {C.RED}⚠  Unexpected error: {err}{C.R}\n")

if __name__ == "__main__":
    main()
