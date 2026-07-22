"""Build the Herakleitos corpus from committed raw sources.

Deterministic and offline: parses the files in ``corpus/sources/raw/`` (fetched
once from Wikisource, Project Gutenberg, and the Internet Archive; see SOURCES
below) into ``corpus/data/fragments.jsonl`` and ``corpus/data/contrast.jsonl``.

Run:  python -m corpus.build_corpus [--check]

``--check`` rebuilds into a temp dir and fails if the result differs from the
committed data files (used by CI as a determinism / drift guard).

SOURCES
-------
- dk22b_greek_elwikisource.wikitext   Greek text of DK 22 B fragments,
  el.wikisource.org "Αποσπάσματα (Ηράκλειτος)" (Diels-Kranz text, public domain).
- burnet1920_heraclitus_enwikisource.json   Rendered HTML of en.wikisource
  "Fragments of Heraclitus (annotated)": John Burnet, Early Greek Philosophy,
  3rd ed. 1920 (public domain). DK-numbered; Bywater numbers in parentheses.
- patrick1889_peithosweb_archive.html   G.T.W. Patrick's 1889 translation with
  Bywater's Greek text (public domain), via Internet Archive snapshot of
  classicpersuasion.org (2003).
- dk28b_greek_elwikisource.wikitext   Parmenides, DK 28 B Greek text.
- burnet1920_parmenides_enwikisource.json   Burnet ch. 4 (Parmenides), rendered.
- plato_cratylus_jowett_pg1616.txt / plato_theaetetus_jowett_pg1726.txt
  Jowett translations, Project Gutenberg (public domain).
- marcus_aurelius_long_pg2680.txt   Meditations, George Long translation,
  Project Gutenberg (public domain).

The DK spurious tail (B126b-B139) and a few gaps (B67a, B3a translations) are
not present in any machine-readable public-domain source we could locate; they
are supplied from curated transcriptions below, each flagged
``needs_verification`` in its notes. Verify against a critical edition before
using them in gold-set discrimination items (Phase 1).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "sources" / "raw"
DATA = ROOT / "data"

# --------------------------------------------------------------------------
# Curated scholarship: authenticity labels
# --------------------------------------------------------------------------

# DK 22 B fragments widely flagged as doubtful, paraphrastic, or later
# composites. Everything else parsed from the DK text is labeled genuine;
# B126b-B139 (the DK "Zweifelhaftes, Falsches" tail) are labeled spurious.
DISPUTED: dict[str, str] = {
    "B6a": "Testimonium variant of B6 (Plutarch); not verbatim Heraclitus.",
    "B6b": "Testimonium variant of B6 (stars kindled and quenched); not verbatim.",
    "B49a": "Likely a later composite blending B12 and B91 (Marcovich, Kahn).",
    "B64a": "Apparatus variant transmitted alongside B64 (Hippolytus).",
    "B67a": "Spider simile transmitted only in Latin by Hisdosus Scholasticus; "
    "widely rejected as paraphrase.",
    "B75": "Preserved only as Marcus Aurelius' paraphrase (Med. vi. 42).",
    "B76": "Stoicized doublet of B31/B36 (Marcovich); wording varies by witness.",
    "B82": "Paraphrase in Plato, Hippias Major 289a; not verbatim Heraclitus.",
    "B83": "Paraphrase in Plato, Hippias Major 289b; not verbatim Heraclitus.",
    "B105": "Inference by a Homeric scholiast ('Heraclitus the astrologer'); "
    "not a quotation.",
    "B115": "Attributed to Socrates in Stobaeus; attribution to Heraclitus uncertain.",
    "B122": "Single transmitted word (ἀγχιβασίην); context lost.",
    "B125a": "Curse on the Ephesians (Tzetzes); suspected later embellishment.",
    "B126a": "Classed by DK among the doubtful fragments.",
}

NOTES: dict[str, str] = {
    "B3a": "Derveni papyrus col. IV addition (post-DK); genuine attestation "
    "joining B3 and B94.",
    "B4": "Transmitted only in Latin (Albertus Magnus, De vegetabilibus vi. 401).",
    "B129": "Doubted by early Diels, now generally accepted as genuine "
    "(Diogenes Laertius viii. 6).",
}

# --------------------------------------------------------------------------
# Curated texts: gaps in the machine-readable sources
# --------------------------------------------------------------------------

_NEEDS_VERIFICATION = (
    "needs_verification: transcribed from DK apparatus by the project, no "
    "machine-readable public-domain source located; verify against a critical "
    "edition before gold-set use. Confidence: {conf}."
)

# B67a is present but empty in the el.wikisource text.
CURATED_TEXTS: dict[str, dict[str, str]] = {
    "B67a": {
        "text": "ut aranea stans in medio telae sentit, quam cito musca aliquem "
        "filum eius corrumpit itaque illuc celeriter currit quasi de fili "
        "persectione dolens, sic hominis anima aliqua parte corporis laesa "
        "illuc festine meat quasi impatiens laesionis corporis, cui firme et "
        "proportionaliter iuncta est.",
        "source_author": "Hisdosus Scholasticus, ad Chalcidium in Plat. Tim.",
        "note": "Transmitted in Latin. " + _NEEDS_VERIFICATION.format(conf="medium"),
    },
}

# The DK spurious/doubtful tail. authenticity=spurious for all.
# conf = transcription confidence (see _NEEDS_VERIFICATION).
SPURIOUS_TAIL: list[dict[str, str]] = [
    {
        "dk": "B126b",
        "text": "ἄλλως ἄλλο ἀεὶ αὔξεται πρὸς ὃ ἂν ᾖ ἐλλιπές.",
        "en": "Each thing grows in its own way, according to what it lacks.",
        "source_author": "Anonymus in Platonis Theaetetum",
        "conf": "medium",
    },
    {
        "dk": "B127",
        "text": "εἰ θεοί εἰσιν, ἵνα τί θρηνεῖτε αὐτούς; εἰ δὲ θρηνεῖτε αὐτούς, "
        "μηκέτι τούτους ἡγεῖσθε θεούς.",
        "en": "If they are gods, why do you lament them? And if you lament them, "
        "no longer consider them gods.",
        "source_author": "Aristocritus, Theosophia 69",
        "conf": "high",
    },
    {
        "dk": "B128",
        "text": "δαιμόνων ἀγάλμασιν εὔχονται οὐκ ἀκούουσιν, ὥσπερ ἀκούοιεν, "
        "οὐκ ἀποδιδοῦσιν, ὥσπερ οὐκ ἀπαιτοῖεν.",
        "en": "They pray to images of gods that do not hear, as though they heard, "
        "and that give nothing back, as though they asked nothing.",
        "source_author": "Aristocritus, Theosophia 74",
        "conf": "medium",
    },
    {
        "dk": "B130",
        "text": "non convenit ridiculum esse ita, ut ridiculus ipse videaris.",
        "en": "It is not fitting to be so given to mockery that you yourself "
        "appear ridiculous.",
        "source_author": "Gnomologium Monacense Latinum",
        "conf": "medium",
    },
    {
        "dk": "B131",
        "text": "ἡ οἴησις προκοπῆς ἐγκοπή.",
        "en": "Self-conceit is the hindrance of progress.",
        "source_author": "Gnomologium Parisinum",
        "conf": "medium",
    },
    {
        "dk": "B132",
        "text": "τιμαὶ θεοὺς καὶ ἀνθρώπους καταδουλοῦνται.",
        "en": "Honors enslave gods and men.",
        "source_author": "Gnomologium Vaticanum 743, n. 312",
        "conf": "medium",
    },
    {
        "dk": "B133",
        "text": "ἄνθρωποι κακοὶ ἀληθινῶν ἀντίδικοι.",
        "en": "Bad men are the adversaries of the truthful.",
        "source_author": "Gnomologium Vaticanum 743, n. 313",
        "conf": "medium",
    },
    {
        "dk": "B134",
        "text": "τὴν παιδείαν ἕτερον ἥλιον εἶναι τοῖς πεπαιδευμένοις.",
        "en": "Education is a second sun to the educated.",
        "source_author": "Gnomologium Vaticanum 743, n. 314",
        "conf": "medium",
    },
    {
        "dk": "B135",
        "text": "συντομωτάτην ὁδὸν ἔλεγεν εἰς εὐδοξίαν τὸ γενέσθαι ἀγαθόν.",
        "en": "He said the shortest road to good repute is to become good.",
        "source_author": "Gnomologium Vaticanum 743, n. 315",
        "conf": "medium",
    },
    {
        "dk": "B136",
        "text": "ψυχαὶ ἀρηίφατοι καθαρώτεραι ἢ ἐνὶ νούσοις.",
        "en": "Souls slain in war are purer than those that perish in disease.",
        "source_author": "Scholium on Epictetus (Codex Bodleianus)",
        "conf": "medium",
    },
    {
        "dk": "B137",
        "text": "ἔστι γὰρ εἱμαρμένα πάντως.",
        "en": "For there are things wholly ordained by fate.",
        "source_author": "Stobaeus, Ecl. i. 5, 15",
        "conf": "low",
    },
    {
        "dk": "B138",
        "text": "ποίην τις βιότοιο τάμοι τρίβον;",
        "en": "What path of life should one cut? (opening of an epigram elsewhere "
        "attributed to Posidippus)",
        "source_author": "Codex Parisinus 1630 (cf. Anth. Pal. ix. 359)",
        "conf": "low",
    },
    {
        "dk": "B139",
        "text": "ἐπειδὴ φασί τινες εἰς ἀρχὰς κεῖσθαι τὰ ἄστρα...",
        "en": "Since some say that the stars are set as ruling principles... "
        "(opening of a Byzantine astrological text circulated under "
        "Heraclitus' name)",
        "source_author": "Catalogus Codicum Astrologorum Graecorum iv. 32, vii. 106",
        "conf": "low",
    },
]

# Working translations for fragments that end up with no public-domain
# translation from the parsed sources (MIT, by the project; flagged in notes).
WORKING_TRANSLATIONS: dict[str, str] = {
    "B3a": "The sun, by its nature, is the width of a human foot and does not "
    "overstep its bounds; if it oversteps its measures, the Erinyes will "
    "find it out.",
    "B6a": "They are quenched even more than the Heraclitean sun, inasmuch as "
    "they are never kindled again.",
    "B6b": "The stars are kindled and quenched (according to Heraclitus).",
    "B64a": "The fire is intelligent.",
    "B126a": "According to the law of the seasons, the hebdomad is brought "
    "together in respect of the moon, but divided in respect of the Bears, "
    "the two signs of immortal memory.",
    "B4": "If happiness lay in bodily pleasures, we would call oxen happy when "
    "they find bitter vetch to eat.",
    "B67a": "As a spider standing in the middle of its web feels at once when a "
    "fly breaks any thread and runs swiftly there, as if grieving at the "
    "cutting of the thread, so the soul of a man, when any part of the "
    "body is hurt, hastens quickly there, as if unable to bear the hurt "
    "of the body to which it is firmly and proportionately joined.",
    "B122": "Approximation (a single transmitted word, perhaps 'approach' or "
    "'going-near').",
    "B125a": "May wealth never fail you, men of Ephesus, so that you may be "
    "convicted of your wickedness.",
}

WORKING_TRANSLATOR = "Herakleitos project (working translation, MIT)"

# --------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------


def _clean_html(s: str) -> str:
    s = re.sub(r"<style[^>]*>.*?</style>", "", s, flags=re.S)  # inline CSS blocks
    s = re.sub(r"<span[^>]*class=\"[^\"]*pagenum[^\"]*\"[^>]*>.*?</span>", "", s, flags=re.S)
    s = re.sub(r"<sup[^>]*class=\"reference\"[^>]*>.*?</sup>", "", s, flags=re.S)
    s = re.sub(r"<span class=\"mw-editsection\">.*?</span></span>", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    # Strip leftover CSS rule fragments (e.g. ".mw-parser-output ...{...}") that
    # can survive if the source embeds an unclosed or malformed <style> block.
    # Bounded selector/body char classes keep this linear (no nested quantifiers).
    s = re.sub(r"\.mw-parser-output[^{}\n]{0,300}\{[^{}]{0,300}\}", "", s)
    s = s.replace("​", "").replace(" ", " ")
    s = re.sub(r"R\.\s*P\.\s*\d+\s*[a-z]?\.?", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


def parse_greek_fragments(path: Path) -> dict[str, str]:
    """el.wikisource DK 22 B wikitext -> {dk_number: greek_text}."""
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^=+\s*fragmentum\s+(B\s*\d+[a-z]?)\s*=+\s*$", text, flags=re.M)
    out: dict[str, str] = {}
    for i in range(1, len(parts) - 1, 2):
        dk = parts[i].replace(" ", "")
        body = re.sub(r"<!--.*?-->", "", parts[i + 1], flags=re.S)  # html comments
        body = re.sub(r"\[\[[^\]]*\]\]", "", body)  # wiki links/images
        body = re.sub(r"\{\{[^}]*\}\}", "", body)  # templates
        body = re.sub(r"=+", "", body)  # stray heading markers
        body = re.sub(r"\s+", " ", body).strip()
        if body:
            out[dk] = body
    return out


_HEADING_RE = re.compile(r'<div class="mw-heading mw-heading2"><h2 id="([^"]+)">')


def parse_burnet(path: Path) -> dict[str, dict]:
    """en.wikisource rendered Burnet HTML -> {dk_number: {text, bywater}}.

    Section ids look like ``Fragment_12`` / ``Fragment_49a`` / ``Fragment_82-83``.
    The Bywater number appears as a leading parenthesized integer in the text.
    """
    html_text = json.loads(path.read_text(encoding="utf-8"))["parse"]["text"]
    parts = _HEADING_RE.split(html_text)
    out: dict[str, dict] = {}
    for i in range(1, len(parts) - 1, 2):
        sec_id, body_html = parts[i], parts[i + 1]
        m = re.match(r"Fragment_(\d+[a-z]?(?:-\d+[a-z]?)?)$", sec_id)
        if not m:
            continue
        body_html = re.sub(r"^.*?</div>", "", body_html, count=1, flags=re.S)  # heading remnant
        text = _clean_html(body_html)
        # Drop trailing footnote blocks that wikisource appends inside a section.
        text = re.split(r"\n↑", text)[0].strip()
        if not text:
            continue
        bywater_nums = [int(n) for n in re.findall(r"\((\d+)(?:,\s*\d+)?\)", text)[:2]]
        text = re.sub(r"(?m)^\(\d+(?:,\s*\d+)?\)\s*", "", text)
        text = re.sub(r"\s*\n\s*", " ", text).strip()
        dks = [f"B{n}" for n in m.group(1).split("-")]
        for j, dk in enumerate(dks):
            bywater = None
            if bywater_nums:
                bywater = bywater_nums[min(j, len(bywater_nums) - 1)]
            note = f"Burnet prints DK {'/'.join(dks)} together." if len(dks) > 1 else ""
            out[dk] = {"text": text, "bywater": bywater, "note": note}
    return out


def parse_patrick(path: Path) -> dict[int, dict]:
    """Peitho's Web Patrick page -> {bywater_number: {eng, sources, source_author}}."""
    h = path.read_text(encoding="utf-8", errors="replace")
    chunks = re.split(r"<a name='(\d+)'>", h)
    out: dict[int, dict] = {}
    for i in range(1, len(chunks) - 1, 2):
        num, body = int(chunks[i]), chunks[i + 1]
        engs = re.findall(r"<BLOCKQUOTE class='eng'>(.*?)</BLOCKQUOTE>", body, flags=re.S)
        srcs = re.findall(r"<BLOCKQUOTE class='sourceeng'>(.*?)</BLOCKQUOTE>", body, flags=re.S)
        if not engs:
            continue
        eng = _clean_html(" ".join(engs))
        eng = re.sub(r"\s*\n\s*", " ", eng)
        source_author = ""
        if srcs:
            sm = re.match(r"SOURCES--\s*([^,.;<]+)", _clean_html(srcs[0]))
            if sm:
                source_author = sm.group(1).strip()
        out[num] = {"eng": eng, "source_author": source_author}
    return out


