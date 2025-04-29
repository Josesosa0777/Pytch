# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import os
from collections import OrderedDict
from xlwt import Workbook, Style
import numpy

from ..tceval.test_data_and_results_handlers import TestCaseResultsDocMaker

from ..analyze_eval_rail_test_cases import Analyze



class ACCAnalyze(Analyze):

    plot_modules = OrderedDict([
        ('view_aebs_c_ccp_inputs-show_rail_maneuver@raileval',
         ('AEBS_C inputs', dict(windowgeom='785x1500+0+0'))),
        ('view_rail_acc_output_test-def_param@raileval.acc_eval',
         ('ACC outputs', dict(windowgeom='785x1500+0+0')))])

    def _get_ACC_test_results(self):
        querystr = """
        SELECT intrepdata.measloc,
               intrepdata.reptitle,
               intrepdata.starttime,
               intrepdata.endtime,
               intrepdata.intresult
        FROM (
          SELECT me.local measloc,
                 en.title reptitle,
                 ei.start_time starttime,
                 ei.end_time endtime,
                 la.name intresult
          FROM entryintervals ei
          JOIN entries en ON en.id = ei.entryid
          JOIN measurements me ON me.id = en.measurementid
          JOIN modules mo ON mo.id = en.moduleid
          JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
          JOIN labels la ON la.id = i2l.labelid
          WHERE mo.class = "raileval.acc_eval.search_acc_rail_test_cases.Search"
        ) intrepdata        
        ORDER BY intrepdata.measloc
      """
        regr_test_results = self.batch.query(querystr, fetchone=True)
        rep_title = regr_test_results[1]
        sessionid = rep_title.split(' (TS ')[-1][:-1]

        regr_test_results = self.batch.query(querystr)

        test_results = {}
        plots_dict = OrderedDict()
        for meas_fname, tc, start, end, res in regr_test_results:
            test_case_id = tc.split('TC ')[-1]
            test_case_id = test_case_id.split(' (TS ')[0]
            image_folder = self._make_rep_dir(test_case_id)
            test_case = test_results.setdefault(test_case_id, {})
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
            if test_case_id != '0' and res != 'inconclusive':
                image_loc_in = os.path.join(image_folder, "in-%02f.png" % start)
                image_loc_out = os.path.join(image_folder, "acc_out-%02f.png" % start)
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

    def analyze(self):
        results_dict = self._get_ACC_test_results()

        tc_results_doc = TestCaseResultsDocMaker()
        tc_results_doc.fill_up_test_res_doc_with_dict(results_dict)
        xml_file_loc = os.path.split(self.batch.dbname)[0]
        xml_file_loc = os.path.join(xml_file_loc, "TestCaseResultsACC.xml")
        tc_results_doc.save_res_doc_file(xml_file_loc)
        return