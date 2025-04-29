from reportlab.platypus import Paragraph
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()


def intro(title, summary):
  story = [
    Paragraph(title, styles['Title']),
    Paragraph('Scope', styles['Heading1']),
    Paragraph(summary, styles["Normal"]),
  ]
  return story

def toc():
  story = [
    Paragraph("Table of contents", styles['Heading1']),
    TableOfContents(),
  ]
  return story

