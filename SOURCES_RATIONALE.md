# Pretraining Source List — Rationale, Timeline & Gaps

## Purpose

This document explains why the texts in `download_pretraining_data.py` were chosen
and how coverage maps to the established scholarly canon of Eastern and Western
philosophy.

---

## Primary Anchors

The selection of philosophers is driven by two Wikipedia timelines that aggregate
the consensus of academic sources:

| Anchor | URL | Scope |
|---|---|---|
| **Timeline of Eastern Philosophers** | https://en.wikipedia.org/wiki/Timeline_of_Eastern_philosophers | Chinese, Indian, Japanese, Korean, Tibetan philosophers from ~1500 BCE to present |
| **Timeline of Western Philosophers** | https://en.wikipedia.org/wiki/Timeline_of_Western_philosophers | Greek, Roman, Islamic, Medieval, Early Modern, and Modern philosophers from ~600 BCE to present |

These pages are themselves summaries of the mainstream scholarly canon. The rule
applied here is: **if a philosopher appears on either Wikipedia timeline and a
public-domain English translation of their primary works exists, that text is
included.** Where no PD primary translation exists, the closest accessible
substitute is noted as a placeholder.

---

## Supporting References

The following peer-reviewed works informed decisions where the Wikipedia timelines
were ambiguous or where translation quality needed to be verified:

| Reference | Citation |
|---|---|
| Scharfstein 1998 | Ben-Ami Scharfstein, *A Comparative History of World Philosophy: From the Upanishads to Kant* (Albany: SUNY Press, 1998) |
| Fung Yu-lan 1952–53 | Fung Yu-lan, *A History of Chinese Philosophy*, 2 vols., trans. Derk Bodde (Princeton: Princeton UP, 1952–53) |
| Radhakrishnan & Moore 1957 | Sarvepalli Radhakrishnan & Charles A. Moore (eds.), *A Source Book in Indian Philosophy* (Princeton: Princeton UP, 1957) |
| Corbin 1993 | Henry Corbin, *History of Islamic Philosophy*, trans. L. Sherrard (London: Kegan Paul / IIS, 1993) |
| Deutsch & Bontekoe 1997 | Eliot Deutsch & Ron Bontekoe (eds.), *A Companion to World Philosophies* (Oxford: Blackwell, 1997) |

---

## Coverage Table

The table below maps each Wikipedia timeline period to the texts currently
in the corpus. **✓** = text downloaded; **⚠** = placeholder (secondary source
or retelling used because no PD primary translation is accessible);
**–** = philosopher on Wikipedia timeline, no PD English translation found.

---

### Eastern Philosophers

#### Vedic / Pre-Classical India (1500–400 BCE)
*Source: Wikipedia "Late Vedic age 800–400 BCE" section*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Yajnavalkya (Upanishads) | ~700–600 BCE | *Upanishads* — Müller trans. (SBE Vol. 15) | `upanishads_muller_sbe15` | ✓ |
| Siddhartha Gautama (Buddha) | c. 563–483 BCE | Pali Canon — Sujato trans. (SuttaCentral) | `pali_*_sujato` | ✓ |
| Siddhartha Gautama (Buddha) | c. 563–483 BCE | Pali Canon — Thanissaro trans. (Access to Insight) | `pali_thanissaro_ati` | ✓ |
| Mahavira (Jain) | 599–527 BCE | *Jaina Sutras* — Jacobi trans. (SBE Vols 22 & 45) | `jain_sutras_jacobi` | ✓ |

#### Warring States China (475–221 BCE)
*Source: Wikipedia "Warring States period" section, Fung Yu-lan 1952 vol. I*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Confucius | 551–479 BCE | *Analects* — Legge trans. | `analects_legge` | ✓ |
| Mozi | c. 470–390 BCE | *Works of Motse* — Mei trans. | `mozi_mei` | ✓ |
| Laozi | c. 6th c. BCE | *Tao Te Ching* — Legge trans. | `tao_te_ching_legge` | ✓ |
| Mencius | 372–289 BCE | *Works of Mencius* — Legge trans. | `mencius_legge` | ✓ |
| Zhuangzi | c. 4th c. BCE | *Zhuangzi* — Legge trans. | `zhuangzi_legge` | ✓ |
| Xunzi | c. 310–237 BCE | *Works of Hsuntze* — Dubs trans. | `xunzi_dubs` | ✓ |
| Han Feizi | died 233 BCE | *Complete Works of Han Fei Tzu* — W. K. Liao trans. | `han_feizi_liao` | ✓ |

