# Medicine sheet: ind-hi-sangraha-s (rjvim)

Pack: 500 documents, all `ai4bharat/sangraha | synthetic/hin_Deva` (English Wikipedia machine-translated to Hindi). Labels: 464 `fix`, 34 `clean`, 2 `drop`. Most diseases come from the translation step, not from the web.

| Code | Docs | Medicine |
|---|---|---|
| D4 | 458 | M2, M3 (plus a source-level note) |
| A6 | 137 | M1 |
| C3 | 25 | M7 |
| B4 | 12 | M4 |
| C2 | 8 | M6 |
| B2 | 7 | M5 (also covers B3 `<unk>`, 5 docs) |

**Harm test.** The code for every medicine is in `harm_test.py` (next to this file). It runs on any parquet file with a `text` column:
`python harm_test.py <gold.parquet>`. The Data A / Data B Hindi gold set is not in the repository yet (checked 29 Oct). Until it is, the numbers below come from a **proxy gold set**: the 34 documents of this pack that I labelled `clean`. I will replace them with gold-set numbers when the gold set is published. The "pack" column shows how many of the 500 pack documents each medicine touches (its reach, not harm).

| Medicine | Action | Pack (500): changed / dropped | Proxy gold (34): changed / dropped | Result |
|---|---|---|---|---|
| M1 A6 visarga as colon | fix | 120 / 0 | 0 / 0 (0.00%) | PASS |
| M2 D4 empty parentheses | fix | 39 / 0 | 0 / 0 (0.00%) | PASS |
| M3 D4 danda-glued abbreviations (≥3) | drop | 0 / 38 | 0 / 0 (0.00%) | PASS |
| M4 B4 template junk | fix | 12 / 0 | 0 / 0 (0.00%) | PASS |
| M5 B2/B3 tags and `<unk>` | fix (drop if many) | 6 / 3 | 0 / 0 (0.00%) | PASS |
| M6 C2 phrase repeated 3+ times | drop | 0 / 6 | 0 / 0 (0.00%) | PASS |
| M7 C3 empty section headings | fix | 68 / 0 | 0 / 0 (0.00%) | PASS |

A proxy gold set of 34 can only show a failure above 1 changed document (2.9%). It cannot prove the 1% limit. The real gold-set run is needed for that.

## M1: visarga `ः` (U+0903) used as a colon

1. **Disease:** A6, 137 docs. The colon after a Devanagari word became the visarga `ः` (hex `e0 a4 83`). Examples: `0901d3609c93ba66` (`संयोजन हैः डल्ला`), `257cef1fe99b6355` (`निम्नलिखित बच्चे थेः`), `70bab8ad5d120193` (`जनसंख्याः 3,052`).
2. **Medicine:** replace `ः` with `:` when it ends a word and is followed by a line end or by a space and more text, unless the word is a real visarga word (प्रायः, अतः, पुनः, क्रमशः, …). Code: `m1_visarga_colon` in `harm_test.py`.
3. **Action:** fix.
4. **Harm test:** proxy gold 0 of 34 changed. Gold set: pending.
5. **Side effects:** a Sanskrit-style word that ends in visarga and is not in the `KEEP` list (for example a rare `-तः` adverb) loses its visarga. `स्रोतः` as a heading ("Source:") is changed correctly. The same word used as Sanskrit would be changed too.

## M2: empty parentheses after dropped foreign-script text

1. **Disease:** D4. The original name in another script was deleted, leaving `()`, `(,)` or `(,,)`. Found in 39 docs. Examples: `22fd653de4dd666a` (`स्टोरस्ट्रोम पुल (,)`), `257cef1fe99b6355` (`वाल्डेमार द विक्टियर ()`), `a2298260d4c4d456` (`प्लिस्टोस (,,)`).
2. **Medicine:** `re.sub(r"(?<=[\sऀ-ॿ])\s*\(\s*[,;]*\s*\)", "", text)`. The lookbehind keeps code such as `f()`.
3. **Action:** fix.
4. **Harm test:** proxy gold 0 of 34. Gold set: pending.
5. **Side effects:** removes `()` written after a Devanagari word on purpose, which is rare.

## M3: abbreviations cut by a danda (`बी के सहयोगी थे।एफ।`, `एफ।सी।`)

1. **Disease:** D4. English initials such as "B. F." and "F.C." were split into sentences. The period became `।`, with no space after it. Found in 38 docs at 3 or more hits each. Examples: `635cbbdde03f1dad`, `1977bf6aaac83a24`, `5700b1ccb1a5ed64`.
2. **Medicine:** count `re.findall(r"[ऀ-ॿ]।[ऀ-ॿ]", text)`. Drop the document at 3 or more hits. The text cannot be repaired safely, because the original initials are lost.
3. **Action:** drop when there are 3 or more hits.
4. **Harm test:** proxy gold 0 of 34. Gold set: pending.
5. **Side effects:** native web Hindi that leaves out the space after `।` would be dropped. The threshold of 3 is there to limit this.

