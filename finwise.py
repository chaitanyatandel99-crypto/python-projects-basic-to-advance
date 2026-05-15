"""
╔══════════════════════════════════════════════════════════════╗
║          💰  FINWISE — PERSONAL FINANCE TRACKER  💰         ║
║     Track expenses · Visualise habits · Get AI insights      ║
║                     by Chaitanya Tandel                      ║
╚══════════════════════════════════════════════════════════════╝

Features:
  • Log income & expenses with categories and notes
  • Monthly budget setting with real-time alerts
  • ASCII bar charts for spending by category
  • Month-over-month trend lines
  • Smart AI-style insight engine (rule-based, no API needed)
  • Export report to a text file
  • All data stored in a local JSON file
"""

import os
import sys
import json
import time
import calendar
from datetime import datetime, date
from collections import defaultdict

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
    BLU  = "\033[94m"  if supports_color() else ""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def slow_print(text, delay=0.016):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def banner():
    clear()
    print(f"\n{C.GRN}{C.BOLD}╔{'═'*56}╗")
    print(f"║{'💰  F I N W I S E  —  Finance Tracker'.center(56)}║")
    print(f"╚{'═'*56}╝{C.R}\n")

def divider(color=C.DIM):
    print(f"{color}{'─'*58}{C.R}")

# ── Data file ─────────────────────────────────────────────────────────────────
DATA_FILE = "finwise_data.json"

EXPENSE_CATEGORIES = [
    "🍔 Food & Dining",
    "🚌 Transport",
    "🏠 Housing & Rent",
    "💊 Health",
    "📚 Education",
    "🎮 Entertainment",
    "👕 Shopping",
    "💡 Utilities",
    "✈️  Travel",
    "🎁 Gifts",
    "💼 Business",
    "📦 Other",
]

INCOME_CATEGORIES = [
    "💼 Salary",
    "🎓 Stipend",
    "💻 Freelance",
    "🎁 Gift / Transfer",
    "📈 Investment",
    "🏦 Other Income",
]

def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"transactions": [], "budgets": {}, "user_name": ""}
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Input helpers ─────────────────────────────────────────────────────────────
def pick_from_list(items: list, prompt="Choose: ") -> int:
    for i, item in enumerate(items, 1):
        print(f"   {C.CYN}[{i:>2}]{C.R}  {item}")
    while True:
        raw = input(f"\n  {C.YLW}{prompt}{C.R}").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(items):
            return int(raw) - 1
        print(f"  {C.RED}Please enter a number between 1 and {len(items)}.{C.R}")

def get_amount(prompt="Amount (₹): ") -> float:
    while True:
        raw = input(f"  {C.YLW}{prompt}{C.R}").strip().replace(",", "")
        try:
            val = float(raw)
            if val <= 0:
                print(f"  {C.RED}Amount must be positive.{C.R}")
            else:
                return val
        except ValueError:
            print(f"  {C.RED}Enter a valid number.{C.R}")

def get_date(prompt="Date (YYYY-MM-DD) or Enter for today: ") -> str:
    while True:
        raw = input(f"  {C.YLW}{prompt}{C.R}").strip()
        if not raw:
            return date.today().isoformat()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print(f"  {C.RED}Format must be YYYY-MM-DD (e.g. 2025-05-15).{C.R}")

# ── Add transaction ───────────────────────────────────────────────────────────
def add_transaction(data: dict, t_type: str):
    """t_type: 'expense' or 'income'"""
    divider()
    cats = EXPENSE_CATEGORIES if t_type == "expense" else INCOME_CATEGORIES
    emoji = "💸" if t_type == "expense" else "💵"
    print(f"\n  {C.BOLD}{emoji}  Add {t_type.title()}{C.R}\n")
    print(f"  {C.BOLD}Category:{C.R}\n")
    cat_idx = pick_from_list(cats, "Category number: ")
    category = cats[cat_idx]

    amount = get_amount(f"Amount (₹): ")
    tx_date = get_date()
    note = input(f"  {C.YLW}Note (optional): {C.R}").strip()

    tx = {
        "id":       len(data["transactions"]) + 1,
        "type":     t_type,
        "amount":   amount,
        "category": category,
        "date":     tx_date,
        "note":     note,
    }
    data["transactions"].append(tx)
    save_data(data)

    sign = "-" if t_type == "expense" else "+"
    color = C.RED if t_type == "expense" else C.GRN
    print(f"\n  {color}{C.BOLD}✔  {sign}₹{amount:,.2f}  [{category}]  saved!{C.R}")

    # Budget alert
    if t_type == "expense":
        ym = tx_date[:7]
        budget_check(data, ym)

