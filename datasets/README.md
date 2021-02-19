# Format szablonów

## Ogólna zasada działania

Pliki tekstowe (.txt) wchodzące w skład szablonu stanowią zbiory linii, z
których za każdym razem wybierana jest losowo jedna z nich. Pozwala to na
tworzenie losowych zdań.

Przetwarzanie zawsze zaczyna się od pliku "start.txt". Dany plik może dodawać
fragmenty zdań na podstawie losowej linii innych plików przy użyciu stworzonych
w tym celu komend.

## Komendy

* `$[nazwa pliku]` - w to miejsce wstaw tekst z losową linii z [nazwa pliku].txt.
  Za każdym razem może zostać wylosowana inna linia z pliku.
* `!th:słowo:odmiana` - w to miejsce wstaw synonim słowa "słowo" pochodzący z
  tezaurusa. Opcjonalny parametr "odmiana" tworzy razem ze "słowo" parę; np.
  `!th:dobry:dobra` wstawi synonim słowa "dobry" (lub samo słowo "dobry"), który
  odmienia się tak, jak słowo "dobry" do wyrazu "dobra".
* `!syn:słowo:odmiana` - analogicznie jak wyżej, lecz ze zbioru synsetów bazy danych
  WordNet (zawiera ona mniej, ale bardziej dokładnych znaczeniowo synonimów).
* `!repeat:plik:min:max` - wygeneruj tekst z pliku "plik.txt" od "min" do "max" razy,
  i wstaw go w miejsce komendy.
* `!transform:plik:b:c` - przekształć losowe pojedyncze słowo z pliku "plik.txt" tak, jak
  słowo "b" odmienia się do "c".
* `?słowo` - losowo pozostaw lub usuń "słowo".

## Przykładowe zbiory danych

* `socialism` - implementacja tzw. "generatora przemówień PRL" w wyzej opisanym systemie.
* `new` - stworzony przez nas generator zdań obrazujących manifesty, protesty, itd.
