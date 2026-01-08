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
        "limits": {
            "default": 5000
        },
        "auto_apply_fixed_costs": True,
        "applied_fixed_costs_months": [],
        "next_transaction_id": 1,
        "transactions": [],
        "next_fixed_cost_id": 1,
        "fixed_costs": []
    }

def migrate_data(data):
    """Migrate old data structure to new format"""
    migrated = False

    # Migrate limit to limits
    if "limit" in data and "limits" not in data:
        data["limits"] = {
            "default": data["limit"]
        }
        del data["limit"]
        migrated = True

    # Ensure limits structure exists
    if "limits" not in data:
        data["limits"] = {"default": 5000}
        migrated = True

    # Add auto_apply_fixed_costs if missing
    if "auto_apply_fixed_costs" not in data:
        data["auto_apply_fixed_costs"] = True
        migrated = True

    # Add applied_fixed_costs_months if missing
    if "applied_fixed_costs_months" not in data:
        data["applied_fixed_costs_months"] = []
        migrated = True

    # Add IDs to transactions
    if "next_transaction_id" not in data:
        next_id = 1
        for transaction in data.get("transactions", []):
            if "id" not in transaction:
                transaction["id"] = next_id
                next_id += 1
        data["next_transaction_id"] = next_id
        migrated = True

    # Add IDs to fixed costs
    if "next_fixed_cost_id" not in data:
        next_id = 1
        for fixed_cost in data.get("fixed_costs", []):
            if "id" not in fixed_cost:
                fixed_cost["id"] = next_id
                next_id += 1
        data["next_fixed_cost_id"] = next_id
        migrated = True

    return migrated

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

    # Step 11-13: Validate basic structure
    if "transactions" not in data or "fixed_costs" not in data:
        print(f"BŁĄD: Plik {path} ma nieprawidłową strukturę.")
        print("Wymagane pola: transactions, fixed_costs")
        print(f"Sprawdź plik lub przywróć z backupu: {path}.bak")
        sys.exit(1)

    # Step 14: Migrate data if needed
    migrated = migrate_data(data)
    if migrated:
        print("Migracja struktury danych do nowego formatu...")
        save_data(data, path)
        print("Migracja zakończona. Dane zostały zaktualizowane.")

    # Step 15: Auto-apply fixed costs if needed
    count, total = auto_apply_fixed_if_needed(data)
    if count > 0:
        save_data(data, path)
        print(f"Automatycznie dodano {count} kosztów stałych ({total:.2f} PLN) dla bieżącego miesiąca")

    # Step 16: Return data
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

def get_limit_for_month(data, month_str):
    """Get limit for a specific month, fallback to default"""
    limits = data.get("limits", {})
    if month_str in limits:
        return limits[month_str]
    return limits.get("default", 5000)

def set_limit(data, amount, month_str=None):
    """Set limit for a specific month or default"""
    if "limits" not in data:
        data["limits"] = {}

    if month_str is None:
        data["limits"]["default"] = amount
    else:
        data["limits"][month_str] = amount

def format_limits_list(limits):
    """Format limits list output"""
    if not limits:
        return "Brak ustawionych limitów"

    lines = []
    lines.append(f"{'Miesiąc':<15} {'Limit':<15}")
    lines.append("-" * 30)

    # Show default first
    if "default" in limits:
        lines.append(f"{'default':<15} {limits['default']:.2f} PLN")

    # Show month-specific limits sorted
    month_limits = {k: v for k, v in limits.items() if k != "default"}
    for month in sorted(month_limits.keys()):
        lines.append(f"{month:<15} {month_limits[month]:.2f} PLN")

    return "\n".join(lines)

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
        "id": data["next_transaction_id"],
        "date": transaction_date,
        "amount": amount,
        "category": category,
        "description": description
    }
    data["transactions"].append(transaction)
    data["next_transaction_id"] += 1

def group_by_category(transactions):
    """Group transactions by category and sum amounts"""
    grouped = {}
    for t in transactions:
        cat = t["category"]
        grouped[cat] = grouped.get(cat, Decimal(0)) + Decimal(str(t["amount"]))
    return grouped

def find_transaction_by_id(data, transaction_id):
    """Find transaction by ID, return None if not found"""
    for transaction in data["transactions"]:
        if transaction.get("id") == transaction_id:
            return transaction
    return None

