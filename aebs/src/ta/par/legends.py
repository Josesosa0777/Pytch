from groups import Groups
from legendvalues import LegendValues

Legends, Missing = Groups.build_type_params(LegendValues)

if __name__ == '__main__':
  for TypeName in Missing:
    print TypeName
