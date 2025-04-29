#!/usr/bin/python

import sys

import numpy as np
import matplotlib.pyplot as plt

import measproc
import interface

figformat = 'png'

class cParameter(interface.iParameter):
  def __init__(self, title):
    self.title = title
    self.genKeys()
    pass

# instantiation of module parameters
par001      = cParameter(r'SELS changes in POSition matrix - par001')
par001vs002 = cParameter(r'SELS changes in POSition matrix - par001 vs par002')

class cAnalyze(interface.iAnalyze):
  def analyze(self, param):
    Batch = self.get_batch()
    Group = Batch.filter(type='measproc.cFileReport', title=param.title) 
    uniqueReportPaths = set()
    sumtime= 0.
    sumintervals = 0
    valids, misseds, invalids = 0., 0., 0.
    # collect data
    for EntryId in Group:
      report = Batch.wake_entry(EntryId)
      if report.PathToSave in uniqueReportPaths:
        continue
      else:
        uniqueReportPaths.add(report.PathToSave)
        repTime = report.IntervalList.Time
        sumtime += repTime[-1] - repTime[0]
        if Batch.get_entry_attr(EntryId, 'result') == 'passed':
          repAttrs = report.ReportAttrs
          sumintervals += repAttrs['Valids'] + repAttrs['Invalids'] + repAttrs['Misseds']
          for (lower, upper), attribs in report.IntervalAttrs.iteritems():
            if upper != repTime.size:
              dt = repTime[upper]-repTime[lower]
            else:
              dt = (upper-lower) * np.mean(np.diff(repTime))
            if attribs['Vote'] == 'valid':
              valids += dt
            elif attribs['Vote'] == 'missed':
              misseds += dt
            elif attribs['Vote'] == 'invalid':
              invalids += dt
            else:
              print 'Warning: %s unevaluated interval (%s)' %(report.PathToSave, (lower, upper))
    sum = valids + misseds + invalids
    # plotting
    # total time
    fig1 = plt.figure(figsize=(6,6))
    fig1.suptitle('%s\n(%.1fmin)' %(param.title, sumtime/60.))
    ax = plt.axes([0.1, 0.1, 0.8, 0.8])
    labels = 'changed', 'same'
    changed = sum/sumtime
    fracs = [changed, 1.-changed]
    ax.pie(fracs, labels=labels, autopct='%1.1f%%')
    # votes
    fig2 = plt.figure(figsize=(6,6))
    fig2.suptitle('%s\n(%d intervals, %.1fs)' %(param.title, sumintervals, sum))
    ax = plt.axes([0.1, 0.1, 0.8, 0.8])
    labels = 'valid', 'missed', 'invalid'
    colors = 'g', 'b', 'r'
    fracs = [valids/sum, misseds/sum, invalids/sum]
    explode=(0.05, 0.05, 0.05)
    ax.pie(fracs, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)
    # save figures
    figname1 = '%s (total).%s' %(param.title,figformat)
    figname2 = '%s (votes).%s' %(param.title,figformat)
    fig1.savefig(figname1, format=figformat)
    fig2.savefig(figname2, format=figformat)
    print >> sys.stderr, figname1
    print >> sys.stderr, figname2
    return

