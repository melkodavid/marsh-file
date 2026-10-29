#!/usr/bin/env python3
"""Marsh File checker.

Usage:
  python3 tools/check.py FILE [--resume]

FILE is a .docx, .md or .txt. With --resume the layout is also checked: the file is
rendered to PDF with LibreOffice and checked against `resume_layout` in facts.yaml
(page count, what page 1 must contain, what page 2 must start with).

For a cover letter (no --resume) the body length and opening paragraph length are also checked.

Exit code 0 = no FAIL lines. WARN lines never block but are always printed.
Quote this output in the report; never summarise it as "clean".
"""
import os, re, subprocess, sys, tempfile, zipfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
FACTS = os.path.join(HERE, "..", "facts.yaml")

# Zero tolerance.
EM_DASH = "—"

# Researched AI tells. WARN only: convergence matters more than a single hit.
AI_TELLS = [
    r"\bdelve\b", r"\bleverag(e|es|ed|ing)\b", r"\bfoster(s|ed|ing)?\b", r"\btapestry\b",
    r"\brobust\b", r"\bnuanced?\b", r"\bparadigm\b", r"\bsynerg(y|ies)\b",
    r"it is important to note", r"\bwhen it comes to\b", r"\bstudies show\b",
    r"\b(it's|it is) not (just )?[^.]{0,60}[,;]? (it's|it is)\b",
    r"\bnot just [^.]{0,60}\bbut\b",
    r"\bpassionate about\b", r"\bproven track record\b", r"\bdynamic\b",
]

# Never-publish strings and banned phrases live in facts.yaml so each owner sets their own.


def read_text(path):
    if path.lower().endswith(".docx"):
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf8")
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<w:tab/>", "\t", xml)
        text = re.sub(r"<[^>]+>", "", xml)
        for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'")):
            text = text.replace(a, b)
        return text
    return open(path, encoding="utf8").read()


def load_facts():
    with open(FACTS, encoding="utf8") as f:
        return yaml.safe_load(f)


