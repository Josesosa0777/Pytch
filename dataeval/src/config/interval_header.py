import cStringIO

class cIntervalHeader(list):
  NAMES = '--$'
  _lo_names = len(NAMES)
  CUSTOM_QUERY = '--!'
  _lo_custom_query = len(CUSTOM_QUERY)
  COMMENT = '--'

  @classmethod
  def fromFile(cls, HeaderFile):
    "Create interval header from text file with the following syntax\n"\
    "\n"\
    "`--'header column name, another column name, `_', yet\n"\
    "SELECT/LABEL and rest of the query\n\n"\
    "where `_' means dropped value from the query\n"\
    "and `@' shows the id of a static query (without `?')"

    Header = []
    Names = ()
    for Line in HeaderFile:
      Line = Line.strip()
      if not Line:
        continue
      elif Line.startswith(cls.NAMES):
        Names = cls.splitNames(Line, cls._lo_names)
        break

    Query = []
    for Line in HeaderFile:
      Line = Line.strip()
      if not Line:
        continue
      elif Line.startswith(cls.NAMES):
        Header.append( (Names, '\n'.join(Query)) )
        Names = cls.splitNames(Line, cls._lo_names)
        Query = []
      elif Line.startswith(cls.CUSTOM_QUERY):
        Query.append( Line[cls._lo_custom_query:].strip() )
      elif Line.startswith(cls.COMMENT):
        continue
      else:
        Query.append(Line)
    if Names and Query:
      Header.append( (Names, '\n'.join(Query)) )

    self = cls(Header)
    return self

  @classmethod
  def fromFileName(cls, HeaderFileName):
    with open(HeaderFileName, 'r') as HeaderFile:
      self = cls.fromFile(HeaderFile)
    return self

  @classmethod
  def fromString(cls, Query):
    # TODO: solve in a cleaner way (without StringIO) after cleaning up fromFile()
    QueryFile = cStringIO.StringIO()
    QueryFile.write(Query); QueryFile.flush()
    QueryFile.seek(0)
    self = cls.fromFile(QueryFile)
    QueryFile.close()
    return self

  @classmethod
  def splitNames(cls, Line, From=0):
    Names = tuple(Name.strip() for Name in Line[From:].split(','))
    return Names

  @classmethod
  def _stripCustomQuery(cls, Line):
    return