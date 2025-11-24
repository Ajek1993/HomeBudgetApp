# PLAN PRAC - BUDGET CLI MVP

## DATA SCHEMA (Definicja struktur)

### Pełna struktura data.json:
```json
{
  "limit": 5000,
  "transactions": [
    {
      "date": "2025-11-24",
      "amount": 150.50,
      "category": "Jedzenie",
      "description": "Biedronka"
    }
  ],
  "fixed_costs": [
    {
      "amount": 1200,
      "category": "Mieszkanie",
      "description": "Czynsz"
    }
  ]
}
```

**Zasady:**
- `date` w formacie ISO: YYYY-MM-DD
- `amount` jako float (liczba zmiennoprzecinkowa)
- `category` i `description` nie mogą być puste (walidacja w add)
- `fixed_costs` bez pola `date` (dodawane podczas apply-fixed)
- Backup tworzony PRZED ZAPISEM (nie przy starcie)

---

## ETAP 1: JSON Storage (Single-file)
**Cel**: Działający moduł odczytu/zapisu JSON z walidacją i backupem w `budget.py`.

**Kroki**:
1. Utwórz katalog `data/`
2. Utwórz `budget.py` i dodaj importy: `import json`, `from pathlib import Path`, `import shutil`, `import sys`, `from decimal import Decimal`, `from datetime import datetime, date`, `import argparse`
3. Napisz funkcję `create_empty_data()` zwracającą dict: `{"limit": 5000, "transactions": [], "fixed_costs": []}`
4. Napisz funkcję `load_data(path)` która sprawdza `Path(path).exists()`, jeśli nie - wywołuje `create_empty_data()` i zapisuje do pliku i zwraca, jeśli tak - parsuje JSON i zwraca
5. Dodaj obsługę `json.JSONDecodeError` w `load_data()` - wyświetl "BŁĄD: Plik {path} jest uszkodzony..." i wywołaj `sys.exit(1)` bez nadpisywania
6. Napisz funkcję `save_data(data, path)` która najpierw sprawdza `Path(path).exists()`, jeśli tak - tworzy backup używając `shutil.copy2(path, path + '.bak')`, następnie zapisuje JSON z `json.dump(data, f, indent=2)`
7. Dodaj obsługę `PermissionError` w `save_data()` w bloku try/except - wyświetl "BŁĄD: Nie można zapisać do pliku..." i wywołaj `sys.exit(1)`

**Edge cases do obsłużenia**:
- Brak pliku danych (pierwsze uruchomienie) → auto-create
- Uszkodzony JSON (ręczna edycja) → error + exit(1)
- Concurrency/PermissionError (plik otwarty w edytorze) → error + exit(1)

**Definicja "done"**:
- `load_data('data/data.json')` tworzy plik gdy nie istnieje
- `load_data()` wyświetla błąd i kończy program (exit 1) gdy JSON uszkodzony
- `save_data()` tworzy backup `.bak` przed zapisem (tylko jeśli plik istnieje)
- `save_data()` wyświetla błąd i kończy program gdy plik zablokowany

**Test**:
```bash
python -c "import sys; sys.path.insert(0, '.'); from budget import load_data; data = load_data('data/data.json'); print(data)"
# Zwraca: {'limit': 5000, 'transactions': [], 'fixed_costs': []}
```

---

## ETAP 2: Add Transaction
**Cel**: Działająca komenda `python budget.py add` dodająca transakcję.

**Kroki**:
1. Dodaj w `budget.py` setup argparse: `parser = argparse.ArgumentParser()`, `subparsers = parser.add_subparsers(dest='command')`
2. Dodaj subcommand "add": `add_parser = subparsers.add_parser('add')` z argumentami `--amount` (required), `--category` (required), `--description` (required)
3. Napisz funkcję `validate_amount(value)` która próbuje `float(value)` w try/except `ValueError`, jeśli błąd - wyświetl "BŁĄD: Kwota musi być liczbą..." i wywołaj `sys.exit(1)`, jeśli OK - zwróć `float(value)`
4. Napisz funkcję `validate_string(value, field_name)` która sprawdza `if not value or value.strip() == ""` - jeśli puste, wyświetl "BŁĄD: {field_name} nie może być puste" i wywołaj `sys.exit(1)`
5. Napisz funkcję `add_transaction(data, amount, category, description)` która tworzy dict `{"date": date.today().isoformat(), "amount": amount, "category": category, "description": description}` i dopisuje do `data["transactions"]`
6. W `if __name__ == "__main__"` dodaj obsługę komendy "add": parsuj argumenty → validate_amount → validate_string (2x) → load_data → add_transaction → save_data → wyświetl "Dodano {amount} PLN ({category})"