#### Classical India / Bhagavad Gita (400–200 BCE)
*Source: Wikipedia "Maurya Empire" section; Radhakrishnan & Moore 1957*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Badarayana / Bhagavad Gita | c. 400–200 BCE | *Bhagavad Gita* — Arnold trans. ("The Song Celestial") | `bhagavad_gita_arnold` | ✓ |
| Aksapada Gautama (Nyaya) | c. 2nd c. BCE | *Nyaya Sutras of Gautama* — Jha trans. (Sacred Books of the Hindus Vol. 8) | `nyaya_sutras_gautama` | ✓ |
| Patanjali | c. 2nd c. BCE | *Yoga Sutras* — Johnston / Vivekananda trans. | `yoga_sutras_patanjali` | ✓ |

#### Hellenistic Greece & Zoroastrian Persia (1200–200 BCE)
*Source: Wikipedia "Ancient Greece", "Hellenistic Era", and "Zoroastrianism" sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Zoroaster / Gathas (Avesta) | c. 1200 BCE | *Zend-Avesta* — Darmesteter trans. (SBE Vol. 4) | `avesta_darmesteter_vol4` | ✓ |
| Zoroaster / Gathas (Avesta) | c. 1200 BCE | *Zend-Avesta* — Mills trans. (SBE Vol. 31) | `avesta_mills` | ✓ |
| Pre-Socratics (Heraclitus, Parmenides, etc.) | c. 600–400 BCE | *Early Greek Philosophy* — Burnet | `pre_socratics_burnet` | ✓ |
| Pre-Socratics (Empedocles, etc.) | c. 600–400 BCE | *Handbook of Greek Philosophy* — Fairbanks | `pre_socratics_fairbanks` | ✓ |
| Plato | c. 427–347 BCE | *Republic*, *Phaedo*, *Symposium*, *Apology*, *Gorgias*, *Theaetetus*, *Timaeus* — Jowett trans. | `plato_*_jowett` | ✓ |
| Aristotle | c. 384–322 BCE | *Nicomachean Ethics*, *Metaphysics*, *Politics*, *Physics/Organon*, *De Anima* | `aristotle_*` | ✓ |
| Epicurus | c. 341–270 BCE | *Lives of Eminent Philosophers* (Book X) — Diogenes Laertius / Yonge trans. | `epicurus_diogenes_laertius` | ✓ |

