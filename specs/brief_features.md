# Plan implementacji nowych funkcji - Home Budget App

## Przegląd

Dokument opisuje plan implementacji nowych funkcji dla aplikacji Home Budget App. Wszystkie dane będą nadal przechowywane lokalnie w pliku JSON (`data/data.json`).

## Obecna struktura aplikacji

### Istniejące komendy CLI:
- `status` - pokazuje limit, wydane i pozostałe środki w bieżącym miesiącu
- `add` - dodaje nową transakcję
- `list` - pokazuje wydatki pogrupowane po kategoriach
- `apply-fixed` - ręcznie dodaje wszystkie koszty stałe

### Struktura danych (data/data.json):
```json
{
  "limit": 5000,
  "transactions": [
    {
      "date": "2025-01-02",
      "amount": 50.00,
      "category": "Jedzenie",
      "description": "Zakupy w sklepie"
    }
  ],
  "fixed_costs": [
    {
      "amount": 1200,
      "category": "Czynsz",
      "description": "Miesięczny czynsz"
    }
  ]
}
```

---

## Nowe funkcje do zaimplementowania

### 1. Edycja i usuwanie transakcji

#### Funkcje:
- Edycja istniejących transakcji (kwota, kategoria, opis, data)
- Usuwanie transakcji

#### Komendy CLI:
```bash
# Lista wszystkich transakcji z ID
python budget.py transactions [--month YYYY-MM]

# Edycja transakcji
python budget.py edit <transaction_id> [--amount X] [--category "Y"] [--description "Z"] [--date YYYY-MM-DD]

# Usunięcie transakcji
python budget.py delete <transaction_id>
```

#### Modyfikacje struktury danych:
- Dodać pole `"id"` do każdej transakcji (unikalny identyfikator)
- Dodać pole `"next_transaction_id"` w głównej strukturze do śledzenia kolejnych ID

```json
{
  "next_transaction_id": 5,
  "transactions": [
    {
      "id": 1,
      "date": "2025-01-02",
      "amount": 50.00,
      "category": "Jedzenie",
      "description": "Zakupy"
    }
  ]
}
```

#### Implementacja:
1. Dodać funkcję `add_transaction_id()` - dodaje ID do transakcji bez ID (migracja danych)
2. Zmodyfikować `add_transaction()` - automatycznie przypisuje ID nowej transakcji
3. Dodać funkcję `find_transaction_by_id(data, transaction_id)` - wyszukuje transakcję
4. Dodać funkcję `edit_transaction(data, transaction_id, **kwargs)` - edytuje transakcję
5. Dodać funkcję `delete_transaction(data, transaction_id)` - usuwa transakcję
6. Dodać funkcję `format_transactions_list(transactions)` - formatuje listę transakcji z ID
7. Dodać obsługę komend `transactions`, `edit`, `delete` w głównej funkcji

---

### 2. Ustawienie i edycja limitu miesięcznego przez CLI

#### Funkcje:
- Ustawienie limitu na dany miesiąc
- Edycja limitu dla przyszłych miesięcy
- Możliwość ustawienia różnych limitów dla różnych miesięcy

#### Komendy CLI:
```bash
# Ustawienie limitu dla bieżącego miesiąca
python budget.py set-limit 5000

# Ustawienie limitu dla konkretnego miesiąca
python budget.py set-limit 5000 --month 2025-02

# Pokazanie historii limitów
python budget.py limits
```

#### Modyfikacje struktury danych:
- Zmienić `"limit"` z pojedynczej wartości na słownik miesięcy
- Zachować kompatybilność wsteczną (jeśli `limit` jest liczbą, przekonwertować)

```json
{
  "limits": {
    "default": 5000,
    "2025-01": 5000,
    "2025-02": 6000
  }
}
```

#### Implementacja:
1. Dodać funkcję `migrate_limits(data)` - konwertuje stary format limitu na nowy
2. Dodać funkcję `get_limit_for_month(data, month_str)` - pobiera limit dla danego miesiąca
3. Dodać funkcję `set_limit(data, amount, month_str)` - ustawia limit
4. Zmodyfikować `load_data()` - automatyczna migracja przy wczytywaniu
5. Zmodyfikować komendę `status` - używa nowej funkcji `get_limit_for_month()`
6. Dodać obsługę komend `set-limit` i `limits` w głównej funkcji

