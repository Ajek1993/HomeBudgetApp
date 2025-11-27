Chcę sobie stworzyć prostą aplikację CLI, która będzie rozwiązywała mój problem i w kolejnych krokach Ci powiem dokładnie o co chodzi w tym problemie.

Q: Co dokładnie boli?
A: Chce zarządzać swoim budżetem domowym. Dokładnie chcę sobie prowadzić i zarządzać moje wydatki oraz moje przychody, więc chciałbym wiedzieć ile wydałem pieniędzy i na co w danym miesiącu oraz w jakiś sposób ustawiać sobie limit mojego budżetu miesięczny i w każdej chwili będę mógł sprawdzić ile mi tego limitu jeszcze zostało do końca danego miesiąca. Oraz zaplanować jakiś wydatek w przyszłości. Tak samo będę mógł sobie sprawdzić, ile wydałem pieniędzy na daną kategorię wydatków. Na przykład ile wydałem na paliwo danego miesiąca, ile wydałem na zakupy danego miesiąca. I też chciałbym sobie ustawić, móc ustawić moje koszty stałe, które wnoszę każdego miesiąca, żeby nie musieć każdego miesiąca dodawać ponownie. Ale będę mógł je oczywiście edytować, jeżeli ta wartość się zmienia, na przykład poziom czynszu czy rachunki za telefon itd.

Q: Dla kogo to rozwiązanie?
A: Dla mnie na użytek własny.

Q: Dlaczego CLI jest najlepsze?
A: Chcę, żeby to była aplikacja CLI, dlatego, żeby była dostępna w konsoli, ponieważ aktualnie uczę się pracy na modelach AI i chciałbym, aby agenci AI oraz modele miały dostęp do tej aplikacji w sposób bardzo łatwy i przejrzysty.

Q: Jakie są główne potrzeby?
A: Główną potrzebą jest możliwość dodawania wydatków oraz przychodów do budżetu domowego oraz bierzący monitoring tego ile się wydało pieniędzy i na co.

Q: Jakie są oczekiwania?
A: Swoje oczekiwania już podałem wyżej. Najważniejsze jest to, żeby była to bardzo prosta aplikacja CLI. Możemy ją napisać w Pythonie lub w JavaScriptie, ponieważ znam te języki i będzie dla mnie najlepiej, ale nie jest to konieczne, ale myślę, że to by było dla mnie preferowane. Ja korzystam na co dzień z Windowsa, więc fajnie by było, jakby ta aplikacja działała na Windowsie, ponieważ ta aplikacja jest tylko i wyłącznie na mój użytek. Nikt inny z tego nie będzie korzystał.

Q: Co może pójść nie tak?
A: Jedne co może pójśc nie tak na pierwszą myśl to błąd po mojej stronie, czyli wprowadzenie jakiejś błędnej komendy albo jakiejś niestandardowej struktury danych, które chcę wprowadzić do mojej bazy. I takie przypadki trzeba obsłużyć, żeby aplikacja nie wrzuciła jakichś głupot do mojej bazy danych.

Q: Co to jest budżet miesiączny?
A: Stała wartość ustawiona na stałe i zapamiętana, ale możliwa do edycji.

Q: Jaki interfejs CLI?
A: Interaktywne menu oraz jednolinijkowe komendy. Musi być opcja przełączenia, tak aby ja mógł sobie korzystać z interaktywnego menu, a tryb komend lepiej będzie pod agentów AI.

Q: Jaka baza danych?
A: Na początek wystarczy plik JSON, w późniejszej fazie pomyślimy o jakimś SQLite. Ważne aby przed każdym zapisem tworzony był plik .bak w razie w.

Q: Jakie kategorie wydatków ?
A: Zdefinijemy zestaw startowy, spośrod których będzie można wybierać, ale będzie też mozna dodać nowy typ kategorii.

To jest właśnie taki mój ogólny zarys aplikacji jaką bym widział. Teraz proszę Cię żebyś też to wszystko przeanalizował, te wszystkie moje tutaj wytyczne i może masz pomysł na jakieś niestandardowe przypadki które będzie trzeba obsłużyć albo na przykład jakieś uwagi masz do tego wszystkiego żeby jakoś pozbyć się błędów. No tak ogólnie, jeżeli coś widzisz, to o czym mogłaś zapomnieć, to tutaj przeanalizuj to i po prostu napisz mi, co jeszcze można tutaj zrobić.
