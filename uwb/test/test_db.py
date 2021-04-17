import uwb.src.db as db
import uwb.src.util as u
import unittest
import tempfile
from pathlib import Path


def eprint(x: str) -> None:
    u.eprint(f"test_db.py: {x}")


class TestDb(unittest.TestCase):
    def setUp(self):
        _fd, tmp_path = tempfile.mkstemp()
        eprint(f"db temp path is {tmp_path}")

        self.db_path = Path(tmp_path)
        self.db = db.Db(path=self.db_path)

    def tearDown(self):
        eprint(f"removing {self.db_path}")
        self.db_path.unlink()
        self.db.__exit__()

    def test_add_word_sanity(self):
        d = self.db.add_word('dog')
        self.assertEqual(d, {'is-new': True, 'n': 1})
        self.assertEqual(self.db.get_word_count('dog'), 1)
        self.assertEqual(self.db.get_word_count('cat'), 0)
        self.assertEqual(self.db.total_words_seen(), 1)
        self.assertEqual(self.db.unique_words_seen(), 1)
        self.assertEqual(self.db.words_with_count(), {'dog': 1})

        d = self.db.add_word('cat')
        self.assertEqual(d, {'is-new': True, 'n': 2})
        self.assertEqual(self.db.get_word_count('cat'), 1)
        self.assertEqual(self.db.get_word_count('dog'), 1)
        self.assertEqual(self.db.total_words_seen(), 2)
        self.assertEqual(self.db.unique_words_seen(), 2)
        self.assertEqual(self.db.words_with_count(), {'dog': 1, 'cat': 1})

        dogs = [(self.db.add_word('dog'), {
                 'is-new': False, 'count': i + 2}) for i in range(100)]
        for (actual, expected) in dogs:
            self.assertEqual(actual, expected)
        self.assertEqual(self.db.get_word_count('dog'), 101)
        self.assertEqual(self.db.get_word_count('cat'), 1)
        self.assertEqual(self.db.total_words_seen(), 102)
        self.assertEqual(self.db.unique_words_seen(), 2)
        self.assertEqual(self.db.words_with_count(), {'dog': 101, 'cat': 1})

        cats = [(self.db.add_word('cat'), {
                 'is-new': False, 'count': i + 2}) for i in range(50)]
        for (actual, expected) in cats:
            self.assertEqual(actual, expected)
        self.assertEqual(self.db.get_word_count('dog'), 101)
        self.assertEqual(self.db.get_word_count('cat'), 51)
        self.assertEqual(self.db.total_words_seen(), 152)
        self.assertEqual(self.db.unique_words_seen(), 2)

        self.assertEqual(self.db.words_with_count(), {'dog': 101, 'cat': 51})


if __name__ == "__main__":
    unittest.main()
