# PZT_class.py - converted from Ruby to Python using Klayout pya API
import pya
import math
import os
from waveguide import *


def divL(x, activeL, num):
    lens = []
    for iter_i in range(num - 2):
        lens = lens + [x[iter_i]] + [activeL] + [x[iter_i + 1]]
    lens = lens + [x[num - 2]] + [activeL] + [x[num - 1]]
    return lens


class PZT_Modulator:
    def __init__(self, wsin=0.7,
                 wmmi=4.0,
                 lmmi=11.3,
                 radius=50.0,
                 taperL=10.0,
                 gap=0.6,
                 wmmi_in=1.7,
                 spacing=15.0,
                 sbend_len=50.0,
                 cpw_pgap=9.0,
                 cpw_pwidth=8.0,
                 wground=100.0,
                 via_L=2.0,
                 cpw_radius=30.0,
                 cpw_agap=5.0,
                 cpw_awidth=10.0,
                 lay_sin=None,
                 lay_active=None,
                 lay_via=None,
                 lay_probe=None,
                 dbu=None,
                 len_arr=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if lay_sin is None:
            lay_sin = pya.CellView.active().layout().layer(1, 1)
        if lay_active is None:
            lay_active = pya.CellView.active().layout().layer(3, 1)
        if lay_via is None:
            lay_via = pya.CellView.active().layout().layer(4, 1)
        if lay_probe is None:
            lay_probe = pya.CellView.active().layout().layer(5, 1)
        if len_arr is None:
            len_arr = [100.0, 50.0, 100.0, 100.0, 50.0, 200.0, 200.0, 100.0, 300.0]

        self.dbu = dbu
        self.wsin = wsin / self.dbu
        self.wmmi = wmmi / self.dbu
        self.lmmi = lmmi / self.dbu
        self.radius = radius / self.dbu
        self.taperL = taperL / self.dbu
        self.sbend_len = sbend_len / self.dbu
        self.gap = gap / self.dbu
        self.wmmi_in = wmmi_in / self.dbu
        self.spacing = spacing / self.dbu
        self.cpw_pgap = cpw_pgap / self.dbu
        self.cpw_pwidth = cpw_pwidth / self.dbu
        self.wground = wground / self.dbu
        self.via_L = via_L / self.dbu
        self.cpw_radius = cpw_radius / self.dbu
        self.cpw_agap = cpw_agap / self.dbu
        self.cpw_awidth = cpw_awidth / self.dbu
        self.lay_sin = lay_sin
        self.lay_active = lay_active
        self.lay_via = lay_via
        self.lay_probe = lay_probe
        self.ports = []
        self.len_arr = [l / self.dbu for l in len_arr]

    def shapes(self, cell):
        self.ports = []
        shape = cell.shapes(self.lay_sin)
        self._sin(shape)
        shape = cell.shapes(self.lay_active)
        self._active(shape)
        shape = cell.shapes(self.lay_via)
        self._via(shape)
        shape = cell.shapes(self.lay_probe)
        self._probe(shape)

    def _sin(self, shape):
        start_x = 0.0
        self.ports.append(Ports(width=self.wsin,
                                direction=math.pi,
                                face_angle=math.pi + math.pi / 2.0,
                                point=pya.DPoint(start_x, 0.0)))
        wglength = 0
        for iter_i in range(len(self.len_arr) // 3):
            wglength = wglength + self.len_arr[iter_i * 3 + 1] + self.len_arr[iter_i * 3 + 2]
        wglength = wglength - self.len_arr[-1]

        # MMI in
        pts = [pya.DPoint(start_x, 0.0), pya.DPoint(start_x + self.taperL, 0.0)]
        mmi_taper = Taper(pts, self.wsin, self.wmmi_in)
        shape.insert(mmi_taper.poly())
        mmi = [pya.DPoint(self.taperL, -self.wmmi / 2.0), pya.DPoint(self.taperL, self.wmmi / 2.0),
               pya.DPoint(self.taperL + self.lmmi, self.wmmi / 2.0),
               pya.DPoint(self.taperL + self.lmmi, -self.wmmi / 2.0)]
        shape.insert(pya.Polygon.from_dpoly(pya.DPolygon(mmi)))
        t1 = pya.Trans(pya.Trans.M90)
        t2 = pya.Trans(2.0 * self.taperL + self.lmmi, self.gap / 2.0 + self.wmmi_in / 2.0)
        shape.insert(mmi_taper.poly().transformed(t1).transformed(t2))
        t2 = pya.Trans(2.0 * self.taperL + self.lmmi, -self.gap / 2.0 - self.wmmi_in / 2.0)
        shape.insert(mmi_taper.poly().transformed(t1).transformed(t2))

        # Sbend
        p1 = pya.DPoint(2.0 * self.taperL + self.lmmi, self.gap / 2.0 + self.wmmi_in / 2.0)
        dir1 = 0
        p2 = pya.DPoint(2.0 * self.taperL + self.lmmi + self.sbend_len, self.spacing / 2.0)
        dir2 = 0
        pts = sbend(p1, dir1, p2, dir2, self.radius, 1)
        pts.append(pya.DPoint(2.0 * self.taperL + self.lmmi + self.sbend_len + wglength / 2.0,
                               self.spacing / 2.0))
        rwg = Waveguide(pts, self.wsin)
        shape.insert(rwg.poly())
        t3 = pya.Trans(pya.Trans.M0)
        shape.insert(rwg.poly().transformed(t3))

        # Sbend out
        ldev = wglength + self.taperL * 4.0 + self.lmmi * 2.0 + 2.0 * self.sbend_len
        t1 = pya.Trans(pya.Trans.M90)
        t2 = pya.Trans(ldev, 0.0)
        shape.insert(rwg.poly().transformed(t1).transformed(t2))
        shape.insert(rwg.poly().transformed(t1).transformed(t2).transformed(t3))
        # MMI out
        shape.insert(mmi_taper.poly().transformed(t1).transformed(t2))
        shape.insert(pya.Polygon.from_dpoly(pya.DPolygon(mmi)).transformed(t1).transformed(t2))
        t1 = pya.Trans(ldev - self.taperL * 2.0 - self.lmmi, self.gap / 2.0 + self.wmmi_in / 2.0)
        shape.insert(mmi_taper.poly().transformed(t1))
        t1 = pya.Trans(ldev - self.taperL * 2.0 - self.lmmi, -self.gap / 2.0 - self.wmmi_in / 2.0)
        shape.insert(mmi_taper.poly().transformed(t1))
        self.ports.append(Ports(width=self.wsin,
                                direction=0,
                                face_angle=math.pi / 2.0,
                                point=pya.DPoint(start_x + ldev, self.gap / 2.0 + self.wmmi_in / 2.0)))
        self.ports.append(Ports(width=self.wsin,
                                direction=0,
                                face_angle=math.pi / 2.0,
                                point=pya.DPoint(start_x + ldev, -self.gap / 2.0 - self.wmmi_in / 2.0)))

    def _active(self, shape):
        spoly = []
        gpoly = []
        airpoly = []
        start_x = 0.0
        lastx = start_x + self.taperL * 2.0 + self.lmmi + self.sbend_len
        for iter_i in range(len(self.len_arr) // 3):
            wglength = self.len_arr[iter_i * 3 + 1]
            pts = [pya.DPoint(lastx, 0.0), pya.DPoint(lastx + wglength, 0.0)]
            spoly.append(Waveguide(pts, self.cpw_awidth).poly())
            airpoly.append(Waveguide(pts, self.cpw_awidth + self.cpw_agap * 2.0).poly())
            gpoly.append(Waveguide(pts, self.wground).poly())
            lastx = lastx + self.len_arr[iter_i * 3 + 1] + self.len_arr[iter_i * 3 + 2]

        ep = pya.EdgeProcessor()
        out = ep.boolean_p2p(airpoly, gpoly, pya.EdgeProcessor.ModeBNotA, False, False)
        out = ep.boolean_p2p(out, spoly, pya.EdgeProcessor.ModeOr, False, False)
        for p in out:
            shape.insert(p)

    def _via(self, shape):
        extend = 1.0 / self.dbu
        spoly = []
        gpoly = []
        airpoly = []
        start_x = 0.0
        lastx = start_x + self.taperL * 2.0 + self.lmmi + self.sbend_len
        for iter_i in range(len(self.len_arr) // 3):
            wglength = self.len_arr[iter_i * 3 + 1]
            if (self.len_arr[iter_i * 3] > 0) or (iter_i == 0):
                pts = [pya.DPoint(lastx + extend / 2.0, 0.0),
                       pya.DPoint(lastx + self.via_L + extend / 2.0, 0.0)]
                spoly.append(Waveguide(pts, self.cpw_awidth - extend).poly())
                airpoly.append(Waveguide(pts, self.cpw_awidth + self.cpw_agap * 2.0 + extend).poly())
                gpoly.append(Waveguide(pts, self.wground - extend).poly())
            if (self.len_arr[iter_i * 3 + 2] > 0) or (iter_i == (len(self.len_arr) // 3 - 1)):
                pts = [pya.DPoint(lastx + wglength - self.via_L - extend / 2.0, 0.0),
                       pya.DPoint(lastx + wglength - extend / 2.0, 0.0)]
                spoly.append(Waveguide(pts, self.cpw_awidth - extend).poly())
                airpoly.append(Waveguide(pts, self.cpw_awidth + self.cpw_agap * 2.0 + extend).poly())
                gpoly.append(Waveguide(pts, self.wground - extend).poly())
            lastx = lastx + self.len_arr[iter_i * 3 + 1] + self.len_arr[iter_i * 3 + 2]

        ep = pya.EdgeProcessor()
        out = ep.boolean_p2p(airpoly, gpoly, pya.EdgeProcessor.ModeBNotA, False, False)
        for p in out:
            shape.insert(p)
        for p in spoly:
            shape.insert(p)

    def _probe(self, shape):
        extend = 1.0 / self.dbu
        spoly = []
        gpoly = []
        airpoly = []
        start_x = 0.0
        lastx = start_x + self.taperL * 2.0 + self.lmmi + self.sbend_len
        lr = 0.5 * math.pi * self.cpw_radius
        len2 = list(self.len_arr)
        len2[0] = len2[0] - lr
        len2[-1] = len2[-1] - lr
        if len2[0] <= (extend * 50.0):
            len2[0] = extend * 50.0
        if len2[-1] <= (extend * 50.0):
            len2[-1] = extend * 50.0
        totlen = 0
        for iter_i in range(len(len2) // 3):
            wglength_p = len2[iter_i * 3]
            totlen = totlen + len2[iter_i * 3] + len2[iter_i * 3 + 1]
            if wglength_p > 0:
                pts = [pya.DPoint(lastx - wglength_p - self.via_L - extend / 2.0, 0.0),
                       pya.DPoint(lastx + self.via_L + extend / 2.0, 0.0)]
                spoly.append(Waveguide(pts, self.cpw_pwidth).poly())
                gpoly.append(Waveguide(pts, self.wground).poly())
            lastx = lastx + len2[iter_i * 3 + 1] + len2[iter_i * 3 + 2]

        wglength_p = len2[-1]
        totlen = totlen + len2[-1]
        pts = [pya.DPoint(lastx - wglength_p - self.via_L - extend / 2.0, 0.0),
               pya.DPoint(lastx + self.via_L + extend / 2.0, 0.0)]
        spoly.append(Waveguide(pts, self.cpw_pwidth).poly())
        gpoly.append(Waveguide(pts, self.wground).poly())
        firstx = start_x + self.taperL * 2.0 + self.lmmi + self.sbend_len
        pts = [pya.DPoint(firstx - len2[0] - self.via_L - extend / 2.0, 0.0),
               pya.DPoint(lastx + self.via_L + extend / 2.0, 0.0)]
        airpoly.append(Waveguide(pts, self.cpw_pwidth + self.cpw_pgap * 2.0).poly())

        # probe
        probe_L = 80.0 / self.dbu
        taperL = 30.0 / self.dbu
        probe_w = 90.0 / self.dbu
        probe_gap = 18.0 / self.dbu

        # Bend
        t1 = pya.Trans(pya.DTrans.M90)
        lastx = start_x + self.taperL * 2.0 + self.lmmi + self.sbend_len
        pts = [pya.DPoint(lastx - len2[0] - self.via_L - extend / 2.0 + extend, 0.0),
               pya.DPoint(lastx - len2[0] - self.cpw_radius - self.via_L - extend / 2.0, 0.0),
               pya.DPoint(lastx - len2[0] - self.cpw_radius - self.via_L - extend / 2.0,
                          self.cpw_radius + extend)]
        t2 = pya.Trans(totlen + 2.0 * self.via_L - extend + 2.0 * pts[0].x, 0.0)
        pts = round_corners(pts, self.cpw_radius, 2.0)
        spoly.append(Waveguide(pts, self.cpw_pwidth, 90.0, 0, 180.0, 90).poly())
        airpoly.append(Waveguide(pts, self.cpw_pwidth + self.cpw_pgap * 2.0, 90.0, 0.0, 180.0, 90).poly())
        spoly.append(spoly[-1].transformed(t1).transformed(t2))
        airpoly.append(airpoly[-1].transformed(t1).transformed(t2))

        xp0 = lastx - len2[0] - self.cpw_radius - self.via_L - extend / 2.0
        # Taper
        pts = [pya.DPoint(xp0, self.cpw_radius),
               pya.DPoint(xp0, self.cpw_radius + taperL)]
        taper = Taper(pts, self.cpw_pwidth, probe_w)
        spoly.append(taper.poly())
        spoly.append(spoly[-1].transformed(t1).transformed(t2))
        taper = Taper(pts, self.cpw_pwidth + self.cpw_pgap * 2.0, probe_w + probe_gap * 2.0)
        airpoly.append(taper.poly())
        airpoly.append(airpoly[-1].transformed(t1).transformed(t2))

        # Probe
        pts = [pya.DPoint(xp0, self.cpw_radius + taperL),
               pya.DPoint(xp0, self.cpw_radius + taperL + probe_L)]
        wg = Waveguide(pts, probe_w)
        spoly.append(wg.poly())
        spoly.append(spoly[-1].transformed(t1).transformed(t2))
        wg = Waveguide(pts, probe_w + probe_gap * 2.0)
        airpoly.append(wg.poly())
        airpoly.append(airpoly[-1].transformed(t1).transformed(t2))

        # ground
        pts = [pya.DPoint(xp0 + probe_w / 2.0 + probe_gap + probe_w,
                          self.cpw_radius + probe_L + taperL),
               pya.DPoint(xp0 + probe_w / 2.0 + probe_gap + probe_w, -self.wground / 2.0),
               pya.DPoint(xp0 - probe_w / 2.0 - probe_gap - probe_w, -self.wground / 2.0),
               pya.DPoint(xp0 - probe_w / 2.0 - probe_gap - probe_w,
                          self.cpw_radius + probe_L + taperL)]
        poly = pya.Polygon.from_dpoly(pya.DPolygon(pts))
        gpoly.append(poly.round_corners(0.0 / self.dbu, 5.0 / self.dbu, 128))
        gpoly.append(gpoly[-1].transformed(t1).transformed(t2))
        ep = pya.EdgeProcessor()
        out = ep.boolean_p2p(airpoly, gpoly, pya.EdgeProcessor.ModeBNotA, False, False)
        for p in out:
            shape.insert(p)
        for p in spoly:
            shape.insert(p)

    def get_ports(self):
        return self.ports


if __name__ == "__main__":
    layout = pya.Layout()
    dbu = 0.001
    layout.dbu = dbu

    lay_sin = layout.layer(1, 1)
    lay_active = layout.layer(3, 1)
    lay_via = layout.layer(4, 1)
    lay_probe = layout.layer(5, 1)

    cell = layout.create_cell("PZT_Modulator_40G_L4mm_w8_gap9")
    pzt = PZT_Modulator(dbu=dbu, lay_sin=lay_sin, lay_active=lay_active, lay_via=lay_via, lay_probe=lay_probe)
    length_list = [0.0, 4000.0, 0.0]
    pzt.len_arr = [l / dbu for l in length_list]
    pzt.shapes(cell)

    if True:
        cell2 = layout.create_cell("PZT_Modulator_70G_L8mm_w8_gap9")
        pzt2 = PZT_Modulator(dbu=dbu, lay_sin=lay_sin, lay_active=lay_active, lay_via=lay_via, lay_probe=lay_probe)
        plen = [0, 0, 0, 0, 0, 0, 0, 0, 100, 0, 100, 100, 0, 100, 100, 0, 150, 100, 250,
                150, 250, 250, 200, 300, 400, 150, 200, 100, 0, 0, 0, 0, 0, 100, 0, 100,
                100, 200, 100, 100, 0, 100, 0, 0, 0, 0, 0, 0, 100, 0, 0]
        activeL = 4000.0 / (len(plen) - 1.0)
        length_list2 = divL(plen, activeL, 51)
        pzt2.len_arr = [l / dbu for l in length_list2]
        pzt2.shapes(cell2)

    cell3 = layout.create_cell("PZT_Modulator_90G_L10mm_w8_gap9")
    pzt3 = PZT_Modulator(dbu=dbu, lay_sin=lay_sin, lay_active=lay_active, lay_via=lay_via, lay_probe=lay_probe)
    plen3 = [25.8, 40.0, 0.0, 0.0, 49.1, 0.0, 26.9, 40.4, 60.2, 26.5, 40.6, 0.0, 91.2,
             34.6, 47.2, 81.5, 0.0, 29.8, 69.5, 112.5, 101.6, 79.1, 87.8, 144.7, 79.7,
             104.2, 89.1, 85.3, 105.1, 117.1, 57.9, 135.2, 68.2, 107.0, 35.3, 124.4, 120.1,
             92.7, 91.4, 71.8, 79.5, 45.8, 48.1, 71.1, 81.9, 91.9, 140.9, 121.5, 97.2,
             178.7, 97.4, 142.2, 50.8, 117.1, 70.8, 146.7, 79.2, 60.5, 98.1, 55.8, 95.3,
             66.3, 23.6, 106.8, 79.8, 0.0, 67.9, 32.4, 28.2, 0.0, 27.0, 72.0, 121.6, 29.7,
             102.9, 62.6, 38.3, 0.0, 28.1, 0.0, 35.6, 0.0, 0.0, 38.3, 31.0, 68.7, 29.0,
             0.0, 0.0, 63.9, 0.0, 22.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    activeL3 = 4000.0 / (len(plen3) - 1.0)
    length_list3 = divL(plen3, activeL3, 101)
    pzt3.len_arr = [l / dbu for l in length_list3]
    pzt3.shapes(cell3)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
