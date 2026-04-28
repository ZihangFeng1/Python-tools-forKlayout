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
    layer_index1 = layout.insert_layer(pya.LayerInfo(1, 0))
    layer_index2 = layout.insert_layer(pya.LayerInfo(2, 0))
    layer_index3 = layout.insert_layer(pya.LayerInfo(3, 0))

    # add a shape
    pts1 = [pya.DPoint(0, 0), pya.DPoint(10.0 / layout.dbu, 0.0), pya.DPoint(10.0 / layout.dbu, 10.0 / layout.dbu)]
    wg1 = Waveguide(pts1, 4.0 / layout.dbu, 90, 0)
    cell.shapes(layer_index1).insert(wg1.poly())
    t = pya.DCplxTrans(1, 0, False, 10.0 / layout.dbu, 0)
    cell.shapes(layer_index1).insert(wg1.transformed(t))

    pts2 = [pya.DPoint(20.0 / layout.dbu, 0), pya.DPoint(30.0 / layout.dbu, 0.0), pya.DPoint(20.0 / layout.dbu, 20.0 / layout.dbu)]
    wg2 = Waveguide(pts2, 4.0 / layout.dbu, None, None, None, None, 1)
    cell.shapes(layer_index2).insert(wg2.poly())

    pts3 = [pya.DPoint(40.0 / layout.dbu, 0), pya.DPoint(40.0 / layout.dbu, 40.0 / layout.dbu), pya.DPoint(60.0 / layout.dbu, 20.0 / layout.dbu)]
    wg3 = Waveguide(pts3, 4.0 / layout.dbu, None, None, None, None, 1)
    cell.shapes(layer_index3).insert(wg3.poly())

    pts1 = [pya.DPoint(0, 0), pya.DPoint(10.0 / layout.dbu, 0.0), pya.DPoint(10.0 / layout.dbu, 10.0 / layout.dbu)]
    wg1 = Waveguide(pts1, 4.0 / layout.dbu)
    cell.shapes(layer_index1).insert(wg1.poly())

    pts2 = [pya.DPoint(20.0 / layout.dbu, 0), pya.DPoint(30.0 / layout.dbu, 0.0), pya.DPoint(20.0 / layout.dbu, 20.0 / layout.dbu)]
    wg2 = Waveguide(pts2, 4.0 / layout.dbu)
    cell.shapes(layer_index2).insert(wg2.poly())

    pts3 = [pya.DPoint(40.0 / layout.dbu, 0), pya.DPoint(40.0 / layout.dbu, 40.0 / layout.dbu), pya.DPoint(60.0 / layout.dbu, 20.0 / layout.dbu)]
    wg3 = Waveguide(pts3, 4.0 / layout.dbu)
    cell.shapes(layer_index3).insert(wg3.poly())
    pts3_r = round_corners(pts3, 5.0 / layout.dbu)
    wg3r = Waveguide(pts3_r, 4.0 / layout.dbu)
    cell.shapes(layer_index2).insert(wg3r.poly())
    wg3r2 = Waveguide(pts3_r, 4.0 / layout.dbu, None, None, None, None, 1)
    cell.shapes(layer_index1).insert(wg3r2.poly())

    tst = pya.Text('Hello', 0, 0)
    cell.shapes(layer_index1).insert(tst)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