def edit_transaction(data, transaction_id, **kwargs):
    """Edit transaction fields"""
    transaction = find_transaction_by_id(data, transaction_id)
    if not transaction:
        print(f"BŁĄD: Nie znaleziono transakcji o ID {transaction_id}")
        sys.exit(1)

    # Update allowed fields
    if "amount" in kwargs and kwargs["amount"] is not None:
        transaction["amount"] = validate_amount(kwargs["amount"])
    if "category" in kwargs and kwargs["category"] is not None:
        transaction["category"] = validate_string(kwargs["category"], "Kategoria")
    if "description" in kwargs and kwargs["description"] is not None:
        transaction["description"] = validate_string(kwargs["description"], "Opis")
    if "date" in kwargs and kwargs["date"] is not None:
        transaction["date"] = validate_date(kwargs["date"])

    return transaction

def delete_transaction(data, transaction_id):
    """Delete transaction by ID"""
    transaction = find_transaction_by_id(data, transaction_id)
    if not transaction:
        print(f"BŁĄD: Nie znaleziono transakcji o ID {transaction_id}")
        sys.exit(1)

    data["transactions"].remove(transaction)
    return transaction

def format_transactions_list(transactions):
    """Format list of transactions with IDs"""
    if not transactions:
        return "Brak transakcji w tym miesiącu"

    lines = []
    lines.append(f"{'ID':<5} {'Data':<12} {'Kwota':<10} {'Kategoria':<20} Opis")
    lines.append("-" * 80)

    for t in transactions:
        tid = t.get("id", "?")
        date_str = t.get("date", "")
        amount = f"{t.get('amount', 0):.2f} PLN"
        category = t.get("category", "")
        description = t.get("description", "")
        lines.append(f"{tid:<5} {date_str:<12} {amount:<10} {category:<20} {description}")

    return "\n".join(lines)

# === DISPLAY ===

def calculate_detailed_status(limit, spent, month):
    """Calculate detailed budget information"""
    from calendar import monthrange

    # Parse month
    year, month_num = map(int, month.split("-"))
    current_date = date.today()

    # Get days in month
    days_in_month = monthrange(year, month_num)[1]

    # Calculate days elapsed and remaining
    if year == current_date.year and month_num == current_date.month:
        days_elapsed = current_date.day
    elif year < current_date.year or (year == current_date.year and month_num < current_date.month):
        days_elapsed = days_in_month  # Past month
    else:
        days_elapsed = 0  # Future month

    days_remaining = max(0, days_in_month - days_elapsed)

    # Calculate averages
    avg_daily = float(spent) / days_elapsed if days_elapsed > 0 else 0
    remaining_budget = float(limit) - float(spent)
    suggested_daily = remaining_budget / days_remaining if days_remaining > 0 else 0

    return {
        "days_in_month": days_in_month,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "avg_daily": avg_daily,
        "suggested_daily": suggested_daily,
        "remaining": remaining_budget
    }

def format_detailed_status(limit, spent, month, details):
    """Format detailed status output"""
    remaining = details["remaining"]
    percent_spent = (float(spent) / float(limit) * 100) if limit > 0 else 0

    output = f"""=== BUDŻET - {month.upper()} ===
Limit: {limit:.2f} PLN
Wydano: {spent:.2f} PLN ({percent_spent:.0f}%)
Pozostało: {remaining:.2f} PLN ({100-percent_spent:.0f}%)

Dni w miesiącu: {details['days_in_month']}
Upłynęło dni: {details['days_elapsed']}
Pozostało dni: {details['days_remaining']}

Średnie wydatki dziennie: {details['avg_daily']:.2f} PLN
Sugerowany budżet dzienny (pozostałe dni): {details['suggested_daily']:.2f} PLN"""

    return output

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

def apply_fixed_costs(data, month_str=None):
    """Apply fixed costs as transactions for the first day of the month"""
    if not data.get("fixed_costs"):
        print("Brak kosztów stałych do dodania")
        return (0, 0)

    # Use current month if not specified
    if month_str is None:
        month_str = get_current_month()

    # Check if already applied for this month
    if month_str in data.get("applied_fixed_costs_months", []):
        print(f"Koszty stałe dla {month_str} zostały już dodane")
        return (0, 0)

    # Create date for first day of month
    first_day = f"{month_str}-01"

    count = 0
    total_amount = Decimal(0)

    for fixed_cost in data["fixed_costs"]:
        transaction = {
            "id": data["next_transaction_id"],
            "date": first_day,
            "amount": fixed_cost["amount"],
            "category": fixed_cost["category"],
            "description": fixed_cost["description"]
        }
        data["transactions"].append(transaction)
        data["next_transaction_id"] += 1
        count += 1
        total_amount += Decimal(str(fixed_cost["amount"]))

    # Mark month as applied
    if "applied_fixed_costs_months" not in data:
        data["applied_fixed_costs_months"] = []
    data["applied_fixed_costs_months"].append(month_str)

    return (count, total_amount)

