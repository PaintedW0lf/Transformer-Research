# Pretraining Source List — Rationale & Gaps

## Purpose

This document explains why the texts in `download_pretraining_data.py` were chosen,
what principles guided the selection, and where the list has known gaps.

---

## Selection Criteria

### 1. Public Domain / Open Access

Every source must be freely and legally downloadable. This limits the list to:

- Works published before 1928 (US public-domain threshold) or with no copyright.
- Translations completed before 1928, or released under CC0 / open licenses
  (e.g., Bhikkhu Sujato's SuttaCentral translations, Thanissaro Bhikkhu's
  Access to Insight corpus).
- Hosted on Project Gutenberg, Internet Archive, Sacred-Texts.com, or SuttaCentral.

### 2. English Only

The model is trained on English text. All sources are English translations or,
where the original is English (Hobbes, Hume, Locke, etc.), the original text.
Three enforcement layers are in place:

- Internet Archive searches include `language:English` in the query.
- Gutendex (Gutenberg) searches include `&languages=en`.
- A post-download heuristic (`_is_probably_english`) rejects any file that
  falls below ASCII-ratio, Latin-alpha-ratio, and stop-word-ratio thresholds.

### 3. Philosophical or Religious Content

The list is limited to texts whose primary purpose is philosophical inquiry,
theological doctrine, ethical teaching, or mystical/spiritual instruction.
Excluded categories include: chronicles and histories, travel literature,
literary fiction, encyclopedias, and natural science.

### 4. Temporal and Geographic Coverage

Texts are arranged in 100-year intervals from ≥1200 BCE to ~1900 CE across
two broad regions:

| Region | Traditions covered |
|---|---|
| **East** | Indian (Vedic, Buddhist, Jain-adjacent, Bhakti), Chinese (Confucian, Taoist, Chan/Zen), Japanese (Zen, Pure Land, Esoteric) |
| **West** | Greek, Roman-Stoic, Early Christian, Islamic Falsafa, Jewish philosophy, European Scholastic, Early Modern, German Idealist |

The goal is a roughly even temporal spread so that no century is absent from
at least one region, giving the model exposure to how philosophical language
and concerns evolved over time.

### 5. Translation Quality

Where multiple translations exist, preference is given to translations by
named scholars whose work has scholarly standing (e.g., Jowett for Plato,
Rhys Davids for Pali Canon, MacKenna for Plotinus, Chan Wing-tsit for
neo-Confucian texts). This reduces the risk of downloading amateur or
machine-generated translations from the Internet Archive.

---

## Why Each Period Was Included

### BCE Texts (the "older (BC)" folder)

These are the foundational texts of both traditions — Upanishads, Pali Canon,
Confucian classics, Taoist canon, Pre-Socratics, Plato, Aristotle, and the
Avesta. They establish the conceptual vocabulary that later centuries build on.
Heavy coverage here reflects their outsized influence.

### 0–500 CE

The formative period of major world religions as textual traditions:
Mahayana Buddhism crystallises (Nagarjuna, Ashvaghosha, Vasubandhu),
Stoicism produces its literary peak (Seneca, Marcus Aurelius, Epictetus),
Neoplatonism emerges (Plotinus), and Christianity develops its theological
framework (Origen, Augustine, Eusebius, Jerome, Boethius).

### 500–1000 CE

