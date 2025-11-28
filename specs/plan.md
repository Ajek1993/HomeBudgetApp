# PLAN PRAC - BUDGET CLI MVP

## DATA SCHEMA (Definicja struktur)

### Pełna struktura data.json:

```json
{
  "limit": 5000,
  "transactions": [
    {
      "date": "2025-11-24",
      "amount": 150.5,
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
- `amount` jako float (liczba zmiennoprzecinkowa) - walidacja przyjmuje float, obliczenia używają Decimal
- `amount` musi być > 0 (nie akceptujemy ujemnych kwot)
- `category` i `description` nie mogą być puste (walidacja w add)
- `fixed_costs` bez pola `date` (dodawane podczas apply-fixed)
- **Backup tworzony PRZED ZAPISEM** (w save_data, nie przy starcie aplikacji)

---

## REGUŁY INTEGRACJI MIĘDZY ETAPAMI

**Zasada ogólna**: Każdy kolejny etap dodaje nowy kod, ale NIE modyfikuje istniejących funkcji z poprzednich etapów (chyba że specyfikacja wyraźnie to nakazuje).

**Co można zmieniać w każdym etapie:**

- **ETAP 1**: Tworzysz wszystko od zera
- **ETAP 2**:
  - ✅ Dodaj nowe funkcje (validate_amount, validate_string, add_transaction)
  - ✅ Rozbuduj blok `if __name__ == "__main__":`
  - ❌ NIE zmieniaj create_empty_data, load_data, save_data
- **ETAP 3-4**:
  - ✅ Dodaj nowe funkcje
  - ✅ Dodaj nowe subcommandy do argparse
  - ✅ Rozbuduj blok `if __name__ == "__main__":`
  - ❌ NIE zmieniaj funkcji z poprzednich etapów

**Wyjątek**: Jeśli krok explicite mówi "zaktualizuj funkcję X", wtedy można.

---

## CONSTANTS (Stałe projektu)

Zdefiniuj na początku pliku budget.py (po importach):

```python
DATA_FILE = "data/data.json"
```

---

**Test z custom date**:

```bash
python budget.py add --amount 100.00 --category "Test" --description "Test" --date "2025-11-20"
# Wyświetla: "Dodano 100.00 PLN (Test)"
# data.json zawiera wpis z datą "2025-11-20"
```

**Test błędnej daty**:

```bash
python budget.py add --amount 100 --category "Test" --description "Test" --date "20-11-2025"
# Wyświetla: "BŁĄD: Data musi być w formacie YYYY-MM-DD (np. 2025-11-24)"
# Exit code: 1
```

## ETAP 0: Szkielet Projektu

**Cel**: Przygotowanie struktury katalogów i pustego budget.py z komentarzami sekcyjnymi.

**Kroki**:

0. Utwórz katalog data/ używając `Path("data").mkdir(exist_ok=True)`
1. Napisz funkcję `create_empty_data()` która zwraca dict:
   ```python
   {
       "limit": 5000,
       "transactions": [],
       "fixed_costs": []
   }
   ```
2. Napisz funkcję `load_data(path)` - krok 1: sprawdź czy `Path(path).exists()`
3. W `load_data(path)` - krok 2: jeśli plik NIE istnieje, wywołaj `create_empty_data()`
4. W `load_data(path)` - krok 3: zapisz utworzony pusty dict do pliku używając `json.dump(data, f, indent=2)`
5. W `load_data(path)` - krok 4: zwróć utworzony dict
6. W `load_data(path)` - krok 5: jeśli plik istnieje, dodaj blok try dla odczytu
7. W `load_data(path)` - krok 6: w bloku try wczytaj używając `json.load(f)` i zapisz do `data`
8. W `load_data(path)` - krok 7: dodaj obsługę `json.JSONDecodeError` w bloku except
9. W `load_data(path)` - krok 8: w except JSONDecodeError wyświetl komunikat:
   ```
   BŁĄD: Plik {path} jest uszkodzony (nieprawidłowy JSON).
   Sprawdź składnię lub przywróć z backupu: {path}.bak
   Nie próbowano nadpisać pliku.
   ```
10. W `load_data(path)` - krok 9: w except JSONDecodeError wywołaj `sys.exit(1)`
11. W `load_data(path)` - krok 10: po try/except sprawdź czy data ma wymagane pola używając `if not all(k in data for k in ["limit", "transactions", "fixed_costs"])`
12. W `load_data(path)` - krok 11: jeśli brakuje pól, wyświetl komunikat:

```
BŁĄD: Plik {path} ma nieprawidłową strukturę.
Wymagane pola: limit, transactions, fixed_costs
Sprawdź plik lub przywróć z backupu: {path}.bak
```

13. W `load_data(path)` - krok 12: jeśli brakuje pól, wywołaj `sys.exit(1)`
14. W `load_data(path)` - krok 13: zwróć `data`
15. Napisz funkcję `save_data(data, path)` - krok 1: sprawdź czy `Path(path).exists()`
16. W `save_data(data, path)` - krok 2: jeśli plik istnieje, utwórz backup używając `shutil.copy2(path, str(path) + '.bak')`
17. W `save_data(data, path)` - krok 3: dodaj blok try dla zapisu pliku
18. W `save_data(data, path)` - krok 4: w bloku try zapisz JSON używając `json.dump(data, f, indent=2)`
19. W `save_data(data, path)` - krok 5: dodaj obsługę `PermissionError` w bloku except
20. W `save_data(data, path)` - krok 6: w except PermissionError wyświetl komunikat:

```
BŁĄD: Nie można zapisać do pliku {path}
Plik jest otwarty w innym programie. Zamknij edytor i spróbuj ponownie.
```

21. W `save_data(data, path)` - krok 7: w except PermissionError wywołaj `sys.exit(1)`
22. Dodaj blok `if __name__ == "__main__": pass` na końcu pliku
    **Edge cases obsłużone**:

- Brak pliku danych (pierwsze uruchomienie) → auto-create
- Uszkodzony JSON (ręczna edycja) → error + exit(1), nie nadpisuj
- Nieprawidłowa struktura JSON (brakujące pola) → error + exit(1)
- Concurrency/PermissionError (plik otwarty w edytorze) → error + exit(1)

**Definicja "done"**:

- `load_data('data/data.json')` tworzy plik gdy nie istnieje
- `load_data()` wyświetla błąd i kończy program (exit 1) gdy JSON uszkodzony
- `load_data()` wyświetla błąd i kończy program (exit 1) gdy brakuje wymaganych pól
- `save_data()` tworzy backup `.bak` PRZED ZAPISEM (tylko jeśli plik istnieje)
- `save_data()` wyświetla błąd i kończy program gdy plik zablokowany
- Komunikaty błędów są dokładnie takie jak w specyfikacji
  **Test**:

```bash
python -c "from pathlib import Path; print('OK' if Path('data').exists() else 'FAIL')"
# Wyświetla: OK
```

---

## ETAP 1: Status Budżetu

**Cel**: Działająca komenda `python budget.py status` pokazująca bilans budżetu.

**Lokalizacje kodu**: Sekcje `# === TRANSACTIONS ===`, `# === DISPLAY ===`, `# === MAIN ===` w budget.py

