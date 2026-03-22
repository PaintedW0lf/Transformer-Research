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
      older (BC)/   ← Asian texts dated before 0 CE
      100/          ← Asian texts 0–100 CE
      200/          ← Asian texts 100–200 CE
      ...
    west/
      older (BC)/   ← European texts dated before 0 CE
      100/          ← European texts 0–100 CE
      ...

Each text is assigned based on the earliest known date of the source text.
BCE texts go into "older (BC)"; CE texts go into a 100-year interval folder
whose name is the upper bound of that interval (0–100 → "100", etc.).

Usage:
    python download_pretraining_data.py
    python download_pretraining_data.py --dry-run   # list sources, no downloads
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

    BCE (year < 0)  →  "older (BC)"
    CE  (year >= 0) →  upper bound of the containing 100-year interval,
                       e.g. 0–99 → "100", 100–199 → "200", …
    """
    if year < 0:
        return BCE_FOLDER
    return str((year // 100 + 1) * 100)


def get_folder_path(text_name: str, region: str, year: int) -> Path:
    """Return the destination folder for a text given its region and year.

    Mapping: (text_name, region, year) → Path
      region "east" → EAST_DIR / get_time_folder(year)
      region "west" → WEST_DIR / get_time_folder(year)
    """
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
    """Minimal, dependency-free HTML → plain text.

    Only skips <script> and <style> blocks (code/CSS).  Other structural tags
    like <head>, <nav>, <footer> are intentionally NOT skipped because they
    may be missing their closing tags in old HTML, which would cause the depth
    counter to stay positive and silently drop all body text.
    """

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
    """Return lightweight English-likelihood stats for downloaded text.

    Metrics:
    - ascii_ratio: fraction of characters in ASCII range
    - latin_alpha_ratio: fraction of alphabetic chars that are ASCII/Latin
    - stopword_ratio: share of tokens in a small English stopword set
    - word_count: number of alphabetic tokens
    """
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
    """Heuristic language guard to reject non-English or OCR-garble downloads."""
    ascii_ratio, latin_alpha_ratio, stopword_ratio, word_count = _english_stats(text)

    # Extremely short text is never useful for training.
    if word_count < 200:
        return False

    # Keep thresholds permissive enough for old translations with diacritics,
    # but strict enough to reject non-English scripts and OCR noise.
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
        print(f"      [WARN] {url} → {exc}")
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
    """Download a PG ebook by numeric ID, trying standard URL patterns."""
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
    """
    Search Project Gutenberg via the gutendex.com JSON API and download
    the first plain-text result.
    """
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
    """
    Search IA with the advancedsearch JSON API, then download the first
    result that has a .txt file (prefers plain text over djvu.txt).
    Skips items that return 401/403 or exceed IA_MAX_MB.
    """
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
        # Build ranked candidate list: plain .txt first, then _djvu.txt
        candidates = [f for f in files if f["name"].endswith(".txt")
                      and "_djvu" not in f["name"]]
        candidates += [f for f in files if f["name"].endswith("_djvu.txt")]
        if not candidates:
            continue

        for txt in candidates:
            # Skip files over the size limit
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
                    break   # try next search result
                dr.raise_for_status()
            except Exception as exc:
                print(f"      [WARN] {dl_url} → {exc}")
                continue

            _save(label, dr.text, region, year)
            return True

    print(f"  [FAIL] IA '{query}' ({label}): no accessible text file found")
    return False


def fetch_sacred_texts(index_url: str, label: str, region: str = "west",
                       year: Optional[int] = None, max_subpages: int = 80) -> bool:
    """
    Scrape a sacred-texts.com index page, follow same-directory .htm links,
    and concatenate the plain text of all subpages.
    """
    r = _get(index_url)
    if r is None:
        return False

    base = index_url.rsplit("/", 1)[0] + "/"
    links_raw = re.findall(r'href="([^"#?]+\.htm[l]?)"', r.text, re.IGNORECASE)

    seen: set[str] = set()
    pages: list[str] = []
    for lnk in links_raw:
        if lnk.startswith("http"):
            continue   # skip off-site
        full = urljoin(base, lnk)
        if full not in seen:
            seen.add(full)
            pages.append(full)

    if not pages:
        # Single-page source — just use the index itself
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
    """
    Scrape accesstoinsight.org via a two-level traversal:
      1. root_url  (e.g. /tipitaka/) → nikaya index pages
      2. nikaya index pages           → individual sutta pages
    All sutta text is stripped and concatenated.
    """
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

    # Level 1: root → nikaya index pages (end with /index.html)
    nikaya_indexes = [u for u in _collect_links(root_url) if u.endswith("index.html")]
    if not nikaya_indexes:
        print(f"  [FAIL] access-to-insight: no nikaya indexes at {root_url}")
        return False
    print(f"      Found {len(nikaya_indexes)} nikaya indexes — collecting sutta links …")

    # Level 2: each nikaya index → individual sutta pages (non-index .html)
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
    print(f"      Found {len(sutta_urls)} sutta pages — downloading …")

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
    """
    Download a nikaya from SuttaCentral using the suttaplex + bilara API.

    1. GET /api/suttaplex/{nikaya}?lang=en  → list of leaf UIDs
    2. For each UID: GET /api/bilarasuttas/{uid}/{translator} → segments
    """
    plex_url = f"https://suttacentral.net/api/suttaplex/{nikaya}?lang=en"
    r = _get(plex_url)
    if r is None:
        return False

    items = r.json() if isinstance(r.json(), list) else []
    uids = [item["uid"] for item in items if item.get("type") == "leaf"]

    if not uids:
        print(f"  [FAIL] SuttaCentral '{nikaya}': no leaf sutta UIDs found")
        return False

    print(f"      Found {len(uids)} suttas in '{nikaya}' — downloading …")
    chunks: list[str] = []
    for uid in uids[:300]:   # cap to avoid multi-hour runs
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


# ---------------------------------------------------------------------------
# Source catalogue
# ---------------------------------------------------------------------------
# Each entry: (fetcher_fn, *fn_args, label, region, year)
#   label  – output filename stem
#   region – "east" or "west"
#   year   – earliest known year of the source text (negative = BCE)
#             used to assign the time-period subfolder via get_time_folder()

SOURCES: list[tuple] = [

    # ── INDIA: Upanishads (~800 BCE) ──────────────────────────────────────
    # SBE Vol 15 (Müller) contains both Brihadaranyaka and Chandogya
    (fetch_gutenberg_id, 2034, "upanishads_muller_sbe15", "east", -800),

    # ── INDIA: Pali Canon (~480 BCE) ──────────────────────────────────────
    # SuttaCentral — Sujato translation (CC0) — one source per nikaya
    (fetch_suttacentral, "dn",  "pali_dn_sujato",  "east", -480),
    (fetch_suttacentral, "mn",  "pali_mn_sujato",  "east", -480),
    (fetch_suttacentral, "sn",  "pali_sn_sujato",  "east", -480),
    (fetch_suttacentral, "an",  "pali_an_sujato",  "east", -480),
    (fetch_suttacentral, "dhp", "pali_dhp_sujato", "east", -480),
    (fetch_suttacentral, "kn",  "pali_kn_sujato",  "east", -480),
    # Thanissaro Bhikkhu — Access to Insight (different translation, open license)
    (fetch_access_to_insight,
     "https://www.accesstoinsight.org/tipitaka/",
     "pali_thanissaro_ati", "east", -480),

    # ── INDIA: Bhagavad Gita (~400–200 BCE) ──────────────────────────────
    # Edwin Arnold trans. "The Song Celestial" (1885) — PG #2388
    # Authority: Radhakrishnan & Moore 1957, pp. 101–163; Scharfstein 1998, ch. 3
    (fetch_gutenberg_id, 2388, "bhagavad_gita_arnold", "east", -300),

    # ── CHINA: Analects (~479 BCE) ────────────────────────────────────────
    # Authority: Fung Yu-lan 1952, vol. I ch. 4; Scharfstein 1998, ch. 6
    (fetch_gutenberg_id, 3330, "analects_legge", "east", -479),

    # ── CHINA: Mencius (~372 BCE) ─────────────────────────────────────────
    # Authority: Fung Yu-lan 1952, vol. I ch. 7; Scharfstein 1998, ch. 6
    (fetch_gutenberg_id, 38406, "mencius_legge", "east", -372),

    # ── CHINA: Tao Te Ching (~400 BCE) ───────────────────────────────────
    # Authority: Fung Yu-lan 1952, vol. I ch. 8; Scharfstein 1998, ch. 7
    (fetch_gutenberg_id, 216, "tao_te_ching_legge", "east", -400),

    # ── CHINA: Zhuangzi (~350 BCE) ────────────────────────────────────────
    # Authority: Fung Yu-lan 1952, vol. I ch. 10; Scharfstein 1998, ch. 7
    (fetch_gutenberg_id, 29724, "zhuangzi_legge", "east", -350),

    # ── CHINA: Xunzi (~313–238 BCE) ──────────────────────────────────────
    # H.H. Dubs trans. "Works of Hsuntze" (1928, PD) — IA identifier in.ernet.dli.2015.103953
    # Authority: Fung Yu-lan 1952, vol. I ch. 12
    (fetch_internet_archive, "Works Hsuntze",
     "xunzi_dubs", "east", -300),

    # ── CHINA: Mozi (~470 BCE) ────────────────────────────────────────────
    # Authority: Fung Yu-lan 1952, vol. I ch. 5
    (fetch_internet_archive, "Works Motse Yi-Pao Mei",
     "mozi_mei", "east", -470),

    # ── WEST: Pre-Socratics (~600 BCE) ───────────────────────────────────
    # Burnet — Early Greek Philosophy (Heraclitus, Parmenides, Empedocles …)
    (fetch_gutenberg_search, "Early Greek Philosophy Burnet",
     "pre_socratics_burnet", "west", -600),
    (fetch_internet_archive, "Fairbanks handbook Greek philosophy",
     "pre_socratics_fairbanks", "west", -600),

    # ── WEST: Plato (~428 BCE) ────────────────────────────────────────────
    # Known Gutenberg IDs (Jowett translations)
    # Project Gutenberg individual dialogues (Jowett) — one source: Gutenberg only
    (fetch_gutenberg_id, 1497, "plato_republic_jowett",    "west", -428),
    (fetch_gutenberg_id, 1658, "plato_phaedo_jowett",      "west", -428),
    (fetch_gutenberg_id, 1600, "plato_symposium_jowett",   "west", -428),
    (fetch_gutenberg_id, 1656, "plato_apology_jowett",     "west", -428),
    (fetch_gutenberg_id, 1672, "plato_gorgias_jowett",     "west", -428),
    (fetch_gutenberg_id, 1735, "plato_theaetetus_jowett",  "west", -428),
    (fetch_gutenberg_id, 1572, "plato_timaeus_jowett",     "west", -428),

    # ── WEST: Aristotle (~384 BCE) ────────────────────────────────────────
    # Known Gutenberg IDs for Aristotle
    (fetch_gutenberg_id, 8438,  "aristotle_nicomachean_ethics", "west", -384),
    (fetch_internet_archive, "Metaphysica Aristotle",
     "aristotle_metaphysics", "west", -384),
    (fetch_gutenberg_id, 6762,  "aristotle_politics",           "west", -384),
    # Physics — IA: "Aristotle Organon And Other Works" (includes Physics)
    (fetch_internet_archive, "Organon Aristotle",
     "aristotle_physics", "west", -384),
    # De Anima — R.D. Hicks translation
    (fetch_internet_archive, "De Anima Aristotle",
     "aristotle_de_anima", "west", -384),

    # ── PERSIA: Avesta (~1200 BCE, Gathas) ───────────────────────────────
    # Darmesteter — SBE Vol 4 (Vendidad); Mills — SBE Vol 31 (Gathas/Yasnas)
    # One source per translator; dropped Vol 23 (same Darmesteter translator as Vol 4)
    (fetch_internet_archive, "Zend-Avesta Darmesteter Vendidad",
     "avesta_darmesteter_vol4", "west", -1200),
    (fetch_internet_archive, "Avesta Mills Zend",
     "avesta_mills", "west", -1200),

    # =========================================================================
    # CE TEXTS — 100-YEAR INTERVALS (0–1900 CE)
    # =========================================================================

    # ── 0–100 CE ─────────────────────────────────────────────────────────────
    # EAST
    # Ashvaghosha — Buddhacharita (~80 CE)
    (fetch_internet_archive, "Buddhacarita Cowell",
     "buddhacharita_cowell", "east", 80),
    # Milindapanha / Questions of King Milinda (~100 CE)
    (fetch_internet_archive, "Questions King Milinda Rhys Davids",
     "milindapanha_rhys_davids", "east", 100),
    # WEST
    # Seneca — Letters to Lucilius (~65 CE)
    (fetch_gutenberg_search, "Seneca",
     "seneca_letters_lucilius", "west", 65),
    # Epictetus — Enchiridion (~100 CE)
    (fetch_gutenberg_search, "Epictetus",
     "epictetus_enchiridion", "west", 100),

    # ── 100–200 CE ────────────────────────────────────────────────────────────
    # EAST
    # Nagarjuna — Mulamadhyamakakarika (~150 CE)
    (fetch_internet_archive, "Mulamadhyamakakarika Nagarjuna",
     "nagarjuna_mulamadhyamakakarika", "east", 150),
    # Ashvaghosha — Awakening of Faith (~150 CE)
    (fetch_internet_archive, "Awakening Faith Mahayana",
     "awakening_of_faith_suzuki", "east", 150),
    # WEST
    # Marcus Aurelius — Meditations (~170 CE)
    (fetch_gutenberg_id, 2680, "marcus_aurelius_meditations", "west", 170),
    # Epictetus — Discourses (~108 CE)
    (fetch_internet_archive, "Discourses Epictetus",
     "epictetus_discourses", "west", 108),

    # ── 200–300 CE ────────────────────────────────────────────────────────────
    # EAST
    # Paul Carus — The Gospel of Buddha (1894) — PD retelling of Buddhist teaching (~2nd–3rd c. sources)
    # Wang Bi and Diamond Sutra translations without copyright are unavailable
    (fetch_internet_archive, "Gospel Buddha Carus",
     "gospel_of_buddha_carus", "east", 200),
    # WEST
    # Plotinus — Enneads (~250–270 CE)
    (fetch_internet_archive, "Plotinus Enneads MacKenna",
     "plotinus_enneads_mackenna", "west", 260),
    # Origen — On First Principles (~230 CE)
    (fetch_internet_archive, "Ante-Nicene Fathers Origen",
     "origen_de_principiis", "west", 230),

    # ── 300–400 CE ────────────────────────────────────────────────────────────
    # EAST
    # Vimalakirti Sutra (~100–300 CE) — key Mahayana text; Thurman/Lamotte are copyright
    # Use the Hokei Idumi 1922 translation available on IA
    (fetch_internet_archive, "Vimalakirti Sutra Nirdesa Mahayana",
     "vimalakirti_sutra", "east", 300),
    # WEST
    # Augustine — Confessions (~397 CE)
    (fetch_gutenberg_id, 3296, "augustine_confessions", "west", 397),
    # Eusebius — Ecclesiastical History (~313 CE)
    (fetch_internet_archive, "Ecclesiastical History Eusebius",
     "eusebius_church_history", "west", 313),

    # ── 400–500 CE ────────────────────────────────────────────────────────────
    # EAST
    # Patanjali — Yoga Sutras (~400 CE) — Johnston 1912 / Vivekananda trans.
    # Authority: Radhakrishnan & Moore 1957, pp. 453–485 ("Yoga system of Patanjali")
    (fetch_internet_archive, "Yoga Sutras Patanjali",
     "yoga_sutras_patanjali", "east", 400),
    # Buddhaghosa — Visuddhimagga (~430 CE)
    # Authority: Radhakrishnan & Moore 1957, p. 285; Deutsch & Bontekoe 1997, ch. 7
    (fetch_internet_archive, "Visuddhimagga path purification",
     "visuddhimagga_buddhaghosa", "east", 430),
    # WEST
    # Augustine — City of God (~413–426 CE)
    (fetch_gutenberg_search, "Augustine City of God Dods",
     "augustine_city_of_god", "west", 420),
    # Jerome — Selected Letters (~380–420 CE)
    (fetch_internet_archive, "Select Letters Jerome",
     "jerome_letters", "west", 400),

    # ── 500–600 CE ────────────────────────────────────────────────────────────
    # EAST
    # Lankavatara Sutra (~4th–5th c.) — Suzuki 1932 translation; PD in US
    # Asanga's Mahayana-samgraha only available in modern copyright translations
    (fetch_internet_archive, "Lankavatara Sutra Suzuki Buddhist",
     "lankavatara_sutra_suzuki", "east", 500),
    # WEST
    # Boethius — Consolation of Philosophy (~524 CE)
    (fetch_gutenberg_id, 14328, "boethius_consolation_philosophy", "west", 524),
    # Benedict of Nursia — Rule of Saint Benedict (~530 CE)
    (fetch_internet_archive, "Rule Saint Benedict Gasquet",
     "benedict_rule", "west", 530),

    # ── 600–700 CE ────────────────────────────────────────────────────────────
    # WEST
    # The Quran (~632 CE) — Rodwell translation
    (fetch_internet_archive, "Koran Quran Rodwell translation",
     "quran_rodwell", "west", 632),

    # ── 700–800 CE ────────────────────────────────────────────────────────────
    # EAST
    # Shantideva — Bodhicaryavatara (~700 CE)
    (fetch_internet_archive, "Bodhisattva way life Shantideva",
     "shantideva_bodhicaryavatara", "east", 700),
    # Platform Sutra of the Sixth Patriarch / Huineng (~750 CE)
    (fetch_internet_archive, "Platform sutra patriarch",
     "platform_sutra_huineng", "east", 750),
    # WEST
    # John of Damascus — Orthodox Faith (~730 CE) — Salmond translation (Nicene Fathers vol 9)
    (fetch_internet_archive, "John Damascus Exposition Orthodox Faith Salmond",
     "john_damascus_orthodox_faith", "west", 730),

    # ── 800–900 CE ────────────────────────────────────────────────────────────
    # EAST
    # Shankara — Vivekachudamani ("Crest-Jewel of Wisdom") (~788 CE) — Johnston 1925 trans., PD
    # Authority: Radhakrishnan & Moore 1957, pp. 506–517; Scharfstein 1998, ch. 3
    (fetch_internet_archive, "Crest Jewel Wisdom Shankara Johnston",
     "shankara_vivekachudamani", "east", 788),
    # Tibetan Book of the Dead (~8th–9th c. CE) — Evans-Wentz 1927 translation, public domain
    # Authority: Deutsch & Bontekoe 1997, ch. 9
    (fetch_internet_archive, "Tibetan Book Dead Evans-Wentz",
     "tibetan_book_of_dead", "east", 820),
    # WEST
    # John Scotus Eriugena — Periphyseon (~866 CE)
    (fetch_internet_archive, "Eriugena Periphyseon division nature",
     "eriugena_periphyseon", "west", 866),
    # Al-Kindi — On First Philosophy (~850 CE)
    (fetch_internet_archive, "Al-Kindi first philosophy",
     "al_kindi_first_philosophy", "west", 850),

    # ── 900–1000 CE ───────────────────────────────────────────────────────────
    # EAST
    # Genshin — Ojoyoshu (~985 CE) / Pure Land Buddhism Japan
    (fetch_internet_archive, "Pure Land Buddhism Japan Amida",
     "genshin_ojoyoshu", "east", 985),
    # WEST
    # Al-Farabi — Opinions of the Inhabitants of the Virtuous City (~940 CE)
    (fetch_internet_archive, "Al-Farabi virtuous city",
     "al_farabi_virtuous_city", "west", 940),
    # Avicenna — Book of Healing (~1020 CE — started ~1000 CE)
    (fetch_internet_archive, "Avicenna Canon Medicine philosophy",
     "avicenna_book_of_healing", "west", 1020),

    # ── 1000–1100 CE ──────────────────────────────────────────────────────────
    # EAST
    # Ramanuja — Sri Bhasya / Vedarthasangraha (~1017–1137 CE)
    (fetch_internet_archive, "Ramanuja Vedarthasangraha",
     "ramanuja_vedarthasangraha", "east", 1100),
    # WEST
    # Anselm — Proslogion (~1077 CE) + Cur Deus Homo (~1098 CE)
    (fetch_internet_archive, "Anselm Proslogion Cur Deus Homo",
     "anselm_proslogion_cur_deus", "west", 1090),
    # Al-Ghazali — Incoherence of the Philosophers (~1095 CE)
    (fetch_internet_archive, "Al-Ghazali Tahafut incoherence philosophers",
     "al_ghazali_incoherence", "west", 1095),

    # ── 1100–1200 CE ──────────────────────────────────────────────────────────
    # EAST
    # I Ching / Yi Jing — Legge translation (SBE Vol 16, 1882), PD
    # Zhu Xi's Neo-Confucian school centred on commentary of I Ching; unique text not yet covered
    (fetch_internet_archive, "I Ching Legge",
     "i_ching_legge", "east", 1175),
    # WEST
    # Averroes — Incoherence of the Incoherence (~1180 CE)
    (fetch_internet_archive, "Averroes Tahafut incoherence",
     "averroes_tahafut", "west", 1180),
    # Maimonides — Guide for the Perplexed (~1190 CE)
    (fetch_internet_archive, "Guide for the Perplexed Maimonides Friedlander",
     "maimonides_guide_perplexed", "west", 1190),

    # ── 1200–1300 CE ──────────────────────────────────────────────────────────
    # EAST
    # Dogen — Shobogenzo (~1231–1253 CE) — modern translations are copyright; use older essays
    (fetch_internet_archive, "Dogen Soto Zen essays",
     "dogen_shobogenzo", "east", 1250),
    # Nichiren — Anesaki "Nichiren, the Buddhist Prophet" (1916) — PD, contains translations
    (fetch_internet_archive, "Nichiren Buddhist prophet Anesaki",
     "nichiren_writings", "east", 1270),
    # WEST
    # Thomas Aquinas — Summa Theologica (~1265–1274 CE)
    (fetch_internet_archive, "Summa Theologica Aquinas",
     "aquinas_summa_theologica", "west", 1270),

    # ── 1300–1400 CE ──────────────────────────────────────────────────────────
    # EAST
    # Aston — History of Japanese Literature (~1899, PD) — contains Kenko and other medieval texts
    # Kenko's Essays in Idleness: all English translations are post-1923 (restricted on IA)
    (fetch_internet_archive, "History Japanese literature Aston",
     "kenko_essays_idleness", "east", 1330),
    # WEST
    # Dante — Divine Comedy (~1320 CE) — Cary translation
    (fetch_gutenberg_id, 8800, "dante_divine_comedy_cary", "west", 1320),
    # Meister Eckhart — Sermons (~1300–1327 CE)
    (fetch_internet_archive, "Meister Eckhart sermons Evans",
     "meister_eckhart_sermons", "west", 1310),
    # Julian of Norwich — Revelations of Divine Love (~1395 CE)
    (fetch_gutenberg_search, "Julian Norwich Revelations Divine Love",
     "julian_norwich_revelations", "west", 1395),

    # ── 1400–1500 CE ──────────────────────────────────────────────────────────
    # EAST
    # Kabir — Songs and Poems (~1440–1518 CE) — Tagore translation (1915), public domain
    (fetch_internet_archive, "Kabir Tagore poems",
     "kabir_songs_tagore", "east", 1480),
    # WEST
    # Thomas à Kempis — Imitation of Christ (~1418 CE)
    (fetch_gutenberg_id, 1653, "thomas_kempis_imitation_christ", "west", 1418),
    # Nicholas of Cusa — On Learned Ignorance (~1440 CE)
    (fetch_internet_archive, "Nicholas Cusa learned ignorance",
     "nicholas_cusa_learned_ignorance", "west", 1440),

    # ── 1500–1600 CE ──────────────────────────────────────────────────────────
    # EAST
    # Wang Yangming — Instructions for Practical Living (~1518 CE)
    (fetch_internet_archive, "Wang Yangming instructions",
     "wang_yangming_instructions", "east", 1518),
    # WEST
    # Erasmus — Praise of Folly (~1509 CE)
    (fetch_gutenberg_id, 9371, "erasmus_praise_of_folly", "west", 1509),
    # Thomas More — Utopia (~1516 CE)
    (fetch_gutenberg_id, 2130, "more_utopia", "west", 1516),
    # Machiavelli — The Prince (~1513 CE)
    (fetch_gutenberg_id, 1232, "machiavelli_prince", "west", 1513),
    # Montaigne — Essays (~1580–1588 CE)
    (fetch_gutenberg_search, "Montaigne",
     "montaigne_essays", "west", 1580),

    # ── 1600–1700 CE ──────────────────────────────────────────────────────────
    # EAST
    # Bankei Yotaku — Zen talks / Unborn Dharma (~1650–1690 CE)
    (fetch_internet_archive, "Bankei unborn Zen",
     "bankei_unborn_zen", "east", 1690),
    # WEST
    # Descartes — Discourse on Method (~1637 CE)
    (fetch_gutenberg_id, 59, "descartes_discourse_method", "west", 1637),
    # Hobbes — Leviathan (~1651 CE)
    (fetch_gutenberg_id, 3207, "hobbes_leviathan", "west", 1651),
    # Spinoza — Ethics (~1677 CE)
    (fetch_gutenberg_id, 3800, "spinoza_ethics", "west", 1677),
    # Pascal — Pensées (~1670 CE)
    (fetch_gutenberg_search, "Pascal",
     "pascal_pensees", "west", 1670),
    # Locke — Essay Concerning Human Understanding (~1689 CE)
    (fetch_gutenberg_id, 10615, "locke_essay_human_understanding", "west", 1689),

    # ── 1700–1800 CE ──────────────────────────────────────────────────────────
    # EAST
    # D.T. Suzuki — Outlines of Mahayana Buddhism (1907) — public domain
    # Hakuin translations are copyright; using Suzuki's 1907 overview of Zen/Mahayana philosophy
    (fetch_internet_archive, "Outlines Mahayana Buddhism Suzuki 1907",
     "suzuki_essays_zen", "east", 1750),
    # WEST
    # Berkeley — Principles of Human Knowledge (~1710 CE)
    (fetch_gutenberg_id, 4723, "berkeley_principles_human_knowledge", "west", 1710),
    # Hume — Treatise of Human Nature (~1739 CE)
    (fetch_gutenberg_id, 4705, "hume_treatise_human_nature", "west", 1739),
    # Hume — Enquiry Concerning Human Understanding (~1748 CE)
    (fetch_gutenberg_id, 9662, "hume_enquiry_human_understanding", "west", 1748),
    # Adam Smith — Theory of Moral Sentiments (~1759 CE)
    (fetch_gutenberg_search, "Adam Smith Theory Moral Sentiments",
     "adam_smith_moral_sentiments", "west", 1759),
    # Kant — Critique of Pure Reason (~1781 CE)
    (fetch_gutenberg_id, 4280, "kant_critique_pure_reason", "west", 1781),

    # ── 1800–1900 CE ──────────────────────────────────────────────────────────
    # EAST
    # Swami Vivekananda — Complete Works (~1893–1902 CE)
    (fetch_internet_archive, "Vivekananda complete works",
     "vivekananda_complete_works", "east", 1890),
    # Sri Ramakrishna — Gospel of Ramakrishna (~1882 CE)
    (fetch_internet_archive, "Gospel Ramakrishna Nikhilananda",
     "gospel_ramakrishna", "east", 1882),
    # WEST
    # Hegel — Phenomenology of Spirit (~1807 CE)
    (fetch_internet_archive, "Hegel Phenomenology Spirit Miller",
     "hegel_phenomenology_spirit", "west", 1807),
    # Schopenhauer — World as Will and Representation (~1818 CE)
    (fetch_gutenberg_id, 38427, "schopenhauer_world_will_representation", "west", 1818),
    # John Stuart Mill — Utilitarianism (~1863 CE)
    (fetch_gutenberg_id, 11224, "mill_utilitarianism", "west", 1863),
    # Nietzsche — Beyond Good and Evil (~1886 CE)
    (fetch_gutenberg_id, 4363, "nietzsche_beyond_good_evil", "west", 1886),
    # William James — Varieties of Religious Experience (~1902 CE)
    (fetch_gutenberg_search, "William James varieties religious experience",
     "james_varieties_religious_experience", "west", 1902),
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
    return p.parse_args()


def _parse_entry(entry: tuple) -> tuple:
    """Unpack a SOURCES entry into (fn, fn_args, label, region, year).

    Expected tuple format: (fn, *fn_args, label, region, year)
      - year   is always an int (the last element)
      - region is always "east" or "west" (second-to-last)
      - label  is always a str (third-to-last)
    """
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
        sources = [s for s in SOURCES if _parse_entry(s)[2] == args.label]
        if not sources:
            print(f"No source found with label '{args.label}'")
            return

    if args.dry_run:
        print(f"{'FETCHER':<30} {'LABEL':<40} {'REGION':<6} {'YEAR':<8} FOLDER")
        print("-" * 105)
        for entry in sources:
            fn, fn_args, label, region, year = _parse_entry(entry)
            folder = get_folder_path(label, region, year).relative_to(DATA_DIR)
            print(f"  {fn.__name__:<28} {label:<40} {region:<6} {year:<8} {folder}")
        print(f"\n{len(sources)} source(s) listed.")
        return

    print(f"Output directory: {DATA_DIR.resolve()}\n")
    ok = fail = 0
    for entry in sources:
        fn, fn_args, label, region, year = _parse_entry(entry)
        print(f"Fetching: {label}")
        try:
            success = fn(*fn_args, label, region, year=year)
        except Exception as exc:
            print(f"  [ERROR] {label}: {exc}")
            success = False
        if success:
            ok += 1
        else:
            fail += 1
        time.sleep(DELAY)

    print(f"\nDone. {ok} succeeded, {fail} failed.")
    for region_dir in (EAST_DIR, WEST_DIR):
        files = sorted(region_dir.rglob("*.txt"))
        if files:
            print(f"\nFiles in {region_dir}/:")
            for f in files:
                print(f"  {str(f.relative_to(region_dir)):<60} {f.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()
