cd ..
cd ..
cd schema2dot
python C:/ToolChainRepo/schema2dot/schema2dot.py < C:/KBData/test_scripts/tets_schema.sql > C:/KBData/test_scripts/can.dot
C:\KBApps\Graphviz2.38\bin\dot.exe -Grankdir=LR -Granksep=3.0 -Nshape=plaintext -Tpng -oC:\KBData\test_scripts\can_sql.png C:\KBData\test_scripts\can.dot