**Kroki**:

1. W sekcji `# === TRANSACTIONS ===` napisz funkcję `get_current_month()` zwracającą `date.today().strftime("%Y-%m")`
2. W sekcji `# === TRANSACTIONS ===` napisz funkcję `filter_by_month(transactions, month_str)`
3. W `filter_by_month()` - utwórz pustą listę `filtered = []`
4. W `filter_by_month()` - iteruj po transactions
5. W `filter_by_month()` - dla każdej transakcji dodaj blok try
6. W `filter_by_month()` - w bloku try sprawdź czy `t["date"].startswith(month_str)`
7. W `filter_by_month()` - jeśli tak, dodaj transakcję do `filtered`
8. W `filter_by_month()` - dodaj except `(KeyError, AttributeError)` - pomiń transakcje z błędnymi datami
9. W `filter_by_month()` - zwróć `filtered`
10. W sekcji `# === TRANSACTIONS ===` napisz funkcję `calculate_total(transactions)`
11. W `calculate_total()` - utwórz `total = Decimal(0)`
12. W `calculate_total()` - iteruj po transactions i dla każdej dodaj `Decimal(str(t["amount"]))` do total
13. W `calculate_total()` - zwróć total
14. W sekcji `# === DISPLAY ===` napisz funkcję `format_status(limit, spent, remaining, month)`
15. W `format_status()` - zwróć f-string z formatem:

