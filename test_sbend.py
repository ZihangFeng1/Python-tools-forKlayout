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

    # p1 = DPoint.new(0.0,0.0)
    # radius = 10.0/layout.dbu
    # start_angle = 270.0
    # span_angle = 90.0
    # pts = linearc_one_point_two_angle(p1,radius,start_angle,span_angle)
    # wg1 = Waveguide.new(pts,width,90,0)
    # cell.shapes(layer_index2).insert(wg1.poly)

    for iter_i in [20]:
        width = 2.0 / layout.dbu
        radius = 5.0 / layout.dbu
        len_seg = 10.0 / layout.dbu
        dx = 20.0 / layout.dbu
        dy = 0.0 / layout.dbu
        start_x = 0
        start_y = 60.0 / layout.dbu * iter_i
        dir1 = 0
        dir2 = iter_i * 10.0
        p0 = pya.DPoint(start_x - len_seg * math.cos(dir1 / 180.0 * math.pi),
                         start_y - len_seg * math.sin(dir1 / 180.0 * math.pi))
        p1 = pya.DPoint(start_x, start_y)
        dir1 = line_angle(p0, p1) / math.pi * 180.0
        p2 = pya.DPoint(dx + start_x, dy + start_y)
        p3 = pya.DPoint(len_seg * math.cos(dir2 / 180.0 * math.pi) + dx + start_x,
                         len_seg * math.sin(dir2 / 180.0 * math.pi) + dy + start_y)
        dir2 = line_angle(p2, p3) / math.pi * 180.0
        pts1 = [p0, p1]
        pts2 = [p2, p3]
        pts3 = sbend(p1, dir1, p2, dir2, radius, 5)
        pts = pts1 + pts3 + pts2
        wg1 = Waveguide(pts, width)
        cell.shapes(layer_index1).insert(wg1.poly())

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
