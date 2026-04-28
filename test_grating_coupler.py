import pya
import math
import os
from waveguide import *

# creat awg with same waveguide spacing

if __name__ == "__main__":
    layout = pya.Layout()
    # set the database unit (shown as an example, the default is 0.001)
    dbu = 0.001
    layout.dbu = dbu
    # create a cell
    cell = layout.create_cell("Grating_coupler")
    # create a layer
    layer_index1 = layout.insert_layer(pya.LayerInfo(1, 0, 'Grating'))

    # awg parameter
    period = 0.63 / dbu
    duty = 0.38
    width_in = 0.45 / dbu
    width_out = 10.0 / dbu
    grating_length = 15 / dbu
    behind_length = 5.0 / dbu
    taper_length = 150.0 / dbu
    p0 = pya.DPoint(0.0, 0.0)

    pts = [pya.DPoint(0.0, 0.0), pya.DPoint(taper_length, 0.0)]
    taper = Taper(pts, width_in, width_out, 'x')
    cell.shapes(layer_index1).insert(taper.poly())

    grtg_len = 0
    while grtg_len < grating_length:
        pts = [pya.DPoint(taper_length + grtg_len + period * (1 - duty), 0.0),
               pya.DPoint(taper_length + grtg_len + period, 0.0)]
        wg = Waveguide(pts, width_out)
        cell.shapes(layer_index1).insert(wg.poly())
        grtg_len = grtg_len + period

    pts = [pya.DPoint(taper_length + grtg_len + period * (1 - duty), 0.0),
           pya.DPoint(taper_length + grtg_len + behind_length, 0.0)]
    wg = Waveguide(pts, width_out)
    cell.shapes(layer_index1).insert(wg.poly())

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
