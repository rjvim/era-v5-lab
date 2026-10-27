# Medicine sheet: ind-hi-sangraha-s (rjvim)

Status (27 Oct): draft after the first 150 rows. Counts below are for the first 150 documents. Harm tests on the Hindi gold set follow by Sat 31 Oct.

Pack note: every document is `synthetic/hin_Deva` (machine-translated English Wikipedia). Most diseases come from the translation step, not from the web.

## Medicine 1: visarga `ः` (U+0903) used as a colon

1. **Disease:** A6 (look-alike character). The colon `:` after a Devanagari word was replaced with the visarga `ः` (hex `e0 a4 83`). Count: 46 of the first 150 documents in labels.csv (the regex alone finds 39 of 150 and 120 of 500). Examples: `0901d3609c93ba66` (`संयोजन हैः डल्ला`), `257cef1fe99b6355` (`निम्नलिखित बच्चे थेः`), `70bab8ad5d120193` (`जनसंख्याः 3,052`).
2. **Medicine:** replace `ः` with `:` when it ends a word that is followed by a line end or by a space and more text, and the word is not a real visarga word (प्रायः, अतः, पुनः, सामान्यतः, क्रमशः, दुः-, …).
   ```python
   import re
   KEEP = re.compile(r"(प्राय|अत|पुन|सामान्यत|मुख्यत|स्वत|विशेषत|वस्तुत|क्रमश|अंतत|प्रात|दु|अध|नम|मूलत|संभवत|पूर्णत|स्पष्टत)$")
   RX = re.compile(r"(?<=[क-हा-ौ])ः(?=[ \t]*(?:\n|$)|[ ]+[\"0-9ऀ-ॿ])")
   def fix(t):
       return RX.sub(lambda m: "ः" if KEEP.search(t[max(0, m.start()-10):m.start()]) else ":", t)
   ```
3. **Action:** fix.
4. **Harm test:** pending (gold set). Expected risk: Sanskrit-style words ending in visarga that are not in `KEEP`.
5. **Side effects:** a real visarga word missing from `KEEP` loses its visarga; `स्रोतः` as a heading ("Source:") is correctly changed, but the same word as Sanskrit `स्रोतः` would be changed too.

## Medicine 2: empty parentheses left after dropped foreign-script text

1. **Disease:** D4 (translation damage). The original name in another script was deleted, leaving `()`, `(,)` or `(,,)`. Count: 11 of 150. Examples: `22fd653de4dd666a` (`स्टोरस्ट्रोम पुल (,)`), `257cef1fe99b6355` (`वाल्डेमार द विक्टियर ()`), `a2298260d4c4d456` (`प्लिस्टोस (,,)`).
2. **Medicine:** `re.sub(r"\s*\(\s*[,;]*\s*\)", "", text)`.
3. **Action:** fix.
4. **Harm test:** pending (gold set). Expected near 0: empty parentheses are rare in good prose. Code-like text `f()` must be excluded (add a check that the character before `(` is a space).
5. **Side effects:** removes `()` in function names in technical text.

## Medicine 3: abbreviations split by danda (`बी के सहयोगी थे।एफ।`, `यू है।यह`, `एफ।सी।`)

1. **Disease:** D4. English initials like "B. F." or "U.S." were cut into sentences, and the period became a danda `।` with no space after it. Count: 31 of 150 docs have `।` directly followed by a Devanagari letter. Examples: `635cbbdde03f1dad`, `1977bf6aaac83a24`, `5700b1ccb1a5ed64`.
2. **Medicine:** flag only (cannot be fixed safely): `re.search(r"[ऀ-ॿ]।[ऀ-ॿ]", text)`. Drop the document if there are 3 or more hits.
3. **Action:** drop when >= 3 hits; otherwise keep.
4. **Harm test:** pending (gold set).
5. **Side effects:** native text that leaves out the space after `।` (common in some web Hindi) would be dropped.

## Medicine 4 (candidate): proper names translated as common words

1. **Disease:** D4. Examples: `3878784268dd0561` (Fansler → `प्रशंसक`), `99184df1a9f23e59` (Maidman → `नौकरानी`), `64fe6627135b0e41` (Price → `कीमत`). This is very common in this pack.
2. **Medicine:** none by rule. Report to the TSAI Lab: the synthetic source may need a lower sampling weight.
