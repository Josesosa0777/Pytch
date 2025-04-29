# -*- dataeval: init -*-
import numpy as np
from numpy.core.fromnumeric import size
from pyutils.enum import enum
from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals


MEASURED_BY_VALS = (
		'NO_INFO',
		'PREDICTION',
		'RADAR_ONLY',
		'CAMERA_ONLY',
		'FUSED',
)
MEASURED_BY_ST = enum(**dict((name, n) for n, name in enumerate(MEASURED_BY_VALS)))

class Search(iSearch):
        dep = ('fill_flc25_cem_tpf_tracks@aebs.fill', 'fillFLC25_AOA_ACC@aebs.fill', 'fill_flc25_aoa_aebs_tracks@aebs.fill')
        optdep = {
            'drivdist': 'set_drivendistance@egoeval',
        }

        def check(self):
                modules = self.get_modules()
                tracks,_ = modules.fill("fill_flc25_cem_tpf_tracks@aebs.fill")
                t, acc_obj = modules.fill("fillFLC25_AOA_ACC@aebs.fill")
                aebs_obj = modules.fill("fill_flc25_aoa_aebs_tracks@aebs.fill")[0]
                return tracks, acc_obj, aebs_obj

        def fill(self, tracks, acc_obj, aebs_obj):
                time = tracks.time
                title = "FLC25 fused state"
                votes = self.batch.get_labelgroups(title)
                report = Report(cIntervalList(time), title, votes=votes)
                for obj in acc_obj:
                #for i, obj in tracks.iteritems():
                    #valid_object_classif = obj.obj_type.truck | obj.obj_type.pedestrian | obj.obj_type.motorcycle | obj.obj_type.truck | obj.obj_type.bicycle
                    #valid_moving_state = obj.mov_state.stat | obj.mov_state.stopped | obj.mov_state.moving | obj.mov_state.crossing | obj.mov_state.crossing_left | obj.mov_state.crossing_right
                    #valid_lane_assoc = obj.lane.same | obj.lane.left | obj.lane.right
                    #measuredByNone =   (obj.eMeasuredBy == 0) & (obj.obj_type != 5) & valid_object_classif
                    #measuredByPred =   (obj.eMeasuredBy == 1) & valid_object_classif
                    #measuredByRadar =  (obj.eMeasuredBy == 2) & valid_object_classif
                    #measuredByCamera = (obj.eMeasuredBy == 3) & valid_object_classif
                    #measuredByFused =  (obj.eMeasuredBy == 4) & valid_object_classif
                
                    measuredByNone   = (obj['measured_by'] == 0) & (obj['id'] != 255)
                    measuredByPred   = (obj['measured_by'] == 1) & (obj['id'] != 255)
                    measuredByRadar  = (obj['measured_by'] == 2) & (obj['id'] != 255)
                    measuredByCamera = (obj['measured_by'] == 3) & (obj['id'] != 255)
                    measuredByFused  = (obj['measured_by'] == 4) & (obj['id'] != 255)
                
                    for st,end in maskToIntervals(measuredByNone):
                        index = report.addInterval( (st,end) )
                        report.vote(index, title, 'None')
                
                    for st,end in maskToIntervals(measuredByPred):
                        index = report.addInterval( (st,end) )
                        report.vote(index, title, 'Prediction')
                
                    for st,end in maskToIntervals(measuredByRadar):
                        index = report.addInterval( (st,end) )
                        report.vote(index, title, 'Radar only')
                
                    for st,end in maskToIntervals(measuredByCamera):
                        index = report.addInterval( (st,end) )
                        report.vote(index, title, 'Camera only')

                    for st,end in maskToIntervals(measuredByFused):
                        index = report.addInterval( (st,end) )
                        report.vote(index, title, 'Fused')
                
                obj = aebs_obj
                measuredByNone = obj.measured_by.none & (obj.object_id != 255)
                measuredByPred = obj.measured_by.prediction & (obj.object_id != 255)
                measuredByRadar = obj.measured_by.radar_only & (obj.object_id != 255)    
                measuredByCamera = obj.measured_by.camera_only & (obj.object_id != 255)
                measuredByFused = obj.measured_by.fused & (obj.object_id != 255)

                for st,end in maskToIntervals(measuredByNone):
                    index = report.addInterval( (st,end) )
                    report.vote(index, title, 'None')
            
                for st,end in maskToIntervals(measuredByPred):
                    index = report.addInterval( (st,end) )
                    report.vote(index, title, 'Prediction')
            
                for st,end in maskToIntervals(measuredByRadar):
                    index = report.addInterval( (st,end) )
                    report.vote(index, title, 'Radar only')
            
                for st,end in maskToIntervals(measuredByCamera):
                    index = report.addInterval( (st,end) )
                    report.vote(index, title, 'Camera only')

                for st,end in maskToIntervals(measuredByFused):
                    index = report.addInterval( (st,end) )
                    report.vote(index, title, 'Fused')
                
                return report

        def search(self, report):
            self.batch.add_entry(report, result=self.PASSED)
            return