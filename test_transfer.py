import pya
import os

if __name__ == "__main__":
    layout = pya.Layout()
    # set the database unit (shown as an example, the default is 0.001)
    layout.dbu = 0.001
    # create a cell
    cell = layout.create_cell("TOP")
    # create a layer
    layer_index1 = layout.insert_layer(pya.LayerInfo(10, 0))
    layer_index2 = layout.insert_layer(pya.LayerInfo(11, 0))

    pt1 = pya.Point(-10, -10)
    pt2 = pya.Point(-10, 10)
    pt3 = pya.Point(100, 25)
    pt4 = pya.Point(100, -25)
    taper = pya.Polygon([pt1, pt2, pt3, pt4])
    start_angle = 0
    t1 = pya.Trans(pya.Trans.M90)
    t2 = pya.Trans(0.0, 0.0)
    trans_taper = taper.transformed(t1).transformed(t2)
    cell.shapes(layer_index1).insert(taper)
    cell.shapes(layer_index2).insert(trans_taper)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