**Edge cases do obsłużenia**:
- Błędny typ danych (kwota jako tekst "sto złotych") → error + exit(1)
- Pusta kategoria lub opis → error + exit(1)

**Definicja "done"**:
- Komenda przyjmuje wszystkie wymagane parametry (--amount, --category, --description)
- Walidacja kwoty zwraca błąd dla nie-liczb
- Walidacja stringów zwraca błąd dla pustych wartości
- Transakcja zapisuje się w `data.json` z datą dzisiejszą (ISO format)
- Output potwierdza dodanie: "Dodano X PLN (kategoria)"

**Test**:
```bash
python budget.py add --amount 150.50 --category "Jedzenie" --description "Biedronka"
# Wyświetla: "Dodano 150.50 PLN (Jedzenie)"
# data.json zawiera nowy wpis w transactions[]
```

**Test błędu (kwota)**:
```bash
python budget.py add --amount "sto złotych" --category "Test" --description "Test"
# Wyświetla: "BŁĄD: Kwota musi być liczbą (np. 50.00 lub 50)"
# Exit code: 1
```

**Test błędu (pusta kategoria)**:
```bash
python budget.py add --amount 100 --category "" --description "Test"
# Wyświetla: "BŁĄD: Kategoria nie może być pusta"
# Exit code: 1
```

---

## ETAP 3: Status Budżetu
**Cel**: Działająca komenda `python budget.py status` pokazująca bilans.

**Kroki**:
1. Dodaj subcommand "status" do argparse: `status_parser = subparsers.add_parser('status')`
2. Napisz funkcję `get_current_month()` zwracającą `date.today().strftime("%Y-%m")`
3. Napisz funkcję `filter_by_month(transactions, month_str)` która zwraca listę transakcji gdzie `t["date"].startswith(month_str)`
4. Napisz funkcję `calculate_total(transactions)` która sumuje `Decimal(str(t["amount"]))` dla każdej transakcji i zwraca Decimal
5. Napisz funkcję `format_status(limit, spent, remaining, month)` która zwraca string w formacie: "Limit: {limit} PLN\nWydano ({month}): {spent} PLN\nPozostało: {remaining} PLN"
6. W `if __name__ == "__main__"` dodaj obsługę "status": load_data → get_current_month → filter_by_month → calculate_total → oblicz remaining (`Decimal(data["limit"]) - spent`) → format_status → print

**Edge cases do obsłużenia**:
- Brak transakcji (suma = 0) → wyświetl "Wydano: 0.00 PLN"

**Definicja "done"**:
- Komenda działa bez parametrów
- Filtrowanie uwzględnia tylko bieżący miesiąc (porównanie startswith)
- Obliczenia używają `Decimal` (konwersja float → string → Decimal)
- Output pokazuje: Limit, Wydano (YYYY-MM), Pozostało z 2 miejscami po przecinku

**Test**:
```bash
python budget.py status
# Wyświetla:
# Limit: 5000.00 PLN
# Wydano (2025-11): 150.50 PLN
# Pozostało: 4849.50 PLN
```

---

## ETAP 4: Apply Fixed Costs
**Cel**: Działająca komenda `python budget.py apply-fixed` kopiująca szablony.

**Kroki**:
1. Dodaj subcommand "apply-fixed" do argparse: `fixed_parser = subparsers.add_parser('apply-fixed')`
2. Zaktualizuj `create_empty_data()` aby zwracała przykładowe fixed_costs: `"fixed_costs": [{"amount": 1200, "category": "Mieszkanie", "description": "Czynsz"}, {"amount": 150, "category": "Rachunki", "description": "Prąd"}]`
3. Napisz funkcję `apply_fixed_costs(data)` która sprawdza `if not data["fixed_costs"]` - jeśli pusta, wyświetl "Brak kosztów stałych do dodania" i zwróć (bez exit), jeśli nie - iteruj po fixed_costs i dla każdego dodaj transaction z dzisiejszą datą
4. Dodaj w `apply_fixed_costs()` obliczenie total_amount (suma wszystkich fixed_costs) i zwróć tuple `(count, total_amount)`
5. W `if __name__ == "__main__"` dodaj obsługę "apply-fixed": load_data → apply_fixed_costs → save_data (tylko jeśli count > 0) → wyświetl "Dodano {count} kosztów stałych ({total} PLN)"

