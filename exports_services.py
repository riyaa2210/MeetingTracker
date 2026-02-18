from fpdf import FPDF
from datetime import datetime


class MeetingPDF(FPDF):

    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Meeting Outcome Report", align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(
            0,
            10,
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            align="C"
        )


def create_pdf(meeting, actions):
    pdf = MeetingPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, f"Title: {meeting.title}")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"Date: {meeting.date}")
    pdf.ln(5)

    pdf.multi_cell(0, 8, f"Notes:\n{meeting.description}")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Action Items:")
    pdf.ln(8)

    pdf.set_font("Arial", "", 12)

    if not actions:
        pdf.cell(0, 8, "No action items recorded.")
    else:
        for idx, item in enumerate(actions, 1):
            pdf.multi_cell(
                0,
                8,
                f"{idx}. {item.task}\n"
                f"Assigned to: {item.assigned_to}\n"
                f"Status: {item.status}\n"
                f"Due Date: {item.due_date or 'Not Set'}"
            )
            pdf.ln(4)

    return pdf.output(dest="S").encode("latin-1")
