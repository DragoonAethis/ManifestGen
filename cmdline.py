# Czy wiesz, że?: Jeśli wykonasz s/I/O/g na IWI, dostaniesz OWO?
import sys
from generator import generate_text

# ./cmdline.py <N> <STARTER>
# Opcjonalne parametry:
# - N: Ilość zdań do wygenerowania (domyślnie 1)
# - STARTER: Token od którego zacząć generowanie (domyślnie "start")

if __name__ == "__main__":
    iter_count = 1
    starter = "start"

    if len(sys.argv) > 1:
        iter_count = int(sys.argv[1])

    if len(sys.argv) > 2:
        starter = sys.argv[2]

    for i in range(iter_count):
        print(generate_text(starter))
