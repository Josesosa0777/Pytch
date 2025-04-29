from .groups import Groups
from .shapeprops import ShapeProps

ShapeLegends, Missing = Groups.build_type_params(ShapeProps)

if __name__ == '__main__':
  for TypeName in Missing:
    print TypeName
