#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import re


class TextileFlowable(object):
  def __init__(self, *args, **kwargs):
    return
  
  def _print(self):
    return ""
  
  def print_(self):
    return self._print() + "\n"


class Spacer(TextileFlowable):
  def __init__(self, *args, **kwargs):
    # TODO: handle width, height
    return
  
  def _print(self):
    return "\n"  # dummy (no real effect)


class Paragraph(TextileFlowable):
  def __init__(self, text, style='Normal', **kwargs):
    if isinstance(text, Paragraph):
      text = text.text
    self.text = decorate(text, **kwargs)
    self.style = style
    return
  
  def _print(self):
    dd = {
      'Normal': "%(text)s\n",
      'Heading1': "h1. %(text)s\n",
      'Heading2': "h2. %(text)s\n",
      'Heading3': "h3. %(text)s\n",
    }
    return dd[self.style] % dict(text=self.text)


class TableOfContent(TextileFlowable):
  def __init__(self):
    pass

  def _print(self):
    return '{{toc}}\n'


class IndexedParagraph(Paragraph):
  """
    Supports 3 levels : Heading1, Heading2, Heading3
  """
  entries = [0, 0, 0]

  def __init__(self, text, style='Normal', **kwargs):
    # Create numbering
    if style == 'Heading1':
      self.entries[0] += 1
      self.entries[1] = 0
      self.entries[2] = 0
      new_text = "{} {}".format(str(self.entries[0]), text)
      super(IndexedParagraph, self).__init__(new_text, style, **kwargs)
    if style == 'Heading2':
      if self.entries[0] == 0:
        self.entries[0] += 1
      self.entries[1] += 1
      self.entries[2] = 0
      new_text = "{}.{} {}".format(str(self.entries[0]), str(self.entries[1]), text)
      super(IndexedParagraph, self).__init__(new_text, style, **kwargs)
    if style == 'Heading3':
      if self.entries[0] == 0:
        self.entries[0] += 1
      if self.entries[1] == 0:
        self.entries[1] += 1
      self.entries[2] += 1
      new_text = "{}.{}.{} {}".format(str(self.entries[0]), str(self.entries[1]), str(self.entries[2]), text)
      super(IndexedParagraph, self).__init__(new_text, style, **kwargs)

"""
# Old style, this is not compatible now
class ListItem(TextileFlowable):
  def __init__(self, listitem):
    self.listitem = listitem
    return
  
  def _print(self):
    def str_item(item, none_value=""):
      if isinstance(item, TextileFlowable):
        return item._print()
      if item is None:
        return none_value
      if isinstance(item, basestring):
        return item
      if isinstance(item, int):
        return "%d" % item
      if isinstance(item, float):
        return "%.2f" % item
      if isinstance(item, (list, tuple, set)):
        if len(item) == 0:
          return none_value
        return "; ".join(str_item(subitem) for subitem in item)  # recursion
      return str(item)
    return str_item(self.listitem)

  ListFlowable old print function
  def _print(self):
    item_strs = []
    for item in self.items:
      if isinstance(item, (tuple, list, set)):
        item_strs.append(ListFlowable(item, init_level=self.level, symbol=self.symbol)._print())
      if not isinstance(item, TextileFlowable):
        item = ListItem(item)
      item_strs.append("%s %s" % (self.bullet*self.level, item._print()))
    return "\n".join(item_strs)+'\n'

"""

class List(TextileFlowable):
  def __init__(self, texts, style='', init_level=0, **kwargs):
    # list.__init__(self, texts)
    self.texts = texts
    self.level = init_level
    self.symbol = kwargs.pop('symbol', 'bullet')
    if self.symbol == 'bullet':
      self.bullet = "*"
    elif self.symbol == 'number':
      self.bullet = "#"
    else:
      self.bullet = 'n/a'
    return
  
  def _print(self):
    return self._build_list_from_tuple(self.texts)

  def _build_list_from_tuple(self, texts, level=0):
    result = ''
    for text in texts:
      if isinstance(text, (tuple, set, list)):
        result += "{}".format(self._build_list_from_tuple(text, level + 1))
      elif isinstance(text, TextileFlowable):
        result += "{} {}".format(self.bullet * (level+1), text)
      else:
        result += "{} {}".format(self.bullet * (level+1), text + '\n')
    return result


