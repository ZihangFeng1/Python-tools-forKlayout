# HalfWaveRing_class.py - converted from Ruby to Python using Klayout pya API
import pya
import math
import os
from waveguide import *


class HalfWaveRing:
    def __init__(self, radius=50.0,
                 width=0.45,
                 coupler_length=30.0,
                 gap=0.2,
                 extension_length=100.0,
                 layer_ring=None,
                 layer_coupler=None,
                 centre_line=None,
                 dbu=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if layer_ring is None:
            layer_ring = pya.CellView.active().layout().layer(1, 0)
        if layer_coupler is None:
            layer_coupler = pya.CellView.active().layout().layer(2, 0)

        self.dbu = dbu
        self.radius = radius / self.dbu
        self.width = width / self.dbu
        self.coupler_length = coupler_length / self.dbu
        self.gap = gap / self.dbu
        self.extension_length = extension_length / self.dbu
        self.layer_ring = layer_ring
        self.layer_coupler = layer_coupler
        self.centre_line = centre_line
        self.ports = []

    def shapes(self, cell):
        self.ports = []
        pts = [pya.DPoint(0.0, 0.0),
               pya.DPoint(self.extension_length + self.coupler_length + self.extension_length, 0.0)]
        self.ports.append(Ports(width=self.width,
                                direction=line_angle(pts[1], pts[0]),
                                face_angle=line_angle(pts[1], pts[0]) + math.pi / 2.0,
                                point=pts[0]))
        self.ports.append(Ports(width=self.width,
                                direction=math.pi + line_angle(pts[1], pts[0]),
                                face_angle=math.pi + line_angle(pts[1], pts[0]) + math.pi / 2.0,
                                point=pts[1]))
        wg1 = Waveguide(pts, self.width)
        cell.shapes(self.layer_coupler).insert(wg1.poly())
        if self.centre_line:
            layercentre = pya.CellView.active().layout().layer(self.layer_coupler + 1, 1)
            wg1_line = Waveguide(pts, 0)
            cell.shapes(layercentre).insert(wg1_line.poly())

        gap_total = self.width + self.gap
        pts = [pya.DPoint(self.extension_length, gap_total),
               pya.DPoint(self.extension_length + self.coupler_length, gap_total)]
        wg2 = Waveguide(pts, self.width)
        cell.shapes(self.layer_coupler).insert(wg2.poly())
        if self.centre_line:
            wg2_line = Waveguide(pts, 0)
            cell.shapes(layercentre).insert(wg2_line.poly())

        pts = [pya.DPoint(self.extension_length, gap_total * 2.0),
               pya.DPoint(self.extension_length + self.coupler_length + self.radius, gap_total * 2.0),
               pya.DPoint(self.extension_length + self.coupler_length + self.radius,
                          gap_total * 2.0 + self.radius * 2.0),
               pya.DPoint(self.extension_length - self.radius, gap_total * 2.0 + self.radius * 2.0),
               pya.DPoint(self.extension_length - self.radius, gap_total * 2.0),
               pya.DPoint(self.extension_length, gap_total * 2.0)]
        pts = round_corners(pts, self.radius)
        wg3 = Waveguide(pts, self.width, None, None)
        cell.shapes(self.layer_ring).insert(wg3.poly())
        if self.centre_line:
            wg3_line = Waveguide(pts, 0)
            cell.shapes(layercentre).insert(wg3_line.poly())

    def get_ports(self):
        return self.ports


if __name__ == "__main__":
    from GratingCoupler_class import GratingCoupler

    layout = pya.Layout()
    dbu = 0.001
    layout.dbu = dbu

    ltot = 377.0
    gap = [0.45, 0.45, 0.6, 0.6]
    L = [19.0, 21.5, 43.5, 49]
    radius = [(ltot - 2.0 * x) / (2.0 * math.pi) for x in L]
    cell = []
    cell.append(layout.create_cell("half_wave_ring_gap0.45_L19"))
    cell.append(layout.create_cell("half_wave_ring_gap0.45_L21.5"))
    cell.append(layout.create_cell("half_wave_ring_gap0.6_L43.5"))
    cell.append(layout.create_cell("half_wave_ring_gap0.6_L49"))

    ring = HalfWaveRing(dbu=dbu, layer_ring=layout.layer(1, 0), layer_coupler=layout.layer(2, 0))
    ring.centre_line = True

    # Grating Coupler
    gccell = layout.create_cell("Grating_Coupler_340nm")
    gcoupler = GratingCoupler(dbu=dbu, layer_grating=layout.layer(1, 0))
    gcoupler.width_in = 0.45 / dbu
    gcoupler.period = 0.64 / dbu
    gcoupler.duty = 0.38
    gcoupler.shapes(gccell)

    for iter_i in range(len(cell)):
        ring.radius = radius[iter_i] / dbu
        ring.width = 0.45 / dbu
        ring.coupler_length = L[iter_i] / dbu
        ring.gap = gap[iter_i] / dbu
        ring.shapes(cell[iter_i])

        overlap = 0.1 / dbu
        for port in ring.ports:
            angle = port.direction - gcoupler.ports[0].direction - math.pi
            tmpover = pya.DPoint(overlap * math.cos(angle), overlap * math.sin(angle))
            disp = port.point - gcoupler.ports[0].point - tmpover
            t = pya.CplxTrans(1.0, angle / math.pi * 180.0, False, disp)
            tmp = pya.CellInstArray(gccell.cell_index, t)
            cell[iter_i].insert(tmp)

    topcell = layout.create_cell("Top")
    dy = 200.0 / dbu
    for iter_i in range(len(cell)):
        t = pya.CplxTrans(1.0, 0, False, 0.0, iter_i * dy)
        tmp = pya.CellInstArray(cell[iter_i].cell_index, t)
        topcell.insert(tmp)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
