"""
╔══════════════════════════════════════════════════════════════╗
║               🧠  BRAIN BUSTER QUIZ GAME  🧠                ║
║                  Built with Python & passion                 ║
║                     by Chaitanya Tandel                      ║
╚══════════════════════════════════════════════════════════════╝
"""

import random
import time
import os
import sys

# ── Colour helpers (works on Windows + Mac + Linux) ──────────────────────────
def supports_color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

class C:  # Colours
    RESET  = "\033[0m"   if supports_color() else ""
    BOLD   = "\033[1m"   if supports_color() else ""
    RED    = "\033[91m"  if supports_color() else ""
    GREEN  = "\033[92m"  if supports_color() else ""
    YELLOW = "\033[93m"  if supports_color() else ""
    CYAN   = "\033[96m"  if supports_color() else ""
    PURPLE = "\033[95m"  if supports_color() else ""
    WHITE  = "\033[97m"  if supports_color() else ""
    DIM    = "\033[2m"   if supports_color() else ""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def slow_print(text, delay=0.025):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def banner(title, color=C.CYAN):
    width = 60
    border = "═" * width
    print(f"\n{color}{C.BOLD}╔{border}╗")
    print(f"║{title.center(width)}║")
    print(f"╚{border}╝{C.RESET}\n")

# ── Question Bank ─────────────────────────────────────────────────────────────
CATEGORIES = {
    "🔬 Science": [
        {
            "q": "What is the chemical symbol for gold?",
            "options": ["Go", "Gd", "Au", "Ag"],
            "answer": "Au",
            "fact": "Au comes from the Latin word 'Aurum', meaning gold."
        },
        {
            "q": "How many bones are in the adult human body?",
            "options": ["196", "206", "216", "226"],
            "answer": "206",
            "fact": "Babies are born with ~270 bones; many fuse together as we grow!"
        },
        {
            "q": "What planet is known as the Red Planet?",
            "options": ["Venus", "Jupiter", "Saturn", "Mars"],
            "answer": "Mars",
            "fact": "Mars looks red because its surface is covered in iron oxide (rust)."
        },
        {
            "q": "What is the speed of light (approx)?",
            "options": ["300,000 km/s", "150,000 km/s", "450,000 km/s", "100,000 km/s"],
            "answer": "300,000 km/s",
            "fact": "Light travels 299,792,458 metres per second — roughly 7.5 times around Earth each second!"
        },
        {
            "q": "Which gas do plants absorb during photosynthesis?",
            "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
            "answer": "Carbon Dioxide",
            "fact": "Plants absorb CO₂ and release oxygen — the exact opposite of us breathing!"
        },
    ],
    "💻 Technology": [
        {
            "q": "Who is credited as the creator of Python?",
            "options": ["Linus Torvalds", "Guido van Rossum", "James Gosling", "Dennis Ritchie"],
            "answer": "Guido van Rossum",
            "fact": "Guido named Python after 'Monty Python's Flying Circus', not the snake!"
        },
        {
            "q": "What does CPU stand for?",
            "options": ["Central Processing Unit", "Core Program Utility", "Central Program Unit", "Core Processing Unit"],
            "answer": "Central Processing Unit",
            "fact": "Modern CPUs can execute billions of instructions per second."
        },
        {
            "q": "What does HTML stand for?",
            "options": ["HyperText Markup Language", "HighText Machine Language", "HyperText Machine Language", "HyperTool Markup Language"],
            "answer": "HyperText Markup Language",
            "fact": "HTML was created by Tim Berners-Lee in 1991 to share documents at CERN."
        },
        {
            "q": "Which company developed the ChatGPT AI?",
            "options": ["Google", "Meta", "OpenAI", "Microsoft"],
            "answer": "OpenAI",
            "fact": "ChatGPT reached 100 million users in just 2 months — the fastest ever."
        },
        {
            "q": "What does 'RAM' stand for in computers?",
            "options": ["Random Access Memory", "Read And Modify", "Runtime Access Module", "Rapid Access Memory"],
            "answer": "Random Access Memory",
            "fact": "RAM is 'volatile' — it loses all data when power is cut."
        },
    ],
    "🌍 General Knowledge": [
        {
            "q": "What is the capital of Japan?",
            "options": ["Osaka", "Kyoto", "Tokyo", "Hiroshima"],
            "answer": "Tokyo",
            "fact": "Tokyo is the world's most populous metropolitan area, with ~37 million people."
        },
        {
            "q": "How many continents are there on Earth?",
            "options": ["5", "6", "7", "8"],
            "answer": "7",
            "fact": "The 7 continents are Africa, Antarctica, Asia, Australia, Europe, N.America & S.America."
        },
        {
            "q": "Which is the longest river in the world?",
            "options": ["Amazon", "Yangtze", "Mississippi", "Nile"],
            "answer": "Nile",
            "fact": "The Nile stretches approximately 6,650 km through northeastern Africa."
        },
        {
            "q": "In which country would you find the Great Wall?",
            "options": ["Japan", "China", "Mongolia", "India"],
            "answer": "China",
            "fact": "The Great Wall of China stretches over 21,000 km — longer than the distance from NY to Tokyo!"
        },
        {
            "q": "What is the national sport of India?",
            "options": ["Cricket", "Hockey", "Kabaddi", "Football"],
            "answer": "Hockey",
            "fact": "India's field hockey team won 8 Olympic gold medals — a record in the sport!"
        },
    ],
}

