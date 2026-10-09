from flask import Flask, render_template, request, send_file, jsonify
import io
from grounding import analyze, generate_draft_summary
from sample_data import (
    SAMPLE_SOURCE, SAMPLE_SUMMARY_WITH_HALLUCINATION,
    NEURO_SOURCE, NEURO_SUMMARY_HALLUCINATED,
    CODIESP_SOURCE_ES, CODIESP_SUMMARY_HALLUCINATED_ES,
)
from pdf_export import build_audit_pdf

app = Flask(__name__)


def build_role_views(report: dict, atomic: bool = False) -> dict:
    if not report or not report.get("claims"):
        return {}

    claims = report["claims"]
    unverified = [c for c in claims if c["flag"] == "unverified"]
    weak = [c for c in claims if c["flag"] == "weak"]
    grounded = [c for c in claims if c["flag"] == "grounded"]

    granularity_note = "clause-level atomic claims" if atomic else "sentence-level claims"

    clinical_view = {
        "claims": claims,
        "summary_line": (
            f"{len(unverified)} unverified, {len(weak)} weak, "
            f"{len(grounded)} grounded claim(s) out of {len(claims)} total "
            f"({granularity_note})."
        ),
    }

    if not unverified:
        patient_message = "This summary appears to closely follow your medical record. No unsupported statements were flagged."
        patient_tone = "reassuring"
    else:
        patient_message = (
            f"{len(unverified)} statement(s) in this AI-generated summary could not be "
            "clearly matched back to your medical record. This doesn't necessarily mean "
            "they're wrong — but it means a clinician should double-check them before you "
            "rely on this summary."
        )
        patient_tone = "caution"
    patient_view = {
        "message": patient_message,
        "tone": patient_tone,
        "flagged_claims": [c["claim"] for c in unverified],
    }

    governance_view = {
        "overall_risk_pct": round(report["overall_risk"] * 100, 1),
        "audit_log": [
            {
                "claim": c["claim"],
                "source_match": c["best_match"],
                "similarity_score": c["similarity"],
                "flag": c["flag"],
                "method": "TF-IDF cosine similarity (Research Edition; see paper for validated behaviour)",
            }
            for c in claims
        ],
    }

    return {"clinical": clinical_view, "patient": patient_view, "governance": governance_view}


@app.route("/generate-summary", methods=["POST"])
def generate_summary_endpoint():
    """
    Auto-populates a FAITHFUL draft summary from the pasted source text.
    This does not introduce fabrications — it gives the user a starting
    point to edit if they want to test hallucination detection. The
    fabrication check itself only runs when the user clicks
    'Analyze Grounding' — auto-population and analysis are deliberately
    separate steps.
    """
    source_text = request.form.get("source_text", "").strip()
    lang = request.form.get("lang", "en")
    return jsonify({"summary": generate_draft_summary(source_text)})


@app.route("/", methods=["GET", "POST"])
def index():
    report = None
    role_views = None
    source_text = ""
    summary_text = ""
    active_role = request.values.get("role", "clinical")
    atomic = request.form.get("atomic") == "on"
    lang = request.form.get("lang", "en")

    if request.method == "POST":
        source_text = request.form.get("source_text", "").strip()
        summary_text = request.form.get("summary_text", "").strip()
        if source_text and summary_text:
            report = analyze(source_text, summary_text, atomic=atomic, lang=lang)
            role_views = build_role_views(report, atomic=atomic)

    return render_template(
        "index.html",
        report=report,
        role_views=role_views,
        active_role=active_role,
        atomic=atomic,
        lang=lang,
        source_text=source_text,
        summary_text=summary_text,
        sample_source=SAMPLE_SOURCE.strip(),
        sample_summary=SAMPLE_SUMMARY_WITH_HALLUCINATION.strip(),
        neuro_source=NEURO_SOURCE.strip(),
        neuro_summary=NEURO_SUMMARY_HALLUCINATED.strip(),
        codiesp_source=CODIESP_SOURCE_ES.strip(),
        codiesp_summary=CODIESP_SUMMARY_HALLUCINATED_ES.strip(),
    )


@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    source_text = request.form.get("source_text", "").strip()
    summary_text = request.form.get("summary_text", "").strip()
    if not source_text or not summary_text:
        return "Missing source or summary text.", 400

    report = analyze(source_text, summary_text)
    pdf_bytes = build_audit_pdf(report)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="verimed_research_audit_log.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
