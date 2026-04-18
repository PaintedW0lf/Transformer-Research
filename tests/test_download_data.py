from __future__ import annotations

from pathlib import Path

import pytest

from download_pretraining_data import (
    _english_stats,
    _is_probably_english,
    _parse_entry,
    clean_whitespace,
    fetch_unavailable,
    get_folder_path,
    get_time_folder,
    html_to_text,
    strip_gutenberg_boilerplate,
)


# ---------------------------------------------------------------------------
# get_time_folder
# ---------------------------------------------------------------------------

def test_get_time_folder_bce_returns_older() -> None:
    assert get_time_folder(-500) == "older (BC)"
    assert get_time_folder(-1) == "older (BC)"


def test_get_time_folder_ce_returns_century_upper_bound() -> None:
    assert get_time_folder(0) == "100"
    assert get_time_folder(99) == "100"
    assert get_time_folder(100) == "200"
    assert get_time_folder(1999) == "2000"


# ---------------------------------------------------------------------------
# get_folder_path
# ---------------------------------------------------------------------------

def test_get_folder_path_east_bce() -> None:
    path = get_folder_path("some_text", "east", -300)
    assert "east" in str(path)
    assert "older (BC)" in str(path)


def test_get_folder_path_west_ce() -> None:
    path = get_folder_path("some_text", "west", 500)
    assert "west" in str(path)
    assert "600" in str(path)


# ---------------------------------------------------------------------------
# clean_whitespace
# ---------------------------------------------------------------------------

def test_clean_whitespace_normalizes_crlf() -> None:
    assert "\r" not in clean_whitespace("line1\r\nline2")


def test_clean_whitespace_collapses_blank_lines() -> None:
    result = clean_whitespace("a\n\n\n\nb")
    assert "\n\n\n" not in result


def test_clean_whitespace_collapses_spaces() -> None:
    result = clean_whitespace("too   many   spaces")
    assert "  " not in result


def test_clean_whitespace_strips_edges() -> None:
    assert clean_whitespace("  hello  ") == "hello"


# ---------------------------------------------------------------------------
# strip_gutenberg_boilerplate
# ---------------------------------------------------------------------------

def test_strip_gutenberg_boilerplate_removes_header() -> None:
    text = "junk\n*** START OF THE PROJECT GUTENBERG EBOOK ***\nreal content\n*** END OF THE PROJECT GUTENBERG EBOOK ***\nmore junk"
    result = strip_gutenberg_boilerplate(text)
    assert "real content" in result
    assert "junk" not in result


def test_strip_gutenberg_boilerplate_passthrough_when_no_markers() -> None:
    text = "plain text with no markers"
    assert strip_gutenberg_boilerplate(text) == text


# ---------------------------------------------------------------------------
# html_to_text
# ---------------------------------------------------------------------------

def test_html_to_text_strips_tags() -> None:
    result = html_to_text("<p>Hello <b>world</b></p>")
    assert "Hello" in result
    assert "world" in result
    assert "<" not in result


def test_html_to_text_skips_script_content() -> None:
    result = html_to_text("<p>visible</p><script>hidden()</script>")
    assert "visible" in result
    assert "hidden" not in result


def test_html_to_text_skips_style_content() -> None:
    result = html_to_text("<p>text</p><style>.cls { color: red; }</style>")
    assert "text" in result
    assert "color" not in result


# ---------------------------------------------------------------------------
# _english_stats
# ---------------------------------------------------------------------------

def test_english_stats_empty_text() -> None:
    ascii_r, latin_r, stop_r, word_count = _english_stats("")
    assert word_count == 0


def test_english_stats_english_text() -> None:
    text = " ".join(["the and of to in"] * 50)
    ascii_r, latin_r, stop_r, word_count = _english_stats(text)
    assert ascii_r > 0.9
    assert stop_r > 0.5


# ---------------------------------------------------------------------------
# _is_probably_english
# ---------------------------------------------------------------------------

def test_is_probably_english_rejects_short_text() -> None:
    assert not _is_probably_english("hello world")


def test_is_probably_english_accepts_english_corpus() -> None:
    text = " ".join(["the and of to in that is for with as on by from this be"] * 20)
    assert _is_probably_english(text)


def test_is_probably_english_rejects_non_latin() -> None:
    text = " ".join(["的 是 在 不 了 有 和 人 这 中"] * 30)
    assert not _is_probably_english(text)


# ---------------------------------------------------------------------------
# fetch_unavailable
# ---------------------------------------------------------------------------

def test_fetch_unavailable_always_returns_false(capsys) -> None:
    result = fetch_unavailable("no_pd_english: test reason", "test_label", "east", 500)
    assert result is False
    assert "test_label" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# _parse_entry
# ---------------------------------------------------------------------------

def test_parse_entry_unpacks_correctly() -> None:
    def dummy_fn(*args): pass
    entry = (dummy_fn, 123, "my_label", "west", -400)
    fn, fn_args, label, region, year = _parse_entry(entry)
    assert fn is dummy_fn
    assert fn_args == [123]
    assert label == "my_label"
    assert region == "west"
    assert year == -400
