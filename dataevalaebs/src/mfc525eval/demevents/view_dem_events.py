# -*- dataeval: init -*-
from collections import OrderedDict

import interface
import datavis
import logging


logger = logging.getLogger("view_dem_events")
def_param = interface.NullParam


class View(interface.iView):

		dep = {
				'dem_data': 'fill_dem_events@aebs.fill'
		}
		def check(self):
				commonTime, group = self.modules.fill(self.dep["dem_data"])
				table_headers_mapping = OrderedDict(
								[
									('EventId HEX', 'EventId HEX'),
									('EventId DEC', 'EventId DEC'),
									('DEM Event', 'DEM Event'),
									("EntryStatus", "EntryStatus"),
									("OccCtr", "OccCtr"),
									("OccOrder", "OccOrder"),
									("EntryDataPos","EntryDataPos"),
								]
				)
				return commonTime , group, table_headers_mapping

		def view(self, commonTime, group,table_headers_mapping):
				table_nav = datavis.cTableNavigator(title = "DEM Events")
				self.sync.addClient(table_nav)
				table_nav.addtabledata(commonTime, group, table_headers_mapping)


if __name__ == "__main__":
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\Measurement\DEM_meas\mi5id787__2023-03-10_16-00-07_1678464611490000_DI6522540_Issue2.h5"
		config, manager, manager_modules = init_dataeval(["-m", meas_path])
		manager.build(["view_dem_events@aebseval.bitfiled_aebs"], show_navigators=True)
		print("Done")