# Deploy FlowLedger AI for the Zamp submission

You need **two working links**: the deployed app and a demo video (maximum 5 minutes). These links cannot be generated solely by downloading this source package; they must be created through your own hosting and recording accounts.

## Fast route: GitHub → Streamlit Community Cloud

1. Download and unzip `FlowLedger_AI_Zamp_Submission.zip`.
2. Open https://github.com/new, create a repository named `flowledger-ai`, and upload **all contents inside** the unzipped `flowledger_ai` folder. Ensure that the GitHub repo root includes `app.py`, `engine.py`, `requirements.txt`, `packages.txt`, `data/`, `samples/`, and `.streamlit/`.
3. Open https://share.streamlit.io and sign in with your GitHub account.
4. Select **Create app**, choose the existing GitHub repo, branch `main`, and **entrypoint `app.py`**. Deploy. The platform reads `requirements.txt` for Python dependencies and `packages.txt` to install Tesseract OCR.
5. Copy the deployed `https://....streamlit.app/` link. Open it in a **private/incognito tab** and confirm you can process `01_clean_invoice.pdf`, then process the same file a second time to see `DUPLICATE_HOLD`.
6. In **Run history → Demo maintenance**, reset all runs. Record your own 5-minute video following `DEMO_SCRIPT.md`, using one clean path and at least one exception. Upload to Loom or Google Drive with interviewer-visible sharing permissions.
7. Paste the `*.streamlit.app` link and demo video link into the Zamp submission form before EOD. Optionally paste your public GitHub repo in **Any other links**.

**Optional:** You can configure `OPENAI_API_KEY` via Streamlit's secrets settings to enable AI-assisted field extraction. The demo works without it, and the submission should remain live and runnable if no key is supplied.

**Important limitation:** SQLite histories stored on free, ephemeral hosting can reset after an app restart. Do not describe this as a permanent production audit database. For the case study, the dashboard records and displays actual runs while instance storage remains available.

## If deployment fails

- Open the Streamlit app deployment logs. Check whether dependencies installed successfully.
- Confirm all root-level source files and CSV/PDF sample files were uploaded (not just `app.py`).
- Python 3.12 is the recommended version for this package.
- Check if `tesseract-ocr` was installed from `packages.txt` (scanned invoices need OCR, native PDFs do not).
- If the optional OpenAI API fails, remove the key and use the built-in local extraction mode.
- If you don't have time to polish further, submit the fully running version. Zamp emphasizes a genuine end-to-end working process.

The first priority is **a public app that processes a real PDF on demand**, then the video. A code repository by itself does **not** satisfy the live-process requirement.
