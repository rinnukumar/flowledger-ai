"""FlowLedger AI — Zamp ASA take-home case study | Streamlit entry point."""
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from engine import (
    ROOT, STAGES, create_db, get_history, get_run, clear_history,
    process_invoice, fmt_money, load_masters,
)

st.set_page_config(page_title="FlowLedger AI | Invoice Intelligence", page_icon="🧾", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container {padding-top:1.8rem; padding-bottom:3rem; max-width:1240px;}
section[data-testid="stSidebar"] {background:#0C1D30;}
section[data-testid="stSidebar"] * {color:#ECF5FF;}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {background:#0C1D30;}
section[data-testid="stSidebar"] .stTextInput input {color:#0C1D30;}
section[data-testid="stSidebar"] .stMarkdown p {line-height:1.55;}
.logo {font-family:Manrope,sans-serif;font-size:1.18rem;letter-spacing:-.6px;font-weight:800;color:#153044;}
.logo-mark{background:#0F766E; color:white;display:inline-flex;align-items:center;justify-content:center;border-radius:12px;width:39px;height:39px;margin-right:10px;font-size:20px;vertical-align:middle;}
.eyebrow{color:#0F766E;text-transform:uppercase;font-size:11px;letter-spacing:2px;font-weight:800;}
.headline{font-family:Manrope,sans-serif;font-size:2.25rem;letter-spacing:-1.4px;line-height:1.18;font-weight:800;color:#102438;margin:.55rem 0;}
.subheadline{color:#66788B;font-size:15px;line-height:1.65;max-width:800px;margin-bottom:1rem;}
.pill{display:inline-block;background:#E1F5F1;color:#116C62;border:1px solid #B8E8DD;border-radius:100px;padding:5px 11px;font-size:11px;font-weight:800;letter-spacing:.25px;}
.status-good{border-left:5px solid #0D9488;background:#EAF8F5;color:#145349;padding:18px 22px;border-radius:10px;margin:15px 0;}
.status-warning{border-left:5px solid #F59E0B;background:#FFF6E7;color:#864809;padding:18px 22px;border-radius:10px;margin:15px 0;}
.status-alert{border-left:5px solid #E76F51;background:#FFF0EB;color:#853723;padding:18px 22px;border-radius:10px;margin:15px 0;}
.status-title{font-size:18px;font-weight:800;margin-bottom:5px;}
.status-copy{font-size:13px;line-height:1.5;}
.step-card {background:#FFFFFF;border:1px solid #E2EBF0;padding:15px 17px;border-radius:12px;margin-bottom:9px;}
.step-label {font-size:13px;color:#182F43;font-weight:750;}
.step-detail {font-size:12px;color:#708395;margin-top:4px;}
.note{font-size:12px;color:#708295;}
[data-testid="stMetric"] {background:#FFFFFF;border:1px solid #E6EFF2; border-radius:12px;padding:16px 17px;}
[data-testid="stMetricLabel"] p {color:#64748B !important;font-size:12px;font-weight:700;}
[data-testid="stMetricValue"] {color:#16364D !important;font-weight:800;}
div.stButton>button[kind="primary"] {background:#0D9488;border:0;border-radius:10px;font-weight:750;padding:.64rem 1.2rem;}
div.stButton>button[kind="primary"]:hover {background:#0F766E;}
[data-testid="stFileUploader"] {border-radius:13px;}
hr{border-color:#E5EDF2;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def demo_invoices():
    return sorted((ROOT / "samples").glob("*.pdf"))


def decision_panel(report):
    d = report["decision"]
    info = {
        "READY_FOR_APPROVAL":("status-good", "✓ Ready for AP approval"),
        "REVIEW_REQUIRED":("status-warning", "⚠ Manual review required"),
        "MISSING_INFORMATION":("status-warning", "◌ Information needed"),
        "DUPLICATE_HOLD":("status-alert", "⊘ Potential duplicate — hold"),
    }
    css, label = info.get(d, ("status-warning",d))
    st.markdown(f'<div class="{css}"><div class="status-title">{label}</div><div class="status-copy">{report["explanation"]}</div></div>',unsafe_allow_html=True)


def report_details(report, show_timeline=True, key_prefix="work"):
    decision_panel(report)
    data = report["invoice"]
    mt = report["matching"]
    a,b,c,d = st.columns(4)
    a.metric("Invoice total",fmt_money(data.get("total"),data.get("currency")))
    b.metric("Exceptions",str(len(report["findings"])))
    c.metric("Controls passed",f'{sum(x["passed"] for x in report["checks"])}/{len(report["checks"])}')
    d.metric("Run reference", f'#{report["run_id"]}')

    lt,rt = st.columns([1.05,.95],gap="large")
    with lt:
        st.markdown("#### Extracted invoice data")
        name_map = {"vendor_name":"Vendor", "invoice_number":"Invoice number", "po_number":"PO reference", "invoice_date":"Invoice date", "currency":"Currency", "subtotal":"Subtotal", "tax":"Tax", "total":"Total due"}
        rows=[{"Field":name_map[k], "Extracted value":(fmt_money(v,data.get("currency")) if k in ("subtotal","tax","total") and v is not None else (v if v is not None else "Not found"))} for k,v in data.items()]
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
        st.caption(f'Extraction mode: {report["extraction_mode"]}')
    with rt:
        st.markdown("#### Control results")
        for c in report["checks"]:
            symbol = "✅" if c["passed"] else "⚠️"
            st.markdown(f'{symbol}  **{c["name"]}**')
        if mt.get("vendor"):
            st.caption(f'Vendor matching: {mt["vendor"].get("match")}')
        financials=mt.get("financials")
        if financials:
            with st.expander("Purchase order balance breakdown",expanded=True):
                currency=data.get("currency")
                for key,label in (("po_amount","PO approved value"),("previously_billed","Already billed in ERP snapshot"),("committed_in_flowledger","Earlier FlowLedger recommendations"),("remaining_before_invoice","Balance before this invoice"),("tolerance_amount","Allowed tolerance"),("remaining_after_invoice","Balance after this invoice")):
                    st.markdown(f'**{label}:** {fmt_money(financials[key],currency)}')

    st.markdown("#### Exceptions and recommended actions")
    if not report["findings"]:
        st.success("No exceptions raised. The invoice passed all configured business controls.")
    else:
        for f in report["findings"]:
            with st.container(border=True):
                st.markdown(f'**{f["code"].replace("_"," ").title()}** · `{f["severity"].upper()}`')
                st.write(f["message"])
                if f.get("evidence"):
                    st.caption(f'Evidence: {f["evidence"]}')
    if show_timeline:
        st.markdown("#### Run audit trail")
        for s in report["workflow"]:
            if s["outcome"] != "done":
                continue
            st.markdown(f'<div class="step-card"><div class="step-label">✓ {s["label"]}</div><div class="step-detail">{s["detail"]}</div></div>',unsafe_allow_html=True)
    with st.expander("Assumptions, provenance and safe-use notes"):
        for n in report.get("notes",[]):
            st.write("• "+n)
        st.write(report["policy"])
        st.write("Vendor names require exact identity or an explicit registered alias; approximate names cannot pass automated approval.")
        st.write("Amount tolerance is PO-specific. An invoice within tolerance still requires manual review if it exceeds remaining balance.")
    json_str=json.dumps(report,indent=2,ensure_ascii=False)
    st.download_button("↓ Download decision report (JSON)",json_str, file_name=f'flowledger_run_{report["run_id"]}.json',mime="application/json", key=f'download_{key_prefix}_{report["run_id"]}')


with st.sidebar:
    st.markdown("### ◈ FLOWLEDGER")
    st.caption("INVOICE INTELLIGENCE SYSTEM")
    st.divider()
    st.markdown("**WORKFLOW COVERAGE**")
    st.markdown("✓ PDF & scanned invoices\n\n✓ Approved vendor matching\n\n✓ PO balance controls\n\n✓ Duplicate detection\n\n✓ Explainable decisions\n\n✓ Searchable run history")
    st.divider()
    st.markdown("**AI EXTRACTION (OPTIONAL)**")
    api_key = st.text_input("OpenAI API key", type="password", placeholder="sk-...", help="Only used for this browser session. If blank, the reliable local parser will run. Never paste a key in a screenshot or demo video.")
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", "")
        except Exception:
            api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        st.caption("● AI-assisted extraction available")
    else:
        st.caption("● Local PDF extraction active — no key required")
    st.divider()
    st.caption("Demonstration workflow · Synthetic vendor and purchase order data · No payment execution")

st.markdown('<div class="logo"><span class="logo-mark">◈</span> FlowLedger <span style="color:#0D9488">AI</span> <span class="pill">OPERATIONS COPILOT</span></div>',unsafe_allow_html=True)
st.markdown('<div class="headline">From invoice to insight.<br>Every exception explained.</div>',unsafe_allow_html=True)
st.markdown('<div class="subheadline">An auditable accounts payable workflow that reads invoices, validates purchase orders, prevents duplicate processing, and helps analysts decide what happens next.</div>',unsafe_allow_html=True)

try:
    db = create_db()
except Exception as exc:
    st.error(f"Unable to initialize the local run database: {exc}")
    st.stop()

worktab, historytab, policystab = st.tabs(["⚡ Invoice workbench", "▤ Run history", "⚙ Control policy"])
with worktab:
    st.markdown("### Start a new invoice review")
    st.caption("Upload a vendor PDF or select one of the realistic, prebuilt cases. The same processing engine handles both.")
    mode=st.radio("Input source",["Try a sample invoice", "Upload my own PDF"],horizontal=True)
    file_bytes = None
    filename = None
    if mode == "Try a sample invoice":
        samples=demo_invoices()
        names=[f.name for f in samples]
        if names:
            selected=st.selectbox("Demo invoice",names,help="Use 01 for the clean case, then re-run 01 for the duplicate case. Other numbered files test mismatches and missing data.")
            path=next(p for p in samples if p.name==selected)
            file_bytes=path.read_bytes()
            filename=path.name
            with st.expander("Preview sample document"):
                try:
                    import fitz
                    preview = fitz.open(stream=file_bytes,filetype="pdf")
                    page = preview[0].get_pixmap(matrix=fitz.Matrix(1.25,1.25))
                    st.image(page.tobytes("png"),width=620)
                    preview.close()
                except Exception:
                    st.caption("Document preview not available, but processing can still run.")
        else:
            st.warning("No sample files were found in the deployment.")
    else:
        uploaded=st.file_uploader("Select an invoice PDF",type=["pdf"],help="Maximum 10 MB; up to 10 pages; an OCR fallback handles scanned pages where supported.")
        if uploaded:
            filename=uploaded.name
            file_bytes=uploaded.getvalue()
    if st.button("▶ Run invoice review",type="primary",disabled=file_bytes is None,use_container_width=True):
        st.markdown("#### Live process execution")
        live_status=st.status("Running automated controls...",expanded=True,state="running")
        progress=st.progress(0,text="Processing document")
        done=set()
        def on_stage(stage_id, outcome, detail):
            if outcome == "done":
                live_status.write(f'✓ **{dict(STAGES)[stage_id]}** — {detail}')
                done.add(stage_id)
                progress.progress(int(len(done)/len(STAGES)*100),text=f'{len(done)} of {len(STAGES)} stages completed')
        try:
            result=process_invoice(file_bytes,filename,db,api_key=api_key,on_stage=on_stage)
            st.session_state["last_report"]=result
            live_status.update(label="Completed — recommendation and audit saved",state="complete",expanded=False)
        except Exception as exc:
            live_status.update(label="Workflow stopped safely",state="error",expanded=True)
            st.error(f"Processing failed: {exc}")
            st.info("This invoice was not processed or inserted into history. Check the PDF format and retry.")
    if st.session_state.get("last_report"):
        st.divider()
        st.markdown("### Decision output")
        report_details(st.session_state["last_report"])

with historytab:
    st.markdown("### Activity overview")
    st.caption("Each completed process run is logged with its input, decision, extraction method and full audit evidence.")
    history=get_history(db)
    n=len(history)
    approved=sum(x["decision"]=="READY_FOR_APPROVAL" for x in history)
    flags=sum(x["decision"]!="READY_FOR_APPROVAL" for x in history)
    dup=sum(x["decision"]=="DUPLICATE_HOLD" for x in history)
    a,b,c,d=st.columns(4)
    a.metric("Total processed",n)
    b.metric("Ready for approval",approved)
    c.metric("Exceptions flagged",flags)
    d.metric("Duplicate holds",dup)
    if not history:
        st.info("No runs yet. Process your first sample invoice in the Workbench to populate this dashboard.")
    else:
        df=pd.DataFrame(history)
        labels={"READY_FOR_APPROVAL":"Ready for approval","REVIEW_REQUIRED":"Review required","MISSING_INFORMATION":"Information needed","DUPLICATE_HOLD":"Duplicate hold"}
        summary=df["decision"].map(labels).value_counts().reset_index()
        summary.columns=["Decision","Count"]
        st.markdown("#### Decision distribution")
        st.bar_chart(summary.set_index("Decision"),height=230,horizontal=True)
        st.markdown("#### Audit register")
        display=df.rename(columns={"id":"Run","created_at":"UTC timestamp","filename":"Document","invoice_number":"Invoice no.","vendor_name":"Vendor","po_number":"PO","invoice_total":"Amount","currency":"Currency","decision":"Decision","extraction_mode":"Extraction"})
        st.dataframe(display,hide_index=True,use_container_width=True)
        choices=[x["id"] for x in history]
        selected=st.selectbox("Inspect a previous run",choices,format_func=lambda i:f'Run #{i} · {next(x["filename"] for x in history if x["id"]==i)}')
        prior=get_run(db,selected)
        if prior:
            report_details(prior,show_timeline=True,key_prefix="history")
    with st.expander("Demo maintenance"):
        st.warning("Resetting history deletes all demo run records and their invoice commitments. Do not do this before recording a video unless you want a clean demo.")
        confirm=st.checkbox("I understand that this will remove the history")
        if st.button("Reset all demo runs",disabled=not confirm):
            clear_history(db)
            st.session_state.pop("last_report",None)
            st.rerun()

with policystab:
    st.markdown("### Business control policy")
    st.caption("These are explicit case-study assumptions using synthetic master data. Edit the CSV files to adapt the business rules.")
    pos,vendors=load_masters()
    with st.expander("Registered vendors",expanded=True):
        st.dataframe(vendors.rename(columns={"vendor_id":"Vendor ID","vendor_name":"Legal name","aliases":"Known aliases","status":"Status","country":"Country"}),hide_index=True,use_container_width=True)
    with st.expander("Purchase order master",expanded=True):
        st.dataframe(pos,hide_index=True,use_container_width=True)
    st.markdown("#### Decision hierarchy")
    st.markdown("**1. Duplicate hold** if an invoice number/vendor pair or document hash appeared in a previous run.\n\n**2. Information needed** when a mandatory invoice field is missing.\n\n**3. Manual review** if vendor/PO/currency validation, budget, arithmetic, or date checks require investigation.\n\n**4. Ready for approval** only when all configured checks pass.")
    st.info("This is a decision-support demonstration, not a payment system. It does not verify live bank accounts, make payments, or connect to an ERP. The example PO master represents a static snapshot plus local run commitments.")
    st.markdown("#### Architecture")
    st.code("PDF input → PyMuPDF/OCR → structured field extraction (optional AI) → vendor/PO lookup → deterministic policy checks → decision → SQLite audit trail → dashboard", language="text")
    st.markdown("#### Reliability & security")
    st.markdown("Input size and page limits · no silent guessing of missing values · evidence checks for optional AI suggestions · exact vendor identity for approval · blocked duplicate invoices · cautious human-review outcomes · database audit records.")

st.divider()
st.caption("FLOWLEDGER AI  ·  Zamp ASA case-study demonstration  ·  Real processing, explainable decisions  ·  All sample company data is synthetic")