```
Limit: {limit:.2f} PLN
Wydano ({month}): {spent:.2f} PLN
Pozostało: {remaining:.2f} PLN
```

16. W sekcji `# === MAIN ===` usuń `pass` i dodaj setup argparse: `parser = argparse.ArgumentParser(description="Budget CLI - Prosty system zarządzania budżetem domowym")`
17. W `# === MAIN ===` dodaj `subparsers = parser.add_subparsers(dest='command', required=True)`
18. W sekcji `# === MAIN ===` dodaj parsowanie argumentów: `args = parser.parse_args()`
19. W sekcji `# === MAIN ===` dodaj nowy subcommand "status": `status_parser = subparsers.add_parser('status', help='Sprawdź stan budżetu')`
20. Dodaj nowy blok `if args.command == 'status':`
21. W bloku "status" - wywołaj `load_data(DATA_FILE)` i zapisz do `data`
22. W bloku "status" - wywołaj `get_current_month()` i zapisz do `month`
23. W bloku "status" - wywołaj `filter_by_month(data["transactions"], month)` i zapisz do `current_month_transactions`
24. W bloku "status" - wywołaj `calculate_total(current_month_transactions)` i zapisz do `spent`
25. W bloku "status" - oblicz `remaining = Decimal(str(data["limit"])) - spent`
26. W bloku "status" - wywołaj `format_status(data["limit"], spent, remaining, month)` i zapisz do `output`
27. W bloku "status" - wyświetl `output`

**Edge cases obsłużone**:

- Brak transakcji (suma = 0) → wyświetl "Wydano: 0.00 PLN"
- Nieprawidłowy format daty w istniejących transakcjach → pomija taką transakcję (ciche niepowodzenie)

**Definicja "done"**:

- Komenda działa bez parametrów
- Filtrowanie uwzględnia tylko bieżący miesiąc (porównanie startswith)
- Filtrowanie pomija transakcje z błędnymi datami
- Obliczenia używają `Decimal` (konwersja float → string → Decimal)
- Output pokazuje: Limit, Wydano (YYYY-MM), Pozostało z 2 miejscami po przecinku
  **Test**:

```bash
python -c "import sys; sys.path.insert(0, '.'); from budget import load_data; data = load_data('data/data.json'); print(data)"
# Zwraca: {'limit': 5000, 'transactions': [], 'fixed_costs': []}
```

---

## ETAP 2: Add Transaction

**Cel**: Działająca komenda `python budget.py add` dodająca transakcję.

**Lokalizacje kodu**:

- Sekcja `# === VALIDATION ===` - funkcje walidacyjne
- Sekcja `# === TRANSACTIONS ===` - funkcja add_transaction
- Sekcja `# === MAIN ===` - argparse + routing

**REGUŁA INTEGRACJI**: NIE zmieniaj funkcji create_empty_data, load_data, save_data z ETAPU 1.

**Kroki**:

1. W sekcji `# === VALIDATION ===` napisz funkcję `validate_amount(value)` - dodaj blok try
2. W `validate_amount(value)` - w bloku try wykonaj `float(value)`
3. W `validate_amount(value)` - dodaj sprawdzenie `if float(value) <= 0`
4. W `validate_amount(value)` - jeśli kwota <= 0, wyświetl:
   ```
   BŁĄD: Kwota musi być większa od 0
   Podano: {value}
   ```
5. W `validate_amount(value)` - jeśli kwota <= 0, wywołaj `sys.exit(1)`
6. W `validate_amount(value)` - jeśli kwota OK, zwróć `float(value)`
7. W `validate_amount(value)` - dodaj except `ValueError`
8. W `validate_amount(value)` - w except ValueError wyświetl: BŁĄD: Kwota musi być liczbą (np. 50.00 lub 50) Podano: {value}
9. W `validate_amount(value)` - w except ValueError wywołaj `sys.exit(1)`
10. W sekcji `# === VALIDATION ===` napisz funkcję `validate_string(value, field_name)`
11. W `validate_string()` - sprawdź `if not value or not value.strip()`
12. W `validate_string()` - jeśli pusty, wyświetl: `BŁĄD: {field_name} nie może być pusta(y)`
13. W `validate_string()` - jeśli pusty, wywołaj `sys.exit(1)`
14. W `validate_string()` - zwróć `value.strip()`
15. W sekcji `# === VALIDATION ===` napisz funkcję `validate_date(value)`
16. W `validate_date(value)` - jeśli value is None, zwróć `date.today().isoformat()`
17. W `validate_date(value)` - dodaj blok try dla parsowania daty
18. W `validate_date(value)` - w bloku try wywołaj `datetime.strptime(value, "%Y-%m-%d")`
19. W `validate_date(value)` - jeśli parsowanie OK, zwróć `value`
20. W `validate_date(value)` - dodaj except `ValueError`
21. W `validate_date(value)` - w except ValueError wyświetl:

