# Draw boxes in a layout

import pya
import os

if __name__ == "__main__":
    layout = pya.Layout()
    # set the database unit (shown as an example, the default is 0.001)
    layout.dbu = 0.001

    # create a cell
    cell = layout.create_cell("TOP")

    # create a layer
    layer_index = layout.insert_layer(pya.LayerInfo(10, 0, 'box'))

    # add a shape
    for alength in range(1, 11):
        box = pya.Box(1000 * (alength - 1), 0, 1000 * alength, 2000 * alength)
        cell.shapes(layer_index).insert(box)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
