import copy
import hashlib
from collections import Iterable
import re
import reportlab.platypus as plat
from reportlab.lib import colors
from reportlab.lib.pagesizes import cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus.tableofcontents import TableOfContents

STYLES = getSampleStyleSheet()


def _get_style(style):
  if isinstance(style, ParagraphStyle):
    return style
  if isinstance(style, str):
    return STYLES[style]
  raise TypeError("unknown style: %s" % style)

def _optiondict2xml(dct):
  return ' '.join(["%s='%s'" % (k, v) for k, v in dct.iteritems()])

def get_index_link(text, style='Normal'):
  style = _get_style(style)
  bookmark = hashlib.sha224(text+style.name).hexdigest()
  return bookmark

Spacer = plat.Spacer
Image = plat.Image


def TableOfContent():
  """
  Create table of content
  Added for compatibility reasons with docxlab and textilab
  :return: tuple of elements, add it to the story (+=) or extend it with these, do not append!
  """
  toc = TableOfContents()
  toc.levelStyles = [
    ParagraphStyle(fontSize=14, name='Heading1', leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=16),
    ParagraphStyle(fontSize=12, name='Heading2', leftIndent=40, firstLineIndent=-20, spaceBefore=0, leading=12),
    ParagraphStyle(fontSize=10, name='Heading3', leftIndent=60, firstLineIndent=-20, spaceBefore=0, leading=12),
  ]
  return toc


def IndexedParagraph(text, style='Normal', **kwargs):
  """
  Factory for paragraphs to be numbered and shown in the table of contents.
  
  :Parameters:
    style : str or reportlab.lib.styles.ParagraphStyle, optional
      The style of the paragraph. If string, the given named style will be used
      from the default reportlab styles.
  :Keywords:
    * : *
      Any valid `Paragraph` keyword.
  """
  style = _get_style(style)
  # generate bookmarkname
  bn = get_index_link(text, style)
  # define sequence tag
  if style.name == 'Heading1':
    seq = '<seq id="section"/><seqreset id="subsection"/>. '
  elif style.name == 'Heading2':
    seq = '<seq template="%(section)s.%(subsection+)s"/>' \
          '<seqreset id="subsubsection"/>. '
  elif style.name == 'Heading3':
    seq = '<seq template="%(section)s.%(subsection)s.%(subsubsection+)s"/>. '
  else:
    raise NotImplementedError(
      "unsupported paragraph type for indexing: %s" % style.name)
  # modify paragraph text to include an anchor point with name 'bn'
  link = '<a name="%s"/>' % bn
  h = Paragraph(seq + text + link, style, **kwargs)
  # store the bookmark name on the flowable so afterFlowable can see this
  h._bookmarkName = bn
  return h

def Paragraph(text, style='Normal', **kwargs):
  """
  Create a formatted paragraph.
  
  :Parameters:
    text : str, plat.Paragraph
      The item text itself, or a Paragraph that we want to reformat.
    style : str or reportlab.lib.styles.ParagraphStyle, optional
      The style of the paragraph. If string, the given named style will be used
      from the default reportlab styles.
  :Keywords:
    bulletText : str
      The text of the list symbol. Custom text as well as HTML symbols are
      supported. Default symbol is a bullet.
    caseSensitive : int
      Set to 0 if you want the markup tags and their attributes to be
      case-insensitive, otherwise 1.
    bold : boolean
      The text of the paragraph will become bold
    italic : boolean
      The text of the paragraph will become italic
    underline : boolean
      The text of the paragraph will become underlined
    size : int
      Sets the size of the font being used for the paragraph
    alignment : {'LEFT', 'CENTER', 'RIGHT'}
      Alignment of the paragraph on the page or in a table cell
    * : *
      Any valid `para` tag option.
  
  :ReturnType: reportlab.platypus.Paragraph
  :Return: The formatted paragraph.
  """
  # TODO add paragraph reformat
  style = _get_style(style)
  bulletText = kwargs.pop('bulletText', None)
  caseSensitive = kwargs.pop('caseSensitive', 1)

  # Pop text and font styles - only plat.paragraph kwargs should be left!
  is_underline = kwargs.pop('underline', False)
  is_italic = kwargs.pop('italic', False)
  is_bold = kwargs.pop('bold', False)
  font_size = kwargs.pop('size', None)

  if isinstance(text, plat.Paragraph):
    # Previous paragraph formating and adding new
    options = ""
    para_option_dict = dict()
    prevparatext = _get_para_text(text.text)
    # Get previous paragraph options
    for m in re.finditer(" (\w*)='(\w*)'", prevparatext):
      para_option_dict[m.group(1)] = m.group(2)
    para_option_dict.update(kwargs)
    # save it back to kwargs
    kwargs = para_option_dict
    text = _get_text(text.text)  # get the text between para tags

  # Global formatting for text and font
  font_text = _get_font_text(text)
  raw_text = _get_raw_text(text)
  if is_underline:
    raw_text = underline(raw_text)
  if is_italic:
    raw_text = italic(raw_text)
  if is_bold:
    raw_text = bold(raw_text)
  # Create font tags with previous font formatting
  raw_text_with_font = "<font{1}>{0}</font>".format(raw_text, font_text)

  # Add new font formatting
  if font_size is not None:
    raw_text_with_font = _size(raw_text_with_font, font_size)
    kwargs['leading'] = int(font_size * 1.2)

  options = _optiondict2xml(kwargs)
  paratext = "<para %s>%s</para>" % (options, raw_text_with_font)
  parag = plat.Paragraph(
    paratext, style, bulletText=bulletText, caseSensitive=caseSensitive)
  return parag


