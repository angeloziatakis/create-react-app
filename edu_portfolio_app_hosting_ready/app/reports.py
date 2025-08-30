import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def build_student_report(student_email: str, assignments: list, stats: dict) -> bytes:
    """Create a very simple PDF with student progress summary."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2*cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y, f"Progress Report: {student_email}")
    y -= 1*cm

    c.setFont("Helvetica", 12)
    c.drawString(2*cm, y, f"Total Assignments: {stats.get('total', 0)}")
    y -= 0.6*cm
    c.drawString(2*cm, y, f"Reviewed: {stats.get('reviewed', 0)} | Returned: {stats.get('returned', 0)} | Submitted: {stats.get('submitted', 0)}")
    y -= 1*cm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(2*cm, y, "Recent Assignments:")
    y -= 0.7*cm
    c.setFont("Helvetica", 10)
    for a in assignments[:10]:
        line = f"#{a.id} {a.original_name} — {a.status} — {a.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
        c.drawString(2*cm, y, line[:95])
        y -= 0.5*cm
        if y < 3*cm:
            c.showPage(); y = height - 2*cm

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
