# FlowLedger AI — natural 5-minute demo script

**Record your own voice.** Keep the app open, run the PDFs live, and speak naturally; this is a guide, not something you need to memorize word for word. Before recording, use **Run history → Demo maintenance → Reset all demo runs** so the initial clean invoice does not start as a duplicate.

## 0:00–0:35 — Problem and user

> Hi, I chose problem statement one: invoice processing. The problem is that AP teams spend a lot of time opening PDFs, checking purchase orders, and manually finding exceptions. I built FlowLedger AI to turn an invoice into a clear, explainable decision. My focus is not just extraction, but what happens when the invoice is wrong or incomplete.

## 0:35–1:35 — Happy path

In **Invoice workbench**, choose **01_clean_invoice.pdf**, click **Run invoice review**.

> I'll upload a real PDF now. You can see the stages execute: document intake, extraction, vendor and PO matching, financial controls, and the decision. This invoice is for Acme Technology Services. Its amount is 4,500 dollars and the purchase order has sufficient remaining balance. All checks pass, so the system marks it ready for AP approval. It does not actually release a payment.

Point to the extracted fields, PO balance and checklist.

## 1:35–2:25 — Duplicate prevention

Select **01_clean_invoice.pdf** again and run it.

> Now I'll upload the same invoice again. The system searches past runs, detects the same invoice, and places it on duplicate hold. It also points to the previous run, so the reviewer has an audit trail instead of just a warning message. That's important because duplicate payments can be costly.

## 2:25–3:20 — Business exception

Select **02_overbudget_invoice.pdf** and run it.

> Here's a different case. The invoice is valid as a PDF, but the PO has already been mostly used. The remaining balance is only 1,000 dollars, while this invoice is for 1,800 dollars. So the decision is manual review. The app shows the exact reason and the configured tolerance, rather than silently approving it.

## 3:20–4:05 — Dashboard and output

Click **Run history**.

> Every run is stored with its status, amounts, documents, and findings. A user can open an earlier run and download the decision as JSON. I separated extraction from decision rules deliberately: document interpretation can be uncertain, but financial controls need to be explicit and testable.

## 4:05–4:45 — Thoughtful limitations and next steps

> For this case study, the PO and vendor lists are synthetic master data. The application can process native PDFs and scanned PDFs with OCR. There's also an optional AI extraction path, which checks suggestions against actual document evidence. The base workflow works without an API key. For a production version, I'd integrate an ERP, a durable cloud database, and a proper approval workflow. My goal here was to make a smaller process work end-to-end and handle exceptions safely.

## Quick tips for your video

- If you don't configure an AI key, say **local document extraction**, not **AI extracted all fields**. The workflow is real either way.
- Do not claim actual bank, ERP, tax registry, or payment connectivity.
- Keep the browser zoom around 85–100%, close unrelated tabs, and avoid showing credentials.
- Use the included synthetic PDF files only.
- Share the demo video link with permissions that let an interviewer view it without logging into your account.

## Potential live-interview questions (natural answers)

**Why separate extraction and decision-making?** Because extracted text can be uncertain, but money-related approvals should use consistent, explainable rules. I also check AI-suggested fields against document text.

**Why not automatically reject an over-budget invoice?** Procurement terms may allow legitimate partial delivery or authorized overages. I flag it for human review instead of pretending the app has complete commercial context.

**How are duplicate invoices detected?** Primarily by verified vendor + invoice number; I also compare file hashes to catch identical document re-uploads even if fields are missing.

**What about several invoices against one PO?** I combine the billed amount from the synthetic ERP snapshot with earlier positive FlowLedger decisions, then check the new invoice against the remaining balance. This is demo commitment tracking, not real ERP accounting.

**What happens if a PDF is scanned?** I try native text extraction first. If the page is effectively image-only, I run Tesseract OCR before checking fields. If extraction is still insufficient, the process fails safely or requests information; it never guesses mandatory financial data.

**What if the AI model is unavailable?** The workflow falls back to the local parser and rule engine, so it stays runnable without an external model service.

**What would you improve next?** Cloud database, authentication, real ERP integration, better line-item matching, supplier confirmation workflows, and human approval routing.
