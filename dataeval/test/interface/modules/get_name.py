from unittest import TestCase

from interface.modules import Container

class BuildNameSpace(TestCase):
  def setUp(self):
    namespace = {
      'viewWithParam-egg@prj': 0,
      'viewWithParam-eggegg@prj': 1,
      'viewWithoutParam@prj': 2,
      'viewWithParamAlone-bar@prj': 3,
      'viewWithTwoParams-param1-param2@prj': 4,
    }
    self.container = Container(namespace)
    return

  def test_name_without_param(self):
    self.assertEqual(self.container.get_name('viewWithoutParam@prj'),
                     'viewWithoutParam@prj')
    return

  def test_name_with_param(self):
    self.assertEqual(self.container.get_name('viewWithParam-egg@prj'),
                     'viewWithParam-egg@prj')
    return

  def test_name_with_two_params(self):
    self.assertEqual(self.container.get_name(
                      'viewWithTwoParams-param1-param2@prj'),
                     'viewWithTwoParams-param1-param2@prj')
    return

  #[kovesdv] : I think it is obsolated
  #def test_extend_name_with_param(self):
  #  self.assertEqual(self.container.get_name('viewWithParamAlone@prj'),
  #                   'viewWithParamAlone-bar@prj')
  #  return

  #[kovesdv] : I think it is obsolated
  #def test_error_for_multiple_result(self):
  #  name = 'viewWithParam@prj'
  #  msg = r'Multiple modules registered with `%s`: [\w, ]+' % name
  #  with self.assertRaisesRegexp(AssertionError, msg):
  #    self.container.get_name(name)
  #  return

  def test_error_for_no_match(self):
    name = 'viewSilly@prj'
    msg = r'`%s` is not a registered module' % name
    with self.assertRaisesRegexp(AssertionError, msg):
      self.container.get_name(name)
    return

if __name__ == '__main__':
  from unittest import main

  main()