**Edge cases do obsłużenia**:
- Brak fixed_costs w JSON (pusta lista) → wyświetl "Brak kosztów stałych do dodania" i zakończ bez zapisu

**Definicja "done"**:
- Komenda działa bez parametrów
- Każdy wpis z `fixed_costs[]` kopiuje się jako transakcja z wszystkimi polami (amount, category, description)
- Data ustawiana na dzisiejszą (ISO format)
- Output potwierdza ilość i sumę: "Dodano X kosztów stałych (Y PLN)"
- Jeśli lista pusta - wyświetl komunikat i nie zapisuj

**Test**:
```bash
python budget.py apply-fixed
# Wyświetla: "Dodano 2 kosztów stałych (1350.00 PLN)"
# data.json ma 2 nowe wpisy w transactions[] z dzisiejszą datą
```

**Test pustej listy**:
```bash
# Ręcznie wyczyść fixed_costs w data.json: "fixed_costs": []
python budget.py apply-fixed
# Wyświetla: "Brak kosztów stałych do dodania"
# Exit code: 0 (bez błędu)
```

---

## ETAP 5: List by Category
**Cel**: Działająca komenda `python budget.py list` grupująca wydatki.

**Kroki**:
1. Dodaj subcommand "list" do argparse: `list_parser = subparsers.add_parser('list')`
2. Napisz funkcję `group_by_category(transactions)` która tworzy pusty dict, iteruje po transactions i dla każdej kategorii sumuje kwoty: `grouped[cat] = grouped.get(cat, Decimal(0)) + Decimal(str(t["amount"]))`
3. Użyj `filter_by_month()` z Etapu 3 do filtrowania tylko bieżącego miesiąca
4. Napisz funkcję `format_category_list(grouped)` która zwraca listę stringów `"{cat}: {amount:.2f} PLN"` posortowaną alfabetycznie po kategorii
5. W `if __name__ == "__main__"` dodaj obsługę "list": load_data → get_current_month → filter_by_month → group_by_category → format_category_list → print każdą linię

**Edge cases do obsłużenia**:
- Brak transakcji w bieżącym miesiącu → wyświetl "Brak transakcji w tym miesiącu"

**Definicja "done"**:
- Komenda działa bez parametrów
- Grupowanie działa dla wielu kategorii (sumowanie Decimal)
- Output pokazuje każdą kategorię z sumą (2 miejsca po przecinku)
- Tylko transakcje z bieżącego miesiąca
- Lista posortowana alfabetycznie

**Test**:
```bash
# Po dodaniu kilku transakcji różnych kategorii:
python budget.py list
# Wyświetla:
# Jedzenie: 150.50 PLN
# Mieszkanie: 1350.00 PLN
# Transport: 45.80 PLN
```

**Test brak transakcji**:
```bash
# Na pustym pliku:
python budget.py list
# Wyświetla: "Brak transakcji w tym miesiącu"
```

---

## TEST INTEGRACYJNY - END TO END

### Scenariusz sukcesu: Pierwszy miesiąc budżetu

**Użytkownik robi**:
```bash
# 1. Pierwsze uruchomienie (plik nie istnieje)
python budget.py status

# 2. Dodaje koszty stałe
python budget.py apply-fixed

# 3. Sprawdza status
python budget.py status

# 4. Dodaje transakcje ręczne
python budget.py add --amount 45.80 --category "Transport" --description "Uber"
python budget.py add --amount 120.00 --category "Jedzenie" --description "Zakupy"

# 5. Sprawdza podział po kategoriach
python budget.py list

# 6. Sprawdza końcowy status
python budget.py status
```