def auto_apply_fixed_if_needed(data):
    """Automatically apply fixed costs if not yet applied for current month"""
    if not data.get("auto_apply_fixed_costs", True):
        return (0, 0)

    month_str = get_current_month()
    if month_str in data.get("applied_fixed_costs_months", []):
        return (0, 0)

    return apply_fixed_costs(data, month_str)

def add_fixed_cost(data, amount, category, description):
    """Add a new fixed cost"""
    fixed_cost = {
        "id": data["next_fixed_cost_id"],
        "amount": amount,
        "category": category,
        "description": description
    }
    data["fixed_costs"].append(fixed_cost)
    data["next_fixed_cost_id"] += 1
    return fixed_cost

def find_fixed_cost_by_id(data, fixed_cost_id):
    """Find fixed cost by ID, return None if not found"""
    for fixed_cost in data["fixed_costs"]:
        if fixed_cost.get("id") == fixed_cost_id:
            return fixed_cost
    return None

def edit_fixed_cost(data, fixed_cost_id, **kwargs):
    """Edit fixed cost fields"""
    fixed_cost = find_fixed_cost_by_id(data, fixed_cost_id)
    if not fixed_cost:
        print(f"BŁĄD: Nie znaleziono kosztu stałego o ID {fixed_cost_id}")
        sys.exit(1)

    # Update allowed fields
    if "amount" in kwargs and kwargs["amount"] is not None:
        fixed_cost["amount"] = validate_amount(kwargs["amount"])
    if "category" in kwargs and kwargs["category"] is not None:
        fixed_cost["category"] = validate_string(kwargs["category"], "Kategoria")
    if "description" in kwargs and kwargs["description"] is not None:
        fixed_cost["description"] = validate_string(kwargs["description"], "Opis")

    return fixed_cost

def delete_fixed_cost(data, fixed_cost_id):
    """Delete fixed cost by ID"""
    fixed_cost = find_fixed_cost_by_id(data, fixed_cost_id)
    if not fixed_cost:
        print(f"BŁĄD: Nie znaleziono kosztu stałego o ID {fixed_cost_id}")
        sys.exit(1)

    data["fixed_costs"].remove(fixed_cost)
    return fixed_cost

def format_fixed_costs_list(fixed_costs):
    """Format list of fixed costs with IDs"""
    if not fixed_costs:
        return "Brak kosztów stałych"

    lines = []
    lines.append(f"{'ID':<5} {'Kwota':<15} {'Kategoria':<20} Opis")
    lines.append("-" * 70)

    for fc in fixed_costs:
        fid = fc.get("id", "?")
        amount = f"{fc.get('amount', 0):.2f} PLN"
        category = fc.get("category", "")
        description = fc.get("description", "")
        lines.append(f"{fid:<5} {amount:<15} {category:<20} {description}")

    return "\n".join(lines)

# === MAIN ===

