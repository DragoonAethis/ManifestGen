import sys
import json

from client import reddit

MIN_SCORE = 3
MIN_BODY_LENGTH = 32
SUBREDDIT = "polska"
CORPUS_NAME = f"score{MIN_SCORE}-length{MIN_BODY_LENGTH}"


def load_state(identifier, corpus):
    state = {}
    try:
        with open(f"{corpus}.{identifier}.json") as f:
            state = json.load(f)
    except FileNotFoundError:
        pass
    except json.decoder.JSONDecodeError:
        pass

    return state


def save_state(identifier, corpus, state):
    with open(f"{corpus}.{identifier}.json", 'w') as f:
        json.dump(state, f)


def scrape(subreddit, corpus):
    print(f"Scraping {subreddit} to {corpus}.txt...")
    output = open(f"{corpus}.txt", mode='a', encoding='utf-8')
    subreddit = reddit.subreddit(SUBREDDIT)
    state = load_state('submission', corpus)
    scraped = 0

    while True:
        print(f"[{scraped}] Scraping 100 submissions with params {state}")

        submissions = subreddit.top(params=state)
        for submission in submissions:
            print(f"[{scraped}] Scraping {submission.name}")
            state['after'] = submission.name
            save_state('submission', corpus, state)

            submission.comments.replace_more(limit=0)
            comments = submission.comments.list()

            for comment in comments:
                if comment.score < MIN_SCORE:
                    continue

                if len(comment.body) < MIN_BODY_LENGTH:
                    continue

                print(f"Appending {comment.name} ({len(comment.body)} chars)")
                output.write(f"{comment.body}\n")
                scraped += 1


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        subreddit = sys.argv[1]
    else:
        subreddit = SUBREDDIT

    scrape(subreddit, f"reddit-{subreddit}-{CORPUS_NAME}")
