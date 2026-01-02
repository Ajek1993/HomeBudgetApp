import json
import sys
import shutil
from pathlib import Path
from decimal import Decimal
from datetime import date, datetime
import argparse

# === CONSTANTS ===
DATA_FILE = "data/data.json"

# === STORAGE ===

def create_empty_data():
    """Create initial empty data structure"""
    return {
        "limit": 5000,
        "transactions": [],
        "fixed_costs": []
    }

def load_data(path):
    """Load data from JSON file, create if doesn't exist"""
    # Step 1-2: Check if file exists, if not create empty data
    if not Path(path).exists():
        # Step 3: Create empty data
        data = create_empty_data()
        # Step 4: Save to file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        # Step 5: Return created dict
        return data

    # Step 6-7: File exists, try to read it
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    # Step 8-10: Handle corrupted JSON
    except json.JSONDecodeError:
        print(f"BŁĄD: Plik {path} jest uszkodzony (nieprawidłowy JSON).")
        print(f"Sprawdź składnię lub przywróć z backupu: {path}.bak")
        print("Nie próbowano nadpisać pliku.")
        sys.exit(1)

    # Step 11-13: Validate structure
    if not all(k in data for k in ["limit", "transactions", "fixed_costs"]):
        print(f"BŁĄD: Plik {path} ma nieprawidłową strukturę.")
        print("Wymagane pola: limit, transactions, fixed_costs")
        print(f"Sprawdź plik lub przywróć z backupu: {path}.bak")
        sys.exit(1)

    # Step 14: Return data
    return data

def save_data(data, path):
    """Save data to JSON file with backup"""
    # Step 1-2: Create backup if file exists
    if Path(path).exists():
        shutil.copy2(path, str(path) + '.bak')

    # Step 3-4: Try to save file
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    # Step 5-7: Handle permission errors
    except PermissionError:
        print(f"BŁĄD: Nie można zapisać do pliku {path}")
        print("Plik jest otwarty w innym programie. Zamknij edytor i spróbuj ponownie.")
        sys.exit(1)

# === VALIDATION ===

def validate_amount(value):
    """Validate amount is a positive number"""
    try:
        amount = float(value)
        if amount <= 0:
            print("BŁĄD: Kwota musi być większa od 0")
            print(f"Podano: {value}")
            sys.exit(1)
        return amount
    except ValueError:
        print("BŁĄD: Kwota musi być liczbą (np. 50.00 lub 50)")
        print(f"Podano: {value}")
        sys.exit(1)

def validate_string(value, field_name):
    """Validate string is not empty"""
    if not value or not value.strip():
        print(f"BŁĄD: {field_name} nie może być pusta(y)")
        sys.exit(1)
    return value.strip()

def validate_date(value):
    """Validate date is in YYYY-MM-DD format, default to today"""
    if value is None:
        return date.today().isoformat()
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        print("BŁĄD: Data musi być w formacie YYYY-MM-DD (np. 2025-11-24)")
        print(f"Podano: {value}")
        sys.exit(1)

# === TRANSACTIONS ===

def get_current_month():
    """Get current month in YYYY-MM format"""
    return date.today().strftime("%Y-%m")

def filter_by_month(transactions, month_str):
    """Filter transactions by month (YYYY-MM)"""
    filtered = []
    for t in transactions:
        try:
            if t["date"].startswith(month_str):
                filtered.append(t)
        except (KeyError, AttributeError):
            # Skip transactions with invalid dates
            pass
    return filtered

def calculate_total(transactions):
    """Calculate total amount from transactions"""
    total = Decimal(0)
    for t in transactions:
        total += Decimal(str(t["amount"]))
    return total

def add_transaction(data, amount, category, description, transaction_date):
    """Add a transaction to data"""
    transaction = {
        "date": transaction_date,
        "amount": amount,
        "category": category,
        "description": description
    }
    data["transactions"].append(transaction)

