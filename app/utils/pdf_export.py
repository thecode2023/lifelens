"""PDF export for Community Health Profiles."""
from fpdf import FPDF
import re
from io import BytesIO


class ProfilePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'LifeLens | Community Health Profile', align='R')
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')


def markdown_to_pdf(markdown_text: str, county_name: str = '') -> bytes:
    """Convert markdown profile text to PDF bytes."""
    pdf = ProfilePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    lines = markdown_text.split('\n')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(4)
            continue

        # H1
        if stripped.startswith('# ') and not stripped.startswith('## '):
            pdf.set_font('Helvetica', 'B', 18)
            pdf.set_text_color(30, 30, 30)
            text = stripped[2:].strip()
            pdf.cell(0, 12, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            # underline
            pdf.set_draw_color(59, 130, 246)
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(6)

        # H2
        elif stripped.startswith('## '):
            pdf.set_font('Helvetica', 'B', 13)
            pdf.set_text_color(50, 50, 50)
            text = stripped[3:].strip()
            pdf.ln(4)
            pdf.cell(0, 9, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

        # H3
        elif stripped.startswith('### '):
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(70, 70, 70)
            text = stripped[4:].strip()
            pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        # Table row
        elif stripped.startswith('|') and '---' not in stripped:
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if cells:
                pdf.set_font('Helvetica', '', 9)
                pdf.set_text_color(60, 60, 60)
                col_width = (190) / max(len(cells), 1)
                for cell in cells:
                    clean = re.sub(r'\*\*(.*?)\*\*', r'\1', cell)
                    pdf.cell(col_width, 7, clean, border=1, align='C')
                pdf.ln()

        # Horizontal rule
        elif stripped.startswith('---'):
            pdf.ln(3)
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.3)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

        # Bullet points
        elif stripped.startswith('- ') or stripped.startswith('* '):
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(40, 40, 40)
            text = stripped[2:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            pdf.cell(8, 6, chr(8226))  # bullet
            pdf.multi_cell(172, 6, text)

        # Italic/note lines
        elif stripped.startswith('*') and stripped.endswith('*'):
            pdf.set_font('Helvetica', 'I', 8)
            pdf.set_text_color(120, 120, 120)
            text = stripped.strip('*').strip()
            pdf.multi_cell(0, 5, text)

        # Regular paragraph
        else:
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(40, 40, 40)
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
            pdf.multi_cell(0, 6, text)

    # Return as bytes
    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()