# ── Budget ────────────────────────────────────────────────────────────────────
def set_budget(data: dict):
    divider()
    print(f"\n  {C.BOLD}🎯  Set Monthly Budget{C.R}\n")
    ym = input(f"  {C.YLW}Month (YYYY-MM) or Enter for current: {C.R}").strip()
    if not ym:
        ym = date.today().strftime("%Y-%m")
    try:
        datetime.strptime(ym + "-01", "%Y-%m-%d")
    except ValueError:
        print(f"  {C.RED}Invalid format. Use YYYY-MM.{C.R}")
        return

    amount = get_amount(f"Budget for {ym} (₹): ")
    data["budgets"][ym] = amount
    save_data(data)
    print(f"  {C.GRN}✔  Budget set: ₹{amount:,.2f} for {ym}{C.R}")

def budget_check(data: dict, ym: str):
    budget = data["budgets"].get(ym)
    if not budget:
        return
    spent = sum(t["amount"] for t in data["transactions"]
                if t["type"] == "expense" and t["date"].startswith(ym))
    pct = (spent / budget) * 100
    remaining = budget - spent

    if pct >= 100:
        print(f"\n  {C.RED}{C.BOLD}🚨 BUDGET EXCEEDED! Spent ₹{spent:,.0f} of ₹{budget:,.0f} ({pct:.0f}%){C.R}")
    elif pct >= 80:
        print(f"\n  {C.YLW}⚠️  Heads up! {pct:.0f}% of budget used. ₹{remaining:,.0f} remaining.{C.R}")

# ── Summary & charts ──────────────────────────────────────────────────────────
def monthly_summary(data: dict, ym=None):
    if not ym:
        ym = date.today().strftime("%Y-%m")
    txs = [t for t in data["transactions"] if t["date"].startswith(ym)]
    if not txs:
        print(f"\n  {C.YLW}No transactions for {ym}.{C.R}")
        return

    income  = sum(t["amount"] for t in txs if t["type"] == "income")
    expense = sum(t["amount"] for t in txs if t["type"] == "expense")
    balance = income - expense
    bal_color = C.GRN if balance >= 0 else C.RED

    # Header
    try:
        yr, mo = map(int, ym.split("-"))
        month_name = calendar.month_name[mo]
    except Exception:
        month_name = ym

    print(f"\n  {C.BOLD}📅  {month_name} {yr if 'yr' in dir() else ym}  Summary{C.R}\n")
    divider()
    print(f"  {C.GRN}Income {C.R}   ₹{income:>12,.2f}")
    print(f"  {C.RED}Expenses{C.R}  ₹{expense:>12,.2f}")
    divider()
    print(f"  {bal_color}{C.BOLD}Balance{C.R}   ₹{balance:>12,.2f}\n")

    budget = data["budgets"].get(ym)
    if budget:
        pct = (expense / budget) * 100
        bar_len = 30
        filled = min(int(bar_len * pct / 100), bar_len)
        color = C.GRN if pct < 70 else (C.YLW if pct < 90 else C.RED)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  Budget  : {color}[{bar}] {pct:.0f}% of ₹{budget:,.0f}{C.R}\n")

    # Category breakdown (expense)
    cat_totals = defaultdict(float)
    for t in txs:
        if t["type"] == "expense":
            cat_totals[t["category"]] += t["amount"]

    if cat_totals:
        print(f"  {C.BOLD}Expense Breakdown:{C.R}\n")
        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
        max_amt = sorted_cats[0][1] if sorted_cats else 1
        for cat, amt in sorted_cats:
            bar_len = 25
            filled = max(1, int(bar_len * amt / max_amt))
            bar = "█" * filled
            pct = (amt / expense * 100) if expense else 0
            print(f"  {cat:<25}  {C.CYN}{bar:<25}{C.R}  ₹{amt:>9,.0f}  ({pct:.0f}%)")
        print()

def recent_transactions(data: dict, n=15):
    txs = sorted(data["transactions"], key=lambda t: t["date"], reverse=True)[:n]
    if not txs:
        print(f"\n  {C.YLW}No transactions yet.{C.R}")
        return
    print(f"\n  {C.BOLD}📋  Recent {len(txs)} Transactions{C.R}\n")
    print(f"  {'#':<4} {'Date':<12} {'Type':<9} {'Category':<26} {'Amount':>10}  Notes")
    divider()
    for t in txs:
        color  = C.RED if t["type"] == "expense" else C.GRN
        sign   = "-" if t["type"] == "expense" else "+"
        note   = (t["note"][:18] + "…") if len(t["note"]) > 19 else t["note"]
        print(f"  {C.DIM}{t['id']:<4}{C.R} {t['date']:<12} {t['type']:<9} {t['category']:<26} {color}{sign}₹{t['amount']:>8,.0f}{C.R}  {C.DIM}{note}{C.R}")

