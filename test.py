import pya
import math
import os
from waveguide import *

if __name__ == "__main__":
    layout = pya.Layout()
    # set the database unit (shown as an example, the default is 0.001)
    dbu = 0.001
    layout.dbu = dbu
    # create a cell
    cell = layout.create_cell("top")
    layer_index = layout.insert_layer(pya.LayerInfo(1, 0, 'FPR'))

    pts = [pya.DPoint(0.0, 0.0), pya.DPoint(1000.0, 1000.0)]
    width = 500.0
    wg = Waveguide(pts, width)
    wg.start_face_angle = 73.0
    wg.end_face_angle = 73.0
    print(wg.start_face_angle / math.pi * 180.0)
    cell.shapes(layer_index).insert(wg.poly())

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
