import os
import sys

import markovify


def try_model(corpus, sentences, ngrams):
    with open(file) as f:
        model = markovify.Text(f, state_size=ngrams, retain_original=False)

    for i in range(sentences):
        print(model.make_short_sentence(280))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("./markov.py CORPUS [SENTENCES=50] [NGRAMS=2]")
        exit()

    # Defaults:
    file = sys.argv[1]
    sentences = 50
    ngrams = 2

    if len(sys.argv) >= 3:
        sentences = int(sys.argv[2])

    if len(sys.argv) >= 4:
        ngrams = int(sys.argv[3])

    try_model(file, sentences, ngrams)
