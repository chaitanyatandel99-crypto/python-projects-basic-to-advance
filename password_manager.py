"""
╔══════════════════════════════════════════════════════════════╗
║               🔐  VAULT — PASSWORD MANAGER  🔐              ║
║             Because your passwords deserve better            ║
║                     by Chaitanya Tandel                      ║
╚══════════════════════════════════════════════════════════════╝

Features:
  • AES-style XOR encryption with a master password
  • Add, view, search, edit, delete passwords
  • Password strength checker
  • Random strong password generator
  • Clipboard copy (optional)
  • All data stored locally in an encrypted JSON vault
"""

import os
import sys
import json
import time
import random
import string
import hashlib
import getpass
import base64

# ── Colour helpers ────────────────────────────────────────────────────────────
def supports_color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

class C:
    R = "\033[0m"    if supports_color() else ""
    BOLD = "\033[1m" if supports_color() else ""
    RED  = "\033[91m" if supports_color() else ""
    GRN  = "\033[92m" if supports_color() else ""
    YLW  = "\033[93m" if supports_color() else ""
    CYN  = "\033[96m" if supports_color() else ""
    PUR  = "\033[95m" if supports_color() else ""
    DIM  = "\033[2m"  if supports_color() else ""
    WHT  = "\033[97m" if supports_color() else ""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def slow_print(text, delay=0.018):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def banner():
    clear()
    print(f"\n{C.CYN}{C.BOLD}{'═'*58}")
    print("   🔐  V A U L T  —  Your Personal Password Manager")
    print(f"{'═'*58}{C.R}\n")

def divider(color=C.DIM):
    print(f"{color}{'─'*58}{C.R}")

# ── Encryption (XOR + SHA-256 key) ───────────────────────────────────────────
def derive_key(master_password: str) -> bytes:
    """Derive a 32-byte key from the master password using SHA-256."""
    return hashlib.sha256(master_password.encode()).digest()

def xor_encrypt(data: str, key: bytes) -> str:
    """XOR-encrypt a string and return base64-encoded ciphertext."""
    data_bytes = data.encode("utf-8")
    key_stream = (key[i % len(key)] for i in range(len(data_bytes)))
    encrypted = bytes(b ^ k for b, k in zip(data_bytes, key_stream))
    return base64.b64encode(encrypted).decode("utf-8")

def xor_decrypt(ciphertext: str, key: bytes) -> str:
    """Decode base64 and XOR-decrypt back to plaintext."""
    encrypted = base64.b64decode(ciphertext.encode("utf-8"))
    key_stream = (key[i % len(key)] for i in range(len(encrypted)))
    decrypted = bytes(b ^ k for b, k in zip(encrypted, key_stream))
    return decrypted.decode("utf-8")

