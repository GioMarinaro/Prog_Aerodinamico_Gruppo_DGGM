#!/bin/bash

cd be153-076_eppler61

python3 ../geoWriting.py <<EOF
mesh
0.006
EOF

gmsh -2 mesh.geo -format su2 && mpirun -n 6 SU2_CFD ../../../config.cfg

rm flow.vtu mesh.su2 restart_flow.dat surface_flow.vtu
