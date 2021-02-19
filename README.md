# Generator Manifestów

Prosty generator tekstu umożliwiający szablonowe tworzenie bloków tekstu w stylu generatora
[przemówień PRL](https://www.eurostudent.pl/generator-przemowienia/), z dodatkami:

- Szablony są plikami tekstowymi z których losowo wybierane są linie.
- Poszczególne słowa w szablonie mogą zostać zamieniane na ich synonimy z tezaurusa lub Słowosieci.

Projekt ten korzysta z:

- [Biblioteki Morfeusz 2](http://morfeusz.sgjp.pl) Instytutu Podstaw Informatyki PAN,
- [Słowosieci](http://plwordnet.pwr.wroc.pl) Politechniki Wrocławskiej,
- [Biblioteki Flask](https://flask.palletsprojects.com) projektu Pallets.


## Jak włożyć tu własne templatki?

W folderze `datasets` przeczytaj plik [README](datasets/README.md) i zmodyfikuj znajdujące się tam
pliki tekstowe.


## Co gdzie się znajduje w projekcie?

- Aplikacja webowa jest w `app.py` - w zasadzie hostuje tylko 2 endpointy z templatkami.
- Generowanie zdań z konsoli jest w `cmdline.py`, przydatne do szybkiego rozwoju generatora.
- Sam generator znajduje się w `generator.py`, gdzie najbardziej interesuje nas `generate_text`
  i funkcje konfigurujące generator w zależności od templatki.
- Do wyciągania synonimów używamy okrojonej wersji Słowosieci Politechniki Wrocławskiej - podzbiór
  danych który używamy jest w bazie SQLite w `wordnet/plwordnet.sqlite`, a interfejs do niej mamy
  obok w `wordnet/synsets.py`. (Bazę możesz ściągnąć z release'ów na GitHubie.)


## Jak to postawić?

- Zainstaluj w systemie paczkę Flask (Jeśli korzystasz z Virtualenva, umożliw z niego dostęp do
  paczek systemowych - będzie to potrzebne w następnym kroku).
- Zainstaluj w systemie Morfeusza 2 zgodnie z instrukcjami ze strony biblioteki, lub skorzystaj z
  PKGBUILDów w `.packaging` jeśli korzystasz z systemu korzystającego z pacmana/makepkg. (Jest to
  biblioteka natywna z generowanymi bindingami do Pythona, więc instalacja w Virtualenvie odpada.)
- Pobierz i rozpakuj [kod programu](https://github.com/DragoonAethis/ManifestGen/releases).
- Pobierz zmodyfikowaną Słowosieć z ostatniego wydania i umieść plik `plwordnet.sqlite` w folderze
  `wordnet` tego projektu.
- Uruchom w folderze projektu `flask run` i otwórz wypisany adres, albo odpal `cmdline.py`.

"Produkcyjna" wersja powinna korzystać z serwera WSGI i Apache'a/Nginxa zamiast wystawiać serwer
Flaska, ale zostawiamy to jako zadanie domowe dla chętnych. Przykładowa instalacja z Gunicornem
opisana jest w Dockerfile'u w repozytorium, na samym dole.
