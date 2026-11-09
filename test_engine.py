import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from engine import create_db, process_invoice, extract_pdf, regex_extract, get_history, get_run, find_vendor, load_masters

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def db(tmp_path):
    conn=create_db(tmp_path/'test_history.sqlite3')
    yield conn
    conn.close()

def run(db,name):
    file=ROOT/'samples'/name
    return process_invoice(file.read_bytes(),file.name,db)

def codes(r):
    return {x['code'] for x in r['findings']}

def test_happy_path(db):
    r=run(db,'01_clean_invoice.pdf')
    assert r['decision']=='READY_FOR_APPROVAL'
    assert r['invoice']['invoice_number']=='ACT-2026-104'
    assert r['matching']['financials']['remaining_before_invoice']==9000
    assert r['matching']['financials']['remaining_after_invoice']==4500
    assert len([x for x in r['workflow'] if x['outcome']=='done'])==5
    assert len(get_history(db))==1
    assert get_run(db,r['run_id'])['decision']==r['decision']

def test_duplicate_identical_upload(db):
    r1=run(db,'01_clean_invoice.pdf')
    r2=run(db,'01_clean_invoice.pdf')
    assert r1['decision']=='READY_FOR_APPROVAL'
    assert r2['decision']=='DUPLICATE_HOLD'
    assert 'POTENTIAL_DUPLICATE' in codes(r2)

def test_over_budget(db):
    r=run(db,'02_overbudget_invoice.pdf')
    assert r['decision']=='REVIEW_REQUIRED'
    assert 'PO_OVER_BUDGET' in codes(r)

def test_missing_fields(db):
    r=run(db,'03_missing_fields_invoice.pdf')
    assert r['decision']=='MISSING_INFORMATION'
    assert 'MISSING_INVOICE_NUMBER' in codes(r)
    assert 'MISSING_INVOICE_DATE' in codes(r)

def test_po_vendor_mismatch(db):
    r=run(db,'04_vendor_po_mismatch.pdf')
    assert r['decision']=='REVIEW_REQUIRED'
    assert 'VENDOR_PO_MISMATCH' in codes(r)

def test_currency_mismatch(db):
    r=run(db,'05_currency_mismatch.pdf')
    assert r['decision']=='REVIEW_REQUIRED'
    assert 'CURRENCY_MISMATCH' in codes(r)

def test_arithmetic_mismatch(db):
    r=run(db,'06_arithmetic_mismatch.pdf')
    assert r['decision']=='REVIEW_REQUIRED'
    assert 'TOTAL_ARITHMETIC_MISMATCH' in codes(r)

def test_split_invoices_cumulative_budget(db):
    r1=run(db,'07_split_po_invoice.pdf')
    r2=run(db,'08_split_po_invoice.pdf')
    assert r1['decision']=='READY_FOR_APPROVAL'
    assert r2['decision']=='READY_FOR_APPROVAL'
    assert r2['matching']['financials']['committed_in_flowledger']==2500
    assert r2['matching']['financials']['remaining_after_invoice']==3700

def test_image_only_scanned_pdf_ocr(db):
    r=run(db,'09_scanned_image_invoice.pdf')
    assert r['decision']=='READY_FOR_APPROVAL'
    assert r['invoice']['invoice_number']=='ACT-2026-109'
    assert 'OCR' in r['extraction_mode']

def test_invalid_pdf_rejected_without_logging(db):
    with pytest.raises(ValueError,match='not a valid PDF'):
        process_invoice(b'not a pdf','bogus.pdf',db)
    assert get_history(db)==[]

def test_fuzzy_vendor_does_not_auto_authorize():
    pos,vendors=load_masters()
    v,why=find_vendor('Acme Technology Servics',vendors)
    assert v is None
    assert 'manual verification' in why

def test_split_po_late_invoice_exceeds_cumulative_balance(db):
    assert run(db,'07_split_po_invoice.pdf')['decision']=='READY_FOR_APPROVAL'
    assert run(db,'08_split_po_invoice.pdf')['decision']=='READY_FOR_APPROVAL'
    third=run(db,'10_late_split_over_budget.pdf')
    assert third['decision']=='REVIEW_REQUIRED'
    assert third['matching']['financials']['remaining_before_invoice']==3700
    assert 'PO_OVER_BUDGET' in codes(third)