def group_by_category(transactions):
    """Group transactions by category and sum amounts"""
    grouped = {}
    for t in transactions:
        cat = t["category"]
        grouped[cat] = grouped.get(cat, Decimal(0)) + Decimal(str(t["amount"]))
    return grouped

# === DISPLAY ===

def format_status(limit, spent, remaining, month):
    """Format status output"""
    return f"""Limit: {limit:.2f} PLN
Wydano ({month}): {spent:.2f} PLN
Pozostało: {remaining:.2f} PLN"""

def format_category_list(grouped):
    """Format category list output"""
    if not grouped:
        return "Brak transakcji w tym miesiącu"
    sorted_cats = sorted(grouped.keys())
    lines = [f"{cat}: {grouped[cat]:.2f} PLN" for cat in sorted_cats]
    return "\n".join(lines)

# === FIXED COSTS ===

def apply_fixed_costs(data):
    """Apply fixed costs as transactions with today's date"""
    if not data.get("fixed_costs"):
        print("Brak kosztów stałych do dodania")
        return (0, 0)

    count = 0
    total_amount = Decimal(0)

    for fixed_cost in data["fixed_costs"]:
        transaction = {
            "date": date.today().isoformat(),
            "amount": fixed_cost["amount"],
            "category": fixed_cost["category"],
            "description": fixed_cost["description"]
        }
        data["transactions"].append(transaction)
        count += 1
        total_amount += Decimal(str(fixed_cost["amount"]))

    return (count, total_amount)

# === MAIN ===

if __name__ == "__main__":
    # Setup argparse
    parser = argparse.ArgumentParser(description="Budget CLI - Prosty system zarządzania budżetem domowym")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Status subcommand
    status_parser = subparsers.add_parser('status', help='Sprawdź stan budżetu')

    # Add subcommand
    add_parser = subparsers.add_parser('add', help='Dodaj transakcję')
    add_parser.add_argument('--amount', required=True, help='Kwota')
    add_parser.add_argument('--category', required=True, help='Kategoria')
    add_parser.add_argument('--description', required=True, help='Opis')
    add_parser.add_argument('--date', required=False, default=None, help='Data (YYYY-MM-DD), domyślnie dziś')

    # Apply-fixed subcommand
    fixed_parser = subparsers.add_parser('apply-fixed', help='Dodaj koszty stałe')

    # List subcommand
    list_parser = subparsers.add_parser('list', help='Pokaż wydatki po kategoriach')

    # Parse arguments
    args = parser.parse_args()

    # Handle status command
    if args.command == 'status':
        data = load_data(DATA_FILE)
        month = get_current_month()
        current_month_transactions = filter_by_month(data["transactions"], month)
        spent = calculate_total(current_month_transactions)
        remaining = Decimal(str(data["limit"])) - spent
        output = format_status(data["limit"], spent, remaining, month)
        print(output)

    # Handle add command
    elif args.command == 'add':
        amount = validate_amount(args.amount)
        category = validate_string(args.category, "Kategoria")
        description = validate_string(args.description, "Opis")
        transaction_date = validate_date(args.date)
        data = load_data(DATA_FILE)
        add_transaction(data, amount, category, description, transaction_date)
        save_data(data, DATA_FILE)
        print(f"Dodano {amount} PLN ({category})")

    # Handle apply-fixed command
    elif args.command == 'apply-fixed':
        data = load_data(DATA_FILE)
        count, total = apply_fixed_costs(data)
        if count > 0:
            save_data(data, DATA_FILE)
            print(f"Dodano {count} kosztów stałych ({total:.2f} PLN)")

    # Handle list command
    elif args.command == 'list':
        data = load_data(DATA_FILE)
        month = get_current_month()
        current_month_transactions = filter_by_month(data["transactions"], month)
        grouped = group_by_category(current_month_transactions)
        output = format_category_list(grouped)
        print(output)
