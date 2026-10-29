# The Marsh File: job application kit

Read this file, `facts.yaml`, `voice-lessons.md`, and everything in `exemplars/` at the start of EVERY session before writing anything. Nothing carries over between sessions except what is in this repo.

## Setup mode (first session only)

If `facts.yaml` still says `setup_complete: false`, run setup before anything else. The owner may just type "Set me up".

1. **Interview** in small batches (no more than 5 questions at a time). Collect:
   - Name, contact line (email, phone, LinkedIn, portfolio), city, current role, the roles he is targeting, and stretch roles he would consider
   - Every number, date, title, and result he might use, and how sure he is of each (verified, provisional, pending)
   - Anything he must never put in writing (confidential numbers, internal strategy, why something went badly). These go in `never_publish`.
   - Places where a team should get credit instead of him, and words he hates or overuses (`banned_phrases`)
   - Hometown or personal connections worth mentioning when relevant
   - Resume layout: page count, which section must end page 1, colour preference
2. **Ask for files:** his current resume as a .docx (not PDF) into `resume/`, and 1 to 3 cover letters he wrote himself and liked into `exemplars/` (pasted text is fine).
3. **Fill in** `facts.yaml` (every number in his resume needs a fact entry with its exact `tokens`), the "About the owner" section below, and the layout block. Replace each `<placeholder>` in this file.
4. **Test** the checker on his resume (`--resume`) and on each exemplar. Every FAIL should be either a real problem to show him or a missing fact to add. Repeat until the resume passes, and quote the output.
5. Set `setup_complete: true`, commit, push, open a pull request into `main`, and merge it (see "Saving work"). Tell him setup is done and ask for his first posting.

## About the owner

<Name> is <current role> at <employer>, <city>. Targets: <target roles>. Stretch roles he would consider: <stretch roles>.
Personal connections to play when relevant: <hometown, community, past local work>.

## The job

He pastes a posting link or posting text (often from his phone). You return a tailored resume and a cover letter in his voice, plus a check report. He reviews, edits, and sends back his final version. You learn from the difference.

## Workflow per posting