# --------------------------------------------------------------------------
# Fragment assembly
# --------------------------------------------------------------------------


def build_fragments() -> list[dict]:
    greek = parse_greek_fragments(RAW / "dk22b_greek_elwikisource.wikitext")
    burnet = parse_burnet(RAW / "burnet1920_heraclitus_enwikisource.json")
    patrick = parse_patrick(RAW / "patrick1889_peithosweb_archive.html")

    for dk, cur in CURATED_TEXTS.items():
        if not greek.get(dk):
            greek[dk] = cur["text"]

    records: list[dict] = []
    missing_translation: list[str] = []

    for dk, greek_text in greek.items():
        translations: list[dict] = []
        notes: list[str] = []
        source_author = ""

        if dk in CURATED_TEXTS:
            notes.append(CURATED_TEXTS[dk]["note"])
            source_author = CURATED_TEXTS[dk]["source_author"]

        # Burnet prints DK B84a/B84b together as his fr. 84.
        b = burnet.get(dk) or burnet.get({"B84a": "B84", "B84b": "B84"}.get(dk, ""))
        bywater = None
        if b:
            translations.append(
                {
                    "translator": "John Burnet",
                    "year": 1920,
                    "source": "Early Greek Philosophy, 3rd ed. (en.wikisource)",
                    "text": b["text"],
                }
            )
            bywater = b["bywater"]
            if b["note"]:
                notes.append(b["note"])
        if bywater is not None and bywater in patrick:
            p = patrick[bywater]
            translations.append(
                {
                    "translator": "G. T. W. Patrick",
                    "year": 1889,
                    "source": "The Fragments of the Work of Heraclitus of Ephesus "
                    "on Nature (Peitho's Web / Internet Archive)",
                    "text": p["eng"],
                }
            )
            if not source_author:
                source_author = p["source_author"]

        if not translations:
            if dk in WORKING_TRANSLATIONS:
                translations.append(
                    {
                        "translator": WORKING_TRANSLATOR,
                        "year": 2026,
                        "source": "this repository",
                        "text": WORKING_TRANSLATIONS[dk],
                    }
                )
                notes.append("No public-domain translation located; working translation only.")
            else:
                missing_translation.append(dk)

        if dk in DISPUTED:
            authenticity = "disputed"
            notes.append(DISPUTED[dk])
        else:
            authenticity = "genuine"
        if dk in NOTES:
            notes.append(NOTES[dk])

        records.append(
            {
                "dk_number": dk,
                "greek": greek_text,
                "translations": translations,
                "authenticity": authenticity,
                "source_author": source_author,
                "bywater_number": bywater,
                "notes": " ".join(notes),
            }
        )

    for tail in SPURIOUS_TAIL:
        records.append(
            {
                "dk_number": tail["dk"],
                "greek": tail["text"],
                "translations": [
                    {
                        "translator": WORKING_TRANSLATOR,
                        "year": 2026,
                        "source": "this repository",
                        "text": tail["en"],
                    }
                ],
                "authenticity": "spurious",
                "source_author": tail["source_author"],
                "bywater_number": None,
                "notes": "DK 'Zweifelhaftes/Falsches' tail. "
                + _NEEDS_VERIFICATION.format(conf=tail["conf"]),
            }
        )

    if missing_translation:
        raise SystemExit(
            f"fragments with no translation and no curated fallback: {missing_translation}"
        )

    records.sort(key=_dk_sort_key)
    return records


