"""One-command end-to-end smoke run. Creates no persistent database."""
from pathlib import Path
from tempfile import TemporaryDirectory
from engine import create_db, process_invoice

root=Path(__file__).resolve().parent
cases=[
    ("01_clean_invoice.pdf","READY_FOR_APPROVAL"),
    ("01_clean_invoice.pdf","DUPLICATE_HOLD"),
    ("02_overbudget_invoice.pdf","REVIEW_REQUIRED"),
    ("03_missing_fields_invoice.pdf","MISSING_INFORMATION"),
    ("09_scanned_image_invoice.pdf","READY_FOR_APPROVAL"),
]
with TemporaryDirectory() as td:
    db=create_db(Path(td)/"smoke.sqlite3")
    for name, expected in cases:
        path=root/'samples'/name
        result=process_invoice(path.read_bytes(),name,db)
        actual=result['decision']
        print(f"{name:<34} {actual:<22} {'PASS' if actual==expected else 'FAIL'}")
        assert actual==expected, (name,actual,expected)
    db.close()
print("All 5 smoke scenarios passed.")