## M4: translated wiki-template and placeholder junk

1. **Disease:** B4, 12 docs. Wikitable markup was translated (`!कोलन = 9| प्रदर्शनी खेल`, `! शैली = "पृष्ठभूमिः #ffcc00; …"|`), and formula or score placeholders remain (`(सूत्र _ 1)`, `<ID1`, `<5>`). Examples: `1b0e1771a362f1a5`, `487a621e98c3ad74`, `4a26d9ce3fbaa87b`.
2. **Medicine:** delete lines that start with `!` or `|` and contain `कोलन`, `शैली` or `=`, and lines with `|… =}}`. Delete the placeholder tokens `(सूत्र _ N)`, `<IDN` and `<N>`. Code: `m4_template_junk`.
3. **Action:** fix.
4. **Harm test:** proxy gold 0 of 34. Gold set: pending.
5. **Side effects:** a real `<5>` in maths text would be removed. Formula documents lose the formula slot, because there was no formula left to keep.

## M5: markup tags (Latin or translated into Devanagari) and `<unk>`

1. **Disease:** B2, 7 docs, plus B3 `<unk>` in 5 docs. Examples: `94f9ac0d9c39d021` (`<बी. आर.>`, a translated `<br>`), `97c453c003f59b98` (`</रेफ>`), `8d4a1eb74b3a464c` (a whole MediaWiki XML header with translated tags, dropped). The `<unk>` docs `59aef801fa585bdf` and `a285d1d618a6c203` have up to 288 `<unk>` tokens where Japanese or Chinese text was.
2. **Medicine:** drop the document when it has 3 or more `<unk>` or 5 or more Devanagari tags. Otherwise remove the known tags (`br`, `ref`, `बी. आर.`, `रेफ`, …) and `<unk>`. Code: `m5_tags`.
3. **Action:** fix, or drop when there are many.
4. **Harm test:** proxy gold 0 of 34. Gold set: pending.
5. **Side effects:** an article about HTML or tokenizers that quotes these tags would be changed.

## M6: phrase repeated 3+ times in a row (translation loop)

1. **Disease:** C2, 8 docs. The translator got stuck in a loop. Examples: `adc639e30cf4b95b` (`और उत्तर में लॉर्ड कैपिटल्स,` repeated, then cut off), `38ea6e7718826a61` (`हदीस उल्रिका (हदीस उल्रिका),` 7 times), `59aef801fa585bdf`.
2. **Medicine:** `re.search(r"(\S.{9,80}?)(?:[\s,]*\1){2,}", text)`, which drops the document.
3. **Action:** drop.
4. **Harm test:** proxy gold 0 of 34. Gold set: pending.
5. **Side effects:** poems, song lyrics and lists with a real refrain would be dropped.

## M7: empty sections (table or list dropped, heading left)

1. **Disease:** C3, 25 docs. The text ends, or a section ends, in a heading or caption with no body, for example `अनुसूची।`, `स्रोतः`, or `"23 फरवरी 2020 तक अद्यतन किया गया।`. Examples: `131b86eb077ba739`, `ec95ed1fb82e3503`, `8d73071e61bd24ef`.
2. **Medicine:** remove a heading line (3 words or fewer, ending in `।`, `ः` or `:`) when the next non-empty line is also a heading or the document ends. Code: `m7_empty_sections`. A first version (5 words or fewer) changed 2 of 34 proxy gold documents. It cut the line `जीवनी।` because the next line was a short sentence, so I tightened it to 3 words.
3. **Action:** fix.
4. **Harm test:** proxy gold 0 of 34 after the fix. Gold set: pending.
5. **Side effects:** a short real sentence directly before another short sentence can look like a heading, so it can be removed.

## Other findings (no medicine)

- **Proper names translated as common words (D4)** are the most common error in this pack. For example, Fansler became `प्रशंसक` (`3878784268dd0561`), Maidman became `नौकरानी` (`99184df1a9f23e59`), Price became `कीमत` (`64fe6627135b0e41`), and the Pittsburgh Pirates became `पिट्सबर्ग समुद्री डाकू`. No regex can find these. Suggestion for spec v1: give `synthetic/hin_Deva` a lower sampling weight than native Hindi sources.
- **Templated stubs:** docs 70/173/300 (baseball seasons) and 151/405 (lists of historic places) share 40–67% of their 5-word shingles, because they follow the same Wikipedia template, not because they are copies. I did not label them H2.
- **Partial reads:** two very long documents (`read=partial`) were not read line by line to the end.
