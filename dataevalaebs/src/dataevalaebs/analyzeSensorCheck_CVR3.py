#!/usr/bin/python

import os

import measproc
import interface

DefParam = interface.NullParam

def calcSensorCheckTable(workspaceGroup, excludeData=[]):
  quantity2Exclude = ['__version__', '__header__', '__globals__'] + excludeData
  values = []
  titleRow = []
  titleCol = []
  invalidIndices = []
  i = 0
  for entry in workspaceGroup:
    measName = interface.Batch.get_entry_attr(entry, "measurement")
    titleCol.append(measName)
    workspace = interface.Batch.wake_entry(entry)
    workspace = workspace.workspace
    row = []
    j = 0
    for quantity, data in workspace.iteritems():
      if quantity in quantity2Exclude:
        continue
      if i == 0:
        titleRow.append(quantity)
      value = data.item(0)
      row.append(value)
      isValid = data.item(1)
      if not isValid:
        invalidIndices.append((i, j))
      j += 1  # enumerate() cannot be used in "for" because of the ignored quantities
    values.append(row)
    i += 1
  table = measproc.Table(values, titleRow, titleCol, "", invalidIndices)
  return table

class cAnalyze(interface.iAnalyze):
  repTitle = 'SensorCheckWS-CVR3'
  
  def check(self):
    workspaceGroup = interface.Batch.filter(type='measproc.FileWorkSpace', title=self.repTitle)
    return workspaceGroup
  
  def fill(self, workspaceGroup):
    table = calcSensorCheckTable(workspaceGroup)
    return table
  
  def analyze(self, param, table):
    # sort table
    table = table.getSortedByRows().getSortedByColumns()
    # print measurements and replace them in the table with their indices
    for i, meas in enumerate(table.titleCol):
      print "%d. %s" % (i+1, meas)
      table.titleCol[i] = str(i+1)
    print
    
    # slice table
    smallTables = table.getChunks(nMaxRows=10)
    # pretty print the pieces
    for smallTable in smallTables:
      smallTable = smallTable.getTransposed()
      smallTable.pprint(invalidTemplate="%s !!")
      print
    return
