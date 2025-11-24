# ETAPY REALIZACJI - BUDGET CLI (MVP)

## ETAP 1: JSON Storage

**Co robi**: Obsługuje odczyt, zapis i backup pliku data.json z walidacją.

**Input**: Ścieżka do pliku (`data/data.json`)
**Output**: Struktura dict Pythona lub rzucenie wyjątku (JSONDecodeError, PermissionError)
**Test**:

```bash
python -c "from core.storage import load_data; print(load_data())"
# Zwraca: {'limit': 3000, 'transactions': [], 'fixed_costs': []}
# Jeśli plik nie istnieje - tworzy go. Jeśli uszkodzony - error.
```

---

## ETAP 2: Add Transaction

**Co robi**: Dodaje pojedynczą transakcję do listy i zapisuje JSON.

**Input**: Kwota (Decimal), kategoria (str), opis (str), data (opcjonalnie)
**Output**: Zaktualizowany data.json z nową transakcją
**Test**:

```bash
python budget.py add --amount 150.50 --category "Jedzenie" --description "Biedronka"
# Plik data.json zawiera nowy wpis w transactions[]
# Wyświetla: "✓ Dodano 150.50 PLN (Jedzenie)"
```

---

## ETAP 3: Status Budżetu

**Co robi**: Oblicza i wyświetla: Limit - Suma wydatków bieżącego miesiąca = Pozostało.

**Input**: data.json (limit, transactions)
**Output**: Tekst w formacie:

```
Limit: 3000.00 PLN
Wydano (2025-11): 1245.80 PLN
Pozostało: 1754.20 PLN
```

**Test**:

```bash
python budget.py status
# Pokazuje podsumowanie bez błędów
```

---

## ETAP 4: Apply Fixed Costs

**Co robi**: Kopiuje szablony z `fixed_costs` jako nowe transakcje z dzisiejszą datą.

**Input**: Lista fixed_costs z data.json
**Output**: Nowe wpisy w transactions[] (czynsz, rachunki, etc.)
**Test**:

```bash
python budget.py apply-fixed
# Wyświetla: "✓ Dodano 5 kosztów stałych (1850.00 PLN)"
# transactions[] zawiera wpisy z datą dzisiejszą
```

---

## ETAP 5: List by Category

**Co robi**: Grupuje wydatki obecnego miesiąca po kategoriach i sumuje.

**Input**: transactions[] z data.json
**Output**: Tekstowa lista:

```
Jedzenie: 450.80 PLN
Transport: 120.00 PLN
Mieszkanie: 1850.00 PLN
```

**Test**:

```bash
python budget.py list
# Pokazuje kategorie z sumami bez błędów
```

---

## KOLEJNOŚĆ REALIZACJI

1. **ETAP 1** (JSON Storage) - Fundament, bez tego nic nie działa
2. **ETAP 2** (Add Transaction) - Pierwsza widoczna funkcja
3. **ETAP 3** (Status) - Główny use case ("ile mi zostało")
4. **ETAP 4** (Apply Fixed) - Rozwiązuje główny pain point (ręczne wpisy)
5. **ETAP 5** (List by Category) - Nice-to-have, analiza wydatków

---

## ETAP KRYTYCZNY

**ETAP 1 (JSON Storage)** - Bez tego żaden inny etap nie zadziała. Obsługuje wszystkie edge cases (uszkodzony JSON, brak pliku, PermissionError).

---

## ETAP DO POMINIĘCIA W PIERWSZEJ WERSJI

**ETAP 5 (List by Category)** - Można obejść się bez grupowania. Status (Etap 3) + ręczne przeglądanie JSON wystarczy do weryfikacji MVP. Dodać jako pierwsze ulepszenie po udanych testach.

---

## UPROSZCZENIA (jeszcze bardziej minimalna wersja):

Jeśli chcesz **3 działające etapy zamiast 5**:

### Wariant "Ultra-MVP":

1. **JSON Storage** (krytyczny)
2. **Add Transaction** (dodawanie ręczne + z apply-fixed w jednym)
3. **Status Budżetu** (główny use case)

W tej wersji:

- Apply-fixed to po prostu pre-defined komendy `add` (skrypt bash lub alias)
- List by category odłożone do v2
- 3 etapy = ~150 linii kodu total
