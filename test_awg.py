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
    cell = layout.create_cell("AWG")
    # create a layer
    layer_index1 = layout.insert_layer(pya.LayerInfo(1, 0, 'FPR'))
    layer_index2 = layout.insert_layer(pya.LayerInfo(2, 0, 'Arryed'))
    layer_index3 = layout.insert_layer(pya.LayerInfo(3, 0, 'Ports'))

    # awg parameter
    narms = 40
    nchannel = 6
    ra = 54.0 / dbu
    theta_da = 0.9
    theta_cs = 1.4
    w_wg = 0.45 / dbu
    w_aperture = 2.0 / dbu
    array_aperture = 1.69 / dbu
    array_w = 0.45 / dbu
    array_R = 50.0 / dbu
    delta_L = 33.117 / dbu

    arrayed_taper = 15.0 / dbu
    w_taper = 22.0 / dbu

    arrayed_spacing = 2.8 / dbu
    ports_spacing = 4.0 / dbu

    overlap_fpr1 = 0.1 / dbu
    overlap_fpr2 = 0.25 / dbu
    overlap_array = 0.04 / dbu
    overlap_ports = 0.04 / dbu

    # add arrayed waveguide
    midn = narms // 2
    start_theta = 90 - theta_da * midn
    round_wg_Len = [0 for i in range(narms)]
    array_Len = [0 for i in range(narms)]  # without consider the difference between the neff_straigth and neff_bend
    manhanttan_dy = 0  # increasing length
    t1 = pya.Trans(pya.DTrans.M90)
    t2 = pya.Trans(0.0, 0.0)
    for iter_i in range(1, narms + 1):
        # add taper arrayed waveguide
        angle = ((iter_i - 1) * theta_da + start_theta) * math.pi / 180.0
        pos1 = pya.DPoint(ra * 2.0 * math.cos(angle), ra * 2.0 * math.sin(angle))
        pos2 = pya.DPoint((ra * 2.0 + arrayed_taper) * math.cos(angle),
                          (ra * 2.0 + arrayed_taper) * math.sin(angle))
        pts = [pos1, pos2]
        width_in = array_aperture
        width_out = array_w
        taper = Taper(pts, width_in, width_out, 'x')
        cell.shapes(layer_index2).insert(taper.poly())

        # add bend taper arrayed waveguide
        # same waveguide spacing
        pts = []
        if iter_i <= midn:
            dw = array_R * (1 - math.sin(angle))
            w1 = arrayed_spacing * (midn + 1 - iter_i) - dw
            lw = w1 / math.cos(angle)
            pos3 = pya.DPoint(lw * math.cos(angle), lw * math.sin(angle))
            pts1 = [pos2, pos3]
            c0 = pya.DPoint(lw * math.cos(angle) - array_R * math.sin(angle),
                            lw * math.sin(angle) + array_R * math.cos(angle))
            c0_manhanttan = c0 + pya.DPoint(array_R * 2.0, -overlap_array)  # manhattan centre
            angle1 = ((iter_i - 1) * theta_da + start_theta) - 90
            arc = linearc(c0, array_R, angle1, 0, 0.5)
            pts = pts1 + arc
            array_Len[iter_i - 1] = lw - arrayed_taper - 2.0 * ra + array_R * (-angle1) / 180.0 * math.pi
        elif iter_i >= midn + 2:
            dw = array_R * (1 - math.sin(angle))
            w1 = arrayed_spacing * (iter_i - midn - 1) - dw
            lw = w1 / math.sin(angle - math.pi / 2.0)
            pos3 = pya.DPoint(lw * math.cos(angle), lw * math.sin(angle))
            pts1 = [pos2, pos3]
            c0 = pya.DPoint(lw * math.cos(angle) + array_R * math.cos(angle - math.pi / 2.0),
                            lw * math.sin(angle) + array_R * math.sin(angle - math.pi / 2.0))
            c0_manhanttan = c0 + pya.DPoint(0.0, -overlap_array)  # manhattan centre
            angle1 = -(180 - (((iter_i - 1) * theta_da + start_theta) - 90))
            arc = linearc(c0, array_R, angle1, -180, 0.5)
            pts = pts1 + arc
            array_Len[iter_i - 1] = lw - arrayed_taper - 2.0 * ra + array_R * (180.0 + angle1) / 180.0 * math.pi
        else:
            angle = (90 - theta_da) * math.pi / 180.0
            dw = array_R * (1 - math.sin(angle))
            w1 = arrayed_spacing - dw
            lw = w1 / math.cos(angle)
            pos3 = pya.DPoint(0, lw)
            pts1 = [pos2, pos3]
            pts = pts1
            array_Len[iter_i - 1] = lw - arrayed_taper - 2.0 * ra
            c0_manhanttan = pya.DPoint(array_R, lw - overlap_array)  # manhattan centre
        wg1 = Waveguide(pts, array_w, None, 180)
        cell.shapes(layer_index2).insert(wg1.poly())
        round_wg_Len[iter_i - 1] = array_Len[iter_i - 1]
        # add manhattan
        if 1 == iter_i:
            arc = linearc(c0_manhanttan, array_R, 180.0, 90.0, 0.5)
            pts = arc
            array_Len[iter_i - 1] = round_wg_Len[iter_i - 1] + math.pi / 2.0 * array_R
            t2 = pya.Trans(c0_manhanttan.x * 2.0, 0.0)
        else:
            pts1 = [pya.DPoint(c0_manhanttan.x - array_R, c0_manhanttan.y)]
            manhanttan_dy = delta_L / 2.0 - (round_wg_Len[iter_i - 1] - round_wg_Len[iter_i - 2]) - arrayed_spacing + manhanttan_dy
            c0_manhanttan.y = c0_manhanttan.y + manhanttan_dy
            arc = linearc(c0_manhanttan, array_R, 180.0, 90.0, 0.5)
            pts2 = [pya.DPoint(c0_manhanttan.x + arrayed_spacing * (iter_i - 1), c0_manhanttan.y + array_R)]
            pts = pts1 + arc + pts2
            array_Len[iter_i - 1] = round_wg_Len[iter_i - 1] + (iter_i - 1) * arrayed_spacing + manhanttan_dy + math.pi / 2.0 * array_R
        wg = Waveguide(pts, array_w, 180, 90)
        cell.shapes(layer_index2).insert(wg.poly())
        cell.shapes(layer_index2).insert(wg.poly().transformed(t1).transformed(t2))
        cell.shapes(layer_index2).insert(wg1.poly().transformed(t1).transformed(t2))
        cell.shapes(layer_index2).insert(taper.poly().transformed(t1).transformed(t2))

    # check array length difference
    for index in range(len(array_Len) - 1):
        print((array_Len[index + 1] - array_Len[index]) * 2)

    # add Free Propagation Region
    centre = pya.DPoint(0, 0)
    angle = 57.0
    arc1 = linearc(centre, ra * 2.0 + overlap_fpr1, 90.0 - angle / 2.0, 90.0 + angle / 2.0, 1.0)
    centre = pya.DPoint(0, ra)
    angle2 = 54.0
    arc2 = linearc(centre, ra + overlap_fpr2, -90 - angle2 / 2.0, -90.0 + angle2 / 2.0)
    arc = arc1 + arc2
    fpr = pya.DPolygon(arc)
    cell.shapes(layer_index1).insert(pya.Polygon.from_dpoly(fpr))
    cell.shapes(layer_index1).insert(pya.Polygon.from_dpoly(fpr).transformed(t1).transformed(t2))

    # add taper ports waveguide
    centre = pya.DPoint(0, ra)
    midn = nchannel // 2
    start_theta = -90 - theta_cs * midn * 2.0
    start_theta2 = -90 - theta_cs * midn
    port_y = 50.0 / dbu  # ports extension_y direction
    port_x = 100.0 / dbu  # ports extension_x direction
    xmin = 0
    for iter_i in range(1, nchannel + 1):
        angle = ((iter_i - 1) * theta_cs * 2.0 + start_theta) * math.pi / 180.0
        angle2 = ((iter_i - 1) * theta_cs + start_theta2) * math.pi / 180.0
        pos1 = pya.DPoint(ra * math.cos(angle), ra * math.sin(angle)) + centre
        pos2 = pya.DPoint(w_taper * math.cos(angle2), w_taper * math.sin(angle2)) + pos1
        pts = [pos1, pos2]
        width_in = w_aperture
        width_out = w_wg
        taper = Taper(pts, width_in, width_out, 'x', 0.1)
        cell.shapes(layer_index3).insert(taper.poly())
        cell.shapes(layer_index3).insert(taper.poly().transformed(t1).transformed(t2))
        if 1 == iter_i:
            pts = [pya.DPoint(pos2.x + overlap_ports / math.tan(angle2), pos2.y + overlap_ports),
                   pya.DPoint(pos2.x - port_y / math.tan(angle2), pos2.y - port_y),
                   pya.DPoint(pos2.x - port_y / math.tan(angle2) - port_x, pos2.y - port_y)]
            xmin = pos2.x - port_y / math.tan(angle2) - port_x
            pts = round_corners(pts, array_R)
        else:
            tmp_y = port_y + (iter_i - 1) * ports_spacing
            pts = [pya.DPoint(pos2.x + overlap_ports / math.tan(angle2), pos2.y + overlap_ports),
                   pya.DPoint(pos2.x - tmp_y / math.tan(angle2), pos2.y - tmp_y),
                   pya.DPoint(xmin, pos2.y - tmp_y)]
            pts = round_corners(pts, array_R)
        wg = Waveguide(pts, w_wg)
        cell.shapes(layer_index3).insert(wg.poly())
        cell.shapes(layer_index3).insert(wg.poly().transformed(t1).transformed(t2))

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