def _dk_sort_key(rec: dict) -> tuple[int, str]:
    m = re.match(r"B(\d+)([a-z]?)", rec["dk_number"])
    return (int(m.group(1)), m.group(2))


# --------------------------------------------------------------------------
# Contrast corpus
# --------------------------------------------------------------------------

_ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
    "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
    "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20,
}  # fmt: skip


def build_parmenides() -> list[dict]:
    text = (RAW / "dk28b_greek_elwikisource.wikitext").read_text(encoding="utf-8")
    text = re.sub(r"<noinclude>.*?</noinclude>", "", text, flags=re.S)
    parts = re.split(r"^==\s*([IVX]+)\s*==\s*$", text, flags=re.M)
    out = []
    for i in range(1, len(parts) - 1, 2):
        num = _ROMAN.get(parts[i])
        body = re.sub(r"\{\{[^}]*\}\}|\[\[[^\]]*\]\]", "", parts[i + 1])
        body = re.sub(r"[ \t]+", " ", body).strip()
        if num and body:
            out.append(
                {
                    "id": f"parmenides-DK28-B{num}",
                    "category": "parmenides",
                    "language": "grc",
                    "text": body,
                    "author": "Parmenides",
                    "source": "DK 28 B, el.wikisource",
                    "notes": "Contrast corpus: the philosophy of static Being.",
                }
            )
    return out