Transmission and synthesis. Buddhism spreads into East Asia and Japan
(Platform Sutra, Shantideva, Kukai). Islamic philosophy begins (Al-Kindi,
Al-Farabi, Avicenna). Christian monasticism codifies (Benedict's Rule).
The Quran provides the foundation of Islamic thought. Eriugena bridges
Greek and Christian metaphysics in the Latin West.

### 1000–1300 CE

High scholasticism in both traditions. Neo-Confucianism matures (Zhu Xi).
Islamic philosophy peaks and is challenged from within (Al-Ghazali,
Averroes). Jewish philosophy engages Greek thought (Maimonides). Latin
scholasticism culminates (Anselm, Aquinas). Zen philosophy develops
its distinctive voice (Dogen).

### 1300–1600 CE

Mysticism, humanism, and reform. Christian mysticism deepens (Eckhart,
Julian of Norwich, Thomas à Kempis, Nicholas of Cusa). Bhakti poetry
bridges devotion and philosophy (Kabir). Neo-Confucian moral psychology
is refined (Wang Yangming). Renaissance humanism emerges in the West
(Erasmus, More, Montaigne, Machiavelli). Japanese Zen matures (Muso Soseki).

### 1600–1900 CE

The modern era. Western rationalism and empiricism lay the groundwork for
secular philosophy (Descartes, Hobbes, Spinoza, Locke, Hume, Berkeley, Kant,
Hegel, Schopenhauer, Nietzsche, Mill). Zen philosophy shifts toward a more
accessible, experiential teaching style (Bankei, Hakuin). The Hindu reform
movement produces systematic English-language philosophy for the first time
(Vivekananda). William James bridges philosophy and the study of religion.

---

## Known Gaps

### Major Traditions with Insufficient Coverage

| Gap | Reason | Possible fix |
|---|---|---|
| **Jainism** | Tattvartha Sutra and Agamas rarely available in quality English translations pre-1928 | Check IA for Jacobi SBE volumes (Vol. 22, 45) |
| **Sikhism** | Guru Granth Sahib full English translation (Sant Singh Khalsa) is modern | Use partial extracts from IA open editions |
| **Tibetan Buddhism** | Milarepa, Tsongkhapa, Longchenpa translations are mostly post-1928 | Seek W.Y. Evans-Wentz translations (1920s) from IA |
| **Sufism** | Rumi, Ibn Arabi, Al-Hallaj translations of scholarly quality are mostly post-1928 | R.A. Nicholson translations (early 1900s) may be available on IA |
| **Zoroastrian later texts** | Bundahishn, Denkard only partially on IA in English | Extend Avesta entries with SBE Vol. 5, 18, 37 (West/Darmesteter) |
| **Jewish texts** | Talmud (Soncino), Zohar, Kabbalistic tradition missing | Soncino Talmud is copyright; seek Rodkinson partial translation (IA) |
| **Korean Buddhism** | Wonhyo, Chinul absent | IA has limited English; BDK English Tripitaka may have some |
| **African philosophy** | Entirely absent | Mostly oral tradition; few pre-1928 scholarly English compilations exist |
| **Mesoamerican** | Popol Vuh, Aztec cosmological texts absent | Spence's "Myths of Mexico and Peru" (PG) is a partial entry point |
| **Ancient Egypt / Mesopotamia** | Book of the Dead, Instructions of Ptahhotep, Epic of Gilgamesh missing | All are on Gutenberg / IA in pre-1928 translations |

### Periods with Thin East Coverage

- **600–700 CE**: No East entry. Dharmakirti's logic texts (epistemology) and
  early Hua-yen texts are candidates but quality English translations are scarce
  pre-1928.
- **800–900 CE**: Only Kukai. Zhanran and Mazu Daoyi (Chan) lack accessible
  English translations from this era.
- **1700–1800 CE**: Only Hakuin for East. Japanese Confucian scholars
  (Ogyu Sorai, Motoori Norinaga) have limited pre-1928 English translations.

### Female Philosophers

The list is overwhelmingly male. Documented exceptions where texts are accessible:

| Author | Work | Approx. date |
|---|---|---|
| Hildegard of Bingen | *Scivias* (~1151 CE) | 1100–1200 CE |
| Julian of Norwich | *Revelations of Divine Love* (~1395 CE) | already included |
| Teresa of Ávila | *Interior Castle* (~1577 CE) | 1500–1600 CE |
| Mirabai | devotional poems (~1498–1547 CE) | 1500–1600 CE |

Hildegard's *Scivias* and Teresa of Ávila's *Interior Castle* are strong
candidates for inclusion and have IA-accessible English translations.

### Post-1900 CE

The list stops at ~1900 CE. Major 20th-century philosophers
(Heidegger, Wittgenstein, Whitehead, Nishida Kitaro, Nishitani Keiji,
Aurobindo) are mostly under copyright. Exceptions to investigate:

- Sri Aurobindo, *The Life Divine* (1914–19, IA may have open editions)
- Nishida Kitaro, *An Inquiry into the Good* (1911, some translations may be
  open access)

---

## Source Reliability Notes

- **Project Gutenberg IDs** are fixed and version-stable; the safest source.
- **Internet Archive** quality varies significantly. The `language:English`
  filter and `_is_probably_english` heuristic mitigate OCR garbage and
  non-English scans, but a manual spot-check of downloaded files is recommended
  before training.
- **Sacred-Texts.com** is consistent and well-formatted for pre-1928 texts
  but the HTML scraper strips minimal markup; tables and verse numbering are lost.
- **SuttaCentral** (Sujato translations) is the highest-quality source for
  the Pali Canon: CC0, modern English, structured JSON. Recommended to verify
  the bilara API endpoint remains active before each training run.
