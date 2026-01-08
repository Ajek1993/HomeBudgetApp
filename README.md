# Home Budget App

Prosta aplikacja CLI do zarządzania budżetem domowym.

## Opis

Home Budget App to narzędzie wiersza poleceń, które pomaga śledzić wydatki, zarządzać budżetem miesięcznym oraz monitorować koszty stałe. Wszystkie dane są przechowywane lokalnie w formacie JSON.

## Funkcje

- Śledzenie transakcji z kategoriami i opisami
- Edycja i usuwanie transakcji
- Zarządzanie limitami miesięcznymi przez CLI
- Różne limity dla różnych miesięcy
- Automatyczne dodawanie kosztów stałych 1-go dnia każdego miesiąca
- Zarządzanie kosztami stałymi przez CLI (dodawanie, edycja, usuwanie)
- Rozszerzone informacje o budżecie (średnie dzienne wydatki, sugerowany budżet)
- Podgląd statusu budżetu (ile wydano, ile pozostało)
- Grupowanie wydatków po kategoriach
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

### Sprawdzenie statusu budżetu

```bash
python budget.py status
```

Wyświetla:
- Ustawiony limit miesięczny
- Suma wydatków w bieżącym miesiącu
- Pozostała kwota do wydania

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
  ]
}
```

### Opis pól:

- `limits` - słownik limitów dla różnych miesięcy, `default` to domyślny limit
- `auto_apply_fixed_costs` - czy automatycznie dodawać koszty stałe (domyślnie `true`)
- `applied_fixed_costs_months` - lista miesięcy, w których już dodano koszty stałe
- `next_transaction_id` - następny ID dla nowej transakcji
- `transactions` - lista wszystkich transakcji
- `next_fixed_cost_id` - następny ID dla nowego kosztu stałego
- `fixed_costs` - lista kosztów stałych

## Bezpieczeństwo danych

- Przy każdym zapisie tworzony jest plik kopii zapasowej (`data/data.json.bak`)
- Automatyczna migracja starych danych do nowego formatu
- Walidacja struktury danych przy wczytywaniu
- Obsługa błędów przy uszkodzonych plikach

## Przykładowy przepływ pracy

1. Ustaw domyślny limit: `python budget.py set-limit 5000`
2. Dodaj koszty stałe:
   ```bash
   python budget.py fixed-add --amount 1200 --category "Czynsz" --description "Miesięczny czynsz"
   python budget.py fixed-add --amount 150 --category "Internet" --description "Abonament"
   ```
3. Koszty stałe zostaną automatycznie dodane 1-go dnia miesiąca przy pierwszym uruchomieniu
4. Dodawaj transakcje na bieżąco:
   ```bash
   python budget.py add --amount 50 --category "Jedzenie" --description "Zakupy"
   ```
5. Sprawdzaj stan budżetu:
   ```bash
   python budget.py status --detailed
   ```
6. Przeglądaj wydatki po kategoriach:
   ```bash
   python budget.py list
   ```
7. Zarządzaj transakcjami:
   ```bash
   python budget.py transactions  # zobacz listę z ID
   python budget.py edit <id> --amount 60  # edytuj
   python budget.py delete <id>  # usuń
   ```

## Kompatybilność wsteczna

Aplikacja automatycznie migruje stare pliki `data.json` do nowego formatu przy pierwszym uruchomieniu. Kopia zapasowa jest tworzona przed migracją.

## Licencja

Ten projekt jest dostępny na licencji MIT.