DIFFICULTY = {
    "Easy":   {"time": 30, "bonus": 10},
    "Medium": {"time": 20, "bonus": 20},
    "Hard":   {"time": 10, "bonus": 50},
}

# ── Timer bar ─────────────────────────────────────────────────────────────────
def countdown_bar(seconds, label="Time"):
    bar_len = 30
    for remaining in range(seconds, 0, -1):
        filled = int(bar_len * remaining / seconds)
        bar = "█" * filled + "░" * (bar_len - filled)
        color = C.GREEN if remaining > seconds * 0.5 else (C.YELLOW if remaining > seconds * 0.25 else C.RED)
        print(f"\r  {color}{label}: [{bar}] {remaining:2d}s{C.RESET}", end="", flush=True)
        time.sleep(1)
    print(f"\r  {C.RED}⏰ TIME'S UP!{' ' * 40}{C.RESET}")

# ── Ask a single question ─────────────────────────────────────────────────────
def ask_question(question_data, q_num, total, time_limit, bonus_pts):
    print(f"\n  {C.DIM}Question {q_num} of {total}{C.RESET}")
    print(f"\n  {C.WHITE}{C.BOLD}{question_data['q']}{C.RESET}\n")

    labels = ["A", "B", "C", "D"]
    options = question_data["options"][:]
    random.shuffle(options)
    answer_letter = labels[options.index(question_data["answer"])]

    for label, option in zip(labels, options):
        print(f"   {C.CYAN}[{label}]{C.RESET}  {option}")

    print()
    # Countdown in a thread so user can type simultaneously
    import threading
    timed_out = [False]

    def run_timer():
        countdown_bar(time_limit)
        timed_out[0] = True

    timer_thread = threading.Thread(target=run_timer, daemon=True)
    timer_thread.start()

    start = time.time()
    try:
        raw = input(f"\n  {C.YELLOW}Your answer (A/B/C/D): {C.RESET}").strip().upper()
    except EOFError:
        raw = ""

    elapsed = time.time() - start
    timer_thread.join(timeout=0)  # let thread die naturally

    if timed_out[0] or not raw:
        print(f"\n  {C.RED}✘  Time's up! The answer was {C.BOLD}{answer_letter}) {question_data['answer']}{C.RESET}")
        return 0, False

    if raw not in labels:
        print(f"\n  {C.RED}✘  Invalid choice. The answer was {C.BOLD}{answer_letter}) {question_data['answer']}{C.RESET}")
        return 0, False

    if raw == answer_letter:
        speed_bonus = max(0, int(bonus_pts * (1 - elapsed / time_limit)))
        total_pts = 10 + speed_bonus
        print(f"\n  {C.GREEN}{C.BOLD}✔  Correct!{C.RESET}  {C.GREEN}+{total_pts} pts (includes speed bonus!){C.RESET}")
        slow_print(f"  {C.DIM}💡 Fun fact: {question_data['fact']}{C.RESET}", 0.015)
        return total_pts, True
    else:
        print(f"\n  {C.RED}✘  Wrong! The correct answer was {C.BOLD}{answer_letter}) {question_data['answer']}{C.RESET}")
        slow_print(f"  {C.DIM}💡 Fun fact: {question_data['fact']}{C.RESET}", 0.015)
        return 0, False

