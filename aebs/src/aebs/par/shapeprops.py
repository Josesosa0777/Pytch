"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''The module defines legend and display style for every single group type.
'''

__docformat__ = "restructuredtext en"

import grouptypes as gtps
from datavis.OpenGLutil import EDGE, FACE

UPSIDE_DOWN = (180.0, 1.0, 0.0, 0.0)
# rgb color codes
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
CYAN = (0,255,255)
BROWN = (139,69,0)
PURPLE = (104,34,139)
MAGENTA = (255,0,255)
GRAY = (192,192,192)
YELLOW = (255, 255, 0)

COL = WHITE
""":type: tuple
Default color in (R,G,B) format, where each component is in range(255)"""
ALP = 100
""":type: int
Default alpha (trasparency level) in range(255): 0 is transparent, 255 is opaque"""
LW  =   1
""":type: int
Default line width in positive integer range"""
ROT = UPSIDE_DOWN
""":type: int
Default rotation in (angle,x,y,z) format, where angle specifies the rotation rate in degrees,
x,y,z are the coordinates of the vector where the rotation is done around (in OpenGL coordinate system)"""

ShapeProps  = { 
  'LRR3_FUS_MOV':      ('LRR3_FUS - Moving',               ( dict( shape='rectangle',          type=EDGE, color=COL,          lw=2,            ),   
                                                                dict( shape='rectangle',          type=FACE, color=COL,                 alpha=ALP ) )),
  'INTROS':            ('Intros',                          ( dict( shape='aimingSign',         type=EDGE, color=COL,          lw=2             ),)),
  'LRR3_FUS_STAT':     ('LRR3_FUS - Stationary',           ( dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),
  'CVR3_ATS_MOV':      ('CVR3_ATS - Moving',               ( dict( shape='diamond',            type=EDGE, color=COL,          lw=2             ),
                                                                dict( shape='diamond',            type=FACE, color=COL,                 alpha=ALP ) )),
  'CVR3_ATS_STAT':     ('CVR3_ATS - Stationary',           ( dict( shape='soundLines',         type=EDGE, color=COL,          lw=2             ),)),
  'FLR20_MOV':         ('FLR20    - Moving',               ( dict( shape='triangle',           type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='triangle',           type=FACE, color=COL,                 alpha=ALP ) )),
  'FLR20_STAT':        ('FLR20    - Stationary',           ( dict( shape='+',                  type=EDGE, color=COL,          lw=LW            ),)),
  'FLR20_AEB':         ('FLR20 AEB track',                 ( dict( shape='intro',              type=EDGE, color=COL,          lw=2             ),)),
  'FLR20_ACC':         ('FLR20 ACC track',                 ( dict( shape='greaterLessThanSign',type=EDGE, color=COL,          lw=2             ),)),
  'FLR20_FUSED_MOV':   ('FLR20 - Fused moving',            ( dict( shape='triangle',           type=EDGE, color=MAGENTA,      lw=LW            ),
                                                                dict( shape='triangle',           type=FACE, color=MAGENTA,             alpha=ALP ) )),
  'FLR20_FUSED_STAT':  ('FLR20 - Fused stationary',        ( dict( shape='+',                  type=EDGE, color=MAGENTA,      lw=2             ),)),
  'FLR20_RADAR_ONLY_MOV':
                       ('FLR20 - Radar-only moving',       ( dict( shape='triangle',           type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='triangle',           type=FACE, color=COL,                 alpha=ALP ) )),
  'FLR20_RADAR_ONLY_STAT':
                       ('FLR20 - Radar-only stationary',   ( dict( shape='+',                  type=EDGE, color=COL,          lw=2             ),)),
  'FLR20_AEBS_WARNING_KB':      ('FLR20 AEBS Warning - KB',      ( dict( shape='soundLines',   type=EDGE, color=COL,          lw=2             ),)),
  'FLR20_AEBS_WARNING_TRW':     ('FLR20 AEBS Warning - TRW',     ( dict( shape='soundLines',   type=EDGE, color=COL,          lw=2             ),)),
  'FLR20_AEBS_WARNING_FLR20':   ('FLR20 AEBS Warning - FLR20',   ( dict( shape='soundLines',   type=EDGE, color=COL,          lw=2             ),)),
  'FLR20_AEBS_WARNING_AUTOBOX': ('FLR20 AEBS Warning - AUTOBOX', ( dict( shape='soundLines',   type=EDGE, color=COL,          lw=2             ),)),
  'FLR20_AEBS_WARNING_SIL':     ('FLR20 AEBS Warning - SIL',     ( dict( shape='soundLines',   type=EDGE, color=COL,          lw=2             ),)),
  'FLR20_TARGET':      ('FLR20 target',                    ( dict( shape='circle',             type=EDGE, color=COL,          lw=LW            ),)),

  'FLR25_MOV':  ('FLR25    - Moving',             (dict(shape='diamond',              type=EDGE, color=GREEN,       lw=2),          )),
  'FLR25_STOPPED':  ('FLR25    - Stopped',            (dict(shape='diamond',              type=EDGE, color=RED,         lw=2),          )),
  'FLR25_STAT': ('FLR25    - Stationary',         (dict(shape='circle',                     type=EDGE, color=RED,         lw=2),          )),
  'FLR25_AEB':         ('FLR25 AEB track',                 ( dict( shape='intro',              type=EDGE, color=COL,          lw=2             ),)),
  'FLC25_AEBS_FIRST_OBJ': ('FLC25_AEBS_FIRST_OBJ track', (dict(shape = 'intro', type = EDGE, color = COL, lw = 2),)),

  'FLC25_AEBS_SECOND_OBJ': ('FLC25_AEBS_SECOND_OBJ track', (dict(shape = 'circle', type = EDGE, color = COL, lw = 2),)),
  'FLC25_AEBS_THIRD_OBJ': ('FLC25_AEBS_THIRD_OBJ track', (dict(shape = 'triangle', type = EDGE, color = COL, lw = 2),)),
  'FLC25_MLAEB_LEFT_FIRST_OBJ': ('FLC25_MLAEB_LEFT_FIRST_OBJ track', (dict(shape = 'hexagon', type = EDGE, color = COL, lw = 2),)),
  'FLC25_MLAEB_LEFT_SECOND_OBJ': ('FLC25_MLAEB_LEFT_SECOND_OBJ track', (dict(shape = 'diamond', type = EDGE, color = COL, lw = 2),)),
  'FLC25_MLAEB_LEFT_THIRD_OBJ': ('FLC25_MLAEB_LEFT_THIRD_OBJ track', (dict(shape = 'rectangle', type = EDGE, color = COL, lw = 2),)),
  'FLC25_MLAEB_RIGHT_FIRST_OBJ': ('FLC25_MLAEB_RIGHT_FIRST_OBJ track', (dict(shape = '+', type = EDGE, color = COL, lw = 2),)),
  'FLC25_MLAEB_RIGHT_SECOND_OBJ': ('FLC25_MLAEB_RIGHT_SECOND_OBJ track', (dict(shape = 'X', type = EDGE, color = COL, lw = 2),)),
  'FLC25_MLAEB_RIGHT_THIRD_OBJ': ('FLC25_MLAEB_RIGHT_THIRD_OBJ track', (dict(shape = 'triangleUpsideDown', type = EDGE, color = COL, lw = 2),)),

  'FLR25_AEB_RESIM':         ('FLR25 AEB resim track',                 ( dict( shape='triangle', type=EDGE, color=MAGENTA,        lw=2             ),)),
  'FLR25_AEB_RETEST_RESIM': ('FLR25 AEB retest resim track', (dict(shape='triangle', type=EDGE, color=GREEN, lw=2),)),
  'FLR25_AEB_BASELINE_RESIM': ('FLR25 AEB baseline resim track', (dict(shape='circle', type=EDGE, color=BLUE, lw=2),)),
  'FLR25_ACC_PED':         ('FLR25_ACC_PED - Stopped',                 (dict(shape='circle',     type=EDGE, color=BLUE,         lw=2),          )),
  'FLR25_ACC_PED_STOP':         ('FLR25_ACC_PED - Stopped',                 (dict(shape='circle',     type=EDGE, color=BLUE,         lw=2),          )),
  'FLR25_ACC_MOV' : ('FLR25_ACC   - Moving', (dict(shape = 'circle', type = EDGE, color = GREEN, lw = 2),
                                                    dict(shape = 'circle', type = EDGE, color = GREEN,
                                                         alpha = ALP))),

  'FLR25_ACC_STOPPED':  ('FLR25 _ACC   - Stopped',            (dict(shape='circle',              type=EDGE, color=BLUE,         lw=2),          )),

  'FLR25_ACC_STAT': (
  'FLR25_ACC    - Stationary', (dict(shape = 'circle', type = EDGE, color = RED, lw = LW),)),

  'FLR25_ACC_GO_SUPP_PED_MOV'    : ('FLR25_ACC_GO_SUPP_PED   - Moving', (dict(shape = 'pedestrian', type = EDGE, color = GREEN, lw = 2),
                                                   dict(shape = 'pedestrian', type = EDGE, color = GREEN,
                                                        alpha = ALP))),
  'FLR25_ACC_GO_SUPP_PED_STOPPED': ('FLR25_ACC_GO_SUPP_PED   - Stopped', (dict(shape = 'pedestrian', type = EDGE, color = BLUE, lw = 2),)),
  'FLR25_ACC_GO_SUPP_PED_STAT'   : (
        'FLR25_ACC_GO_SUPP_PED   - Stationary', (dict(shape = 'pedestrian', type = EDGE, color = RED, lw = LW),)),


    'AC100_MOV':         ('AC100    - Moving',               ( dict( shape='triangle',           type=EDGE, color=COL,          lw=LW            ),
                                                            dict( shape='triangle',           type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_STAT':        ('AC100    - Stationary',           ( dict( shape='+',                  type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_ACC':         ('AC100    - SameLane_near',        ( dict( shape='diamond',            type=EDGE, color=COL,          lw=2             ),
                                                                dict( shape='diamond',            type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_IIV':         ('AC100    - SameLane_far',         ( dict( shape='diamond',            type=EDGE, color=COL,          lw=2             ),
                                                                dict( shape='diamond',            type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_NIV_L':       ('AC100    - LeftLane_near',        ( dict( shape='diamond',            type=EDGE, color=COL,          lw=2             ),
                                                                dict( shape='diamond',            type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_NIV_R':       ('AC100    - RightLane_near',       ( dict( shape='diamond',            type=EDGE, color=COL,          lw=2             ),
                                                                dict( shape='diamond',            type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_CW':          ('AC100    - Coll. warning',        ( dict( shape='soundLines',         type=EDGE, color=COL,          lw=2             ),)),
  'AC100_CO':          ('AC100    - Coll. object',         ( dict( shape='intro',              type=EDGE, color=COL,          lw=2             ),)),
  'AC100_STAT_TARGET': ('AC100_TargetFlag - STAT',         ( dict( shape='circle',             type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_AMBIGUOUS':   ('AC100_TargetFlag - AMBIGUOUS',    ( dict( shape='circle',             type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_WEAK_DET':    ('AC100_TargetFlag - WEAK_DET',     ( dict( shape='circle',             type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_WEAK_PARTNER':('AC100_TargetFlag - WEAK_PARTNER', ( dict( shape='circle',             type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_PHI_ERROR':   ('AC100_TargetFlag - PHI_ERROR',    ( dict( shape='circle',             type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_UNCONF':      ('AC100_TargetStatus - UNCONF',     ( dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_PARTIAL':     ('AC100_TargetStatus - PARTIAL',    ( dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_SHADED':      ('AC100_TargetStatus - SHADED',     ( dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_CONF':        ('AC100_TargetStatus - CONF',       ( dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),
  'AC100_POSITION':    ('AC100_TrackingFlag - POS',        ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_CLOSE_TO_ACC':('AC100_TrackingFlag - CLOSE_TO_ACC',  
                                                              ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_BEHIND_CBR':  ('AC100_TrackingFlag - BEHIND_CBR', ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_CLOSE_LOWPWR':('AC100_TrackingFlag - CLOSE_LOWPWR',  
                                                              ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_FREQ':        ('AC100_TrackingFlag - FREQ',       ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_CLOSE_TO_TRACK':         
                          ('AC100_TrackingFlag - CLOSE_TO_TRACK',  
                                                              ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_TYRE':        ('AC100_TrackingFlag - TYRE',       ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'AC100_SEC_PHI_ERR': ('AC100_TrackingFlag - SEC_PHI_ERR',( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'FLC20_MOV':         ('FLC20    - Moving',               ( dict( shape='eye',                type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='eye',                type=FACE, color=COL,                 alpha=ALP ) )),
  'FLC20_STAT':        ('FLC20    - Stationary',           ( dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),
  'FLC25_TSR_STAT': ('FLC25 TSR - Stationary', (dict(shape = 'circle', type = EDGE, color = RED, lw = 2),)),
  'FLC25_TSR_SHORTLISTED_STAT': ('FLC25 TSR SHORTLISTED - Stationary', (dict(shape = 'X', type = EDGE, color = RED, lw = 2),)),
  'FLC25_CEM_TPF_MOV': ('FLC25_CEM_TPF   - Moving',                       ( dict(shape='rectangle', type=EDGE, color=BLUE, lw=2),
                                                            dict(shape='rectangle', type=EDGE, color=BLUE, alpha=ALP))),
  'FLC25_CEM_TPF_STAT': ('FLC25_CEM_TPF    - Stationary', (dict(shape='triangleUpsideDown', type=EDGE, color=RED, lw=LW),)),
  'FLC25_CEM_TPF_MG_AOA_ACC_MOV': ('FLC25_CEM_TPF_MG_AOA_ACC   - Moving',                       ( dict(shape='rectangle', type=EDGE, color=BLUE, lw=2),
                                                            dict(shape='rectangle', type=EDGE, color=BLUE, alpha=ALP))),
  'FLC25_CEM_TPF_MG_AOA_ACC_STAT': ('FLC25_CEM_TPF_MG_AOA_ACC    - Stationary', (dict(shape='triangleUpsideDown', type=EDGE, color=RED, lw=LW),)),
  'FLC25_CAN_MOV' : ('FLC25_CAN    - Moving', (dict(shape = 'hexagon', type = EDGE, color = BLUE, lw = 2),
                                     dict(shape = 'hexagon', type = EDGE, color = BLUE, alpha = ALP))),
  'FLC25_CAN_STAT': ('FLC25_CAN    - Stationary', (dict(shape = 'flippedN', type = EDGE, color = RED, lw = LW),)),
  'FLC25_ARS_FCU_MOV': ('FLC25_ARS_FCU    - Moving', (dict(shape='car', type=EDGE, color=BLUE, lw=2),
   dict(shape='car', type=FACE, color=BLUE, alpha=ALP))),
  'FLC25_ARS_FCU_STAT': ('FLC25_ARS_FCU   - Stationary', (dict(shape='YupsideDown', type=EDGE, color=RED, lw=2),)),
  'FLC25_ARS620_MOV': ('FLC25_ARS620    - Moving', (dict(shape = 'rectangle', type = EDGE, color = BLUE, lw = 2), dict(shape = 'rectangle', type = EDGE, color = BLUE, alpha = ALP))),
  'FLC25_ARS620_STAT': ('FLC25_ARS620   - Stationary', (dict(shape='triangleUpsideDown', type=EDGE, color=RED, lw=2),)),
  'FLC25_EM_MOV' : ('FLC25_EM   - Moving', (dict(shape = 'rectangle', type = EDGE, color = BLUE, lw = 2), dict(shape = 'rectangle', type = EDGE, color = BLUE, alpha = ALP))),
  'FLC25_EM_STAT': ('FLC25_EM    - Stationary', (dict(shape = 'triangleUpsideDown', type = EDGE, color = RED, lw = LW),)),

   'FLC25_PAEBS_AOAOUTPUT_MOV' : ('FLC25_PAEBS_AOAOUTPUT   - Moving', (dict(shape = 'rectangle', type = EDGE, color = BLUE, lw = 2),
                                                        dict(shape = 'rectangle', type = EDGE, color = BLUE,
                                                             alpha = ALP))),

   'FLC25_PAEBS_AOAOUTPUT_MOV_RESIM' : ('FLC25_PAEBS_AOAOUTPUT_RESIM   - Moving', (dict(shape = 'circle', type = EDGE, color = MAGENTA, lw = 2),
                                                        dict(shape = 'circle', type = EDGE, color = MAGENTA,
                                                             alpha = ALP))),
   'FLC25_PAEBS_AOAOUTPUT_STAT': (

   'FLC25_PAEBS_AOAOUTPUT   - Stationary', (dict(shape = 'triangleUpsideDown', type = EDGE, color = RED, lw = LW),)),

   'FLC25_PAEBS_AOAOUTPUT_STAT_RESIM': (

   'FLC25_PAEBS_AOAOUTPUT_RESIM   - Stationary', (dict(shape = 'flippedN', type = EDGE, color = RED, lw = LW),)),

  'FLC25_PAEBS_DEBUG_PED_CROSS' : ('FLC25_PAEBS_DEBUG   - Pedestrian, crossing', (dict(shape = 'diamond', type = FACE, color = RED, lw = 2),)),
   
  'FLC25_PAEBS_DEBUG_BIC_CROSS' : ('FLC25_PAEBS_DEBUG   - Bicycle, crossing', (dict(shape = 'circle', type = FACE, color = RED, lw = 2),)),
      
   'FLC25_PAEBS_DEBUG_PED_NOT_CROSS' : ('FLC25_PAEBS_DEBUG   - Pedestrian, not crossing', (dict(shape = 'diamond', type = EDGE, color = BLUE, lw = LW),)),
   
   'FLC25_PAEBS_DEBUG_BIC_NOT_CROSS' : ('FLC25_PAEBS_DEBUG   - Bicycle, not crossing', (dict(shape = 'circle', type = EDGE, color = BLUE, lw = LW),)),

  'FLC25_PAEBS_DEBUG_UNDEFINED' : ('FLC25_PAEBS_DEBUG   - Undefined', (dict(shape = 'X', type = EDGE, color = BLACK, lw = LW),)),

  'FLC25_PAEBS_LAUSCH_PED_CROSS': (
    'FLC25_PAEBS_DEBUG   - Pedestrian, crossing', (dict(shape='pentagon', type=FACE, color=RED, lw=2),)),

  'FLC25_PAEBS_LAUSCH_PED_NOT_CROSS': (
    'FLC25_PAEBS_DEBUG   - Pedestrian, not crossing', (dict(shape='pentagon', type=EDGE, color=BLUE, lw=LW),)),

  'FLC25_PAEBS_LAUSCH_UNDEFINED': (
    'FLC25_PAEBS_DEBUG   - Undefined', (dict(shape='X', type=EDGE, color=BLACK, lw=LW),)),

    'FLC25_AOA_AEBS_MOV' : (
    'FLC25_AOA_AEBS   - Moving', (dict(shape = 'rectangle', type = EDGE, color = BLUE, lw = 2),
                                   dict(shape = 'rectangle', type = EDGE, color = BLUE,
                                        alpha = ALP))),
    'FLC25_AOA_AEBS_STAT': (

        'FLC25_AOA_AEBS    - Stationary', (dict(shape = 'triangleUpsideDown', type = EDGE, color = RED, lw = LW),)),

    'FLC25_AOA_ACC_MOV' : (
        'FLC25_AOA_ACC   - Moving', (dict(shape = 'circle', type = EDGE, color = BLUE, lw = 2),
                                      dict(shape = 'circle', type = EDGE, color = BLUE,
                                           alpha = ALP))),
    'FLC25_AOA_ACC_STAT': (

        'FLC25_AOA_ACC    - Stationary', (dict(shape = 'triangle', type = EDGE, color = RED, lw = LW),)),

    'FLC25_PAEBS_CAN_MOV' : ('FLC25_PAEBS_CAN   - Moving', (dict(shape = 'rectangle', type = EDGE, color = BLUE, lw = 2),
                                                        dict(shape = 'rectangle', type = EDGE, color = BLUE,
                                                             alpha = ALP))),
   'FLC25_PAEBS_CAN_STAT': (
   'FLC25_PAEBS_CAN    - Stationary', (dict(shape = 'triangleUpsideDown', type = EDGE, color = RED, lw = LW),)),

  'GT_FREEBOARD_STAT': ('GROUND_TRUTH_FREEBOARD-State', (dict(shape='circle', type=EDGE, color=RED, lw=2),)),
  'GT_DELTA_STAT': ('GROUND_TRUTH_DELTA-State', (dict(shape='hexagon', type=EDGE, color=RED, lw=2),)),
  'SLR25_RFB_MOV' : ('SLR25_RFB   - Moving', (dict(shape = 'rectangle', type = EDGE, color = BLUE, lw = 2),
                                                dict(shape = 'rectangle', type = EDGE, color = BLUE,
                                                     alpha = ALP))),
  'SLR25_RFB_STAT': (
        'SLR25_RFB    - Stationary', (dict(shape = 'triangleUpsideDown', type = EDGE, color = RED, lw = LW),)),
  'SLR25_RFF_MOV' : ('SLR25_RFF   - Moving', (dict(shape = 'rectangle', type = EDGE, color = BLUE, lw = 2),
                                                dict(shape = 'rectangle', type = EDGE, color = BLUE,
                                                     alpha = ALP))),
  'SLR25_RFF_STAT': (
        'SLR25_RFF    - Stationary', (dict(shape = 'triangleUpsideDown', type = EDGE, color = RED, lw = LW),)),

   'SLR25_Front_STAT': (
        'SLR25_Front    - Stationary', (dict(shape = 'triangleUpsideDown', type = EDGE, color = RED, lw = LW),)),

   'SLR25_Front_MOV' : ('SLR25_Front   - Moving', (dict(shape = 'rectangle', type = EDGE, color = BLUE, lw = 2),
                                                dict(shape = 'rectangle', type = EDGE, color = BLUE,
                                                     alpha = ALP))),

    'SCAM_MOV':          ('S-Cam    - Moving',               ( dict( shape='eye',                type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='eye',                type=FACE, color=COL,                 alpha=ALP ) )),
  'SCAM_STAT':         ('S-Cam    - Stationary',           ( dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),

  'ESR_MOV':           ('ESR      - Moving',               ( dict( shape='hexagon',            type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='hexagon',            type=FACE, color=COL,                 alpha=ALP ) )),
  'ESR_STAT':          ('ESR      - Stationary',           ( dict( shape='upsideDownT',        type=EDGE, color=COL,          lw=LW            ),)),
  'IBEO_STAT':         ('IBEO     - Stationary',           ( dict( shape='v',                  type=EDGE, color=COL,          lw=LW            ),)),
  'IBEO_MOV':          ('IBEO     - Moving',               ( dict( shape='rectNoCorn',         type=EDGE, color=COL,          lw=2             ),)),
  'VFP_MOV':           ('VFP      - Moving',               ( dict( shape='eye',                type=EDGE, color=COL,          lw=2             ),)),
  'VFP_STAT':          ('VFP      - Stationary',           ( dict( shape='smallBow',           type=EDGE, color=COL,          lw=LW            ),)),
  'VFP_PEDESTRIAN':    ('VFP      - Pedestrian',           ( dict( shape='pedestrian',         type=EDGE, color=COL,          lw=LW            ),)),
  'ITERIS':            ('Iteris   - Moving',               ( dict( shape='eyeRot',             type=EDGE, color=COL,          lw=2,            ),
                                                                dict( shape='eyeRot',             type=FACE, color=COL,                 alpha=ALP ) )),
  'MOBILEYE':          ('MobilEye - Moving',               ( dict( shape='circle',             type=EDGE, color=COL,          lw=2             ),
                                                                dict( shape='circle',             type=FACE, color=COL,                 alpha=ALP ) )),
  'LRR3_SIT_MOV':      ('LRR3_SIT - Moving',               ( dict( shape='trapezoid',          type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='trapezoid',          type=FACE, color=COL,                 alpha=ALP ) )),
  'LRR3_SIT_STAT':     ('LRR3_SIT - Stationary',           ( dict( shape='flippedN',           type=EDGE, color=COL,          lw=LW            ),)),
  'CVR3_LOC_VALID':    ('CVR3_LOC - Valid',                ( dict( shape='YupsideDown',        type=EDGE, color=COL,          lw=LW,           ),)),
  'CVR3_LOC_INVALID':  ('CVR3_LOC - Invalid',              ( dict( shape='YupsideDown',        type=EDGE, color=COL,          lw=LW,           ),)),
  'CVR3_OHL_MOV':      ('CVR3_OHL - Moving',               ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'CVR3_OHL_STAT':     ('CVR3_OHL - Stationary',           ( dict( shape='Y',                  type=EDGE, color=COL,          lw=LW            ),)),
  'CVR3_POS_MOV':      ('CVR3_POS - Moving',               ( dict( shape='car',                type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='car',                type=FACE, color=COL,                 alpha=ALP ) )),
  'CVR3_POS_STAT':     ('CVR3_POS - Stationary',           ( dict( shape='stop',               type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='stop',               type=FACE, color=COL,                 alpha=ALP ) )),
  'CVR3_POS_INTRO':    ('LRR3_POS - Intro',                ( dict( shape='intro',              type=EDGE, color=MAGENTA,      lw=2             ),)),
  'LRR3_POS_MOV':      ('LRR3_POS - Moving',               ( dict( shape='car',                type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='car',                type=FACE, color=COL,                 alpha=ALP ) )),
  'LRR3_POS_STAT':     ('LRR3_POS - Stationary',           ( dict( shape='stop',               type=EDGE, color=COL,          lw=LW             ),
                                                                dict( shape='stop',               type=FACE, color=COL,                 alpha=ALP ) )),
  'LRR3_OHL_MOV':      ('LRR3_OHL - Moving',               ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'LRR3_OHL_STAT':     ('LRR3_OHL - Stationary',           ( dict( shape='Y',                  type=EDGE, color=COL,          lw=LW            ),)),
  'CVR3_SIT_MOV':      ('CVR3_SIT - Moving',               ( dict( shape='trapezoid',          type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='trapezoid',          type=FACE, color=COL,                 alpha=ALP ) )),
  'CVR3_SIT_STAT':     ('CVR3_SIT - Stationary',           ( dict( shape='flippedN',           type=EDGE, color=COL,          lw=LW            ),)),
  'LRR3_ATS_MOV':      ('LRR3_ATS - Moving',               ( dict( shape='diamond',            type=EDGE, color=COL,          lw=2             ),
                                                                dict( shape='diamond',            type=FACE, color=COL,                 alpha=ALP ) )),               
  'LRR3_ATS_STAT':     ('LRR3_ATS - Stationary',           ( dict( shape='soundLines',         type=EDGE, color=COL,          lw=2             ),)),
  'CVR3_FUS_FUSED_MOV':
                          ('CVR3_FUS - Fused moving',         ( dict( shape='rectangle',          type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='rectangle',          type=FACE, color=COL,                 alpha=ALP ) )),
  'CVR3_FUS_RADAR_ONLY_MOV':
                          ('CVR3_FUS - Radar-only moving',    ( dict( shape='rectangle',          type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='rectangle',          type=FACE, color=COL,                 alpha=ALP ) )),
  'CVR3_FUS_VIDEO_ONLY_MOV':
                          ('CVR3_FUS - Camera-only moving',   ( dict( shape='rectangle',          type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='rectangle',          type=FACE, color=COL,                 alpha=ALP ) )),
  'CVR3_FUS_FUSED_STAT':
                          ('CVR3_FUS - Fused stationary',     ( dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),
  'CVR3_FUS_RADAR_ONLY_STAT':
                          ('CVR3_FUS - Radar-only stationary',( dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),
  'CVR3_FUS_VIDEO_ONLY_STAT':
                          ('CVR3_FUS - Camera-only stationary',(dict( shape='X',                  type=EDGE, color=COL,          lw=LW            ),)),
  'CVR3_FUS_VID':      ('CVR3_FUS - Video',                ( dict( shape='circle',             type=EDGE, color=COL,          lw=2             ),
                                                                dict( shape='circle',             type=FACE, color=COL,                 alpha=ALP ) )),
  'LRR3_LOC_INVALID':  ('LRR3_LOC - Invalid',              ( dict( shape='YupsideDown',        type=EDGE, color=COL,          lw=LW,           ),)),
  'LRR3_LOC_VALID':    ('LRR3_LOC - Valid',                ( dict( shape='YupsideDown',        type=EDGE, color=COL,          lw=LW,           ),)),
  'SDF_LRR3_CVR3_OHL': ('SDF_LRR3_CVR3_OHL',               ( dict( shape='triangleUpsideDown', type=EDGE, color=COL,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=COL,                 alpha=ALP ) )),
  'SDF_CVR3_SCAM_CIPV':('SDF_CVR3_SCam_CIPV',              ( dict( shape='triangleUpsideDown', type=EDGE, color=RED,          lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=RED,                 alpha=ALP ) )),
  'SDF_CVR3_SCAM_STAT':('SDF_CVR3_SCam - Stationary',      ( dict( shape='X',                  type=EDGE, color=RED,          lw=3             ),)),
  'SDF_CVR3_SCAM_MOV': ('SDF_CVR3_SCam - Moving',          ( dict( shape='diamond',            type=EDGE, color=RED,          lw=2             ),
                                                                dict( shape='diamond',            type=FACE, color=RED,                 alpha=ALP ) )),
  'UNKNOWN_OBJECT':    ('Unknown object',                  ( dict( shape='?',                  type=EDGE, color=COL,          lw=LW            ),)),
  'LRR3_ASF_BRAKE':    ('LRR3_ASF - Brake',                ( dict( shape='circle',             type=FACE, color=COL,          lw=2             ),)),
  'LRR3_ASF_WARNING':  ('LRR3_ASF - Warning',              ( dict( shape='soundLines',         type=EDGE, color=BLACK,        lw=6             ),
                                                                dict( shape='soundLines',         type=EDGE, color=MAGENTA,   lw=2             ) )),
  'CVR3_ASF_WARNING':  ('CVR3_ASF - Warning',              ( dict( shape='soundLines',         type=EDGE, color=BLACK,        lw=6             ),
                                                                dict( shape='soundLines',         type=EDGE, color=MAGENTA,   lw=2             ) )),
  'LRR3_ASF_VIDEOCONF':('LRR3_ASF - Video confirmation',   ( dict( shape='aimingSign',         type=EDGE, color=BLACK,        lw=6             ),
                                                                dict( shape='aimingSign',         type=EDGE, color=CYAN,      lw=2             ) )),
  'MBL2_TARGET':       ('MBL2 Target',                     ( dict( shape='YupsideDown',        type=EDGE, color=GREEN,        lw=LW,           ),)),
  'MBL2_TRACK':        ('MBL2 Track',                      ( dict( shape='triangleUpsideDown', type=EDGE, color=BLUE,         lw=LW,           ),
                                                                dict( shape='triangleUpsideDown', type=FACE, color=BLUE,                alpha=ALP ) )),
  'MB79_TARGET':       ('MB79_TARGET',                     ( dict( shape='Y',                  type=EDGE, color=GRAY,         lw=LW            ),)),
  'KB_TARGET':         ('KB_TARGET',                       (dict(shape='Y',                    type=EDGE, color=GRAY,         lw=LW            ),)),
  'MB79_DET_REPR':     ('MB79_DET_REPR',                   (dict(shape='Y',                    type=EDGE, color=BLACK,        lw=LW            ),)),
  'MB79_TRACK_MOV':    ('MB79_TRACK - Moving',             (dict(shape='triangle',              type=EDGE, color=COL,         lw=LW),
                                                                dict(shape='triangle',            type=FACE, color=COL,                 alpha=ALP))),
  'MB79_TRACK_STAT':   ('MB79_TRACK - Stationary',         (dict(shape='+',                     type=EDGE, color=COL,         lw=LW),          )),
  'KB_TRACK_MOV':      ('KB_TRACK - Moving',               (dict(shape='triangle',              type=EDGE, color=COL,         lw=LW),
                                                                dict(shape='triangle',            type=FACE, color=COL,                 alpha=ALP))),
  'KB_TRACK_STAT':     ('KB_TRACK - Stationary',           (dict(shape='X',                     type=EDGE, color=COL,         lw=LW),          )),
  'KB_TRACK_STOP':     ('KB_TRACK - Stopped',              (dict(shape='triangle',              type=EDGE, color=RED,         lw=LW),          )),
  'KB_TRACK_UNK':      ('KB_TRACK - Unknown',              (dict(shape='?',                     type=EDGE, color=BLACK,       lw=LW),          )),
  'MB79_KB_WARNING_TRACK':
                       ('KB Warning Track',                (dict(shape='soundLines',            type=EDGE, color=COL,         lw=2),           )),
  'FURUKAWA_TARGET':   ('FURUKAWA_TARGET',                 (dict(shape='triangle',              type=EDGE, color=COL,         lw=LW),
                                                                dict(shape='triangle',            type=FACE, color=COL,                 alpha=ALP))),
  'KB_AREAS':          ('KB_AREAS',                        (dict(shape=None,                    type=None                                       ),)),
  'KB_CLUSTERS':       ('KB_CLUSTERS',                     (dict(shape=None,                    type=None                                       ),)),
  'CONTI_SRR320':       ('CONTI_SRR320',                   (dict(shape='X',                     type=EDGE, color=COL,         lw=LW),          )),
  'CONTI_AEBS_WARNING':('CONTI AEBS Warning',              (dict(shape='soundLines',            type=EDGE, color=COL,         lw=2             ),)),
  'CONTI_ARS440_MOVING':
                       ('CONTI_ARS440-Moving',             (dict(shape=None,                    type=EDGE, color=GREEN,       lw=LW),          )),
  'CONTI_ARS440_STOPPED':
                       ('CONTI_ARS440-Stopped',            (dict(shape=None,                    type=EDGE, color=RED,         lw=LW),          )),
  'CONTI_ARS440_STAT': ('CONTI_ARS440-Stationary',         (dict(shape=None,                    type=EDGE, color=RED,         lw=LW),          )),
  'CONTI_ARS430_MOVING':
                       ('CONTI_ARS430-Moving',             (dict(shape='triangle',              type=EDGE, color=GREEN,       lw=LW),          )),
  'CONTI_ARS430_STOPPED':
                       ('CONTI_ARS430-Stopped',            (dict(shape='triangle',              type=EDGE, color=RED,         lw=LW),          )),
  'CONTI_ARS430_STAT': ('CONTI_ARS430-Stationary',         (dict(shape='X',                     type=EDGE, color=RED,         lw=LW),          )),
  'VBOX_OBJ':          ('VBox Object',                     ( dict( shape='triangle',           type=EDGE, color=COL,          lw=LW            ),
                                                                dict( shape='triangle',           type=FACE, color=COL,                 alpha=ALP ) )),
  'NONE_TYPE':         ('NoneType',                        ( dict( shape=None,                 type=None                                       ),))
}
""":type: dict
Container of legend and display style definitions {GroupType<str> : (Legend<str>, (DisplayStyle<dict>,) ), }"""

# setting up guardrail display properties
ShapeProps['NOT_GUARDRAIL'] = 'Not Guardrail object', (dict(shape='?', type=EDGE, color=COL, lw=LW),)
for type_name in gtps.OHL_GUARDRAILS:
  ShapeProps[type_name] = 'CVR3_OHL  - Guardrail', (dict(shape='pentagon', type=EDGE, color=BROWN, lw=LW),
                                                    dict(shape='pentagon', type=FACE, color=BROWN, alpha=ALP))
for type_name in gtps.FUS_GUARDRAILS:
  ShapeProps[type_name] = 'CVR3_FUS  - Guardrail', (dict(shape='pentagon', type=EDGE, color=PURPLE, lw=LW),
                                                    dict(shape='pentagon', type=FACE, color=PURPLE, alpha=ALP))
if '__main__' == __name__:
  """Module test
  """
  import datavis.OpenGLutil
  for Type, (Legend, Shapes) in ShapeProps.iteritems():
    for Props in Shapes:
      shapeName = Props['shape']
      shapeType = Props['type']
      if shapeName not in datavis.OpenGLutil.shapeBuildProps or shapeType not in datavis.OpenGLutil.shapeBuildProps[shapeName]:
        print 'Warning: "%s" shape with "%s" type has no build properties!'%(shapeName, shapeType)