```
BŁĄD: Data musi być w formacie YYYY-MM-DD (np. 2025-11-24)
Podano: {value}
```

22. W `validate_date(value)` - w except ValueError wywołaj `sys.exit(1)`
23. W sekcji `# === TRANSACTIONS ===` napisz funkcję `add_transaction(data, amount, category, description, transaction_date)`
24. W `add_transaction()` - utwórz dict transakcji z polami: date (transaction_date), amount, category, description
25. W `add_transaction()` - dopisz dict do `data["transactions"]`
26. W `# === MAIN ===` dodaj subcommand "add": `add_parser = subparsers.add_parser('add', help='Dodaj transakcję')`
27. Do `add_parser` dodaj argument `--amount` (required=True, help='Kwota')
28. Do `add_parser` dodaj argument `--category` (required=True, help='Kategoria')
29. Do `add_parser` dodaj argument `--description` (required=True, help='Opis')
30. Do `add_parser` dodaj argument `--date` (required=False, default=None, help='Data (YYYY-MM-DD), domyślnie dziś')
31. W `# === MAIN ===` dodaj obsługę komendy "add": `if args.command == 'add':`
32. W bloku if dla "add" - wywołaj `validate_amount(args.amount)` i zapisz wynik do zmiennej `amount`
33. W bloku if dla "add" - wywołaj `validate_string(args.category, "Kategoria")` i zapisz do `category`
34. W bloku if dla "add" - wywołaj `validate_string(args.description, "Opis")` i zapisz do `description`
35. W bloku if dla "add" - wywołaj `validate_date(args.date)` i zapisz do `transaction_date`
36. W bloku if dla "add" - wywołaj `load_data(DATA_FILE)` i zapisz do `data`
37. W bloku if dla "add" - wywołaj `add_transaction(data, amount, category, description, transaction_date)`
38. W bloku if dla "add" - wywołaj `save_data(data, DATA_FILE)`
39. W bloku if dla "add" - wyświetl `Dodano {amount} PLN ({category})`

**Edge cases obsłużone**:

- Błędny typ danych (kwota jako tekst "sto złotych") → error + exit(1)
- Ujemna lub zerowa kwota → error + exit(1)
- Pusta kategoria lub opis → error + exit(1)
- Błędny format daty (np. "24-11-2025" zamiast "2025-11-24") → error + exit(1)

**Definicja "done"**:

- Komenda przyjmuje wszystkie wymagane parametry (--amount, --category, --description)
- Komenda przyjmuje opcjonalny parametr --date (domyślnie dziś)
- Walidacja kwoty zwraca błąd dla nie-liczb
- Walidacja kwoty zwraca błąd dla kwot <= 0
- Walidacja stringów zwraca błąd dla pustych wartości
- Walidacja daty zwraca błąd dla błędnego formatu
- Transakcja zapisuje się w `data.json` z datą (podaną lub dzisiejszą, ISO format)
- Output potwierdza dodanie: "Dodano X PLN (kategoria)"

**Test sukcesu**:

```bash
python budget.py add --amount 150.50 --category "Jedzenie" --description "Biedronka"
# Wyświetla: "Dodano 150.50 PLN (Jedzenie)"
# data.json zawiera nowy wpis w transactions[]
```

**Test błędu (kwota - tekst)**:

```bash
python budget.py add --amount "sto złotych" --category "Test" --description "Test"
# Wyświetla: "BŁĄD: Kwota musi być liczbą (np. 50.00 lub 50)"
# Exit code: 1
```

**Test błędu (kwota - ujemna)**:

```bash
python budget.py add --amount -50 --category "Test" --description "Test"
# Wyświetla: "BŁĄD: Kwota musi być większa od 0"
# Exit code: 1
```

