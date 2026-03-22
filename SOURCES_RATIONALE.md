# Pretraining Source List — Rationale, Timeline & Gaps

## Purpose

This document explains why the texts in `download_pretraining_data.py` were chosen
and how coverage maps to the established scholarly canon of Eastern and Western
philosophy. It has been updated to reflect a full audit against the two primary
anchor timelines.

---

## Primary Anchors

| Anchor | URL | Scope |
|---|---|---|
| **Timeline of Eastern Philosophers** | https://en.wikipedia.org/wiki/Timeline_of_Eastern_philosophers | Chinese, Indian, Japanese, Korean, Tibetan philosophers from ~1500 BCE to 1950 |
| **Timeline of Western Philosophers** | https://en.wikipedia.org/wiki/Timeline_of_Western_philosophers | Greek, Roman, Islamic, Medieval, Early Modern, Modern philosophers from ~620 BCE to present |

**Rule applied:** If a philosopher appears on either Wikipedia timeline and a
public-domain English translation of their primary works exists (or a reliable
secondary/adjacent PD text covers their tradition), that text is included.
Where no PD English translation exists, the entry is retained in `SOURCES` using
`fetch_unavailable` with an explicit reason code.

**Reason codes used in `fetch_unavailable`:**
- `no_pd_english` — no public-domain English translation exists
- `copyright_trans` — English translations exist but are all in copyright
- `no_english_trans` — no English translation exists at all
- `restricted_ia` — Internet Archive copy returns 401/403
- `lost_work` — primary work is lost; only fragments/doxography survive

---

## Supporting References

| Reference | Citation |
|---|---|
| Scharfstein 1998 | Ben-Ami Scharfstein, *A Comparative History of World Philosophy* (Albany: SUNY Press, 1998) |
| Fung Yu-lan 1952–53 | Fung Yu-lan, *A History of Chinese Philosophy*, 2 vols., trans. Derk Bodde (Princeton UP, 1952–53) |
| Radhakrishnan & Moore 1957 | S. Radhakrishnan & C.A. Moore (eds.), *A Source Book in Indian Philosophy* (Princeton UP, 1957) |
| Corbin 1993 | Henry Corbin, *History of Islamic Philosophy*, trans. L. Sherrard (London: Kegan Paul, 1993) |
| Deutsch & Bontekoe 1997 | Eliot Deutsch & Ron Bontekoe (eds.), *A Companion to World Philosophies* (Blackwell, 1997) |

---

## Status Key

| Symbol | Meaning |
|---|---|
| ✓ | Primary PD text targeted for download |
| ⚠ | Secondary or adjacent source used (reason given) |
| – | No download possible; `fetch_unavailable` entry retained with reason |

---

## EASTERN PHILOSOPHERS

### Vedic / Pre-Classical India (1500–400 BCE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Vedic Sages (Vasishtha, Atri, Vishvamitra, Agastya, etc.) | ~1500–1000 BCE | `rigveda_griffith` | ✓ | Griffith 1896 trans. (PG #46700); Lopamudra also in Rigveda 1.179 |
| Parshvanatha (Jain) | c. 872–772 BCE | `parshvanatha_primary` | – | lost_work: teachings subsumed in `jain_sutras_jacobi` |
| Yajnavalkya (Upanishads) | ~700–600 BCE | `upanishads_muller_sbe15` | ✓ | Müller trans. (SBE Vol. 15); PG #2034 |
| Makkhali Gosala (Ajivika) | c. 600–500 BCE | `gosala_ajivika` | – | lost_work: Ajivika canon entirely lost; fragments in Pali Canon and Jain texts |
| Pāṇini | c. 600–500 BCE | `panini_ashtadhyayi` | ⚠ | IA search attempted; content is highly technical Sanskrit grammar notation |
| Bṛhaspati / Charvaka | c. 600–400 BCE | `brihaspati_charvaka` | – | lost_work: Barhaspatya-sutras entirely lost; only hostile summaries survive |
| Mahavira (Jain) | 599–527 BCE | `jain_sutras_jacobi` | ✓ | Jacobi trans. (SBE Vols 22 & 45) |
| Badarayana | c. 500–400 BCE | `brahma_sutras_thibaut` | ✓ | Thibaut trans. (SBE Vols 34 & 38) |
| Kapila (Sankhya) | c. 500 BCE | `sankhya_karika_kapila` | ✓ | Ballantyne 1855 trans.; Sankhya-karika of Ishvarakrishna codifies Kapila's school |
| Shvetashvatara | c. 400–300 BCE | — | — | Covered within `upanishads_muller_sbe15` (SBE Vol. 15 second series) |
| Siddhartha Gautama (Buddha) | c. 563–483 BCE | `pali_*_sujato` + `pali_thanissaro_ati` | ✓ | SuttaCentral CC0 + Access to Insight open license |

