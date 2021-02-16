import re
import os.path
import sqlite3
from typing import Optional

__all__ = [
    'query',  # Returns a ParsedSynset for a given word, or None
    'Synset',  # Class representing a parsed synset and its related words
    'RELATION_TYPES',  # Dict of all relation type IDs to their names
    'FALLBACK_RELATION',  # Default relation name (if not found in database)
]

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "plwordnet.sqlite")

RELATION_TYPES = {}
FALLBACK_RELATION = "relacja"

with sqlite3.connect(DATABASE_PATH) as rel_db:
    for rel_type in rel_db.execute("SELECT id, name FROM relation_types"):
        RELATION_TYPES[rel_type[0]] = rel_type[1]


class Synset:
    def __init__(self, pk: int, words: list[str]):
        self.id = pk
        self.words = words
        self.outgoing = []
        self.incoming = []

    def __str__(self):
        return f"{self.words} (Out: {self.outgoing} - In: {self.incoming})"

    def __repr__(self):
        return f"<Synset at {hex(id(self))}: {str(self.words)}>"


def get_synset(db: sqlite3.Connection, word: str) -> Optional[Synset]:
    """Given a word, find its Synset (or None if not found)."""

    matching_synset = None
    upper_word = word.upper()

    # Get all likely synsets with case-insensitive LIKE first.
    # From those results, pick the most appropriate one.
    for row in db.execute("SELECT id, synset FROM synsets WHERE synset LIKE ?", (f"%{word}%",)):
        words = parse_synset_units(row[1])
        if word in words:
            matching_synset = Synset(row[0], words)
            break  # It doesn't get any better, so...
        elif any([x.upper() == upper_word for x in words]):
            matching_synset = Synset(row[0], words)
            # Don't break yet, see if we can get a case match.

    # If we didn't find anything, we'll return None here.
    return matching_synset


def parse_synset_units(units: str) -> list[str]:
    """Parse the synset string into a list of words."""
    units = units.strip()
    if units[0] == '(' and units[-1] == ')':
        units = units[1:-1]

    splits = []
    for main_split in units.split('|'):
        for part in main_split.split(','):
            splits.append(part.strip())

    words = []
    for split in splits:
        match = re.match("^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ ]+", split)
        if match is None:
            continue

        words.append(match[0].strip())

    return words


def get_related_words(db: sqlite3.Connection, pk: int) ->\
        tuple[list[tuple[str, list[str]]], list[tuple[str, list[str]]]]:
    """Given a synset ID, get all incoming/outgoing relations and
    parse their related words, returning two from/to result lists."""
    cursor = db.execute("SELECT rel.type_id, s1.id, s1.synset, s2.id, s2.synset"
                        "  FROM synset_relations rel"
                        "  JOIN synsets s1 ON rel.parent_id = s1.id"
                        "  JOIN synsets s2 ON rel.child_id = s2.id"
                        " WHERE rel.parent_id = ? OR rel.child_id = ?",
                        (pk, pk))

    synsets_from, synsets_to = [], []
    for row in cursor:
        # rel_id, parent_id, parent, child_id, child
        relation = RELATION_TYPES.get(row[0]) or FALLBACK_RELATION

        if row[1] == pk:  # Synset is the parent, get child words:
            words = parse_synset_units(row[4])
            synsets_from.append((relation, words))
        else:  # Synset is the child, get parent words:
            words = parse_synset_units(row[2])
            synsets_to.append((relation, words))

    return synsets_from, synsets_to


def query(word: str) -> Optional[Synset]:
    """Returns a matching, parsed synonym set with its associated
    relations, if found. Returns None otherwise."""
    db = sqlite3.connect(DATABASE_PATH)

    synset = get_synset(db, word)
    if synset is None:
        return None

    synset.outgoing, synset.incoming = get_related_words(db, synset.id)
    return synset
