# Home Budget App

Kompleksowa aplikacja CLI do zarządzania budżetem domowym - wydatki, przychody i saldo w jednym miejscu.

## Opis

Home Budget App to kompleksowe narzędzie wiersza poleceń do zarządzania budżetem domowym. Aplikacja pozwala śledzić zarówno wydatki jak i przychody, monitorować saldo portfela oraz zarządzać budżetem miesięcznym. Obsługuje koszty stałe i przychody cykliczne, które są automatycznie dodawane każdego miesiąca. Wszystkie dane są przechowywane lokalnie w formacie JSON z automatycznymi kopiami zapasowymi.

## Funkcje

### Zarządzanie wydatkami
- Śledzenie transakcji z kategoriami i opisami
- Edycja i usuwanie transakcji
- Zarządzanie limitami miesięcznymi przez CLI
- Różne limity dla różnych miesięcy
- Automatyczne dodawanie kosztów stałych 1-go dnia każdego miesiąca
- Zarządzanie kosztami stałymi przez CLI (dodawanie, edycja, usuwanie)
- Grupowanie wydatków po kategoriach

### Zarządzanie przychodami
- Zarządzanie saldem portfela
- Przychody cykliczne (miesięczne, np. wypłata)
- Przychody jednorazowe (np. premia, zwrot)
- Automatyczne dodawanie przychodów cyklicznych 1-go dnia każdego miesiąca
- Śledzenie bilansu miesięcznego (przychody - wydatki)

### Informacje i analizy
- Rozszerzone informacje o budżecie (średnie dzienne wydatki, sugerowany budżet)
- Podgląd statusu budżetu z saldem portfela
- Szczegółowe zestawienia przychodów i wydatków

### Bezpieczeństwo
- Automatyczne tworzenie kopii zapasowych danych
- Automatyczna migracja danych do nowego formatu

## Wymagania

