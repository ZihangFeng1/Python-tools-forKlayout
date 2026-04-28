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
    cell = layout.create_cell("EDG")
    # create a layer
    layer_index1 = layout.insert_layer(pya.LayerInfo(1, 0, 'Grating'))
    layer_index2 = layout.insert_layer(pya.LayerInfo(2, 0, 'Ports'))
    layer_index3 = layout.insert_layer(pya.LayerInfo(3, 0, 'Others'))
    # edg parameter
    thetai = 45.0 * math.pi / 180.0
    thetad = 41.0 * math.pi / 180.0
    w_wg = 0.8 / dbu
    ra = 340.356 / dbu
    wg_spacing = 3.0 / dbu
    output_num = 6
    bend_R = 50.0 / dbu
    output_spacing = 15.0 / dbu
    grating_period = 0.336 / dbu
    grating_width = 0.168 / dbu
    grating_num = 3

    overlap_fpr1 = 0.1 / dbu
    overlap_fpr2 = 0.25 / dbu
    overlap_array = 0.04 / dbu
    overlap_ports = 0.04 / dbu

    p0 = pya.DPoint(0.0, 0.0)
    ex_len = 60.0 / dbu
    ex_len2 = 100.0 / dbu

    grating_pos = []
    filename = "G:\\Gent\\AWG\\EDG\\huannan_grating_parameter.txt"
    with open(filename, "r") as f:
        for line in f:
            data = [float(iter) / dbu for iter in line.split(' ')]
            grating_pos.append(data)
    edg_fnum = len(grating_pos) // 2

    # Circle
    c1 = Circle(pya.DPoint(0.0, ra), ra)
    cell.shapes(layer_index3).insert(c1.poly())
    c2 = Circle(pya.DPoint(0.0, 2.0 * ra), 2.0 * ra)
    cell.shapes(layer_index3).insert(c2.poly())

    # output waveguide
    outP0 = p0 + pya.DPoint(0.0, ra) + pya.DPoint(math.sin(2 * thetad) * ra, math.cos(2 * thetad) * ra)
    dtheta = wg_spacing / ra
    tmp_theta = 2.0 * thetad + ((output_num // 2) - 1) * dtheta
    tmp_y = 0
    output_x = 0  # x coorinate of outputwaveguide
    for iter_i in range(1, output_num + 1):
        pts1 = p0 + pya.DPoint(0.0, ra) + pya.DPoint(math.sin(tmp_theta) * ra, math.cos(tmp_theta) * ra)
        if 1 == iter_i:
            pts2 = pts1 + pya.DPoint(math.sin(tmp_theta / 2.0) * ex_len, math.cos(tmp_theta / 2.0) * ex_len)
            pts3 = pts2 + pya.DPoint(ex_len2, 0)
            output_x = pts3.x
            tmpy = pts3.y
            pts = [pts1, pts2, pts3]
            pts = round_corners(pts, bend_R)
            wg = Waveguide(pts, w_wg)
            cell.shapes(layer_index2).insert(wg.poly())
            wg = Waveguide([p0, pts2], 0)
            cell.shapes(layer_index3).insert(wg.poly())
        else:
            pts2 = pts1 + pya.DPoint(((tmpy + output_spacing) - pts1.y) * math.tan(tmp_theta / 2.0), (tmpy + output_spacing) - pts1.y)
            pts3 = pya.DPoint(output_x, pts2.y)
            tmpy = pts3.y
            pts = [pts1, pts2, pts3]
            pts = round_corners(pts, bend_R)
            wg = Waveguide(pts, w_wg)
            cell.shapes(layer_index2).insert(wg.poly())
            wg = Waveguide([p0, pts2], 0.0)
            cell.shapes(layer_index3).insert(wg.poly())
        tmp_theta = tmp_theta - dtheta

    # input waveguide
    pts1 = p0 + pya.DPoint(0.0, ra) + pya.DPoint(math.sin(2 * thetai) * ra, math.cos(2 * thetai) * ra)
    pts2 = pts1 + pya.DPoint(math.sin(thetai) * ex_len, math.cos(thetai) * ex_len)
    pts3 = pya.DPoint(output_x, pts2.y)
    pts = [pts1, pts2, pts3]
    pts = round_corners(pts, bend_R)
    wg = Waveguide(pts, w_wg)
    cell.shapes(layer_index2).insert(wg.poly())
    wg = Waveguide([p0, pts2], 0.0)
    cell.shapes(layer_index3).insert(wg.poly())

    # EDG Grating

    for iter_i in range(edg_fnum):
        pts = [pya.DPoint(grating_pos[iter_i * 2][0], grating_pos[iter_i * 2][1]),
               pya.DPoint(grating_pos[iter_i * 2 + 1][0], grating_pos[iter_i * 2 + 1][1])]
        wg = Waveguide(pts, grating_width)
        normV = pya.DPoint((pts[0] - pts[1]).y, -(pts[0] - pts[1]).x)
        normV = normV * (1.0 / math.sqrt(normV.sq_abs()))
        for yiter in range(grating_num):
            t = pya.DCplxTrans(1, 0, False, normV * (grating_width / 2.0 + grating_period * yiter))
            cell.shapes(layer_index1).insert(wg.transformed(t))

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
