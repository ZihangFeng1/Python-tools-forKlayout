# Awg_class.py - converted from Ruby to Python using Klayout pya API
import pya
import math
import os
from waveguide import *


class Awg:
    def __init__(self, narms=34,
                 nchannel=8,
                 ra=54.0,
                 theta_da=1.06,
                 theta_cs=1.406,
                 w_wg=0.8,
                 w_aperture=1.9,
                 array_aperture=1.5,
                 array_w=0.8,
                 array_R=50.0,
                 delta_L=17.27,
                 arrayed_taper=15.0,
                 w_taper=22.0,
                 arrayed_spacing=3.0,
                 ports_spacing=100.0,
                 overlap_fpr1=0.1,
                 overlap_fpr2=0.25,
                 overlap_array=0.04,
                 overlap_ports=0.04,
                 fsr_angle1=57.0,
                 fsr_angle2=53.0,
                 layer_fsr=None,
                 layer_arrayed=None,
                 layer_ports=None,
                 centre_line=None,
                 straight_neff=1.0,
                 bend_neff=1.0,
                 dbu=None):
        if dbu is None:
            self.dbu = pya.CellView.active().layout().dbu
        else:
            self.dbu = dbu
        self.narms = narms
        self.nchannel = nchannel
        self.ra = ra / self.dbu
        self.theta_da = theta_da
        self.theta_cs = theta_cs
        self.w_wg = w_wg / self.dbu
        self.w_aperture = w_aperture / self.dbu
        self.array_aperture = array_aperture / self.dbu
        self.array_w = array_w / self.dbu
        self.array_R = array_R / self.dbu
        self.delta_L = delta_L / self.dbu

        self.arrayed_taper = arrayed_taper / self.dbu
        self.w_taper = w_taper / self.dbu

        self.arrayed_spacing = arrayed_spacing / self.dbu
        self.ports_spacing = ports_spacing / self.dbu

        self.overlap_fpr1 = overlap_fpr1 / self.dbu
        self.overlap_fpr2 = overlap_fpr2 / self.dbu
        self.overlap_array = overlap_array / self.dbu
        self.overlap_ports = overlap_ports / self.dbu

        self.fsr_angle1 = fsr_angle1
        self.fsr_angle2 = fsr_angle2

        if layer_fsr is None:
            layer_fsr = pya.CellView.active().layout().layer(1, 0)
        if layer_arrayed is None:
            layer_arrayed = pya.CellView.active().layout().layer(2, 0)
        if layer_ports is None:
            layer_ports = pya.CellView.active().layout().layer(3, 0)
        self.layer_fsr = layer_fsr
        self.layer_arrayed = layer_arrayed
        self.layer_ports = layer_ports

        self.centre_line = centre_line

        self.straight_neff = straight_neff
        self.bend_neff = bend_neff
        self.ports = []

    def shapes(self, cell):
        dbu = self.dbu
        narms = self.narms
        nchannel = self.nchannel
        ra = self.ra
        theta_da = self.theta_da
        theta_cs = self.theta_cs
        w_wg = self.w_wg
        w_aperture = self.w_aperture
        array_aperture = self.array_aperture
        array_w = self.array_w
        array_R = self.array_R
        delta_L = self.delta_L

        arrayed_taper = self.arrayed_taper
        w_taper = self.w_taper
        arrayed_spacing = self.arrayed_spacing
        ports_spacing = self.ports_spacing

        overlap_fpr1 = self.overlap_fpr1
        overlap_fpr2 = self.overlap_fpr2
        overlap_array = self.overlap_array
        overlap_ports = self.overlap_ports

        layer_index1 = self.layer_fsr
        layer_index2 = self.layer_arrayed
        layer_index3 = self.layer_ports
        self.ports = []
        if self.centre_line:
            layer_index_c2 = self.active_layout.layer(2, 1)
            layer_index_c3 = self.active_layout.layer(3, 1)

        midn = narms // 2
        start_theta = 90 - theta_da * midn
        round_wg_Len = [0] * narms
        array_Len = [0] * narms
        manhanttan_dy = 0
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
            pts_bend = []
            if iter_i <= midn:
                dw = array_R * (1 - math.sin(angle))
                w1 = arrayed_spacing * (midn + 1 - iter_i) - dw
                lw = w1 / math.cos(angle)
                pos3 = pya.DPoint(lw * math.cos(angle), lw * math.sin(angle))
                pts1 = [pos2, pos3]
                c0 = pya.DPoint(lw * math.cos(angle) - array_R * math.sin(angle),
                                lw * math.sin(angle) + array_R * math.cos(angle))
                c0_manhanttan = c0 + pya.DPoint(array_R * 2.0, 0.0)
                angle1 = ((iter_i - 1) * theta_da + start_theta) - 90
                arc = linearc(c0, array_R, angle1, 0, 0.5)
                arc.append(pya.DPoint(arc[-1].x, arc[-1].y + overlap_array))
                pts_bend = pts1 + arc
                array_Len[iter_i - 1] = lw - arrayed_taper - 2.0 * ra + \
                    (array_R * (-angle1) / 180.0 * math.pi) * self.bend_neff / self.straight_neff
            elif iter_i >= midn + 2:
                dw = array_R * (1 - math.sin(angle))
                w1 = arrayed_spacing * (iter_i - midn - 1) - dw
                lw = w1 / math.sin(angle - math.pi / 2.0)
                pos3 = pya.DPoint(lw * math.cos(angle), lw * math.sin(angle))
                pts1 = [pos2, pos3]
                c0 = pya.DPoint(lw * math.cos(angle) + array_R * math.cos(angle - math.pi / 2.0),
                                lw * math.sin(angle) + array_R * math.sin(angle - math.pi / 2.0))
                c0_manhanttan = c0
                angle1 = -(180 - (((iter_i - 1) * theta_da + start_theta) - 90))
                arc = linearc(c0, array_R, angle1, -180, 0.5)
                arc.append(pya.DPoint(arc[-1].x, arc[-1].y + overlap_array))
                pts_bend = pts1 + arc
                array_Len[iter_i - 1] = lw - arrayed_taper - 2.0 * ra + \
                    (array_R * (180.0 + angle1) / 180.0 * math.pi) * self.bend_neff / self.straight_neff
            else:
                angle_mid = (90 - theta_da) * math.pi / 180.0
                dw = array_R * (1 - math.sin(angle_mid))
                w1 = arrayed_spacing - dw
                lw = w1 / math.cos(angle_mid)
                pos3 = pya.DPoint(0, lw)
                pos4 = pya.DPoint(pos3.x, pos3.y + overlap_array)
                pts1 = [pos2, pos3, pos4]
                pts_bend = pts1
                array_Len[iter_i - 1] = lw - arrayed_taper - 2.0 * ra
                c0_manhanttan = pya.DPoint(array_R, lw)

            wg1 = Waveguide(pts_bend, array_w, None, 180, None, 90.0)
            cell.shapes(layer_index2).insert(wg1.poly())
            round_wg_Len[iter_i - 1] = array_Len[iter_i - 1]
            array_Len[iter_i - 1] = wg1.wg_length

            # add manhattan
            if 1 == iter_i:
                pts1_m = [pya.DPoint(c0_manhanttan.x - array_R, c0_manhanttan.y)]
                manhanttan_dy = 0
                c0_manhanttan.y = c0_manhanttan.y + manhanttan_dy + overlap_array
                arc_m = linearc(c0_manhanttan, array_R, 180.0, 90.0, 0.5)
                pts_m = pts1_m + arc_m
                t2 = pya.Trans(c0_manhanttan.x * 2.0, 0.0)
            else:
                pts1_m = [pya.DPoint(c0_manhanttan.x - array_R, c0_manhanttan.y)]
                manhanttan_dy = delta_L / 2.0 - (round_wg_Len[iter_i - 1] - round_wg_Len[iter_i - 2]) \
                    - arrayed_spacing + manhanttan_dy
                c0_manhanttan.y = c0_manhanttan.y + manhanttan_dy + overlap_array
                arc_m = linearc(c0_manhanttan, array_R, 180.0, 90.0, 0.5)
                pts2_m = [pya.DPoint(c0_manhanttan.x + arrayed_spacing * (iter_i - 1),
                                     c0_manhanttan.y + array_R)]
                pts_m = pts1_m + arc_m + pts2_m

            wg = Waveguide(pts_m, array_w, 180, 90, 90.0, 0.0)
            array_Len[iter_i - 1] = array_Len[iter_i - 1] + wg.wg_length
            cell.shapes(layer_index2).insert(wg.poly())
            cell.shapes(layer_index2).insert(wg.poly().transformed(t1).transformed(t2))
            cell.shapes(layer_index2).insert(wg1.poly().transformed(t1).transformed(t2))
            cell.shapes(layer_index2).insert(taper.poly().transformed(t1).transformed(t2))

            if self.centre_line:
                newpts = []
                pt_end = pts_m[-1]
                newpts.insert(0, pt_end)
                for idx in range(len(pts_m) - 1):
                    newpts.insert(idx, pts_m[idx])
                    newpts.insert(-1 - idx, pya.DPoint(2.0 * pt_end.x - pts_m[idx].x, pts_m[idx].y))
                wg03 = Waveguide(newpts, 0)
                cell.shapes(layer_index_c2).insert(wg03.poly())

        # check array length difference
        for index in range(len(array_Len) - 1):
            print((array_Len[index + 1] - array_Len[index]) * 2)

        # add Free Propagation Region
        centre = pya.DPoint(0, 0)
        angle_fpr = self.fsr_angle1
        arc1 = linearc(centre, ra * 2.0 + overlap_fpr1, 90.0 - angle_fpr / 2.0, 90.0 + angle_fpr / 2.0, 1.0)
        centre = pya.DPoint(0, ra)
        angle2_fpr = self.fsr_angle2
        arc2 = linearc(centre, ra + overlap_fpr2, -90 - angle2_fpr / 2.0, -90.0 + angle2_fpr / 2.0)
        arc_fpr = arc1 + arc2
        fpr = pya.DPolygon(arc_fpr)
        cell.shapes(layer_index1).insert(pya.Polygon.from_dpoly(fpr))
        cell.shapes(layer_index1).insert(pya.Polygon.from_dpoly(fpr).transformed(t1).transformed(t2))

        # add taper ports waveguide
        centre_port = pya.DPoint(0, ra)
        midn_port = nchannel // 2
        start_theta_port = -90 - theta_cs * midn_port * 2.0
        start_theta2 = -90 - theta_cs * midn_port
        port_y = array_R
        port_x = 100.0 / dbu
        xmin = 0
        for iter_i in range(1, nchannel + 1):
            angle_p = ((iter_i - 1) * theta_cs * 2.0 + start_theta_port) * math.pi / 180.0
            angle2_p = ((iter_i - 1) * theta_cs + start_theta2) * math.pi / 180.0
            pos1 = pya.DPoint(ra * math.cos(angle_p), ra * math.sin(angle_p)) + centre_port
            pos2 = pya.DPoint(w_taper * math.cos(angle2_p), w_taper * math.sin(angle2_p)) + pos1
            pts_port = [pos1, pos2]
            width_in_port = w_aperture
            width_out_port = w_wg
            taper_port = Taper(pts_port, width_in_port, width_out_port, 'x')
            cell.shapes(layer_index3).insert(taper_port.poly())
            cell.shapes(layer_index3).insert(taper_port.poly().transformed(t1).transformed(t2))
            if 1 == iter_i:
                pts_route = [pya.DPoint(pos2.x + overlap_ports / math.tan(angle2_p),
                                        pos2.y + overlap_ports),
                             pya.DPoint(pos2.x - port_y / math.tan(angle2_p), pos2.y - port_y),
                             pya.DPoint(pos2.x - port_y / math.tan(angle2_p) - array_R * 2.0,
                                        pos2.y - port_y),
                             pya.DPoint(pos2.x - port_y / math.tan(angle2_p) - array_R * 2.0,
                                        pos2.y - port_y + (nchannel - iter_i) * ports_spacing),
                             pya.DPoint(pos2.x - port_y / math.tan(angle2_p) - array_R * 2.0 - port_x,
                                        pos2.y - port_y + (nchannel - iter_i) * ports_spacing)]
                xmin = pts_route[-1].x
                pts_route = round_corners(pts_route, array_R)
            else:
                tmp_y = port_y + (iter_i - 1) * arrayed_spacing
                pts_route = [pya.DPoint(pos2.x + overlap_ports / math.tan(angle2_p),
                                        pos2.y + overlap_ports),
                             pya.DPoint(pos2.x - tmp_y / math.tan(angle2_p), pos2.y - tmp_y),
                             pya.DPoint(xmin + port_x - (iter_i - 1) * arrayed_spacing,
                                        pos2.y - tmp_y),
                             pya.DPoint(xmin + port_x - (iter_i - 1) * arrayed_spacing,
                                        pos2.y - tmp_y + (nchannel - iter_i) * ports_spacing),
                             pya.DPoint(xmin, pos2.y - tmp_y + (nchannel - iter_i) * ports_spacing)]
                pts_route = round_corners(pts_route, array_R)

            wg_port = Waveguide(pts_route, w_wg)
            cell.shapes(layer_index3).insert(wg_port.poly())
            cell.shapes(layer_index3).insert(wg_port.poly().transformed(t1).transformed(t2))
            self.ports.append(Ports(width=w_wg,
                                    direction=line_angle(pts_route[-2], pts_route[-1]),
                                    face_angle=line_angle(pts_route[-2], pts_route[-1]) + math.pi / 2.0,
                                    point=pts_route[-1]))
            tpoint = pya.DTrans.from_itrans(t2).trans(pya.DTrans.from_itrans(t1).trans(pts_route[-1]))
            self.ports.append(Ports(width=w_wg,
                                    direction=math.pi + line_angle(pts_route[-2], pts_route[-1]),
                                    face_angle=math.pi + line_angle(pts_route[-2], pts_route[-1]) + math.pi / 2.0,
                                    point=tpoint))
            if self.centre_line:
                wg01 = Waveguide(pts_route, 0)
                cell.shapes(layer_index_c3).insert(wg01.poly())
                cell.shapes(layer_index_c3).insert(wg01.poly().transformed(t1).transformed(t2))

    def get_ports(self):
        return self.ports


if __name__ == "__main__":
    layout = pya.Layout()
    dbu = 0.001
    layout.dbu = dbu

    cell = layout.create_cell("AWG")
    awg = Awg(dbu=dbu, layer_fsr=layout.layer(1, 0), layer_arrayed=layout.layer(2, 0),
              layer_ports=layout.layer(3, 0))
    awg.nchannel = 6
    awg.shapes(cell)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