# ── Trend chart ───────────────────────────────────────────────────────────────
def trend_chart(data: dict, months=6):
    today = date.today()
    labels, incomes, expenses = [], [], []

    for offset in range(months - 1, -1, -1):
        mo = today.month - offset
        yr = today.year
        while mo <= 0:
            mo += 12
            yr -= 1
        ym = f"{yr:04d}-{mo:02d}"
        txs = [t for t in data["transactions"] if t["date"].startswith(ym)]
        inc = sum(t["amount"] for t in txs if t["type"] == "income")
        exp = sum(t["amount"] for t in txs if t["type"] == "expense")
        labels.append(calendar.month_abbr[mo])
        incomes.append(inc)
        expenses.append(exp)

    all_vals = incomes + expenses
    max_val = max(all_vals) if any(v > 0 for v in all_vals) else 1
    chart_h = 8

    print(f"\n  {C.BOLD}📈  {months}-Month Trend  ({C.GRN}■ Income{C.R}{C.BOLD}  {C.RED}■ Expense{C.R}{C.BOLD}){C.R}\n")

    for row in range(chart_h, 0, -1):
        threshold = (row / chart_h) * max_val
        line = f"  {C.DIM}₹{threshold:>7,.0f}{C.R}  "
        for i in range(months):
            inc_bar = incomes[i] >= threshold
            exp_bar = expenses[i] >= threshold
            if inc_bar and exp_bar:
                line += f"{C.YLW}▐▌ {C.R}"
            elif inc_bar:
                line += f"{C.GRN}▐  {C.R}"
            elif exp_bar:
                line += f"{C.RED} ▌ {C.R}"
            else:
                line += "   "
        print(line)

    divider()
    label_line = "           "
    for lbl in labels:
        label_line += f" {lbl} "
    print(f"{C.DIM}{label_line}{C.R}\n")

# ── AI Insight Engine ─────────────────────────────────────────────────────────
def generate_insights(data: dict):
    """Rule-based financial insight engine."""
    txs = data["transactions"]
    if len(txs) < 3:
        print(f"\n  {C.YLW}Add more transactions to unlock insights!{C.R}")
        return

    insights = []
    today = date.today()
    ym_now  = today.strftime("%Y-%m")

    mo = today.month - 1 or 12
    yr = today.year if today.month > 1 else today.year - 1
    ym_prev = f"{yr:04d}-{mo:02d}"

    now_exp  = sum(t["amount"] for t in txs if t["type"]=="expense" and t["date"].startswith(ym_now))
    prev_exp = sum(t["amount"] for t in txs if t["type"]=="expense" and t["date"].startswith(ym_prev))
    now_inc  = sum(t["amount"] for t in txs if t["type"]=="income"  and t["date"].startswith(ym_now))

    # 1. Spending trend
    if prev_exp > 0:
        pct_change = ((now_exp - prev_exp) / prev_exp) * 100
        if pct_change > 20:
            insights.append((C.RED,   f"Your spending is up {pct_change:.0f}% compared to last month. Consider reviewing non-essentials."))
        elif pct_change < -10:
            insights.append((C.GRN,   f"Great job! Spending is down {abs(pct_change):.0f}% from last month. You're improving!"))

    # 2. Savings rate
    if now_inc > 0:
        savings_rate = ((now_inc - now_exp) / now_inc) * 100
        if savings_rate >= 30:
            insights.append((C.GRN,   f"Excellent savings rate this month: {savings_rate:.0f}%. Financial experts recommend 20%+."))
        elif savings_rate < 0:
            insights.append((C.RED,   f"You're spending more than you earn this month by ₹{abs(now_inc - now_exp):,.0f}. Watch out!"))
        else:
            insights.append((C.YLW,   f"Savings rate: {savings_rate:.0f}%. Try to push toward 20% — small cuts add up!"))

    # 3. Top spending category
    cat_totals = defaultdict(float)
    for t in txs:
        if t["type"] == "expense" and t["date"].startswith(ym_now):
            cat_totals[t["category"]] += t["amount"]
    if cat_totals:
        top_cat, top_amt = max(cat_totals.items(), key=lambda x: x[1])
        insights.append((C.CYN, f"Your biggest spend this month is {top_cat} at ₹{top_amt:,.0f}. Is this expected?"))

    # 4. Budget warning
    budget = data["budgets"].get(ym_now)
    if budget:
        pct = (now_exp / budget) * 100
        days_left = (date(today.year, today.month, calendar.monthrange(today.year, today.month)[1]) - today).days
        if pct > 80 and days_left > 7:
            insights.append((C.RED, f"You've used {pct:.0f}% of your budget with {days_left} days left. Slow down on spending!"))

    # 5. Food spending
    food_amt = sum(t["amount"] for t in txs if "Food" in t["category"] and t["date"].startswith(ym_now))
    if food_amt > 0 and now_inc > 0 and (food_amt / now_inc) > 0.30:
        insights.append((C.YLW, f"Food & dining takes {food_amt/now_inc*100:.0f}% of income. Cooking at home can save a lot!"))

    # 6. No income logged
    if now_inc == 0 and now_exp > 0:
        insights.append((C.DIM, "No income logged this month yet. Don't forget to record your earnings for an accurate picture."))

    # Display
    print(f"\n  {C.BOLD}🤖  FinWise AI Insights{C.R}\n")
    if not insights:
        insights.append((C.GRN, "Everything looks balanced! Keep up the good habits."))

    for color, msg in insights:
        slow_print(f"  {color}▸  {msg}{C.R}", 0.012)
        print()

