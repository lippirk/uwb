from typing import Iterator

import uwb.src.reddit as reddit
import uwb.src.dictionary as dictionary
from uwb.src.db import Db
import uwb.src.clean as clean
import uwb.src.util as u
import atexit

POST = True


def eprint(x: str) -> None:
    u.eprint(f"app.py: {x}")


def _words_for_db(t_dict: dictionary.T, post: reddit.Post) -> Iterator[str]:
    raw_text = f"{post.title}\n{post.content}"
    text = clean.unrawify(raw_text)
    words = clean.extract_words(text)
    if words is None:
        eprint(f"post[{post._id}] extract_words failed")
        return []
    for w in words:
        if dictionary.is_valid_word(t_dict, w):
            yield w


def _on_new_post(db: Db,
                 r: reddit.PrawClient,
                 t_dict: dictionary.T,
                 post: reddit.Post) -> None:
    submission = post._id
    i = 0
    new_word_ds = []
    for w in _words_for_db(t_dict, post):
        d = db.add_word(w)
        if d['is-new']:
            d['word'] = w
            new_word_ds.append(d)
        i += 1
    eprint(f"added {i} words to db from post[{submission}]")

    if new_word_ds:
        total_words_seen = db.total_words_seen()
        out_of = dictionary.size(t_dict)
        new_words = [d['word'] for d in new_word_ds]
        n = max(d['n'] for d in new_word_ds)
        assert n >= 1
        assert len(new_words) >= 1
        if POST:
            if len(new_words) == 1:
                params = dict(submission_id=submission,
                              word=new_words[0],
                              n=n,
                              _out_of=out_of,
                              total_words_seen=total_words_seen)
                eprint(f"new_word_comment: params={params}")
                r.new_word_comment(**params)
            else:
                params = dict(submission_id=submission,
                              words=new_words,
                              n=n,
                              _out_of=out_of,
                              total_words_seen=total_words_seen)
                eprint(f"new_words_comment: params={params}")
                r.new_words_comment(**params)
        else:
            eprint(f"POST=False, but would have posted about {new_words}")


def pp_db() -> None:
    with Db() as db:
        u.eprint_pprint(db.words_with_count())
        u.eprint(f"total words seen = {db.total_words_seen()}")
        u.eprint(f"unique words seen = {db.unique_words_seen()}")


def test_comment() -> None:
    with reddit.PrawClient() as pc:
        pc._test_comment()


def collect_words_forever_loop(db: Db, t_dict: dictionary.T, t_reddit: reddit.T, r: reddit.PrawClient) -> None:
    i = 1
    for p in reddit.new_posts(t_reddit):
        eprint(f"processing post#{i} id={p._id}")
        _on_new_post(db, r, t_dict, p)
        i += 1


def collect_words_forever():
    with Db() as db:
        with reddit.PrawClient() as r:
            t_dict = dictionary.init()
            t_reddit = reddit.init()
            while True:
                try:
                    collect_words_forever_loop(db, t_dict, t_reddit, r)
                except Exception as e:
                    eprint(f"encountered error: {str(e)}")
                    eprint(f"trying again...")


def run():
    atexit.register(lambda: u.eprint("====UWB EXITING====="))
    u.eprint(f"====UWB STARTING [time={u.now_str()}]====")
    #  pp_db()
    collect_words_forever()
    #  test_comment()
