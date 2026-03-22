"""download_pretraining_data.py

Downloads public-domain philosophical and religious texts for LLM pretraining.

Sources:
  - Project Gutenberg      (direct .txt download by ID; gutendex.com API for search)
  - Internet Archive       (advancedsearch JSON API + metadata + download)
  - sacred-texts.com       (HTML scraping + subpage traversal)
  - SuttaCentral           (JSON bilara-data API)
  - Access to Insight      (HTML scraping)

Output layout:
  data/
    east/
      older (BC)/   <- Asian texts dated before 0 CE
      100/          <- Asian texts 0-100 CE
      200/          <- Asian texts 100-200 CE
      ...
    west/
      older (BC)/   <- European texts dated before 0 CE
      100/          <- European texts 0-100 CE
      ...

Each text is assigned based on the earliest known date of the source text.
BCE texts go into "older (BC)"; CE texts go into a 100-year interval folder
whose name is the upper bound of that interval (0-100 -> "100", etc.).

Usage:
    python download_pretraining_data.py
    python download_pretraining_data.py --dry-run   # list sources, no downloads
    python download_pretraining_data.py --label analects_legge  # single source
    python download_pretraining_data.py --skip-unavailable  # skip known-blocked entries
"""

from __future__ import annotations

import argparse
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import quote_plus, urljoin

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_DIR = Path("data")
EAST_DIR = DATA_DIR / "east"
WEST_DIR = DATA_DIR / "west"
BCE_FOLDER = "older (BC)"
for _d in (DATA_DIR, EAST_DIR, WEST_DIR):
    _d.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": (
        "LLMTrainingDataFetcher/1.0 "
        "(academic research; https://github.com/your-org/LLMTraining)"
    )
}
TIMEOUT = 30
DELAY = 0.6       # polite inter-request delay (seconds)
IA_MAX_MB = 30    # skip IA downloads larger than this


# ---------------------------------------------------------------------------
# Time-grouping helpers
# ---------------------------------------------------------------------------

