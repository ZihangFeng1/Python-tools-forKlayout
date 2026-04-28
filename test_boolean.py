import pya
import os
from waveguide import *

if __name__ == "__main__":
    layout = pya.Layout()
    # set the database unit (shown as an example, the default is 0.001)
    layout.dbu = 0.001
    # create a cell
    cell = layout.create_cell("TOP")
    # create a layer
    layer_index1 = layout.insert_layer(pya.LayerInfo(10, 0))
    layer_index2 = layout.insert_layer(pya.LayerInfo(11, 0))
    layer_index3 = layout.insert_layer(pya.LayerInfo(12, 0))
    pt1 = pya.DPoint(-10 / layout.dbu, -10 / layout.dbu)
    pt2 = pya.DPoint(-10 / layout.dbu, 10 / layout.dbu)
    pts = [pt1, pt2]
    wg1 = Waveguide(pts, 1.0 / layout.dbu)
    wg2 = Waveguide(pts, 2.0 / layout.dbu)
    poly1 = wg1.poly()
    poly2 = wg2.poly()
    cell.shapes(layer_index1).insert(poly1)
    cell.shapes(layer_index2).insert(poly2)
    ep = pya.EdgeProcessor()
    out = ep.boolean_p2p([poly1], [poly2], pya.EdgeProcessor.ModeBNotA, False, False)
    for p in out:
        cell.shapes(layer_index3).insert(p)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
