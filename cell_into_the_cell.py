# Cell in cell instantiation

import pya
import os

if __name__ == "__main__":
    layout = pya.Layout()
    # get the current layout
    layer_align = layout.insert_layer(pya.LayerInfo(10, 0))
    cell1 = layout.create_cell("TOP")
    cell2 = layout.create_cell("BOTTOM")
    cell2.shapes(layer_align).insert(pya.Box(0, 0, 400, 400))
    array1 = pya.CellInstArray(cell2.cell_index, pya.Trans(0, 0), pya.Point(500, 0), pya.Point(0, 0), 10, 1)
    cell1.insert(array1)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