def hash_master(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ── Vault file I/O ────────────────────────────────────────────────────────────
VAULT_FILE = "vault.json"

def load_vault():
    if not os.path.exists(VAULT_FILE):
        return {}
    with open(VAULT_FILE, "r") as f:
        return json.load(f)

def save_vault(data: dict):
    with open(VAULT_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Master password setup / unlock ───────────────────────────────────────────
def setup_master_password() -> str:
    slow_print(f"\n  {C.YLW}Welcome! Let's set up your Vault.{C.R}\n", 0.02)
    while True:
        pw  = getpass.getpass(f"  {C.CYN}Create a master password: {C.R}")
        pw2 = getpass.getpass(f"  {C.CYN}Confirm master password : {C.R}")
        if pw != pw2:
            print(f"  {C.RED}Passwords don't match. Try again.{C.R}")
        elif len(pw) < 6:
            print(f"  {C.RED}Please use at least 6 characters.{C.R}")
        else:
            print(f"\n  {C.GRN}✔  Vault created successfully!{C.R}")
            return pw

def unlock_vault() -> tuple[dict, str]:
    """Load vault, ask for master password, verify it, return (vault, key_bytes)."""
    vault = load_vault()
    if "master_hash" not in vault:
        master_pw = setup_master_password()
        vault["master_hash"] = hash_master(master_pw)
        vault["entries"] = []
        save_vault(vault)
    else:
        for attempt in range(3):
            master_pw = getpass.getpass(f"\n  {C.CYN}🔑 Enter master password: {C.R}")
            if hash_master(master_pw) == vault["master_hash"]:
                break
            remaining = 2 - attempt
            if remaining > 0:
                print(f"  {C.RED}Wrong password. {remaining} attempt(s) left.{C.R}")
            else:
                print(f"  {C.RED}Too many failed attempts. Vault locked.{C.R}")
                sys.exit(1)
        print(f"  {C.GRN}✔  Vault unlocked!{C.R}")

    key = derive_key(master_pw)
    return vault, key

# ── Password strength checker ─────────────────────────────────────────────────
def check_strength(pw: str) -> tuple[str, str]:
    score = 0
    if len(pw) >= 8:  score += 1
    if len(pw) >= 12: score += 1
    if any(c.isupper() for c in pw): score += 1
    if any(c.islower() for c in pw): score += 1
    if any(c.isdigit() for c in pw): score += 1
    if any(c in string.punctuation for c in pw): score += 1

    if score <= 2:   return "Weak",   C.RED
    if score <= 4:   return "Medium", C.YLW
    return "Strong", C.GRN

def strength_bar(pw: str) -> str:
    label, color = check_strength(pw)
    bars = {"Weak": 2, "Medium": 4, "Strong": 6}
    filled = bars[label]
    bar = "█" * filled + "░" * (6 - filled)
    return f"{color}[{bar}] {label}{C.R}"

# ── Random password generator ─────────────────────────────────────────────────
def generate_password(length=16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    # Guarantee at least one of each type
    pw = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*()"),
    ]
    pw += [random.choice(alphabet) for _ in range(length - 4)]
    random.shuffle(pw)
    return "".join(pw)

# ── CRUD operations ───────────────────────────────────────────────────────────
def add_entry(vault: dict, key: bytes):
    divider()
    print(f"\n  {C.BOLD}➕  Add New Entry{C.R}\n")

    site  = input(f"  {C.CYN}Website / App name : {C.R}").strip()
    uname = input(f"  {C.CYN}Username / Email   : {C.R}").strip()

    print(f"\n  {C.DIM}Leave blank to generate a strong password automatically.{C.R}")
    pw_raw = getpass.getpass(f"  {C.CYN}Password           : {C.R}")

    if not pw_raw:
        pw_raw = generate_password()
        print(f"  {C.GRN}✔  Generated: {C.BOLD}{pw_raw}{C.R}")

    label, _ = check_strength(pw_raw)
    print(f"  Strength : {strength_bar(pw_raw)}")

    notes = input(f"  {C.CYN}Notes (optional)   : {C.R}").strip()

    if not site or not uname:
        print(f"  {C.RED}Site and username are required.{C.R}")
        return

    entry = {
        "id":       len(vault["entries"]) + 1,
        "site":     xor_encrypt(site,  key),
        "username": xor_encrypt(uname, key),
        "password": xor_encrypt(pw_raw, key),
        "notes":    xor_encrypt(notes, key),
        "added":    time.strftime("%Y-%m-%d"),
    }
    vault["entries"].append(entry)
    save_vault(vault)
    print(f"\n  {C.GRN}✔  Entry saved successfully!{C.R}")

def list_entries(vault: dict, key: bytes, filter_term="") -> list:
    entries = vault.get("entries", [])
    results = []
    for e in entries:
        site = xor_decrypt(e["site"], key)
        uname = xor_decrypt(e["username"], key)
        if filter_term.lower() in site.lower() or filter_term.lower() in uname.lower():
            results.append((e, site, uname))
    return results

def view_entries(vault: dict, key: bytes, search=""):
    divider()
    results = list_entries(vault, key, search)
    if not results:
        print(f"\n  {C.YLW}No entries found.{C.R}")
        return

    title = f"  {C.BOLD}🔍 Search: '{search}'{C.R}" if search else f"  {C.BOLD}📋 All Entries ({len(results)}){C.R}"
    print(f"\n{title}\n")
    print(f"  {'#':<4} {'Site/App':<22} {'Username':<25} {'Added'}")
    divider()
    for i, (e, site, uname) in enumerate(results, 1):
        print(f"  {C.CYN}{i:<4}{C.R} {C.WHT}{site:<22}{C.R} {uname:<25} {C.DIM}{e['added']}{C.R}")

def reveal_entry(vault: dict, key: bytes):
    view_entries(vault, key)
    if not vault.get("entries"):
        return
    try:
        idx = int(input(f"\n  {C.YLW}Enter entry number to reveal: {C.R}")) - 1
        results = list_entries(vault, key)
        if idx < 0 or idx >= len(results):
            print(f"  {C.RED}Invalid number.{C.R}")
            return
        e, site, uname = results[idx]
        pw    = xor_decrypt(e["password"], key)
        notes = xor_decrypt(e["notes"], key)

        divider()
        print(f"\n  {C.BOLD}🔎 Entry Details{C.R}\n")
        print(f"  Site     : {C.WHT}{C.BOLD}{site}{C.R}")
        print(f"  Username : {C.CYN}{uname}{C.R}")
        print(f"  Password : {C.GRN}{C.BOLD}{pw}{C.R}  {strength_bar(pw)}")
        if notes:
            print(f"  Notes    : {C.DIM}{notes}{C.R}")
        print(f"  Added    : {C.DIM}{e['added']}{C.R}")

        # Optional clipboard copy
        try:
            import subprocess
            if os.name == "nt":
                subprocess.run("clip", input=pw.encode(), check=True)
            else:
                subprocess.run(["xclip", "-selection", "clipboard"],
                               input=pw.encode(), check=True)
            print(f"\n  {C.GRN}📋 Password copied to clipboard!{C.R}")
        except Exception:
            pass  # clipboard not available — silently skip

    except ValueError:
        print(f"  {C.RED}Please enter a valid number.{C.R}")

def delete_entry(vault: dict, key: bytes):
    view_entries(vault, key)
    if not vault.get("entries"):
        return
    try:
        idx = int(input(f"\n  {C.YLW}Enter entry number to DELETE: {C.R}")) - 1
        results = list_entries(vault, key)
        if idx < 0 or idx >= len(results):
            print(f"  {C.RED}Invalid number.{C.R}")
            return
        e, site, _ = results[idx]
        confirm = input(f"  {C.RED}Delete '{site}'? This cannot be undone. (yes/no): {C.R}").strip().lower()
        if confirm == "yes":
            vault["entries"].remove(e)
            save_vault(vault)
            print(f"  {C.GRN}✔  Entry deleted.{C.R}")
        else:
            print(f"  {C.DIM}Cancelled.{C.R}")
    except ValueError:
        print(f"  {C.RED}Please enter a valid number.{C.R}")

def generate_menu():
    divider()
    print(f"\n  {C.BOLD}🎲 Password Generator{C.R}\n")
    try:
        length = int(input(f"  {C.CYN}Length (default 16): {C.R}") or 16)
    except ValueError:
        length = 16
    pw = generate_password(max(8, min(64, length)))
    print(f"\n  {C.GRN}{C.BOLD}  {pw}{C.R}")
    print(f"  Strength : {strength_bar(pw)}")

def change_master(vault: dict, key: bytes):
    old = getpass.getpass(f"\n  {C.CYN}Current master password: {C.R}")
    if hash_master(old) != vault["master_hash"]:
        print(f"  {C.RED}Wrong password.{C.R}")
        return key
    while True:
        new1 = getpass.getpass(f"  {C.CYN}New master password    : {C.R}")
        new2 = getpass.getpass(f"  {C.CYN}Confirm new password   : {C.R}")
        if new1 != new2:
            print(f"  {C.RED}Passwords don't match.{C.R}")
        elif len(new1) < 6:
            print(f"  {C.RED}Must be at least 6 characters.{C.R}")
        else:
            break

    old_key = derive_key(old)
    new_key = derive_key(new1)

    # Re-encrypt all entries with the new key
    for e in vault.get("entries", []):
        for field in ("site", "username", "password", "notes"):
            plain = xor_decrypt(e[field], old_key)
            e[field] = xor_encrypt(plain, new_key)

    vault["master_hash"] = hash_master(new1)
    save_vault(vault)
    print(f"  {C.GRN}✔  Master password changed and vault re-encrypted!{C.R}")
    return new_key

# ── Main menu ─────────────────────────────────────────────────────────────────
def main_menu(vault: dict, key: bytes):
    count = len(vault.get("entries", []))
    banner()
    print(f"  {C.DIM}Vault: {VAULT_FILE}  ·  {count} entries stored{C.R}\n")
    options = [
        ("1", "➕  Add new entry"),
        ("2", "📋  View all entries"),
        ("3", "🔍  Search entries"),
        ("4", "👁   Reveal a password"),
        ("5", "🗑   Delete an entry"),
        ("6", "🎲  Generate strong password"),
        ("7", "🔑  Change master password"),
        ("0", "🚪  Lock & exit"),
    ]
    for key_opt, label in options:
        print(f"  {C.CYN}[{key_opt}]{C.R}  {label}")
    print()
    return input(f"  {C.YLW}Choose an option: {C.R}").strip()

def main():
    banner()
    vault, enc_key = unlock_vault()
    time.sleep(0.5)

    while True:
        choice = main_menu(vault, enc_key)

        if   choice == "1": add_entry(vault, enc_key)
        elif choice == "2": view_entries(vault, enc_key)
        elif choice == "3":
            term = input(f"  {C.CYN}Search term: {C.R}").strip()
            view_entries(vault, enc_key, search=term)
        elif choice == "4": reveal_entry(vault, enc_key)
        elif choice == "5": delete_entry(vault, enc_key)
        elif choice == "6": generate_menu()
        elif choice == "7": enc_key = change_master(vault, enc_key)
        elif choice == "0":
            slow_print(f"\n  {C.CYN}🔒 Vault locked. Stay safe out there!{C.R}\n", 0.02)
            break
        else:
            print(f"  {C.RED}Invalid option.{C.R}")

        input(f"\n  {C.DIM}Press Enter to return to menu...{C.R}")

if __name__ == "__main__":
    main()