def Table(data, style=None, **kwargs):
  # TODO check if cell data is tuple and not Paragraph or basestring

  # Convert it to be BodyText, this way it will try fit the cells horizontally
  for i, row in zip(range(len(data)), data):
    for j, cell_text in zip(range(len(row)), row):
      if isinstance(data[i][j], (basestring, plat.Paragraph)):
        data[i][j] = Paragraph(cell_text, 'BodyText')

  def _get_base_indices(c):
    if not isinstance(c, (list, tuple)):
      raise TypeError("Indices must be an (int,int), not '{}'".format(type(c)))
    cell = list(c)
    cell[0] = len(data[0]) + c[0] if c[0] < 0 else c[0]
    cell[1] = len(data) + c[1] if c[1] < 0 else c[1]
    return cell

  reportlab_styles = []
  if style is not None:
    for s in style:
      if isinstance(s, Iterable) and not isinstance(s, basestring):
        if s[0] == 'TEXT_STYLE':
          luc = _get_base_indices(s[1])
          rbc = _get_base_indices(s[2])
          if not isinstance(s[3], dict):
            raise TypeError("Styles must be a dictionary, not {}".format(type(s[1])))
          # Decorate box with s[3] styling
          for i in range(luc[0], rbc[0] + 1):  # column indices
            for j in range(luc[1], rbc[1] + 1):  # row indices
              if isinstance(data[j][i], plat.Paragraph):
                data[j][i] = Paragraph(data[j][i], 'BodyText', **s[3])
          continue

        elif s[0] == 'ALIGN':
          # Format the paragraphs
          luc = _get_base_indices(s[1])
          rbc = _get_base_indices(s[2])
          for i in range(luc[0], rbc[0] + 1):  # column indices
            for j in range(luc[1], rbc[1] + 1):  # row indices
              if isinstance(data[j][i], plat.Paragraph):
                data[j][i] = Paragraph(data[j][i], 'BodyText', alignment=s[3])
          # Add it the formatting command to plat as well
          reportlab_styles.append(s)
          continue

        elif s[0] == 'TEXT_DIRECTION':
          # TODO parse text_direction
          continue
        else:
          reportlab_styles.append(s)
  t = plat.Table(data, **kwargs)
  t.setStyle(reportlab_styles)
  return t

EMPTY_MSG = "No items to display."
def NonEmptyTable(data, **kwargs):
  if len(data) > 0:
    return plat.Table(data, **kwargs)
  return Paragraph(EMPTY_MSG)

def NonEmptyTableWithHeader(data, **kwargs):
  # header-only still counts as empty table
  # TODO: handle tables with and without header in a cleaner way
  if len(data) > 1:
    return plat.Table(data, **kwargs)
  return Paragraph(EMPTY_MSG)

def bullet(symbol="&bull;", indent=20):
  text = "<bullet bulletIndent='%d'>%s</bullet>" % (indent, symbol)
  return text

def ListItem(text, style='Normal', level=0, levels= [],
             symbol="bullet", indent=20, indent_after=10):
  """
  Create a list item.
  
  :Parameters:
    text : str
      The item text itself.
    style : str or reportlab.lib.styles.ParagraphStyle, optional
      The style of the paragraph. If string, the given named style will be used
      from the default reportlab styles.
    level : int, optional
      The depth of the actual list item in the list. Default is 0.
    symbol : str, optional
      The text of the list symbol. Custom text as well as HTML symbols are
      supported. Default symbol is a bullet.
    indent : float, optional
      The left indentation of the item, i.e. the bullet offset.
    indent_after : float, optional
      The offset after the bullet (including the bullet size). Setting it to 0
      results that the next lines will start right below the bullet (if the
      item is split into multiple lines).
      Remark: There is a default minimal gap between the bullet and the text
      (which affects the first line of the item).
  
  :ReturnType: reportlab.platypus.Paragraph
  :Return: The list item as a paragraph.
  """
  style = copy.copy(_get_style(style))  # copy for _local_ modifications

  if symbol == "bullet":
    symbol = "&bull;"
    bullet_indent = style.leftIndent + (level + 1) * indent
    style.leftIndent = bullet_indent + indent_after  # indent text as line above
    full_text = "%s%s" % (bullet(symbol=symbol, indent=bullet_indent), text)
  elif symbol == 'number':
    bullet_indent = style.leftIndent + (level + 1) * indent
    style.leftIndent = bullet_indent  # indent text as line above
    seq = ''
    for i in range(len(levels)):
      if levels[i] > 0:
        seq += str(levels[i])+'.'
    full_text = "%s%s" % (seq+' ', text)
  else:
    full_text = text

  parag = Paragraph(full_text, style)
  return parag