**Test błędu (pusta kategoria)**:

```bash
python budget.py add --amount 100 --category "" --description "Test"
# Wyświetla: "BŁĄD: Kategoria nie może być pusta"
# Exit code: 1
```

---

## ETAP 3: Apply Fixed Costs

**Cel**: Działająca komenda `python budget.py apply-fixed` kopiująca szablony.

**Lokalizacje kodu**:

- Sekcja `# === FIXED COSTS ===` - funkcja apply_fixed_costs
- Sekcja `# === MAIN ===` - nowy subcommand (apply-fixed)

**REGUŁA INTEGRACJI**: Reszta standardowo - dodajesz nowe funkcje.

**Kroki**:

1. W sekcji `# === FIXED COSTS ===` napisz funkcję `apply_fixed_costs(data)`

2. W `apply_fixed_costs()` - sprawdź `if not data.get("fixed_costs")`
3. W `apply_fixed_costs()` - jeśli lista pusta lub brak klucza, wyświetl "Brak kosztów stałych do dodania"
4. W `apply_fixed_costs()` - jeśli lista pusta, zwróć `(0, 0)` bez dalszych operacji
5. W `apply_fixed_costs()` - utwórz zmienne `count = 0` i `total_amount = Decimal(0)`
6. W `apply_fixed_costs()` - iteruj po `data["fixed_costs"]`
7. W `apply_fixed_costs()` - dla każdego fixed_cost utwórz nową transakcję z polami: date (date.today().isoformat()), amount, category, description
8. W `apply_fixed_costs()` - dopisz transakcję do `data["transactions"]`
9. W `apply_fixed_costs()` - zwiększ `count += 1`
10. W `apply_fixed_costs()` - dodaj `total_amount += Decimal(str(fixed_cost["amount"]))`
11. W `apply_fixed_costs()` - zwróć `(count, total_amount)`
12. W sekcji `# === MAIN ===` dodaj nowy subcommand "apply-fixed": `fixed_parser = subparsers.add_parser('apply-fixed', help='Dodaj koszty stałe')`
13. Dodaj nowy blok `elif args.command == 'apply-fixed':`
14. W bloku "apply-fixed" - wywołaj `load_data(DATA_FILE)` i zapisz do `data`
15. W bloku "apply-fixed" - wywołaj `apply_fixed_costs(data)` i zapisz wynik do `count, total`
16. W bloku "apply-fixed" - sprawdź `if count > 0:`
17. W bloku if (count > 0) - wywołaj `save_data(data, DATA_FILE)`
18. W bloku if (count > 0) - wyświetl `Dodano {count} kosztów stałych ({total:.2f} PLN)`

**Definicja "done"**:

- Komenda działa bez parametrów
- Jeśli fixed_costs pusta - wyświetla komunikat i kończy (bez zapisu)
- Każdy wpis z fixed_costs kopiuje się jako transakcja z datą dzisiejszą
- Output pokazuje liczbę dodanych kosztów i sumę
- Plik zapisuje się tylko gdy count > 0
  **Test domyślny (pusta lista)**:

```bash
python budget.py apply-fixed
# Wyświetla: "Brak kosztów stałych do dodania"
# Exit code: 0 (bez błędu)
```

**Test sukcesu** (po ręcznym dodaniu fixed_costs do data.json):

```bash
# Ręcznie dodaj do data.json:
# "fixed_costs": [
#     {"amount": 1200, "category": "Mieszkanie", "description": "Czynsz"},
#     {"amount": 150, "category": "Rachunki", "description": "Prąd"}
# ]
python budget.py apply-fixed
# Wyświetla: "Dodano 2 kosztów stałych (1350.00 PLN)"
# data.json ma 2 nowe wpisy w transactions[] z dzisiejszą datą
```

---

## ETAP 4: List by Category

**Cel**: Działająca komenda `python budget.py list` grupująca wydatki.

**Lokalizacje kodu**:

- Sekcja `# === TRANSACTIONS ===` - funkcja group_by_category
- Sekcja `# === DISPLAY ===` - funkcja format_category_list
- Sekcja `# === MAIN ===` - nowy subcommand

**REGUŁA INTEGRACJI**: Dodajesz nowe funkcje i nowy subcommand. NIE zmieniasz istniejącego kodu.

