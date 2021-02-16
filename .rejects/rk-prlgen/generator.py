import random
from dictionary import DICTS, DICT_BLOCKS

PUNCTUATION = ['.', '!', '?', '-']


def generate_block(body_gen=None):
    block_texts = []
    for block in DICT_BLOCKS:
        generate_times = block.gen_times
        if block.name == "body" and body_gen is not None:
            generate_times = body_gen

        for i in range(block.gen_times):
            block_picks = []
            source_block = random.choice(DICTS[block.name])
            for part_list in source_block:
                block_picks.append(random.choice(part_list).strip())

            gen_block = " ".join(block_picks)
            if not any([gen_block.endswith(x) for x in PUNCTUATION]):
                gen_block += "."

            block_texts.append(gen_block.strip())

    return " ".join(block_texts)


if __name__ == "__main__":
    print(generate_block())
