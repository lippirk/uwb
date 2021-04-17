from psaw import PushshiftAPI
from typing import Iterator, List
from pathlib import Path
import importlib_resources
import re
import praw

import uwb.src.util as u

T = PushshiftAPI
_test_posts_folder = (importlib_resources.files(
    'uwb') / "resources" / "test_posts")


def eprint(x: str) -> None:
    u.eprint(f"reddit.py: {x}")


class Post:
    def __init__(self, *, _id: str, subreddit: str, title: str, content: str):
        self._id = _id
        self.subreddit = subreddit
        self.title = title
        self.content = content


def init(test=False) -> T:
    if test:
        return None
    return PushshiftAPI()


def new_posts(t: T) -> Iterator[Post]:
    for x in t.search_submissions():
        try:
            content = x.selftext.strip()
            if content == "" or content == "[removed]":
                continue
            else:
                yield Post(_id=x.id,
                           subreddit=x.subreddit,
                           title=x.title,
                           content=content)
        except:
            id_ = None
            try:
                id_ = x.id
            except:
                pass
            eprint(f"bad submission object id_={id_}")
            continue


def get_test_posts(t: T, fetch_more=False) -> Iterator[Post]:
    for p in Path(_test_posts_folder).glob("*.pickle"):
        yield u.load_pickle(p)

    if fetch_more:
        for p in new_posts(t):
            fname = (Path(_test_posts_folder) / f"{p._id}.pickle")
            u.dump_pickle(p, fname=fname)
            yield p


class PrawClient:
    def __init__(self):
        self.secrets = u.load_json("./secrets.json")

    def __enter__(self):
        s = self.secrets["unusual-word-bot"]
        self.r = praw.Reddit(
            client_id=s["id"],
            client_secret=s["secret"],
            user_agent="uwb",
            username="unusual-word-bot",
            password=s["password"]
        )
        _ = self.r.__enter__()
        eprint("initialized praw!")
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.r.__exit__(exception_type, exception_value, traceback)

    def _post_comment(self, submission_id: str, comment: str) -> None:
        eprint(f"attempting to comment on submission={submission_id}")
        submission = self.r.submission(id=submission_id)
        try:
            submission.reply(comment)
            eprint(f"successfully commented on submission={submission_id}")
        except Exception as e:
            eprint(f"failed to comment on submission={submission_id}")

    def _test_comment(self) -> None:
        for s in self.r.subreddit("testingground4bots").hot(limit=1):
            params = dict(submission_id=s, word="solisequious",
                          n=1, _out_of=3, total_words_seen=5)
            self.new_word_comment(**params)

    def _get_test_submission_id(self) -> str:
        for s in self.r.subreddit("testingground4bots").hot(limit=1):
            return s.id

    def new_word_comment(self,
                         submission_id: str,
                         word: str,
                         n: int,
                         _out_of: int,
                         total_words_seen: int) -> None:
        comment = f"""Beeby Boopy

I'm searching reddit for words, and you mentioned '{word}' - I haven't seen that one before!

I have seen {total_words_seen} words in total, and {n} _unique_ words. You can see my code [here](https://github.com/lippirk/uwb)."""

        self._post_comment(submission_id, comment)

    def new_words_comment(self,
                          submission_id: str,
                          words: List[str],
                          n: int,
                          _out_of: int,
                          total_words_seen) -> None:
        num_of_new_words = len(words)
        words = [f"'{w}'" for w in words]
        words_str = ", ".join(words[:-1]) + f" and {words[-1]}"
        comment = f"""Beeby Boopy

I'm reddit for words, and you mentioned {num_of_new_words} words I haven't seen before: {words_str}!

I have seen {total_words_seen} words in total, and {n} _unique_ words. You can see my code [here](https://github.com/lippirk/uwb)."""

        self._post_comment(submission_id, comment)