**Kroki**:

1. W sekcji `# === TRANSACTIONS ===` napisz funkcję `group_by_category(transactions)`
2. W `group_by_category()` - utwórz pusty dict: `grouped = {}`
3. W `group_by_category()` - iteruj po transactions
4. W `group_by_category()` - dla każdej transakcji pobierz kategorię: `cat = t["category"]`
5. W `group_by_category()` - oblicz `grouped[cat] = grouped.get(cat, Decimal(0)) + Decimal(str(t["amount"]))`
6. W `group_by_category()` - zwróć `grouped`
7. W sekcji `# === DISPLAY ===` napisz funkcję `format_category_list(grouped)`
8. W `format_category_list()` - sprawdź `if not grouped:`
9. W `format_category_list()` - jeśli pusty, zwróć `"Brak transakcji w tym miesiącu"`
10. W `format_category_list()` - posortuj kategorie alfabetycznie: `sorted_cats = sorted(grouped.keys())`
11. W `format_category_list()` - utwórz listę formatowanych linii: `lines = [f"{cat}: {grouped[cat]:.2f} PLN" for cat in sorted_cats]`
12. W `format_category_list()` - zwróć `"\n".join(lines)`
13. W sekcji `# === MAIN ===` dodaj nowy subcommand "list": `list_parser = subparsers.add_parser('list', help='Pokaż wydatki po kategoriach')`
14. Dodaj nowy blok `elif args.command == 'list':`
15. W bloku "list" - wywołaj `load_data(DATA_FILE)` i zapisz do `data`
16. W bloku "list" - wywołaj `get_current_month()` i zapisz do `month`
17. W bloku "list" - wywołaj `filter_by_month(data["transactions"], month)` i zapisz do `current_month_transactions`
18. W bloku "list" - wywołaj `group_by_category(current_month_transactions)` i zapisz do `grouped`
19. W bloku "list" - wywołaj `format_category_list(grouped)` i zapisz do `output`
19. W bloku "list" - wyświetl `output`

**Definicja "done"**:

- Komenda działa bez parametrów
- Grupowanie sumuje wydatki po kategoriach używając Decimal
- Lista posortowana alfabetycznie
- Output pokazuje każdą kategorię z sumą (2 miejsca po przecinku)
- Jeśli brak transakcji - wyświetla odpowiedni komunikat
- Filtruje tylko transakcje z bieżącego miesiąca
  **Test sukcesu**:

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

## ETAP 5: Walidacja MVP

**Cel**: Wykonanie pełnych testów integracyjnych i walidacja wszystkich wymagań.

**Kroki**:

### 5.1 Test End-to-End - Pierwszy miesiąc budżetu

1. Usuń `data/data.json` i `data/data.json.bak` (jeśli istnieją) - symulacja pierwszego uruchomienia
2. Uruchom `python budget.py status` - sprawdź czy wyświetla:
   ```
   Limit: 5000.00 PLN
   Wydano (2025-11): 0.00 PLN
   Pozostało: 5000.00 PLN
   ```
3. Sprawdź czy `data/data.json` został utworzony
4. Uruchom `python budget.py add --amount 45.80 --category "Transport" --description "Uber"` - sprawdź komunikat sukcesu
5. Uruchom `python budget.py add --amount 120.00 --category "Jedzenie" --description "Zakupy"` - sprawdź komunikat sukcesu
6. Uruchom `python budget.py list` - sprawdź czy wyświetla 2 kategorie posortowane alfabetycznie (Jedzenie, Transport)
7. Uruchom `python budget.py status` - sprawdź czy wydatki = 165.80, pozostało = 4834.20
8. Sprawdź czy `data/data.json.bak` istnieje

### 5.2 Test edge case - Uszkodzony JSON

9. Otwórz `data/data.json` w edytorze tekstowym
10. Usuń jeden przecinek lub nawias (zepsuj składnię JSON)
11. Zapisz plik
12. Uruchom `python budget.py status`
13. Sprawdź czy wyświetla komunikat błędu o uszkodzonym JSON
14. Sprawdź exit code = 1: `echo %ERRORLEVEL%` (Windows) lub `echo $?` (Linux)
15. Sprawdź czy plik NIE został nadpisany (wciąż uszkodzony)

### 5.3 Test edge case - Błędna kwota (tekst)

