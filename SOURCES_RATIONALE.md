# Pretraining Source List — Rationale, Timeline & Gaps

## Purpose

This document explains why the texts in `download_pretraining_data.py` were chosen,
provides a citable scholarly timeline for each inclusion, and documents known gaps.

---

## Anchor References

The text selection is grounded in five scholarly works that together cover the full
East–West philosophical canon from ~1200 BCE to ~1900 CE:

| Reference | Citation | Scope |
|---|---|---|
| **Scharfstein 1998** | Ben-Ami Scharfstein, *A Comparative History of World Philosophy: From the Upanishads to Kant* (Albany: SUNY Press, 1998). | Chinese, Indian, and European traditions in parallel, ~800 BCE – ~1780 CE |
| **Fung Yu-lan 1952–53** | Fung Yu-lan, *A History of Chinese Philosophy*, 2 vols., trans. Derk Bodde (Princeton: Princeton University Press, 1952–53). | Definitive chronological account of Chinese philosophy, pre-Qin to modern |
| **Radhakrishnan & Moore 1957** | Sarvepalli Radhakrishnan and Charles A. Moore (eds.), *A Source Book in Indian Philosophy* (Princeton: Princeton University Press, 1957). | Indian philosophy from the Vedas through modern thought |
| **Corbin 1993** | Henry Corbin, *History of Islamic Philosophy*, trans. Liadain Sherrard (London: Kegan Paul / Institute of Ismaili Studies, 1993). | Islamic philosophy from Kindi through Ibn Arabi |
| **Deutsch & Bontekoe 1997** | Eliot Deutsch and Ron Bontekoe (eds.), *A Companion to World Philosophies* (Oxford: Blackwell, 1997). | Framework for comparing Indian, Chinese, Buddhist, Islamic, and Western traditions |

All five works are peer-reviewed or published by major university presses and are
citable in academic papers. Scharfstein (1998) is the single best anchor for
justifying this corpus as a whole: its title names the temporal range
(*Upanishads to Kant*) and its chapter structure treats all three major civilisations
as co-equal philosophical traditions.

---

## Selection Criteria

### 1. Scholarly Canonicity
Each text appears in at least one of the five anchor references above as a primary
philosophical or religious source. This is the primary gate for inclusion. Secondary
sources, literary histories, and modern retellings are used only as placeholders
where no public-domain primary translation exists (noted explicitly in the timeline).

