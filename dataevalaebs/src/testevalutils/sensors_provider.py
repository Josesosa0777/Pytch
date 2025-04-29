from config.Config import init_dataeval
class SensorsProvider:
    SensorsRegistry = {
        "FLC25_CEM_TPF": {
            "raw"  : "fill_flc25_cem_tpf_tracks@aebs.fill",
            "clean": "fillFLC25_CEM_TPF@aebs.fill"
        }
    }


    @staticmethod
    def getSensorData(measurementPath, sensorName, needRaw = False):
        # try:

        config, manager, manager_modules = init_dataeval(
            ['-m', measurementPath])

        sensorScript = SensorsProvider.SensorsRegistry[sensorName]["clean"]
        if needRaw:
            sensorScript = SensorsProvider.SensorsRegistry[sensorName]["raw"]

        object = manager_modules.calc(sensorScript, manager)
        return object
        # except:
        #     return None
        # finally:
        #     return None

    def getAvailableSensors(self):
        return SensorsProvider.SensorsRegistry.keys()


if __name__ == '__main__':

    meas_path = r"C:\KBData\Data\Development\PythonToolchainSupport" \
                r"\ContiMeasurementsSuport\dcnvth5_naming\mi5id787__2021-10" \
                r"-28_00-03-59.h5"
    data = SensorsProvider.getSensorData(meas_path, "FLC25_CEM_TPF")
    print(data)
