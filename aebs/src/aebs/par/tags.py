default = {
  'sensor type': [
    'radar', 'lidar', 'laser', 'camera', 'infrared camera',
  ],
  'sensor': [
    'CVR2', 'CVR3', 'AC100', 'ESR', 'IBEO', 'S-Cam', 'Iteris', 'CANape',
  ],
  'function': [
    'object tracking', 'lane tracking', 'SDF', 'association', 'fusion',
    'object following', 'pedestrian detection', 'traffic sign recognition',
    'path prediction',
  ],
  'application': [
    'AEBS', 'ACC', 'LDW', 'LKS',
  ],
  'association defect': [
    'late', 'dropout', 'replaced', 'missing', 'wrong',
  ],
}
""":type: dict
{taggroup<str>: [tag<str>]}"""
