import grouptypes as gtps
from datavis.GroupParam import cGroupParam as Param
from config.parameter import GroupParams

fill_prj = '@ta.fill'

Groups = GroupParams({
    'fillContiSRR320%s' % fill_prj: {
        'ContiSRR320':Param(gtps.CONTI_SRR320, 'C', False, False),
    },
    'fillContiSRR520%s' % fill_prj: {
        'Conti_SRR520_radar_1':Param(gtps.CONTI_SRR520_radar_1, 'C', False, False),
        'Conti_SRR520_radar_2':Param(gtps.CONTI_SRR520_radar_2, 'V', False, False),
    },
    'fillContiSRR520_CAM%s' % fill_prj: {
        'BSM_CAM':Param(gtps.BSM_CAM, '4', False, False),
    },
    'fillContiSRR520_LS%s' % fill_prj: {
        'BSM_LS':Param(gtps.BSM_LS, '5', False, False),
    },
    'fillContiSRR520_HS%s' % fill_prj: {
        'BSM_HS':Param(gtps.BSM_HS, '6', False, False),
    },
    'fillContiSRR520_DRAD_LONG%s' % fill_prj: {
        'BSM_DRAD_LONG': Param(gtps.BSM_DRAD_LONG, '7', False, False),
    },
    'fillContiSRR520_DRAD_LAT%s' % fill_prj: {
        'BSM_DRAD_LAT': Param(gtps.BSM_DRAD_LAT, '8', False, False),
    }
})
"""type : GroupParams
{StatusName<str>: {GroupName<str> : GroupParam<Param>}, }"""
