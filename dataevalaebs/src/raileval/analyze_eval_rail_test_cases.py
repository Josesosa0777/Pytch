# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import os
from collections import OrderedDict
from xlwt import Workbook, Style
import numpy

from interface import iAnalyze
from tceval.rail_tc_eval import FAULT_POS_4_COMMENT,\
  FAULT_TYPE_4_COMMENT, CAN_MSG_ID_4_COMMENT, CAN_SGN_CHG_TYPE_4_COMMENT,\
  CAN_SGN_ID_4_COMMENT
from tceval.test_data_and_results_handlers import TestCaseResultsDocMaker


class Analyze(iAnalyze):
  plot_modules = OrderedDict([
    ('view_aebs_c_ccp_inputs-show_rail_maneuver@raileval',
     ('AEBS_C inputs', dict(windowgeom='785x1500+0+0'))),
    ('view_aebs_c_ccp_outputs-show_rail_maneuver@raileval',
     ('AEBS_C outputs', dict(windowgeom='785x1500+0+0')))])

  def _create_plots(self, plots_dict):
    for meas_fname, plt_data in plots_dict.iteritems():
      manager = self.clone_manager()
      manager.set_measurement(meas_fname)
      manager.build(self.plot_modules, show_navigators=False)
      sync = manager.get_sync()
      for (start, end), in_fname, out_fname in plt_data:
        sync.set_xlim_online(start-1.0, end+3.0)
        for plot_module, (plot_winID, props) in self.plot_modules.iteritems():
          client = sync.getClient(plot_module, plot_winID)
          client.setWindowGeometry(props['windowgeom'])
          if 'input' in plot_module:
            client.copyContentToFile(in_fname)
          elif 'output' in plot_module:
            client.copyContentToFile(out_fname)
          # close plot to prevent matplotlib's memory allocation error
          client.closePlot()
      manager.close()
    return
  
  def _make_rep_dir(self, tc_id):
    batch_db_dir = os.path.split(self.batch.dbname)[0]
    rep_dir = os.path.join(batch_db_dir, "Reports")
    if not os.path.exists(rep_dir):
      os.mkdir(rep_dir)
    rep_dir = os.path.join(rep_dir, "%s" % tc_id)
    if not os.path.exists(rep_dir):
      os.mkdir(rep_dir)
    return rep_dir
  
  def _init_xls_ws(self, xls_ws, row_titles, col_titles, xls_style=None):
    if xls_style is None:
      xls_style = Style.XFStyle()
      xls_style.borders.left = xls_style.borders.THIN
      xls_style.borders.right = xls_style.borders.THIN
      xls_style.borders.top = xls_style.borders.THIN
      xls_style.borders.bottom = xls_style.borders.THIN
    cells = [[""] + col_titles]
    for row_title in row_titles:
      row = [row_title] + (["n/a"] * len(col_titles))
      cells.append(row)
    for r_idx, row in enumerate(cells):
      for c_idx, cell in enumerate(row):
        xls_ws.write(r_idx, c_idx, cell, xls_style)
    return xls_style
  
  def _get_regression_test_results(self):
    querystr = """
      SELECT intrepdata.measloc,
             intrepdata.reptitle,
             intrepdata.starttime,
             intrepdata.endtime,
             intrepdata.intresult,
             intrepdata.intcomment
      FROM (
        SELECT me.local measloc,
               en.title reptitle,
               ei.start_time starttime,
               ei.end_time endtime,
               la.name intresult,
               IFNULL(ic.comment, '') intcomment
        FROM entryintervals ei
        JOIN entries en ON en.id = ei.entryid
        JOIN measurements me ON me.id = en.measurementid
        JOIN modules mo ON mo.id = en.moduleid
        JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
        JOIN labels la ON la.id = i2l.labelid
        LEFT JOIN intervalcomments ic ON ic.entry_intervalid = i2l.entry_intervalid
        WHERE mo.class = "raileval.search_eval_rail_test_cases.Search"
      ) intrepdata
      WHERE intrepdata.reptitle NOT GLOB '*893451*'
        AND intrepdata.reptitle NOT GLOB '*951017*'
        AND intrepdata.reptitle NOT GLOB '*893448*'
      ORDER BY intrepdata.measloc
    """
    regr_test_results = self.batch.query(querystr, fetchone=True)

    if not regr_test_results:  # no results
      return {}

    rep_title = regr_test_results[1]
    sessionid = rep_title.split(' (TS ')[-1][:-1]
    
    regr_test_results = self.batch.query(querystr)
    
    test_results = {}
    plots_dict = OrderedDict()
    for meas_fname, tc, start, end, res, comment in regr_test_results:
      test_case_id = tc.split('TC ')[-1]
      test_case_id = test_case_id.split(' (TS ')[0]
      image_folder = self._make_rep_dir(test_case_id)
      test_case = test_results.setdefault(test_case_id, {})
      test_case.setdefault('sessionid', sessionid)
      test_case.setdefault('annotation', " ".join([comment, meas_fname]) if comment else meas_fname)
      verdict = test_case.setdefault('verdict', [])
      if res == 'passed':
        verdict.append(True)
      elif res == 'inconclusive':
        verdict.append(None)
      else:
        verdict.append(False)
      attachment = test_case.setdefault('attachment', [])
      if test_case_id != '0' and res != 'inconclusive':
        image_loc_in = os.path.join(image_folder, "in-%02f.png" % start)
        image_loc_out = os.path.join(image_folder, "out-%02f.png" % start)
        meas_plot = plots_dict.setdefault(meas_fname, [])
        seek_img = ((start, end), image_loc_in, image_loc_out)
        meas_plot.append(seek_img)
        images_loc = [image_loc_in, image_loc_out]
        attachment.extend(images_loc)
    self._create_plots(plots_dict)
    for test_case_id, test_result in test_results.iteritems():
      test_results[test_case_id]['attachment'] = list(set(test_result['attachment']))
      test_results[test_case_id]['attachment'].sort()
      if None in test_result['verdict']:
        test_results[test_case_id]['verdict'] = 'skipped'
      elif numpy.all(test_result['verdict']):
        test_results[test_case_id]['verdict'] = 'passed'
      else:
        test_results[test_case_id]['verdict'] = 'failed'
    return test_results
  
  def _get_func_errhan_test_results(self, tc_id):
    # tc_id should only take one of these values: 893451, 951017
    querystr = """
      SELECT intrepdata.measloc,
             intrepdata.reptitle,
             intrepdata.starttime,
             intrepdata.endtime,
             intrepdata.intresult,
             intrepdata.intcomment
      FROM (
        SELECT me.local measloc,
               en.title reptitle,
               ei.start_time starttime,
               ei.end_time endtime,
               la.name intresult,
               IFNULL(ic.comment, '') intcomment
        FROM entryintervals ei
        JOIN entries en ON en.id = ei.entryid
        JOIN measurements me ON me.id = en.measurementid
        JOIN modules mo ON mo.id = en.moduleid
        JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
        JOIN labels la ON la.id = i2l.labelid
        LEFT JOIN intervalcomments ic ON ic.entry_intervalid = i2l.entry_intervalid
        WHERE mo.class = "raileval.search_eval_rail_test_cases.Search"
      ) intrepdata
      WHERE intrepdata.reptitle GLOB '*%s*'
      ORDER BY intrepdata.measloc
    """
    querystr = querystr % tc_id
    func_errhan_test_results = self.batch.query(querystr, fetchone=True)
    if not func_errhan_test_results:
      return {}
    rep_title = func_errhan_test_results[1]
    sessionid = rep_title.split(' (TS ')[-1][:-1]
    
    func_errhan_test_results = self.batch.query(querystr)
    
    row_titles = FAULT_POS_4_COMMENT.values()
    col_titles = FAULT_TYPE_4_COMMENT.values()
    
    rep_dir = self._make_rep_dir(tc_id)
    xls_file = os.path.join(rep_dir, 'Evaluation_report_of_TC_%s_in_TS_%s.xls'
                            % (tc_id, sessionid))
    xls_wb = Workbook()
    xls_ws = xls_wb.add_sheet('TC_%s' % tc_id, cell_overwrite_ok=True)
    xls_style = self._init_xls_ws(xls_ws, row_titles, col_titles)
    
    test_results = {}
    test_case = test_results.setdefault(tc_id, {})
    # As the tests are split to separate measurements this set will collect
    # all the file names. Counter for checking completeness
    fnames = set()
    cases_count = 0
    for meas_fname, _, _, _, res, comment in func_errhan_test_results:
      fnames.add(meas_fname)
      test_case.setdefault('sessionid', sessionid)
      verdict = test_case.setdefault('verdict', [])
      if res == 'passed':
        verdict.append(True)
      elif res == 'inconclusive':
        verdict.append(None)
      else:
        verdict.append(False)
      attachment = test_case.setdefault('attachment', [])
      attachment.append(xls_file)
      col_idx, row_idx = comment.split(' | ')
      col_idx = col_titles.index(col_idx) + 1
      row_idx = row_titles.index(row_idx) + 1
      xls_ws.write(row_idx, col_idx, res, xls_style)
      cases_count += 1
    # Put collected file names into the annotation field
    test_case['annotation'] = '; '.join(fnames)
    xls_wb.save(xls_file)
    test_results[tc_id]['attachment'] = list(set(test_results[tc_id]['attachment']))
    test_results[tc_id]['attachment'].sort()
    if None in test_results[tc_id]['verdict']:
      test_results[tc_id]['verdict'] = 'skipped'
    elif numpy.all(test_results[tc_id]['verdict']):
      test_results[tc_id]['verdict'] = 'passed'
    else:
      test_results[tc_id]['verdict'] = 'failed'
    # Check if all test steps has been evaluated (16 for moving 20 for stationary)
    if ((tc_id == '893451' and cases_count == 16) or 
        (tc_id == '951017' and cases_count == 20)):
      pass
    else:
      test_results[tc_id]['verdict'] = 'failed'
      test_results[tc_id]['annotation'] = 'Not enough test steps, missing measurements?'      
    return test_results
  
  def _get_interface_errhan_test_results(self, tc_id='893448'):
    querystr = """
      SELECT intrepdata.measloc,
             intrepdata.reptitle,
             intrepdata.starttime,
             intrepdata.endtime,
             intrepdata.intresult,
             intrepdata.intcomment
      FROM (
        SELECT me.local measloc,
               en.title reptitle,
               ei.start_time starttime,
               ei.end_time endtime,
               la.name intresult,
               IFNULL(ic.comment, '') intcomment
        FROM entryintervals ei
        JOIN entries en ON en.id = ei.entryid
        JOIN measurements me ON me.id = en.measurementid
        JOIN modules mo ON mo.id = en.moduleid
        JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
        JOIN labels la ON la.id = i2l.labelid
        LEFT JOIN intervalcomments ic ON ic.entry_intervalid = i2l.entry_intervalid
        WHERE mo.class = "raileval.search_eval_rail_test_cases.Search"
      ) intrepdata
      WHERE intrepdata.reptitle GLOB '*%s*'
      ORDER BY intrepdata.measloc
    """
    querystr = querystr % tc_id
    interf_errhan_test_results = self.batch.query(querystr, fetchone=True)
    if not interf_errhan_test_results:
      return {}
    rep_title = interf_errhan_test_results[1]
    sessionid = rep_title.split(' (TS ')[-1][:-1]
    
    interf_errhan_test_results = self.batch.query(querystr)
    
    to_row_titles = CAN_MSG_ID_4_COMMENT.values()
    chg_row_titles = CAN_SGN_ID_4_COMMENT.values()
    chg_col_titles = CAN_SGN_CHG_TYPE_4_COMMENT.values()
    
    rep_dir = self._make_rep_dir(tc_id)
    xls_file = os.path.join(rep_dir, 'Evaluation_report_of_TC_%s_in_TS_%s.xls'
                            % (tc_id, sessionid))
    xls_wb = Workbook()
    xls_ws_to = xls_wb.add_sheet('Timeout error results', cell_overwrite_ok=True)
    xls_ws_sgnerr = xls_wb.add_sheet('Signal error results', cell_overwrite_ok=True)
    xls_style = self._init_xls_ws(xls_ws_to, to_row_titles, ['Timeout'])
    xls_style = self._init_xls_ws(xls_ws_sgnerr, chg_row_titles, chg_col_titles,
                      xls_style=xls_style)
    
    test_results = {}
    test_case = test_results.setdefault(tc_id, {})
    for meas_fname, _, _, _, res, comment in interf_errhan_test_results:
      test_case.setdefault('sessionid', sessionid)
      test_case.setdefault('annotation', meas_fname)
      verdict = test_case.setdefault('verdict', [])
      if res == 'passed':
        verdict.append(True)
      elif res == 'inconclusive':
        verdict.append(None)
      else:
        verdict.append(False)
      attachment = test_case.setdefault('attachment', [])
      attachment.append(xls_file)
      if 'Timeout' in comment:
        row_idx = comment.split(' | ')[-1]
        row_idx = to_row_titles.index(row_idx) + 1
        xls_ws_to.write(row_idx, 1, res, xls_style)
      else:
        col_idx, row_idx = comment.split(' | ')
        col_idx = chg_col_titles.index(col_idx) + 1
        row_idx = chg_row_titles.index(row_idx) + 1
        xls_ws_sgnerr.write(row_idx, col_idx, res, xls_style)
    xls_wb.save(xls_file)
    test_results[tc_id]['attachment'] = list(set(test_results[tc_id]['attachment']))
    test_results[tc_id]['attachment'].sort()
    if numpy.all(test_results[tc_id]['verdict']):
      test_results[tc_id]['verdict'] = 'passed'
    else:
      test_results[tc_id]['verdict'] = 'failed'
    return test_results
  
  def analyze(self):
    results_dict = self._get_regression_test_results()
    results_dict.update(self._get_interface_errhan_test_results())
    results_dict.update(self._get_func_errhan_test_results('893451'))
    results_dict.update(self._get_func_errhan_test_results('951017'))
    tc_results_doc = TestCaseResultsDocMaker()
    tc_results_doc.fill_up_test_res_doc_with_dict(results_dict)
    xml_file_loc = os.path.split(self.batch.dbname)[0]
    xml_file_loc = os.path.join(xml_file_loc, "TestCaseResults.xml")
    tc_results_doc.save_res_doc_file(xml_file_loc)
    return