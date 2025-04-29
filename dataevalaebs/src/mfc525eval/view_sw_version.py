# -*- dataeval: init -*-
import os
__file__ = os.path.abspath(os.path.join(os.path.dirname(__file__), 'version\\view_sw_version.py'))
exec(compile(open(__file__).read(), __file__, 'exec'))