---

### 3. Rozszerzone informacje o budżecie

#### Funkcje:
- Pokazanie ile pozostało do końca miesiąca
- Średnie dzienne wydatki
- Sugerowany dzienny budżet na pozostałe dni

#### Komendy CLI:
```bash
# Rozszerzony status z dodatkowymi informacjami
python budget.py status --detailed
```

#### Przykładowy output:
```
=== BUDŻET - STYCZEŃ 2025 ===
Limit: 5000.00 PLN
Wydano: 3200.00 PLN (64%)
Pozostało: 1800.00 PLN (36%)

Dni w miesiącu: 31
Upłynęło dni: 15
Pozostało dni: 16

Średnie wydatki dziennie: 213.33 PLN
Sugerowany budżet dzienny (pozostałe dni): 112.50 PLN
```

#### Implementacja:
1. Dodać funkcję `calculate_detailed_status(limit, spent, month)` - oblicza szczegóły
2. Dodać funkcję `format_detailed_status(...)` - formatuje rozszerzony output
3. Zmodyfikować komendę `status` - dodać flagę `--detailed`

---

### 4. Automatyczne dodawanie kosztów stałych

#### Funkcje:
- Automatyczne dodawanie kosztów stałych 1-go dnia każdego miesiąca
- Śledzenie, które miesiące mają już dodane koszty stałe
- Możliwość ręcznego dodania kosztów stałych (jeśli ktoś uruchomi aplikację później)

#### Komendy CLI:
```bash
# Automatyczne sprawdzenie i dodanie kosztów stałych (uruchamiane przy każdej komendzie)
# Użytkownik może też ręcznie wywołać:
python budget.py apply-fixed
```

#### Modyfikacje struktury danych:
- Dodać pole `"applied_fixed_costs_months"` - lista miesięcy, w których już dodano koszty stałe
- Dodać pole `"auto_apply_fixed_costs"` - flaga, czy automatycznie dodawać (domyślnie true)

```json
{
  "auto_apply_fixed_costs": true,
  "applied_fixed_costs_months": [
    "2025-01",
    "2025-02"
  ],
  "fixed_costs": [...]
}
```

#### Implementacja:
1. Zmodyfikować `apply_fixed_costs(data)`:
   - Sprawdza, czy koszty stałe już zostały dodane w bieżącym miesiącu
   - Dodaje datę jako 1-szy dzień miesiąca
   - Oznacza miesiąc jako "obsłużony" w `applied_fixed_costs_months`
2. Dodać funkcję `auto_apply_fixed_if_needed(data)`:
   - Sprawdza, czy `auto_apply_fixed_costs` jest true
   - Sprawdza, czy obecny miesiąc jest w `applied_fixed_costs_months`
   - Jeśli nie, wywołuje `apply_fixed_costs()`
3. Dodać wywołanie `auto_apply_fixed_if_needed()` w `load_data()` - przed zwróceniem danych
4. Zmodyfikować `apply_fixed_costs()` - data transakcji to 1-szy dzień miesiąca

---

### 5. Zarządzanie kosztami stałymi przez CLI

#### Funkcje:
- Wyświetlanie listy kosztów stałych
- Dodawanie nowego kosztu stałego
- Edycja kosztu stałego (wpływ tylko na przyszłe transakcje)
- Usuwanie kosztu stałego

#### Komendy CLI:
```bash
# Lista kosztów stałych
python budget.py fixed-list

# Dodanie nowego kosztu stałego
python budget.py fixed-add --amount 1200 --category "Czynsz" --description "Miesięczny czynsz"

# Edycja kosztu stałego
python budget.py fixed-edit <fixed_cost_id> [--amount X] [--category "Y"] [--description "Z"]

# Usunięcie kosztu stałego
python budget.py fixed-delete <fixed_cost_id>
```

#### Modyfikacje struktury danych:
- Dodać pole `"id"` do każdego kosztu stałego
- Dodać pole `"next_fixed_cost_id"` w głównej strukturze

