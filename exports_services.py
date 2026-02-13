from fpdf import FPDF

def create_pdf(meeting, actions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(40, 10, f"Minutes: {meeting.title}")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Notes: {meeting.description}")
    
    pdf.ln(5)
    pdf.cell(40, 10, "Action Items:")
    for item in actions:
        pdf.ln(8)
        pdf.cell(0, 10, f"- {item.task} (Assigned to: {item.assigned_to})")
    
    # Return the byte string of the PDF
    return pdf.output(dest='S').encode('latin-1')