import sys

STRINGREPR = {
  "int":           "%d",
  "numpy.int8":    "%d",
  "numpy.int16":   "%d",
  "numpy.int32":   "%d",
  "numpy.int64":   "%d",
  "float":         "%.2f",
  "numpy.float16": "%.2f",
  "numpy.float32": "%.2f",
  "numpy.float64": "%.2f",
  "numpy.float96": "%.2f",
}

def convert4cell(data, conversionMap=STRINGREPR):
  dataTypeStr = str(type(data))
  key = dataTypeStr[7:-2]  # <type '%s'>
  try:
    cellValue = conversionMap[key] % data
  except KeyError:
    cellValue = data
  return cellValue

class Table:
  """General class for 2-D tables.
  
  cornerCell || t | i | t | l | e | R | o | w 
  ===========||===|===|===|===|===|===|===|===
       t     || . | . | . | . | . | . | . | .
       i     || . | . | . | . | . | . | . | .
       t     || . | . | . | . | . | . | . | .
       l     || . | . | d | a | t | a | . | .
       e     || . | . | . | . | . | . | . | .
       C     || . | . | . | . | . | . | . | .
       o     || . | . | . | . | . | . | . | .
       l     || . | . | . | . | . | . | . | .
  """
  def __init__(self, data, titleRow=[], titleCol=[], cornerCell="", invalidIndices=[]):
    # check consistency
    nRows = len(data)
    nCols = len(data[0]) if nRows > 0 else 0
    assert all([len(row) == nCols for row in data]), "Different column numbers"
    if titleRow and nCols > 0:
      assert len(titleRow) == nCols, "Invalid length for titleRow"
    if titleCol and nRows > 0:
      assert len(titleCol) == nRows, "Invalid length for titleCol"
    if invalidIndices:
      assert all([i < nRows and j < nCols for i, j in invalidIndices]), "invalidIndex out of range"
    # copy values
    self.data = list(data)
    self.titleRow = list(titleRow)  # header
    self.titleCol = list(titleCol)
    self.cornerCell = cornerCell    # cell (0,0)
    self.invalidIndices = list(invalidIndices)  # list of indices to be marked as invalid (optional)
    return
  
  def getItem(self, row, col):
    """Get item from the given position."""
    if type(row) is str and type(col) is str and self.titleRow and self.titleCol:
      row = self.titleCol.index(row)
      col = self.titleRow.index(col)
    return self.data[row][col]
  
  def setItem(self, row, col, value):
    """Set item in the given position."""
    if type(row) is str and type(col) is str and self.titleRow and self.titleCol:
      row = self.titleCol.index(row)
      col = self.titleRow.index(col)
    self.data[row][col] = value
    return
  
  def getSortedByRows(self):
    """Return a Table instance where the rows are sorted by the title column."""
    if not self.titleCol:
      return self
    try:
      titleColSorted = sorted(self.titleCol, key=float)  # for proper sorting in case of numbers
    except ValueError:
      titleColSorted = sorted(self.titleCol)
    orderedIndices = [self.titleCol.index(title) for title in titleColSorted]
    data = [self.data[i] for i in orderedIndices]
    invalidIndices = [(orderedIndices.index(i), j) for i, j in self.invalidIndices]
    return Table(data, self.titleRow, titleColSorted, self.cornerCell, invalidIndices)
  
  def getSortedByColumns(self):
    """Return a Table instance where the columns are sorted by the title row."""
    if not self.titleRow:
      return self
    return self.getTransposed().getSortedByRows().getTransposed()
  
  def getPrintable(self, conversionMap=STRINGREPR, invalidTemplate=""):
    """Return the table as a list of lists, where the title row and column are added to the top and left."""
    printable = [[convert4cell(value, conversionMap) for value in row] for row in self.data]
    if invalidTemplate:
      for i, j in self.invalidIndices:
        try:
          printable[i][j] = invalidTemplate % printable[i][j]
        except TypeError:
          printable[i][j] = invalidTemplate
    for row, title in zip(printable, self.titleCol):
      row.insert(0, title)
    if self.titleRow:
      titleRow = list(self.titleRow)
      if self.titleCol:
        titleRow.insert(0, self.cornerCell)
      printable.insert(0, titleRow)
    return printable
  
  def pprint(self, conversionMap=STRINGREPR, invalidTemplate="", output=sys.stdout):
    """Pretty printer."""
    table = self.getPrintable(conversionMap, invalidTemplate)
    colPaddings = []
    for iCol in xrange(len(table[0])):
      padding = max([len(row[iCol]) for row in table])
      colPaddings.append(padding)
    for row in table:
      # left col
      print >> output, row[0].ljust(colPaddings[0] + 1),
      # rest of the cols
      for i in xrange(1, len(row)):
        col = row[i].rjust(colPaddings[i] + 2)
        print >> output, col,
      print >> output
    return
  
  def getTransposed(self):
    """Return the transposed as a Table instance."""
    newData = zip(*self.data)
    newTitleRow = self.titleCol
    newTitleCol = self.titleRow
    newInvalidIndices = [(j, i) for (i, j) in self.invalidIndices]
    return Table(newData, newTitleRow, newTitleCol, self.cornerCell, newInvalidIndices)
  
  def getChunks(self, nMaxRows=10):
    """Return the chunks with maximum 'nMaxRows' rows as separate Table instances."""
    if len(self.data) <= nMaxRows:
      return [self]
    splitter = lambda data: [data[i:i+nMaxRows] for i in xrange(0, len(data), nMaxRows)]
    newDatas = splitter(self.data)
    nChunks = len(newDatas)
    newTitleCols = splitter(self.titleCol) if self.titleCol else [[]] * nChunks
    newTitleRows = [self.titleRow] * nChunks
    newInvalidIndices = []  # list of list of tuples
    for k in xrange(nChunks):
      invalidIndices = []
      firstRowIndex = k * nMaxRows
      for i, j in self.invalidIndices:
        if i >= firstRowIndex and i < firstRowIndex+nMaxRows:
          invalidIndices.append((i-firstRowIndex, j))
      newInvalidIndices.append(invalidIndices)
    return [Table(a, b, c, self.cornerCell, d) for (a, b, c, d) in zip(newDatas, newTitleRows, newTitleCols, newInvalidIndices)]