#### Early CE India & Mahayana Buddhism (0–550 CE)
*Source: Wikipedia "100–300" and "300–550" Indian sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Ashvaghosha | c. 1st c. CE | *Buddhacharita* — Cowell trans. | `buddhacharita_cowell` | ✓ |
| Ashvaghosha | c. 1st c. CE | *Awakening of Faith in the Mahayana* | `awakening_of_faith_suzuki` | ✓ |
| Milindapanha (anon.) | c. 1st c. CE | *Questions of King Milinda* — Rhys Davids trans. | `milindapanha_rhys_davids` | ✓ |
| Nagarjuna | c. 150–250 CE | *Mulamadhyamakakarika* | `nagarjuna_mulamadhyamakakarika` | ✓ |
| Vasubandhu | c. 4th c. CE | Eliot, *Hinduism and Buddhism* (1921) — covers Yogacara | `vasubandhu_eliot_hinduism_buddhism` | ⚠ (secondary source; primary trans. are copyright) |
| Asanga | c. 4th c. CE | *Lankavatara Sutra* (related Yogacara text) | `lankavatara_sutra_suzuki` | ⚠ (Yogacara text, not Asanga's own work) |
| Buddhaghosa | c. 5th c. CE | *Visuddhimagga* — Bhikkhu Nanamoli trans. | `visuddhimagga_buddhaghosa` | ✓ |

#### Classical China — Han through Tang (220 BCE–907 CE)
*Source: Wikipedia "221 BCE–220 CE" and "220 CE–907 CE" Chinese sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Wang Bi | 226–249 CE | — | — | – (Lynn 1994 trans. is copyright) |
| Paul Carus retelling (placeholder) | — | *The Gospel of Buddha* | `gospel_of_buddha_carus` | ⚠ |
| Huineng | 638–713 CE | *Platform Sutra of the Sixth Patriarch* | `platform_sutra_huineng` | ✓ |

#### Classical India — Gupta & Later (600–900 CE)
*Source: Wikipedia "600–900" Indian section; Radhakrishnan & Moore 1957*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Shantideva | c. 7th–8th c. CE | *Bodhicaryavatara* | `shantideva_bodhicaryavatara` | ✓ |
| Adi Shankara | c. 788–820 CE | *Vivekachudamani* ("Crest-Jewel of Wisdom") — Johnston 1925 trans. | `shankara_vivekachudamani` | ✓ |

#### Tibetan Buddhism (8th–19th c.)
*Source: Wikipedia "Tibetan Philosophers" section*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Padmasambhava (attr.) | c. 8th c. CE | *Bardo Thodol* — Evans-Wentz 1927 trans. | `tibetan_book_of_dead` | ✓ |
| Tsongkhapa | 1357–1419 | Waddell, *The Buddhism of Tibet, or Lamaism* (1895) — covers Gelug tradition | `waddell_buddhism_tibet` | ⚠ (secondary source; no PD primary translation) |
| Longchenpa | 1308–1364 | *Guhyagarbha Tantra with Commentary* (Longchenpa's own commentary) | `longchenpa_guhyagarbha` | ✓ |

#### Japan — Heian through Edo (774–1800 CE)
*Source: Wikipedia "Japanese Philosophers" sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Kukai | 774–835 CE | Eliot, *Japanese Buddhism* (1935) — covers Shingon/Kukai | `kukai_eliot_japanese_buddhism` | ⚠ (secondary source; Hakeda 1972 trans. is copyright) |
| Genshin | 942–1017 CE | *Pure Land Buddhism* texts (IA) | `genshin_ojoyoshu` | ✓ |
| Honen | 1133–1212 CE | Eliot, *Japanese Buddhism* (1935) — covers Honen and Pure Land | `kukai_eliot_japanese_buddhism` | ⚠ (covered by Eliot umbrella; Coates 1949 restricted) |
| Shinran | 1173–1261 CE | *Buddhist Psalms* — Yamabe & Beck trans. (1921) | `shinran_buddhist_psalms` | ✓ |
| Dogen Zenji | 1200–1253 CE | *Shobogenzo* (essays, older IA edition) | `dogen_shobogenzo` | ✓ |
| Nichiren | 1222–1282 CE | Anesaki, *Nichiren, the Buddhist Prophet* (1916) | `nichiren_writings` | ⚠ (secondary source) |
| Yoshida Kenko | c. 1330 CE | Aston, *A History of Japanese Literature* (1899) | `kenko_essays_idleness` | ⚠ (literary history, not primary text) |
| Hakuin Ekaku | 1686–1769 CE | Suzuki, *Outlines of Mahayana Buddhism* (1907) | `suzuki_essays_zen` | ⚠ (secondary source; Hakuin's own works copyright) |

#### Korea (617–1210 CE)
*Source: Wikipedia "Korean Philosophers" section*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Wonhyo | 617–686 CE | Sung Bae Park, *Wonhyo's Commentaries on Awakening of Faith* (1960 thesis) | `wonhyo_awakening_faith` | ⚠ (secondary source; no PD primary translation) |
| Jinul | 1158–1210 CE | — | — | – (Buswell 1991 trans. is copyright; no PD English) |

#### India — Medieval & Bhakti (900–1800 CE)
*Source: Wikipedia "900–1100" and "1100–1500" Indian sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Ramanuja | c. 1017–1137 CE | *Vedarthasangraha* | `ramanuja_vedarthasangraha` | ✓ |
| Kabir | 1440–1518 CE | *One Hundred Poems of Kabir* — Tagore trans. (1915) | `kabir_songs_tagore` | ✓ |

#### Neo-Confucianism — Song through Ming (980–1644 CE)
*Source: Wikipedia "907–1368" Chinese section; Fung Yu-lan 1953 vol. II*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Zhu Xi | 1130–1200 CE | *I Ching* — Legge trans. (text Zhu Xi centred his school on) | `i_ching_legge` | ✓ |
| Wang Yangming | 1472–1529 CE | *Instructions for Practical Living* | `wang_yangming_instructions` | ✓ |

#### Modern India (1800–1900 CE)
*Source: Wikipedia "1800–1947" Indian section; Radhakrishnan & Moore 1957*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Ramakrishna Paramahamsa | 1836–1886 CE | *Gospel of Sri Ramakrishna* | `gospel_ramakrishna` | ✓ |
| Swami Vivekananda | 1863–1902 CE | *Complete Works* | `vivekananda_complete_works` | ✓ |

---

### Western Philosophers

#### Pre-Socratics (600–400 BCE)
*Source: Wikipedia "600–500 BC" and "400 BC" sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Thales, Parmenides, Heraclitus, etc. | c. 624–400 BCE | *Early Greek Philosophy* — Burnet | `pre_socratics_burnet` | ✓ |
| Empedocles, Zeno, etc. | c. 492–400 BCE | *Handbook of Greek Philosophy* — Fairbanks | `pre_socratics_fairbanks` | ✓ |
| Epicurus | c. 341–270 BCE | *Lives of Eminent Philosophers* (Book X) — Diogenes Laertius / Yonge trans. | `epicurus_diogenes_laertius` | ✓ |

#### Classical Athens & Hellenistic Era (400–100 BCE)
*Source: Wikipedia "400 BC" and "300–200 BC" sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Plato | c. 427–347 BCE | *Republic*, *Phaedo*, *Symposium*, *Apology*, *Gorgias*, *Theaetetus*, *Timaeus* | `plato_*_jowett` | ✓ |
| Aristotle | c. 384–322 BCE | *Nicomachean Ethics*, *Metaphysics*, *Politics*, *Physics*, *De Anima* | `aristotle_*` | ✓ |
| Epicurus | c. 341–270 BCE | *Lives of Eminent Philosophers* Book X (Diogenes Laertius / Yonge trans.) — contains Epicurus's letters and doctrines verbatim | `epicurus_diogenes_laertius` | ✓ — Note: Bailey's direct trans. rejected (too many Greek characters); PG #51 Yonge trans. is clean English |

#### Classical Rome & Stoics (100 BCE–200 CE)
*Source: Wikipedia "100 BC–100 AD" and "100–400" sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Cicero | 106–43 BCE | *On the Nature of the Gods* — Yonge trans. (PG #14988) | `cicero_nature_of_gods` | ✓ |
| Seneca the Younger | c. 4 BCE–65 CE | *Letters to Lucilius* | `seneca_letters_lucilius` | ✓ |
| Epictetus | c. 55–135 CE | *Enchiridion* | `epictetus_enchiridion` | ✓ |
| Epictetus | c. 55–135 CE | *Discourses* | `epictetus_discourses` | ✓ |
| Marcus Aurelius | 121–180 CE | *Meditations* | `marcus_aurelius_meditations` | ✓ |
| Plotinus | c. 205–270 CE | *Enneads* — MacKenna trans. | `plotinus_enneads_mackenna` | ✓ |

#### Early Christianity (200–550 CE)
*Source: Wikipedia "100–400" and "500–900" sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Origen | c. 184–253 CE | *De Principiis* (Ante-Nicene Fathers) | `origen_de_principiis` | ✓ |
| Augustine of Hippo | c. 354–430 CE | *Confessions* | `augustine_confessions` | ✓ |
| Augustine of Hippo | c. 354–430 CE | *City of God* | `augustine_city_of_god` | ✓ |
| Eusebius | c. 260–339 CE | *Ecclesiastical History* | `eusebius_church_history` | ✓ |
| Jerome | c. 347–420 CE | *Select Letters* | `jerome_letters` | ✓ |
| Boethius | c. 480–524 CE | *Consolation of Philosophy* | `boethius_consolation_philosophy` | ✓ |
| Benedict of Nursia | c. 480–547 CE | *Rule of Saint Benedict* | `benedict_rule` | ✓ |

#### Islamic Philosophy (632–1200 CE)
*Source: Wikipedia "500–900" and "1000–1100" sections; Corbin 1993*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Muhammad (Quran) | c. 570–632 CE | *Quran* — Rodwell trans. | `quran_rodwell` | ✓ |
| Al-Kindi | c. 801–873 CE | *On First Philosophy* | `al_kindi_first_philosophy` | ✓ |
| Al-Farabi | c. 870–950 CE | *Opinions of the Inhabitants of the Virtuous City* | `al_farabi_virtuous_city` | ✓ |
| Avicenna | c. 980–1037 CE | *Book of Healing* | `avicenna_book_of_healing` | ✓ |
| Al-Ghazali | c. 1058–1111 CE | *Tahafut al-Falasifa* | `al_ghazali_incoherence` | ✓ |
| Ibn Tufayl | c. 1105–1185 CE | *Hayy ibn Yaqzan* — Simon Ockley 1708 trans. | `ibn_tufayl_hayy` | ✓ |
| Averroes / Ibn Rushd | c. 1126–1198 CE | *Tahafut al-Tahafut* | `averroes_tahafut` | ✓ |
| Maimonides | c. 1135–1204 CE | *Guide for the Perplexed* | `maimonides_guide_perplexed` | ✓ |
| Ibn Arabi | 1165–1240 CE | *Tarjuman al-Ashwaq* — R. A. Nicholson trans. (1911) | `ibn_arabi_tarjuman` | ✓ |

#### Medieval & Scholastic (700–1400 CE)
*Source: Wikipedia "500–900" and "1200–1300" sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| John of Damascus | c. 680–750 CE | *Exposition of the Orthodox Faith* | `john_damascus_orthodox_faith` | ✓ |
| John Scotus Eriugena | c. 815–877 CE | *Periphyseon* | `eriugena_periphyseon` | ✓ |
| Anselm of Canterbury | c. 1034–1109 CE | *Proslogion* + *Cur Deus Homo* | `anselm_proslogion_cur_deus` | ✓ |
| Thomas Aquinas | c. 1221–1274 CE | *Summa Theologica* | `aquinas_summa_theologica` | ✓ |
| William of Ockham | c. 1288–1348 CE | *Summa Logicae* (excerpts) | `ockham_summa_logicae` | ✓ |
| Meister Eckhart | c. 1260–1328 CE | *Sermons* — Evans trans. | `meister_eckhart_sermons` | ✓ |
| Dante Alighieri | c. 1265–1321 CE | *Divine Comedy* — Cary trans. | `dante_divine_comedy_cary` | ✓ |
| Julian of Norwich | c. 1342–1416 CE | *Revelations of Divine Love* | `julian_norwich_revelations` | ✓ |
| Thomas à Kempis | c. 1380–1471 CE | *Imitation of Christ* | `thomas_kempis_imitation_christ` | ✓ |
| Nicholas of Cusa | 1401–1464 CE | *On Learned Ignorance* | `nicholas_cusa_learned_ignorance` | ✓ |

#### Renaissance & Early Modern (1450–1650 CE)
*Source: Wikipedia "1400" and "1500" sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Erasmus | 1466–1536 CE | *Praise of Folly* | `erasmus_praise_of_folly` | ✓ |
| Machiavelli | 1469–1527 CE | *The Prince* | `machiavelli_prince` | ✓ |
| Thomas More | 1478–1535 CE | *Utopia* | `more_utopia` | ✓ |
| Montaigne | 1533–1592 CE | *Essays* | `montaigne_essays` | ✓ |
| Francis Bacon | 1561–1626 CE | *Novum Organum* | `bacon_novum_organum` | ✓ |
| Thomas Hobbes | 1588–1679 CE | *Leviathan* | `hobbes_leviathan` | ✓ |
| René Descartes | 1596–1650 CE | *Discourse on Method* | `descartes_discourse_method` | ✓ |

#### Rationalism & Empiricism (1620–1750 CE)
*Source: Wikipedia "1600" section*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Blaise Pascal | 1623–1662 CE | *Pensées* | `pascal_pensees` | ✓ |
| Baruch Spinoza | 1632–1677 CE | *Ethics* | `spinoza_ethics` | ✓ |
| John Locke | 1632–1704 CE | *Essay Concerning Human Understanding* | `locke_essay_human_understanding` | ✓ |
| Gottfried Leibniz | 1646–1716 CE | *Monadology* + *Discourse on Metaphysics* | `leibniz_monadology` | ✓ |
| George Berkeley | 1685–1753 CE | *Principles of Human Knowledge* | `berkeley_principles_human_knowledge` | ✓ |
| David Hume | 1711–1776 CE | *Treatise of Human Nature* | `hume_treatise_human_nature` | ✓ |
| David Hume | 1711–1776 CE | *Enquiry Concerning Human Understanding* | `hume_enquiry_human_understanding` | ✓ |

#### Enlightenment (1700–1800 CE)
*Source: Wikipedia "1700" section*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Jean-Jacques Rousseau | 1712–1778 CE | *The Social Contract* | `rousseau_social_contract` | ✓ |
| Adam Smith | 1723–1790 CE | *Theory of Moral Sentiments* | `adam_smith_moral_sentiments` | ✓ |
| Immanuel Kant | 1724–1804 CE | *Critique of Pure Reason* | `kant_critique_pure_reason` | ✓ |
| Mary Wollstonecraft | 1759–1797 CE | *Vindication of the Rights of Woman* | `wollstonecraft_vindication` | ✓ |
| G. W. F. Hegel | 1770–1831 CE | *Phenomenology of Spirit* | `hegel_phenomenology_spirit` | ✓ |

#### 19th Century (1800–1900 CE)
*Source: Wikipedia "1800–1850" and "1850–1900" sections*

| Philosopher | Dates | Work in corpus | Label | Status |
|---|---|---|---|---|
| Arthur Schopenhauer | 1788–1860 CE | *World as Will and Representation* | `schopenhauer_world_will_representation` | ✓ |
| Søren Kierkegaard | 1813–1855 CE | *Selections from the Writings of Kierkegaard* — PG #60333 | `kierkegaard_selections` | ✓ |
| John Stuart Mill | 1806–1873 CE | *Utilitarianism* | `mill_utilitarianism` | ✓ |
| Friedrich Nietzsche | 1844–1900 CE | *Beyond Good and Evil* | `nietzsche_beyond_good_evil` | ✓ |
| William James | 1842–1910 CE | *Varieties of Religious Experience* | `james_varieties_religious_experience` | ✓ |
| Karl Marx | 1818–1883 CE | *The Communist Manifesto* — PG #61 | `marx_communist_manifesto` | ✓ |

---

## Known Gaps & Substitutions

Every philosopher on the Wikipedia timelines is listed below with its final status.
**✓** = primary PD text downloaded. **⚠** = secondary source used (reason given). **–** = no entry possible (reason given).

### East

| Philosopher | Dates | Label | Status | Reason / Note |
|---|---|---|---|---|
| Mahavira (Jain) | 599–527 BCE | `jain_sutras_jacobi` | ✓ | Jacobi SBE Vols 22 & 45 — closest available primary text |
| Han Feizi | died 233 BCE | `han_feizi_liao` | ✓ | W. K. Liao trans., IA open-access copy |
| Aksapada Gautama (Nyaya) | c. 2nd c. BCE | `nyaya_sutras_gautama` | ✓ | Jha 1912 trans. — Sacred Books of the Hindus Vol. 8 |
| Vasubandhu | c. 4th c. CE | `vasubandhu_eliot_hinduism_buddhism` | ⚠ | Eliot *Hinduism and Buddhism* (1921) secondary. Primary: Pruden trans. (copyright); IA scans non-English OCR |
| Asanga | c. 4th c. CE | `lankavatara_sutra_suzuki` | ⚠ | Related Yogacara text used. No PD English of Asanga's own works exists |
| Wang Bi | 226–249 CE | — | – | Richard Lynn trans. (1994) copyright. No earlier PD English translation of his Tao/Yi commentaries |
| Wonhyo | 617–686 CE | `wonhyo_awakening_faith` | ⚠ | Sung Bae Park 1960 thesis (secondary). No PD English primary translation |
| Kukai | 774–835 CE | `kukai_eliot_japanese_buddhism` | ⚠ | Eliot *Japanese Buddhism* (1935) secondary. Hakeda 1972 trans. copyright |
| Honen | 1133–1212 CE | `kukai_eliot_japanese_buddhism` | ⚠ | Same Eliot umbrella. Coates 1949 trans. is restricted on IA |
| Shinran | 1173–1261 CE | `shinran_buddhist_psalms` | ✓ | Yamabe & Beck 1921 trans. — *Buddhist Psalms* — PD |
| Jinul | 1158–1210 CE | — | – | Buswell 1991 trans. copyright; no PD English found on IA or PG |
| Longchenpa | 1308–1364 CE | `longchenpa_guhyagarbha` | ✓ | *Guhyagarbha Tantra with Commentary* — IA open access |
| Tsongkhapa | 1357–1419 CE | `waddell_buddhism_tibet` | ⚠ | Waddell *Buddhism of Tibet* (1895) secondary. No PD English of Lamrim or primary works |
| Hakuin Ekaku | 1686–1769 CE | `suzuki_essays_zen` | ⚠ | Suzuki *Outlines of Mahayana Buddhism* (1907) secondary. Waddell trans. of Hakuin copyright |

### West

| Philosopher | Dates | Label | Status | Reason / Note |
|---|---|---|---|---|
| Epicurus | c. 341–270 BCE | `epicurus_diogenes_laertius` | ✓ | PG #51 Diogenes Laertius Book X (Yonge trans.) contains all letters and Principal Doctrines. Bailey direct trans. rejected by English filter (Greek characters) |
| Cicero | 106–43 BCE | `cicero_nature_of_gods` | ✓ | PG #14988 — Yonge trans. *On the Nature of the Gods* |
| Ibn Tufayl | c. 1105–1185 CE | `ibn_tufayl_hayy` | ✓ | Simon Ockley 1708 trans. — IA open access |
| Ibn Arabi | 1165–1240 CE | `ibn_arabi_tarjuman` | ✓ | R. A. Nicholson 1911 trans. *Tarjuman al-Ashwaq* — IA open access |
| Søren Kierkegaard | 1813–1855 CE | `kierkegaard_selections` | ✓ | PG #60333 — *Selections from the Writings of Kierkegaard*. Lowrie/Swenson translations copyright |
| Karl Marx | 1818–1883 CE | `marx_communist_manifesto` | ✓ | PG #61 — *The Communist Manifesto* |

### Placeholder Texts (Secondary Sources Used)

These labels exist in the script but use secondary/indirect sources because no PD primary translation is accessible:

| Label | What it actually is | Ideal primary text | Why not available |
|---|---|---|---|
| `gospel_of_buddha_carus` | Paul Carus retelling (1894) | A primary Mahayana sutra | Diamond Sutra: Tibetan scan; Wang Bi commentary: copyright |
| `nichiren_writings` | Anesaki *Nichiren, the Buddhist Prophet* (1916) | Nichiren's own letters/writings | No PD English translation exists |
| `kenko_essays_idleness` | Aston *History of Japanese Literature* (1899) | Kenko *Tsurezuregusa* | All English translations post-1927; all restricted on IA |
| `suzuki_essays_zen` | D. T. Suzuki *Outlines of Mahayana Buddhism* (1907) | Hakuin primary works | Waddell trans. copyright |
| `vasubandhu_eliot_hinduism_buddhism` | Eliot *Hinduism and Buddhism* (1921) | Vasubandhu's Trimsika / Vimsatika | Anacker 1984 trans. restricted on IA; OCR scans non-English |
| `wonhyo_awakening_faith` | Park 1960 academic thesis | Wonhyo's *Awakening of Faith* commentary | No PD English translation of primary texts |
| `kukai_eliot_japanese_buddhism` | Eliot *Japanese Buddhism* (1935) | Kukai's *Sokushin Jobutsu Gi* etc. | Hakeda 1972 trans. copyright |
| `waddell_buddhism_tibet` | Waddell *Buddhism of Tibet* (1895) | Tsongkhapa's *Lamrim Chenmo* | No PD English translation |

---

## Source Reliability Notes

- **Project Gutenberg** IDs are fixed and stable; safest and most consistent source.
- **SuttaCentral** (Sujato CC0) is the highest-quality Pali Canon source.
- **Internet Archive** quality varies; the `_is_probably_english` heuristic and
  manual spot-checks are recommended before any training run.
