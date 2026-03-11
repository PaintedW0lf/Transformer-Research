"""download_pretraining_data.py

Downloads public-domain philosophical and religious texts for LLM pretraining.

Sources:
  - Project Gutenberg      (direct .txt download by ID; gutendex.com API for search)
  - Internet Archive       (advancedsearch JSON API + metadata + download)
  - sacred-texts.com       (HTML scraping + subpage traversal)
  - SuttaCentral           (JSON bilara-data API)
  - Access to Insight      (HTML scraping)

Output: data/<label>.txt  (one file per source, UTF-8, normalised whitespace)

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
        and latin_alpha_ratio >= 0.90
        and stopword_ratio >= 0.04
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


def _save(label: str, text: str, region: str = "west") -> None:
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
    folder = EAST_DIR if region == "east" else WEST_DIR
    out = folder / f"{label}.txt"
    out.write_text(text, encoding="utf-8")
    kb = len(text.encode()) // 1024
    print(f"  [OK]   {out.relative_to(DATA_DIR)}  ({kb} KB)")


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

def fetch_gutenberg_id(book_id: int, label: str, region: str = "west") -> bool:
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
            _save(label, text, region)
            return True
        time.sleep(DELAY)
    print(f"  [FAIL] Gutenberg #{book_id} ({label})")
    return False


def fetch_gutenberg_search(query: str, label: str, region: str = "west") -> bool:
    """
    Search Project Gutenberg via the gutendex.com JSON API and download
    the first plain-text result.
    """
    api_url = f"https://gutendex.com/books/?search={quote_plus(query)}"
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
            _save(label, text, region)
            return True

    print(f"  [FAIL] Gutendex '{query}' ({label}): no downloadable text found")
    return False


def fetch_internet_archive(query: str, label: str, region: str = "west", max_candidates: int = 8) -> bool:
    """
    Search IA with the advancedsearch JSON API, then download the first
    result that has a .txt file (prefers plain text over djvu.txt).
    Skips items that return 401/403 or exceed IA_MAX_MB.
    """
    search_url = (
        "https://archive.org/advancedsearch.php"
        f"?q={quote_plus(query)}+mediatype:texts+language:English"
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

            _save(label, dr.text, region)
            return True

    print(f"  [FAIL] IA '{query}' ({label}): no accessible text file found")
    return False


def fetch_sacred_texts(index_url: str, label: str, region: str = "west", max_subpages: int = 80) -> bool:
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

    _save(label, "\n\n".join(chunks), region)
    return True


def fetch_access_to_insight(root_url: str, label: str, region: str = "east", max_suttas: int = 400) -> bool:
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

    _save(label, "\n\n".join(chunks), region)
    return True


def fetch_suttacentral(nikaya: str, label: str, region: str = "east", translator: str = "sujato") -> bool:
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

    _save(label, "\n\n".join(chunks), region)
    return True


# ---------------------------------------------------------------------------
# Source catalogue
# ---------------------------------------------------------------------------
# Each entry: (fetcher_fn, *args_for_fetcher, label_str)
# The last positional arg is always the output label.

SOURCES: list[tuple] = [

    # ── INDIA: Upanishads ─────────────────────────────────────────────────
    # SBE Vol 15 (Müller) contains both Brihadaranyaka and Chandogya
    (fetch_gutenberg_id, 2034, "upanishads_muller_sbe15", "east"),

    # ── INDIA: Pali Canon ─────────────────────────────────────────────────
    # Rhys Davids — Dialogues of the Buddha (PG #38399)
    (fetch_gutenberg_id, 38399, "pali_dialogues_rhys_davids", "east"),
    # Rhys Davids — Buddhist Suttas (PG #2051)
    (fetch_gutenberg_id, 2051, "pali_rhys_davids_pg", "east"),
    # Thanissaro Bhikkhu — Access to Insight (open license)
    (fetch_access_to_insight,
     "https://www.accesstoinsight.org/tipitaka/",
     "pali_thanissaro_ati"),   # region defaults to "east" in the function
    # SuttaCentral — Sujato translation (CC0)
    (fetch_suttacentral, "dn",  "pali_dn_sujato"),   # region defaults to "east"
    (fetch_suttacentral, "mn",  "pali_mn_sujato"),
    (fetch_suttacentral, "sn",  "pali_sn_sujato"),
    (fetch_suttacentral, "an",  "pali_an_sujato"),
    (fetch_suttacentral, "dhp", "pali_dhp_sujato"),
    (fetch_suttacentral, "kn",  "pali_kn_sujato"),

    # ── CHINA: Analects ───────────────────────────────────────────────────
    (fetch_gutenberg_id, 3330, "analects_legge", "east"),
    (fetch_internet_archive, "Analects of Confucius Soothill",
     "analects_soothill", "east"),

    # ── CHINA: Mencius ────────────────────────────────────────────────────
    (fetch_gutenberg_id, 38406, "mencius_legge", "east"),
    (fetch_internet_archive, "Mencius Jennings",
     "mencius_jennings", "east"),

    # ── CHINA: Tao Te Ching ───────────────────────────────────────────────
    (fetch_gutenberg_id, 216, "tao_te_ching_legge", "east"),
    # Waley is login-restricted; use Paul Carus open edition from sacred-texts
    (fetch_sacred_texts,
     "https://www.sacred-texts.com/tao/taote.htm",
     "tao_te_ching_carus", "east"),

    # ── CHINA: Zhuangzi ───────────────────────────────────────────────────
    (fetch_gutenberg_id, 29724, "zhuangzi_legge", "east"),
    (fetch_internet_archive, "Chuang Tzu Giles",
     "zhuangzi_giles", "east"),

    # ── CHINA: Mozi ───────────────────────────────────────────────────────
    (fetch_internet_archive, "Mo Tzu ethical works",
     "mozi_mei", "east"),

    # ── WEST: Pre-Socratics ───────────────────────────────────────────────
    # Burnet — Early Greek Philosophy (Heraclitus, Parmenides, Empedocles …)
    (fetch_gutenberg_search, "Early Greek Philosophy Burnet", "pre_socratics_burnet"),
    (fetch_internet_archive, "Fairbanks handbook Greek philosophy",
     "pre_socratics_fairbanks"),

    # ── WEST: Plato ───────────────────────────────────────────────────────
    # Known Gutenberg IDs (Jowett translations)
    (fetch_gutenberg_id, 1497, "plato_republic_jowett"),
    (fetch_gutenberg_id, 1658, "plato_phaedo_jowett"),
    (fetch_gutenberg_id, 1600, "plato_symposium_jowett"),
    (fetch_gutenberg_id, 1656, "plato_apology_jowett"),
    (fetch_gutenberg_id, 1672, "plato_gorgias_jowett"),
    (fetch_gutenberg_id, 1735, "plato_theaetetus_jowett"),
    (fetch_gutenberg_id, 1572, "plato_timaeus_jowett"),
    (fetch_internet_archive, "Plato dialogues Jowett",
     "plato_ia_jowett"),

    # ── WEST: Aristotle ───────────────────────────────────────────────────
    # Known Gutenberg IDs for Aristotle
    (fetch_gutenberg_id, 8438,  "aristotle_nicomachean_ethics"),
    (fetch_gutenberg_id, 12236, "aristotle_metaphysics"),
    (fetch_gutenberg_id, 6762,  "aristotle_politics"),
    # Physics — not on Gutendex; use IA
    (fetch_internet_archive, "Aristotle Physics natural science",
     "aristotle_physics"),
    (fetch_internet_archive, "Aristotle De Anima On the Soul translation",
     "aristotle_de_anima"),

    # ── PERSIA: Avesta ────────────────────────────────────────────────────
    # Darmesteter — sacred-texts.com (SBE Vol 4 = Vendidad, Vol 23 = Yasts + Gathas)
    (fetch_sacred_texts,
     "https://www.sacred-texts.com/zor/sbe04/index.htm",
     "avesta_darmesteter_vol4"),
    (fetch_sacred_texts,
     "https://www.sacred-texts.com/zor/sbe23/index.htm",
     "avesta_darmesteter_vol23"),
    (fetch_internet_archive, "Avesta Mills Zend",
     "avesta_mills"),
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


def main() -> None:
    args = _parse_args()

    sources = SOURCES
    if args.label:
        sources = [s for s in SOURCES if s[-1] == args.label]
        if not sources:
            print(f"No source found with label '{args.label}'")
            return

    def _label_of(rest: list) -> str:
        """Extract label from a SOURCES rest-args list.
        Region ("east"/"west") may appear as the last positional arg after label."""
        if rest and rest[-1] in ("east", "west"):
            return rest[-2]
        return rest[-1]

    if args.dry_run:
        print(f"{'FETCHER':<30} {'LABEL':<40} {'REGION'}")
        print("-" * 75)
        for entry in sources:
            fn, *rest = entry
            label = _label_of(rest)
            region = rest[-1] if rest[-1] in ("east", "west") else "default"
            print(f"  {fn.__name__:<28} {label:<40} {region}")
        print(f"\n{len(sources)} source(s) listed.")
        return

    print(f"Output directory: {DATA_DIR.resolve()}\n")
    ok = fail = 0
    for entry in sources:
        fn, *rest = entry
        label = _label_of(rest)
        print(f"Fetching: {label}")
        try:
            success = fn(*rest)
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
        files = sorted(region_dir.glob("*.txt"))
        if files:
            print(f"\nFiles in {region_dir}/:")
            for f in files:
                print(f"  {f.name:<55} {f.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()