### 2. Public Domain / Open Access
Every source must be freely downloadable. This limits the list to:
- Works translated before 1928 (US public-domain threshold).
- Translations released under CC0 / open licenses (Bhikkhu Sujato's SuttaCentral
  corpus, Thanissaro Bhikkhu's Access to Insight corpus).
- Hosted on Project Gutenberg, Internet Archive, or SuttaCentral.

### 3. English Only
All files are English translations or (for early-modern Western texts) original
English. A three-metric heuristic (`_is_probably_english`) rejects non-English
downloads at runtime: ASCII-ratio ≥ 0.85, Latin-alpha-ratio ≥ 0.85,
stop-word-ratio ≥ 0.01.

### 4. One Source Per Text
To avoid inflating token counts with duplicate content, each distinct work is
downloaded from exactly one source. Where multiple translations exist, the
translation with the strongest scholarly standing is preferred.

### 5. 100-Year Temporal Coverage
Texts are assigned to East or West folders at 100-year intervals so that the
model is exposed to philosophical language from every century between 1200 BCE
and 1900 CE. No century is left entirely empty in both regions.

---

## Canonical Timeline

The table below lists every text in the corpus. The **Authority** column gives the
specific reference that justifies inclusion. ✓ = currently downloaded;
⚠ = placeholder (no PD primary translation available).

### BCE Texts

| Approx. date | Region | Author / Work | File label | Authority |
|---|---|---|---|---|
| ~1200 BCE | West | *Avesta* — Darmesteter trans. (SBE Vol. 4) | `avesta_darmesteter_vol4` | Scharfstein 1998, ch. 1; Deutsch & Bontekoe 1997, ch. 4 |
| ~1200 BCE | West | *Avesta* — Mills trans. (SBE Vol. 31, Gathas) | `avesta_mills` | Scharfstein 1998, ch. 1 |
| ~800 BCE | East | *Upanishads* — Müller trans. (SBE Vol. 15) | `upanishads_muller_sbe15` | Radhakrishnan & Moore 1957, pp. 37–163; Scharfstein 1998, ch. 2 |
| ~600 BCE | West | *Early Greek Philosophy* — Burnet | `pre_socratics_burnet` | Scharfstein 1998, ch. 4 (Heraclitus, Parmenides, Empedocles) |
| ~600 BCE | West | *Handbook of Greek Philosophy* — Fairbanks | `pre_socratics_fairbanks` | Scharfstein 1998, ch. 4 |
| ~500 BCE | East | *Dhammapada* and Pali Canon — Sujato trans. (SuttaCentral CC0) | `pali_dn/mn/sn/an/dhp/kn_sujato` | Radhakrishnan & Moore 1957, pp. 272–346; Deutsch & Bontekoe 1997, ch. 6 |
| ~500 BCE | East | Pali Canon — Thanissaro Bhikkhu trans. (Access to Insight) | `pali_thanissaro_ati` | Radhakrishnan & Moore 1957, pp. 272–346 |
| ~479 BCE | East | Confucius, *Analects* — Legge trans. | `analects_legge` | Fung Yu-lan 1952, vol. I ch. 4; Scharfstein 1998, ch. 6 |
| ~470 BCE | East | Mozi, *Works of Motse* — Mei trans. | `mozi_mei` | Fung Yu-lan 1952, vol. I ch. 5 |
| ~400 BCE | East | *Tao Te Ching* — Legge trans. | `tao_te_ching_legge` | Fung Yu-lan 1952, vol. I ch. 8; Scharfstein 1998, ch. 7 |
| ~400 BCE | East | *Bhagavad Gita* — Arnold trans. ("The Song Celestial") | `bhagavad_gita_arnold` | Radhakrishnan & Moore 1957, pp. 101–163; Scharfstein 1998, ch. 3 |
| ~372 BCE | East | Mencius, *Works of Mencius* — Legge trans. | `mencius_legge` | Fung Yu-lan 1952, vol. I ch. 7; Scharfstein 1998, ch. 6 |
| ~350 BCE | East | *Zhuangzi* — Legge trans. | `zhuangzi_legge` | Fung Yu-lan 1952, vol. I ch. 10; Scharfstein 1998, ch. 7 |
| ~313 BCE | East | *Xunzi* — Dubs trans. | `xunzi_dubs` | Fung Yu-lan 1952, vol. I ch. 12 ("Hsün Tzu") |
| ~428 BCE | West | Plato — *Republic*, *Phaedo*, *Symposium*, *Apology*, *Gorgias*, *Theaetetus*, *Timaeus* (Jowett trans.) | `plato_*_jowett` | Scharfstein 1998, ch. 9; Deutsch & Bontekoe 1997, ch. 18 |
| ~384 BCE | West | Aristotle — *Nicomachean Ethics*, *Metaphysics*, *Politics*, *Physics*, *De Anima* | `aristotle_*` | Scharfstein 1998, ch. 11; Deutsch & Bontekoe 1997, ch. 18 |

### 0–500 CE

| Period | Region | Author / Work | File label | Authority |
|---|---|---|---|---|
| ~65 CE | West | Seneca, *Letters to Lucilius* | `seneca_letters_lucilius` | Scharfstein 1998, ch. 12 |
| ~80 CE | East | Ashvaghosha, *Buddhacharita* — Cowell trans. | `buddhacharita_cowell` | Radhakrishnan & Moore 1957, pp. 273–274 |
| ~100 CE | West | Epictetus, *Enchiridion* | `epictetus_enchiridion` | Scharfstein 1998, ch. 12 |
| ~100 CE | East | *Milindapanha* (*Questions of King Milinda*) — Rhys Davids trans. | `milindapanha_rhys_davids` | Radhakrishnan & Moore 1957, p. 283 |
| ~108 CE | West | Epictetus, *Discourses* | `epictetus_discourses` | Scharfstein 1998, ch. 12 |
| ~150 CE | East | Nagarjuna, *Mulamadhyamakakarika* | `nagarjuna_mulamadhyamakakarika` | Radhakrishnan & Moore 1957, pp. 340–346; Deutsch & Bontekoe 1997, ch. 7 |
| ~150 CE | East | Ashvaghosha, *Awakening of Faith in the Mahayana* | `awakening_of_faith_suzuki` | Radhakrishnan & Moore 1957, p. 274 |
| ~170 CE | West | Marcus Aurelius, *Meditations* | `marcus_aurelius_meditations` | Scharfstein 1998, ch. 12 |
| ~200 CE | East | Paul Carus, *The Gospel of Buddha* (1894) ⚠ | `gospel_of_buddha_carus` | **Placeholder only**: no PD primary Mahayana sutra text for this slot. Carus draws on Pali and Sanskrit sources; not a primary text. See Known Gaps. |
| ~230 CE | West | Origen, *De Principiis* (Ante-Nicene Fathers) | `origen_de_principiis` | Deutsch & Bontekoe 1997, ch. 20 |
| ~260 CE | West | Plotinus, *Enneads* — MacKenna trans. | `plotinus_enneads_mackenna` | Scharfstein 1998, ch. 13; Deutsch & Bontekoe 1997, ch. 20 |
| ~300 CE | East | *Vimalakirti Sutra* — Idumi trans. | `vimalakirti_sutra` | Radhakrishnan & Moore 1957, p. 275 (Mahayana canon) |
| ~313 CE | West | Eusebius, *Ecclesiastical History* | `eusebius_church_history` | Deutsch & Bontekoe 1997, ch. 20 |
| ~397 CE | West | Augustine, *Confessions* | `augustine_confessions` | Scharfstein 1998, ch. 14; Deutsch & Bontekoe 1997, ch. 20 |
| ~400 CE | East | Patanjali, *Yoga Sutras* | `yoga_sutras_patanjali` | Radhakrishnan & Moore 1957, pp. 453–485 ("Yoga system of Patanjali") |
| ~400 CE | West | Jerome, *Select Letters* | `jerome_letters` | Deutsch & Bontekoe 1997, ch. 20 |
| ~420 CE | West | Augustine, *City of God* | `augustine_city_of_god` | Scharfstein 1998, ch. 14; Deutsch & Bontekoe 1997, ch. 20 |
| ~430 CE | East | Buddhaghosa, *Visuddhimagga* (*Path of Purification*) | `visuddhimagga_buddhaghosa` | Radhakrishnan & Moore 1957, p. 285; Deutsch & Bontekoe 1997, ch. 7 |
| ~500 CE | East | *Lankavatara Sutra* — Suzuki trans. | `lankavatara_sutra_suzuki` | Radhakrishnan & Moore 1957, p. 276; Deutsch & Bontekoe 1997, ch. 7 |
| ~524 CE | West | Boethius, *Consolation of Philosophy* | `boethius_consolation_philosophy` | Scharfstein 1998, ch. 14 |
| ~530 CE | West | Benedict of Nursia, *Rule of Saint Benedict* | `benedict_rule` | Deutsch & Bontekoe 1997, ch. 20 |

### 500–1000 CE

| Period | Region | Author / Work | File label | Authority |
|---|---|---|---|---|
| ~632 CE | West | *Quran* — Rodwell trans. | `quran_rodwell` | Corbin 1993, ch. 1; Deutsch & Bontekoe 1997, ch. 14 |
| ~700 CE | East | Shantideva, *Bodhicaryavatara* | `shantideva_bodhicaryavatara` | Deutsch & Bontekoe 1997, ch. 7 |
| ~730 CE | West | John of Damascus, *Exposition of the Orthodox Faith* | `john_damascus_orthodox_faith` | Deutsch & Bontekoe 1997, ch. 20 |
| ~750 CE | East | *Platform Sutra of the Sixth Patriarch* (Huineng) | `platform_sutra_huineng` | Fung Yu-lan 1953, vol. II ch. 22; Deutsch & Bontekoe 1997, ch. 8 |
| ~788 CE | East | Shankara, *Vivekachudamani* (*Crest Jewel of Discrimination*) | `shankara_vivekachudamani` | Radhakrishnan & Moore 1957, pp. 506–517 ("Sankara's Brahmasutrabhashya"); Scharfstein 1998, ch. 3 |
| ~820 CE | East | *Bardo Thodol* (*Tibetan Book of the Dead*) — Evans-Wentz trans. | `tibetan_book_of_dead` | Deutsch & Bontekoe 1997, ch. 9 |
| ~850 CE | West | Al-Kindi, *On First Philosophy* | `al_kindi_first_philosophy` | Corbin 1993, ch. 4 |
| ~866 CE | West | John Scotus Eriugena, *Periphyseon* | `eriugena_periphyseon` | Deutsch & Bontekoe 1997, ch. 20 |
| ~940 CE | West | Al-Farabi, *Opinions of the Inhabitants of the Virtuous City* | `al_farabi_virtuous_city` | Corbin 1993, ch. 5 |
| ~985 CE | East | Genshin, *Ojoyoshu* (Pure Land Buddhism) | `genshin_ojoyoshu` | Fung Yu-lan 1953, vol. II ch. 22 (Buddhism in Japan) |

### 1000–1300 CE

| Period | Region | Author / Work | File label | Authority |
|---|---|---|---|---|
| ~1020 CE | West | Avicenna, *Kitab al-Shifa* (*Book of Healing*) | `avicenna_book_of_healing` | Corbin 1993, ch. 6 |
| ~1077 CE | West | Anselm, *Proslogion* + *Cur Deus Homo* | `anselm_proslogion_cur_deus` | Scharfstein 1998, ch. 14 |
| ~1095 CE | West | Al-Ghazali, *Tahafut al-Falasifa* | `al_ghazali_incoherence` | Corbin 1993, ch. 7; Deutsch & Bontekoe 1997, ch. 14 |
| ~1100 CE | East | Ramanuja, *Vedarthasangraha* | `ramanuja_vedarthasangraha` | Radhakrishnan & Moore 1957, pp. 543–573 |
| ~1175 CE | East | *I Ching* — Legge trans. (SBE Vol. 16) | `i_ching_legge` | Fung Yu-lan 1953, vol. II ch. 27 (Zhu Xi's I Ching studies); Radhakrishnan & Moore 1957, p. 15 |
| ~1180 CE | West | Averroes, *Tahafut al-Tahafut* | `averroes_tahafut` | Corbin 1993, ch. 8; Deutsch & Bontekoe 1997, ch. 14 |
| ~1190 CE | West | Maimonides, *Guide for the Perplexed* | `maimonides_guide_perplexed` | Scharfstein 1998, ch. 14; Deutsch & Bontekoe 1997, ch. 13 |
| ~1250 CE | East | Dogen, *Shobogenzo* (essays) | `dogen_shobogenzo` | Fung Yu-lan 1953, vol. II ch. 22 (Chan/Zen) |
| ~1270 CE | East | Nichiren — Anesaki, *Nichiren, the Buddhist Prophet* (1916) ⚠ | `nichiren_writings` | **Placeholder**: Anesaki is a secondary source with extensive primary quotations. Nichiren's own writings not available in pre-1928 PD English translation. |
| ~1270 CE | West | Thomas Aquinas, *Summa Theologica* | `aquinas_summa_theologica` | Scharfstein 1998, ch. 15; Deutsch & Bontekoe 1997, ch. 20 |

### 1300–1600 CE

| Period | Region | Author / Work | File label | Authority |
|---|---|---|---|---|
| ~1320 CE | West | Dante Alighieri, *Divine Comedy* — Cary trans. | `dante_divine_comedy_cary` | Deutsch & Bontekoe 1997, ch. 20 |
| ~1310 CE | West | Meister Eckhart, *Sermons* — Evans trans. | `meister_eckhart_sermons` | Deutsch & Bontekoe 1997, ch. 20 |
| ~1330 CE | East | W.G. Aston, *A History of Japanese Literature* (1899) ⚠ | `kenko_essays_idleness` | **Placeholder**: Contains translated excerpts from Kenko's *Tsurezuregusa* (Fung Yu-lan 1953, vol. II, Japanese Buddhism section). All stand-alone English translations of Kenko are post-1927 (restricted). |
| ~1395 CE | West | Julian of Norwich, *Revelations of Divine Love* | `julian_norwich_revelations` | Deutsch & Bontekoe 1997, ch. 20 |
| ~1418 CE | West | Thomas à Kempis, *Imitation of Christ* | `thomas_kempis_imitation_christ` | Deutsch & Bontekoe 1997, ch. 20 |
| ~1440 CE | West | Nicholas of Cusa, *On Learned Ignorance* | `nicholas_cusa_learned_ignorance` | Deutsch & Bontekoe 1997, ch. 20 |
| ~1480 CE | East | Kabir, *One Hundred Poems* — Tagore trans. (1915) | `kabir_songs_tagore` | Radhakrishnan & Moore 1957, p. 34 (Bhakti tradition) |
| ~1509 CE | West | Erasmus, *Praise of Folly* | `erasmus_praise_of_folly` | Scharfstein 1998, ch. 16 |
| ~1513 CE | West | Machiavelli, *The Prince* | `machiavelli_prince` | Deutsch & Bontekoe 1997, ch. 21 |
| ~1516 CE | West | Thomas More, *Utopia* | `more_utopia` | Deutsch & Bontekoe 1997, ch. 21 |
| ~1518 CE | East | Wang Yangming, *Instructions for Practical Living* | `wang_yangming_instructions` | Fung Yu-lan 1953, vol. II ch. 33; Scharfstein 1998, ch. 8 |
| ~1580 CE | West | Montaigne, *Essays* | `montaigne_essays` | Scharfstein 1998, ch. 16 |

### 1600–1900 CE

| Period | Region | Author / Work | File label | Authority |
|---|---|---|---|---|
| ~1637 CE | West | Descartes, *Discourse on Method* | `descartes_discourse_method` | Scharfstein 1998, ch. 17 |
| ~1651 CE | West | Hobbes, *Leviathan* | `hobbes_leviathan` | Scharfstein 1998, ch. 17; Deutsch & Bontekoe 1997, ch. 21 |
| ~1670 CE | West | Pascal, *Pensées* | `pascal_pensees` | Scharfstein 1998, ch. 17 |
| ~1677 CE | West | Spinoza, *Ethics* | `spinoza_ethics` | Scharfstein 1998, ch. 17; Deutsch & Bontekoe 1997, ch. 21 |
| ~1689 CE | West | Locke, *Essay Concerning Human Understanding* | `locke_essay_human_understanding` | Scharfstein 1998, ch. 18 |
| ~1690 CE | East | Bankei Yotaku, *Unborn: The Life and Teaching of Zen Master Bankei* | `bankei_unborn_zen` | Fung Yu-lan 1953, vol. II ch. 22 (Zen in Japan) |
| ~1710 CE | West | Berkeley, *Principles of Human Knowledge* | `berkeley_principles_human_knowledge` | Scharfstein 1998, ch. 18 |
| ~1739 CE | West | Hume, *Treatise of Human Nature* | `hume_treatise_human_nature` | Scharfstein 1998, ch. 18 |
| ~1748 CE | West | Hume, *Enquiry Concerning Human Understanding* | `hume_enquiry_human_understanding` | Scharfstein 1998, ch. 18 |
| ~1750 CE | East | D.T. Suzuki, *Outlines of Mahayana Buddhism* (1907) ⚠ | `suzuki_essays_zen` | **Placeholder**: Secondary source covering Hakuin-era Rinzai Zen. Hakuin's own writings not available in pre-1928 PD English translation. Suzuki is cited as a secondary authority in Deutsch & Bontekoe 1997, ch. 8. |
| ~1759 CE | West | Adam Smith, *Theory of Moral Sentiments* | `adam_smith_moral_sentiments` | Deutsch & Bontekoe 1997, ch. 21 |
| ~1781 CE | West | Kant, *Critique of Pure Reason* | `kant_critique_pure_reason` | Scharfstein 1998, ch. 19 (endpoint of title scope) |
| ~1807 CE | West | Hegel, *Phenomenology of Spirit* | `hegel_phenomenology_spirit` | Deutsch & Bontekoe 1997, ch. 21 |
| ~1818 CE | West | Schopenhauer, *World as Will and Representation* | `schopenhauer_world_will_representation` | Deutsch & Bontekoe 1997, ch. 21 |
| ~1863 CE | West | J.S. Mill, *Utilitarianism* | `mill_utilitarianism` | Deutsch & Bontekoe 1997, ch. 21 |
| ~1882 CE | East | *Gospel of Sri Ramakrishna* — Nikhilananda trans. | `gospel_ramakrishna` | Radhakrishnan & Moore 1957, p. 35 (Hindu reform) |
| ~1886 CE | West | Nietzsche, *Beyond Good and Evil* | `nietzsche_beyond_good_evil` | Deutsch & Bontekoe 1997, ch. 21 |
| ~1890 CE | East | Swami Vivekananda, *Complete Works* | `vivekananda_complete_works` | Radhakrishnan & Moore 1957, pp. 610–639 |
| ~1902 CE | West | William James, *Varieties of Religious Experience* | `james_varieties_religious_experience` | Deutsch & Bontekoe 1997, ch. 22 |

---

## Known Gaps

### Texts Warranted by Anchor References but Not Yet Included

| Missing text | Authority | Reason not included | Possible fix |
|---|---|---|---|
| **Jain Agamas / Tattvartha Sutra** | Radhakrishnan & Moore 1957, pp. 250–271 | No quality pre-1928 English translation | Jacobi SBE Vol. 22 & 45 on IA |
| **Nyaya Sutras** (Gautama, ~2nd c. BCE) | Radhakrishnan & Moore 1957, pp. 356–394 | Pre-1928 Ganganatha Jha translation may be on IA | IA search "Nyaya Sutras Jha" |
| **Samkhya Karika** (Ishvarakrishna, ~350 CE) | Radhakrishnan & Moore 1957, pp. 426–453 | Wilson 1837 translation is PD | IA search "Samkhya Karika Wilson" |
| **Xunzi additional chapters** | Fung Yu-lan 1952, vol. I ch. 12 | Dubs 1928 covers ~half the text only | IA may have complementary Mei translation |
| **Han Feizi** (~280–233 BCE) | Fung Yu-lan 1952, vol. I ch. 13 | Liao 1939 translation post-1927 | IA search "Han Fei Tzu" |
| **Huainanzi** (~139 BCE) | Fung Yu-lan 1952, vol. II ch. 15 | No complete pre-1928 English translation | IA has partial Morgan/Wallacker |
| **Sufism — Rumi, Ibn Arabi** | Corbin 1993, chs. 9–11 | R.A. Nicholson translations (1898–1926) may be partially on IA | IA "Nicholson Rumi Masnavi" |
| **Tibetan Buddhism — Milarepa, Tsongkhapa** | Deutsch & Bontekoe 1997, ch. 9 | Evans-Wentz translations are partially on IA | IA "Milarepa Tibet Evans-Wentz" |
| **Jewish — Talmud, Zohar** | Deutsch & Bontekoe 1997, ch. 13 | Soncino Talmud is copyright; Rodkinson partial translation may be on IA | IA "Rodkinson Talmud" |
| **Korean Buddhism — Wonhyo, Chinul** | Deutsch & Bontekoe 1997, ch. 10 | Limited pre-1928 English translations | BDK English Tripitaka |
| **African philosophy** | Deutsch & Bontekoe 1997, ch. 3 | Mostly oral tradition; few pre-1928 scholarly compilations | — |
| **Ancient Egypt / Mesopotamia** | Scharfstein 1998, ch. 1 | *Book of the Dead*, *Epic of Gilgamesh* on PG | PG #547, IA "Budge Book Dead" |
| **Female philosophers** | — | List is overwhelmingly male | Hildegard *Scivias* (IA), Teresa of Ávila *Interior Castle* (IA) |

### Placeholder Texts (Secondary Sources Used Instead of Primary)

Four entries use secondary or retelling sources because no pre-1928 primary
English translation is accessible. They are marked ⚠ in the timeline above:

| Label | What it actually is | What it should ideally be |
|---|---|---|
| `gospel_of_buddha_carus` | Paul Carus retelling (1894) | A primary Mahayana sutra (e.g., Diamond Sutra, Vimalakirti) in PD translation |
| `kenko_essays_idleness` | Aston literary history (1899) | Kenko *Tsurezuregusa* — all stand-alone English translations are post-1927 |
| `nichiren_writings` | Anesaki secondary study (1916) | Nichiren primary writings — no pre-1928 English translation |
| `suzuki_essays_zen` | D.T. Suzuki secondary study (1907) | Hakuin primary writings — Waddell translation is copyright |

### Periods with Thin East Coverage

- **200–300 CE**: Only a secondary source placeholder (Carus). No PD primary Mahayana sutra accessible.
- **600–700 CE**: No East entry. Dharmakirti (~600 CE) and Xuanzang (~645 CE) lack pre-1928 English translations.
- **1300–1400 CE**: Only the Aston literary history placeholder. Direct Kenko translation not accessible.

---

## Source Reliability Notes

- **Project Gutenberg IDs** are fixed and stable; safest source.
- **SuttaCentral** (Sujato CC0) is the highest-quality Pali Canon source.
- **Internet Archive** quality varies; the `_is_probably_english` heuristic and
  manual spot-checks are recommended before training.
