# The Marsh File

Your personal job application kit, run by Claude. Paste a job posting, get back a tailored resume, a one-page cover letter in your voice, and a check report, as PDFs ready to upload. Edit the letter, send your final version back, and it learns how you write. The drafts get closer to your voice with every application.

## Start here (about 15 minutes, once)

**You need:** Claude Pro, a free GitHub account, your current resume as a **.docx** (Word, not PDF), and 1 to 3 cover letters you wrote and liked.

1. **Make your own private copy.** On this page, click the green **Use this template** button, then **Create a new repository**. Name it whatever you like, set it to **Private** (it will hold your resume and personal details), and click **Create repository**.
2. **Open Claude Code.** Go to https://claude.ai/code (works on desktop and in the Claude phone app). Connect GitHub when it asks, and pick **your new private repository**, not this one.
3. **Type `Set me up`.** Claude will interview you a few questions at a time: your roles, your numbers and results, anything you never want in writing, words you hate. Then it asks for your resume and letters. Upload them in the chat.
4. **Let it finish.** Claude fills in your files, tests the checker on your resume, and saves everything. When it says setup is done, you're ready.

## Every application after that

1. Open a new session on your repository at https://claude.ai/code.
2. Paste the job link or the posting text. (LinkedIn, Indeed, and Workday block automated reading, so pasting the text saves a round trip.)
3. Claude scores the fit, then sends you the resume and cover letter PDFs, screenshots of each page, and a note on what it changed and why.
4. Edit the letter however you like and send your final version back. That's how it learns your voice.
5. When you've sent the application, tell it **"I applied"**. That saves everything to your repository so the next session remembers it. If you skip this step, the next session won't see this application.

## Tips

- **The first few letters need the most editing.** That's normal. Keep sending your final versions back.
- **Keep your numbers honest.** Anything you're not sure of gets marked `pending` in `facts.yaml`, and the checker blocks it from ever reaching an employer.
- **Ask for reasons.** Claude explains each change. Push back when you disagree: your edits count as the senior opinion.
- **New resume?** Upload it and say "this is my new master resume". The newest file in `resume/` is always the base.

## What's inside

| File | What it does |
|---|---|
| `CLAUDE.md` | Claude's instructions: the workflow, the rules, the cover letter format |
| `facts.yaml` | Every number and result you can use, with how sure you are of each |
| `voice-lessons.md` | What Claude has learned from your edits |
| `exemplars/` | Your best finished letters, used as voice reference |
| `resume/` | Your master resume |
| `tools/check.py` | Quality gate: em dashes, AI-sounding phrases, numbers not in your facts, page layout, letter length |
| `applications/` | One folder per job |
| `tracker.csv` | Every job, with its status |
