from collections import namedtuple

DictBlock = namedtuple('DictBlock', ['name', 'gen_times'])
DICTS = {}

# Dict key, generate N times from block
DICT_BLOCKS = [
    DictBlock('intro', 1),
    DictBlock('body', 5),
    #DictBlock('end', 1)
]

DICTS['intro'] = [
    (["Koleżanki i koledzy!",
      "Towarzysze!"],
     ["Stoimy na skraju biedy i spierdolenia",
      "Mamy problem"]),
    (["Wyśmienici towarzysze -",
      "Zacni współtowarzysze niewoli -"],
     ["wszystko jeszcze będzie dobrze!",
      "co nas nie zabije, to nas wzmocni!",
      "mamy jeszcze szansę uwolnić się od szwabskiego kapitału!",]),
]

DICTS['body'] = [
    (
        [
            "Z drugiej strony",
            "Podobnie",
            "Nie zapominajmy jednak, że",
            "W ten sposób",
            "Praktyka dnia codziennego dowodzi, że",
            "Wagi i znaczenia tych problemów nie trzeba szerzej udowadniać, ponieważ",
            "Różnorakie i bogate doświadczenia",
            "Troska organizacji a szczególnie",
            "Wyższe założenia ideowe, a szczególnie"
        ],
        [
            "realizacja nakreślonych zadań programowych",
            "zakres i miejsce szkolenia kadr",
            "stały wzrost ilości i zakres naszej aktywności",
            "aktualna struktura organizacji",
            "nowy model działalności organizacyjnej",
            "dalszy rozwój różnych form działalności",
            "stałe zabezpieczanie informacyjno-propagandowe naszej działalności",
            "wzmocnienie i rozwijanie struktur",
            "konsultacja z szerokim aktywem",
            "rozpoczęcie powszechnej akcji kształtowania postaw"
        ],
        [
            "zmusza nas do przeanalizowania",
            "spełnia istotną rolę w kształtowaniu",
            "wymaga sprecyzowania i określenia",
            "pomaga w przygotowaniu i realizacji",
            "zabezpiecza udział szerokiej grupie w kształtowaniu",
            "spełnia ważne zadania w wprowadzaniu",
            "umożliwia w większym stopniu tworzenie",
            "powoduje docenienie wagi",
            "przedstawia interesująca próbę sprawdzenia",
            "pociąga za sobą proces wdrażania i unowocześniania"
        ],
        [
            "istniejących warunków administracyjno-finansowych",
            "dalszych kierunków rozwoju",
            "systemu powszechnego uczestnictwa",
            "postaw uczestników wobec zadań stawianych przez organizację",
            "nowych propozycji",
            "kierunków postępowego wychowania",
            "systemu szkolenia kadry odpowiadającemu potrzebom",
            "odpowiednich warunków aktywizacji",
            "modelu rozwoju",
            "form oddziaływania"
        ],
    )
]
