"""
VeriMed (Research Edition) — Core Grounding & Attribution Engine
------------------------------------------------------------------
This is the engine described and tested in the accompanying research paper
("Requirements Engineering for Trustworthy Clinical NLP Systems"). It is
maintained as a separate, independently versioned build from any other
VeriMed engine, specifically so that what the paper describes and what this
code does never drift apart.

Given a SOURCE clinical text and an AI-GENERATED SUMMARY of that text:
  1. Splits the summary into individual factual claims. Two granularities
     are supported: sentence-level (split_sentences) and clause-level
     (extract_atomic_claims).
  2. Splits the source into sentences.
  3. For each claim, finds the source sentence(s) that best support it
     using TF-IDF cosine similarity — a lightweight, dependency-free
     proxy for semantic grounding.
  4. Applies a negation-aware check: a claim whose key phrase appears in
     the source ONLY inside an explicit denial is still flagged as
     unverified, rather than being treated as grounded on lexical
     overlap alone.
  5. Flags claims as grounded / weak / unverified with a similarity
     score and the best-matching source sentence, for transparency.

No patient data is used anywhere — only synthetic or user-supplied text,
plus one real, publicly licensed (CC-BY 4.0) clinical case report
retrieved from its original open-access publication.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

NEGATION_MARKERS = ["denies", "denied", "no history of", "without", "negative for", "ruled out"]
NEGATION_WINDOW_CHARS = 80

SPANISH_NEGATION_MARKERS = ["no presentaba", "no se apreciaron", "sin ", "niega", "ausencia de", "no antecedentes"]
SPANISH_STOPWORDS = [
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un",
    "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le",
    "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando", "muy", "sin", "sobre",
    "también", "me", "hasta", "hay", "donde", "quien", "desde", "todo", "nos", "durante",
    "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e",
    "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él",
    "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella",
    "estar", "estas", "algunas", "algo", "nosotros", "es", "fue", "fueron", "había",
    "tenía", "tras", "mediante",
]


def split_sentences(text: str) -> list[str]:
    text = text.strip().replace("\n", " ")
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sentences if len(s.strip()) > 3]


def extract_atomic_claims(text: str) -> list[str]:
    atomic = []
    for sentence in split_sentences(text):
        parts = re.split(r';\s*|\s*,?\s+and\s+(?=[a-z])', sentence)
        for part in parts:
            part = part.strip(" ,.")
            if not part:
                continue
            if re.search(r'\b(history of|denies|includes|reports?|shows?)\b', part, re.I):
                sub_items = re.split(r',\s+', part)
                atomic.extend(s.strip(" ,.") for s in sub_items if s.strip())
            else:
                atomic.append(part)
    return [c for c in atomic if len(c.split()) >= 2]


def generate_draft_summary(source_text: str, max_facts: int = 7) -> str:
    """
    Auto-generates a faithful, extractive draft summary from the source
    text, for UI auto-population when the user pastes a source note.
    This produces a FAITHFUL summary (no fabrications) — it is a
    starting draft the user can edit to introduce errors, if they want
    to test the detector, not a stress-test generator itself. This
    matters: an extractive summary drawn from the source cannot itself
    demonstrate hallucination detection, since it introduces nothing
    ungrounded to detect.
    """
    if not source_text or len(source_text.strip()) < 10:
        return ""
    facts = split_sentences(source_text)
    if not facts:
        return ""
    return (" ".join(facts[:max_facts])).strip()


def _is_negated_in_source(phrase_words: set, source_text: str, lang: str = "en") -> bool:
    markers = SPANISH_NEGATION_MARKERS if lang == "es" else NEGATION_MARKERS
    lower_source = source_text.lower()
    found_any = False
    for marker in markers:
        for m in re.finditer(re.escape(marker), lower_source):
            window = lower_source[m.start():m.start() + NEGATION_WINDOW_CHARS]
            overlap = phrase_words & set(re.findall(r"[a-záéíóúñü]+", window))
            if len(overlap) >= max(1, len(phrase_words) // 2):
                found_any = True
    return found_any


def analyze(source_text: str, summary_text: str, threshold: float = 0.20,
            atomic: bool = False, lang: str = "en") -> dict:
    source_sentences = split_sentences(source_text)
    claims = extract_atomic_claims(summary_text) if atomic else split_sentences(summary_text)

    if not source_sentences or not claims:
        return {"claims": [], "overall_risk": 0.0, "error": "Empty input"}

    stop_words = SPANISH_STOPWORDS if lang == "es" else "english"
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    all_text = source_sentences + claims
    tfidf_matrix = vectorizer.fit_transform(all_text)

    source_vectors = tfidf_matrix[: len(source_sentences)]
    claim_vectors = tfidf_matrix[len(source_sentences):]

    results = []
    unverified_count = 0

    for i, claim in enumerate(claims):
        sims = cosine_similarity(claim_vectors[i], source_vectors)[0]
        best_idx = sims.argmax()
        best_score = float(sims[best_idx])
        best_match = source_sentences[best_idx]

        word_pattern = r"[a-záéíóúñü]+" if lang == "es" else r"[a-z]+"
        stop_set = set(SPANISH_STOPWORDS) if lang == "es" else {
            "the", "a", "an", "and", "with", "of", "to", "for", "on", "in", "at", "is", "was"
        }
        claim_words = set(re.findall(word_pattern, claim.lower())) - stop_set
        negation_flagged = _is_negated_in_source(claim_words, source_text, lang=lang) if atomic else False

        if negation_flagged:
            flag = "unverified"
            unverified_count += 1
        elif best_score >= 0.45:
            flag = "grounded"
        elif best_score >= threshold:
            flag = "weak"
        else:
            flag = "unverified"
            unverified_count += 1

        results.append({
            "claim": claim,
            "best_match": best_match,
            "similarity": round(best_score, 3),
            "flag": flag,
            "negation_flagged": negation_flagged,
        })

    overall_risk = round(unverified_count / len(claims), 3) if claims else 0.0
    return {"claims": results, "overall_risk": overall_risk}


if __name__ == "__main__":
    from sample_data import SAMPLE_SOURCE, SAMPLE_SUMMARY_WITH_HALLUCINATION
    report = analyze(SAMPLE_SOURCE, SAMPLE_SUMMARY_WITH_HALLUCINATION)
    for c in report["claims"]:
        print(f"[{c['flag'].upper():10}] sim={c['similarity']:.2f}  {c['claim']}")
    print(f"\nOverall hallucination risk: {report['overall_risk'] * 100:.1f}%")
