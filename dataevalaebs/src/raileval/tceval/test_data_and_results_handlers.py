from xml.dom import minidom
import os

class TestError(Exception):
  def __init__(self, value):
    self.value = value
    return
  
  def __str__(self):
    return repr(self.value)


class MKSExportParser(object):
  def __init__(self, xml_file_loc):
    self.xmldoc = minidom.parse(xml_file_loc)
    return
  
  def _get_test_cases(self):
    test_cases = []
    issue_list = self.xmldoc.getElementsByTagName('Issue')
    for issue in issue_list:
      if issue.getAttribute('type') == 'RQ4_Test Case':
        for parameter in issue.childNodes:
          if (parameter.nodeName == 'Parameter'
              and (parameter.getAttribute('value') == 'Test Case'
                   and parameter.getAttribute('name') == 'RQ_Category')):
            test_cases.append(issue)
    return test_cases
  
  def _get_session_suite_id_pairs(self):
    session_suite_id_pairs = {}
    issue_list = self.xmldoc.getElementsByTagName('Issue')
    for issue in issue_list:
      if issue.getAttribute('type') == 'RQ4_Test Session':
        suite_ids = session_suite_id_pairs.setdefault(issue.getAttribute('IssueID'), [])
        for parameter in issue.childNodes:
          if (parameter.nodeName == 'Parameter'
              and parameter.getAttribute('name') == 'Tests'):
            for test_suites in parameter.childNodes:
              if test_suites.nodeName == 'Parameter':
                for test_suite in test_suites.childNodes:
                  if (test_suite.nodeName == 'Parameter'
                      and test_suite.getAttribute('name') == 'ID'):
                    suite_ids.append(test_suite.getAttribute('value'))
    return session_suite_id_pairs
  
  def get_test_cases(self):
    return self._get_test_cases()
  
  def get_test_session_test_case_id_pairs(self):
    test_session_data = {}
    session_suite_id_pairs = self._get_session_suite_id_pairs()
    test_case_list = self._get_test_cases()
    
    for test_session_id, test_suite_ids in session_suite_id_pairs.iteritems():
      test_cases = test_session_data.setdefault(test_session_id, [])
      for test_suite_id in test_suite_ids:
        for test_case in test_case_list:
          for parameter in test_case.childNodes:
            if (parameter.nodeName == 'Parameter'
                and (parameter.getAttribute('name') == 'RQ_Contained By'
                     and test_suite_id in parameter.getAttribute('value'))):
              test_cases.append(test_case.getAttribute('IssueID'))
    return test_session_data
  
  def get_test_case_data(self):
    test_case_list = self._get_test_cases()
    test_case_data = {}
    for test_case in test_case_list:
      test_data = test_case_data.setdefault(test_case.getAttribute('IssueID'), {})
      for parameter in test_case.childNodes:
        if (parameter.nodeName == 'Parameter'
            and parameter.getAttribute('name') == 'Summary'):
          test_case_name = parameter.getAttribute('value')
          test_case_name = test_case_name.split(' - ')[0]
          test_data.setdefault('test_name', test_case_name)
          scr_n_cfg = test_data.setdefault('scr_n_cfg', [])
        if (parameter.nodeName == 'Parameter'
            and parameter.getAttribute('name') == 'TestScripts'):
          for test_scripts_param in parameter.childNodes:
            if test_scripts_param.nodeName == 'Parameter':
              for test_scr_param in test_scripts_param.childNodes:
                if (test_scr_param.nodeName == 'Parameter'
                    and test_scr_param.getAttribute('name') == 'Member'):
                  scr_n_cfg.append(test_scr_param.getAttribute('value'))
    return test_case_data
  
  def _get_radar_SW_version(self):
    TS_sum1 = self._get_Test_Session_summary()
    radar_SW_version = []
    issue_list = self.xmldoc.getElementsByTagName('Issue')
    for issue in issue_list:
      for parameter in issue.childNodes:
        if (parameter.nodeName == 'Parameter' and parameter.getAttribute('name') == 'RQ4_SW Version AuC'):
          if (len(parameter.getAttribute('value')) > 3): # reading SW version from 'SW version' if value has appropriate length
            radar_SW_version.append(parameter.getAttribute('value'))
          else:
            start = TS_sum1[0].find('release') + 8
            if ('KB' in TS_sum1[0]): #reading SW version from Test Session summary
              is_num_start = TS_sum1[0].find('KB') + 2
              is_num_end = TS_sum1[0].find('KB') + 8
              is_num = TS_sum1[0][is_num_start:is_num_end]
              if is_num.isdigit():
                end = TS_sum1[0].find('KB') + 8
              else:
                end = start # in order to get 'No SW version is set'
            elif ('BX' in TS_sum1[0]): #reading SW version from Test Session summary
              is_num_start = TS_sum1[0].find('BX') + 2
              is_num_end = TS_sum1[0].find('BX') + 8
              is_num = TS_sum1[0][is_num_start:is_num_end]
              if is_num.isdigit():
                end = TS_sum1[0].find('BX') + 8
              else:
                end = start # in order to get 'No SW version is set'
            else:
              end = start # in order to get 'No SW version is set'
            if (len(TS_sum1[0][start:end]) > 0):
              radar_SW_version.append(TS_sum1[0][start:end])
            else:
              radar_SW_version.append('No SW version is set')
              
        if (parameter.nodeName == 'Parameter' and parameter.getAttribute('name') == 'RQ4_SW Version BuC'):
          if (len(parameter.getAttribute('value')) > 3):#reading SW version from 'SW version' if value has appropriate length
            radar_SW_version.append(parameter.getAttribute('value'))
          else:
            start = TS_sum1[0].find('release') + 8
            if ('KB' in TS_sum1[0]): #reading SW version from Test Session summary
              is_num_start = TS_sum1[0].find('KB') + 2
              is_num_end = TS_sum1[0].find('KB') + 8
              is_num = TS_sum1[0][is_num_start:is_num_end]
              if is_num.isdigit():
                end = TS_sum1[0].find('KB') + 8
              else:
                end = start # in order to get 'No SW version is set'
            elif ('BX' in TS_sum1[0]): #reading SW version from Test Session summary
              is_num_start = TS_sum1[0].find('BX') + 2
              is_num_end = TS_sum1[0].find('BX') + 8
              is_num = TS_sum1[0][is_num_start:is_num_end]
              if is_num.isdigit():
                end = TS_sum1[0].find('BX') + 8
              else:
                end = start # in order to get 'No SW version is set'
            else:
              end = start # in order to get 'No SW version is set'
            if (len(TS_sum1[0][start:end]) > 0):
              radar_SW_version.append(TS_sum1[0][start:end])
            else:
              radar_SW_version.append('No SW version is set!')
    return radar_SW_version
  
  def get_radar_SW_version(self):
    return self._get_radar_SW_version()
  
  def _get_Test_Session_summary(self):
    TS_summary = []
    issue_list = self.xmldoc.getElementsByTagName('Issue')
    for issue in issue_list:
      if (issue.nodeName == 'Issue' and issue.getAttribute('type') == 'RQ4_Test Session'):
        for parameter in issue.childNodes:
          if (parameter.nodeName == 'Parameter' and parameter.getAttribute('name') == 'Summary'):
            if (len(parameter.getAttribute('value')) > 3): #if Summary has appropriate length
              TS_summary.append(parameter.getAttribute('value'))
            else:
              TS_summary.append('No Test Session Summary is set!')
    return TS_summary
  
  def get_Test_Session_summary(self):
    return self._get_Test_Session_summary()