16. Przywróć poprawny JSON z `data/data.json.bak`
17. Uruchom `python budget.py add --amount "sto złotych" --category "Test" --description "Test"`
18. Sprawdź czy wyświetla "BŁĄD: Kwota musi być liczbą"
19. Sprawdź exit code = 1

### 5.4 Test edge case - Ujemna kwota

20. Uruchom `python budget.py add --amount -50 --category "Test" --description "Test"`
21. Sprawdź czy wyświetla "BŁĄD: Kwota musi być większa od 0"
22. Sprawdź exit code = 1

### 5.5 Test edge case - Pusta kategoria

23. Uruchom `python budget.py add --amount 100 --category "" --description "Test"`
24. Sprawdź czy wyświetla "BŁĄD: Kategoria nie może być pusta"
25. Sprawdź exit code = 1

### 5.6 Test edge case - PermissionError (tylko Windows)

26. Otwórz `data/data.json` w Notatniku (NIE zamykaj)
27. Uruchom `python budget.py add --amount 100 --category "Test" --description "Test"`
28. Sprawdź czy wyświetla komunikat o pliku otwartym w innym programie
29. Sprawdź exit code = 1
30. Zamknij Notatnik

### 5.7 Test edge case - Brak transakcji w miesiącu

37. Otwórz `data/data.json` w edytorze
38. Zmień wszystkie daty transakcji na poprzedni miesiąc (np. z "2025-11" na "2025-10")
39. Zapisz
40. Uruchom `python budget.py list`
41. Sprawdź czy wyświetla "Brak transakcji w tym miesiącu"

### 5.8 Walidacja struktury danych

42. Otwórz `data/data.json` i sprawdź ręcznie:
    - Czy istnieje pole `"limit"` (liczba)
    - Czy istnieje `"transactions"` (lista)
    - Czy każda transakcja ma pola: date, amount, category, description
    - Czy date jest w formacie ISO (YYYY-MM-DD)
    - Czy amount jest liczbą float (nie stringiem)
    - Czy istnieje `"fixed_costs"` (lista)
43. Sprawdź czy istnieje `data/data.json.bak`
44. Porównaj zawartość obu plików - backup powinien być poprzednią wersją

### 5.9 Checklist funkcjonalny (końcowa weryfikacja)

45. Sprawdź czy wszystkie poniższe punkty są TRUE:
    - [ ] `python budget.py status` działa na pustym pliku (auto-creates)
    - [ ] `python budget.py add` waliduje kwotę (odrzuca tekst)
    - [ ] `python budget.py add` waliduje ujemne kwoty (odrzuca)
    - [ ] `python budget.py add` waliduje puste stringi (kategoria, opis)
    - [ ] `python budget.py apply-fixed` dodaje koszty stałe
    - [ ] `python budget.py apply-fixed` wyświetla komunikat gdy lista pusta
    - [ ] `python budget.py list` grupuje po kategoriach
    - [ ] `python budget.py list` wyświetla komunikat gdy brak transakcji
    - [ ] Uszkodzony JSON nie nadpisuje się (error + exit 1)
    - [ ] PermissionError daje czytelny komunikat (error + exit 1)
    - [ ] Wszystkie komendy sukcesu kończą się exit code 0
    - [ ] Wszystkie komendy błędów kończą się exit code 1
    - [ ] Backup `.bak` tworzy się przed każdym zapisem (tylko jeśli plik istnieje)
    - [ ] Data w transakcjach to format ISO (YYYY-MM-DD)
    - [ ] Sumy używają Decimal w obliczeniach
    - [ ] Domyślny limit to 5000 PLN
    - [ ] Kwoty w JSON zapisane jako float (nie string)
    - [ ] Fixed_costs mają komentarz o testowym charakterze przykładów

**Edge cases obsłużone**:

- Błędny typ danych (kwota jako tekst "sto złotych") → error + exit(1)
- Ujemna lub zerowa kwota → error + exit(1)
- Pusta kategoria lub opis → error + exit(1)
- Błędny format daty (np. "24-11-2025" zamiast "2025-11-24") → error + exit(1)

