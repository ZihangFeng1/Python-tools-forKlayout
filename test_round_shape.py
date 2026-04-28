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
    cell = layout.create_cell("TOP")
    # create a layer

    layer_index1 = layout.insert_layer(pya.LayerInfo(1, 0, 'path'))
    layer_index2 = layout.insert_layer(pya.LayerInfo(10, 0, 'round_path'))
    for iter_i in range(18, 19):
        pts1 = [pya.DPoint(20.0 * iter_i / layout.dbu, 0),
                pya.DPoint(5.0 / layout.dbu + 20.0 * iter_i / layout.dbu, 0),
                pya.DPoint(10.0 / layout.dbu + 20.0 * iter_i / layout.dbu, 0),
                pya.DPoint((10.0 / layout.dbu * math.cos(iter_i * math.pi / 36.0) + 20.0 * iter_i / layout.dbu) + 10.0 / layout.dbu,
                            10.0 / layout.dbu * math.sin(iter_i * math.pi / 36.0))]
        radius = 5.0 / layout.dbu
        pts2 = round_corners(pts1, radius)
        path2 = pya.DPath(pts2, 0)
        print(path2.length())
        cell.shapes(layer_index2).insert(pya.Path.from_dpath(path2))
        cell.shapes(layer_index1).insert(pya.Path.from_dpath(pya.DPath(pts1, 0)))

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