class Table(TextileFlowable):
  def __init__(self, data, style=None, **kwargs):
    # **kwargs store table alignment and cell size data
    self.data = data
    self.style = style
    return
  
  def _print(self):
    self._apply_styling()
    table = ''
    for row in self.data:
      rowstring = '|'
      for cell in row:
        if cell is not None:
          rowstring += cell+'|'
      table += rowstring+'\n'
    return table

  def _cell_2_str(self, cell, none_value='n/a'):
    if cell is None:
      return none_value
    if isinstance(cell, Paragraph):
      return cell.text
    if isinstance(cell, basestring):
      return cell
    if isinstance(cell, int):
      return "%d" % cell
    if isinstance(cell, float):
      return "%.2f" % cell
    if isinstance(cell, (list, tuple, set)):
      if len(cell) == 0:
        return none_value
      return "; ".join(self._cell_2_str(subcell) for subcell in cell)  # recursion
    return str(cell)

  def _get_base_indices(self, c):
    if not isinstance(c, (tuple, set)):
      raise TypeError("Indices must be an (int,int), not '{}'".format(type(c)))
    cell = list(c)
    cell[0] = len(self.data[0]) + c[0] if c[0] < 0 else c[0]
    cell[1] = len(self.data) + c[1] if c[1] < 0 else c[1]
    return cell

  def _get_text(self, text):
    m = re.search("[^.]*\.(.*)", text)
    if m is None:
      return ''
    return m.group(1) if m.group(1) is not None else ''

  def _get_header(self, text):
    m = re.search("([^.]*)\.(.*)", text)
    if m is None:
      return ''
    return m.group(1) if m.group(1) is not None else ''

  def _get_format(self, text):
    m = re.search("(\\[0-9]/[0-9])?([<>=^~]{0,2})\..*", text)
    if m is None:
      return ''
    return m.group(2) if m.group(2) is not None else ''

  def _get_span_format(self, text):
    m = re.search("(\\[0-9]/[0-9])?([<>=^~]{0,2})\..*", text)
    if m is None:
      return ''
    return m.group(1) if m.group(1) is not None else ''

  def _apply_styling(self):
    # Collect data cell_2_str is required for backward compatibility
    self.data = [['.' + self._cell_2_str(cell) for cell in row] for row in self.data]
    if self.style is None:
      return

    for s in self.style:
      if isinstance(s, collections.Iterable) and not isinstance(s, basestring):
        if s[0] == 'SPAN' and len(s) == 3:
          luc = self._get_base_indices(s[1])
          rbc = self._get_base_indices(s[2])
          # init span
          span_header = r"\{}/{}{}.".format(rbc[0]-luc[0]+1, rbc[1]-luc[1]+1, self._get_format(self.data[luc[1]][luc[0]]))
          text = ""
          for i in range(luc[0], rbc[0] + 1):  # column indices
            for j in range(luc[1], rbc[1] + 1):  # row indices
              text += self._get_text(self.data[j][i])  # collect data from span cells
              self.data[j][i] = None
          self.data[luc[1]][luc[0]] = span_header+text

        elif s[0] == 'ALIGN' and len(s) == 4:
          luc = self._get_base_indices(s[1])
          rbc = self._get_base_indices(s[2])
          d = {'LEFT': '<', 'CENTER': '=', 'RIGHT': '>'}
          align = d[s[3]]

          for i in range(luc[0], rbc[0] + 1):  # column indices
            for j in range(luc[1], rbc[1] + 1):  # row indices
              f = self._get_format(self.data[j][i])
              for _, a in d.iteritems():
                if a == align:
                  f += align  # add new direction
                else:
                  f.replace(a, '')  # remove previous
              self.data[j][i] = '{}{}.{}'.format(self._get_span_format(self.data[j][i]), f,
                                                 self._get_text(self.data[j][i]))

        elif s[0] == 'VALIGN' and len(s) == 4:
          luc = self._get_base_indices(s[1])
          rbc = self._get_base_indices(s[2])
          d = {'TOP': '^', 'MIDDLE': '', 'BOTTOM': '~'}
          align = d[s[3]]

          for i in range(luc[0], rbc[0] + 1):  # column indices
            for j in range(luc[1], rbc[1] + 1):  # row indices
              f = self._get_format(self.data[j][i])
              for _, a in d.iteritems():
                if a == align:
                  f += align  # add new direction
                else:
                  f.replace(a, '')  # remove previous
              self.data[j][i] = '{}{}.{}'.format(self._get_span_format(self.data[j][i]), f,
                                                 self._get_text(self.data[j][i]))

        elif s[0] == 'TEXT_STYLE' and len(s) == 4:
          if not isinstance(s[3], collections.Iterable) or isinstance(s, basestring):
            raise TypeError("Styles must be an instance of Iterable even for only one, not {}".format(type(s[1])))
          luc = self._get_base_indices(s[1])
          rbc = self._get_base_indices(s[2])

          for i in range(luc[0], rbc[0] + 1):  # column indices
            for j in range(luc[1], rbc[1] + 1):  # row indices
              self.data[j][i] = '{}.{}'.format(self._get_header(self.data[j][i]),
                                               decorate(self._get_text(self.data[j][i]), **s[3]))


class NonEmptyTable(Table):
  EMPTY_MSG = "No items to display."
  
  def _print(self):
    if len(self.data) > 0:
      return Table._print(self)
    return self.EMPTY_MSG


class NonEmptyTableWithHeader(NonEmptyTable):
  # header-only still counts as empty table
  # TODO: handle tables with and without header in a cleaner way
  def _print(self):
    if len(self.data) > 1:
      return Table._print(self)
    return self.EMPTY_MSG


class Image(TextileFlowable):
  def __init__(self, path, *args, **kwargs):
    self.path = path
    return
  
  def _print(self):
    return "!%s!\n" % self.path


def _replace_special_characters(text):
  """
    Added this functions because input like _((text))_ will be interpreted as a command,
      thus brackets must be changed with html escape characters!
  """
  d = {'(': '&#40;', ')': '&#41;'}
  for ch_old, ch_new in d.iteritems():
    text = text.replace(ch_old, ch_new)
  return text


def bold(text):
  text = _replace_special_characters(text)
  text = '*{}*'.format(text.replace('*', ''))
  return text


def underline(text):
  text = _replace_special_characters(text)
  text = '+{}+'.format(text.replace('+', ''))
  return text


def italic(text):
  text = _replace_special_characters(text)
  text = '_{}_'.format(text.replace('_', ''))
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
  return text