1. **Fetch.** Try the link. LinkedIn, Indeed, and Workday pages usually block automated reading. If blocked, say so in one line and ask for the posting text or a screenshot. Never guess the posting from the URL.
2. **Triage (cheap model).** Score fit 1 to 5 against `facts.yaml` and the resume, run as a haiku-model subagent. If the score is 1 or 2, reply in two lines with the reason and stop, unless he says to go ahead. Stretch roles are his call: present the trade-off, do not decide for him.
3. **Draft (main model).** Create `applications/YYYY-MM-company-role/` containing:
   - `posting.md` (pasted text, link, date found)
   - `<First>_<Last>_Resume_<Role_Title>.docx` (see "Tailoring rules")
   - `<First>_<Last>_Cover_Letter_<Role_Title>.docx` (one page, matching the resume's styling)
   - PDFs of both, exported with `soffice --headless --convert-to pdf`. He uploads the PDFs; the .docx is the editable source. Re-export after every change.
   - Role title in Title_Case with underscores so files upload as is. Set the docx author (docProps/core.xml `dc:creator`) to his name.
   - `check_report.txt` (verbatim checker output)
4. **Check.** Run `python3 tools/check.py <file> --resume` on the resume and `python3 tools/check.py <file>` on the letter. Quote the output. Never say "clean" without it. Fix FAIL lines before showing him anything. Show WARN lines.
5. **Hand over.** Send the PDFs plus a PNG of every page (`pdftoppm -png -r 80`), since he may be on his phone. Add a short note: what you reweighted and why, and any open question. Give the reasoning for every change.
6. **Learn.** When he returns his final letter, diff it against your draft and log the changes in `voice-lessons.md` (rules are in that file). If one of his edits weakens the letter, say so before logging it.
7. **Track.** Add or update the row in `tracker.csv`.

Use the most expensive model only when he asks, or for a final voice pass on a role he really wants.

## Tailoring rules (resume)

- Start from the newest file in `resume/`. Never use an older copy or a rebuilt file as a base.
- Reorder and reweight real bullets toward the posting. Rewrite only the summary and skills line. Never invent experience, tools, or numbers.
- Edit the docx XML in place (exact string replacements) so styling survives. Render and look at it after every change.
- Keep to the layout in `facts.yaml` (`resume_layout`). If added bullets break it, trim the lowest-value bullet and say which one.

## Hard rules

- **No em dashes (U+2014)** in anything written for him. Use a period, comma, colon, or parentheses. En dashes in date ranges are fine.
- **Verify, don't assert.** Before saying anything is fixed, clean, or done, check the actual current file (search it, render it).
- **Every number comes from `facts.yaml`.** `pending` facts are never used. `provisional` facts are used but flagged. When something changes, update facts.yaml first, then every document in one pass.
- **Never publish** anything on the `never_publish` list. It is interview-only.
- **Credit the team** wherever `banned_phrases` or the facts notes say so.

## Voice

Match the exemplars. Informal, authentic, confident but not cocky. Confidence states facts; cockiness narrates one's own virtues, so cut any sentence whose only job is self-commentary. Do not repeat the same strong word in one document. Avoid the AI tells the checker lists, the neat-bow closing paragraph, tricolons used for rhythm, "it's not X, it's Y", and unsourced authority claims.

His edits are usually better than the first draft: treat them as senior, and give real critique when warranted. Do not invite the reader to contact references; he supplies them only when requested. Do not duplicate the resume. Cover letters take several rounds. That is normal.

## Cover letter format

Evidence: a ResumeGo field experiment (7,287 applications) found tailored letters got 16.4% callbacks vs 12.5% generic and 10.7% none. Length and salutation advice is recruiter consensus, not hard data.

- **Length:** 300 to 380 words from salutation to sign-off (hard range 250 to 400). One page.
- **Order:**
  1. Personal connection, then the role (60 to 80 words; a personal story opener can run to about 100).
  2. Strongest proof, matched to the posting's main duty, with numbers.
  3. Second proof for the next key requirement.
  4. Gap and learning, only when there is a real gap. Short and general.
  5. One-line close.
- **Salutation:** a hiring manager's name from the posting or LinkedIn. Never guess one; fall back to "<Company> Hiring Team".
- **Tailored every time.** Never reuse a letter body between employers.

## Files

| Path | Purpose |
|---|---|
| `facts.yaml` | Every number, date, title with status; never-publish list; banned phrases; resume layout |
| `voice-lessons.md` | Feedback pool, read every session |
| `exemplars/` | His best finished letters in his final wording |
| `resume/` | Current master resume (newest file wins) |
| `tools/check.py` | The gate: em dashes, never-publish, AI tells, numbers vs facts, layout, letter length |
| `applications/` | One folder per posting |
| `tracker.csv` | One row per posting |

## Saving work so the next session sees it (important)

Cloud sessions push to their own branch, not to `main`, and every new session starts from `main`. Anything not merged into `main` is invisible to the next session.

**Auto-merge on "applied".** Whenever he confirms he has applied to a job, merge to `main` without asking:
1. Update the tracker row (status `applied`, date), log voice lessons from his final version, and file the exemplar if it is one of his best. Run the checker on anything changed.
2. Commit and push everything on the session branch.
3. Open a pull request from the session branch into `main` (GitHub MCP tools) and merge it. Confirm the result says merged. If it fails, say so in one line and give him the manual steps: open the session's diff, choose Create PR, then Merge on GitHub.
4. Tell him it is merged, with the pull request link.

For anything else that should reach `main` (fact updates, rule changes), ask first.

At the start of each session, check that `voice-lessons.md` and `tracker.csv` are current. If the last application's folder exists only on an unmerged branch, say so before drafting.

## Commits

Small, descriptive messages. Commit each application folder together with its tracker row.