# ── Score display ─────────────────────────────────────────────────────────────
def show_results(name, score, total_qs, correct, category, difficulty):
    clear()
    banner("  📊  QUIZ COMPLETE  📊  ", C.PURPLE)
    pct = int((correct / total_qs) * 100)

    if pct == 100:
        grade, msg = "S", f"{C.YELLOW}🏆 PERFECT SCORE! Absolutely brilliant!{C.RESET}"
    elif pct >= 80:
        grade, msg = "A", f"{C.GREEN}🌟 Excellent work, {name}!{C.RESET}"
    elif pct >= 60:
        grade, msg = "B", f"{C.CYAN}👍 Good job! Keep pushing!{C.RESET}"
    elif pct >= 40:
        grade, msg = "C", f"{C.YELLOW}📚 Not bad — practice makes perfect!{C.RESET}"
    else:
        grade, msg = "D", f"{C.RED}💪 Don't give up! Every expert was once a beginner.{C.RESET}"

    print(f"  Player    : {C.BOLD}{name}{C.RESET}")
    print(f"  Category  : {category}")
    print(f"  Difficulty: {difficulty}")
    print(f"  Score     : {C.BOLD}{C.CYAN}{score} pts{C.RESET}")
    print(f"  Correct   : {C.GREEN}{correct}{C.RESET} / {total_qs}  ({pct}%)")
    print(f"  Grade     : {C.BOLD}{grade}{C.RESET}\n")
    print(f"  {msg}\n")

    # ASCII bar chart
    bar = "█" * correct + "░" * (total_qs - correct)
    print(f"  Progress  : [{C.GREEN}{bar}{C.RESET}]\n")

# ── Main game loop ────────────────────────────────────────────────────────────
def main():
    clear()
    banner("🧠  BRAIN BUSTER QUIZ  🧠", C.CYAN)
    slow_print(f"  {C.DIM}Welcome to the ultimate knowledge challenge!{C.RESET}\n", 0.02)

    name = input(f"  {C.YELLOW}Enter your name: {C.RESET}").strip() or "Player"
    print(f"\n  {C.GREEN}Hey {name}! Let's test that big brain of yours. 🚀{C.RESET}\n")

    # Choose category
    cat_names = list(CATEGORIES.keys())
    print(f"  {C.BOLD}Choose a category:{C.RESET}")
    for i, cat in enumerate(cat_names, 1):
        print(f"   {C.CYAN}[{i}]{C.RESET}  {cat}")
    print(f"   {C.CYAN}[{len(cat_names)+1}]{C.RESET}  🎲 Random Mix")

    while True:
        choice = input(f"\n  {C.YELLOW}Your choice: {C.RESET}").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(cat_names) + 1:
            break
        print(f"  {C.RED}Please enter a valid number.{C.RESET}")

    choice = int(choice)
    if choice == len(cat_names) + 1:
        all_q = [q for qs in CATEGORIES.values() for q in qs]
        questions = random.sample(all_q, min(10, len(all_q)))
        cat_label = "🎲 Random Mix"
    else:
        cat_label = cat_names[choice - 1]
        questions = random.sample(CATEGORIES[cat_label], len(CATEGORIES[cat_label]))

    # Choose difficulty
    diff_names = list(DIFFICULTY.keys())
    print(f"\n  {C.BOLD}Choose difficulty:{C.RESET}")
    for i, d in enumerate(diff_names, 1):
        t = DIFFICULTY[d]["time"]
        b = DIFFICULTY[d]["bonus"]
        print(f"   {C.CYAN}[{i}]{C.RESET}  {d:8s}  ⏱ {t}s/question   ⭐ up to +{b} speed bonus")

    while True:
        dchoice = input(f"\n  {C.YELLOW}Your choice: {C.RESET}").strip()
        if dchoice.isdigit() and 1 <= int(dchoice) <= len(diff_names):
            break
        print(f"  {C.RED}Please enter a valid number.{C.RESET}")

    diff_label = diff_names[int(dchoice) - 1]
    time_limit = DIFFICULTY[diff_label]["time"]
    bonus_pts  = DIFFICULTY[diff_label]["bonus"]

    # Play!
    total_score = 0
    correct_count = 0

    for i, q in enumerate(questions, 1):
        clear()
        banner(f" {cat_label}  ·  {diff_label}  ·  {total_score} pts ", C.PURPLE)
        pts, correct = ask_question(q, i, len(questions), time_limit, bonus_pts)
        total_score += pts
        if correct:
            correct_count += 1
        input(f"\n  {C.DIM}Press Enter to continue...{C.RESET}")

    clear()
    show_results(name, total_score, len(questions), correct_count, cat_label, diff_label)

    play_again = input(f"  {C.YELLOW}Play again? (y/n): {C.RESET}").strip().lower()
    if play_again == "y":
        main()
    else:
        slow_print(f"\n  {C.CYAN}Thanks for playing, {name}! Keep learning every day. 👋{C.RESET}\n", 0.02)

if __name__ == "__main__":
    main()
