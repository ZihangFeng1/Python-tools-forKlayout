# Cpw_class.py - converted from Ruby to Python using Klayout pya API
import pya
import math
import os
from waveguide import *


class Cpw_straight:
    def __init__(self, cpw_gap=18.0,
                 cpw_swidth=10.0,
                 cpw_width=350.0,
                 taperL=30.0,
                 probe_w=90.0,
                 probe_L=90.0,
                 lay_cpw=None,
                 lay_gcpw=None,
                 dbu=None,
                 wg_length=100.0):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if lay_cpw is None:
            lay_cpw = pya.CellView.active().layout().layer(1, 0)
        if lay_gcpw is None:
            lay_gcpw = pya.CellView.active().layout().layer(1, 1)

        self.dbu = dbu
        self.cpw_gap = cpw_gap / self.dbu
        self.cpw_swidth = cpw_swidth / self.dbu
        self.cpw_width = cpw_width / self.dbu
        self.wg_length = wg_length / self.dbu
        self.taperL = taperL / self.dbu
        self.probe_w = probe_w / self.dbu
        self.probe_L = probe_L / self.dbu
        self.lay_cpw = lay_cpw
        self.lay_gcpw = lay_gcpw
        self.ports = []

    def shapes(self, cell):
        self.ports = []
        self.ports.append(Ports(width=self.cpw_swidth,
                                direction=math.pi,
                                face_angle=math.pi + math.pi / 2.0,
                                point=pya.DPoint(0.0, 0.0)))
        shape = cell.shapes(self.lay_cpw)
        gshape = cell.shapes(self.lay_gcpw)

        poly1 = []
        poly2 = []
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        pts = [pya.DPoint(0.0, 0.0), pya.DPoint(self.wg_length, 0.0)]
        wg = Waveguide(pts, self.cpw_swidth)
        poly1.append(wg.poly())
        wg = Waveguide(pts, self.cpw_swidth + 2.0 * self.cpw_gap)
        poly2.append(wg.poly())

        pts = [pya.DPoint(-self.taperL, 0.0), pya.DPoint(0.0, 0.0)]
        taper = Taper(pts, self.probe_w, self.cpw_swidth)
        poly1.append(taper.poly())
        poly1.append(poly1[-1].transformed(t1).transformed(t2))
        taper = Taper(pts, self.probe_w + self.cpw_gap * 2.0, self.cpw_swidth + self.cpw_gap * 2.0)
        poly2.append(taper.poly())
        poly2.append(poly2[-1].transformed(t1).transformed(t2))

        pts = [pya.DPoint(-self.taperL - self.probe_L, 0.0), pya.DPoint(-self.taperL, 0.0)]
        wg = Waveguide(pts, self.probe_w)
        poly1.append(wg.poly())
        poly1.append(poly1[-1].transformed(t1).transformed(t2))
        wg = Waveguide(pts, self.probe_w + self.cpw_gap * 2.0)
        poly2.append(wg.poly())
        poly2.append(poly2[-1].transformed(t1).transformed(t2))

        pts = [pya.DPoint(-self.taperL - self.probe_L, 0.0),
               pya.DPoint(self.wg_length + self.taperL + self.probe_L, 0.0)]
        wg = Waveguide(pts, self.cpw_width)
        poly = wg.poly()
        rpoly = poly.round_corners(0.0 / self.dbu, 5.0 / self.dbu, 128)
        shape.insert(rpoly)
        ep = pya.EdgeProcessor()
        out = ep.boolean_p2p(poly1, poly2, pya.EdgeProcessor.ModeBNotA, False, False)
        for p in out:
            gshape.insert(p)

    def get_ports(self):
        return self.ports


if __name__ == "__main__":
    layout = pya.Layout()
    dbu = 0.001
    layout.dbu = dbu

    top = layout.create_cell("Top")
    cpw = Cpw_straight(dbu=dbu, lay_cpw=layout.layer(1, 0), lay_gcpw=layout.layer(1, 1))
    vlength = [900.0, 1100.0, 1300.0]
    for ind, length_val in enumerate(vlength):
        cell = layout.create_cell(f"CPW {length_val}")
        cpw.wg_length = length_val / dbu
        cpw.shapes(cell)
        top.insert(pya.CellInstArray(cell.cell_index, pya.Trans(0, ind * 250 / dbu)))

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
