# -*- dataeval: init -*-
from collections import OrderedDict

import interface
import datavis
import logging


logger = logging.getLogger("view_bitfiels_aebsoutput")
def_param = interface.NullParam


class View(interface.iView):

		dep = {
				'aeb_data': 'fill_bitfield_aebs_tracks@aebs.fill'
		}
		def check(self):
				commonTime, group = self.modules.fill(self.dep["aeb_data"])
				table_headers_mapping = OrderedDict(
								[
										("attribute","Attribute"),
										("first_bitfield", "aebs_first_bitfield"),
										("second_bitfield", "aebs_second_bitfield"),
										("third_bitfield", "aebs_third_bitfield"),
										("mlaeb_left_first_bitfield", "mlaeb_left_first_bitfield"),
										("mlaeb_left_second_bitfield", "mlaeb_left_second_bitfield"),
										("mlaeb_left_third_bitfield", "mlaeb_left_third_bitfield"),
										("mlaeb_right_first_bitfield", "mlaeb_right_first_bitfield"),
										("mlaeb_right_second_bitfield", "mlaeb_right_second_bitfield"),
										("mlaeb_right_third_bitfield", "mlaeb_right_third_bitfield"),
										("enable_bitfield", "enable_bitfield"),
								]
				)
				return commonTime , group, table_headers_mapping

		def view(self,commonTime, group,table_headers_mapping):
				table_nav = datavis.cTableNavigator(title = "Bitfield Table")
				self.sync.addClient(table_nav)
				table_nav.addtabledata(commonTime, group, table_headers_mapping)


if __name__ == "__main__":
		from config.Config import init_dataeval

		meas_path = r"C:\Users\wattamwa\Desktop\measurments\bitfield_aebs\new\mi5id787__2022-02-15_07-13-31.h5"
		config, manager, manager_modules = init_dataeval(["-m", meas_path])
		manager.build(["view_bitfield_aebsoutput@aebseval.bitfiled_aebs"], show_navigators=True)
		print("Done")