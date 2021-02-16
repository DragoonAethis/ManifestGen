#!/usr/bin/env python3
import re
import sys
import string

from bs4 import BeautifulSoup
from markdown import markdown
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# Configure the cleaner here:

# Minimum stripped line length for inclusion in the cleaned dataset:
MIN_LINE_LENGTH = 8

# All known punctuation and language-specific characters:
PUNCTUATION = '.?! '
NON_ASCII_CHARS = 'ŻÓŁĆĘŚĄŹŃ'

# Needed for whitelist/punctuation-only filters below:
PUNCTUATION_ESCAPES = ''.join(["\\" + x for x in PUNCTUATION])

# Remove any non-whitelisted characters from the dataset.
# True for all datasets.
CLEAN_WHITELIST = False
WHITELIST_REGEX = re.compile(f"[^A-Z{NON_ASCII_CHARS}0-9{PUNCTUATION_ESCAPES}\\n]", flags=re.IGNORECASE)

# Remove lines with punctuation only.
# True for all datasets.
CLEAN_PUNCTUATION_ONLY_LINES = False
PUNCTUATION_ONLY_REGEX = re.compile(f'^[{PUNCTUATION_ESCAPES}]+$', re.MULTILINE)

# Parse Markdown into HTML and extract text from HTML
# Gutenberg: False, Wikipedia: False, Reddit: True
CLEAN_MARKDOWN = False

# Remove all URLs (both clickable and Markdown-based)
# Gutenberg: False, Wikipedia: True, Reddit: True
# https://gist.github.com/gruber/8891611
CLEAN_URLS = False
URL_REGEX = re.compile(r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))")

# Try to detect the language of each line and remove
# any lines matching the specified language. (None to
# disable, unmatched lines will be removed.)
# Gutenberg: None, Wikipedia: None, Reddit: 'en'
REMOVE_DETECTED_LANG = 'en'

# Compress multiple punctuation instances with a single
# instance (eg "test..." -> "test.")
# True for all datasets.
COMPRESS_PUNCTUATION = False
COMPRESS_REGEXES = [(re.compile(f"\\{x}+"), x) for x in PUNCTUATION + '\n']

# Remove swears from black.list.
# Gutenberg: False, Wikipedia: False, Reddit: True
CLEAN_SWEARS = False

def build_blacklist_regex(blacklist="black.list"):
    with open(blacklist) as f:
        data = f.readlines()

    word_list = []
    for line in data:
        line = line.strip().upper()
        if len(line) < 1:
            continue

        word_list.append(line)

    return re.compile('(' + '|'.join(word_list) + ')', flags=re.IGNORECASE)

SWEAREGEX = build_blacklist_regex()

# ---

def clean_line(line):
    # Remove unnecessary whitespace
    line = line.strip()
    if len(line) < MIN_LINE_LENGTH:
        return None

    if REMOVE_DETECTED_LANG:
        try:
            # Perf: This is brutally slow...
            if detect(line) == REMOVE_DETECTED_LANG:
                return None
        except LangDetectException:
            # Manual inspection revealed this to be mostly URLs and
            # useless data - skip these lines.
            return None

    # Perf: Avoid two concats here!
    if line[-1] not in PUNCTUATION:
        return line + '.\n'
    else:
        return line + '\n'


def stop_early(dataset, save_as):
    with open(save_as, 'w') as f:
        print("Partially done, saving and quitting now!")
        f.write(dataset)
        quit()


def clean_dataset(filename, save_as, report_progress=True):
    cleaned = 0
    removed = 0

    try:
        print(f"Loading dataset from {filename}...")
        with open(filename) as f:
            dataset = f.read()
    except FileNotFoundError:
        print(f"Input dataset file {filename} does not exist.")

    print("Running dataset-wide cleaning steps...")

    if CLEAN_MARKDOWN:
        print("Parsing Markdown to HTML...")
        html = markdown(dataset)

        print("Removing code snippets...")
        html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
        html = re.sub(r'<code>(.*?)</code>', ' ', html)

        print("Extracting text from HTML...")
        soup = BeautifulSoup(html, "lxml")
        dataset = ''.join(soup.findAll(text=True))

    if CLEAN_SWEARS:
        print("Removing swears...")
        dataset = SWEAREGEX.sub('', dataset)

    if CLEAN_URLS:
        print("Removing URLs...")
        dataset = URL_REGEX.sub('', dataset)

    if CLEAN_WHITELIST:
        print("Removing non-whitelisted characters...")
        dataset = WHITELIST_REGEX.sub(' ', dataset)

    if CLEAN_PUNCTUATION_ONLY_LINES:
        print("Removing punctuation-only lines...")
        dataset = PUNCTUATION_ONLY_REGEX.sub('', dataset)

    if COMPRESS_PUNCTUATION:
        print("Compressing punctuation...")
        for i in range(len(COMPRESS_REGEXES)):
            regex, char = COMPRESS_REGEXES[i]
            print(f"[{i+1}/{len(COMPRESS_REGEXES)}] Compressing: {char}")
            dataset = regex.sub(char, dataset)

    print("Running per-line cleaning steps...")
    lines = dataset.splitlines()
    total = len(lines)

    with open(save_as, 'w') as f:
        for line in lines:
            cleaned_line = clean_line(line)
            report_status = False

            if cleaned_line is not None:
                f.write(cleaned_line)
                cleaned += 1
            else:
                removed += 1

            processed = cleaned + removed
            progress = ((cleaned + removed) / total) * 100

            if report_progress and processed % 1000 == 0:
                print(f"{progress:.01f}% [{total} lines/{cleaned} cleaned/{removed} removed/{processed} done]")

    print(f"Done, {total} processed, {cleaned} cleaned, {removed} removed")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("./clean.py INPUT OUTPUT [--no-progress]")
        print("--no-progress disables all progress reporting.")
        print("OUTPUT will be overwritten.")
        exit()

    no_progress = not (len(sys.argv) >= 4 and sys.argv[3].lower().strip() == "--no-progress")
    clean_dataset(sys.argv[1], sys.argv[2], report_progress=no_progress)