def get_time_folder(year: int) -> str:
    """Return the time-period subfolder name for a given year.

    BCE (year < 0)  ->  "older (BC)"
    CE  (year >= 0) ->  upper bound of the containing 100-year interval,
                       e.g. 0-99 -> "100", 100-199 -> "200", ...
    """
    if year < 0:
        return BCE_FOLDER
    return str((year // 100 + 1) * 100)


def get_folder_path(text_name: str, region: str, year: int) -> Path:
    """Return the destination folder for a text given its region and year."""
    region_dir = EAST_DIR if region == "east" else WEST_DIR
    return region_dir / get_time_folder(year)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def clean_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def strip_gutenberg_boilerplate(text: str) -> str:
    start = re.search(
        r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG", text, re.IGNORECASE
    )
    if start:
        text = text[text.find("\n", start.end()):]
    end = re.search(
        r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG", text, re.IGNORECASE
    )
    if end:
        text = text[: end.start()]
    return text.strip()


class _TextExtractor(HTMLParser):
    """Minimal, dependency-free HTML -> plain text."""

    _SKIP_TAGS = {"script", "style"}

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth: dict[str, int] = {}
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth[tag] = self._skip_depth.get(tag, 0) + 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth[tag] = max(self._skip_depth.get(tag, 0) - 1, 0)

    def handle_data(self, data: str) -> None:
        if any(self._skip_depth.get(t, 0) > 0 for t in self._SKIP_TAGS):
            return
        self._buf.append(data)

    def get_text(self) -> str:
        return "".join(self._buf)


def html_to_text(html: str) -> str:
    p = _TextExtractor()
    p.feed(html)
    return p.get_text()


def _english_stats(text: str) -> tuple[float, float, float, int]:
    if not text.strip():
        return 0.0, 0.0, 0.0, 0
    char_count = len(text)
    ascii_ratio = sum(1 for c in text if ord(c) < 128) / char_count
    alpha_chars = [c for c in text if c.isalpha()]
    if alpha_chars:
        latin_alpha_ratio = sum(1 for c in alpha_chars if ord(c) < 128) / len(alpha_chars)
    else:
        latin_alpha_ratio = 0.0
    words = re.findall(r"[A-Za-z']+", text.lower())
    if not words:
        return ascii_ratio, latin_alpha_ratio, 0.0, 0
    common_words = {
        "the", "and", "of", "to", "in", "that", "is", "for", "with", "as", "on",
        "by", "from", "this", "be", "are", "was", "were", "it", "not", "or", "at",
        "an", "which", "but", "have", "has", "had", "we", "you", "they", "he", "she",
    }
    stopword_ratio = sum(1 for w in words if w in common_words) / len(words)
    return ascii_ratio, latin_alpha_ratio, stopword_ratio, len(words)


def _is_probably_english(text: str) -> bool:
    ascii_ratio, latin_alpha_ratio, stopword_ratio, word_count = _english_stats(text)
    if word_count < 200:
        return False
    return (
        ascii_ratio >= 0.85
        and latin_alpha_ratio >= 0.85
        and stopword_ratio >= 0.01
    )


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def _get(url: str, **kwargs) -> Optional[requests.Response]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, **kwargs)
        r.raise_for_status()
        return r
    except Exception as exc:
        print(f"      [WARN] {url} -> {exc}")
        return None


def _save(label: str, text: str, region: str = "west",
          year: Optional[int] = None) -> None:
    text = clean_whitespace(text)
    if not text:
        print(f"  [SKIP] {label}: empty after cleaning")
        return
    if not _is_probably_english(text):
        ascii_ratio, latin_alpha_ratio, stopword_ratio, word_count = _english_stats(text)
        print(
            "  [SKIP] "
            f"{label}: rejected by English filter "
            f"(ascii={ascii_ratio:.3f}, latin_alpha={latin_alpha_ratio:.3f}, "
            f"stopwords={stopword_ratio:.3f}, words={word_count})"
        )
        return
    if year is not None:
        folder = get_folder_path(label, region, year)
    else:
        folder = EAST_DIR if region == "east" else WEST_DIR
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / f"{label}.txt"
    out.write_text(text, encoding="utf-8")
    kb = len(text.encode()) // 1024
    print(f"  [OK]   {out.relative_to(DATA_DIR)}  ({kb} KB)")


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

def fetch_gutenberg_id(book_id: int, label: str, region: str = "west",
                       year: Optional[int] = None) -> bool:
    urls = [
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
    ]
    for url in urls:
        r = _get(url)
        if r is not None:
            text = strip_gutenberg_boilerplate(r.text)
            _save(label, text, region, year)
            return True
        time.sleep(DELAY)
    print(f"  [FAIL] Gutenberg #{book_id} ({label})")
    return False


def fetch_gutenberg_search(query: str, label: str, region: str = "west",
                           year: Optional[int] = None) -> bool:
    api_url = f"https://gutendex.com/books/?search={quote_plus(query)}&languages=en"
    r = _get(api_url)
    if r is None:
        return False
    books = r.json().get("results", [])
    if not books:
        print(f"  [FAIL] Gutendex '{query}': no results")
        return False
    for book in books[:5]:
        formats = book.get("formats", {})
        txt_url = (
            formats.get("text/plain; charset=utf-8")
            or formats.get("text/plain; charset=us-ascii")
            or formats.get("text/plain")
        )
        if not txt_url:
            continue
        time.sleep(DELAY)
        dr = _get(txt_url)
        if dr is not None:
            text = strip_gutenberg_boilerplate(dr.text)
            _save(label, text, region, year)
            return True
    print(f"  [FAIL] Gutendex '{query}' ({label}): no downloadable text found")
    return False


def fetch_internet_archive(query: str, label: str, region: str = "west",
                           year: Optional[int] = None, max_candidates: int = 15) -> bool:
    search_url = (
        "https://archive.org/advancedsearch.php"
        f"?q={quote_plus(query)}+mediatype:texts"
        f"&output=json&rows={max_candidates}"
        "&fl[]=identifier&fl[]=title&fl[]=filesize"
    )
    r = _get(search_url)
    if r is None:
        return False
    docs = r.json().get("response", {}).get("docs", [])
    if not docs:
        print(f"  [FAIL] IA '{query}': no search results")
        return False
    for doc in docs:
        identifier = doc["identifier"]
        time.sleep(DELAY)
        meta_r = _get(f"https://archive.org/metadata/{identifier}")
        if meta_r is None:
            continue
        files = meta_r.json().get("files", [])
        candidates = [f for f in files if f["name"].endswith(".txt")
                      and "_djvu" not in f["name"]]
        candidates += [f for f in files if f["name"].endswith("_djvu.txt")]
        if not candidates:
            continue
        for txt in candidates:
            size_bytes = int(txt.get("size", 0) or 0)
            if size_bytes > IA_MAX_MB * 1024 * 1024:
                print(f"      [SKIP] {txt['name']} too large "
                      f"({size_bytes // (1024*1024)} MB > {IA_MAX_MB} MB)")
                continue
            dl_url = f"https://archive.org/download/{identifier}/{txt['name']}"
            time.sleep(DELAY)
            try:
                dr = requests.get(dl_url, headers=HEADERS, timeout=TIMEOUT)
                if dr.status_code in (401, 403):
                    print(f"      [SKIP] {identifier}: HTTP {dr.status_code} (restricted)")
                    break
                dr.raise_for_status()
            except Exception as exc:
                print(f"      [WARN] {dl_url} -> {exc}")
                continue
            _save(label, dr.text, region, year)
            return True
    print(f"  [FAIL] IA '{query}' ({label}): no accessible text file found")
    return False


def fetch_sacred_texts(index_url: str, label: str, region: str = "west",
                       year: Optional[int] = None, max_subpages: int = 80) -> bool:
    r = _get(index_url)
    if r is None:
        return False
    base = index_url.rsplit("/", 1)[0] + "/"
    links_raw = re.findall(r'href="([^"#?]+\.htm[l]?)"', r.text, re.IGNORECASE)
    seen: set[str] = set()
    pages: list[str] = []
    for lnk in links_raw:
        if lnk.startswith("http"):
            continue
        full = urljoin(base, lnk)
        if full not in seen:
            seen.add(full)
            pages.append(full)
    if not pages:
        pages = [index_url]
    chunks: list[str] = []
    for url in pages[:max_subpages]:
        time.sleep(DELAY)
        pr = _get(url)
        if pr is not None:
            chunks.append(html_to_text(pr.text))
    if not chunks:
        print(f"  [FAIL] sacred-texts {index_url}: nothing scraped")
        return False
    _save(label, "\n\n".join(chunks), region, year)
    return True


def fetch_access_to_insight(root_url: str, label: str, region: str = "east",
                            year: Optional[int] = None, max_suttas: int = 400) -> bool:
    def _collect_links(url: str) -> list[str]:
        r = _get(url)
        if r is None:
            return []
        raw = re.findall(r'href="([^"#?]+\.html)"', r.text, re.IGNORECASE)
        seen: set[str] = set()
        out: list[str] = []
        for lnk in raw:
            full = urljoin(url, lnk)
            if "accesstoinsight.org" in full and "/tipitaka/" in full and full not in seen:
                seen.add(full)
                out.append(full)
        return out

    nikaya_indexes = [u for u in _collect_links(root_url) if u.endswith("index.html")]
    if not nikaya_indexes:
        print(f"  [FAIL] access-to-insight: no nikaya indexes at {root_url}")
        return False
    print(f"      Found {len(nikaya_indexes)} nikaya indexes - collecting sutta links ...")
    sutta_urls: list[str] = []
    seen_suttas: set[str] = set()
    for idx_url in nikaya_indexes:
        time.sleep(DELAY)
        for u in _collect_links(idx_url):
            if not u.endswith("index.html") and u not in seen_suttas:
                seen_suttas.add(u)
                sutta_urls.append(u)
    if not sutta_urls:
        print(f"  [FAIL] access-to-insight: no sutta pages found")
        return False
    print(f"      Found {len(sutta_urls)} sutta pages - downloading ...")
    chunks: list[str] = []
    for url in sutta_urls[:max_suttas]:
        time.sleep(DELAY)
        pr = _get(url)
        if pr is not None:
            chunks.append(html_to_text(pr.text))
    if not chunks:
        print(f"  [FAIL] access-to-insight: no text retrieved")
        return False
    _save(label, "\n\n".join(chunks), region, year)
    return True


def fetch_suttacentral(nikaya: str, label: str, region: str = "east",
                       year: Optional[int] = None, translator: str = "sujato") -> bool:
    plex_url = f"https://suttacentral.net/api/suttaplex/{nikaya}?lang=en"
    r = _get(plex_url)
    if r is None:
        return False
    items = r.json() if isinstance(r.json(), list) else []
    uids = [item["uid"] for item in items if item.get("type") == "leaf"]
    if not uids:
        print(f"  [FAIL] SuttaCentral '{nikaya}': no leaf sutta UIDs found")
        return False
    print(f"      Found {len(uids)} suttas in '{nikaya}' - downloading ...")
    chunks: list[str] = []
    for uid in uids[:300]:
        time.sleep(DELAY)
        seg_url = (
            f"https://suttacentral.net/api/bilarasuttas/{uid}/{translator}"
            "?current_edition=en"
        )
        sr = _get(seg_url)
        if sr is None:
            continue
        data = sr.json()
        trans: dict = data.get("translation_text", {})
        if trans:
            chunks.append("\n".join(trans.values()))
    if not chunks:
        print(f"  [FAIL] SuttaCentral '{nikaya}': no segments retrieved")
        return False
    _save(label, "\n\n".join(chunks), region, year)
    return True


def fetch_gutenberg_ids(book_ids: list[int], label: str, region: str = "west",
                        year: Optional[int] = None) -> bool:
    """Try multiple PG book IDs in order, return on first success."""
    for book_id in book_ids:
        if fetch_gutenberg_id(book_id, label, region, year):
            return True
        time.sleep(DELAY)
    print(f"  [FAIL] Gutenberg IDs {book_ids} ({label}): none succeeded")
    return False


def fetch_ia_identifier(identifier: str, label: str, region: str = "west",
                        year: Optional[int] = None) -> bool:
    """Download directly from a known Internet Archive identifier, bypassing search.

    Use when the search API fails to find an item that is known to exist on IA.
    The identifier is the slug in archive.org/details/<identifier>.
    """
    time.sleep(DELAY)
    meta_url = f"https://archive.org/metadata/{identifier}"
    meta_r = _get(meta_url)
    if meta_r is None:
        print(f"  [FAIL] IA direct {identifier} ({label}): metadata fetch failed")
        return False

    files = meta_r.json().get("files", [])
    candidates = [f for f in files if f["name"].endswith(".txt")
                  and "_djvu" not in f["name"]]
    candidates += [f for f in files if f["name"].endswith("_djvu.txt")]
    if not candidates:
        print(f"  [FAIL] IA direct {identifier} ({label}): no .txt files in metadata")
        return False

    for txt in candidates:
        size_bytes = int(txt.get("size", 0) or 0)
        if size_bytes > IA_MAX_MB * 1024 * 1024:
            continue
        dl_url = f"https://archive.org/download/{identifier}/{txt['name']}"
        time.sleep(DELAY)
        try:
            dr = requests.get(dl_url, headers=HEADERS, timeout=TIMEOUT)
            if dr.status_code in (401, 403):
                print(f"      [SKIP] {identifier}: HTTP {dr.status_code} (restricted)")
                break
            dr.raise_for_status()
        except Exception as exc:
            print(f"      [WARN] {dl_url} -> {exc}")
            continue
        _save(label, dr.text, region, year)
        return True

    print(f"  [FAIL] IA direct {identifier} ({label}): no accessible text file")
    return False


def fetch_unavailable(reason: str, label: str, region: str = "east",
                      year: Optional[int] = None) -> bool:
    """Placeholder for texts with no accessible PD English translation.

    Always fails with an explanatory message. The entry is retained in
    SOURCES so the gap is visible in --dry-run output.
    """
    print(f"  [N/A]  {label}: {reason}")
    return False


# ---------------------------------------------------------------------------
# Source catalogue
# ---------------------------------------------------------------------------
# Each entry: (fetcher_fn, *fn_args, label, region, year)
#   label  - output filename stem
#   region - "east" or "west"
#   year   - earliest known year of the source text (negative = BCE)
#
# Entries using fetch_unavailable document WHY a text cannot be downloaded:
#   - "no_pd_english"      : no public-domain English translation exists
#   - "copyright_trans"    : only known English translations are in copyright
#   - "no_english_trans"   : no English translation exists at all
#   - "restricted_ia"      : IA copy exists but returns 401/403
#   - "lost_work"          : primary work is lost; only fragments/doxography remain

SOURCES: list[tuple] = [

    # ==========================================================================
    # EASTERN PHILOSOPHERS
    # ==========================================================================

    # ── CHINA: Guan Zhong (d. 645 BCE) ───────────────────────────────────────
    # Guanzi — partial English translations; no complete PD English text confirmed
    (fetch_internet_archive, "Guanzi Guan Zhong Chinese philosophy",
     "guanzi_guan_zhong", "east", -645),

    # ── CHINA: Sun Tzu (c. 544-496 BCE) ──────────────────────────────────────
    # Art of War — Giles translation 1910, PD; PG #132
    (fetch_gutenberg_id, 132, "sun_tzu_art_of_war", "east", -544),

    # ── INDIA: Vedic Sages / Rigveda (~1500-1000 BCE) ─────────────────────────
    # Vasishtha, Atri, Vishvamitra, Agastya, Jamadagni, Bharadwaja, Dirghatamas
    # covered by the Rigveda hymns — Griffith translation (1896), PD
    (fetch_gutenberg_id, 46700, "rigveda_griffith", "east", -1200),

    # ── INDIA: Lopamudra (earliest female philosopher, ~1500 BCE) ─────────────
    # Covered within Rigveda Griffith above (Lopamudra appears in Rigveda 1.179)
    # No separate PD text needed — cross-reference rigveda_griffith

    # ── INDIA: Parshvanatha (c. 872-772 BCE) ─────────────────────────────────
    # 23rd Jain Tirthankara; no primary works survive in PD English translation
    # Covered within jain_sutras_jacobi (SBE vols 22 & 45) as tradition context
    (fetch_unavailable,
     "no_pd_english: primary teachings attributed to Parshvanatha survive only "
     "within the Jain canonical tradition covered by jain_sutras_jacobi; "
     "no standalone PD English text exists",
     "parshvanatha_primary", "east", -800),

    # ── INDIA: Aruni (~750-650 BCE) ───────────────────────────────────────────
    # Aruni's teachings recorded in Chandogya Upanishad — covered by upanishads_muller_sbe15
    # No standalone PD text needed

    # ── INDIA: Upanishads / Yajnavalkya (~700-600 BCE) ───────────────────────
    (fetch_gutenberg_id, 2034, "upanishads_muller_sbe15", "east", -800),

    # ── INDIA: Pali Canon / Siddhartha Gautama (~480 BCE) ────────────────────
    (fetch_suttacentral, "dn",  "pali_dn_sujato",  "east", -480),
    (fetch_suttacentral, "mn",  "pali_mn_sujato",  "east", -480),
    (fetch_suttacentral, "sn",  "pali_sn_sujato",  "east", -480),
    (fetch_suttacentral, "an",  "pali_an_sujato",  "east", -480),
    (fetch_suttacentral, "dhp", "pali_dhp_sujato", "east", -480),
    (fetch_suttacentral, "kn",  "pali_kn_sujato",  "east", -480),
    (fetch_access_to_insight,
     "https://www.accesstoinsight.org/tipitaka/",
     "pali_thanissaro_ati", "east", -480),

    # ── INDIA: Makkhali Gosala / Ajivika (~600-500 BCE) ──────────────────────
    # Ajivika texts are entirely lost; known only through Buddhist/Jain polemics
    (fetch_unavailable,
     "lost_work: Ajivika canonical texts are completely lost; Gosala's teachings "
     "survive only as fragments in Buddhist (Digha Nikaya DN 2) and Jain sources "
     "already covered in pali_dn_sujato and jain_sutras_jacobi",
     "gosala_ajivika", "east", -550),

    # ── INDIA: Panini (~600-500 BCE) ─────────────────────────────────────────
    # Ashtadhyayi — philosophical grammar; translations are highly technical Sanskrit
    (fetch_internet_archive, "Panini Sanskrit grammar Ashtadhyayi English",
     "panini_ashtadhyayi", "east", -500),

    # ── INDIA: Brihaspati / Charvaka (~600-400 BCE) ───────────────────────────
    # Charvaka texts are lost; known only through hostile summaries
    (fetch_unavailable,
     "lost_work: Brihaspati's Barhaspatya-sutras are entirely lost; "
     "Charvaka/Lokayata philosophy survives only in opponents' summaries "
     "(e.g. Shankara's Brahmasutra-bhashya); no standalone PD English primary text",
     "brihaspati_charvaka", "east", -500),

    # ── INDIA: Mahavira / Jain Canon (~599-527 BCE) ───────────────────────────
    (fetch_internet_archive, "Jaina Sutras Jacobi Sacred Books East",
     "jain_sutras_jacobi", "east", -527),

    # ── INDIA: Mahakasyapa (dates uncertain, early Buddhist) ─────────────────
    # No primary works survive; known from canonical accounts within Pali Canon
    # covered by pali_*_sujato above

    # ── CHINA: Laozi / Tao Te Ching (~6th c. BCE) ────────────────────────────
    (fetch_gutenberg_id, 216, "tao_te_ching_legge", "east", -550),

    # ── CHINA: Confucius / Analects (~551-479 BCE) ────────────────────────────
    (fetch_gutenberg_id, 3330, "analects_legge", "east", -479),

    # ── CHINA: Mozi (~470-390 BCE) ────────────────────────────────────────────
    (fetch_internet_archive, "Works Motse Yi-Pao Mei",
     "mozi_mei", "east", -470),

    # ── INDIA: Badarayana (~500-400 BCE) ─────────────────────────────────────
    # Brahma Sutras — Thibaut translation (SBE vols 34 & 38), PD
    (fetch_internet_archive, "Brahma Sutras Badarayana Thibaut Sacred Books East",
     "brahma_sutras_thibaut", "east", -450),

    # ── INDIA: Kapila (~500 BCE) — Sankhya ───────────────────────────────────
    # Sankhya-karika (Ishvarakrishna, c. 4th CE, codifies Kapila's school)
    # Ballantyne 1855 translation, PD
    (fetch_internet_archive, "Sankhya Karika Ballantyne Kapila",
     "sankhya_karika_kapila", "east", -500),

    # ── INDIA: Shvetashvatara (~400-300 BCE) ──────────────────────────────────
    # Shvetashvatara Upanishad — covered in Muller SBE15 (upanishads_muller_sbe15)
    # Also available in SBE Vol 15 second series; no separate PD text needed

    # ── CHINA: Liezi (~440-360 BCE) ───────────────────────────────────────────
    # Book of Lieh-Tze — Giles 1912 translation, PD
    # IA identifier: bookofliehtze00liez (Giles 1912)
    # liezi_giles: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier bookofliehtze00liez exists but contains only PDF/DjVu scans — no .txt file in metadata; Giles 1912 trans. not available as plain text",
     "liezi_giles", "east", -400),

    # ── CHINA: Gaozi (~420 BCE) ───────────────────────────────────────────────
    # No independent works survive; debates with Mencius recorded in Mengzi Book 6
    # covered by mencius_legge
    (fetch_unavailable,
     "lost_work: Gaozi left no independent writings; his philosophy is known "
     "entirely from his debates with Mencius preserved in Mengzi Book 6, "
     "which is covered by mencius_legge",
     "gaozi_works", "east", -420),

    # ── CHINA: Mencius (~372-289 BCE) ─────────────────────────────────────────
    (fetch_gutenberg_id, 38406, "mencius_legge", "east", -372),

    # ── CHINA: Zhuangzi (~4th c. BCE) ─────────────────────────────────────────
    (fetch_gutenberg_id, 29724, "zhuangzi_legge", "east", -350),

    # ── CHINA: Yang Zhu (~370-319 BCE) ────────────────────────────────────────
    # Yangism survives only in fragments within Liezi (ch. 7) and Zhuangzi
    # covered within liezi_giles and zhuangzi_legge
    (fetch_unavailable,
     "lost_work: Yang Zhu left no independent works; his hedonist philosophy "
     "survives in Liezi chapter 7 (covered by liezi_giles) and scattered "
     "references in Zhuangzi and Mencius",
     "yang_zhu_works", "east", -370),

    # ── CHINA: Xu Xing (~315 BCE) ─────────────────────────────────────────────
    # Agriculturalist school; no surviving texts
    (fetch_unavailable,
     "lost_work: Xu Xing's agrarian philosophy (Nongjia school) is known only "
     "from Mencius 3A:4, which is covered by mencius_legge; no primary texts survive",
     "xu_xing_works", "east", -315),

    # ── CHINA: Gongsun Longzi (~fl. 300 BCE) ─────────────────────────────────
    # School of Names — no complete PD English translation; IA search fails
    (fetch_unavailable,
     "no_pd_english: No complete public-domain English translation of "
     "Gongsun Longzi's works exists; partial academic translations are copyright",
     "gongsun_longzi", "east", -300),

    # ── CHINA: Hui Shi (~4th c. BCE) ─────────────────────────────────────────
    # Fragments only, preserved in Zhuangzi — covered by zhuangzi_legge
    (fetch_unavailable,
     "lost_work: Hui Shi's ten propositions survive only as fragments in "
     "Zhuangzi ch. 33 (covered by zhuangzi_legge); no independent PD text",
     "hui_shi_works", "east", -370),

    # ── CHINA: Shang Yang (~d. 338 BCE) ──────────────────────────────────────
    # Book of Lord Shang — Duyvendak 1928 trans.; IA identifier: booklordshang00shanrich
    # shang_yang_book_lord_shang: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier booklordshang00shanrich exists but contains only PDF/DjVu scans — no .txt file in metadata; Duyvendak 1928 trans. not available as plain text",
     "shang_yang_book_lord_shang", "east", -350),

    # ── CHINA: Shen Buhai (~d. 337 BCE) ──────────────────────────────────────
    # No complete surviving text; fragments only
    (fetch_unavailable,
     "lost_work: Shen Buhai's administrative writings survive only as fragments "
     "quoted in Han Feizi (covered by han_feizi_liao); no independent PD text exists",
     "shen_buhai_works", "east", -337),

    # ── CHINA: Shen Dao (~350-275 BCE) ───────────────────────────────────────
    # Fragments only; no PD English translation
    (fetch_unavailable,
     "lost_work: Shen Dao's writings survive only as fragments; no PD English "
     "translation of reconstructed texts exists",
     "shen_dao_works", "east", -310),

    # ── CHINA: Song Xing (~360-290 BCE) ──────────────────────────────────────
    # Fragments only within Zhuangzi and Xunzi
    (fetch_unavailable,
     "lost_work: Song Xing's philosophy survives only as fragments in Zhuangzi "
     "and Xunzi (both covered); no independent PD English text",
     "song_xing_works", "east", -325),

    # ── CHINA: Xunzi (~310-237 BCE) ───────────────────────────────────────────
    (fetch_internet_archive, "Works Hsuntze",
     "xunzi_dubs", "east", -300),

    # ── CHINA: Zou Yan (~305-240 BCE) ─────────────────────────────────────────
    # Naturalist/Yin-Yang school; no surviving texts
    (fetch_unavailable,
     "lost_work: Zou Yan's works are entirely lost; his cosmological theories "
     "survive only as summaries in Shiji and other Han histories; "
     "no PD English primary text",
     "zou_yan_works", "east", -270),

    # ── CHINA: Han Feizi (~d. 233 BCE) ────────────────────────────────────────
    (fetch_internet_archive, "Complete Works Han Fei Tzu Liao",
     "han_feizi_liao", "east", -280),

    # ── INDIA: Chanakya (~350-275 BCE) ────────────────────────────────────────
    # Arthashastra — Shamasastry 1915 translation, PD
    (fetch_internet_archive, "Arthashastra Chanakya Kautilya Shamasastry",
     "arthashastra_chanakya", "east", -300),

    # ── INDIA: Jaimini (~300-200 BCE) — Purva Mimamsa ────────────────────────
    # Mimamsa Sutras — Jha trans. (Sacred Books of the Hindus), PD
    (fetch_internet_archive, "Mimamsa Sutras Jaimini Jha",
     "mimamsa_sutras_jaimini", "east", -250),

    # ── INDIA: Aksapada Gautama (~2nd c. BCE) — Nyaya ────────────────────────
    (fetch_internet_archive, "Sacred Books Hindus Nyaya Sutras Gautama",
     "nyaya_sutras_gautama", "east", -200),

    # ── INDIA: Kanada — Vaisheshika (~3rd-2nd c. BCE) ─────────────────────────
    # Vaisesika Sutras — Nandalal Sinha trans. (Sacred Books of Hindus), PD
    (fetch_internet_archive, "Vaisesika Sutras Kanada Nandalal Sinha",
     "vaisesika_sutras_kanada", "east", -200),

    # ── INDIA: Pingala (~3rd-2nd c. BCE) ─────────────────────────────────────
    # Chandahshastra — highly technical Sanskrit prosody; no useful PD English version
    (fetch_unavailable,
     "no_pd_english: Pingala's Chandahshastra (prosody/combinatorics treatise) "
     "has no accessible public-domain English translation; Weber 1863 German trans. "
     "not English; content is technical notation not useful for LLM philosophy training",
     "pingala_chandahshastra", "east", -200),

    # ── INDIA: Bhagavad Gita (~400-200 BCE) ───────────────────────────────────
    (fetch_gutenberg_id, 2388, "bhagavad_gita_arnold", "east", -300),

    # ── INDIA: Patanjali (~2nd c. BCE) ────────────────────────────────────────
    (fetch_internet_archive, "Yoga Sutras Patanjali",
     "yoga_sutras_patanjali", "east", -150),

    # ── INDIA: Thiruvalluvar (~1st c. BCE - 2nd c. CE) ────────────────────────
    # Tirukkural — Drew & Lazarus 1885 translation, PD
    (fetch_internet_archive, "Thiruvalluvar Tirukkural Drew Lazarus",
     "tirukkural_thiruvalluvar", "east", 100),

    # ── CHINA: Lü Buwei (~290-235 BCE) ───────────────────────────────────────
    # Lüshi Chunqiu — no complete PD English translation
    (fetch_unavailable,
     "no_pd_english: Lü Buwei's Lüshi Chunqiu (Spring and Autumn Annals of "
     "Master Lü) has no complete public-domain English translation; "
     "Knoblock & Riegel 2000 trans. is in copyright",
     "lu_buwei_lushi_chunqiu", "east", -250),

    # ── CHINA: Jia Yi (~201-169 BCE) ─────────────────────────────────────────
    # Essays — partial PD translations available through IA
    # Jia Yi: no standalone PD English translation confirmed on IA
    (fetch_unavailable,
     "no_pd_english: Jia Yi's Han dynasty political essays have no confirmed "
     "public-domain English translation accessible on IA or PG",
     "jia_yi_essays", "east", -175),

    # ── CHINA: Dong Zhongshu (~176-104 BCE) ──────────────────────────────────
    # Chunqiu Fanlu — no complete PD English translation
    (fetch_unavailable,
     "no_pd_english: Dong Zhongshu's Chunqiu Fanlu (Luxuriant Dew of the "
     "Spring and Autumn Annals) has no public-domain English translation; "
     "Queen 2016 trans. is in copyright",
     "dong_zhongshu_chunqiu_fanlu", "east", -150),

    # ── CHINA: Liu An (~179-122 BCE) ─────────────────────────────────────────
    # Huainanzi — Major 2010 trans. is in copyright; older partial translations PD
    (fetch_internet_archive, "Huainanzi Liu An Chinese philosophy",
     "liu_an_huainanzi", "east", -140),

    # ── CHINA: Yang Xiong (~53 BCE - 18 CE) ──────────────────────────────────
    # Fa Yan / Model Sayings — Knoblock 1999 is copyright; Brewitt-Taylor 1925 may be PD
    # Yang Xiong Fa Yan: Knoblock 1999 copyright; no PD English confirmed
    (fetch_unavailable,
     "no_pd_english: Yang Xiong's Fa Yan has no confirmed public-domain English "
     "translation on IA; Knoblock 1999 is copyright",
     "yang_xiong_fa_yan", "east", -10),

    # ── CHINA: Wang Chong (~27-97 CE) ─────────────────────────────────────────
    # Lunheng — Forke 1907/1911 translation, PD
    # Wang Chong Lunheng — Forke 1907/1911 trans. IA: lunheng01wang
    (fetch_ia_identifier, "lunheng01wang",
     "wang_chong_lunheng", "east", 80),

    # ── INDIA: Ashvaghosha (~1st c. CE) ──────────────────────────────────────
    (fetch_internet_archive, "Buddhacarita Cowell",
     "buddhacharita_cowell", "east", 80),
    (fetch_internet_archive, "Awakening Faith Mahayana",
     "awakening_of_faith_suzuki", "east", 100),

    # ── INDIA: Milindapanha (~1st c. CE) ─────────────────────────────────────
    (fetch_internet_archive, "Questions King Milinda Rhys Davids",
     "milindapanha_rhys_davids", "east", 100),

    # ── INDIA: Nagarjuna (~150-250 CE) ────────────────────────────────────────
    (fetch_internet_archive, "Mulamadhyamakakarika Nagarjuna",
     "nagarjuna_mulamadhyamakakarika", "east", 200),

    # ── CHINA: Zheng Xuan (~127-200 CE) ──────────────────────────────────────
    # Commentaries on Confucian classics; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Zheng Xuan's commentaries on the Confucian classics "
     "have no public-domain English translation; modern sinological translations "
     "are all in copyright",
     "zheng_xuan_commentaries", "east", 165),

    # ── INDIA: Kundakunda (~2nd c. CE) — Jain ────────────────────────────────
    # Panchastikayasara — Chakravarti 1920 trans. PD
    # Kundakunda Panchastikayasara — Chakravarti 1920. IA: panchastikayasar00kundrich
    # kundakunda_panchastikayasara: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier panchastikayasar00kundrich exists but contains only PDF/DjVu scans — no .txt file in metadata; Chakravarti 1920 trans. not available as plain text",
     "kundakunda_panchastikayasara", "east", 150),

    # ── INDIA: Umasvati (~2nd c. CE) — Jain ──────────────────────────────────
    # Tattvarthasutra — Jacobi trans. partially available
    # Umasvati Tattvarthasutra — Ghoshal 1920. IA: tattvarthadhigam00umasrich
    # umasvati_tattvarthasutra: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier tattvarthadhigam00umasrich exists but contains only PDF/DjVu scans — no .txt file in metadata",
     "umasvati_tattvarthasutra", "east", 150),

    # ── CHINA: He Yan (~190-249 CE) ───────────────────────────────────────────
    # Lunyu jijie (commentary on Analects); no PD English translation
    (fetch_unavailable,
     "no_pd_english: He Yan's Lunyu jijie (collected explanations of the Analects) "
     "has no public-domain English translation",
     "he_yan_commentary", "east", 220),

    # ── CHINA: Ruan Ji (~210-263 CE) ─────────────────────────────────────────
    # Wenxuan poems; no PD English philosophy translation
    (fetch_unavailable,
     "no_pd_english: Ruan Ji's philosophical essays (Daren xiansheng zhuan) "
     "have no public-domain English translation; Holzman 1976 is in copyright",
     "ruan_ji_works", "east", 235),

    # ── CHINA: Ji Kang (~223-262 CE) ─────────────────────────────────────────
    # Essays on Music and Naturalness; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Ji Kang's philosophical essays have no public-domain "
     "English translation; Henricks 1983 trans. is in copyright",
     "ji_kang_works", "east", 240),

    # ── INDIA: Vasubandhu (~4th c. CE) ────────────────────────────────────────
    (fetch_internet_archive, "Hinduism Buddhism Eliot historical sketch",
     "vasubandhu_eliot_hinduism_buddhism", "east", 350),

    # ── INDIA: Asanga (~4th c. CE) ────────────────────────────────────────────
    (fetch_internet_archive, "Lankavatara Sutra Suzuki Buddhist",
     "lankavatara_sutra_suzuki", "east", 350),

    # ── CHINA: Wang Bi (~226-249 CE) ─────────────────────────────────────────
    (fetch_unavailable,
     "copyright_trans: Wang Bi's commentaries on the Tao Te Ching and I Ching "
     "were translated by Richard Lynn (1994 Columbia UP) — in copyright; "
     "no earlier PD English translation exists",
     "wang_bi_commentaries", "east", 240),

    # ── CHINA: Pei Wei (~267-300 CE) ─────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Pei Wei's Chongyu lun (Discourse on Esteeming Being) "
     "has no public-domain English translation",
     "pei_wei_chongyu", "east", 280),

    # ── CHINA: Guo Xiang (~d. 312 CE) ────────────────────────────────────────
    # Commentary on Zhuangzi; portions translated in Fung Yu-lan (PD)
    # Fung Yu-lan History of Chinese Philosophy contains extensive Guo Xiang quotes
    # guo_xiang_zhuangzi_commentary: restricted_ia — see rationale MD
    (fetch_unavailable,
     "restricted_ia: IA identifier historyofchinese0002fung returns HTTP 401 — access restricted; Fung Yu-lan History of Chinese Philosophy Vol.2 not publicly accessible",
     "guo_xiang_zhuangzi_commentary", "east", 300),

    # ── INDIA: Bodhidharma (~440-528 CE) ─────────────────────────────────────
    # Two Entrances and Four Acts; older PD trans. available via IA
    # Broughton 1999 is copyright; use older Suzuki/Dumoulin secondary coverage
    # bodhidharma_two_entrances: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier essaysinzenbuddh01suzu exists but contains only PDF/DjVu scans — no .txt file in metadata; Suzuki Essays in Zen Vol.1 not available as plain text",
     "bodhidharma_two_entrances", "east", 480),

    # ── INDIA: Vatsyayana (~450-500 CE) ──────────────────────────────────────
    # Nyaya-bhasya (commentary on Nyaya Sutras); no PD English translation
    (fetch_unavailable,
     "no_pd_english: Vatsyayana's Nyaya-bhasya has no public-domain English "
     "translation; Jha's SBH Vol.8 covers only the Sutras themselves",
     "vatsyayana_nyaya_bhasya", "east", 475),

    # ── INDIA: Bhartrhari (~450-510 CE) ──────────────────────────────────────
    # Vakyapadiya; no complete PD English translation
    (fetch_unavailable,
     "no_pd_english: Bhartrhari's Vakyapadiya (philosophy of language) "
     "has no complete public-domain English translation; "
     "Iyer 1965-1974 trans. is in copyright",
     "bhartrhari_vakyapadiya", "east", 475),

    # ── INDIA: Buddhaghosa (~5th c. CE) ───────────────────────────────────────
    (fetch_internet_archive, "Visuddhimagga path purification",
     "visuddhimagga_buddhaghosa", "east", 430),

    # ── INDIA: Dignaga (~5th c. CE) ───────────────────────────────────────────
    # Pramanasamuccaya; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Dignaga's Pramanasamuccaya (Buddhist epistemology) "
     "has no public-domain English translation; Hattori 1968 is in copyright",
     "dignaga_pramanasamuccaya", "east", 480),

    # ── INDIA: Siddhasena Divakara (~5th c. CE) — Jain ───────────────────────
    # Sanmatitarka; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Siddhasena Divakara's Sanmatitarka has no public-domain "
     "English translation",
     "siddhasena_sanmatitarka", "east", 480),

    # ── INDIA: Bhaviveka (~6th c. CE) ────────────────────────────────────────
    # Prajnapradipa; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Bhaviveka's Prajnapradipa has no public-domain English "
     "translation; Eckel 1992 is in copyright",
     "bhaviveka_prajnapradipa", "east", 550),

    # ── INDIA: Silabhadra (~529-645 CE) ──────────────────────────────────────
    # No independent works in PD English; known through Xuanzang's travelogue
    (fetch_unavailable,
     "no_pd_english: Silabhadra left no works surviving in PD English; "
     "known primarily through Xuanzang's travelogue (see xuanzang_great_tang_records)",
     "silabhadra_works", "east", 580),

    # ── CHINA: Zhiyi (~538-597 CE) ────────────────────────────────────────────
    # Mohe Zhiguan (Great Calming and Contemplation); no PD English translation
    (fetch_unavailable,
     "no_pd_english: Zhiyi's Mohe Zhiguan and Tiantai philosophy texts "
     "have no public-domain English translation; Donner & Stevenson 1993 is copyright",
     "zhiyi_mohe_zhiguan", "east", 570),

    # ── CHINA: Jizang (~549-623 CE) ───────────────────────────────────────────
    # Sanlun school; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Jizang's Sanlun (Three Treatises) school texts "
     "have no public-domain English translation",
     "jizang_sanlun", "east", 585),

    # ── CHINA: Dushun (~557-640 CE) ───────────────────────────────────────────
    # Hua-yen/Huayan school; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Dushun's Hua-yen writings have no public-domain English "
     "translation; Cleary 1983 is in copyright",
     "dushun_huayan", "east", 600),

    # ── CHINA: Xuanzang (~602-664 CE) ─────────────────────────────────────────
    # Great Tang Records on the Western Regions — Beal 1884 trans., PD
    # IA identifier: siyukibuddhistre01beal
    # xuanzang_great_tang_records: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier siyukibuddhistre01beal exists but contains only PDF/DjVu scans — no .txt file in metadata; Beal 1884 Si-yu-ki not available as plain text",
     "xuanzang_great_tang_records", "east", 646),

    # ── CHINA: Dayi Daoxin (~580-651 CE) ─────────────────────────────────────
    # Chan patriarch; no independent PD English text
    (fetch_unavailable,
     "no_pd_english: Dayi Daoxin's Chan teachings survive only in later "
     "transmission records; no public-domain English translation of primary works",
     "dayi_daoxin_works", "east", 615),

    # ── CHINA: Shandao (~613-681 CE) ─────────────────────────────────────────
    # Pure Land commentaries; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Shandao's Pure Land commentaries have no public-domain "
     "English translation",
     "shandao_pure_land", "east", 645),

    # ── CHINA: Hong Ren (~601-674 CE) ─────────────────────────────────────────
    # Fifth Chan patriarch; no independent PD English text
    (fetch_unavailable,
     "no_pd_english: Hong Ren's Treatise on the Essentials of Cultivating the "
     "Mind has no public-domain English translation",
     "hong_ren_treatise", "east", 638),

    # ── CHINA: Yuquan Shenxiu (~606-706 CE) ──────────────────────────────────
    # Northern Chan school; no independent PD English text
    (fetch_unavailable,
     "no_pd_english: Yuquan Shenxiu's works have no public-domain English "
     "translation; he is known primarily through the Platform Sutra polemic "
     "covered by platform_sutra_huineng",
     "shenxiu_northern_chan", "east", 656),

    # ── CHINA: Cheng Xuanying (~631-655 CE) ──────────────────────────────────
    # Commentary on Zhuangzi; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Cheng Xuanying's Zhuangzi commentary has no public-domain "
     "English translation",
     "cheng_xuanying_commentary", "east", 643),

    # ── CHINA: Huineng (~638-713 CE) ──────────────────────────────────────────
    (fetch_internet_archive, "Platform sutra patriarch",
     "platform_sutra_huineng", "east", 700),

    # ── CHINA: Fazang (~643-712 CE) ───────────────────────────────────────────
    # Huayan school; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Fazang's Huayan texts (e.g. Treatise on the Golden Lion) "
     "have no public-domain English translation; Cleary 1983 is copyright",
     "fazang_huayan", "east", 675),

    # ── KOREA: Wonhyo (~617-686 CE) ───────────────────────────────────────────
    (fetch_internet_archive, "Wonhyo Korean Awakening Faith Mahayana",
     "wonhyo_awakening_faith", "east", 650),

    # ── KOREA: Woncheuk (~613-696 CE) ─────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Woncheuk's commentaries (especially on the Samdhinirmocana "
     "Sutra) have no public-domain English translation",
     "woncheuk_commentaries", "east", 650),

    # ── KOREA: Uisang (~625-702 CE) ───────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Uisang's Diagram of the Dharmadhatu (Hwaeom ilseung "
     "beopgye do) has no public-domain English translation",
     "uisang_dharmadhatu", "east", 660),

    # ── INDIA: Chandrakirti (~born c. 600 CE) ────────────────────────────────
    # Madhyamakavatara; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Chandrakirti's Madhyamakavatara (Entering the Middle Way) "
     "has no public-domain English translation; Padmakara 2002 is copyright",
     "chandrakirti_madhyamakavatara", "east", 630),

    # ── INDIA: Kumara Bhatta (~7th c. CE) / Mimansa ───────────────────────────
    (fetch_unavailable,
     "no_pd_english: Kumarila Bhatta's Mimamsa-slokavartika has no public-domain "
     "English translation",
     "kumarila_bhatta_works", "east", 650),

    # ── INDIA: Prabhakara (~7th c. CE) ───────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Prabhakara's Brhati (Mimamsa commentary) has no "
     "public-domain English translation",
     "prabhakara_brhati", "east", 650),

    # ── INDIA: Dharmakirti (~7th c. CE) ──────────────────────────────────────
    # Pramanavarttika; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Dharmakirti's Pramanavarttika (Buddhist epistemology) "
     "has no public-domain English translation",
     "dharmakirti_pramanavarttika", "east", 650),

    # ── INDIA: Gaudapada (~7th c. CE) ────────────────────────────────────────
    # Mandukya Karika — Nikhilananda 1932 trans., PD
    # Gaudapada Mandukya Karika — Bhattacharya 1943. IA: agamasastraofsri00gaud
    # gaudapada_mandukya_karika: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier agamasastraofsri00gaud exists but contains only PDF/DjVu scans — no .txt file in metadata; Bhattacharya 1943 trans. not available as plain text",
     "gaudapada_mandukya_karika", "east", 650),

    # ── INDIA: Udyotakara (~6th-7th c. CE) ───────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Udyotakara's Nyayavarttika has no public-domain English "
     "translation",
     "udyotakara_nyayavarttika", "east", 620),

    # ── INDIA: Shantideva (~7th-8th c. CE) ───────────────────────────────────
    (fetch_internet_archive, "Bodhisattva way life Shantideva",
     "shantideva_bodhicaryavatara", "east", 700),

    # ── JAPAN: Kukai (~774-835 CE) ────────────────────────────────────────────
    (fetch_internet_archive, "Japanese Buddhism Eliot",
     "kukai_eliot_japanese_buddhism", "east", 805),

    # ── INDIA: Adi Shankara (~788-820 CE) ─────────────────────────────────────
    (fetch_internet_archive, "Crest Jewel Wisdom Shankara Johnston",
     "shankara_vivekachudamani", "east", 788),

    # ── TIBET: Padmasambhava (~8th c. CE) ─────────────────────────────────────
    (fetch_internet_archive, "Tibetan Book Dead Evans-Wentz",
     "tibetan_book_of_dead", "east", 780),

    # ── INDIA: Anandavardhana (~820-890 CE) ──────────────────────────────────
    # Dhvanyaloka (philosophy of aesthetics / poetry); no PD English translation
    (fetch_unavailable,
     "no_pd_english: Anandavardhana's Dhvanyaloka (theory of poetic suggestion) "
     "has no public-domain English translation; Ingalls 1990 is copyright",
     "anandavardhana_dhvanyaloka", "east", 850),

    # ── INDIA: Vasugupta (~860-925 CE) ────────────────────────────────────────
    # Shiva Sutras — Singh 1979 trans. is copyright; older translations PD
    # Vasugupta Shiva Sutras — Singh 1963 PD trans. IA: shivasutrastheyog00sing
    # vasugupta_shiva_sutras: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier shivasutrastheyog00sing exists but contains only PDF/DjVu scans — no .txt file in metadata; Singh 1963 trans. not available as plain text",
     "vasugupta_shiva_sutras", "east", 890),

    # ── INDIA: Vacaspati Misra (~9th c. CE) ───────────────────────────────────
    # Tattvabindu; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Vacaspati Misra's Tattvabindu and Nyayasucinibandha "
     "have no public-domain English translation",
     "vacaspati_misra_works", "east", 870),

    # ── INDIA: Jayanta Bhatta (~9th c. CE) ────────────────────────────────────
    # Nyayamanjari; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Jayanta Bhatta's Nyayamanjari has no public-domain "
     "English translation",
     "jayanta_bhatta_nyayamanjari", "east", 880),

    # ── KOREA: Doseon (~827-898 CE) ───────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Doseon's geomantic texts have no public-domain English "
     "translation",
     "doseon_works", "east", 860),

    # ── CHINA: Sengzhao (~384-414 CE) ─────────────────────────────────────────
    # Zhao lun — Liebenthal 1948 trans.; IA identifier: chaolung00lien
    # sengzhao_zhao_lun: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier chaolung00lien exists but contains only PDF/DjVu scans — no .txt file in metadata; Liebenthal 1948 Chao Lun not available as plain text",
     "sengzhao_zhao_lun", "east", 400),

    # ── CHINA: Ge Hong (~4th c. CE) ──────────────────────────────────────────
    # Baopuzi inner chapters — Ware 1966 is copyright; use Fung Yu-lan secondary
    # ge_hong_baopuzi: restricted_ia — see rationale MD
    (fetch_unavailable,
     "restricted_ia: IA identifier historyofchinese0001fung returns HTTP 401 — access restricted; Fung Yu-lan History of Chinese Philosophy Vol.1 not publicly accessible",
     "ge_hong_baopuzi", "east", 320),

    # ── CHINA: Tan-luan (~476-542 CE) ─────────────────────────────────────────
    # Commentary on Vasubandhu's Pure Land; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Tan-luan's Wangsheng Lunzhu (Commentary on the Treatise "
     "on Rebirth) has no public-domain English translation",
     "tan_luan_pure_land", "east", 510),

    # ── CHINA: Zhi Dun (~314-366 CE) ─────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Zhi Dun's Buddhist-Taoist synthesis writings have no "
     "public-domain English translation",
     "zhi_dun_works", "east", 340),

    # ── CHINA: Lushan Huiyuan (~334-416 CE) ──────────────────────────────────
    # Pure Land Buddhism founder; IA copies are access-restricted
    (fetch_unavailable,
     "restricted_ia: Accessible IA copies of Lushan Huiyuan's Pure Land texts "
     "return 401/403; Tanaka 1990 trans. is copyright",
     "lushan_huiyuan_pure_land", "east", 380),

    # ── CHINA: Dazu Huike (~487-593 CE) ──────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Dazu Huike's Chan teachings survive only in transmission "
     "records; no public-domain English translation",
     "dazu_huike_works", "east", 540),

    # ── CHINA: Nanyue Huisi (~515-577 CE) ─────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Nanyue Huisi's works have no public-domain English translation",
     "nanyue_huisi_works", "east", 545),

    # ── CHINA: Shenhui (~684-758 CE) ─────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Shenhui's Platform Talks (Heze Shenhui chanshi yulu) "
     "have no public-domain English translation",
     "shenhui_platform_talks", "east", 720),

    # ── CHINA: Shitou Xiqian (~700-790 CE) ────────────────────────────────────
    # Cantong Qi (Song of the Precious Mirror Samadhi); Cleary is copyright
    (fetch_unavailable,
     "no_pd_english: Shitou Xiqian's Cantong Qi has no public-domain "
     "English translation; Cleary trans. is copyright",
     "shitou_xiqian_cantong", "east", 745),

    # ── CHINA: Mazu Daoyi (~709-788 CE) ──────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Mazu Daoyi's recorded sayings (yulu) have no public-domain "
     "English translation",
     "mazu_daoyi_yulu", "east", 748),

    # ── CHINA: Baizhang Huaihai (~720-814 CE) ────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Baizhang Huaihai's Pure Rules and recorded sayings "
     "have no public-domain English translation",
     "baizhang_huaihai_works", "east", 767),

    # ── CHINA: Li Ao (~722-841 CE) ────────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Li Ao's Fuxing Shu (Essay on Restoring the Nature) "
     "has no public-domain English translation",
     "li_ao_fuxing_shu", "east", 780),

    # ── CHINA: Qingliang Chengguan (~738-839 CE) ─────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Qingliang Chengguan's Huayan commentaries have no "
     "public-domain English translation",
     "chengguan_huayan", "east", 790),

    # ── CHINA: Han Yu (~768-824 CE) ───────────────────────────────────────────
    # Selected essays; Hartman 1986 is copyright; use de Bary Sources anthology (PD)
    # IA identifier: sourcesofchinesetradition1 contains Han Yu's Yuan Dao
    # han_yu_essays: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier sourcesofchinese00debauoft exists but contains only PDF/DjVu scans — no .txt file in metadata; de Bary Sources of Chinese Tradition Vol.1 not available as plain text",
     "han_yu_essays", "east", 800),

    # ── WEST: Pre-Socratics (~600 BCE) ───────────────────────────────────────
    (fetch_gutenberg_search, "Early Greek Philosophy Burnet",
     "pre_socratics_burnet", "west", -600),
    (fetch_internet_archive, "Fairbanks handbook Greek philosophy",
     "pre_socratics_fairbanks", "west", -600),

    # ── WEST: Persia / Avesta (~1200 BCE) ─────────────────────────────────────
    (fetch_internet_archive, "Zend-Avesta Darmesteter Vendidad",
     "avesta_darmesteter_vol4", "west", -1200),
    (fetch_internet_archive, "Avesta Mills Zend",
     "avesta_mills", "west", -1200),

    # ── WEST: Plato (~427-347 BCE) ────────────────────────────────────────────
    (fetch_gutenberg_id, 1497, "plato_republic_jowett",    "west", -427),
    (fetch_gutenberg_id, 1658, "plato_phaedo_jowett",      "west", -427),
    (fetch_gutenberg_id, 1600, "plato_symposium_jowett",   "west", -427),
    (fetch_gutenberg_id, 1656, "plato_apology_jowett",     "west", -427),
    (fetch_gutenberg_id, 1672, "plato_gorgias_jowett",     "west", -427),
    (fetch_gutenberg_id, 1735, "plato_theaetetus_jowett",  "west", -427),
    (fetch_gutenberg_id, 1572, "plato_timaeus_jowett",     "west", -427),
    # Additional Plato dialogues
    (fetch_gutenberg_id, 1750, "plato_meno_jowett",        "west", -427),
    (fetch_gutenberg_id, 1726, "plato_protagoras_jowett",  "west", -427),

    # ── WEST: Aristotle (~384-322 BCE) ────────────────────────────────────────
    (fetch_gutenberg_id, 8438,  "aristotle_nicomachean_ethics", "west", -384),
    (fetch_internet_archive, "Metaphysica Aristotle",
     "aristotle_metaphysics", "west", -384),
    (fetch_gutenberg_id, 6762,  "aristotle_politics",           "west", -384),
    (fetch_internet_archive, "Organon Aristotle",
     "aristotle_physics", "west", -384),
    (fetch_internet_archive, "De Anima Aristotle",
     "aristotle_de_anima", "west", -384),

    # ── WEST: Epicurus (~341-270 BCE) ─────────────────────────────────────────
    (fetch_gutenberg_id, 51, "epicurus_diogenes_laertius", "west", -270),

    # ── WEST: Zeno of Citium (~333-264 BCE) ───────────────────────────────────
    # Stoic founder; no works survive; known through Diogenes Laertius Book VII
    # PG #51 covers Zeno in the same volume as Epicurus
    (fetch_unavailable,
     "lost_work: Zeno of Citium's own writings are completely lost; his Stoic "
     "philosophy is reported in Diogenes Laertius Book VII, covered by "
     "epicurus_diogenes_laertius (PG #51 = full Lives of Eminent Philosophers)",
     "zeno_citium_stoic", "west", -333),

    # ── WEST: Lucretius (~99-55 BCE) ──────────────────────────────────────────
    # De Rerum Natura — Munro trans., PG #785
    (fetch_gutenberg_id, 785, "lucretius_de_rerum_natura", "west", -60),

    # ── WEST: Cicero (~106-43 BCE) ────────────────────────────────────────────
    (fetch_gutenberg_id, 14988, "cicero_nature_of_gods", "west", -55),

    # ── WEST: Philo of Alexandria (~20 BCE - 50 CE) ───────────────────────────
    # Works of Philo — Yonge trans. (1854), PD
    (fetch_internet_archive, "Philo Alexandria works Yonge",
     "philo_alexandria_works", "west", 40),

    # ── WEST: Seneca (~4 BCE - 65 CE) ────────────────────────────────────────
    (fetch_gutenberg_search, "Seneca",
     "seneca_letters_lucilius", "west", 65),

    # ── WEST: Epictetus (~55-135 CE) ─────────────────────────────────────────
    (fetch_gutenberg_search, "Epictetus",
     "epictetus_enchiridion", "west", 100),
    (fetch_internet_archive, "Discourses Epictetus",
     "epictetus_discourses", "west", 108),

    # ── WEST: Marcus Aurelius (~121-180 CE) ───────────────────────────────────
    (fetch_gutenberg_id, 2680, "marcus_aurelius_meditations", "west", 170),

    # ── WEST: Plotinus (~205-270 CE) ─────────────────────────────────────────
    (fetch_internet_archive, "Plotinus Enneads MacKenna",
     "plotinus_enneads_mackenna", "west", 260),

    # ── WEST: Porphyry (~232-304 CE) ─────────────────────────────────────────
    # Isagoge (Introduction to Aristotle's Categories) — Taylor trans. PD
    # IA identifier: isagogeoraristot00porp
    # porphyry_isagoge: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier isagogeoraristot00porp exists but contains only PDF/DjVu scans — no .txt file in metadata; Taylor trans. not available as plain text",
     "porphyry_isagoge", "west", 270),

    # ── WEST: Iamblichus (~245-325 CE) ────────────────────────────────────────
    # On the Pythagorean Way of Life — Clark 1989 is copyright; Taylor 1818 is PD
    (fetch_internet_archive, "Iamblichus Pythagorean life Taylor",
     "iamblichus_pythagorean_life", "west", 300),

    # ── WEST: Origen (~184-253 CE) ────────────────────────────────────────────
    (fetch_internet_archive, "Ante-Nicene Fathers Origen",
     "origen_de_principiis", "west", 230),

    # ── WEST: Hypatia (~360-415 CE) ───────────────────────────────────────────
    # Hypatia's own mathematical works are lost; known through Dzielska 1995 (copyright)
    (fetch_unavailable,
     "lost_work: Hypatia's own works (commentary on Diophantus, etc.) are lost; "
     "her philosophical contributions are known only through letters of Synesius "
     "of Cyrene; Dzielska 1995 biography is copyright",
     "hypatia_works", "west", 390),

    # ── WEST: Proclus (~412-485 CE) ───────────────────────────────────────────
    # Elements of Theology — Dodds 1963 is copyright; Taylor 1816 trans. PD
    (fetch_internet_archive, "Proclus elements theology Taylor",
     "proclus_elements_theology", "west", 450),

    # ── WEST: Augustine (~354-430 CE) ─────────────────────────────────────────
    (fetch_gutenberg_id, 3296, "augustine_confessions", "west", 397),
    (fetch_gutenberg_search, "Augustine City of God Dods",
     "augustine_city_of_god", "west", 420),

    # ── WEST: John Philoponus (~490-570 CE) ───────────────────────────────────
    # Against Proclus — Share 2005 is copyright; no PD English text confirmed on IA
    (fetch_unavailable,
     "no_pd_english: John Philoponus's philosophical works (Against Proclus, "
     "Against Aristotle) are available only in modern copyright translations "
     "(Share 2005, Wildberg 1987); no public-domain English text found",
     "john_philoponus_works", "west", 530),

    # ── WEST: Pseudo-Dionysius the Areopagite (~c. 500 CE) ────────────────────
    # Divine Names — Parker 1897 trans., PD
    (fetch_internet_archive, "Pseudo-Dionysius Areopagite divine names mystical theology",
     "pseudo_dionysius_divine_names", "west", 500),

    # ── WEST: Isidore of Seville (~560-636 CE) ────────────────────────────────
    # Etymologiae; no complete PD English translation
    (fetch_unavailable,
     "no_pd_english: Isidore of Seville's Etymologiae has no complete "
     "public-domain English translation; Barney et al. 2006 (Cambridge UP) "
     "is in copyright",
     "isidore_seville_etymologiae", "west", 600),

    # ── WEST: Eusebius (~260-339 CE) ─────────────────────────────────────────
    (fetch_internet_archive, "Ecclesiastical History Eusebius",
     "eusebius_church_history", "west", 313),

    # ── WEST: Jerome (~347-420 CE) ────────────────────────────────────────────
    (fetch_internet_archive, "Select Letters Jerome",
     "jerome_letters", "west", 400),

    # ── WEST: Boethius (~480-524 CE) ─────────────────────────────────────────
    (fetch_gutenberg_id, 14328, "boethius_consolation_philosophy", "west", 524),

    # ── WEST: Benedict of Nursia (~480-547 CE) ────────────────────────────────
    (fetch_internet_archive, "Rule Saint Benedict Gasquet",
     "benedict_rule", "west", 530),

    # ── WEST: John of Damascus (~680-750 CE) ─────────────────────────────────
    # Exposition of the Orthodox Faith — Nicene & Post-Nicene Fathers series
    # IA identifier: niceneandpostni09scha (Vol. 9 contains John of Damascus)
    # john_damascus_orthodox_faith: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier niceneandpostni09scha exists but contains only PDF/DjVu scans — no .txt file in metadata; Nicene & Post-Nicene Fathers Vol.9 not available as plain text",
     "john_damascus_orthodox_faith", "west", 730),

    # ── WEST: Alcuin (~735-804 CE) ────────────────────────────────────────────
    # On Dialectic (De Dialectica); no standalone PD English translation confirmed
    # Alcuin — no standalone PD English translation of De Dialectica
    (fetch_unavailable,
     "no_pd_english: Alcuin's De Dialectica and philosophical letters have no "
     "standalone public-domain English translation",
     "alcuin_works", "west", 780),

    # ── WEST: Al-Kindi (~801-873 CE) ─────────────────────────────────────────
    (fetch_internet_archive, "Al-Kindi first philosophy",
     "al_kindi_first_philosophy", "west", 850),

    # ── WEST: John Scotus Eriugena (~815-877 CE) ──────────────────────────────
    (fetch_internet_archive, "Eriugena Periphyseon division nature",
     "eriugena_periphyseon", "west", 866),

    # ── WEST: Al-Farabi (~870-950 CE) ─────────────────────────────────────────
    (fetch_internet_archive, "Al-Farabi virtuous city",
     "al_farabi_virtuous_city", "west", 940),

    # ── WEST: Al-Razi (~865-925 CE) ───────────────────────────────────────────
    # Spiritual Medicine — Arberry 1950 is copyright; older partial translations PD
    # Al-Razi — Browne Arabian Medicine 1921 (PD) covers Al-Razi's philosophy
    # IA: arabianmedicine00brow
    # al_razi_spiritual_medicine: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier arabianmedicine00brow exists but contains only PDF/DjVu scans — no .txt file in metadata; Browne 1921 Arabian Medicine not available as plain text",
     "al_razi_spiritual_medicine", "west", 900),

    # ── WEST: Saadia Gaon (~882-942 CE) ──────────────────────────────────────
    # Book of Beliefs and Opinions — Rosenblatt 1948 is copyright; PD PG version exists
    # Saadia Gaon — Cohen 1880 PD partial trans. IA: bookofbeliefsopin00saad
    # saadia_gaon_emunot: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier bookofbeliefsopin00saad exists but contains only PDF/DjVu scans — no .txt file in metadata; no plain-text PD English translation found",
     "saadia_gaon_emunot", "west", 933),

    # ── WEST: Avicenna (~980-1037 CE) ─────────────────────────────────────────
    (fetch_internet_archive, "Avicenna Canon Medicine philosophy",
     "avicenna_book_of_healing", "west", 1020),

    # ── WEST: Al-Biruni (~973-1050 CE) ────────────────────────────────────────
    # Kitab al-Hind (India) — Sachau 1887/1910 trans., PD
    (fetch_internet_archive, "Al-Biruni Alberuni India Sachau",
     "al_biruni_india", "west", 1030),

    # ── WEST: Anselm (~1034-1109 CE) ──────────────────────────────────────────
    (fetch_internet_archive, "Anselm Proslogion Cur Deus Homo",
     "anselm_proslogion_cur_deus", "west", 1090),

    # ── WEST: Ibn Hazm (~994-1064 CE) ────────────────────────────────────────
    # The Ring of the Dove (Tawq al-Hamama) — Arberry 1953 is copyright; Nykl 1931 PD
    # Ibn Hazm Necklace of the Pigeon — Nykl 1931. IA: necklaceofpigeonbeingr00ibnh
    # ibn_hazm_ring_dove: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier necklaceofpigeonbeingr00ibnh exists but contains only PDF/DjVu scans — no .txt file in metadata; Nykl 1931 Necklace of the Pigeon not available as plain text",
     "ibn_hazm_ring_dove", "west", 1022),

    # ── WEST: Ibn Gabirol (Avicebron) (~1021-1058 CE) ─────────────────────────
    # Fons Vitae (Source of Life) — Myer 1888 trans., PD
    # Ibn Gabirol Fons Vitae — Myer 1888. IA: avicebron00ibng
    # ibn_gabirol_fons_vitae: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier avicebron00ibng exists but contains only PDF/DjVu scans — no .txt file in metadata; Myer 1888 Fons Vitae not available as plain text",
     "ibn_gabirol_fons_vitae", "west", 1050),

    # ── WEST: Omar Khayyam (~1048-1131 CE) ────────────────────────────────────
    # Rubaiyat — FitzGerald trans. (1859), PG #246
    (fetch_gutenberg_id, 246, "omar_khayyam_rubaiyat_fitzgerald", "west", 1100),

    # ── WEST: Al-Ghazali (~1058-1111 CE) ─────────────────────────────────────
    (fetch_internet_archive, "Al-Ghazali Tahafut incoherence philosophers",
     "al_ghazali_incoherence", "west", 1095),
    # Also fetch Deliverance from Error (Munqidh) — shorter PD text
    # Al-Ghazali Deliverance from Error — Field 1909 PD trans. IA: confessionsofanal00ghaz
    # al_ghazali_deliverance_error: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier confessionsofanal00ghaz exists but contains only PDF/DjVu scans — no .txt file in metadata; Field 1909 Deliverance from Error not available as plain text",
     "al_ghazali_deliverance_error", "west", 1108),

    # ── WEST: Yehudah Halevi (~1075-1141 CE) ─────────────────────────────────
    # Kuzari — Hirschfeld 1905 trans., PD
    # Yehudah Halevi Kuzari — Hirschfeld 1905. IA: kuzariargumentfordivin00haleuoft
    # halevi_kuzari: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier kuzariargumentfordivin00haleuoft exists but contains only PDF/DjVu scans — no .txt file in metadata; Hirschfeld 1905 Kuzari not available as plain text",
     "halevi_kuzari", "west", 1130),

    # ── WEST: Peter Abelard (~1079-1142 CE) ──────────────────────────────────
    # Sic et Non — no complete PD English translation
    # Peter Abelard Sic et Non — Boyer & McKeon 1977 copyright; no PD English
    (fetch_unavailable,
     "no_pd_english: Peter Abelard's Sic et Non has no public-domain English "
     "translation; Boyer & McKeon 1977 is copyright",
     "abelard_sic_et_non", "west", 1120),

    # ── WEST: Peter Lombard (~1100-1160 CE) ──────────────────────────────────
    # Four Books of Sentences; no complete PD English translation
    (fetch_unavailable,
     "no_pd_english: Peter Lombard's Sententiarum Libri IV has no complete "
     "public-domain English translation; Silano 2007-2010 trans. is copyright",
     "peter_lombard_sentences", "west", 1150),

    # ── WEST: Ibn Tufayl (~1105-1185 CE) ─────────────────────────────────────
    (fetch_internet_archive, "Hayy ibn Yaqzan Ockley",
     "ibn_tufayl_hayy", "west", 1160),

    # ── WEST: Averroes (~1126-1198 CE) ────────────────────────────────────────
    (fetch_internet_archive, "Averroes Tahafut incoherence",
     "averroes_tahafut", "west", 1180),

    # ── WEST: Maimonides (~1135-1204 CE) ─────────────────────────────────────
    (fetch_internet_archive, "Guide for the Perplexed Maimonides Friedlander",
     "maimonides_guide_perplexed", "west", 1190),

    # ── WEST: Fakhr al-Din al-Razi (~1149-1209 CE) ────────────────────────────
    # Mafatih al-Ghayb; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Fakhr al-Din al-Razi's Mafatih al-Ghayb (Keys of the Unseen) "
     "and Muhassal have no public-domain English translation",
     "fakhr_al_din_al_razi_works", "west", 1185),

    # ── WEST: Suhrawardi (~1154-1191 CE) ─────────────────────────────────────
    # Philosophy of Illumination — Walbridge & Ziai 1999 is copyright; older partial PD
    # Suhrawardi — Corbin History of Islamic Philosophy 1964 PD. IA: historyofislamicph00corb
    # suhrawardi_philosophy_illumination: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier historyofislamicph00corb exists but contains only PDF/DjVu scans — no .txt file in metadata; Corbin History of Islamic Philosophy not available as plain text",
     "suhrawardi_philosophy_illumination", "west", 1186),

    # ── WEST: Ibn Arabi (~1165-1240 CE) ──────────────────────────────────────
    (fetch_internet_archive, "Tarjuman Ibn Arabi Nicholson",
     "ibn_arabi_tarjuman", "west", 1200),

    # ── WEST: Robert Grosseteste (~1175-1253 CE) ─────────────────────────────
    # On Light (De Luce) — Riedl 1942 trans. is PD
    # Robert Grosseteste On Light — Riedl 1942 PD. IA: onlight00gros
    # grosseteste_de_luce: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier onlight00gros exists but contains only PDF/DjVu scans — no .txt file in metadata; Riedl 1942 On Light not available as plain text",
     "grosseteste_de_luce", "west", 1235),

    # ── WEST: Francis of Assisi (~1182-1226 CE) ──────────────────────────────
    # Little Flowers of St. Francis — PG #655
    (fetch_gutenberg_id, 655, "francis_assisi_little_flowers", "west", 1220),

    # ── WEST: Albert the Great (~1193-1280 CE) ────────────────────────────────
    # No complete PD English translation of primary works
    (fetch_unavailable,
     "no_pd_english: Albertus Magnus's primary philosophical works have no "
     "complete public-domain English translation; Weisheipl 1980 is copyright",
     "albertus_magnus_works", "west", 1250),

    # ── WEST: Roger Bacon (~1214-1294 CE) ─────────────────────────────────────
    # Opus Majus — Burke 1928 trans., PD on IA
    (fetch_internet_archive, "Roger Bacon Opus Majus Burke",
     "roger_bacon_opus_majus", "west", 1267),

    # ── WEST: Thomas Aquinas (~1221-1274 CE) ─────────────────────────────────
    (fetch_internet_archive, "Summa Theologica Aquinas",
     "aquinas_summa_theologica", "west", 1270),

    # ── WEST: Bonaventure (~1225-1274 CE) ─────────────────────────────────────
    # The Soul's Journey into God (Itinerarium) — Boehner 1956 is copyright; de Vinck PD
    # Bonaventure Itinerarium — older Rober 1904 PD trans. IA: itinerariumofmind00bona
    # bonaventure_soul_journey: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier itinerariumofmind00bona exists but contains only PDF/DjVu scans — no .txt file in metadata; no plain-text PD English translation found",
     "bonaventure_soul_journey", "west", 1259),

    # ── WEST: Ramon Llull (~1232-1315 CE) ────────────────────────────────────
    # Ars Magna; no complete PD English translation
    # Ramon Llull — Peers 1929 Selected Works PD. IA: ramonlullhislife00peer
    # ramon_llull_ars_magna: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier ramonlullhislife00peer exists but contains only PDF/DjVu scans — no .txt file in metadata; Peers 1929 Ramon Llull not available as plain text",
     "ramon_llull_ars_magna", "west", 1305),

    # ── WEST: Meister Eckhart (~1260-1328 CE) ─────────────────────────────────
    (fetch_internet_archive, "Meister Eckhart sermons Evans",
     "meister_eckhart_sermons", "west", 1310),

    # ── WEST: Ibn Taymiyya (~1263-1328 CE) ────────────────────────────────────
    # Treatises; partial PD translations available
    # Ibn Taymiyya — Macdonald Development of Muslim Theology 1903 PD. IA: developmentofmusl00macd
    # ibn_taymiyya_works: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier developmentofmusl00macd exists but contains only PDF/DjVu scans — no .txt file in metadata; Macdonald 1903 Development of Muslim Theology not available as plain text",
     "ibn_taymiyya_works", "west", 1300),

    # ── WEST: Dante (~1265-1321 CE) ───────────────────────────────────────────
    (fetch_gutenberg_id, 8800, "dante_divine_comedy_cary", "west", 1320),

    # ── WEST: Duns Scotus (~1266-1308 CE) ─────────────────────────────────────
    # Ordinatio; no complete PD English translation
    (fetch_unavailable,
     "no_pd_english: Duns Scotus's Ordinatio and Opus Oxoniense have no "
     "complete public-domain English translation; Wolter 1954 trans. is copyright",
     "duns_scotus_ordinatio", "west", 1290),

    # ── WEST: Marsilius of Padua (~1270-1342 CE) ─────────────────────────────
    # Defensor Pacis — Previte-Orton 1928 trans., PD
    (fetch_internet_archive, "Marsilius Padua Defensor Pacis",
     "marsilius_defensor_pacis", "west", 1324),

    # ── WEST: William of Ockham (~1288-1348 CE) ───────────────────────────────
    (fetch_internet_archive, "Ockham Summa Logicae logic",
     "ockham_summa_logicae", "west", 1323),

    # ── WEST: Jean Buridan (~1300-1358 CE) ────────────────────────────────────
    # Summulae de Dialectica; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Jean Buridan's Summulae de Dialectica has no "
     "public-domain English translation; Zupko 2001 trans. is copyright",
     "buridan_summulae", "west", 1340),

    # ── WEST: John Wycliffe (~1320-1384 CE) ───────────────────────────────────
    # On the Truth of Holy Scripture and On Dominion — partial PD English
    # John Wycliffe Select English Works — Arnold 1871 PD. IA: selectenglishwor01wycl
    (fetch_ia_identifier, "selectenglishwor01wycl",
     "wycliffe_on_truth", "west", 1378),

    # ── WEST: Nicole Oresme (~1320-1382 CE) ──────────────────────────────────
    # De Moneta (On Money) — Johnson 1956 trans. PD
    # Nicole Oresme De Moneta — Johnson 1956 PD. IA: demoneta00ores
    # oresme_de_moneta: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier demoneta00ores exists but contains only PDF/DjVu scans — no .txt file in metadata; Johnson 1956 De Moneta not available as plain text",
     "oresme_de_moneta", "west", 1360),

    # ── WEST: Ibn Khaldun (~1332-1406 CE) ─────────────────────────────────────
    # Muqaddimah — de Slane 1863 trans., PD
    # Ibn Khaldun Muqaddimah — Rosenthal 1958 intro vol. IA: muqaddimahanintro01khaliala
    # ibn_khaldun_muqaddimah: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier muqaddimahanintro01khaliala exists but contains only PDF/DjVu scans — no .txt file in metadata; Rosenthal 1958 Muqaddimah intro not available as plain text",
     "ibn_khaldun_muqaddimah", "west", 1377),

    # ── WEST: Hasdai Crescas (~1340-1411 CE) ─────────────────────────────────
    # Or Adonai (Light of the Lord); Wolfson 1929 trans. PD
    # Hasdai Crescas — Wolfson 1929 Critique of Aristotle PD. IA: crescascritique00wolf
    # crescas_or_adonai: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier crescascritique00wolf exists but contains only PDF/DjVu scans — no .txt file in metadata; Wolfson 1929 Crescas' Critique of Aristotle not available as plain text",
     "crescas_or_adonai", "west", 1410),

    # ── WEST: Gemistus Pletho (~1355-1452 CE) ─────────────────────────────────
    # On the Differences Between Aristotle and Plato; no complete PD English trans.
    (fetch_unavailable,
     "no_pd_english: Gemistus Pletho's De Differentiis has no public-domain "
     "English translation; Woodhouse 1986 is copyright",
     "pletho_de_differentiis", "west", 1440),

    # ── WEST: Julian of Norwich (~1342-1416 CE) ───────────────────────────────
    (fetch_gutenberg_search, "Julian Norwich Revelations Divine Love",
     "julian_norwich_revelations", "west", 1395),

    # ── WEST: Thomas à Kempis (~1380-1471 CE) ─────────────────────────────────
    (fetch_gutenberg_id, 1653, "thomas_kempis_imitation_christ", "west", 1418),

    # ── WEST: Nicholas of Cusa (~1401-1464 CE) ────────────────────────────────
    (fetch_internet_archive, "Nicholas Cusa learned ignorance",
     "nicholas_cusa_learned_ignorance", "west", 1440),

    # ── WEST: Lorenzo Valla (~1407-1457 CE) ──────────────────────────────────
    # On the Donation of Constantine; Coleman 1922 trans. PD
    (fetch_internet_archive, "Lorenzo Valla Donation Constantine humanist",
     "valla_donation_constantine", "west", 1440),

    # ── WEST: Marsilio Ficino (~1433-1499 CE) ─────────────────────────────────
    # Theologia Platonica; Allen 2001 is copyright; older partial translations PD
    (fetch_internet_archive, "Marsilio Ficino Platonic theology Renaissance",
     "ficino_platonic_theology", "west", 1482),

    # ── WEST: Pico della Mirandola (~1463-1494 CE) ────────────────────────────
    # Oration on the Dignity of Man — PG no ID; Forbes 1907 trans. PD
    (fetch_internet_archive, "Pico Mirandola Oration Dignity Man",
     "pico_mirandola_oration", "west", 1486),

    # ── WEST: Erasmus (~1466-1536 CE) ─────────────────────────────────────────
    (fetch_gutenberg_id, 9371, "erasmus_praise_of_folly", "west", 1509),

    # ── WEST: Machiavelli (~1469-1527 CE) ─────────────────────────────────────
    (fetch_gutenberg_id, 1232, "machiavelli_prince", "west", 1513),

    # ── WEST: Copernicus (~1473-1543 CE) ─────────────────────────────────────
    # De Revolutionibus — Dobson/Brodetsky 1947 trans. PD
    (fetch_internet_archive, "Copernicus De Revolutionibus orbium coelestium",
     "copernicus_de_revolutionibus", "west", 1543),

    # ── WEST: Thomas More (~1478-1535 CE) ─────────────────────────────────────
    (fetch_gutenberg_id, 2130, "more_utopia", "west", 1516),

    # ── WEST: Martin Luther (~1483-1546 CE) ──────────────────────────────────
    # Ninety-Five Theses + Treatise on Christian Liberty — PG trans. PD
    (fetch_gutenberg_id, 274, "luther_works_selected", "west", 1520),

    # ── WEST: John Calvin (~1509-1564 CE) ─────────────────────────────────────
    # Institutes of the Christian Religion — Beveridge trans. PD
    (fetch_internet_archive, "Calvin Institutes Christian Religion Beveridge",
     "calvin_institutes", "west", 1559),

    # ── WEST: Montaigne (~1533-1592 CE) ───────────────────────────────────────
    (fetch_gutenberg_search, "Montaigne",
     "montaigne_essays", "west", 1580),

    # ── WEST: Giordano Bruno (~1548-1600 CE) ─────────────────────────────────
    # On the Infinite Universe and Worlds — Singer 1950 PD
    # Giordano Bruno On the Infinite Universe — Singer 1950 PD. IA: ontheinfiniteuni00brun
    # bruno_infinite_universe: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier ontheinfiniteuni00brun exists but contains only PDF/DjVu scans — no .txt file in metadata; Singer 1950 On the Infinite Universe not available as plain text",
     "bruno_infinite_universe", "west", 1584),

    # ── WEST: Francisco Suarez (~1548-1617 CE) ────────────────────────────────
    # Metaphysical Disputations; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Francisco Suarez's Metaphysicae Disputationes has no "
     "complete public-domain English translation",
     "suarez_metaphysical_disputations", "west", 1597),

    # ── WEST: Francis Bacon (~1561-1626 CE) ───────────────────────────────────
    (fetch_gutenberg_search, "Novum Organum Bacon",
     "bacon_novum_organum", "west", 1620),

    # ── WEST: Galileo (~1564-1642 CE) ─────────────────────────────────────────
    # Dialogue Concerning Two Chief World Systems — Drake 1953 is copyright; older PD
    # Galileo Dialogue — Salusbury 1661 rpt. IA: systemofworldint00gali
    # Drake 1953/67 is copyright; all modern IA copies restricted
    # galileo_dialogue: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier systemofworldint00gali exists but contains only PDF/DjVu scans — no .txt file in metadata; Salusbury 1661 trans. not available as plain text; Drake 1953 is copyright",
     "galileo_dialogue", "west", 1632),

    # ── WEST: Kepler (~1571-1630 CE) ─────────────────────────────────────────
    # Harmonices Mundi; no complete PD English translation
    (fetch_unavailable,
     "no_pd_english: Kepler's Harmonices Mundi has no complete public-domain "
     "English translation; Aiton et al. 1997 is copyright",
     "kepler_harmonices_mundi", "west", 1619),

    # ── WEST: Molla-Sadra (~1572-1640 CE) ────────────────────────────────────
    # Asfar; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Molla-Sadra's al-Asfar al-Arba'a (Four Journeys) "
     "has no public-domain English translation",
     "molla_sadra_asfar", "west", 1612),

    # ── WEST: Hugo Grotius (~1583-1645 CE) ────────────────────────────────────
    # On the Law of War and Peace — Whewell 1853 trans., PD
    (fetch_internet_archive, "Hugo Grotius law war peace Whewell natural law",
     "grotius_law_war_peace", "west", 1625),

    # ── WEST: Descartes (~1596-1650 CE) ──────────────────────────────────────
    (fetch_gutenberg_id, 59, "descartes_discourse_method", "west", 1637),

    # ── WEST: Thomas Hobbes (~1588-1679 CE) ───────────────────────────────────
    (fetch_gutenberg_id, 3207, "hobbes_leviathan", "west", 1651),

    # ── WEST: Blaise Pascal (~1623-1662 CE) ──────────────────────────────────
    (fetch_gutenberg_search, "Pascal",
     "pascal_pensees", "west", 1670),

    # ── WEST: Margaret Cavendish (~1623-1673 CE) ─────────────────────────────
    # Observations upon Experimental Philosophy — 1666, PD
    (fetch_internet_archive, "Margaret Cavendish observations experimental philosophy",
     "cavendish_observations", "west", 1666),

    # ── WEST: Baruch Spinoza (~1632-1677 CE) ─────────────────────────────────
    (fetch_gutenberg_id, 3800, "spinoza_ethics", "west", 1677),

    # ── WEST: John Locke (~1632-1704 CE) ─────────────────────────────────────
    (fetch_gutenberg_id, 10615, "locke_essay_human_understanding", "west", 1689),

    # ── WEST: Gottfried Leibniz (~1646-1716 CE) ───────────────────────────────
    (fetch_internet_archive, "Leibniz philosophical writings Monadology",
     "leibniz_monadology", "west", 1714),

    # ── WEST: George Berkeley (~1685-1753 CE) ─────────────────────────────────
    (fetch_gutenberg_id, 4723, "berkeley_principles_human_knowledge", "west", 1710),

    # ── WEST: David Hume (~1711-1776 CE) ─────────────────────────────────────
    (fetch_gutenberg_id, 4705, "hume_treatise_human_nature", "west", 1739),
    (fetch_gutenberg_id, 9662, "hume_enquiry_human_understanding", "west", 1748),

    # ── WEST: Jean-Jacques Rousseau (~1712-1778 CE) ───────────────────────────
    (fetch_gutenberg_search, "Rousseau Social Contract",
     "rousseau_social_contract", "west", 1762),

    # ── WEST: Voltaire (~1694-1778 CE) ────────────────────────────────────────
    # Candide — PG #19942 (PD trans.)
    (fetch_gutenberg_id, 19942, "voltaire_candide", "west", 1759),

    # ── WEST: Adam Smith (~1723-1790 CE) ─────────────────────────────────────
    (fetch_gutenberg_search, "Adam Smith Theory Moral Sentiments",
     "adam_smith_moral_sentiments", "west", 1759),

    # ── WEST: Immanuel Kant (~1724-1804 CE) ───────────────────────────────────
    (fetch_gutenberg_id, 4280, "kant_critique_pure_reason", "west", 1781),

    # ── WEST: Mary Wollstonecraft (~1759-1797 CE) ────────────────────────────
    (fetch_gutenberg_id, 3420, "wollstonecraft_vindication", "west", 1792),

    # ── WEST: Edmund Burke (~1729-1797 CE) ────────────────────────────────────
    # Reflections on the Revolution in France — PG #2173
    (fetch_gutenberg_id, 2173, "burke_reflections_revolution", "west", 1790),

    # ── WEST: Thomas Paine (~1737-1809 CE) ────────────────────────────────────
    # Rights of Man + Age of Reason — PG #3742
    (fetch_gutenberg_id, 3742, "paine_rights_of_man", "west", 1791),

    # ── WEST: Jeremy Bentham (~1748-1832 CE) ─────────────────────────────────
    # Introduction to the Principles of Morals and Legislation — PG #781
    (fetch_gutenberg_id, 781, "bentham_principles_morals", "west", 1789),

    # ── WEST: G.W.F. Hegel (~1770-1831 CE) ────────────────────────────────────
    (fetch_internet_archive, "Hegel Phenomenology Spirit Miller",
     "hegel_phenomenology_spirit", "west", 1807),

    # ── WEST: Arthur Schopenhauer (~1788-1860 CE) ────────────────────────────
    (fetch_gutenberg_id, 38427, "schopenhauer_world_will_representation", "west", 1818),

    # ── WEST: Søren Kierkegaard (~1813-1855 CE) ───────────────────────────────
    (fetch_gutenberg_id, 60333, "kierkegaard_selections", "west", 1843),

    # ── WEST: Karl Marx (~1818-1883 CE) ───────────────────────────────────────
    (fetch_gutenberg_id, 61, "marx_communist_manifesto", "west", 1848),

    # ── WEST: John Stuart Mill (~1806-1873 CE) ────────────────────────────────
    (fetch_gutenberg_id, 11224, "mill_utilitarianism", "west", 1863),

    # ── WEST: Ralph Waldo Emerson (~1803-1882 CE) ────────────────────────────
    # Essays: First and Second Series — PG #2944 and PG #3541
    (fetch_gutenberg_id, 2944, "emerson_essays_first_series", "west", 1841),

    # ── WEST: Ludwig Feuerbach (~1804-1872 CE) ────────────────────────────────
    # The Essence of Christianity — Evans 1854 trans., PG #4955
    (fetch_gutenberg_id, 4955, "feuerbach_essence_christianity", "west", 1841),

    # ── WEST: Henry David Thoreau (~1817-1862 CE) ────────────────────────────
    # Walden — PG #205
    (fetch_gutenberg_id, 205, "thoreau_walden", "west", 1854),

    # ── WEST: Friedrich Nietzsche (~1844-1900 CE) ─────────────────────────────
    (fetch_gutenberg_id, 4363, "nietzsche_beyond_good_evil", "west", 1886),
    # Also Thus Spake Zarathustra — PG #1998
    (fetch_gutenberg_id, 1998, "nietzsche_zarathustra", "west", 1883),

    # ── WEST: William James (~1842-1910 CE) ───────────────────────────────────
    (fetch_gutenberg_search, "William James varieties religious experience",
     "james_varieties_religious_experience", "west", 1902),

    # ── CHINA: Zhaozhou Congshen (~778-897 CE) ────────────────────────────────
    # Recorded sayings; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Zhaozhou Congshen's recorded sayings have no public-domain "
     "English translation; Cleary trans. is copyright",
     "zhaozhou_congshen_works", "east", 835),

    # ── CHINA: Zongmi (~780-841 CE) ──────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Zongmi's Chan Prolegomenon and Inquiry into the Origin of "
     "Humanity have no public-domain English translation",
     "zongmi_works", "east", 810),

    # ── CHINA: Huangbo Xiyun (~d. 850 CE) ────────────────────────────────────
    # The Zen Teaching of Huang Po — Blofeld 1958 is copyright
    (fetch_unavailable,
     "copyright_trans: Huangbo Xiyun's Chun Zhou Lu is available only in "
     "John Blofeld's 1958 trans. (in copyright); no PD English translation exists",
     "huangbo_xiyun_works", "east", 830),

    # ── CHINA: Linji Yixuan (~d. 866 CE) ─────────────────────────────────────
    # Linji Lu (Record of Linji); no PD English translation
    (fetch_unavailable,
     "no_pd_english: Linji Yixuan's Record (Linji Lu) has no public-domain "
     "English translation",
     "linji_yixuan_record", "east", 850),

    # ── CHINA: Yunmen Wenyan (~864-949 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Yunmen Wenyan's recorded sayings have no public-domain "
     "English translation",
     "yunmen_wenyan_works", "east", 906),

    # ── CHINA: Xuedou Chongxian (~980-1052 CE) ────────────────────────────────
    # Blue Cliff Record verses; full text in Cleary 1977 (copyright)
    (fetch_unavailable,
     "copyright_trans: Xuedou's verses in the Blue Cliff Record are available "
     "only in Cleary & Cleary 1977 (copyright); no standalone PD English text",
     "xuedou_chongxian_works", "east", 1016),

    # ── CHINA: Fan Zhongyan (~989-1052 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Fan Zhongyan's political-philosophical essays have no "
     "public-domain English translation",
     "fan_zhongyan_works", "east", 1020),

    # ── CHINA: Hu Yuan (~993-1059 CE) ─────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Hu Yuan's Confucian revival writings have no public-domain "
     "English translation",
     "hu_yuan_works", "east", 1026),

    # ── CHINA: Shao Yung (~1011-1077 CE) ─────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Shao Yung's Huangji Jingshi (Supreme Principles) has no "
     "public-domain English translation",
     "shao_yung_works", "east", 1044),

    # ── CHINA: Zhou Dunyi (~1017-1073 CE) ────────────────────────────────────
    # Taijitu Shuo (Explanation of the Diagram of the Supreme Ultimate);
    # brief PD translations available within secondary sources
    # Zhou Dunyi Taijitu — de Bary Sources Vol 1. IA: sourcesofchinese00debauoft
    # zhou_dunyi_taijitu: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier sourcesofchinese00debauoft exists but contains only PDF/DjVu scans — no .txt file in metadata; de Bary Sources of Chinese Tradition Vol.1 not available as plain text",
     "zhou_dunyi_taijitu", "east", 1060),

    # ── CHINA: Chang Tsai (~1020-1077 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Zhang Zai's Zhengmeng (Correcting Youthful Ignorance) "
     "has no public-domain English translation",
     "zhang_zai_zhengmeng", "east", 1060),

    # ── CHINA: Cheng Hao (~1032-1085 CE) ─────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Cheng Hao's philosophical writings have no public-domain "
     "English translation",
     "cheng_hao_works", "east", 1058),

    # ── CHINA: Cheng Yi (~1033-1107 CE) ──────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Cheng Yi's philosophical writings have no public-domain "
     "English translation",
     "cheng_yi_works", "east", 1070),

    # ── CHINA: Yuanwu Keqin (~1063-1135 CE) ──────────────────────────────────
    # Blue Cliff Record (Biyanlu) — Cleary 1977 is copyright
    (fetch_unavailable,
     "copyright_trans: Yuanwu Keqin's Blue Cliff Record is available only in "
     "Cleary & Cleary 1977 (copyright); no standalone PD English trans.",
     "yuanwu_keqin_biyanlu", "east", 1100),

    # ── CHINA: Dahui Zonggao (~1089-1163 CE) ─────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Dahui Zonggao's letters and recorded sayings have no "
     "public-domain English translation",
     "dahui_zonggao_works", "east", 1126),

    # ── CHINA: Hu Hong (~1105-1161 CE) ────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Hu Hong's Zhiyan (Knowing Words) has no public-domain "
     "English translation",
     "hu_hong_works", "east", 1133),

    # ── CHINA: Zhu Xi (~1130-1200 CE) ─────────────────────────────────────────
    (fetch_internet_archive, "I Ching Legge",
     "i_ching_legge", "east", 1175),

    # ── CHINA: Lu Jiuyuan (~1139-1193 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Lu Jiuyuan's philosophical letters and essays have no "
     "public-domain English translation",
     "lu_jiuyuan_works", "east", 1166),

    # ── CHINA: Wumen Huikai (~1183-1260 CE) ──────────────────────────────────
    # Wumenguan (Gateless Gate) — Senzaki & Reps 1934 trans., PD on IA
    (fetch_internet_archive, "Wumen Huikai Gateless Gate koan Zen",
     "wumen_huikai_gateless_gate", "east", 1228),

    # ── KOREA: Jinul (~1158-1210 CE) ─────────────────────────────────────────
    (fetch_unavailable,
     "copyright_trans: Jinul's works available only in Buswell 1991 "
     "(copyright); no PD English translation found on IA or PG",
     "jinul_works", "east", 1185),

    # ── CHINA: Chen Xianzhang (~1428-1500 CE) ────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Chen Xianzhang's philosophical poetry and essays have no "
     "public-domain English translation",
     "chen_xianzhang_works", "east", 1464),

    # ── CHINA: Wang Yangming (~1472-1529 CE) ─────────────────────────────────
    (fetch_internet_archive, "Wang Yangming instructions",
     "wang_yangming_instructions", "east", 1518),

    # ── CHINA: Wang Gen (~1483-1541 CE) ──────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Wang Gen's works (Taizhou school) have no public-domain "
     "English translation",
     "wang_gen_works", "east", 1521),

    # ── CHINA: He Xinyin (~1517-1579 CE) ─────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: He Xinyin's writings have no public-domain English translation",
     "he_xinyin_works", "east", 1548),

    # ── CHINA: Li Zhi (~1527-1602 CE) ────────────────────────────────────────
    # A Book to Burn (Fenshu); de Bary anthology excerpts available
    # Li Zhi — de Bary Sources of Chinese Tradition Vol 2. IA: sourcesofchinese0002deba
    (fetch_ia_identifier, "sourcesofchinese0002deba",
     "li_zhi_fenshu", "east", 1590),

    # ── CHINA: Jiao Hong (~1540-1620 CE) ─────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Jiao Hong's works have no public-domain English translation",
     "jiao_hong_works", "east", 1580),

    # ── CHINA: Liu Tsung-chou (~1578-1645 CE) ────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Liu Tsung-chou's Renpu (Moral Cultivation Record) has no "
     "public-domain English translation",
     "liu_tsung_chou_works", "east", 1610),

    # ── INDIA: Ramanuja (~1017-1137 CE) ──────────────────────────────────────
    (fetch_internet_archive, "Ramanuja Vedarthasangraha",
     "ramanuja_vedarthasangraha", "east", 1100),

    # ── INDIA: Gorakshanath (~11th-12th c. CE) ────────────────────────────────
    # Goraksha Paddhati; Briggs 1938 trans. PD
    # Gorakshanath — Briggs 1938 Gorakhnath and Kanphata Yogis. IA: gorakhnathkanpha00brig
    # gorakshanath_works: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier gorakhnathkanpha00brig exists but contains only PDF/DjVu scans — no .txt file in metadata; Briggs 1938 Gorakhnath and Kanphata Yogis not available as plain text",
     "gorakshanath_works", "east", 1100),

    # ── INDIA: Basaveshwara (~1134-1196 CE) ───────────────────────────────────
    # Vachanas (sayings); PD translations available
    # Basaveshwara Vachanas — Ramanujan 1973 copyright; no PD English confirmed
    (fetch_unavailable,
     "copyright_trans: Basaveshwara's Vachanas available only in Ramanujan 1973 "
     "(copyright); no public-domain English translation confirmed on IA",
     "basaveshwara_vachanas", "east", 1168),

    # ── INDIA: Shri Madhvacharya (~1238-1317 CE) ──────────────────────────────
    # Brahma Sutra Bhashya (Dvaita commentary); Rao 1936 trans. PD
    (fetch_internet_archive, "Madhvacharya Dvaita Vedanta Brahma Sutra",
     "madhvacharya_brahma_sutra", "east", 1280),

    # ── INDIA: Gangesha Upadhyaya (~13th c. CE) ───────────────────────────────
    # Tattvacintamani (New Nyaya); no PD English translation
    (fetch_unavailable,
     "no_pd_english: Gangesha Upadhyaya's Tattvacintamani has no "
     "public-domain English translation",
     "gangesha_tattvacintamani", "east", 1250),

    # ── INDIA: Nimbarka (~13th c. CE) ─────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Nimbarka's Vedanta-parijata-saurabha has no "
     "public-domain English translation",
     "nimbarka_vedanta", "east", 1250),

    # ── INDIA: Madhava Vidyaranya (~1268-1386 CE) ─────────────────────────────
    # Pancadasi — Srinivasa Rao trans. PD
    # Vidyaranya Pancadasi — Srinivasa Rao 1920. IA: pancadasiofshrim00vidyrich
    # vidyaranya_pancadasi: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier pancadasiofshrim00vidyrich exists but contains only PDF/DjVu scans — no .txt file in metadata; Srinivasa Rao 1920 trans. not available as plain text",
     "vidyaranya_pancadasi", "east", 1350),

    # ── TIBET: Sakya Pandita (~1182-1251 CE) ─────────────────────────────────
    # Treasury of Aphoristic Jewels; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Sakya Pandita's Sakya Legshay (Treasury of Aphoristic Jewels) "
     "has no public-domain English translation",
     "sakya_pandita_works", "east", 1220),

    # ── TIBET: Rangjung Dorje (~1284-1339 CE) ────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Rangjung Dorje's Mahamudra Aspiration Prayer and other works "
     "have no public-domain English translation",
     "rangjung_dorje_works", "east", 1310),

    # ── TIBET: Dolpopa (~1292-1361 CE) ────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Dolpopa's Mountain Dharma (Ri Chos Nges Don Rgya Mtsho) "
     "has no public-domain English translation; Stearns 1999 is copyright",
     "dolpopa_mountain_dharma", "east", 1330),

    # ── TIBET: Longchenpa (~1308-1364 CE) ─────────────────────────────────────
    (fetch_internet_archive, "Guhyagarbha Tantra Longchenpa",
     "longchenpa_guhyagarbha", "east", 1340),

    # ── CHINA: Aston / Kenko placeholder (~1330 CE) ───────────────────────────
    (fetch_internet_archive, "History Japanese literature Aston",
     "kenko_essays_idleness", "east", 1330),

    # ── TIBET: Gyeltsap Darma Rinchen (~1364-1432 CE) ────────────────────────
    (fetch_unavailable,
     "no_pd_english: Gyeltsap Darma Rinchen's works have no public-domain "
     "English translation",
     "gyeltsap_darma_rinchen_works", "east", 1398),

    # ── TIBET: Je Tsongkhapa (~1357-1419 CE) ─────────────────────────────────
    (fetch_internet_archive, "Buddhism Tibet Waddell Lamaism",
     "waddell_buddhism_tibet", "east", 1390),

    # ── CHINA: Wumen Huikai (~1183-1260 CE) — already listed above

    # ── JAPAN: Shinran (~1173-1261 CE) ────────────────────────────────────────
    (fetch_internet_archive, "Buddhist Psalms Shinran 1921",
     "shinran_buddhist_psalms", "east", 1200),

    # ── JAPAN: Dogen (~1200-1253 CE) ─────────────────────────────────────────
    (fetch_internet_archive, "Dogen Soto Zen essays",
     "dogen_shobogenzo", "east", 1250),

    # ── JAPAN: Nichiren (~1222-1282 CE) ───────────────────────────────────────
    (fetch_internet_archive, "Nichiren Buddhist prophet Anesaki",
     "nichiren_writings", "east", 1270),

    # ── JAPAN: Zeami Motokiyo (~1363-1443 CE) ────────────────────────────────
    # On the Art of the No Drama — Rimer & Yamazaki 1984 is copyright
    (fetch_unavailable,
     "copyright_trans: Zeami Motokiyo's treatises on Noh drama are available "
     "only in Rimer & Yamazaki 1984 (copyright); no PD English translation",
     "zeami_noh_treatises", "east", 1400),

    # ── TIBET: Gorampa (~1429-1489 CE) ────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Gorampa Sonam Sengge's philosophical works have no "
     "public-domain English translation",
     "gorampa_works", "east", 1460),

    # ── TIBET: Sakya Chokden (~1428-1507 CE) ─────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Sakya Chokden's works have no public-domain English translation",
     "sakya_chokden_works", "east", 1467),

    # ── INDIA: Kabir (~1440-1518 CE) ─────────────────────────────────────────
    (fetch_internet_archive, "Kabir Tagore poems",
     "kabir_songs_tagore", "east", 1480),

    # ── INDIA: Vyasatirtha (~1460-1539 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Vyasatirtha's Nyayamrita has no public-domain English "
     "translation",
     "vyasatirtha_nyayamrita", "east", 1500),

    # ── INDIA: Raghunatha Siromani (~1477-1547 CE) ────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Raghunatha Siromani's Navya-Nyaya works have no "
     "public-domain English translation",
     "raghunatha_siromani_works", "east", 1510),

    # ── INDIA: Vallabhacharya (~1479-1531 CE) ─────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Vallabhacharya's Shodasha Granthas have no complete "
     "public-domain English translation",
     "vallabhacharya_works", "east", 1510),

    # ── INDIA: Chaitanya Mahaprabhu (~1486-1534 CE) ───────────────────────────
    # Siksastaka (8 verses); translations available within Vaishnava texts
    (fetch_internet_archive, "Chaitanya Mahaprabhu Vaishnava devotion",
     "chaitanya_mahaprabhu_works", "east", 1520),

    # ── INDIA: Ravidas (~1450-1520 CE) ────────────────────────────────────────
    # Shabads (hymns in Guru Granth Sahib); Hawley & Juergensmeyer 1988 is copyright
    (fetch_unavailable,
     "copyright_trans: Ravidas's hymns in the Guru Granth Sahib are available "
     "only in modern copyright translations; no standalone PD English text",
     "ravidas_hymns", "east", 1490),

    # ── INDIA: Mirabai (~1498-1557 CE) ────────────────────────────────────────
    # Bhakti poetry; Alston 1980 is copyright; older IA versions available
    # Mirabai — Thakur Das 1936 partial PD trans. IA: mirabaithakurdas00mira
    # mirabai_poems: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier mirabaithakurdas00mira exists but contains only PDF/DjVu scans — no .txt file in metadata; no plain-text PD English translation found",
     "mirabai_poems", "east", 1530),

    # ── INDIA: Guru Nanak (~1469-1539 CE) ────────────────────────────────────
    # Japji Sahib and other hymns — Macauliffe 1909 trans. PD
    # Guru Nanak — Macauliffe 1909 Sikh Religion Vol 1. IA: sikhreligionits01macauoft
    # guru_nanak_japji: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier sikhreligionits01macauoft exists but contains only PDF/DjVu scans — no .txt file in metadata; Macauliffe 1909 Sikh Religion Vol.1 not available as plain text",
     "guru_nanak_japji", "east", 1504),

    # ── TIBET: Mikyö Dorje (~1507-1554 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Mikyö Dorje's philosophical works have no public-domain "
     "English translation",
     "mikyo_dorje_works", "east", 1530),

    # ── INDIA: Madhusudana Sarasvati (~1540-1640 CE) ──────────────────────────
    (fetch_unavailable,
     "no_pd_english: Madhusudana Sarasvati's Advaita Siddhi has no "
     "public-domain English translation",
     "madhusudana_sarasvati_works", "east", 1580),

    # ── INDIA: Vijnana Bhikshu (~1550-1600 CE) ────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Vijnana Bhikshu's synthetic Vedanta works have no "
     "public-domain English translation",
     "vijnana_bhikshu_works", "east", 1575),

    # ── JAPAN: Fujiwara Seika (~1561-1619 CE) ────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Fujiwara Seika's Neo-Confucian writings have no "
     "public-domain English translation",
     "fujiwara_seika_works", "east", 1590),

    # ── JAPAN: Miyamoto Musashi (~1584-1645 CE) ───────────────────────────────
    # Book of Five Rings — Harris 1974 is copyright; Wilson 1982 is copyright;
    # but older PG trans. may exist
    (fetch_internet_archive, "Miyamoto Musashi Book Five Rings Go Rin No Sho",
     "musashi_book_five_rings", "east", 1645),

    # ── JAPAN: Kumazawa Banzan (~1619-1691 CE) ────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Kumazawa Banzan's Neo-Confucian writings have no "
     "public-domain English translation",
     "kumazawa_banzan_works", "east", 1655),

    # ── CHINA: Huang Zongxi (~1610-1695 CE) ──────────────────────────────────
    # Mingru Xue'an; de Bary 1993 anthology PD passages available
    # Huang Zongxi Mingru Xue'an — no complete PD English translation
    (fetch_unavailable,
     "no_pd_english: Huang Zongxi's Mingru Xue'an has no complete public-domain "
     "English translation",
     "huang_zongxi_mingru", "east", 1676),

    # ── CHINA: Wang Fuzhi (~1619-1692 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Wang Fuzhi's extensive philosophical writings have no "
     "public-domain English translation",
     "wang_fuzhi_works", "east", 1655),

    # ── JAPAN: Ito Jinsai (~1627-1705 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Ito Jinsai's Gomojigi (Meanings of the Analects and Mencius) "
     "has no public-domain English translation",
     "ito_jinsai_works", "east", 1666),

    # ── JAPAN: Kaibara Ekken (~1630-1714 CE) ─────────────────────────────────
    # Women and the Wisdom of Japan — Kaibara Ekken; Tucker 1989 is copyright
    # Kaibara Ekken — Tucker 1989 copyright; no PD English translation
    (fetch_unavailable,
     "copyright_trans: Kaibara Ekken's works available only in Tucker 1989 "
     "(copyright); no public-domain English translation confirmed",
     "kaibara_ekken_works", "east", 1672),

    # ── CHINA: Yen Yuan (~1635-1704 CE) ──────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Yen Yuan's practical Confucian writings have no "
     "public-domain English translation",
     "yen_yuan_works", "east", 1670),

    # ── JAPAN: Ogyu Sorai (~1666-1728 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Ogyu Sorai's Bendo (On Distinguishing the Way) has no "
     "public-domain English translation",
     "ogyu_sorai_works", "east", 1700),

    # ── CHINA: Li Gong (~1659-1733 CE) ────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Li Gong's practical Confucian writings have no "
     "public-domain English translation",
     "li_gong_works", "east", 1695),

    # ── EAST: D.T. Suzuki / Bankei / Hakuin placeholder (~1700-1800 CE) ──────
    (fetch_internet_archive, "Outlines Mahayana Buddhism Suzuki 1907",
     "suzuki_essays_zen", "east", 1750),
    (fetch_internet_archive, "Bankei unborn Zen",
     "bankei_unborn_zen", "east", 1690),

    # ── JAPAN: Tominaga Nakamoto (~1715-1746 CE) ─────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Tominaga Nakamoto's Shutsujo Kogo (Emerging from Meditation) "
     "has no public-domain English translation",
     "tominaga_nakamoto_works", "east", 1730),

    # ── JAPAN: Motoori Norinaga (~1730-1801 CE) ───────────────────────────────
    # Kojikiden commentary; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Motoori Norinaga's Kojikiden has no public-domain English "
     "translation; Nishimura 1997 is copyright",
     "motoori_norinaga_works", "east", 1765),

    # ── CHINA: Dai Zhen (~1724-1777 CE) ──────────────────────────────────────
    # Mengzi Ziyi Shuzheng; Chin & Freeman 1990 trans. is copyright
    (fetch_unavailable,
     "copyright_trans: Dai Zhen's Mengzi Ziyi Shuzheng available only in "
     "Chin & Freeman 1990 (copyright); no PD English translation",
     "dai_zhen_mengzi", "east", 1777),

    # ── CHINA: Zhang Xuecheng (~1738-1801 CE) ────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Zhang Xuecheng's Wenshi Tongyi has no public-domain "
     "English translation",
     "zhang_xuecheng_works", "east", 1789),

    # ── CHINA: Yu Zhengxie (~1775-1840 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Yu Zhengxie's Guisi Cunlao has no public-domain English "
     "translation",
     "yu_zhengxie_works", "east", 1808),

    # ── TIBET: Wangchuk Dorje (~1556-1603 CE) ────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Wangchuk Dorje's Mahamudra texts have no public-domain "
     "English translation",
     "wangchuk_dorje_works", "east", 1578),

    # ── TIBET: Jamyang Khyentse Wangpo (~1820-1892 CE) ───────────────────────
    (fetch_unavailable,
     "no_pd_english: Jamyang Khyentse Wangpo's Rime movement writings have no "
     "public-domain English translation",
     "jamyang_khyentse_wangpo_works", "east", 1856),

    # ── TIBET: Jamgon Kongtrul (~1813-1899 CE) ────────────────────────────────
    # Treasury of Knowledge; Guarisco & McLeod 2010 is copyright
    (fetch_unavailable,
     "copyright_trans: Jamgon Kongtrul's Sheja Dzö available only in "
     "Guarisco & McLeod 2010 (copyright); no PD English translation",
     "jamgon_kongtrul_works", "east", 1856),

    # ── TIBET: Jamgon Ju Mipham (~1846-1912 CE) ──────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Jamgon Ju Mipham's philosophical works have no "
     "public-domain English translation",
     "mipham_works", "east", 1879),

    # ── INDIA: Debendranath Tagore (~1817-1905 CE) ────────────────────────────
    # Autobiography — trans. Marjorie Sykes 1914, PD
    # Debendranath Tagore Autobiography — Collet 1914. IA: autobiographyofm00tago
    # debendranath_tagore_autobiography: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier autobiographyofm00tago exists but contains only PDF/DjVu scans — no .txt file in metadata; Collet 1914 trans. not available as plain text",
     "debendranath_tagore_autobiography", "east", 1890),

    # ── INDIA: Dayananda Saraswati (~1824-1883 CE) ────────────────────────────
    # Satyartha Prakash (Light of Truth) — PD trans. available
    # Dayananda Satyartha Prakash — Durga Prasad 1906. IA: satyarthaprakas00dayagoog
    # dayananda_satyartha_prakash: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier satyarthaprakas00dayagoog exists but contains only PDF/DjVu scans — no .txt file in metadata; Durga Prasad 1906 trans. not available as plain text",
     "dayananda_satyartha_prakash", "east", 1875),

    # ── INDIA: Ramakrishna Paramahamsa (~1836-1886 CE) ───────────────────────
    (fetch_internet_archive, "Gospel Ramakrishna Nikhilananda",
     "gospel_ramakrishna", "east", 1882),

    # ── INDIA: Swami Vivekananda (~1863-1902 CE) ──────────────────────────────
    (fetch_internet_archive, "Vivekananda complete works",
     "vivekananda_complete_works", "east", 1890),

    # ── INDIA: Bal Gangadhar Tilak (~1856-1920 CE) ────────────────────────────
    # The Arctic Home in the Vedas — PD
    # Tilak Gita Rahasya — Sukthankar 1935. IA: srimadbhagavadgi00tilauoft
    # tilak_gita_rahasya: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier srimadbhagavadgi00tilauoft exists but contains only PDF/DjVu scans — no .txt file in metadata; Sukthankar 1935 trans. not available as plain text",
     "tilak_gita_rahasya", "east", 1915),

    # ── INDIA: Rabindranath Tagore (~1861-1941 CE) ────────────────────────────
    # Gitanjali — PG #7164 (Nobel Prize 1913, PD)
    (fetch_gutenberg_id, 7164, "tagore_gitanjali", "east", 1910),

    # ── INDIA: Sri Aurobindo (~1872-1950 CE) ─────────────────────────────────
    # The Life Divine — 1939-1940; PD in many jurisdictions
    (fetch_internet_archive, "Sri Aurobindo Life Divine philosophy",
     "aurobindo_life_divine", "east", 1939),

    # ── INDIA: Ramana Maharshi (~1879-1950 CE) ────────────────────────────────
    # Who Am I? — PD pamphlet translation
    (fetch_internet_archive, "Ramana Maharshi Who Am I Self-Inquiry",
     "ramana_maharshi_who_am_i", "east", 1902),

    # ── INDIA: B.R. Ambedkar (~1891-1956 CE) ─────────────────────────────────
    # The Buddha and His Dhamma — PD
    (fetch_internet_archive, "Ambedkar Buddha Dhamma Buddhist conversion",
     "ambedkar_buddha_and_dhamma", "east", 1956),

    # ── INDIA: Sarvepalli Radhakrishnan (~1888-1975 CE) ───────────────────────
    # Indian Philosophy Vol 1 — 1923 PD
    # Radhakrishnan Indian Philosophy Vol 1 — 1923 PD. IA: indianphilosophy01radhuoft
    # radhakrishnan_indian_philosophy: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier indianphilosophy01radhuoft exists but contains only PDF/DjVu scans — no .txt file in metadata; Radhakrishnan Indian Philosophy Vol.1 1923 not available as plain text",
     "radhakrishnan_indian_philosophy", "east", 1923),

    # ── INDIA: Mahatma Gandhi (~1869-1948 CE) ────────────────────────────────
    # Hind Swaraj — PG #23440 (PD)
    (fetch_gutenberg_id, 23440, "gandhi_hind_swaraj", "east", 1909),

    # ── INDIA: Muhammad Iqbal (~1877-1938 CE) ────────────────────────────────
    # Reconstruction of Religious Thought in Islam — PD in many jurisdictions
    (fetch_internet_archive, "Iqbal Reconstruction Religious Thought Islam",
     "iqbal_reconstruction", "east", 1930),

    # ── CHINA: Kang Youwei (~1858-1927 CE) ────────────────────────────────────
    # Ta Tung Shu (Book of Great Harmony) — Thompson 1958 trans. PD
    # Kang Youwei Ta Tung Shu — Thompson 1958. IA: tatungshuoneworldthomp
    # kang_youwei_ta_tung_shu: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier tatungshuoneworldthomp exists but contains only PDF/DjVu scans — no .txt file in metadata; Thompson 1958 Ta T'ung Shu not available as plain text",
     "kang_youwei_ta_tung_shu", "east", 1902),

    # ── CHINA: Liang Qichao (~1873-1929 CE) ──────────────────────────────────
    # Liang Qichao — no complete PD English primary text
    (fetch_unavailable,
     "no_pd_english: Liang Qichao's philosophical essays have no complete "
     "public-domain English translation",
     "liang_qichao_works", "east", 1902),

    # ── CHINA: Hu Shih (~1891-1962 CE) ───────────────────────────────────────
    # The Development of the Logical Method in Ancient China — 1922 PD
    (fetch_internet_archive, "Hu Shih Development Logical Method Ancient China",
     "hu_shih_logical_method", "east", 1922),

    # ── KOREA: Ch'oe Ch'i-won (~born 857 CE) ─────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Ch'oe Ch'i-won's philosophical writings have no "
     "public-domain English translation",
     "choe_chi_won_works", "east", 880),

    # ── KOREA: Chong Tojon (~1342-1398 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Chong Tojon's Joseon Confucian writings have no "
     "public-domain English translation",
     "chong_tojon_works", "east", 1370),

    # ── KOREA: Yi Hwang (~1501-1570 CE) ──────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Yi Hwang's (Toegye) Neo-Confucian writings have no "
     "public-domain English translation",
     "yi_hwang_toegye_works", "east", 1536),

    # ── KOREA: Yi I (~1536-1584 CE) ───────────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Yi I's (Yulgok) Neo-Confucian writings have no "
     "public-domain English translation",
     "yi_i_yulgok_works", "east", 1568),

    # ── KOREA: Chong Yagyong (~1762-1836 CE) ─────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Chong Yagyong's (Dasan) extensive philosophical writings "
     "have no public-domain English translation",
     "chong_yagyong_dasan_works", "east", 1800),

    # ── JAPAN: Nishi Amane (~1829-1897 CE) ────────────────────────────────────
    (fetch_unavailable,
     "no_pd_english: Nishi Amane's philosophical writings have no public-domain "
     "English translation",
     "nishi_amane_works", "east", 1864),

    # ── JAPAN: Nishida Kitaro (~1870-1945 CE) ────────────────────────────────
    # An Inquiry into the Good — Abe & Ives 1990 is copyright; older PD version exists
    # Nishida — A Study of Good, Shimomura 1960. IA: studyofgood00nish
    # nishida_inquiry_into_good: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier studyofgood00nish exists but contains only PDF/DjVu scans — no .txt file in metadata; Shimomura 1960 A Study of Good not available as plain text",
     "nishida_inquiry_into_good", "east", 1911),

    # ── JAPAN: D.T. Suzuki (~1870-1966 CE) ───────────────────────────────────
    # Already covered by suzuki_essays_zen above; also add Essays in Zen Buddhism
    # D.T. Suzuki Essays in Zen Buddhism First Series 1927. IA: essaysinzenbud01suzu
    # suzuki_essays_zen_buddhism: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier essaysinzenbud01suzu exists but contains only PDF/DjVu scans — no .txt file in metadata; Suzuki Essays in Zen Buddhism 1927 not available as plain text",
     "suzuki_essays_zen_buddhism", "east", 1927),

    # ── EAST: Paul Carus placeholder (~200 CE) ────────────────────────────────
    (fetch_internet_archive, "Gospel Buddha Carus",
     "gospel_of_buddha_carus", "east", 200),

    # ==========================================================================
    # WEST: Additional previously missing entries
    # ==========================================================================

    # ── WEST: Bertrand Russell (~1872-1970 CE) ────────────────────────────────
    # The Problems of Philosophy (1912) — PD
    (fetch_gutenberg_id, 5827, "russell_problems_of_philosophy", "west", 1912),

    # ── WEST: William James — Pragmatism (1907) ───────────────────────────────
    (fetch_gutenberg_id, 5116, "james_pragmatism", "west", 1907),

    # ── WEST: Charles Sanders Peirce (~1839-1914 CE) ──────────────────────────
    # How to Make Our Ideas Clear (1878) — PD, available via IA
    # C.S. Peirce Chance Love and Logic — Cohen 1923 PD. IA: chancelovelogics00peiriala
    # peirce_pragmatism_essays: pdf_only — see rationale MD
    (fetch_unavailable,
     "pdf_only: IA identifier chancelovelogics00peiriala exists but contains only PDF/DjVu scans — no .txt file in metadata; Cohen 1923 Chance Love and Logic not available as plain text",
     "peirce_pragmatism_essays", "west", 1878),

    # ── WEST: Friedrich Schleiermacher (~1768-1834 CE) ────────────────────────
    # On Religion: Speeches to Its Cultured Despisers — Oman 1893 trans., PD
    (fetch_internet_archive, "Schleiermacher On Religion Speeches Cultured Despisers",
     "schleiermacher_on_religion", "west", 1799),

    # ── WEST: Johann Gottlieb Fichte (~1762-1814 CE) ──────────────────────────
    # The Vocation of Man — PG #38088
    (fetch_gutenberg_id, 38088, "fichte_vocation_of_man", "west", 1800),

    # ── WEST: F.W.J. von Schelling (~1775-1854 CE) ────────────────────────────
    # System of Transcendental Idealism; Heath 1978 is copyright
    (fetch_unavailable,
     "copyright_trans: Schelling's System of Transcendental Idealism available "
     "only in Heath 1978 (copyright); older translations are not in clean PD English",
     "schelling_system_idealism", "west", 1800),

    # ── WEST: Auguste Comte (~1798-1857 CE) ──────────────────────────────────
    # A General View of Positivism — Bridges 1865 trans., PD
    (fetch_internet_archive, "Auguste Comte General View Positivism Bridges",
     "comte_general_view_positivism", "west", 1848),

    # ── WEST: Ludwig Feuerbach (~1804-1872 CE) ────────────────────────────────
    # Already added above as feuerbach_essence_christianity

    # ── WEST: Pierre-Joseph Proudhon (~1809-1865 CE) ─────────────────────────
    # What is Property? — Tucker 1876 trans., PD
    (fetch_gutenberg_id, 360, "proudhon_what_is_property", "west", 1840),

    # ── WEST: Michael Bakunin (~1814-1876 CE) ─────────────────────────────────
    # God and the State — 1882 PD trans.
    (fetch_gutenberg_id, 36776, "bakunin_god_and_state", "west", 1882),

    # ── WEST: Herbert Spencer (~1820-1903 CE) ─────────────────────────────────
    # First Principles — PG #4350
    (fetch_gutenberg_id, 4350, "spencer_first_principles", "west", 1862),

    # ── WEST: Wilhelm Dilthey (~1833-1911 CE) ─────────────────────────────────
    # Introduction to the Human Sciences; no PD English translation
    (fetch_unavailable,
     "no_pd_english: Dilthey's Einleitung in die Geisteswissenschaften has no "
     "public-domain English translation; Rickman 1976 is copyright",
     "dilthey_introduction_human_sciences", "west", 1883),

    # ── WEST: Franz Brentano (~1838-1917 CE) ─────────────────────────────────
    # Psychology from an Empirical Standpoint; Rancurello 1973 is copyright
    (fetch_unavailable,
     "copyright_trans: Brentano's Psychologie vom empirischen Standpunkt "
     "available only in Rancurello et al. 1973 (copyright)",
     "brentano_psychology_empirical", "west", 1874),

    # ── WEST: Gottlob Frege (~1848-1925 CE) ──────────────────────────────────
    # Begriffsschrift; van Heijenoort 1967 is copyright
    (fetch_unavailable,
     "copyright_trans: Frege's Begriffsschrift and Grundlagen der Arithmetik "
     "available only in modern copyright translations",
     "frege_begriffsschrift", "west", 1879),

    # ── WEST: Edmund Husserl (~1859-1938 CE) ─────────────────────────────────
    # Ideas: General Introduction to Pure Phenomenology; Boyce Gibson 1931 PD
    (fetch_internet_archive, "Husserl Ideas Pure Phenomenology Boyce Gibson",
     "husserl_ideas_phenomenology", "west", 1913),

    # ── WEST: Henri Bergson (~1859-1941 CE) ──────────────────────────────────
    # Creative Evolution — Mitchell 1911 trans., PD
    (fetch_gutenberg_id, 26163, "bergson_creative_evolution", "west", 1907),

    # ── WEST: John Dewey (~1859-1952 CE) ─────────────────────────────────────
    # Reconstruction in Philosophy — PG #40089
    (fetch_gutenberg_id, 40089, "dewey_reconstruction_philosophy", "west", 1920),

    # ── WEST: Sigmund Freud (~1856-1939 CE) ──────────────────────────────────
    # The Interpretation of Dreams (1900) — Brill 1913 trans., PD
    (fetch_gutenberg_id, 39521, "freud_interpretation_dreams", "west", 1900),

    # ── WEST: Max Weber (~1864-1920 CE) ──────────────────────────────────────
    # The Protestant Ethic and the Spirit of Capitalism; Parsons 1930 PD
    (fetch_internet_archive, "Max Weber Protestant Ethic Capitalism Parsons",
     "weber_protestant_ethic", "west", 1905),

    # ── WEST: Ludwig Wittgenstein (~1889-1951 CE) ─────────────────────────────
    # Tractatus Logico-Philosophicus — Ogden 1922 trans., PD
    # Wittgenstein Tractatus — Ogden 1922 PD. PG #5740 dead; IA: tractatuslogicop00witt
    # wittgenstein_tractatus: restricted_ia — see rationale MD
    (fetch_unavailable,
     "restricted_ia: IA identifier tractatuslogicop00witt returns HTTP 401 — access restricted; PG #5740 also dead; Ogden 1922 Tractatus not currently accessible as plain text",
     "wittgenstein_tractatus", "west", 1921),

    # ── WEST: Martin Heidegger (~1889-1976 CE) ────────────────────────────────
    # Being and Time; Macquarrie & Robinson 1962 is copyright
    (fetch_unavailable,
     "copyright_trans: Heidegger's Sein und Zeit available only in copyright "
     "English translations (Macquarrie & Robinson 1962; Stambaugh 1996); "
     "no PD English translation exists",
     "heidegger_being_and_time", "west", 1927),

    # ── WEST: Jean-Paul Sartre (~1905-1980 CE) ────────────────────────────────
    # Existentialism is a Humanism (1945); various PD reprints
    (fetch_internet_archive, "Sartre Existentialism Humanism",
     "sartre_existentialism_humanism", "west", 1945),

    # ── WEST: Simone de Beauvoir (~1908-1986 CE) ─────────────────────────────
    # The Second Sex; Parshley 1953 is copyright
    (fetch_unavailable,
     "copyright_trans: Beauvoir's Le Deuxième Sexe available only in copyright "
     "English translations; Parshley 1953 and Borde & Malovany-Chevallier 2010 "
     "are both copyright",
     "beauvoir_second_sex", "west", 1949),

    # ── WEST: Albert Camus (~1913-1960 CE) ────────────────────────────────────
    # The Myth of Sisyphus; O'Brien 1955 is copyright
    (fetch_unavailable,
     "copyright_trans: Camus's Le Mythe de Sisyphe available only in O'Brien "
     "1955 trans. (copyright); The Stranger (O'Brien 1946) also copyright",
     "camus_myth_sisyphus", "west", 1942),

    # ── WEST: Ralph Waldo Emerson — also add Nature (1836) ───────────────────
    (fetch_gutenberg_id, 29433, "emerson_nature", "west", 1836),

    # ── WEST: William James — also included above already

    # ── WEST: Hegel — also add Philosophy of Right ───────────────────────────
    (fetch_internet_archive, "Hegel Philosophy Right Knox",
     "hegel_philosophy_right", "west", 1820),
]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true",
                   help="Print sources without downloading anything")
    p.add_argument("--label", metavar="LABEL",
                   help="Only fetch the source with this label")
    p.add_argument("--skip-unavailable", action="store_true",
                   help="Skip entries that use fetch_unavailable")
    p.add_argument("--region", choices=["east", "west"],
                   help="Only fetch sources for this region")
    p.add_argument("--year-min", type=int, metavar="YEAR",
                   help="Only fetch sources with year >= YEAR")
    p.add_argument("--year-max", type=int, metavar="YEAR",
                   help="Only fetch sources with year <= YEAR")
    return p.parse_args()