def List(texts, style='Normal', init_level=0, levels=[0], **kwargs):
  """
  Create a list of `ListItem`-s recursively from an embedded iterable input.
  For example, calling
  
    List([1, 'a', ['aa'], 'b', [3, ['bb'], 'cc']], style)
  
  will create a pdf output similar like:
  
    * 1
    * a
      * aa
    * b
      * 3
        * bb
      * cc
  
  :Parameters:
    texts : iterable
      The list, tuple, etc. of objects to be included in the list.
    style : str or reportlab.lib.styles.ParagraphStyle, optional
      The style of the paragraph. If string, the given named style will be used
      from the default reportlab styles.
    init_level : int, optional
      The starting depth of the list.
  :Keywords:
    symbol : str
      See `ListItem` for details.
    indent : float
      See `ListItem` for details.
    indent_after : float
      See `ListItem` for details.
  
  :ReturnType: list
  :Return: [<reportlab.platypus.Paragraph>,]
    The list of paragraphs with the list items.
  """

  style = _get_style(style)
  listitems = []
  for item in texts:
    if isinstance(item, Iterable) and not isinstance(item, basestring):
      levels += [0]
      listitems.extend(List(item, style, init_level=init_level+1, levels=levels,  **kwargs))
    else:
      levels[init_level] += 1
      for i in range(init_level + 1, len(levels)):
        levels[i] = 0
      listitems.append(ListItem(item, style, level=init_level, levels=levels, **kwargs))
  # Add a spacer after the list
  listitems.append(Spacer(width=1*cm, height=0.2*cm))
  return listitems


def _get_para_text(text):
  m = re.search("<para( .*?)>", text)
  if m is None:
    text = ''
  else:
    text = m.group(1)
  return text

def _get_text(text):
  # get text between para tags (with font as well)
  m = re.search("<para .*?>(.*)</para>", text)
  if m is None:
    pass  # There are not para tags
  else:
    text = m.group(1)
  return text

def _get_font_text(text):
  text = _get_text(text)
  m = re.search("<font( .*?)>", text)
  if m is None:
    text = ''
  else:
    text = m.group(1)
  return text

def _get_raw_text(text):
  # get text between font tags
  text = _get_text(text)
  m = re.search("<font .*?>(.*)</font>", text)
  if m is None:
    pass  # There are no font tags
  else:
    text = m.group(1)
  return text


def bold(text):
  text = "<b>%s</b>" % text.replace('<b>', '').replace('</b>', '')
  return text

def underline(text):
  text = "<u>%s</u>" % text.replace('<u>', '').replace('</u>', '')
  return text

def italic(text):
  text = "<i>%s</i>" % text.replace('<i>', '').replace('</i>', '')
  return text

def superscript(text):
  text = "<super>%s</super>" % text.replace('<super>', '').replace('</super>', '')
  return text

def subscript(text):
  text = "<sub>%s</sub>" % text.replace('<sub>', '').replace('</sub>', '')
  return text

def _size(text, font_size):
  options = ''
  for m in re.finditer(" (\w*)='(\w*)'", _get_font_text(text)):
    if m.group(1) != 'size':
      options += m.group(0)
    else:
      options += " size='{}'".format(font_size)
  # It did not have size before
  if options == '':
    options += " size='{}'".format(font_size)
  text = _get_raw_text(text)
  text = "<font{1}>{0}</font>".format(text, options)
  return text


def decorate(text, **kwargs):
  """
  Format text.
  
  :Keywords:
    bold : bool
      Bold text.
    italic : bool
      Italic text.
    underline : bool
      Underlined text.
    size : float
      Font size.
    face, name : str
      Name of the font face.
    color, fg : str
      Color of the text. HTML colors are accepted.
  
  :ReturnType: str
  :Return: Formatted text.
  """
  is_bold = kwargs.pop('bold', False)
  is_underlined = kwargs.pop('underline', False)
  is_italic = kwargs.pop('italic', False)

  if is_bold:
    text = bold(text)
  if is_underlined:
    text = underline(text)
  if is_italic:
    text = italic(text)
  options = _optiondict2xml(kwargs)
  # TODO check if previous font has to be deleted
  text = "<font %s>%s</font>" % (options, text)
  return text

def Link(link, text, color='blue'):
  text = "<a href='%s' color='%s'>%s</a>" % (link, color, text)
  return text

def LinkDst(name):
  text = "<a name='%s'/>" % name
  return text

dtc_table = [
  ('GRID', (0, 0), (-1, -1), 0.025 * cm, colors.black),
  ('FONT', (0, 0), (-1, 0), '%s-Bold' % 'Helvetica',  7),
  ('FONT', (0, 1), (-1, -1), 'Helvetica',  7),
  ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
  ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
]

grid_table_style = [
  ('INNERGRID', (0, 0), (-1, -1), 0.025*cm, colors.black),
  ('BOX',       (0, 0), (-1, -1), 0.025*cm, colors.black),
  ('FONT',      (0, 0), (-1,  0), 'Helvetica-Bold'),
]