def build_burnet_parmenides_passages() -> list[dict]:
    """A few English passages of Burnet's Parmenides chapter (the poem)."""
    html_text = json.loads(
        (RAW / "burnet1920_parmenides_enwikisource.json").read_text(encoding="utf-8")
    )["parse"]["text"]
    paras = [_clean_html(p) for p in re.findall(r"<p>(.*?)</p>", html_text, flags=re.S)]
    keys = [
        "steeds that bear me",
        "it is, and it is impossible for it not to be",
        "one path only",
        "without beginning and without end",
    ]
    out = []
    for k in keys:
        for p in paras:
            if k.lower() in p.lower() and len(p) > 100:
                out.append(
                    {
                        "id": f"parmenides-burnet-{len(out) + 1}",
                        "category": "parmenides",
                        "language": "en",
                        "text": re.sub(r"\s*\n\s*", " ", p)[:2000],
                        "author": "Parmenides (tr. John Burnet, 1920)",
                        "source": "Early Greek Philosophy ch. 4, en.wikisource",
                        "notes": "Contrast corpus: the poem in English.",
                    }
                )
                break
    return out


def _gutenberg_paragraphs(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    body = re.split(r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", text)[-1]
    body = re.split(r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG", body)[0]
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", body)]


def build_quoting_passages(
    path: Path, category: str, author: str, source: str, pattern: str, limit: int
) -> list[dict]:
    """Harvest passages that actually engage Heraclitus.

    The text stored is a window CENTERED on the match, not the paragraph's first
    N chars - otherwise a long introductory paragraph whose Heraclitus mention
    sits deep inside gets truncated to generic scholarly boilerplate that is not
    about Heraclitus at all (a real bug the eval pre-flight caught).
    """
    paras = _gutenberg_paragraphs(path)
    out = []
    for p in paras:
        m = re.search(pattern, p)
        if not m or len(p) <= 150:
            continue
        start = max(0, m.start() - 250)
        end = min(len(p), m.start() + 400)
        window = p[start:end].strip()
        if start > 0:
            window = "... " + window
        # the stored window must still contain the Heraclitus/flux hook
        if not re.search(pattern, window):
            continue
        out.append(
            {
                "id": f"{category}-{Path(path).stem}-{len(out) + 1}",
                "category": category,
                "language": "en",
                "text": window,
                "author": author,
                "source": source,
                "notes": "Contrast corpus: later discussion/paraphrase of Heraclitus.",
            }
        )
        if len(out) >= limit:
            break
    return out


def build_contrast() -> list[dict]:
    out = build_parmenides()
    out += build_burnet_parmenides_passages()
    out += build_quoting_passages(
        RAW / "plato_cratylus_jowett_pg1616.txt",
        "platonic",
        "Plato, Cratylus (tr. Jowett)",
        "Project Gutenberg #1616",
        r"Heracl[ei]itus|Heracleitean|flux|all things (?:are in motion|flow)",
        8,
    )
    out += build_quoting_passages(
        RAW / "plato_theaetetus_jowett_pg1726.txt",
        "platonic",
        "Plato, Theaetetus (tr. Jowett)",
        "Project Gutenberg #1726",
        r"Heracl[ei]itus|Heracleitean|all things flow|in a flux|perpetual flux|flowing",
        8,
    )
    out += build_quoting_passages(
        RAW / "marcus_aurelius_long_pg2680.txt",
        "stoic",
        "Marcus Aurelius, Meditations (tr. George Long)",
        "Project Gutenberg #2680",
        r"Heraclitus",
        8,
    )
    return out


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="verify committed data is current")
    args = ap.parse_args(argv)

    fragments = build_fragments()
    contrast = build_contrast()

    counts = {
        "genuine": sum(1 for r in fragments if r["authenticity"] == "genuine"),
        "disputed": sum(1 for r in fragments if r["authenticity"] == "disputed"),
        "spurious": sum(1 for r in fragments if r["authenticity"] == "spurious"),
    }
    by_cat: dict[str, int] = {}
    for c in contrast:
        by_cat[c["category"]] = by_cat.get(c["category"], 0) + 1
    print(f"fragments: {len(fragments)} {counts}")
    print(f"contrast:  {len(contrast)} {by_cat}")

    if args.check:
        for name, records in [("fragments.jsonl", fragments), ("contrast.jsonl", contrast)]:
            committed = (DATA / name).read_text(encoding="utf-8")
            fresh = "".join(
                json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records
            )
            if committed != fresh:
                print(f"STALE: {name} differs from a fresh build", file=sys.stderr)
                return 1
        print("check ok: committed data matches a fresh build")
        return 0

    _write_jsonl(DATA / "fragments.jsonl", fragments)
    _write_jsonl(DATA / "contrast.jsonl", contrast)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