if __name__ == "__main__":
    # Setup argparse
    parser = argparse.ArgumentParser(description="Budget CLI - Prosty system zarządzania budżetem domowym")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Status subcommand
    status_parser = subparsers.add_parser('status', help='Sprawdź stan budżetu')
    status_parser.add_argument('--detailed', action='store_true', help='Pokaż szczegółowe informacje')

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

    # Transactions subcommand
    transactions_parser = subparsers.add_parser('transactions', help='Pokaż listę transakcji')
    transactions_parser.add_argument('--month', required=False, default=None, help='Miesiąc (YYYY-MM), domyślnie bieżący')

    # Edit subcommand
    edit_parser = subparsers.add_parser('edit', help='Edytuj transakcję')
    edit_parser.add_argument('transaction_id', type=int, help='ID transakcji')
    edit_parser.add_argument('--amount', required=False, default=None, help='Nowa kwota')
    edit_parser.add_argument('--category', required=False, default=None, help='Nowa kategoria')
    edit_parser.add_argument('--description', required=False, default=None, help='Nowy opis')
    edit_parser.add_argument('--date', required=False, default=None, help='Nowa data (YYYY-MM-DD)')

    # Delete subcommand
    delete_parser = subparsers.add_parser('delete', help='Usuń transakcję')
    delete_parser.add_argument('transaction_id', type=int, help='ID transakcji')

    # Set-limit subcommand
    set_limit_parser = subparsers.add_parser('set-limit', help='Ustaw limit budżetu')
    set_limit_parser.add_argument('amount', type=float, help='Kwota limitu')
    set_limit_parser.add_argument('--month', required=False, default=None, help='Miesiąc (YYYY-MM), brak = default')

    # Limits subcommand
    limits_parser = subparsers.add_parser('limits', help='Pokaż historię limitów')

    # Fixed-list subcommand
    fixed_list_parser = subparsers.add_parser('fixed-list', help='Pokaż listę kosztów stałych')

    # Fixed-add subcommand
    fixed_add_parser = subparsers.add_parser('fixed-add', help='Dodaj nowy koszt stały')
    fixed_add_parser.add_argument('--amount', required=True, help='Kwota')
    fixed_add_parser.add_argument('--category', required=True, help='Kategoria')
    fixed_add_parser.add_argument('--description', required=True, help='Opis')

    # Fixed-edit subcommand
    fixed_edit_parser = subparsers.add_parser('fixed-edit', help='Edytuj koszt stały')
    fixed_edit_parser.add_argument('fixed_cost_id', type=int, help='ID kosztu stałego')
    fixed_edit_parser.add_argument('--amount', required=False, default=None, help='Nowa kwota')
    fixed_edit_parser.add_argument('--category', required=False, default=None, help='Nowa kategoria')
    fixed_edit_parser.add_argument('--description', required=False, default=None, help='Nowy opis')

    # Fixed-delete subcommand
    fixed_delete_parser = subparsers.add_parser('fixed-delete', help='Usuń koszt stały')
    fixed_delete_parser.add_argument('fixed_cost_id', type=int, help='ID kosztu stałego')

    # Parse arguments
    args = parser.parse_args()

    # Handle status command
    if args.command == 'status':
        data = load_data(DATA_FILE)
        month = get_current_month()
        current_month_transactions = filter_by_month(data["transactions"], month)
        spent = calculate_total(current_month_transactions)
        limit = get_limit_for_month(data, month)
        remaining = Decimal(str(limit)) - spent

        if args.detailed:
            details = calculate_detailed_status(limit, spent, month)
            output = format_detailed_status(limit, spent, month, details)
        else:
            output = format_status(limit, spent, remaining, month)

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

    # Handle transactions command
    elif args.command == 'transactions':
        data = load_data(DATA_FILE)
        month = args.month if args.month else get_current_month()
        transactions = filter_by_month(data["transactions"], month)
        output = format_transactions_list(transactions)
        print(output)

    # Handle edit command
    elif args.command == 'edit':
        data = load_data(DATA_FILE)
        edit_transaction(data, args.transaction_id,
                        amount=args.amount,
                        category=args.category,
                        description=args.description,
                        date=args.date)
        save_data(data, DATA_FILE)
        print(f"Transakcja {args.transaction_id} została zaktualizowana")

    # Handle delete command
    elif args.command == 'delete':
        data = load_data(DATA_FILE)
        transaction = delete_transaction(data, args.transaction_id)
        save_data(data, DATA_FILE)
        print(f"Usunięto transakcję {args.transaction_id}: {transaction['amount']:.2f} PLN ({transaction['category']})")

    # Handle set-limit command
    elif args.command == 'set-limit':
        amount = validate_amount(args.amount)
        data = load_data(DATA_FILE)
        set_limit(data, amount, args.month)
        save_data(data, DATA_FILE)
        if args.month:
            print(f"Ustawiono limit dla {args.month}: {amount:.2f} PLN")
        else:
            print(f"Ustawiono domyślny limit: {amount:.2f} PLN")

    # Handle limits command
    elif args.command == 'limits':
        data = load_data(DATA_FILE)
        output = format_limits_list(data.get("limits", {}))
        print(output)

    # Handle fixed-list command
    elif args.command == 'fixed-list':
        data = load_data(DATA_FILE)
        output = format_fixed_costs_list(data.get("fixed_costs", []))
        print(output)

    # Handle fixed-add command
    elif args.command == 'fixed-add':
        amount = validate_amount(args.amount)
        category = validate_string(args.category, "Kategoria")
        description = validate_string(args.description, "Opis")
        data = load_data(DATA_FILE)
        fixed_cost = add_fixed_cost(data, amount, category, description)
        save_data(data, DATA_FILE)
        print(f"Dodano koszt stały {fixed_cost['id']}: {amount:.2f} PLN ({category})")

    # Handle fixed-edit command
    elif args.command == 'fixed-edit':
        data = load_data(DATA_FILE)
        edit_fixed_cost(data, args.fixed_cost_id,
                       amount=args.amount,
                       category=args.category,
                       description=args.description)
        save_data(data, DATA_FILE)
        print(f"Koszt stały {args.fixed_cost_id} został zaktualizowany")

    # Handle fixed-delete command
    elif args.command == 'fixed-delete':
        data = load_data(DATA_FILE)
        fixed_cost = delete_fixed_cost(data, args.fixed_cost_id)
        save_data(data, DATA_FILE)
        print(f"Usunięto koszt stały {args.fixed_cost_id}: {fixed_cost['amount']:.2f} PLN ({fixed_cost['category']})")