def _parse_entry(entry: tuple) -> tuple:
    """Unpack a SOURCES entry into (fn, fn_args, label, region, year)."""
    fn, *rest = entry
    year: int = rest[-1]
    region: str = rest[-2]
    label: str = rest[-3]
    fn_args: list = rest[:-3]
    return fn, fn_args, label, region, year


def main() -> None:
    args = _parse_args()

    sources = SOURCES

    if args.label:
        sources = [s for s in sources if _parse_entry(s)[2] == args.label]
        if not sources:
            print(f"No source found with label '{args.label}'")
            return

    if args.skip_unavailable:
        sources = [s for s in sources if _parse_entry(s)[0] is not fetch_unavailable]

    if args.region:
        sources = [s for s in sources if _parse_entry(s)[3] == args.region]

    if args.year_min is not None:
        sources = [s for s in sources if _parse_entry(s)[4] >= args.year_min]

    if args.year_max is not None:
        sources = [s for s in sources if _parse_entry(s)[4] <= args.year_max]

    if args.dry_run:
        total = len(sources)
        unavailable = sum(1 for s in sources if _parse_entry(s)[0] is fetch_unavailable)
        fetchable = total - unavailable

        print(f"{'FETCHER':<30} {'LABEL':<50} {'REGION':<6} {'YEAR':<8} FOLDER")
        print("-" * 115)
        for entry in sources:
            fn, fn_args, label, region, year = _parse_entry(entry)
            folder = get_folder_path(label, region, year).relative_to(DATA_DIR)
            status = "[N/A]" if fn is fetch_unavailable else "     "
            print(f"{status} {fn.__name__:<28} {label:<50} {region:<6} {year:<8} {folder}")
        print(f"\n{total} source(s) listed  ({fetchable} fetchable, {unavailable} unavailable).")
        return

    print(f"Output directory: {DATA_DIR.resolve()}\n")
    ok = fail = skipped = 0
    for entry in sources:
        fn, fn_args, label, region, year = _parse_entry(entry)
        print(f"Fetching: {label}")
        try:
            success = fn(*fn_args, label, region, year=year)
        except Exception as exc:
            print(f"  [ERROR] {label}: {exc}")
            success = False
        if fn is fetch_unavailable:
            skipped += 1
        elif success:
            ok += 1
        else:
            fail += 1
        time.sleep(DELAY)

    print(f"\nDone. {ok} succeeded, {fail} failed, {skipped} unavailable/skipped.")
    for region_dir in (EAST_DIR, WEST_DIR):
        files = sorted(region_dir.rglob("*.txt"))
        if files:
            print(f"\nFiles in {region_dir}/:")
            for f in files:
                print(f"  {str(f.relative_to(region_dir)):<60} {f.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()