```json
{
  "next_fixed_cost_id": 3,
  "fixed_costs": [
    {
      "id": 1,
      "amount": 1200,
      "category": "Czynsz",
      "description": "Miesięczny czynsz"
    },
    {
      "id": 2,
      "amount": 150,
      "category": "Internet",
      "description": "Abonament internetowy"
    }
  ]
}
```

#### Implementacja:
1. Dodać funkcję `add_fixed_cost_id(data)` - migracja danych
2. Dodać funkcję `add_fixed_cost(data, amount, category, description)` - dodaje nowy koszt stały
3. Dodać funkcję `find_fixed_cost_by_id(data, fixed_cost_id)` - wyszukuje koszt stały
4. Dodać funkcję `edit_fixed_cost(data, fixed_cost_id, **kwargs)` - edytuje koszt stały
5. Dodać funkcję `delete_fixed_cost(data, fixed_cost_id)` - usuwa koszt stały
6. Dodać funkcję `format_fixed_costs_list(fixed_costs)` - formatuje listę
7. Dodać obsługę komend `fixed-list`, `fixed-add`, `fixed-edit`, `fixed-delete`

---

## Etapy implementacji

### Etap 1: Rozszerzenie struktury danych i migracja
**Pliki**: `budget.py`

**Zadania**:
1. Dodać funkcję `migrate_data(data)` - główna funkcja migracji
2. Dodać pola do struktury danych:
   - `next_transaction_id` i `id` w transakcjach
   - `next_fixed_cost_id` i `id` w kosztach stałych
   - `limits` (zmiana z pojedynczego `limit`)
   - `applied_fixed_costs_months`
   - `auto_apply_fixed_costs`
3. Zintegrować migrację z `load_data()`
4. Przetestować migrację na istniejącym pliku data.json

**Oczekiwany rezultat**: Aplikacja automatycznie migruje stare dane do nowego formatu przy pierwszym uruchomieniu

---

### Etap 2: Zarządzanie transakcjami
**Pliki**: `budget.py`

**Zadania**:
1. Implementacja funkcji:
   - `find_transaction_by_id()`
   - `edit_transaction()`
   - `delete_transaction()`
   - `format_transactions_list()`
2. Dodanie komend CLI:
   - `transactions` - lista transakcji
   - `edit <id>` - edycja transakcji
   - `delete <id>` - usunięcie transakcji
3. Dodanie walidacji ID transakcji
4. Testy manualne wszystkich operacji

**Oczekiwany rezultat**: Użytkownik może wyświetlić, edytować i usuwać transakcje

---

### Etap 3: Zarządzanie limitami
**Pliki**: `budget.py`

**Zadania**:
1. Implementacja funkcji:
   - `get_limit_for_month()`
   - `set_limit()`
   - `format_limits_list()`
2. Modyfikacja komendy `status` - używa nowej funkcji limitu
3. Dodanie komend CLI:
   - `set-limit <amount> [--month YYYY-MM]`
   - `limits` - historia limitów
4. Testy z różnymi limitami dla różnych miesięcy

**Oczekiwany rezultat**: Użytkownik może ustawiać różne limity dla różnych miesięcy

---

### Etap 4: Automatyczne koszty stałe
**Pliki**: `budget.py`

**Zadania**:
1. Implementacja funkcji:
   - `auto_apply_fixed_if_needed()`
   - Modyfikacja `apply_fixed_costs()` - data 1-szy dzień miesiąca
2. Integracja z `load_data()` - automatyczne sprawdzanie
3. Testy:
   - Sprawdzenie, czy koszty są dodawane tylko raz na miesiąc
   - Sprawdzenie, czy data to 1-szy dzień miesiąca
   - Test ręcznego wywołania `apply-fixed`

**Oczekiwany rezultat**: Koszty stałe są automatycznie dodawane 1-go dnia każdego miesiąca

---

### Etap 5: Zarządzanie kosztami stałymi
**Pliki**: `budget.py`