- Komenda przyjmuje wszystkie wymagane parametry (--amount, --category, --description)
- Komenda przyjmuje opcjonalny parametr --date (domyślnie dziś)
- Walidacja kwoty zwraca błąd dla nie-liczb
- Walidacja kwoty zwraca błąd dla kwot <= 0
- Walidacja stringów zwraca błąd dla pustych wartości
- Walidacja daty zwraca błąd dla błędnego formatu
- Transakcja zapisuje się w `data.json` z datą (podaną lub dzisiejszą, ISO format)
- Output potwierdza dodanie: "Dodano X PLN (kategoria)"
- Wszystkie 47 kroków wykonane
- Wszystkie punkty checklisty (5.9) są TRUE
- Żaden test nie zwrócił nieoczekiwanego rezultatu
- Backup działa poprawnie (tworzy się przed zapisem)
- Wszystkie edge cases obsłużone zgodnie ze specyfikacją

---

## TEST SCENARIUSZE - OCZEKIWANE OUTPUTY

### Scenariusz sukcesu: Pierwszy miesiąc budżetu

**Użytkownik robi**:

```bash
# 1. Pierwsze uruchomienie (plik nie istnieje)
python budget.py status

# 2. Dodaje transakcje ręczne
python budget.py add --amount 45.80 --category "Transport" --description "Uber"
python budget.py add --amount 120.00 --category "Jedzenie" --description "Zakupy"

# 3. Sprawdza podział po kategoriach
python budget.py list

# 4. Sprawdza końcowy status
python budget.py status
```

**Dostaje**:

```
# Krok 1:
Limit: 5000.00 PLN
Wydano (2025-11): 0.00 PLN
Pozostało: 5000.00 PLN

# Krok 2:
Dodano 45.80 PLN (Transport)
Dodano 120.00 PLN (Jedzenie)

# Krok 3:
Jedzenie: 120.00 PLN
Transport: 45.80 PLN

# Krok 4:
Limit: 5000.00 PLN
Wydano (2025-11): 165.80 PLN
Pozostało: 4834.20 PLN
```

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

**2. Błędna kwota (tekst)**

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

**3. Ujemna kwota**

Użytkownik robi:

```bash
python budget.py add --amount -50 --category "Test" --description "Test"
```

Dostaje komunikat:

```
BŁĄD: Kwota musi być większa od 0
Podano: -50
```

Exit code: 1

---

**4. Plik zablokowany (otwarty w Notatniku)**

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

**5. Brak wymaganych parametrów**

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

**6. Pusta kategoria**

Użytkownik robi:

```bash
python budget.py add --amount 100 --category "" --description "Test"
# Wyświetla: "BŁĄD: Kategoria nie może być pusta"
# Exit code: 1
```

```

Dostaje komunikat:
```

BŁĄD: Kategoria nie może być pusta

```
Exit code: 1

---

## STRUKTURA FINALNA PROJEKTU

```

PROJEKT/
├── budget.py # Single-file MVP (~300-350 linii z komentarzami)
├── data/
│ ├── data.json # Auto-created przy pierwszym uruchomieniu
│ └── data.json.bak # Auto-created przed zapisem (jeśli plik istnieje)
└── specs/
├── brief.v3.technology.md
├── brief.v4.etaps.md
└── plan.md # Ten dokument

```

**Single-file architecture**: Cały kod w `budget.py`, zorganizowany w sekcje oznaczone komentarzami.

**Kolejność sekcji w budget.py**:
1. Importy
2. `# === CONSTANTS ===`
3. `# === STORAGE ===`
4. `# === VALIDATION ===`
5. `# === TRANSACTIONS ===`
6. `# === DISPLAY ===`
7. `# === FIXED COSTS ===`
8. `# === MAIN ===`

---

## PODSUMOWANIE RÓŻNIC WZGLĘDEM BRIEFU

**Decyzje projektowe (potwierdzone przez użytkownika):**

1. **Backup timing**: PRZED ZAPISEM (w save_data), nie przy starcie aplikacji
2. **Walidacja kwot**: Przyjmuje float, obliczenia używają Decimal
3. **Ujemne kwoty**: NIE akceptujemy (dodana walidacja amount > 0)
4. **Fixed_costs przykłady**: Są TYLKO DO TESTÓW (dodany komentarz w kodzie)
5. **Organizacja kodu**: Sekcje z komentarzami (# === NAZWA ===)
6. **Reguły integracji**: Każdy etap dodaje kod, nie modyfikuje poprzednich (z wyjątkiem ETAPU 3)
```