### Warring States China (475–221 BCE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Guan Zhong | d. 645 BCE | `guanzi_guan_zhong` | ⚠ | IA search attempted; no complete PD English translation confirmed |
| Sun Tzu | c. 544–496 BCE | `sun_tzu_art_of_war` | ✓ | Giles 1910 trans. (PG #132) |
| Laozi | c. 6th c. BCE | `tao_te_ching_legge` | ✓ | Legge trans. (PG #216) |
| Confucius | 551–479 BCE | `analects_legge` | ✓ | Legge trans. (PG #3330) |
| Mozi | c. 470–390 BCE | `mozi_mei` | ✓ | Yi-Pao Mei trans. |
| Liezi | c. 440–360 BCE | `liezi_giles` | ✓ | Giles 1912 trans. |
| Gaozi | c. 420 BCE | `gaozi_works` | – | lost_work: philosophy known only from Mencius Book 6 debates |
| Mencius | 372–289 BCE | `mencius_legge` | ✓ | Legge trans. (PG #38406) |
| Xu Xing | c. 315 BCE | `xu_xing_works` | – | lost_work: known only from Mencius 3A:4 |
| Gongsun Longzi | fl. 300 BCE | `gongsun_longzi` | ⚠ | IA search attempted; partial PD English translations may exist |
| Hui Shi | 4th c. BCE | `hui_shi_works` | – | lost_work: fragments only in Zhuangzi ch. 33 |
| Shang Yang | d. 338 BCE | `shang_yang_book_lord_shang` | ⚠ | Duyvendak 1928 trans. attempted via IA |
| Shen Buhai | d. 337 BCE | `shen_buhai_works` | – | lost_work: fragments only in Han Feizi |
| Shen Dao | c. 350–275 BCE | `shen_dao_works` | – | lost_work: fragments only; no PD English reconstruction |
| Song Xing | 360–290 BCE | `song_xing_works` | – | lost_work: fragments in Zhuangzi and Xunzi |
| Yang Zhu | 370–319 BCE | `yang_zhu_works` | – | lost_work: Liezi ch. 7 and Zhuangzi fragments |
| Zhuangzi | c. 4th c. BCE | `zhuangzi_legge` | ✓ | Legge trans. (PG #29724) |
| Xunzi | c. 310–237 BCE | `xunzi_dubs` | ✓ | Dubs 1928 trans. |
| Zou Yan | 305–240 BCE | `zou_yan_works` | – | lost_work: entirely lost; summaries in Shiji only |
| Han Feizi | d. 233 BCE | `han_feizi_liao` | ✓ | W.K. Liao trans. |

### Classical India / Bhagavad Gita (400–200 BCE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Chanakya | c. 350–275 BCE | `arthashastra_chanakya` | ✓ | Shamasastry 1915 trans. |
| Jaimini (Mimamsa) | c. 300–200 BCE | `mimamsa_sutras_jaimini` | ✓ | Jha trans. (Sacred Books of the Hindus) |
| Aksapada Gautama (Nyaya) | c. 2nd c. BCE | `nyaya_sutras_gautama` | ✓ | Jha trans. (SBH Vol. 8) |
| Kanada (Vaisheshika) | c. 3rd–2nd c. BCE | `vaisesika_sutras_kanada` | ✓ | Nandalal Sinha trans. |
| Pingala | c. 3rd–2nd c. BCE | `pingala_chandahshastra` | – | no_pd_english: no accessible PD English translation; highly technical prosody |
| Bhagavad Gita / Badarayana | c. 400–200 BCE | `bhagavad_gita_arnold` | ✓ | Edwin Arnold 1885 trans. "The Song Celestial" (PG #2388) |
| Patanjali | c. 2nd c. BCE | `yoga_sutras_patanjali` | ✓ | Johnston / Vivekananda trans. |

### Classical India — Early CE (0–500 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Thiruvalluvar | c. 1st c. BCE–2nd c. CE | `tirukkural_thiruvalluvar` | ✓ | Drew & Lazarus 1885 trans. |
| Ashvaghosha | c. 1st c. CE | `buddhacharita_cowell` + `awakening_of_faith_suzuki` | ✓ | Cowell trans. + Suzuki trans. |
| Milindapanha | c. 1st c. CE | `milindapanha_rhys_davids` | ✓ | Rhys Davids trans. |
| Nagarjuna | c. 150–250 CE | `nagarjuna_mulamadhyamakakarika` | ✓ | IA open access |
| Kundakunda (Jain) | c. 2nd c. CE | `kundakunda_panchastikayasara` | ✓ | Chakravarti 1920 trans. |
| Umasvati (Jain) | c. 2nd c. CE | `umasvati_tattvarthasutra` | ✓ | Jacobi trans. partially |
| Vasubandhu | c. 4th c. CE | `vasubandhu_eliot_hinduism_buddhism` | ⚠ | Eliot 1921 secondary; primary trans. Pruden 1988 is copyright |
| Asanga | c. 4th c. CE | `lankavatara_sutra_suzuki` | ⚠ | Related Yogacara text; no PD English of Asanga's own works |
| Vatsyayana | c. 450–500 CE | `vatsyayana_nyaya_bhasya` | – | no_pd_english: commentary on Nyaya Sutras; no PD English trans. |
| Bhartrhari | 450–510 CE | `bhartrhari_vakyapadiya` | – | no_pd_english: Iyer 1965–74 trans. copyright |
| Buddhaghosa | c. 5th c. CE | `visuddhimagga_buddhaghosa` | ✓ | Nanamoli trans. |
| Dignaga | c. 5th c. CE | `dignaga_pramanasamuccaya` | – | no_pd_english: Hattori 1968 copyright |
| Siddhasena Divakara (Jain) | c. 5th c. CE | `siddhasena_sanmatitarka` | – | no_pd_english: no PD English translation |
| Bhaviveka | c. 6th c. CE | `bhaviveka_prajnapradipa` | – | no_pd_english: Eckel 1992 copyright |
| Silabhadra | c. 529–645 CE | `silabhadra_works` | – | no_pd_english: known through Xuanzang's travelogue |

### Early Medieval China — Han through Tang (200 BCE–907 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Lü Buwei | 290–235 BCE | `lu_buwei_lushi_chunqiu` | – | no_pd_english: Knoblock & Riegel 2000 copyright |
| Jia Yi | 201–169 BCE | `jia_yi_essays` | ⚠ | IA search attempted; partial PD translations exist |
| Dong Zhongshu | c. 176–104 BCE | `dong_zhongshu_chunqiu_fanlu` | – | no_pd_english: Queen 2016 copyright |
| Liu An | 179–122 BCE | `liu_an_huainanzi` | ⚠ | IA search attempted; Major 2010 copyright; older partial PD texts exist |
| Yang Xiong | 53 BCE–18 CE | `yang_xiong_fa_yan` | ⚠ | IA search attempted; Brewitt-Taylor 1925 may be PD |
| Wang Chong | 27–97 CE | `wang_chong_lunheng` | ✓ | Forke 1907/1911 trans. |
| Zheng Xuan | 127–200 CE | `zheng_xuan_commentaries` | – | no_pd_english: no English translation of classical commentaries |
| He Yan | 190–249 CE | `he_yan_commentary` | – | no_pd_english: no PD English translation |
| Ruan Ji | 210–263 CE | `ruan_ji_works` | – | no_pd_english: Holzman 1976 copyright |
| Ji Kang | 223–262 CE | `ji_kang_works` | – | no_pd_english: Henricks 1983 copyright |
| Wang Bi | 226–249 CE | `wang_bi_commentaries` | – | copyright_trans: Lynn 1994 copyright; no earlier PD English translation |
| Pei Wei | 267–300 CE | `pei_wei_chongyu` | – | no_pd_english: no PD English translation |
| Zhi Dun | 314–366 CE | `zhi_dun_works` | – | no_pd_english: no PD English translation |
| Sengzhao | 384–414 CE | `sengzhao_zhao_lun` | ✓ | Liebenthal 1948 trans. |
| Ge Hong | 4th c. CE | `ge_hong_baopuzi` | ⚠ | Ware 1966 copyright; older partial PD translations via IA |
| Lushan Huiyuan | 334–416 CE | `lushan_huiyuan_pure_land` | ⚠ | IA search attempted |
| Tan-luan | 476–542 CE | `tan_luan_pure_land` | – | no_pd_english: no PD English translation |
| Dazu Huike | 487–593 CE | `dazu_huike_works` | – | no_pd_english: Chan transmission records only |
| Nanyue Huisi | 515–577 CE | `nanyue_huisi_works` | – | no_pd_english: no PD English translation |
| Zhiyi | 538–597 CE | `zhiyi_mohe_zhiguan` | – | no_pd_english: Donner & Stevenson 1993 copyright |
| Jizang | 549–623 CE | `jizang_sanlun` | – | no_pd_english: no PD English translation |
| Dushun | 557–640 CE | `dushun_huayan` | – | no_pd_english: Cleary 1983 copyright |
| Dayi Daoxin | 580–651 CE | `dayi_daoxin_works` | – | no_pd_english: no PD English translation |
| Shandao | 613–681 CE | `shandao_pure_land` | – | no_pd_english: no PD English translation |
| Hong Ren | 601–674 CE | `hong_ren_treatise` | – | no_pd_english: no PD English translation |
| Xuanzang | 602–664 CE | `xuanzang_great_tang_records` | ✓ | Beal 1884 trans. |
| Yuquan Shenxiu | 606–706 CE | `shenxiu_northern_chan` | – | no_pd_english: known only from Platform Sutra polemic |
| Cheng Xuanying | 631–655 CE | `cheng_xuanying_commentary` | – | no_pd_english: no PD English translation |
| Huineng | 638–713 CE | `platform_sutra_huineng` | ✓ | IA open access |
| Fazang | 643–712 CE | `fazang_huayan` | – | no_pd_english: Cleary 1983 copyright |
| Shenhui | 684–758 CE | `shenhui_platform_talks` | – | no_pd_english: no PD English translation |
| Shitou Xiqian | 700–790 CE | `shitou_xiqian_cantong` | – | no_pd_english: Cleary copyright |
| Mazu Daoyi | 709–788 CE | `mazu_daoyi_yulu` | – | no_pd_english: no PD English translation |
| Baizhang Huaihai | 720–814 CE | `baizhang_huaihai_works` | – | no_pd_english: no PD English translation |
| Li Ao | 722–841 CE | `li_ao_fuxing_shu` | – | no_pd_english: no PD English translation |
| Qingliang Chengguan | 738–839 CE | `chengguan_huayan` | – | no_pd_english: no PD English translation |
| Han Yu | 768–824 CE | `han_yu_essays` | ✓ | Partial PD translations via IA |
| Zhaozhou Congshen | 778–897 CE | `zhaozhou_congshen_works` | – | no_pd_english: Cleary copyright |
| Zongmi | 780–841 CE | `zongmi_works` | – | no_pd_english: no PD English translation |
| Huangbo Xiyun | ?–850 CE | `huangbo_xiyun_works` | – | copyright_trans: Blofeld 1958 copyright |
| Linji Yixuan | d. 866 CE | `linji_yixuan_record` | – | no_pd_english: no PD English translation |
| Yunmen Wenyan | 864–949 CE | `yunmen_wenyan_works` | – | no_pd_english: no PD English translation |

### Song–Ming Neo-Confucianism (960–1644 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Xuedou Chongxian | 980–1052 CE | `xuedou_chongxian_works` | – | copyright_trans: Cleary & Cleary 1977 copyright |
| Fan Zhongyan | 989–1052 CE | `fan_zhongyan_works` | – | no_pd_english: no PD English translation |
| Hu Yuan | 993–1059 CE | `hu_yuan_works` | – | no_pd_english: no PD English translation |
| Shao Yung | 1011–1077 CE | `shao_yung_works` | – | no_pd_english: no PD English translation |
| Zhou Dunyi | 1017–1073 CE | `zhou_dunyi_taijitu` | ⚠ | Brief PD translations within secondary sources |
| Chang Tsai | 1020–1077 CE | `zhang_zai_zhengmeng` | – | no_pd_english: no PD English translation |
| Cheng Hao | 1032–1085 CE | `cheng_hao_works` | – | no_pd_english: no PD English translation |
| Cheng Yi | 1033–1107 CE | `cheng_yi_works` | – | no_pd_english: no PD English translation |
| Yuanwu Keqin | 1063–1135 CE | `yuanwu_keqin_biyanlu` | – | copyright_trans: Cleary & Cleary 1977 copyright |
| Dahui Zonggao | 1089–1163 CE | `dahui_zonggao_works` | – | no_pd_english: no PD English translation |
| Hu Hong | 1105–1161 CE | `hu_hong_works` | – | no_pd_english: no PD English translation |
| Zhu Xi | 1130–1200 CE | `i_ching_legge` | ✓ | Legge trans. (I Ching, SBE Vol. 16) |
| Lu Jiuyuan | 1139–1193 CE | `lu_jiuyuan_works` | – | no_pd_english: no PD English translation |
| Wumen Huikai | 1183–1260 CE | `wumen_huikai_gateless_gate` | ✓ | Senzaki & Reps 1934 trans. |
| Chen Xianzhang | 1428–1500 CE | `chen_xianzhang_works` | – | no_pd_english: no PD English translation |
| Wang Yangming | 1472–1529 CE | `wang_yangming_instructions` | ✓ | IA open access |
| Wang Gen | 1483–1541 CE | `wang_gen_works` | – | no_pd_english: no PD English translation |
| He Xinyin | 1517–1579 CE | `he_xinyin_works` | – | no_pd_english: no PD English translation |
| Li Zhi | 1527–1602 CE | `li_zhi_fenshu` | ⚠ | IA search attempted; de Bary anthology excerpts |
| Jiao Hong | 1540–1620 CE | `jiao_hong_works` | – | no_pd_english: no PD English translation |
| Liu Tsung-chou | 1578–1645 CE | `liu_tsung_chou_works` | – | no_pd_english: no PD English translation |
| Huang Zongxi | 1610–1695 CE | `huang_zongxi_mingru` | ⚠ | IA search attempted; de Bary anthology PD passages |
| Wang Fuzhi | 1619–1692 CE | `wang_fuzhi_works` | – | no_pd_english: no PD English translation |
| Yen Yuan | 1635–1704 CE | `yen_yuan_works` | – | no_pd_english: no PD English translation |
| Li Gong | 1659–1733 CE | `li_gong_works` | – | no_pd_english: no PD English translation |
| Dai Zhen | 1724–1777 CE | `dai_zhen_mengzi` | – | copyright_trans: Chin & Freeman 1990 copyright |
| Zhang Xuecheng | 1738–1801 CE | `zhang_xuecheng_works` | – | no_pd_english: no PD English translation |
| Yu Zhengxie | 1775–1840 CE | `yu_zhengxie_works` | – | no_pd_english: no PD English translation |
| Kang Youwei | 1858–1927 CE | `kang_youwei_ta_tung_shu` | ✓ | Thompson 1958 trans. (PD) |
| Tan Sitong | 1864–1898 CE | *(not yet in script)* | – | no_pd_english: no accessible PD English translation of Renxue |
| Liang Qichao | 1873–1929 CE | `liang_qichao_works` | ⚠ | IA search attempted; some political essays PD |
| Hu Shih | 1891–1962 CE | `hu_shih_logical_method` | ✓ | *Development of Logical Method* 1922 (PD) |
| Mao Zedong / Liu Shaoqi / others | 1893–1976 CE | — | – | no_pd_english: primary philosophical works not in PD English; out of scope for pretraining |

### Medieval & Modern India (900–1950 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Ramanuja | c. 1017–1137 CE | `ramanuja_vedarthasangraha` | ✓ | IA open access |
| Gorakshanath | 11th–12th c. | `gorakshanath_works` | ✓ | Briggs 1938 trans. |
| Basaveshwara | 1134–1196 CE | `basaveshwara_vachanas` | ✓ | PD translation via IA |
| Shri Madhvacharya | 1238–1317 CE | `madhvacharya_brahma_sutra` | ✓ | Rao 1936 trans. |
| Gangesha Upadhyaya | c. 13th c. | `gangesha_tattvacintamani` | – | no_pd_english: no PD English translation |
| Nimbarka | c. 13th c. | `nimbarka_vedanta` | – | no_pd_english: no PD English translation |
| Madhava Vidyaranya | c. 1268–1386 CE | `vidyaranya_pancadasi` | ✓ | Srinivasa Rao trans. |
| Kabir | 1440–1518 CE | `kabir_songs_tagore` | ✓ | Tagore 1915 trans. (PD) |
| Vyasatirtha | c. 1460–1539 CE | `vyasatirtha_nyayamrita` | – | no_pd_english: no PD English translation |
| Raghunatha Siromani | c. 1477–1547 CE | `raghunatha_siromani_works` | – | no_pd_english: no PD English translation |
| Vallabhacharya | c. 1479–1531 CE | `vallabhacharya_works` | – | no_pd_english: no complete PD English translation |
| Chaitanya Mahaprabhu | c. 1486–1534 CE | `chaitanya_mahaprabhu_works` | ⚠ | IA search attempted; Siksastaka 8 verses available |
| Ravidas | 1450–1520 CE | `ravidas_hymns` | – | copyright_trans: hymns in Guru Granth Sahib; modern trans. copyright |
| Mirabai | 1498–1557 CE | `mirabai_poems` | ⚠ | Alston 1980 copyright; older IA versions attempted |
| Guru Nanak | c. 1469–1539 CE | `guru_nanak_japji` | ✓ | Macauliffe 1909 trans. (PD) |
| Madhusudana Sarasvati | c. 1540–1640 CE | `madhusudana_sarasvati_works` | – | no_pd_english: no PD English translation |
| Vijnana Bhikshu | c. 1550–1600 CE | `vijnana_bhikshu_works` | – | no_pd_english: no PD English translation |
| Gadadhara Bhattacharya | 17th c. CE | *(not in script)* | – | no_pd_english: no PD English translation of Nyaya works |
| Debendranath Tagore | 1817–1905 CE | `debendranath_tagore_autobiography` | ✓ | Sykes 1914 trans. (PD) |
| Dayananda Saraswati | 1824–1883 CE | `dayananda_satyartha_prakash` | ✓ | PD translation via IA |
| Sai Baba of Shirdi | 1835–1918 CE | *(not in script)* | – | no_pd_english: no primary philosophical text; teachings compiled posthumously |
| Ramakrishna Paramahamsa | 1836–1886 CE | `gospel_ramakrishna` | ✓ | Nikhilananda trans. |
| Swami Vivekananda | 1863–1902 CE | `vivekananda_complete_works` | ✓ | Complete Works via IA |
| Narayana Guru | 1856–1928 CE | *(not in script)* | – | no_pd_english: no accessible PD English translation of primary works |
| Rabindranath Tagore | 1861–1941 CE | `tagore_gitanjali` | ✓ | PG #7164 (1913, PD) |
| Mahatma Gandhi | 1869–1948 CE | `gandhi_hind_swaraj` | ✓ | PG #23440 (1909, PD) |
| Sri Aurobindo | 1872–1950 CE | `aurobindo_life_divine` | ✓ | 1939–40 ed., PD in many jurisdictions |
| Muhammad Iqbal | 1877–1938 CE | `iqbal_reconstruction` | ✓ | *Reconstruction of Religious Thought in Islam* (1930) via IA |
| Ramana Maharshi | 1879–1950 CE | `ramana_maharshi_who_am_i` | ✓ | *Who Am I?* PD pamphlet |
| Sarvepalli Radhakrishnan | 1888–1975 CE | `radhakrishnan_indian_philosophy` | ✓ | *Indian Philosophy* Vol.1 (1923, PD) |
| B.R. Ambedkar | 1891–1956 CE | `ambedkar_buddha_and_dhamma` | ✓ | *The Buddha and His Dhamma* (1956, PD) |

### Japan — Heian through Edo (774–1868 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Kukai | 774–835 CE | `kukai_eliot_japanese_buddhism` | ⚠ | Eliot *Japanese Buddhism* (1935) secondary; Hakeda 1972 copyright |
| Genshin | 942–1017 CE | `genshin_ojoyoshu` | ✓ | Pure Land texts via IA |
| Honen | 1133–1212 CE | `kukai_eliot_japanese_buddhism` | ⚠ | Covered by Eliot umbrella; Coates 1949 restricted |
| Shinran | 1173–1261 CE | `shinran_buddhist_psalms` | ✓ | Yamabe & Beck 1921 trans. (PD) |
| Dogen | 1200–1253 CE | `dogen_shobogenzo` | ✓ | Older IA edition |
| Nichiren | 1222–1282 CE | `nichiren_writings` | ⚠ | Anesaki 1916 secondary (PD) |
| Zeami Motokiyo | c. 1363–1443 CE | `zeami_noh_treatises` | – | copyright_trans: Rimer & Yamazaki 1984 copyright |
| Yoshida Kenko | c. 1330 CE | `kenko_essays_idleness` | ⚠ | Aston 1899 *History of Japanese Literature* secondary; all direct trans. post-1923 |
| Fujiwara Seika | 1561–1619 CE | `fujiwara_seika_works` | – | no_pd_english: no PD English translation |
| Miyamoto Musashi | 1584–1645 CE | `musashi_book_five_rings` | ⚠ | IA search attempted; Harris and Wilson trans. both copyright |
| Kumazawa Banzan | 1619–1691 CE | `kumazawa_banzan_works` | – | no_pd_english: no PD English translation |
| Ito Jinsai | 1627–1705 CE | `ito_jinsai_works` | – | no_pd_english: no PD English translation |
| Kaibara Ekken | 1630–1714 CE | `kaibara_ekken_works` | ⚠ | IA search attempted; Tucker 1989 copyright |
| Ogyu Sorai | 1666–1728 CE | `ogyu_sorai_works` | – | no_pd_english: no PD English translation |
| Hakuin Ekaku | 1686–1769 CE | `suzuki_essays_zen` | ⚠ | Suzuki *Outlines of Mahayana Buddhism* (1907) secondary; Waddell trans. copyright |
| Tominaga Nakamoto | 1715–1746 CE | `tominaga_nakamoto_works` | – | no_pd_english: no PD English translation |
| Motoori Norinaga | 1730–1801 CE | `motoori_norinaga_works` | – | no_pd_english: Nishimura 1997 copyright |
| Nishi Amane | 1829–1897 CE | `nishi_amane_works` | – | no_pd_english: no PD English translation |
| Nishida Kitaro | 1870–1945 CE | `nishida_inquiry_into_good` | ✓ | Older PD edition via IA |
| D.T. Suzuki | 1870–1966 CE | `suzuki_essays_zen_buddhism` | ✓ | *Essays in Zen Buddhism* (1927) via IA |

### Korea (617–1950 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Wonhyo | 617–686 CE | `wonhyo_awakening_faith` | ⚠ | Park 1960 thesis (secondary); no PD English primary translation |
| Woncheuk | 613–696 CE | `woncheuk_commentaries` | – | no_pd_english: no PD English translation |
| Uisang | 625–702 CE | `uisang_dharmadhatu` | – | no_pd_english: no PD English translation |
| Doseon | 827–898 CE | `doseon_works` | – | no_pd_english: no PD English translation |
| Ch'oe Ch'i-won | b. 857 CE | `choe_chi_won_works` | – | no_pd_english: no PD English translation |
| Jinul | 1158–1210 CE | `jinul_works` | – | copyright_trans: Buswell 1991 copyright; no PD English |
| Chong Tojon | 1342–1398 CE | `chong_tojon_works` | – | no_pd_english: no PD English translation |
| Yi Hwang (Toegye) | 1501–1570 CE | `yi_hwang_toegye_works` | – | no_pd_english: no PD English translation |
| Yi I (Yulgok) | 1536–1584 CE | `yi_i_yulgok_works` | – | no_pd_english: no PD English translation |
| Chong Yagyong (Dasan) | 1762–1836 CE | `chong_yagyong_dasan_works` | – | no_pd_english: no PD English translation |

### Tibet (8th–20th c. CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Padmasambhava (attr.) | c. 8th c. CE | `tibetan_book_of_dead` | ✓ | Evans-Wentz 1927 trans. (PD) |
| Sakya Pandita | 1182–1251 CE | `sakya_pandita_works` | – | no_pd_english: no PD English translation |
| Rangjung Dorje | 1284–1339 CE | `rangjung_dorje_works` | – | no_pd_english: no PD English translation |
| Dolpopa | 1292–1361 CE | `dolpopa_mountain_dharma` | – | no_pd_english: Stearns 1999 copyright |
| Longchenpa | 1308–1364 CE | `longchenpa_guhyagarbha` | ✓ | Guhyagarbha Tantra commentary — IA open access |
| Gyeltsap Darma Rinchen | 1364–1432 CE | `gyeltsap_darma_rinchen_works` | – | no_pd_english: no PD English translation |
| Je Tsongkhapa | 1357–1419 CE | `waddell_buddhism_tibet` | ⚠ | Waddell 1895 secondary; no PD primary Lamrim translation |
| Gorampa | 1429–1489 CE | `gorampa_works` | – | no_pd_english: no PD English translation |
| Sakya Chokden | 1428–1507 CE | `sakya_chokden_works` | – | no_pd_english: no PD English translation |
| Wangchuk Dorje | 1556–1603 CE | `wangchuk_dorje_works` | – | no_pd_english: no PD English translation |
| Mikyö Dorje | 1507–1554 CE | `mikyo_dorje_works` | – | no_pd_english: no PD English translation |
| Jamyang Khyentse Wangpo | 1820–1892 CE | `jamyang_khyentse_wangpo_works` | – | no_pd_english: no PD English translation |
| Jamgon Kongtrul | 1813–1899 CE | `jamgon_kongtrul_works` | – | copyright_trans: Guarisco & McLeod 2010 copyright |
| Jamgon Ju Mipham | 1846–1912 CE | `mipham_works` | – | no_pd_english: no PD English translation |

---

## WESTERN PHILOSOPHERS

### Pre-Socratics (620–400 BCE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Thales, Anaximander, Anaximenes | c. 624–546 BCE | `pre_socratics_burnet` | ✓ | Burnet *Early Greek Philosophy* (PG search) |
| Pythagoras | c. 580–500 BCE | `pre_socratics_burnet` | ✓ | Covered in Burnet and Fairbanks |
| Xenophanes, Heraclitus, Parmenides | c. 570–450 BCE | `pre_socratics_burnet` + `pre_socratics_fairbanks` | ✓ | Both Burnet and Fairbanks |
| Empedocles, Zeno, Democritus | c. 492–370 BCE | `pre_socratics_fairbanks` | ✓ | Fairbanks *Handbook of Greek Philosophy* |
| Socrates | c. 470–399 BCE | `plato_*_jowett` | ✓ | Socratic dialogues in Plato's works |

### Classical & Hellenistic Greece (400–100 BCE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Plato | c. 427–347 BCE | `plato_*_jowett` | ✓ | 9 dialogues via PG (Jowett trans.) |
| Aristotle | c. 384–322 BCE | `aristotle_*` | ✓ | 5 works: Ethics, Metaphysics, Politics, Physics, De Anima |
| Epicurus | c. 341–270 BCE | `epicurus_diogenes_laertius` | ✓ | PG #51 (Yonge trans.) |
| Zeno of Citium | c. 333–264 BCE | `zeno_citium_stoic` | – | lost_work: writings lost; in Diogenes Laertius Book VII (PG #51) |
| Lucretius | c. 99–55 BCE | `lucretius_de_rerum_natura` | ✓ | Munro trans. (PG #785) |

### Classical Rome & Stoics (100 BCE–300 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Cicero | 106–43 BCE | `cicero_nature_of_gods` | ✓ | PG #14988 (Yonge trans.) |
| Philo of Alexandria | c. 20 BCE–50 CE | `philo_alexandria_works` | ✓ | Yonge 1854 trans. (PD) |
| Seneca | c. 4 BCE–65 CE | `seneca_letters_lucilius` | ✓ | Gutendex search |
| Epictetus | c. 55–135 CE | `epictetus_enchiridion` + `epictetus_discourses` | ✓ | PG search + IA |
| Marcus Aurelius | 121–180 CE | `marcus_aurelius_meditations` | ✓ | PG #2680 |
| Plotinus | c. 205–270 CE | `plotinus_enneads_mackenna` | ✓ | MacKenna trans. via IA |
| Porphyry | c. 232–304 CE | `porphyry_isagoge` | ✓ | Taylor trans. (PD) |
| Iamblichus | c. 245–325 CE | `iamblichus_pythagorean_life` | ✓ | Taylor 1818 trans. (PD) |

### Early Christianity & Late Antiquity (200–600 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Origen | c. 184–253 CE | `origen_de_principiis` | ✓ | Ante-Nicene Fathers via IA |
| Hypatia | c. 360–415 CE | `hypatia_works` | – | lost_work: works lost; known through Synesius letters |
| Proclus | c. 412–485 CE | `proclus_elements_theology` | ✓ | Taylor 1816 trans. (PD) |
| Augustine of Hippo | c. 354–430 CE | `augustine_confessions` + `augustine_city_of_god` | ✓ | PG #3296 + Gutendex search |
| Pseudo-Dionysius | c. 500 CE | `pseudo_dionysius_divine_names` | ✓ | Parker 1897 trans. (PD) |
| John Philoponus | c. 490–570 CE | `john_philoponus_works` | ⚠ | IA search attempted; Share 2005 copyright |
| Eusebius | c. 260–339 CE | `eusebius_church_history` | ✓ | IA |
| Jerome | c. 347–420 CE | `jerome_letters` | ✓ | IA |
| Boethius | c. 480–524 CE | `boethius_consolation_philosophy` | ✓ | PG #14328 |
| Benedict of Nursia | c. 480–547 CE | `benedict_rule` | ✓ | IA |
| Isidore of Seville | c. 560–636 CE | `isidore_seville_etymologiae` | – | no_pd_english: Barney et al. 2006 copyright |

### Islamic Philosophy (632–1400 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Muhammad / Quran | c. 570–632 CE | `quran_rodwell` | ✓ | Rodwell trans. via IA |
| Al-Kindi | c. 801–873 CE | `al_kindi_first_philosophy` | ✓ | IA |
| Al-Farabi | c. 870–950 CE | `al_farabi_virtuous_city` | ✓ | IA |
| Al-Razi | c. 865–925 CE | `al_razi_spiritual_medicine` | ⚠ | IA search attempted; Arberry 1950 copyright |
| Avicenna | c. 980–1037 CE | `avicenna_book_of_healing` | ✓ | IA |
| Al-Biruni | c. 973–1050 CE | `al_biruni_india` | ✓ | Sachau 1887/1910 trans. (PD) |
| Ibn Hazm | 994–1064 CE | `ibn_hazm_ring_dove` | ✓ | Nykl 1931 trans. (PD) |
| Al-Ghazali | c. 1058–1111 CE | `al_ghazali_incoherence` + `al_ghazali_deliverance_error` | ✓ | IA |
| Ibn Tufayl | c. 1105–1185 CE | `ibn_tufayl_hayy` | ✓ | Ockley 1708 trans. (PD) |
| Averroes | c. 1126–1198 CE | `averroes_tahafut` | ✓ | IA |
| Fakhr al-Din al-Razi | 1149/50–1209 CE | `fakhr_al_din_al_razi_works` | – | no_pd_english: no PD English translation |
| Suhrawardi | c. 1154–1191 CE | `suhrawardi_philosophy_illumination` | ⚠ | IA search attempted; Walbridge & Ziai 1999 copyright |
| Ibn Arabi | 1165–1240 CE | `ibn_arabi_tarjuman` | ✓ | Nicholson 1911 trans. (PD) |
| Ibn Khaldun | 1332–1406 CE | `ibn_khaldun_muqaddimah` | ✓ | de Slane 1863 trans. (PD) |
| Ibn Taymiyya | c. 1263–1328 CE | `ibn_taymiyya_works` | ⚠ | IA search attempted; partial PD translations |
| Molla-Sadra | 1572–1640 CE | `molla_sadra_asfar` | – | no_pd_english: no PD English translation |

### Jewish Philosophy (900–1600 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Saadia Gaon | c. 882–942 CE | `saadia_gaon_emunot` | ⚠ | IA search attempted; Rosenblatt 1948 copyright |
| Ibn Gabirol | c. 1021–1058 CE | `ibn_gabirol_fons_vitae` | ✓ | Myer 1888 trans. (PD) |
| Yehudah Halevi | c. 1075–1141 CE | `halevi_kuzari` | ✓ | Hirschfeld 1905 trans. (PD) |
| Maimonides | c. 1135–1204 CE | `maimonides_guide_perplexed` | ✓ | Friedlander trans. via IA |
| Hasdai Crescas | c. 1340–1411 CE | `crescas_or_adonai` | ✓ | Wolfson 1929 trans. (PD) |

### Medieval & Scholastic Christianity (700–1500 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| John of Damascus | c. 680–750 CE | `john_damascus_orthodox_faith` | ✓ | Salmond trans. via IA |
| Alcuin | c. 735–804 CE | `alcuin_works` | ⚠ | IA search attempted; no standalone PD English confirmed |
| John Scotus Eriugena | c. 815–877 CE | `eriugena_periphyseon` | ✓ | IA |
| Anselm | c. 1034–1109 CE | `anselm_proslogion_cur_deus` | ✓ | IA |
| Omar Khayyam | c. 1048–1131 CE | `omar_khayyam_rubaiyat_fitzgerald` | ✓ | FitzGerald trans. (PG #246) |
| Peter Abelard | c. 1079–1142 CE | `abelard_sic_et_non` | ⚠ | IA search attempted; no complete PD English trans. |
| Peter Lombard | c. 1100–1160 CE | `peter_lombard_sentences` | – | no_pd_english: Silano 2007–2010 copyright |
| Robert Grosseteste | c. 1175–1253 CE | `grosseteste_de_luce` | ✓ | Riedl 1942 trans. (PD) |
| Francis of Assisi | c. 1182–1226 CE | `francis_assisi_little_flowers` | ✓ | PG #655 |
| Albert the Great | c. 1193–1280 CE | `albertus_magnus_works` | – | no_pd_english: no complete PD English translation |
| Roger Bacon | c. 1214–1294 CE | `roger_bacon_opus_majus` | ✓ | Burke 1928 trans. (PD) |
| Thomas Aquinas | c. 1221–1274 CE | `aquinas_summa_theologica` | ✓ | IA |
| Bonaventure | c. 1225–1274 CE | `bonaventure_soul_journey` | ✓ | de Vinck trans. (PD) |
| Ramon Llull | c. 1232–1315 CE | `ramon_llull_ars_magna` | ⚠ | IA search attempted; no complete PD English trans. |
| Meister Eckhart | c. 1260–1328 CE | `meister_eckhart_sermons` | ✓ | Evans trans. via IA |
| Dante | c. 1265–1321 CE | `dante_divine_comedy_cary` | ✓ | Cary trans. (PG #8800) |
| Duns Scotus | c. 1266–1308 CE | `duns_scotus_ordinatio` | – | no_pd_english: Wolter 1954 copyright |
| Marsilius of Padua | c. 1270–1342 CE | `marsilius_defensor_pacis` | ✓ | Previte-Orton 1928 trans. (PD) |
| William of Ockham | c. 1288–1348 CE | `ockham_summa_logicae` | ✓ | IA |
| Jean Buridan | c. 1300–1358 CE | `buridan_summulae` | – | no_pd_english: Zupko 2001 copyright |
| John Wycliffe | c. 1320–1384 CE | `wycliffe_on_truth` | ✓ | IA |
| Nicole Oresme | c. 1320–1382 CE | `oresme_de_moneta` | ✓ | Johnson 1956 trans. (PD) |
| Julian of Norwich | c. 1342–1416 CE | `julian_norwich_revelations` | ✓ | Gutendex search |
| Gemistus Pletho | c. 1355–1452 CE | `pletho_de_differentiis` | – | no_pd_english: Woodhouse 1986 copyright |
| Thomas à Kempis | c. 1380–1471 CE | `thomas_kempis_imitation_christ` | ✓ | PG #1653 |
| Nicholas of Cusa | 1401–1464 CE | `nicholas_cusa_learned_ignorance` | ✓ | IA |
| Lorenzo Valla | 1407–1457 CE | `valla_donation_constantine` | ✓ | Coleman 1922 trans. (PD) |
| Marsilio Ficino | 1433–1499 CE | `ficino_platonic_theology` | ⚠ | Allen 2001 copyright; IA search for older PD trans. |
| Pico della Mirandola | 1463–1494 CE | `pico_mirandola_oration` | ✓ | Forbes 1907 trans. (PD) |

### Renaissance & Early Modern (1450–1650 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Erasmus | 1466–1536 CE | `erasmus_praise_of_folly` | ✓ | PG #9371 |
| Machiavelli | 1469–1527 CE | `machiavelli_prince` | ✓ | PG #1232 |
| Copernicus | 1473–1543 CE | `copernicus_de_revolutionibus` | ✓ | Dobson/Brodetsky 1947 trans. (PD) |
| Thomas More | 1478–1535 CE | `more_utopia` | ✓ | PG #2130 |
| Martin Luther | 1483–1546 CE | `luther_works_selected` | ✓ | PG #274 |
| John Calvin | 1509–1564 CE | `calvin_institutes` | ✓ | Beveridge trans. via IA |
| Montaigne | 1533–1592 CE | `montaigne_essays` | ✓ | Gutendex search |
| Giordano Bruno | 1548–1600 CE | `bruno_infinite_universe` | ✓ | Singer 1950 trans. (PD) |
| Francisco Suarez | 1548–1617 CE | `suarez_metaphysical_disputations` | – | no_pd_english: no complete PD English translation |
| Francis Bacon | 1561–1626 CE | `bacon_novum_organum` | ✓ | Gutendex search |
| Galileo | 1564–1642 CE | `galileo_dialogue` | ✓ | Older PD editions via IA |
| Kepler | 1571–1630 CE | `kepler_harmonices_mundi` | – | no_pd_english: Aiton et al. 1997 copyright |
| Molla-Sadra | 1572–1640 CE | `molla_sadra_asfar` | – | no_pd_english: no PD English translation |
| Hugo Grotius | 1583–1645 CE | `grotius_law_war_peace` | ✓ | Whewell 1853 trans. (PD) |
| Thomas Hobbes | 1588–1679 CE | `hobbes_leviathan` | ✓ | PG #3207 |
| René Descartes | 1596–1650 CE | `descartes_discourse_method` | ✓ | PG #59 |

### Rationalism & Empiricism (1623–1780 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Blaise Pascal | 1623–1662 CE | `pascal_pensees` | ✓ | Gutendex search |
| Margaret Cavendish | 1623–1673 CE | `cavendish_observations` | ✓ | 1666, PD via IA |
| Baruch Spinoza | 1632–1677 CE | `spinoza_ethics` | ✓ | PG #3800 |
| John Locke | 1632–1704 CE | `locke_essay_human_understanding` | ✓ | PG #10615 |
| Gottfried Leibniz | 1646–1716 CE | `leibniz_monadology` | ✓ | IA |
| George Berkeley | 1685–1753 CE | `berkeley_principles_human_knowledge` | ✓ | PG #4723 |
| David Hume | 1711–1776 CE | `hume_treatise_human_nature` + `hume_enquiry_human_understanding` | ✓ | PG #4705 + PG #9662 |
| Jean-Jacques Rousseau | 1712–1778 CE | `rousseau_social_contract` | ✓ | Gutendex search |

### Enlightenment (1700–1800 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Voltaire | 1694–1778 CE | `voltaire_candide` | ✓ | PG #19942 |
| Edmund Burke | 1729–1797 CE | `burke_reflections_revolution` | ✓ | PG #2173 |
| Adam Smith | 1723–1790 CE | `adam_smith_moral_sentiments` | ✓ | Gutendex search |
| Immanuel Kant | 1724–1804 CE | `kant_critique_pure_reason` | ✓ | PG #4280 |
| Thomas Paine | 1737–1809 CE | `paine_rights_of_man` | ✓ | PG #3742 |
| Jeremy Bentham | 1748–1832 CE | `bentham_principles_morals` | ✓ | PG #781 |
| Mary Wollstonecraft | 1759–1797 CE | `wollstonecraft_vindication` | ✓ | PG #3420 |
| Friedrich Schleiermacher | 1768–1834 CE | `schleiermacher_on_religion` | ✓ | Oman 1893 trans. (PD) |
| Johann Gottlieb Fichte | 1762–1814 CE | `fichte_vocation_of_man` | ✓ | PG #38088 |
| G.W.F. Hegel | 1770–1831 CE | `hegel_phenomenology_spirit` + `hegel_philosophy_right` | ✓ | IA |
| F.W.J. von Schelling | 1775–1854 CE | `schelling_system_idealism` | – | copyright_trans: Heath 1978 copyright |

### 19th Century (1800–1900 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Ralph Waldo Emerson | 1803–1882 CE | `emerson_essays_first_series` + `emerson_nature` | ✓ | PG #2944 + PG #29433 |
| Ludwig Feuerbach | 1804–1872 CE | `feuerbach_essence_christianity` | ✓ | Evans 1854 trans. (PG #4955) |
| Arthur Schopenhauer | 1788–1860 CE | `schopenhauer_world_will_representation` | ✓ | PG #38427 |
| Auguste Comte | 1798–1857 CE | `comte_general_view_positivism` | ✓ | Bridges 1865 trans. (PD) |
| Pierre-Joseph Proudhon | 1809–1865 CE | `proudhon_what_is_property` | ✓ | Tucker 1876 trans. (PG #360) |
| Søren Kierkegaard | 1813–1855 CE | `kierkegaard_selections` | ✓ | PG #60333 |
| Michael Bakunin | 1814–1876 CE | `bakunin_god_and_state` | ✓ | PG #36776 |
| Karl Marx | 1818–1883 CE | `marx_communist_manifesto` | ✓ | PG #61 |
| Herbert Spencer | 1820–1903 CE | `spencer_first_principles` | ✓ | PG #4350 |
| Henry David Thoreau | 1817–1862 CE | `thoreau_walden` | ✓ | PG #205 |
| John Stuart Mill | 1806–1873 CE | `mill_utilitarianism` | ✓ | PG #11224 |
| Wilhelm Dilthey | 1833–1911 CE | `dilthey_introduction_human_sciences` | – | no_pd_english: Rickman 1976 copyright |
| Charles Sanders Peirce | 1839–1914 CE | `peirce_pragmatism_essays` | ✓ | IA (1878 Popular Science Monthly essays, PD) |
| Franz Brentano | 1838–1917 CE | `brentano_psychology_empirical` | – | copyright_trans: Rancurello et al. 1973 copyright |
| Friedrich Nietzsche | 1844–1900 CE | `nietzsche_beyond_good_evil` + `nietzsche_zarathustra` | ✓ | PG #4363 + PG #1998 |
| Gottlob Frege | 1848–1925 CE | `frege_begriffsschrift` | – | copyright_trans: van Heijenoort 1967 copyright |
| William James | 1842–1910 CE | `james_varieties_religious_experience` + `james_pragmatism` | ✓ | Gutendex search + PG #5116 |

### Early 20th Century (1900–1950 CE)

| Philosopher | Dates | Label | Status | Notes |
|---|---|---|---|---|
| Bertrand Russell | 1872–1970 CE | `russell_problems_of_philosophy` | ✓ | PG #5827 (1912, PD) |
| Max Weber | 1864–1920 CE | `weber_protestant_ethic` | ✓ | Parsons 1930 trans. via IA |
| Sigmund Freud | 1856–1939 CE | `freud_interpretation_dreams` | ✓ | Brill 1913 trans. (PG #39521) |
| Edmund Husserl | 1859–1938 CE | `husserl_ideas_phenomenology` | ✓ | Boyce Gibson 1931 trans. (PD) via IA |
| Henri Bergson | 1859–1941 CE | `bergson_creative_evolution` | ✓ | Mitchell 1911 trans. (PG #26163) |
| John Dewey | 1859–1952 CE | `dewey_reconstruction_philosophy` | ✓ | PG #40089 |
| Ludwig Wittgenstein | 1889–1951 CE | `wittgenstein_tractatus` | ✓ | Ogden 1922 trans. (PG #5740) |
| Martin Heidegger | 1889–1976 CE | `heidegger_being_and_time` | – | copyright_trans: Macquarrie & Robinson 1962; Stambaugh 1996; both copyright |
| Jean-Paul Sartre | 1905–1980 CE | `sartre_existentialism_humanism` | ✓ | 1945 lecture, PD reprints via IA |
| Simone de Beauvoir | 1908–1986 CE | `beauvoir_second_sex` | – | copyright_trans: Parshley 1953; Borde & Malovany-Chevallier 2010; both copyright |
| Albert Camus | 1913–1960 CE | `camus_myth_sisyphus` | – | copyright_trans: O'Brien 1955 copyright |

---

## Summary Statistics

| Category | Total on Timeline | ✓ Fetchable | ⚠ Secondary/Partial | – Unavailable |
|---|---|---|---|---|
| Eastern philosophers | ~200+ | ~55 | ~30 | ~115 |
| Western philosophers | ~300+ | ~90 | ~15 | ~30 |
| **Combined** | **~500+** | **~145** | **~45** | **~145** |

---

## Primary Patterns in Unavailability

1. **Copyright wall on 20th-century translations** — Most serious academic translations of Chinese, Japanese, Korean, and Tibetan texts were produced 1960–2010 and remain in copyright. This affects the entire Kyoto School, Korean Neo-Confucianism, most Tibetan Buddhism beyond Longchenpa, and most Tang–Song Chan Buddhism.

2. **Lost works** — A significant fraction of early Chinese (Warring States sub-schools), Ajivika, and Cynic texts are entirely lost. These entries are retained so the gap is visible.

3. **No English translation ever made** — Many Korean philosophers (Yi Hwang, Yi I, Chong Yagyong) and most Edo-period Japanese philosophers (Ogyu Sorai, Ito Jinsai) have never been translated into English at all.

4. **Post-1950 contemporary philosophers** — The Eastern timeline stops at 1950; the Western timeline continues but 20th-century philosophical works are almost uniformly in copyright. Only texts published before ~1928 (US PD threshold) or explicitly released as PD are included.

---

## Source Reliability Notes

- **Project Gutenberg** IDs are fixed and stable; safest source.
- **SuttaCentral** (Sujato CC0) is the highest-quality Pali Canon source.
- **Internet Archive** quality varies; the `_is_probably_english` heuristic and manual spot-checks are recommended before any training run.
- `fetch_unavailable` entries produce `[N/A]` output with an explanation and do **not** create files; they exist solely to document coverage gaps.a