def number_tokens(text, allow):
    """Return numeric tokens found in the text, minus years, allowed strings and dates."""
    t = text
    for a in allow:
        t = t.replace(a, " ")
    # Strip things that are not claims: years, phone numbers, URLs, email, month-day dates.
    t = re.sub(r"https?://\S+|www\.\S+|\S+@\S+|linkedin\.com\S*", " ", t)
    t = re.sub(r"(?i)job\s*(id|#|number)?\s*[:#]?\s*\\?#?\s*\d+|\\?#\s?\d+", " ", t)  # posting IDs
    t = re.sub(r"\b(19|20)\d{2}\b", " ", t)
    t = re.sub(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.? \d{1,2}\b", " ", t)
    return re.findall(r"\$?\d[\d,\.]*(?:/\d[\d,\.]*)?(?:%|K|M|\+)?", t)


def covered(token, fact_tokens, text):
    """A token is covered if it is one of the numbers inside a fact token that appears in the text.

    Compared as whole numbers, so '5' is not covered by '250+'."""
    want = token.strip(".,")
    for ft in fact_tokens:
        if ft in text and want in [t.strip(".,") for t in number_tokens(ft, [])]:
            return True
    return False


def check_layout(path, layout):
    """Render with LibreOffice and check page count and page breaks against facts.yaml resume_layout."""
    out = []
    need_pages = layout.get("pages")
    must1 = (layout.get("page1_must_contain") or "").strip()
    start2 = (layout.get("page2_starts_with") or "").strip()
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, path],
                           capture_output=True, text=True)
        pdf = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0] + ".pdf")
        if not os.path.exists(pdf):
            return [("FAIL", "layout: could not render with soffice: " + r.stderr.strip()[:200])]
        pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
        def page_text(n):
            return subprocess.run(["pdftotext", "-f", str(n), "-l", str(n), "-layout", pdf, "-"],
                                  capture_output=True, text=True).stdout
        p1 = page_text(1)
        if need_pages:
            out.append(("OK" if pages == need_pages else "FAIL", f"layout: {pages} page(s) (need {need_pages})"))
        else:
            out.append(("INFO", f"layout: {pages} page(s)"))
        if must1:
            ok1 = must1 in p1 and (not start2 or start2 not in p1)
            out.append(("OK" if ok1 else "FAIL", f"layout: page 1 contains {must1!r}" + (f" and not {start2!r}" if start2 else "")))
        if start2 and pages >= 2:
            first = [l for l in page_text(2).splitlines() if l.strip()][:1]
            ok2 = bool(first) and first[0].strip().startswith(start2)
            out.append(("OK" if ok2 else "FAIL", f"layout: page 2 starts with {start2!r} (first line: {first[0].strip()[:40] if first else 'none'!r})"))
        last = [l for l in p1.splitlines() if l.strip()][-1:]
        out.append(("INFO", f"layout: last line on page 1: {last[0].strip()[:80] if last else ''!r}"))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    path = args[0]
    text = read_text(path)
    facts = load_facts()
    results = []

    n = text.count(EM_DASH)
    results.append(("OK" if n == 0 else "FAIL", f"em dashes: {n}"))

    for pat in facts.get("never_publish") or []:
        hits = re.findall(pat, text, flags=re.I)
        results.append(("OK" if not hits else "FAIL", f"never-publish /{pat}/: {len(hits)} hit(s)"))

    banned = []
    for pat in facts.get("banned_phrases") or []:
        banned += [m.group(0) for m in re.finditer(pat, text, flags=re.I)]
    results.append(("OK" if not banned else "FAIL", f"banned phrases: {len(banned)}" + (f" -> {sorted(set(b.lower() for b in banned))}" if banned else "")))

    tells = []
    for pat in AI_TELLS:
        for m in re.finditer(pat, text, flags=re.I):
            tells.append(m.group(0))
    results.append(("OK" if not tells else "WARN", f"AI-tell phrases: {len(tells)}" + (f" -> {sorted(set(t.lower() for t in tells))}" if tells else "")))

    # Numbers vs facts
    fact_tokens, status_of = [], {}
    for f in facts.get("facts") or []:
        for tok in f.get("tokens", []):
            fact_tokens.append(tok)
            status_of[tok] = (f["id"], f["status"])
    allow = facts.get("allow_numbers") or []
    unmatched = []
    for tok in number_tokens(text, allow):
        if not covered(tok, fact_tokens, text):
            unmatched.append(tok.strip(".,"))
    unmatched = sorted(set(u for u in unmatched if u))
    results.append(("OK" if not unmatched else "FAIL", f"numbers not in facts.yaml: {unmatched if unmatched else 'none'}"))
    for tok, (fid, status) in status_of.items():
        if tok in text:
            if status == "pending":
                results.append(("FAIL", f"fact '{fid}' is PENDING but appears as {tok!r}"))
            elif status == "provisional":
                results.append(("WARN", f"fact '{fid}' is PROVISIONAL (audit open): {tok!r} used"))

    if "--resume" in sys.argv:
        results += check_layout(path, facts.get("resume_layout") or {})
    elif "Dear" in text and "Sincerely" in text:
        # Cover letter length: body from salutation to sign-off. Target 300-380, hard range 250-400.
        body = text[text.index("Dear"):text.index("Sincerely")]
        paras = [p for p in body.split("\n") if p.strip()]
        words = len(body.split())
        ok = 250 <= words <= 400
        results.append(("OK" if ok else "WARN", f"letter length: {words} words (target 300-380, range 250-400)"))
        if len(paras) > 1:
            opening = len(paras[1].split())
            results.append(("OK" if opening <= 100 else "WARN", f"opening paragraph: {opening} words (aim 60-80, personal openers up to 100)"))

    print(f"Checked: {path}")
    for level, msg in results:
        print(f"  [{level}] {msg}")
    fails = sum(1 for l, _ in results if l == "FAIL")
    warns = sum(1 for l, _ in results if l == "WARN")
    print(f"Result: {fails} FAIL, {warns} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
