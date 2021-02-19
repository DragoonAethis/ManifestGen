import pathlib, random, re, sys
from typing import Callable, Optional

from morfeusz2 import Morfeusz
from wordnet import query

morfeusz = Morfeusz(analyse=False)

DATASETS = ["new"]
DICT_LINES = {}
DICT_FUNCTIONS = {}

THESAURUS = {}

# Words from the thesaurus containing these tags will be ignored:
BLACKLISTED_TAGS = [
	"(bardzo potocznie)",
	"(potocznie)",
	"(częściej, ale wg niektórych niepoprawnie)",
	"(eufemistycznie)",  # :(
	#"(nieco potocznie)",  # Eh, it's fine
	"(obraźliwe)",
	"(obraźliwie)",
	#"(pieszczotliwie)",
	"(pogardliwie)",
	"(potoczne)",
	"(potocznie)",
	"(przestarzale)",
	"(ptoocznie)",
	"(regionalnie)",  # Contains some inappropriate words
	"(rzadko, wg niektórych niepoprawnie)",
	"(rzadziej, wg niektórych niepoprawnie)"
]


def setup_function(name: str, function: Callable):
	DICT_FUNCTIONS[name] = function
	print(f"Setup finished for {name}")


def generate_text(name="start", single_words_only=False):
	result = ""
	choices = DICT_LINES[name]
	if single_words_only:
		choices = list(filter(lambda w: " " not in w, choices))
	line = random.choice(choices)
	line_start = 0
	for tok_match in re.finditer(r"([!$?][^ !$?,.]+)", line):
		line_end, line_next = tok_match.span()
		result += line[line_start:line_end]

		tok = tok_match.group(1)
		if tok.startswith("$"):
			result += generate_text(tok[1:])
		elif tok.startswith("!"):
			func_args = tok[1:].split(":")
			result += DICT_FUNCTIONS[func_args[0]](*func_args[1:])
		elif tok.startswith("?"):
			result += random.choice([tok[1:], ""])

		line_start = line_next
	result += line[line_start:]
	if len(result) == 0:
		return line
	else:
		return re.sub(r' [ ]+', ' ', result).strip()


def compare_morfeusz(tag, targets):
	tag = [i.split(".") for i in tag.split(":")]
	for target in targets:
		target = [i.split(".") for i in target.split(":")]
		found = True
		for i in (0, 1, 2, 4):
			if len(target) > i and len(tag) > i:
				if not any(el in target[i] for el in tag[i]):
					found = False
					break
		if found:
			return True
	return False

def transform_morfeusz(new_word, word, word_target):
	if (" " in word) or (" " in new_word):
		return word_target
	if word != word_target:
		if word == new_word:
			return word_target
		# odmień new_word tak jak odmienione jest word -> word_target
		old_word_morf = morfeusz.generate(word)
		new_word_morf = morfeusz.generate(new_word)
		targets = list(map(lambda w: w[2], filter(lambda w: w[0] == word_target, old_word_morf)))
		if len(targets) <= 0:
			print(f"BŁĄD: Nie znaleziono mapowania dla {word} -> {word_target}", file=sys.stderr)
			return word_target
		elif len(targets) >= 2:
			targets_str = ", ".join(targets)
			print(f"UWAGA: Znaleziono więcej niż dwa mapowania dla {word} -> {word_target}: {targets_str}", file=sys.stderr)
		new_word_prop = list(set(map(lambda w: w[0], filter(lambda w: compare_morfeusz(w[2], targets) and (len(w[4]) <= 0), new_word_morf))))
		if len(new_word_prop) <= 0:
			print(f"BŁĄD: Nie znaleziono mapowania dla {new_word} -> ({word} -> {word_target})", file=sys.stderr)
			return word_target
		elif len(new_word_prop) >= 2:
			new_word_prop_str = ", ".join(new_word_prop)
			print(f"UWAGA: Znaleziono więcej niż dwa mapowania dla {new_word} -> ({word} -> {word_target}): {new_word_prop_str}", file=sys.stderr)
		return new_word_prop[0]
	else:
		return new_word


# $repeat:plik:min:max
def dict_repeat(source, occ_min, occ_max):
	occ_min = int(occ_min)
	occ_max = int(occ_max)
	occ_rnd = random.randint(occ_min, occ_max)
	s = [generate_text(source) for _ in range(0, occ_rnd)]
	return " ".join(s)


# $transform:plik:word:word_target
def dict_transform(source, word, word_target):
	return transform_morfeusz(generate_text(source, single_words_only=True), word, word_target)


def clean_word(word: str) -> Optional[str]:
	while '(' in word and ')' in word:
		for tag in BLACKLISTED_TAGS:
			if word.find(tag) != -1:
				return None

		word = re.sub("\(.*\)", "", word)

	if '(' in word or ')' in word or '*' in word:
		return None  # Broken entry

	word = word.strip()
	if len(word) < 1 or word.find(' ') != -1:
		return None

	return word


# $th:word:word_target?
def setup_thesaurus(filename, dictionary):
	with open(filename) as f:
		lines = f.readlines()

	for line in lines:
		line = line.strip()
		if line.startswith("#"):
			continue

		words = [clean_word(w) for w in line.split(";")]
		words = list(filter(lambda w: w is not None, words))

		if len(words) >= 2:
			key = words[0]
			if key not in dictionary:
				dictionary[key] = []

			dictionary[key].extend(words[1:])

	# Remove duplicates:
	#for key in dictionary:
	#	dictionary[key] = list(set(key))

def dict_thesaurus(word, word_target=None):
	if word_target is None:
		word_target = word
	word_lower = word.lower()
	if word_lower in THESAURUS:
		new_word = transform_morfeusz(random.choice(THESAURUS[word_lower] + [word]), word, word_target)
		# TODO: to mogloby byc madrzejsze
		if word_lower != word:
			return new_word[0:1].upper() + new_word[1:]
		else:
			return new_word
	else:
		return word_target

# $sym:word:word_target?
def dict_symset(word, word_target=None):
	if word_target is None:
		word_target = word
	word_lower = word.lower()
	syms = query(word_lower)
	if syms is not None:
		new_word = transform_morfeusz(random.choice(syms.words), word, word_target)
		# TODO: to mogloby byc madrzejsze
		if word_lower != word:
			return new_word[0:1].upper() + new_word[1:]
		else:
			return new_word
	else:
		return word_target


def setup_datasets():
	for dataset in DATASETS:
		for file in pathlib.Path(f"./datasets/{dataset}/").glob("*.txt"):
			with open(file) as f:
				lines = [line.strip() for line in f.readlines()]

			DICT_LINES[file.stem] = list(filter(lambda x: not x.startswith("#"), lines))


setup_thesaurus("./datasets/thesaurus.txt", THESAURUS)
setup_function("th", dict_thesaurus)
setup_function("sym", dict_symset)

setup_function("repeat", dict_repeat)
setup_function("transform", dict_transform)

setup_datasets()
