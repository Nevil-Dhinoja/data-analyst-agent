from fpdf import FPDF
import os
import re
from datetime import datetime

class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(33, 150, 243)
        self.cell(0, 10, "Data Analyst Agent - Report", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"Page {self.page_no()} - Built by Nevil Dhinoja",
                  align="C")

def sanitise(text):
    """Remove markdown and replace unicode chars fpdf can't handle."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    # replace common unicode that breaks Helvetica
    replacements = {
        '\u2014': '-',   # em dash
        '\u2013': '-',   # en dash
        '\u2019': "'",   # right single quote
        '\u2018': "'",   # left single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2022': '-',   # bullet
        '\u00a0': ' ',   # non-breaking space
        '\u2026': '...', # ellipsis
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # strip anything still outside latin-1
    text = text.encode('latin-1', errors='ignore').decode('latin-1')
    return text.strip()

def generate_pdf(goal: str, report: str, chart_paths: list) -> str:
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Goal
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 7, sanitise(f"Analysis Goal: {goal}"))
    pdf.ln(4)

    # Report text
    for line in report.split('\n'):
        line = sanitise(line)
        if not line:
            pdf.ln(3)
        elif line.startswith('## '):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(33, 150, 243)
            pdf.multi_cell(0, 8, line[3:])
            pdf.set_text_color(50, 50, 50)
        elif line.startswith('# '):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(21, 101, 192)
            pdf.multi_cell(0, 9, line[2:])
            pdf.set_text_color(50, 50, 50)
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, f"  - {line[2:]}")
        elif line.startswith('|'):
            pdf.set_font("Courier", "", 9)
            pdf.multi_cell(0, 5, line)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, line)

    # Charts
    for chart in chart_paths:
        if os.path.exists(chart):
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(50, 50, 50)
            name = os.path.basename(chart).replace('_',' ').replace('.png','').title()
            pdf.cell(0, 8, name, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            try:
                pdf.image(chart, x=15, w=180)
            except Exception:
                pass

    path = f"outputs/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(path)
    return path