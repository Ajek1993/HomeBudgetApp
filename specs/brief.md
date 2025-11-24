ULEPSZONY BRIEF - BUDGET CLI (MVP)
Co boli:
Brak szybkiej wiedzy "ile mi zostało do końca miesiąca" oraz konieczność ręcznego, powtarzalnego wpisywania stałych opłat (czynsz, rachunki), co zniechęca do prowadzenia budżetu.

Dla kogo:
Dla Ciebie (backend developera na Windows) oraz Twoich agentów AI (do automatyzacji wpisów).

Dlaczego CLI:
Zapewnia najszybszy interfejs dla człowieka (tryb interaktywny) i jedyny ustandaryzowany interfejs dla AI (flagi/argumenty), działając natywnie w terminalu Windows bez GUI.

Core funkcja MVP (Krok po kroku):

Init & Backup: Przy każdym uruchomieniu skrypt sprawdza data.json. Jeśli istnieje – robi kopię data.json.bak. Jeśli nie – tworzy pustą strukturę.

Add Transaction: Komenda dodająca wpis (kwota, kategoria, opis, data=dziś).

Logika: Pobiera dane -> Waliduje, czy kwota to liczba -> Doppisuje do tablicy transactions w JSON -> Zapisuje plik.

Check Status: Komenda wyświetlająca: Limit Miesięczny vs Suma Wydatków (bieżący m-c) = Pozostało.

Apply Fixed: Komenda "Wstaw koszty stałe".

Logika: Pobiera zdefiniowane w JSON szablony kosztów stałych -> Kopiuje je jako nowe transakcje z dzisiejszą datą -> Zapisuje. (Ręczne wywołanie jest bezpieczniejsze w MVP niż zgadywanie "czy to już nowy miesiąc").

List by Category: Proste wyświetlenie sumy wydatków pogrupowane po kategoriach dla obecnego miesiąca.

Edge cases (4 najważniejsze):

Uszkodzony JSON: Plik istnieje, ale ma błędną składnię (ręczna edycja). Aplikacja musi to wykryć i nie nadpisać go, tylko zgłosić błąd.

Błędny typ danych: Użytkownik wpisuje "sto złotych" zamiast "100.00".

Brak pliku danych: Pierwsze uruchomienie na czystym systemie.

Concurrency (Windows): Próba zapisu, gdy plik jest otwarty w Notatniku/Excelu (PermissionError).

Czego NIE robimy w MVP (Lista cięć):

Brak SQLite: Zostajemy przy JSON.

Brak edycji/usuwania pojedynczych wpisów przez CLI: Jeśli się pomylisz, edytujesz plik JSON ręcznie lub dodajesz transakcję korygującą (minusową). Implementacja edit/delete po ID to za dużo kodu na start.

Brak automatyzacji dat: Nie wykrywamy "nowego miesiąca" automagicznie. Uruchamiasz apply-fixed ręcznie raz w miesiącu.

Brak kolorów i tabelek: Zwykły tekstowy output. Formatowanie markdown-like wystarczy.

Brak "Planowania Przyszłości" w logice budżetu: "Planowany wydatek" to w MVP tylko notatka w JSON (osobna lista), nie wpływa na obliczenia "ile zostało", póki nie stanie się faktycznym wydatkiem.