- Python 3.6+

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone <repository-url>
cd HomeBudgetApp
```

2. Uruchom aplikację:
```bash
python budget.py --help
```

## Użycie

### Sprawdzenie statusu budżetu i salda

Podstawowy status:
```bash
python budget.py status
```

Wyświetla:
- Obecne saldo portfela
- Ustawiony limit miesięczny
- Suma wydatków w bieżącym miesiącu
- Pozostała kwota do wydania
- Przychody w bieżącym miesiącu
- Bilans miesiąca (przychody - wydatki)

Szczegółowy status:
```bash
python budget.py status --detailed
```

Wyświetla dodatkowo:
- Dni w miesiącu / upłynęło / pozostało
- Średnie wydatki dziennie
- Sugerowany budżet dzienny na pozostałe dni

### Zarządzanie transakcjami

Dodawanie transakcji:
```bash
python budget.py add --amount 50.00 --category "Jedzenie" --description "Zakupy w sklepie"
```

Opcjonalnie można podać datę:
```bash
python budget.py add --amount 50.00 --category "Jedzenie" --description "Zakupy" --date 2026-01-15
```

Wyświetlanie listy transakcji:
```bash
python budget.py transactions
```

Wyświetlanie transakcji dla konkretnego miesiąca:
```bash
python budget.py transactions --month 2025-12
```

Edycja transakcji:
```bash
python budget.py edit <id> --amount 60.00 --category "Transport" --description "Taxi"
```

Usuwanie transakcji:
```bash
python budget.py delete <id>
```

### Zarządzanie limitami

Ustawienie domyślnego limitu:
```bash
python budget.py set-limit 5000
```

Ustawienie limitu dla konkretnego miesiąca:
```bash
python budget.py set-limit 6000 --month 2026-02
```

Wyświetlanie historii limitów:
```bash
python budget.py limits
```

### Zarządzanie kosztami stałymi

Wyświetlanie listy kosztów stałych:
```bash
python budget.py fixed-list
```

Dodawanie nowego kosztu stałego:
```bash
python budget.py fixed-add --amount 1200 --category "Czynsz" --description "Miesięczny czynsz"
```

Edycja kosztu stałego:
```bash
python budget.py fixed-edit <id> --amount 1300 --description "Czynsz + media"
```

Usuwanie kosztu stałego:
```bash
python budget.py fixed-delete <id>
```

Ręczne dodanie kosztów stałych jako transakcji:
```bash
python budget.py apply-fixed
```

Uwaga: Koszty stałe są automatycznie dodawane 1-go dnia każdego miesiąca przy pierwszym uruchomieniu aplikacji w tym miesiącu.

### Zarządzanie saldem portfela

Ustawienie początkowego salda:
```bash
python budget.py set-balance 10000
```

Sprawdzenie obecnego salda:
```bash
python budget.py balance
```

Szczegółowe saldo z rozpisaniem:
```bash
python budget.py balance --detailed
```

Wyświetla:
- Początkowe saldo
- Suma wszystkich przychodów
- Suma wszystkich wydatków
- Obecne saldo

### Zarządzanie przychodami cyklicznymi

Wyświetlanie listy przychodów cyklicznych:
```bash
python budget.py recurring-list
```

Dodawanie nowego przychodu cyklicznego (np. wypłata):
```bash
python budget.py recurring-add --amount 5000 --description "Wypłata"
```

Edycja przychodu cyklicznego:
```bash
python budget.py recurring-edit <id> --amount 5500 --description "Nowa wypłata"
```

Usuwanie przychodu cyklicznego:
```bash
python budget.py recurring-delete <id>
```

Ręczne dodanie przychodów cyklicznych jako wpisy jednorazowe:
```bash
python budget.py apply-recurring-income
```

Uwaga: Przychody cykliczne są automatycznie dodawane jako wpisy jednorazowe 1-go dnia każdego miesiąca przy pierwszym uruchomieniu aplikacji w tym miesiącu.

### Zarządzanie przychodami jednorazowymi

Dodawanie przychodu jednorazowego:
```bash
python budget.py income-add --amount 1200 --description "Premia"
```

Opcjonalnie można podać datę:
```bash
python budget.py income-add --amount 1200 --description "Premia" --date 2026-01-15
```

Wyświetlanie listy przychodów:
```bash
python budget.py income-list
```

Wyświetlanie przychodów dla konkretnego miesiąca:
```bash
python budget.py income-list --month 2026-01
```

Edycja przychodu:
```bash
python budget.py income-edit <id> --amount 1500 --description "Zwiększona premia"
```

Usuwanie przychodu:
```bash
python budget.py income-delete <id>
```

### Lista wydatków po kategoriach

```bash
python budget.py list
```

Wyświetla sumę wydatków dla każdej kategorii w bieżącym miesiącu.

## Struktura danych

Dane są przechowywane w pliku `data/data.json`:

```json
{
  "limits": {
    "default": 5000,
    "2026-01": 5500,
    "2026-02": 6000
  },
  "auto_apply_fixed_costs": true,
  "applied_fixed_costs_months": ["2026-01"],
  "next_transaction_id": 10,
  "transactions": [
    {
      "id": 1,
      "date": "2026-01-02",
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
  ],
  "initial_balance": 10000.0,
  "next_income_id": 4,
  "recurring_income": [
    {
      "id": 1,
      "amount": 5000.0,
      "description": "Wypłata"
    }
  ],
  "one_time_income": [
    {
      "id": 2,
      "date": "2026-01-01",
      "amount": 5000.0,
      "description": "Wypłata"
    },
    {
      "id": 3,
      "date": "2026-01-15",
      "amount": 1200.0,
      "description": "Premia"
    }
  ],
  "auto_apply_recurring_income": true,
  "applied_recurring_income_months": ["2026-01"]
}
```

### Opis pól:

#### Wydatki i limity:
- `limits` - słownik limitów dla różnych miesięcy, `default` to domyślny limit
- `auto_apply_fixed_costs` - czy automatycznie dodawać koszty stałe (domyślnie `true`)
- `applied_fixed_costs_months` - lista miesięcy, w których już dodano koszty stałe
- `next_transaction_id` - następny ID dla nowej transakcji
- `transactions` - lista wszystkich transakcji
- `next_fixed_cost_id` - następny ID dla nowego kosztu stałego
- `fixed_costs` - lista kosztów stałych

#### Przychody i saldo:
- `initial_balance` - początkowe saldo portfela
- `next_income_id` - następny ID dla nowego przychodu
- `recurring_income` - lista przychodów cyklicznych (miesięcznych)
- `one_time_income` - lista przychodów jednorazowych
- `auto_apply_recurring_income` - czy automatycznie dodawać przychody cykliczne (domyślnie `true`)
- `applied_recurring_income_months` - lista miesięcy, w których już dodano przychody cykliczne

## Bezpieczeństwo danych

- Przy każdym zapisie tworzony jest plik kopii zapasowej (`data/data.json.bak`)
- Automatyczna migracja starych danych do nowego formatu
- Walidacja struktury danych przy wczytywaniu
- Obsługa błędów przy uszkodzonych plikach

## Przykładowy przepływ pracy

### Początkowa konfiguracja:

1. Ustaw początkowe saldo portfela:
   ```bash
   python budget.py set-balance 10000
   ```

2. Ustaw domyślny limit miesięczny:
   ```bash
   python budget.py set-limit 5000
   ```

3. Dodaj przychody cykliczne (miesięczne):
   ```bash
   python budget.py recurring-add --amount 5000 --description "Wypłata"
   ```

4. Dodaj koszty stałe:
   ```bash
   python budget.py fixed-add --amount 1200 --category "Czynsz" --description "Miesięczny czynsz"
   python budget.py fixed-add --amount 150 --category "Internet" --description "Abonament"
   python budget.py fixed-add --amount 80 --category "Telefon" --description "Telefon"
   ```

### Codzienna praca:

5. Przy pierwszym uruchomieniu miesiąca, automatycznie:
   - Dodają się przychody cykliczne jako wpisy jednorazowe
   - Dodają się koszty stałe jako transakcje

6. Dodawaj przychody jednorazowe gdy otrzymasz:
   ```bash
   python budget.py income-add --amount 1200 --description "Premia"
   ```

7. Dodawaj transakcje na bieżąco:
   ```bash
   python budget.py add --amount 50 --category "Jedzenie" --description "Zakupy"
   python budget.py add --amount 35 --category "Jedzenie" --description "Kebab"
   ```

8. Sprawdzaj stan budżetu i salda:
   ```bash
   python budget.py status --detailed
   python budget.py balance
   ```

9. Przeglądaj wydatki po kategoriach:
   ```bash
   python budget.py list
   ```

10. Zarządzaj transakcjami:
    ```bash
    python budget.py transactions  # zobacz listę z ID
    python budget.py edit <id> --amount 60  # edytuj
    python budget.py delete <id>  # usuń
    ```

11. Zarządzaj przychodami:
    ```bash
    python budget.py income-list  # zobacz listę przychodów
    python budget.py income-edit <id> --amount 1500  # edytuj
    python budget.py income-delete <id>  # usuń
    ```

## Kompatybilność wsteczna

Aplikacja automatycznie migruje stare pliki `data.json` do nowego formatu przy pierwszym uruchomieniu. Kopia zapasowa jest tworzona przed migracją.

## Licencja

Ten projekt jest dostępny na licencji MIT.
