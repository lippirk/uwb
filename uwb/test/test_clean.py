from pathlib import Path
from typing import Iterator, Tuple
import uwb.src.clean as c
import importlib_resources
import unittest
import os

Input = str
Expected = str


def input_expecteds(test_cases_path: Path) -> Iterator[Tuple[Input, Expected]]:
    dirs = [x for x in test_cases_path.glob('*') if x.is_dir()]
    for d in dirs:
        if (bi := d / 'bad_input').exists():
            input_ = bi.read_text().strip()
            expected = None
        else:
            input_ = (d / 'input').read_text().strip()
            expected = (d / 'expected').read_text().strip()
        yield (input_, expected)


class TestClean(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_extract_words(self):
        test_cases = (importlib_resources.files(
            'uwb') / "test" / "test_cases" / "extract_words")
        for (input_, expected) in input_expecteds(test_cases):
            input_ = c.unrawify(input_)
            actual = c.extract_words(input_)
            if actual:
                actual = ' '.join(actual)
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
