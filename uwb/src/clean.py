from typing import Optional, List, Iterator, Tuple
import nltk
import string
import uwb.src.util as u
import re

Word = str

_corpus_words = set(nltk.corpus.words.words())


def eprint(x: str) -> None:
    u.eprint(f"clean.py: {x}")


def words_not_in_corpus(words: List[str]) -> Iterator[str]:
    i = 0
    for w in words:
        if i > 10:
            break
        if w not in _corpus_words:
            i += 1
            yield w


def _remove_links(content: str) -> str:
    '''
    1. remove reference style links
    2. remove other urls
    '''
    content = re.sub(r"\[([^\n]+)\]\(.+\)", r"\1", content)
    content = re.sub(r"http[s]?:\/\/\S+", "", content)
    return content


def _remove_symbol_entities(content: str) -> str:
    '''
    >>> _remove_symbol_entities("&nbsp; blah")
    " blah"
    '''
    return re.sub(r"&\S*;", "", content)


def _remove_unicode(content: str) -> str:
    return content.encode("ascii", "ignore").decode('utf8')


def unrawify(content: str) -> str:
    content = _remove_links(content)
    content = _remove_symbol_entities(content)
    content = _remove_unicode(content)
    content = content.lower()
    return content


_fluff_tokens = ["n't", "'s", "'re"]  # english language specific


def _is_fluff(x: str) -> bool:
    if re.search(r"[^A-Za-z]*", x):
        # no alphabet chars
        return True
    if x in _fluff_tokens:
        # chars like ",', ... etc.
        return True
    return False


def _classify_word(x: str) -> str:
    if not re.search(r"^[A-Za-z]+$", x):
        # not a word
        return "none"
    if x in _corpus_words:
        return "corpus"
    return "non-corpus"


def extract_words(content: str) -> Optional[List[str]]:
    '''
    content should already have been cleaned to some extent.
    '''

    # ctrs
    junk = 0
    fluff = 0
    corpus_word = 0
    non_corpus_word = 0
    total = 0

    words = []
    tokens = nltk.word_tokenize(content)
    if not tokens:
        eprint("empty content")
        return None

    for w in tokens:
        total += 1
        w = re.sub(r"^[\\\-]+([A-Za-z]+)$", r"\1", w)
        w_class = _classify_word(w)
        if w_class == "corpus":
            corpus_word += 1
            words.append(w)
        elif w_class == "non-corpus":
            non_corpus_word += 1
        else:
            assert w_class == "none"
            if _is_fluff(w):
                fluff += 1
            else:
                eprint(f"junk word '{w}'")
                junk += 1

    assert len(words) == corpus_word
    assert total == corpus_word + fluff + junk + non_corpus_word

    # almost like "TP rate"
    # we require that most words are english
    if junk / total > 0.3:
        eprint("refusing to extract words from content - too much junk")
        return None
    if corpus_word < 5:
        eprint("refusing to extract words from content - too short")
        return None
    if (prop := corpus_word / (corpus_word + non_corpus_word)) < 0.50:
        eprint(
            f"refusing to extract words from content - too many words not from the corpus (prop = {prop})")
        return None
    return words
