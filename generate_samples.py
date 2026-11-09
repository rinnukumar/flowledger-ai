"""Generate fictional, realistic invoice PDFs; can be re-run independently."""
from io import BytesIO
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'samples'
OUT.mkdir(exist_ok=True)

SAMPLES=[
    dict(file='01_clean_invoice.pdf', supplier='Acme Technology Services', number='ACT-2026-104', date='2026-11-02', po='PO-1001', currency='USD', subtotal=4250, tax=250, total=4500, description='Cloud migration implementation'),
    dict(file='02_overbudget_invoice.pdf', supplier='BrightPath Consulting', number='BPC-2026-221', date='2026-11-03', po='PO-1002', currency='USD', subtotal=1600, tax=200, total=1800, description='Operations advisory - phase II'),
    dict(file='03_missing_fields_invoice.pdf', supplier='Northstar Office Supply', number=None, date=None, po='PO-1003', currency='USD', subtotal=1500, tax=0, total=1500, description='Office supply restock'),
    dict(file='04_vendor_po_mismatch.pdf', supplier='BrightPath Consulting', number='BPC-2026-222', date='2026-11-04', po='PO-1001', currency='USD', subtotal=900, tax=100, total=1000, description='Consultancy - mismatched PO'),
    dict(file='05_currency_mismatch.pdf', supplier='Acme Technology Services', number='ACT-2026-107', date='2026-11-05', po='PO-1001', currency='EUR', subtotal=800, tax=100, total=900, description='Cloud services - incorrect currency'),
    dict(file='06_arithmetic_mismatch.pdf', supplier='Northstar Office Supply', number='NS-2026-045', date='2026-11-06', po='PO-1003', currency='USD', subtotal=1000, tax=180, total=1380, description='Workstation equipment'),
    dict(file='07_split_po_invoice.pdf', supplier='Northstar Office Supply', number='NS-2026-046', date='2026-11-07', po='PO-1003', currency='USD', subtotal=2400, tax=100, total=2500, description='Office equipment - first delivery'),
    dict(file='08_split_po_invoice.pdf', supplier='Northstar Office Supply', number='NS-2026-047', date='2026-11-08', po='PO-1003', currency='USD', subtotal=1700, tax=100, total=1800, description='Office equipment - second delivery'),
    dict(file='10_late_split_over_budget.pdf', supplier='Northstar Office Supply', number='NS-2026-048', date='2026-11-08', po='PO-1003', currency='USD', subtotal=4900, tax=100, total=5000, description='Office equipment - final delivery'),
]

def render_invoice(d):
    buf=BytesIO()
    c=canvas.Canvas(buf,pagesize=A4)
    w,h=A4
    navy=colors.HexColor('#12293E')
    green=colors.HexColor('#0C8F83')
    light=colors.HexColor('#E8F3F2')
    c.setFillColor(navy);c.rect(0,h-125,w,125,fill=1,stroke=0)
    c.setFillColor(colors.white);c.setFont('Helvetica-Bold',24);c.drawString(42,h-60,'INVOICE')
    c.setFont('Helvetica',11);c.drawString(42,h-86,'Professional services  /  Accounts payable')
    c.setFillColor(green);c.roundRect(w-174,h-93,128,32,12,fill=1,stroke=0)
    c.setFillColor(colors.white);c.setFont('Helvetica-Bold',9);c.drawCentredString(w-110,h-80,'PAYMENT REQUEST')
    y=h-167
    c.setFillColor(colors.HexColor('#6B8091'));c.setFont('Helvetica-Bold',9);c.drawString(42,y,'SUPPLIER')
    c.setFillColor(navy);c.setFont('Helvetica-Bold',15);c.drawString(42,y-22,d['supplier'])
    c.setFillColor(colors.HexColor('#718595'));c.setFont('Helvetica',10);c.drawString(42,y-41,'Fictional supplier · training sample only')
    y-=105
    fields=[('Invoice No',d['number']),('Invoice Date',d['date']),('Purchase Order',d['po']),('Currency',d['currency'])]
    c.setFillColor(light);c.roundRect(39,y-85,w-78,96,11,fill=1,stroke=0)
    for idx,(label,val) in enumerate(fields):
        x=54+(idx%2)*264;yy=y-(idx//2)*42
        c.setFillColor(colors.HexColor('#5D7789'));c.setFont('Helvetica-Bold',9);c.drawString(x,yy,label+':')
        c.setFillColor(navy);c.setFont('Helvetica',11);c.drawString(x,yy-18,str(val) if val is not None else '')
    y-=130
    c.setFillColor(navy);c.setFont('Helvetica-Bold',12);c.drawString(42,y,'DESCRIPTION')
    c.drawRightString(w-42,y,'AMOUNT')
    c.setStrokeColor(colors.HexColor('#D5E1E8'));c.line(42,y-10,w-42,y-10)
    c.setFont('Helvetica',11);c.drawString(42,y-44,d['description'])
    c.drawRightString(w-42,y-44,f"{d['subtotal']:,.2f}")
    c.line(42,y-62,w-42,y-62)
    def amount(label,value,y):
        c.setFillColor(colors.HexColor('#597184'));c.setFont('Helvetica',11);c.drawRightString(w-176,y,label+':')
        c.setFillColor(navy);c.setFont('Helvetica-Bold',11);c.drawRightString(w-42,y,f"$ {value:,.2f}")
    amount('Subtotal',d['subtotal'],y-98)
    amount('Tax',d['tax'],y-129)
    c.setFillColor(light);c.roundRect(w-305,y-186,266,39,8,fill=1,stroke=0)
    c.setFillColor(navy);c.setFont('Helvetica-Bold',12);c.drawRightString(w-176,y-172,'Total Due:')
    c.setFillColor(green);c.drawRightString(w-50,y-172,f"$ {d['total']:,.2f}")
    c.setFillColor(colors.HexColor('#748A99'));c.setFont('Helvetica',9)
    c.drawString(42,77,'This invoice is fabricated for the Zamp ASA case study and is not payable.')
    c.drawString(42,61,'Please reconcile with the approved purchase order before any approval.')
    c.save()
    return buf.getvalue()

if __name__=='__main__':
    for d in SAMPLES:
        (OUT/d['file']).write_bytes(render_invoice(d))
    # Image-only PDF validates the actual OCR fallback path.
    import fitz
    from PIL import Image
    native=render_invoice({**SAMPLES[0], 'number':'ACT-2026-109', 'total':1100, 'subtotal':1000, 'tax':100})
    p=fitz.open(stream=native,filetype='pdf')
    page=p[0]
    pix=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
    image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    out=BytesIO();image.save(out,format='PDF',resolution=145.0)
    (OUT/'09_scanned_image_invoice.pdf').write_bytes(out.getvalue())
    p.close()
    print('Generated:',len(list(OUT.glob('*.pdf'))),'sample invoice PDFs')