**Zadania**:
1. Implementacja funkcji:
   - `add_fixed_cost()`
   - `find_fixed_cost_by_id()`
   - `edit_fixed_cost()`
   - `delete_fixed_cost()`
   - `format_fixed_costs_list()`
2. Dodanie komend CLI:
   - `fixed-list`
   - `fixed-add`
   - `fixed-edit <id>`
   - `fixed-delete <id>`
3. Testy wszystkich operacji CRUD na kosztach stałych

**Oczekiwany rezultat**: Użytkownik może zarządzać kosztami stałymi bez edycji pliku JSON

---

### Etap 6: Rozszerzone informacje o budżecie
**Pliki**: `budget.py`

**Zadania**:
1. Implementacja funkcji:
   - `calculate_detailed_status()`
   - `format_detailed_status()`
2. Dodanie flagi `--detailed` do komendy `status`
3. Obliczenia:
   - Liczba dni w miesiącu / upłynęło / pozostało
   - Średnie dzienne wydatki
   - Sugerowany dzienny budżet
4. Testy obliczeń dla różnych scenariuszy

**Oczekiwany rezultat**: Komenda `status --detailed` pokazuje rozszerzone informacje o budżecie

---

### Etap 7: Aktualizacja dokumentacji
**Pliki**: `README.md`

**Zadania**:
1. Aktualizacja sekcji "Funkcje"
2. Dodanie dokumentacji nowych komend CLI
3. Aktualizacja struktury danych w sekcji "Struktura danych"
4. Dodanie przykładów użycia nowych funkcji
5. Aktualizacja "Przykładowego przepływu pracy"

**Oczekiwany rezultat**: README.md odzwierciedla wszystkie nowe funkcje

---

### Etap 8: Testy końcowe
**Zadania**:
1. Test pełnego przepływu pracy z nowymi funkcjami
2. Test migracji na czystych danych
3. Test migracji na istniejących danych
4. Test wszystkich komend CLI
5. Test walidacji i obsługi błędów
6. Test backup'ów i odzyskiwania danych

**Oczekiwany rezultat**: Aplikacja działa stabilnie ze wszystkimi nowymi funkcjami

---

## Kompatybilność wsteczna

Wszystkie zmiany będą zachowywać kompatybilność wsteczną:
- Stare pliki `data.json` zostaną automatycznie zmigrowane przy pierwszym uruchomieniu
- Kopia zapasowa przed migracją zostanie utworzona automatycznie
- Stare komendy będą nadal działać bez zmian

## Podsumowanie nowych komend CLI

```bash
# Transakcje
python budget.py transactions [--month YYYY-MM]
python budget.py edit <id> [--amount X] [--category Y] [--description Z] [--date YYYY-MM-DD]
python budget.py delete <id>

# Limity
python budget.py set-limit <amount> [--month YYYY-MM]
python budget.py limits

# Status
python budget.py status [--detailed]

# Koszty stałe
python budget.py fixed-list
python budget.py fixed-add --amount X --category Y --description Z
python budget.py fixed-edit <id> [--amount X] [--category Y] [--description Z]
python budget.py fixed-delete <id>

# Istniejące (bez zmian)
python budget.py add --amount X --category Y --description Z [--date YYYY-MM-DD]
python budget.py apply-fixed  # Teraz też automatycznie przy pierwszym uruchomieniu w miesiącu
python budget.py list
```

## Struktura danych po wszystkich zmianach

```json
{
  "limits": {
    "default": 5000,
    "2025-01": 5000,
    "2025-02": 6000
  },
  "auto_apply_fixed_costs": true,
  "applied_fixed_costs_months": ["2025-01"],
  "next_transaction_id": 10,
  "transactions": [
    {
      "id": 1,
      "date": "2025-01-02",
      "amount": 50.00,
      "category": "Jedzenie",
      "description": "Zakupy w sklepie"
    }
  ],
  "next_fixed_cost_id": 3,
  "fixed_costs": [
    {
      "id": 1,
      "amount": 1200,
      "category": "Czynsz",
      "description": "Miesięczny czynsz"
    },
    {
      "id": 2,
      "amount": 150,
      "category": "Internet",
      "description": "Abonament internetowy"
    }
  ]
}
```
