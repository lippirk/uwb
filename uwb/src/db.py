from pathlib import Path
from tinydb import TinyDB, Query
from typing import Dict
import threading
import string
import uwb.src.util as u

_tinydb = "/var/lib/unusual-word-bot/tinydb.json"


def _word_sanity_check(word: str) -> None:
    assert word.islower(), f"word='{word}' should be lowercase"
    assert not u.contains_whitespace(
        word), f"word='{word}' should not contain whitespace"


class Db:
    def __init__(self, path: Path = None):
        if not path:
            path = Path(_tinydb)

        path.parent.mkdir(exist_ok=True, parents=True)

        # only a single thread should ready or modify the database at any one time
        # so we will use this lock whenever we use self.tinydb
        self._lock = threading.Lock()
        self.tinydb = TinyDB(str(path))
        self.seen = self.tinydb.table("seen")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.tinydb.__exit__()

    def debug_eprint_all(self) -> None:
        t = self.seen
        with self._lock:
            all_ = t.all()
        u.eprint("====db.all")
        u.eprint_pprint(all_)
        u.eprint("db.all====")

    def _unique_words_seen_no_lock(self) -> int:
        return len(self.seen)

    def unique_words_seen(self) -> int:
        with self._lock:
            return self._unique_words_seen_no_lock()

    def add_word(self, word: str) -> Dict:
        '''
        Usage
        =====
        >>> is_unusual = add_word(t, 'augend')

        Returns
        =======

        True iff word has not been seen before
        '''
        _word_sanity_check(word)
        t = self.seen
        with self._lock:
            Q = Query()
            q = t.get(Q.word == word)
            if not q:
                n = self._unique_words_seen_no_lock()
                _doc_id = t.insert({'word': word, 'count': 1})
                return {"n": n + 1, "is-new": True}
            doc_id = q.doc_id
            count = t.get(doc_id=doc_id)['count'] + 1
            t.update({'count': count}, doc_ids=[doc_id])
            return {"is-new": False, 'count': count}

    def get_word_count(self, word: str) -> int:
        t = self.seen
        with self._lock:
            Q = Query()
            q = t.search(Q.word == word)
            lenq = len(q)
            if lenq == 0:
                return 0
            elif lenq == 1:
                return q[0]['count']
            else:
                u.eprint(
                    f"db.py: corrupt data! word '{word}' occured {lenq} times in db, expected 0 or 1")

    def total_words_seen(self) -> int:
        t = self.seen
        with self._lock:
            _all = t.all()
        total = 0
        for x in _all:
            total += x["count"]
        return total

    def words_with_count(self) -> Dict[str, int]:
        t = self.seen
        d = {}
        with self._lock:
            for x in t.all():
                d[x["word"]] = x["count"]
        return d
