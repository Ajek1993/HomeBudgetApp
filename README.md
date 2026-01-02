# Home Budget App

Prosta aplikacja CLI do zarządzania budżetem domowym.

## Opis

Home Budget App to narzędzie wiersza poleceń, które pomaga śledzić wydatki, zarządzać budżetem miesięcznym oraz monitorować koszty stałe. Wszystkie dane są przechowywane lokalnie w formacie JSON.

## Funkcje

- Śledzenie transakcji z kategoriami i opisami
- Ustawianie miesięcznego limitu wydatków
- Automatyczne dodawanie kosztów stałych
- Podgląd statusu budżetu (ile wydano, ile pozostało)
- Grupowanie wydatków po kategoriach
- Automatyczne tworzenie kopii zapasowych danych

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

### Dodawanie transakcji

```bash
python budget.py add --amount 50.00 --category "Jedzenie" --description "Zakupy w sklepie"
```

Opcjonalnie można podać datę:
```bash
python budget.py add --amount 50.00 --category "Jedzenie" --description "Zakupy" --date 2025-01-01
```

### Lista wydatków po kategoriach

```bash
python budget.py list
```

Wyświetla sumę wydatków dla każdej kategorii w bieżącym miesiącu.

### Dodawanie kosztów stałych

```bash
python budget.py apply-fixed
```

Dodaje wszystkie zdefiniowane koszty stałe jako transakcje z dzisiejszą datą.

## Struktura danych

Dane są przechowywane w pliku `data/data.json`:

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

### Edycja limitu i kosztów stałych

Limit miesięczny oraz koszty stałe można edytować bezpośrednio w pliku `data/data.json`.

## Bezpieczeństwo danych

- Przy każdym zapisie tworzony jest plik kopii zapasowej (`data/data.json.bak`)
- Walidacja struktury danych przy wczytywaniu
- Obsługa błędów przy uszkodzonych plikach

## Przykładowy przepływ pracy

1. Ustaw limit miesięczny w `data/data.json`
2. Dodaj koszty stałe do sekcji `fixed_costs`
3. Na początku miesiąca uruchom `python budget.py apply-fixed`
4. Dodawaj transakcje na bieżąco: `python budget.py add ...`
5. Sprawdzaj stan budżetu: `python budget.py status`
6. Przeglądaj wydatki po kategoriach: `python budget.py list`

## Licencja

Ten projekt jest dostępny na licencji MIT.