# ── Export report ─────────────────────────────────────────────────────────────
def export_report(data: dict):
    ym = input(f"  {C.YLW}Export month (YYYY-MM) or Enter for current: {C.R}").strip()
    if not ym:
        ym = date.today().strftime("%Y-%m")
    txs = [t for t in data["transactions"] if t["date"].startswith(ym)]
    if not txs:
        print(f"  {C.YLW}No data for {ym}.{C.R}")
        return

    filename = f"finwise_report_{ym}.txt"
    income  = sum(t["amount"] for t in txs if t["type"] == "income")
    expense = sum(t["amount"] for t in txs if t["type"] == "expense")
    balance = income - expense

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"FinWise Report — {ym}\n")
        f.write("=" * 50 + "\n")
        f.write(f"Income  : Rs {income:,.2f}\n")
        f.write(f"Expenses: Rs {expense:,.2f}\n")
        f.write(f"Balance : Rs {balance:,.2f}\n\n")
        f.write("Transactions:\n")
        f.write("-" * 50 + "\n")
        for t in sorted(txs, key=lambda x: x["date"]):
            sign = "-" if t["type"] == "expense" else "+"
            f.write(f"{t['date']}  {sign}Rs {t['amount']:>10,.2f}  {t['category']:<26}  {t['note']}\n")

    print(f"  {C.GRN}✔  Report saved to {filename}{C.R}")

# ── Main menu ─────────────────────────────────────────────────────────────────
def main_menu(data: dict):
    ym = date.today().strftime("%Y-%m")
    expense = sum(t["amount"] for t in data["transactions"]
                  if t["type"] == "expense" and t["date"].startswith(ym))
    income  = sum(t["amount"] for t in data["transactions"]
                  if t["type"] == "income" and t["date"].startswith(ym))
    budget  = data["budgets"].get(ym, 0)

    banner()
    print(f"  {C.DIM}This month  ·  Income: {C.GRN}₹{income:,.0f}{C.R}{C.DIM}  ·  Expenses: {C.RED}₹{expense:,.0f}{C.R}{C.DIM}  ·  Budget: ₹{budget:,.0f}{C.R}\n")

    options = [
        ("1", "💸  Add Expense"),
        ("2", "💵  Add Income"),
        ("3", "📅  Monthly Summary"),
        ("4", "📋  Recent Transactions"),
        ("5", "📈  Trend Chart (6 months)"),
        ("6", "🤖  AI Insights"),
        ("7", "🎯  Set Monthly Budget"),
        ("8", "📄  Export Report"),
        ("0", "🚪  Exit"),
    ]
    for key, label in options:
        print(f"  {C.CYN}[{key}]{C.R}  {label}")
    print()
    return input(f"  {C.YLW}Choose: {C.R}").strip()

def main():
    data = load_data()

    if not data.get("user_name"):
        banner()
        slow_print(f"  {C.CYN}Welcome to FinWise! Let's personalise your tracker.{C.R}\n", 0.02)
        name = input(f"  {C.YLW}Your name: {C.R}").strip() or "User"
        data["user_name"] = name
        save_data(data)
        print(f"\n  {C.GRN}Hey {name}! Your finance vault is ready. Let's build great habits. 💪{C.R}")
        time.sleep(1.5)

    while True:
        choice = main_menu(data)

        if   choice == "1": add_transaction(data, "expense")
        elif choice == "2": add_transaction(data, "income")
        elif choice == "3":
            ym_in = input(f"  {C.YLW}Month (YYYY-MM) or Enter for current: {C.R}").strip()
            monthly_summary(data, ym_in or None)
        elif choice == "4": recent_transactions(data)
        elif choice == "5": trend_chart(data)
        elif choice == "6": generate_insights(data)
        elif choice == "7": set_budget(data)
        elif choice == "8": export_report(data)
        elif choice == "0":
            slow_print(f"\n  {C.GRN}Keep hustling, {data['user_name']}! Every rupee saved is a step forward. 👋{C.R}\n", 0.02)
            break
        else:
            print(f"  {C.RED}Invalid option.{C.R}")

        input(f"\n  {C.DIM}Press Enter to return to menu...{C.R}")

if __name__ == "__main__":
    main()
