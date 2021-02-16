# Czy wiesz, że?: Jeśli wykonasz s/I/O/g na IWI, dostaniesz OWO?
import sys
from generator import generate_text

if __name__ == "__main__":
    iter_count = 1
    if len(sys.argv) > 1:
        iter_count = int(sys.argv[1])

    for i in range(iter_count):
        print(generate_text("start"))