**Dostaje**:
```
# Krok 1:
Limit: 5000.00 PLN
Wydano (2025-11): 0.00 PLN
Pozostało: 5000.00 PLN

# Krok 2:
Dodano 2 kosztów stałych (1350.00 PLN)

# Krok 3:
Limit: 5000.00 PLN
Wydano (2025-11): 1350.00 PLN
Pozostało: 3650.00 PLN

# Krok 4:
Dodano 45.80 PLN (Transport)
Dodano 120.00 PLN (Jedzenie)

# Krok 5:
Jedzenie: 120.00 PLN
Mieszkanie: 1200.00 PLN
Rachunki: 150.00 PLN
Transport: 45.80 PLN

# Krok 6:
Limit: 5000.00 PLN
Wydano (2025-11): 1515.80 PLN
Pozostało: 3484.20 PLN
```

---

### Scenariusze błędów

**1. Uszkodzony JSON**

Użytkownik robi:
```bash
# Ręcznie psuje data.json (usuwa przecinek)
python budget.py status
```

Dostaje komunikat:
```
BŁĄD: Plik data/data.json jest uszkodzony (nieprawidłowy JSON).
Sprawdź składnię lub przywróć z backupu: data/data.json.bak
Nie próbowano nadpisać pliku.
```
Exit code: 1

---

**2. Błędna kwota**

Użytkownik robi:
```bash
python budget.py add --amount "pięćdziesiąt" --category "Test" --description "Test"
```

Dostaje komunikat:
```
BŁĄD: Kwota musi być liczbą (np. 50.00 lub 50)
Podano: pięćdziesiąt
```
Exit code: 1

---

**3. Plik zablokowany (otwarty w Notatniku)**

Użytkownik robi:
```bash
# Otwiera data.json w Notatniku (Windows blokuje zapis)
python budget.py add --amount 100 --category "Test" --description "Test"
```

Dostaje komunikat:
```
BŁĄD: Nie można zapisać do pliku data/data.json
Plik jest otwarty w innym programie. Zamknij edytor i spróbuj ponownie.
```
Exit code: 1

---

**4. Brak wymaganych parametrów**

Użytkownik robi:
```bash
python budget.py add --amount 100
```

Dostaje komunikat (argparse):
```
usage: budget.py add [-h] --amount AMOUNT --category CATEGORY --description DESCRIPTION
budget.py add: error: the following arguments are required: --category, --description
```
Exit code: 2

---

**5. Pusta kategoria**

Użytkownik robi:
```bash
python budget.py add --amount 100 --category "" --description "Test"
```

Dostaje komunikat:
```
BŁĄD: Kategoria nie może być pusta
```
Exit code: 1

---

## WALIDACJA MVP - CHECKLIST

Po zakończeniu wszystkich etapów sprawdź:

- [ ] `python budget.py status` działa na pustym pliku (auto-creates)
- [ ] `python budget.py add` waliduje kwotę (odrzuca tekst)
- [ ] `python budget.py add` waliduje puste stringi (kategoria, opis)
- [ ] `python budget.py apply-fixed` dodaje koszty stałe
- [ ] `python budget.py apply-fixed` wyświetla komunikat gdy lista pusta
- [ ] `python budget.py list` grupuje po kategoriach
- [ ] `python budget.py list` wyświetla komunikat gdy brak transakcji
- [ ] Uszkodzony JSON nie nadpisuje się (error + exit 1)
- [ ] PermissionError daje czytelny komunikat (error + exit 1)
- [ ] Wszystkie komendy kończą się exit code 0 (sukces) lub 1 (błąd)
- [ ] Backup `.bak` tworzy się przed każdym zapisem (tylko jeśli plik istnieje)
- [ ] Data w transakcjach to format ISO (YYYY-MM-DD via date.today().isoformat())
- [ ] Sumy używają Decimal (konwersja float → str → Decimal)
- [ ] Domyślny limit to 5000 PLN
- [ ] Kwoty w JSON zapisane jako float (nie string)

---

## STRUKTURA FINALNA PROJEKTU

```
PROJEKT/
├── budget.py              # Single-file MVP (wszystkie funkcje + argparse)
├── data/
│   ├── data.json          # Auto-created przy pierwszym uruchomieniu
│   └── data.json.bak      # Auto-created przed zapisem (jeśli plik istnieje)
└── specs/
    ├── brief.v3.md
    ├── brief.etaps.v4.md
    └── plan.md            # Ten dokument
```

**Single-file architecture**: Cały kod w `budget.py` (~250-300 linii), zgodnie z decyzją projektową.
