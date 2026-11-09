# FlowLedger AI — invoice intelligence & exception management

A fully runnable **Zamp AI Solutions Analyst (PS-1)** case-study implementation: PDF input → extraction → vendor & PO lookup → financial control checks → reasoned recommendation → audit history dashboard.

**Status:** The app performs real PDF processing and stores each run. It **never initiates payments** or directly approves funds. All included vendor and PO data is fictional.

## Features

- Upload a real PDF or use ten included demonstration PDFs.
- Real PDF text extraction plus OCR for image-only/scanned PDFs.
- Optional **OpenAI gpt-4o-mini** extraction refinement, with evidence checks and deterministic fallback (API key is not required).
- Checks for mandatory fields, approved vendors/aliases, inactive vendors, PO existence/status, vendor–PO mismatch, currency mismatch, subtotal/tax math, duplicates, available PO budget and tolerance.
- Track previous positive decisions as *demo commitments* so split invoices don't silently exceed budgets.
- Shows processing milestones and makes each decision interpretable.
- Dashboard with counts, status distribution, run history, run inspection, downloadable decision report.
- 12 regression tests covering the working path, meaningful exceptions, scanning and malformed input.

## Run locally

1. Install Python 3.10 or later and Tesseract OCR (optional, but needed for scanned PDFs). On Ubuntu: `sudo apt-get install tesseract-ocr`; on Windows install Tesseract and ensure it is in PATH.
2. From the project folder:

   ```bash
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

3. In the browser, open the shown local URL (usually http://localhost:8501).
4. Choose `01_clean_invoice.pdf` and click **Run invoice review**.
5. Re-run `01_clean_invoice.pdf` to demonstrate duplicate detection; then select `02_overbudget_invoice.pdf` and `03_missing_fields_invoice.pdf`.

**Optional AI model:** Enter an OpenAI API key in the sidebar or set `OPENAI_API_KEY` as a secret. Without a key, the robust PDF extractor and all business rules still execute. Don't show or hardcode API keys in your public GitHub repository or video.

## Run tests

```bash
python -m pip install pytest
python -m pytest -q
```

## Deploy publicly with Streamlit Community Cloud

1. Create a new GitHub repository and upload the *contents of this folder* (including `data/`, `samples/`, `packages.txt`, `requirements.txt` and `.streamlit/config.toml`).
2. Go to https://share.streamlit.io, sign in with GitHub, and click **Create app** or **New app** (wording can vary). Choose your repository, branch (`main`), and entry-point file `app.py`.
3. Click **Deploy**, open the public `*.streamlit.app` URL and run at least two of the included PDFs.
4. Add the URL to Zamp's **Link of the live process** field.
5. Record an unedited screen-share video with your own voice of no more than 5 minutes; upload to Loom/Drive and share it using link access.

**Persistence note:** The default audit backend is local SQLite. It retains history while the application instance's disk remains intact, but some free hosting services may reset ephemeral storage after restarts. For production, replace it with a managed database. Demo history can be repopulated by running the included sample PDFs. This case study does not claim durable cross-restart cloud storage.

## Suggested 5-minute walkthrough

- `0:00–0:35` Explain AP pain point and why every decision has an audit trail.
- `0:35–1:45` Process `01_clean_invoice.pdf` live, inspect workflow stages, show extracted fields and PO balance.
- `1:45–2:40` Process the exact same invoice again, show **duplicate hold** and the previous-run reference.
- `2:40–3:30` Process `02_overbudget_invoice.pdf`, show prior billed, remaining balance, tolerance, and manual-review decision.
- `3:30–4:20` Show dashboard, detailed run record and downloadable JSON.
- `4:20–5:00` Explain tradeoffs: deterministic financial controls vs probabilistic extraction; image-only OCR; model grounding; limitations and what you'd integrate next.

**Prepare your inputs and test the deployed link before recording. The interviewer may ask you to run additional cases live.**

## Data model and rules

- `data/vendors.csv`: approved vendor master + controlled aliases, status.
- `data/purchase_orders.csv`: active PO master with amounts, prior ERP billed amount and tolerance.
- `flowledger_runs.sqlite3`: auto-created run history (ignored by Git).
- `engine.py`: extraction, rules, and audit storage.
- `app.py`: Streamlit interactive workbench and run dashboard.
- `generate_samples.py`: reproducible generation of fictional PDFs.

**Decision hierarchy:** Potential duplicate → `DUPLICATE_HOLD`; otherwise missing mandatory fields → `MISSING_INFORMATION`; otherwise control exceptions → `REVIEW_REQUIRED`; otherwise `READY_FOR_APPROVAL`. Even the last state requires AP authorization; it does not make payments.

**Security & product boundaries:** PDF content is untrusted input. AI output is validated against document evidence. Do not upload confidential or sensitive financial documents into a public demo. The optional model sends extracted document text to an external service; use only fictional/test information unless permitted. No live ERP, tax registry, bank validation or payment integration exists in this submission.
