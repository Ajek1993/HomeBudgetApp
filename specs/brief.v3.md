# ULEPSZONY BRIEF - BUDGET CLI (MVP)

## Co boli:
Brak szybkiej wiedzy "ile mi zostało do końca miesiąca" oraz konieczność ręcznego, powtarzalnego wpisywania stałych opłat (czynsz, rachunki), co zniechęca do prowadzenia budżetu.

## Dla kogo:
Dla Ciebie (backend developera na Windows) oraz Twoich agentów AI (do automatyzacji wpisów).

## Dlaczego CLI:
Zapewnia najszybszy interfejs dla człowieka (tryb interaktywny) i jedyny ustandaryzowany interfejs dla AI (flagi/argumenty), działając natywnie w terminalu Windows bez GUI.

## Core funkcja MVP (Krok po kroku):

### Init & Backup
Przy każdym uruchomieniu skrypt sprawdza data.json. Jeśli istnieje – robi kopię data.json.bak. Jeśli nie – tworzy pustą strukturę.

### Add Transaction
Komenda dodająca wpis (kwota, kategoria, opis, data=dziś).

**Logika**: Pobiera dane -> Waliduje, czy kwota to liczba -> Doppisuje do tablicy transactions w JSON -> Zapisuje plik.

### Check Status
Komenda wyświetlająca: Limit Miesięczny vs Suma Wydatków (bieżący m-c) = Pozostało.

### Apply Fixed
Komenda "Wstaw koszty stałe".

**Logika**: Pobiera zdefiniowane w JSON szablony kosztów stałych -> Kopiuje je jako nowe transakcje z dzisiejszą datą -> Zapisuje. (Ręczne wywołanie jest bezpieczniejsze w MVP niż zgadywanie "czy to już nowy miesiąc").

### List by Category
Proste wyświetlenie sumy wydatków pogrupowane po kategoriach dla obecnego miesiąca.

## Edge cases (4 najważniejsze):

- **Uszkodzony JSON**: Plik istnieje, ale ma błędną składnię (ręczna edycja). Aplikacja musi to wykryć i nie nadpisać go, tylko zgłosić błąd.

- **Błędny typ danych**: Użytkownik wpisuje "sto złotych" zamiast "100.00".

- **Brak pliku danych**: Pierwsze uruchomienie na czystym systemie.

- **Concurrency (Windows)**: Próba zapisu, gdy plik jest otwarty w Notatniku/Excelu (PermissionError).

## Czego NIE robimy w MVP (Lista cięć):

- **Brak SQLite**: Zostajemy przy JSON.

- **Brak edycji/usuwania pojedynczych wpisów przez CLI**: Jeśli się pomylisz, edytujesz plik JSON ręcznie lub dodajesz transakcję korygującą (minusową). Implementacja edit/delete po ID to za dużo kodu na start.

- **Brak automatyzacji dat**: Nie wykrywamy "nowego miesiąca" automagicznie. Uruchamiasz apply-fixed ręcznie raz w miesiącu.

- **Brak kolorów i tabelek**: Zwykły tekstowy output. Formatowanie markdown-like wystarczy.

- **Brak "Planowania Przyszłości" w logice budżetu**: "Planowany wydatek" to w MVP tylko notatka w JSON (osobna lista), nie wpływa na obliczenia "ile zostało", póki nie stanie się faktycznym wydatkiem.

---

## TECHNOLOGIA

### Dlaczego Python pasuje do tego projektu
Python idealnie nadaje się do tego MVP: wbudowane moduły JSON/datetime/argparse eliminują zależności zewnętrzne, natywna obsługa wyjątków dopasowana do edge cases (JSONDecodeError, PermissionError), a szybki rozwój prototypu bez kompilacji pasuje do iteracyjnego podejścia CLI.

### Biblioteki

#### STDLIB (wbudowane, preferowane):
- **json**: Parsing i zapis data.json, natywna obsługa JSONDecodeError
- **datetime**: Automatyczne ustawienie daty "dziś", filtrowanie transakcji po miesiącu
- **argparse**: Parsing komend CLI (add, status, apply-fixed, list), flagi i argumenty
- **shutil**: Atomic backup data.json → data.json.bak
- **pathlib**: Bezpieczne operacje na ścieżkach (Path.exists(), Path.read_text())
- **sys**: Wyjście z kodem błędu (sys.exit(1)) dla skryptów/agentów AI
- **decimal**: Precyzyjne operacje na kwotach (unikanie błędów float)

#### ZEWNĘTRZNE (tylko jeśli stdlib nie wystarczy):
**BRAK** - Wszystkie wymagania MVP pokrywa stdlib. Kolorowanie terminala (colorama) lub tabelki (tabulate) odrzucone zgodnie z "Czego NIE robimy" (zwykły tekstowy output).

### Struktura plików (minimalna, dla MVP):

```
PROJEKT/
├── budget.py          # Main entry point (argparse CLI router)
├── core/
│   ├── __init__.py
│   ├── storage.py     # JSON: load, save, backup, validation
│   ├── transaction.py # Add, filter, group by category/month
│   └── display.py     # Format output (status, list)
├── data/
│   └── data.json      # Dane (auto-created)
└── specs/
    └── brief.v3.md    # Ten dokument
```

**Alternatywa single-file** (dla maksymalnej prostoty MVP):
```
PROJEKT/
├── budget.py          # Cały kod w jednym pliku (~200-300 linii)
├── data/
│   └── data.json
└── specs/
```

### Jak uruchomić (komendy):

```bash
# Dodanie transakcji (interaktywne lub z flagami)
python budget.py add --amount 150.50 --category "Jedzenie" --description "Zakupy Biedronka"

# Status budżetu (ile zostało)
python budget.py status

# Wstawienie kosztów stałych (czynsz, rachunki)
python budget.py apply-fixed

# Lista wydatków po kategoriach (obecny miesiąc)
python budget.py list

# Dla agentów AI - wszystkie parametry w jednej linii
python budget.py add --amount 45.00 --category "Transport" --description "Uber"
```

### Obsługa edge cases (mapowanie do Python):

| Edge Case | Rozwiązanie Python |
|-----------|-------------------|
| Uszkodzony JSON | `try: json.loads()` → `except json.JSONDecodeError` → Blokada zapisu + error message |
| Błędny typ (kwota) | `Decimal(input)` w `try/except ValueError` + komunikat "Podaj liczbę" |
| Brak pliku | `if not Path('data.json').exists()` → Utwórz pusty template |
| PermissionError | `try: file.write()` → `except PermissionError` → "Zamknij plik w edytorze" |

### Decyzje implementacyjne:

1. **Single-file vs modular**: Start od `budget.py` (1 plik), refactor do `core/*` gdy przekroczy 300 linii
2. **Atomic writes**: `shutil.copy2()` dla backupu + `json.dump()` z `atomic_write=False` (brak race conditions w MVP single-user)
3. **Data validation**: Pydantic odrzucony (zewnętrzna lib), validacja ręczna przez `isinstance()` i `Decimal`
4. **Error handling**: Explicit `sys.exit(1)` z error message dla każdego edge case (czytelne dla AI agents)