class TestCaseResultsDocMaker(object):
  def __init__(self):
    self.dom_doc = minidom.Document()
    self._doc_root = self.dom_doc.createElement('MAIN')
    self.dom_doc.appendChild(self._doc_root)
    self.test_case_res_elem = None
    return
  
  def _create_test_res_node(self, test_case_id):
    self.test_case_res_elem = self.dom_doc.createElement('MKSTestResult')
    self.test_case_res_elem.setAttribute('TestCaseID', test_case_id)
    self._doc_root.appendChild(self.test_case_res_elem)
    return
  
  def _create_param_elem(self, param_name, param_value):
    param_elem = self.dom_doc.createElement('Parameter')
    param_elem.setAttribute('name', param_name)
    param_elem.appendChild(self.dom_doc.createTextNode(param_value))
    self.test_case_res_elem.appendChild(param_elem)
    return
  
  def fill_up_test_res_doc_with_dict(self, doc_input):
    """
    doc_input --> type: dict
      doc_input = {
        testcaseid: {
          sessionid: str
          verdict: str
          annotation: str
          attachment: []
        }
      }
    """
    doc_input_items = doc_input.items()
    doc_input_items.sort()
    for test_case_id, results_content in doc_input_items:
      self._create_test_res_node(test_case_id)
      for param_name, param_value in results_content.iteritems():
        if param_name == 'attachment':
          for attach_content in param_value:
            self._create_param_elem(param_name, attach_content)
        else:
          self._create_param_elem(param_name, param_value)
    return
  
  def save_res_doc_file(self, xml_file_loc, xml_indent='  '):
    file_dir = os.path.split(xml_file_loc)[0]
    if len(file_dir) == 0:
      raise TestError("No appropriate directory is specified for test results doc file!")
    if not os.path.exists(file_dir):
      os.makedirs(file_dir)
    doc_file = open(xml_file_loc, 'wb')
    doc_file.write(self.dom_doc.toprettyxml(indent=xml_indent))
    doc_file.close()
