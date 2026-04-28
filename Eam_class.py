# Eam_class.py - converted from Ruby to Python using Klayout pya API
import pya
import math
import os
from waveguide import *


class Eam_Lump:
    def __init__(self, mesa_width_in=1.4,
                 mesa_width_hybrid=3.0,
                 mqw_width_in=1.8,
                 mqw_width_hybrid=4.0,
                 nInP_width=50.0,
                 nInP_length=300.0,
                 taper1=90.0,
                 taper2=15.0,
                 wg_length=100.0,
                 nmetal_gap=8.0,
                 lay_mesa=None,
                 lay_mqw=None,
                 lay_nInP=None,
                 lay_nmetal=None,
                 lay_pvia=None,
                 lay_nvia=None,
                 lay_probe=None,
                 dbu=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if lay_mesa is None:
            lay_mesa = pya.CellView.active().layout().layer(1, 1)
        if lay_mqw is None:
            lay_mqw = pya.CellView.active().layout().layer(3, 1)
        if lay_nInP is None:
            lay_nInP = pya.CellView.active().layout().layer(4, 1)
        if lay_nmetal is None:
            lay_nmetal = pya.CellView.active().layout().layer(5, 1)
        if lay_pvia is None:
            lay_pvia = pya.CellView.active().layout().layer(8, 1)
        if lay_nvia is None:
            lay_nvia = pya.CellView.active().layout().layer(7, 1)
        if lay_probe is None:
            lay_probe = pya.CellView.active().layout().layer(9, 1)

        self.dbu = dbu
        self.mesa_width_in = mesa_width_in / self.dbu
        self.mesa_width_hybrid = mesa_width_hybrid / self.dbu
        self.mqw_width_in = mqw_width_in / self.dbu
        self.mqw_width_hybrid = mqw_width_hybrid / self.dbu
        self.nInP_width = nInP_width / self.dbu
        if wg_length + (taper1 + taper2) * 2.0 > nInP_length:
            nInP_length = wg_length + (taper1 + taper2) * 2.0 + 60.0
            if nInP_length < (300.0 / self.dbu):
                nInP_length = 300.0 / self.dbu
        self.nInP_length = nInP_length / self.dbu
        self.taper1 = taper1 / self.dbu
        self.taper2 = taper2 / self.dbu
        self.wg_length = wg_length / self.dbu
        self.nmetal_gap = nmetal_gap / self.dbu
        self.lay_mesa = lay_mesa
        self.lay_mqw = lay_mqw
        self.lay_nInP = lay_nInP
        self.lay_nmetal = lay_nmetal
        self.lay_pvia = lay_pvia
        self.lay_nvia = lay_nvia
        self.lay_probe = lay_probe
        self.nprobe_w = (self.nInP_width - self.nmetal_gap - 6.0 / self.dbu) / 2.0
        self.nproble_l = 20.0 / self.dbu
        self.ports = []

    def wg_length_set(self, wg_length):
        self.wg_length = wg_length
        if self.wg_length + (self.taper1 + self.taper2) * 2.0 > self.nInP_length:
            self.nInP_length = self.wg_length + (self.taper1 + self.taper2) * 2.0 - 50.0 / self.dbu
            if self.nInP_length < (300.0 / self.dbu):
                self.nInP_length = 300.0 / self.dbu
        else:
            self.nInP_length = 300.0 / self.dbu

    def shapes(self, cell):
        self.ports = []
        self.ports.append(Ports(width=self.mesa_width_hybrid,
                                direction=math.pi,
                                face_angle=math.pi + math.pi / 2.0,
                                point=pya.DPoint(0.0, 0.0)))
        shape = cell.shapes(self.lay_mesa)
        self._mesa(shape)
        shape = cell.shapes(self.lay_mqw)
        self._mqw(shape)
        shape = cell.shapes(self.lay_nInP)
        self._nInP(shape)
        shape = cell.shapes(self.lay_nmetal)
        self._nmetal(shape)
        shape = cell.shapes(self.lay_pvia)
        self._pvia(shape)
        shape = cell.shapes(self.lay_nvia)
        self._nvia(shape)
        shape = cell.shapes(self.lay_probe)
        self._probe(shape)

    def _mesa(self, shape):
        pts = [pya.DPoint(0.0, 0.0), pya.DPoint(self.wg_length, 0.0)]
        wg = Waveguide(pts, self.mesa_width_hybrid)
        shape.insert(wg.poly())
        pts = [pya.DPoint(-self.taper2, 0.0), pya.DPoint(0.0, 0.0)]
        taper = Taper(pts, self.mesa_width_in, self.mesa_width_hybrid)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))

        exten_length = 18.0 / self.dbu
        pts = [pya.DPoint(-self.taper2 - exten_length, 0.0), pya.DPoint(-self.taper2, 0.0)]
        wg = Waveguide(pts, self.mesa_width_in)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(wg.poly().transformed(t1).transformed(t2))

    def _mqw(self, shape):
        pts = [pya.DPoint(-self.taper2, 0.0), pya.DPoint(self.wg_length + self.taper2, 0.0)]
        wg = Waveguide(pts, self.mqw_width_hybrid)
        shape.insert(wg.poly())
        pts = [pya.DPoint(-self.taper1 - self.taper2, 0.0), pya.DPoint(-self.taper2, 0.0)]
        taper = Taper(pts, self.mqw_width_in, self.mqw_width_hybrid)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))
        tip = Circle(pya.DPoint(-self.taper1 - self.taper2, 0.0), self.mqw_width_in / 2.0, 90.0, 270)
        shape.insert(tip.poly())
        shape.insert(tip.poly().transformed(t1).transformed(t2))

        tmpw = [self.mqw_width_hybrid, self.mqw_width_hybrid - 1.5 / self.dbu,
                (self.mqw_width_hybrid - 1.5 / self.dbu) / 2.0]
        for iter_i in range(1, 4):
            pts = [pya.DPoint(0.0, -self.nInP_width / 2.0 - 10.0 * iter_i / self.dbu),
                   pya.DPoint(self.wg_length, -self.nInP_width / 2.0 - 10.0 * iter_i / self.dbu)]
            wg = Waveguide(pts, tmpw[iter_i - 1])
            shape.insert(wg.poly())

    def _nInP(self, shape):
        offset = 0.0 / self.dbu
        pts = [pya.DPoint(-self.taper2 - self.taper1 - offset, 0.0),
               pya.DPoint(self.wg_length + self.taper2 + self.taper1 + offset, 0.0)]
        wg = Waveguide(pts, self.nInP_width)
        shape.insert(wg.poly())
        pts = [pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0, self.nInP_width / 2.0 - self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + self.nInP_length / 2.0, self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w)
        shape.insert(wg.poly())
        t1 = pya.Trans(0.0, -self.nInP_width + self.nprobe_w)
        shape.insert(wg.poly().transformed(t1))

    def _nmetal(self, shape):
        offset = 3.0 / self.dbu
        pts = [pya.DPoint(0.0, -self.nmetal_gap / 2.0 - offset / 2.0),
               pya.DPoint(self.wg_length, -self.nmetal_gap / 2.0 - offset / 2.0)]
        wg = Waveguide(pts, offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        pts = [pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + self.nInP_length / 2.0,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

    def _pvia(self, shape):
        offset = 1.0 / self.dbu
        pts = [pya.DPoint(offset / 2.0, 0.0), pya.DPoint(self.wg_length - offset / 2.0, 0.0)]
        wg = Waveguide(pts, self.mesa_width_hybrid - offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        offset = 1.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0 + offset,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0 + self.nproble_l + offset,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        pts = [pya.DPoint(self.wg_length / 2.0 + self.nInP_length / 2.0 - self.nproble_l - offset,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + self.nInP_length / 2.0 - offset,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

    def _nvia(self, shape):
        offset = 1.0 / self.dbu
        smaller = 1.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0 + offset + smaller,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0 + self.nproble_l + offset - smaller,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w - 2.0 * smaller)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        pts = [pya.DPoint(self.wg_length / 2.0 + self.nInP_length / 2.0 - self.nproble_l - offset + smaller,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + self.nInP_length / 2.0 - offset - smaller,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w - 2.0 * smaller)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

    def _probe(self, shape):
        pprobe_width = 10.0 / self.dbu
        pts = [pya.DPoint(0.0, 0.0), pya.DPoint(self.wg_length, 0.0)]
        wg = Waveguide(pts, pprobe_width)
        shape.insert(wg.poly())

        proble_w1 = 10.0 / self.dbu
        proble_w2 = 90.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0, pprobe_width / 2.0),
               pya.DPoint(self.wg_length / 2.0, self.nInP_width / 2.0)]
        wg = Waveguide(pts, proble_w1)
        shape.insert(wg.poly())

        taperL = 30.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0, self.nInP_width / 2.0),
               pya.DPoint(self.wg_length / 2.0, self.nInP_width / 2.0 + taperL)]
        taper = Taper(pts, proble_w1, proble_w2)
        shape.insert(taper.poly())

        probe_L = 80.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0, self.nInP_width / 2.0 + taperL),
               pya.DPoint(self.wg_length / 2.0, self.nInP_width / 2.0 + taperL + probe_L)]
        wg = Waveguide(pts, proble_w2)
        shape.insert(wg.poly())

        gap = 18.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0 - proble_w2 / 2.0 - gap,
                          self.nInP_width / 2.0 + taperL + probe_L),
               pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0,
                          self.nInP_width / 2.0 + taperL + probe_L),
               pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0, -self.nInP_width / 2.0),
               pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0 + self.nproble_l + 2.0 / self.dbu,
                          -self.nInP_width / 2.0),
               pya.DPoint(self.wg_length / 2.0 - self.nInP_length / 2.0 + self.nproble_l + 2.0 / self.dbu,
                          self.nInP_width / 2.0),
               pya.DPoint(self.wg_length / 2.0 - proble_w2 / 2.0 - gap,
                          self.nInP_width / 2.0 + taperL)]
        poly = pya.Polygon.from_dpoly(pya.DPolygon(pts))
        shape.insert(poly)
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(poly.transformed(t1).transformed(t2))

    def get_ports(self):
        return self.ports


class Eam_TW:
    def __init__(self, mesa_width_in=1.4,
                 mesa_width_hybrid=3.0,
                 mqw_width_in=1.8,
                 mqw_width_hybrid=4.0,
                 nInP_width=50.0,
                 nInP_length=300.0,
                 taper1=90.0,
                 taper2=15.0,
                 wg_length=100.0,
                 nmetal_gap=8.0,
                 cpw_gap=18.0,
                 cpw_radius=30.0,
                 cpw_width=10.0,
                 lay_mesa=None,
                 lay_mqw=None,
                 lay_nInP=None,
                 lay_nmetal=None,
                 lay_pvia=None,
                 lay_nvia=None,
                 lay_probe=None,
                 dbu=None,
                 lp=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if lay_mesa is None:
            lay_mesa = pya.CellView.active().layout().layer(1, 1)
        if lay_mqw is None:
            lay_mqw = pya.CellView.active().layout().layer(3, 1)
        if lay_nInP is None:
            lay_nInP = pya.CellView.active().layout().layer(4, 1)
        if lay_nmetal is None:
            lay_nmetal = pya.CellView.active().layout().layer(5, 1)
        if lay_pvia is None:
            lay_pvia = pya.CellView.active().layout().layer(8, 1)
        if lay_nvia is None:
            lay_nvia = pya.CellView.active().layout().layer(7, 1)
        if lay_probe is None:
            lay_probe = pya.CellView.active().layout().layer(9, 1)
        if lp is None:
            lp = [60.0, 300.0]

        self.dbu = dbu
        self.mesa_width_in = mesa_width_in / self.dbu
        self.mesa_width_hybrid = mesa_width_hybrid / self.dbu
        self.mqw_width_in = mqw_width_in / self.dbu
        self.mqw_width_hybrid = mqw_width_hybrid / self.dbu
        self.nInP_width = nInP_width / self.dbu
        if wg_length + (taper1 + taper2) * 2.0 > nInP_length:
            nInP_length = wg_length + (taper1 + taper2) * 2.0 + 60.0
        self.nInP_length = nInP_length / self.dbu
        self.taper1 = taper1 / self.dbu
        self.taper2 = taper2 / self.dbu
        self.wg_length = wg_length / self.dbu
        self.nmetal_gap = nmetal_gap / self.dbu
        self.lay_mesa = lay_mesa
        self.lay_mqw = lay_mqw
        self.lay_nInP = lay_nInP
        self.lay_nmetal = lay_nmetal
        self.lay_pvia = lay_pvia
        self.lay_nvia = lay_nvia
        self.lay_probe = lay_probe
        self.nprobe_w = (self.nInP_width - self.nmetal_gap - 6.0 / self.dbu) / 2.0
        self.nproble_l = 20.0 / self.dbu
        self.cpw_radius = cpw_radius / self.dbu
        self.cpw_gap = cpw_gap / self.dbu
        self.cpw_width = cpw_width / self.dbu
        self.ports = []
        self.lp = [l / self.dbu for l in lp]

    def shapes(self, cell):
        self.ports = []
        self.ports.append(Ports(width=self.mesa_width_hybrid,
                                direction=math.pi,
                                face_angle=math.pi + math.pi / 2.0,
                                point=pya.DPoint(0.0, 0.0)))
        shape = cell.shapes(self.lay_mesa)
        self._mesa(shape)
        shape = cell.shapes(self.lay_mqw)
        self._mqw(shape)
        shape = cell.shapes(self.lay_nInP)
        self._nInP(shape)
        shape = cell.shapes(self.lay_nmetal)
        self._nmetal(shape)
        shape = cell.shapes(self.lay_pvia)
        self._pvia(shape)
        shape = cell.shapes(self.lay_nvia)
        self._nvia(shape)
        shape = cell.shapes(self.lay_probe)
        self._probe(shape)

    def _mesa(self, shape):
        pts = [pya.DPoint(0.0, 0.0), pya.DPoint(self.wg_length, 0.0)]
        wg = Waveguide(pts, self.mesa_width_hybrid)
        shape.insert(wg.poly())
        pts = [pya.DPoint(-self.taper2, 0.0), pya.DPoint(0.0, 0.0)]
        taper = Taper(pts, self.mesa_width_in, self.mesa_width_hybrid)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))

        exten_length = 18.0 / self.dbu
        pts = [pya.DPoint(-self.taper2 - exten_length, 0.0), pya.DPoint(-self.taper2, 0.0)]
        wg = Waveguide(pts, self.mesa_width_in)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(wg.poly().transformed(t1).transformed(t2))

    def _mqw(self, shape):
        pts = [pya.DPoint(-self.taper2, 0.0), pya.DPoint(self.wg_length + self.taper2, 0.0)]
        wg = Waveguide(pts, self.mqw_width_hybrid)
        shape.insert(wg.poly())
        pts = [pya.DPoint(-self.taper1 - self.taper2, 0.0), pya.DPoint(-self.taper2, 0.0)]
        taper = Taper(pts, self.mqw_width_in, self.mqw_width_hybrid)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))
        tip = Circle(pya.DPoint(-self.taper1 - self.taper2, 0.0), self.mqw_width_in / 2.0, 90.0, 270)
        shape.insert(tip.poly())
        shape.insert(tip.poly().transformed(t1).transformed(t2))

        tmpw = [(self.mqw_width_hybrid - 1.5 / self.dbu) / 2.0,
                self.mqw_width_hybrid - 1.5 / self.dbu,
                self.mqw_width_hybrid]
        for iter_i in range(1, 4):
            pts = [pya.DPoint(self.wg_length + self.nproble_l, -self.nInP_width / 2.0 - 10.0 * iter_i / self.dbu),
                   pya.DPoint(self.wg_length * 2.0 + self.nproble_l, -self.nInP_width / 2.0 - 10.0 * iter_i / self.dbu)]
            wg = Waveguide(pts, tmpw[iter_i - 1])
            shape.insert(wg.poly())

    def _nInP(self, shape):
        # wg section
        offset = 20.0 / self.dbu
        pts = [pya.DPoint(-self.taper2, 0.0), pya.DPoint(self.wg_length + self.taper2, 0.0)]
        wg = Waveguide(pts, self.nInP_width)
        shape.insert(wg.poly())
        # taper section
        pts = [pya.DPoint(-self.taper1 - self.taper2, 0.0), pya.DPoint(-self.taper2, 0.0)]
        taper = Taper(pts, self.mesa_width_in, 10.0 / self.dbu)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))
        tip = Circle(pya.DPoint(-self.taper1 - self.taper2, 0.0), self.mesa_width_in / 2.0, 90.0, 270)
        shape.insert(tip.poly())
        shape.insert(tip.poly().transformed(t1).transformed(t2))
        # nprobe_section
        offset = 2.0 / self.dbu
        pts = [pya.DPoint(-self.nproble_l / 2.0 - offset, -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
               pya.DPoint(self.nproble_l / 2.0 + offset, -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w + offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(wg.poly().transformed(t1))
        shape.insert(wg.poly().transformed(t2))
        shape.insert(wg.poly().transformed(t1).transformed(t2))

    def _nmetal(self, shape):
        offset = 3.0 / self.dbu
        pts = [pya.DPoint(0.0, -self.nmetal_gap / 2.0 - offset / 2.0),
               pya.DPoint(self.wg_length, -self.nmetal_gap / 2.0 - offset / 2.0)]
        wg = Waveguide(pts, offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        nmetal_length = self.wg_length + self.nproble_l + 6.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0 - nmetal_length / 2.0,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + nmetal_length / 2.0,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        offset = 1.5 / self.dbu
        pts = [pya.DPoint(-self.nproble_l / 2.0 - offset, -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
               pya.DPoint(self.nproble_l / 2.0 + offset, -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w + offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(wg.poly().transformed(t1))
        shape.insert(wg.poly().transformed(t2))
        shape.insert(wg.poly().transformed(t1).transformed(t2))

    def _pvia(self, shape):
        offset = 1.0 / self.dbu
        pts = [pya.DPoint(offset / 2.0, 0.0), pya.DPoint(self.wg_length - offset / 2.0, 0.0)]
        wg = Waveguide(pts, self.mesa_width_hybrid - offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        offset = 1.0 / self.dbu
        pts = [pya.DPoint(-self.nproble_l / 2.0 - offset, -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
               pya.DPoint(self.nproble_l / 2.0 + offset, -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(wg.poly().transformed(t1))
        shape.insert(wg.poly().transformed(t2))
        shape.insert(wg.poly().transformed(t1).transformed(t2))

    def _nvia(self, shape):
        offset = 1.0 / self.dbu
        smaller = 1.0 / self.dbu
        pts = [pya.DPoint(-self.nproble_l / 2.0, -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
               pya.DPoint(self.nproble_l / 2.0, -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w - 2.0 * smaller)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(wg.poly().transformed(t1))
        shape.insert(wg.poly().transformed(t2))
        shape.insert(wg.poly().transformed(t1).transformed(t2))

    def _probe(self, shape):
        poly1 = []
        poly2 = []
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length + self.lp[1] - self.lp[0], 0.0)
        t3 = pya.Trans()
        pts = [pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius),
               pya.DPoint(-self.cpw_radius - self.lp[0], 0.0),
               pya.DPoint(self.wg_length + self.cpw_radius + self.lp[1], 0.0),
               pya.DPoint(self.wg_length + self.cpw_radius + self.lp[1], self.cpw_radius)]
        pts = round_corners(pts, self.cpw_radius, 2.0)
        wg = Waveguide(pts, self.cpw_width, 0, 0, -90.0, 90.0)
        poly1.append(wg.poly())
        wg = Waveguide(pts, self.cpw_width + self.cpw_gap * 2.0, 0, 0, -90.0, 90.0)
        poly2.append(wg.poly())

        taperL = 30.0 / self.dbu
        proble_w = 90.0 / self.dbu
        pts = [pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius),
               pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius + taperL)]
        taper = Taper(pts, self.cpw_width, proble_w)
        poly = taper.poly()
        poly1.append(poly)
        poly1.append(poly.transformed(t1).transformed(t2).transformed(t3))
        taper = Taper(pts, self.cpw_width + self.cpw_gap * 2.0, proble_w + self.cpw_gap * 2.0)
        poly = taper.poly()
        poly2.append(poly)
        poly2.append(poly.transformed(t1).transformed(t2).transformed(t3))

        probe_L = 80.0 / self.dbu
        pts = [pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius + taperL),
               pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius + taperL + probe_L)]
        wg = Waveguide(pts, proble_w)
        poly = wg.poly()
        poly1.append(poly)
        poly1.append(poly.transformed(t1).transformed(t2).transformed(t3))
        wg = Waveguide(pts, proble_w + self.cpw_gap * 2.0)
        poly = wg.poly()
        poly2.append(poly)
        poly2.append(poly.transformed(t1).transformed(t2).transformed(t3))
        nprobe_w = 90.0 / self.dbu
        tmp_w = -50.0 / self.dbu
        pts = [pya.DPoint(-self.cpw_radius - proble_w / 2.0 - self.cpw_gap - nprobe_w - self.lp[0],
                          self.cpw_radius + taperL + probe_L),
               pya.DPoint(-self.cpw_radius - proble_w / 2.0 - self.cpw_gap - nprobe_w - self.lp[0], tmp_w),
               pya.DPoint(self.wg_length + self.cpw_radius + proble_w / 2.0 + self.cpw_gap + nprobe_w + self.lp[1],
                          tmp_w),
               pya.DPoint(self.wg_length + self.cpw_radius + proble_w / 2.0 + self.cpw_gap + nprobe_w + self.lp[1],
                          self.cpw_radius + taperL + probe_L)]
        poly = pya.Polygon.from_dpoly(pya.DPolygon(pts))
        rpoly = poly.round_corners(0.0 / self.dbu, 5.0 / self.dbu, 128)
        ep = pya.EdgeProcessor()
        out = ep.boolean_p2p(poly2, [rpoly], pya.EdgeProcessor.ModeBNotA, False, False)
        for p in out:
            shape.insert(p)
        for p in poly1:
            shape.insert(p)

    def get_ports(self):
        return self.ports


class Eam_TW_LUMP:
    def __init__(self, mesa_width_in=1.4,
                 mesa_width_hybrid=3.0,
                 mqw_width_in=1.8,
                 mqw_width_hybrid=4.0,
                 nInP_width=50.0,
                 nInP_length=300.0,
                 taper1=90.0,
                 taper2=15.0,
                 wg_length=100.0,
                 nmetal_gap=8.0,
                 cpw_gap=18.0,
                 cpw_radius=30.0,
                 cpw_width=10.0,
                 lay_mesa=None,
                 lay_mqw=None,
                 lay_nInP=None,
                 lay_nmetal=None,
                 lay_pvia=None,
                 lay_nvia=None,
                 lay_probe=None,
                 dbu=None,
                 lp=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if lay_mesa is None:
            lay_mesa = pya.CellView.active().layout().layer(1, 1)
        if lay_mqw is None:
            lay_mqw = pya.CellView.active().layout().layer(3, 1)
        if lay_nInP is None:
            lay_nInP = pya.CellView.active().layout().layer(4, 1)
        if lay_nmetal is None:
            lay_nmetal = pya.CellView.active().layout().layer(5, 1)
        if lay_pvia is None:
            lay_pvia = pya.CellView.active().layout().layer(8, 1)
        if lay_nvia is None:
            lay_nvia = pya.CellView.active().layout().layer(7, 1)
        if lay_probe is None:
            lay_probe = pya.CellView.active().layout().layer(9, 1)
        if lp is None:
            lp = [60.0, 200.0]

        self.dbu = dbu
        self.mesa_width_in = mesa_width_in / self.dbu
        self.mesa_width_hybrid = mesa_width_hybrid / self.dbu
        self.mqw_width_in = mqw_width_in / self.dbu
        self.mqw_width_hybrid = mqw_width_hybrid / self.dbu
        self.nInP_width = nInP_width / self.dbu
        if wg_length + (taper1 + taper2) * 2.0 > nInP_length:
            nInP_length = wg_length + (taper1 + taper2) * 2.0 + 60.0
        self.nInP_length = nInP_length / self.dbu
        self.taper1 = taper1 / self.dbu
        self.taper2 = taper2 / self.dbu
        self.wg_length = wg_length / self.dbu
        self.nmetal_gap = nmetal_gap / self.dbu
        self.lay_mesa = lay_mesa
        self.lay_mqw = lay_mqw
        self.lay_nInP = lay_nInP
        self.lay_nmetal = lay_nmetal
        self.lay_pvia = lay_pvia
        self.lay_nvia = lay_nvia
        self.lay_probe = lay_probe
        self.nprobe_w = (self.nInP_width - self.nmetal_gap - 6.0 / self.dbu) / 2.0
        self.nproble_l = 20.0 / self.dbu
        self.cpw_radius = cpw_radius / self.dbu
        self.cpw_gap = cpw_gap / self.dbu
        self.cpw_width = cpw_width / self.dbu
        self.ports = []
        self.lp = [l / self.dbu for l in lp]

    def shapes(self, cell):
        self.ports = []
        self.ports.append(Ports(width=self.mesa_width_hybrid,
                                direction=math.pi,
                                face_angle=math.pi + math.pi / 2.0,
                                point=pya.DPoint(0.0, 0.0)))
        shape = cell.shapes(self.lay_mesa)
        self._mesa(shape)
        shape = cell.shapes(self.lay_mqw)
        self._mqw(shape)
        shape = cell.shapes(self.lay_nInP)
        self._nInP(shape)
        shape = cell.shapes(self.lay_nmetal)
        self._nmetal(shape)
        shape = cell.shapes(self.lay_pvia)
        self._pvia(shape)
        shape = cell.shapes(self.lay_nvia)
        self._nvia(shape)
        shape = cell.shapes(self.lay_probe)
        self._probe(shape)

    def _mesa(self, shape):
        pts = [pya.DPoint(0.0, 0.0), pya.DPoint(self.wg_length, 0.0)]
        wg = Waveguide(pts, self.mesa_width_hybrid)
        shape.insert(wg.poly())
        pts = [pya.DPoint(-self.taper2, 0.0), pya.DPoint(0.0, 0.0)]
        taper = Taper(pts, self.mesa_width_in, self.mesa_width_hybrid)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))

        exten_length = 18.0 / self.dbu
        pts = [pya.DPoint(-self.taper2 - exten_length, 0.0), pya.DPoint(-self.taper2, 0.0)]
        wg = Waveguide(pts, self.mesa_width_in)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(wg.poly().transformed(t1).transformed(t2))

    def _mqw(self, shape):
        pts = [pya.DPoint(-self.taper2, 0.0), pya.DPoint(self.wg_length + self.taper2, 0.0)]
        wg = Waveguide(pts, self.mqw_width_hybrid)
        shape.insert(wg.poly())
        pts = [pya.DPoint(-self.taper1 - self.taper2, 0.0), pya.DPoint(-self.taper2, 0.0)]
        taper = Taper(pts, self.mqw_width_in, self.mqw_width_hybrid)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))
        tip = Circle(pya.DPoint(-self.taper1 - self.taper2, 0.0), self.mqw_width_in / 2.0, 90.0, 270)
        shape.insert(tip.poly())
        shape.insert(tip.poly().transformed(t1).transformed(t2))

        tmpw = [(self.mqw_width_hybrid - 1.5 / self.dbu) / 2.0,
                self.mqw_width_hybrid - 1.5 / self.dbu,
                self.mqw_width_hybrid]
        for iter_i in range(1, 4):
            pts = [pya.DPoint(self.wg_length, -self.nInP_width / 2.0 - 10.0 * iter_i / self.dbu),
                   pya.DPoint(self.wg_length * 2.0, -self.nInP_width / 2.0 - 10.0 * iter_i / self.dbu)]
            wg = Waveguide(pts, tmpw[iter_i - 1])
            shape.insert(wg.poly())

    def _nInP(self, shape):
        # wg section
        offset = 20.0 / self.dbu
        pts = [pya.DPoint(-self.taper2, 0.0), pya.DPoint(self.wg_length + self.taper2, 0.0)]
        wg = Waveguide(pts, self.nInP_width)
        shape.insert(wg.poly())
        # taper section
        pts = [pya.DPoint(-self.taper1 - self.taper2, 0.0), pya.DPoint(-self.taper2, 0.0)]
        taper = Taper(pts, self.mesa_width_in, 10.0 / self.dbu)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))
        tip = Circle(pya.DPoint(-self.taper1 - self.taper2, 0.0), self.mesa_width_in / 2.0, 90.0, 270)
        shape.insert(tip.poly())
        shape.insert(tip.poly().transformed(t1).transformed(t2))

        offset = 2.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0 - self.nproble_l / 2.0 - offset,
                          -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + self.nproble_l / 2.0 + offset,
                          -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w + offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

    def _nmetal(self, shape):
        offset = 3.0 / self.dbu
        pts = [pya.DPoint(0.0, -self.nmetal_gap / 2.0 - offset / 2.0),
               pya.DPoint(self.wg_length, -self.nmetal_gap / 2.0 - offset / 2.0)]
        wg = Waveguide(pts, offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        nmetal_length = self.wg_length
        pts = [pya.DPoint(self.wg_length / 2.0 - nmetal_length / 2.0,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + nmetal_length / 2.0,
                          -self.nInP_width / 2.0 + self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        offset = 1.5 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0 - self.nproble_l / 2.0 - offset,
                          -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + self.nproble_l / 2.0 + offset,
                          -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w + offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

    def _pvia(self, shape):
        offset = 1.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0 - self.nproble_l / 2.0 - offset, 0.0),
               pya.DPoint(self.wg_length / 2.0 + self.nproble_l / 2.0 + offset, 0.0)]
        wg = Waveguide(pts, self.mesa_width_hybrid - offset)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

        offset = 1.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0 - self.nproble_l / 2.0 - offset,
                          -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + self.nproble_l / 2.0 + offset,
                          -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

    def _nvia(self, shape):
        offset = 1.0 / self.dbu
        smaller = 1.0 / self.dbu
        pts = [pya.DPoint(self.wg_length / 2.0 - self.nproble_l / 2.0,
                          -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
               pya.DPoint(self.wg_length / 2.0 + self.nproble_l / 2.0,
                          -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
        wg = Waveguide(pts, self.nprobe_w - 2.0 * smaller)
        shape.insert(wg.poly())
        t1 = pya.Trans(pya.Trans.M0)
        shape.insert(wg.poly().transformed(t1))

    def _probe(self, shape):
        poly1 = []
        poly2 = []
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(self.wg_length + self.lp[1] - self.lp[0], 0.0)
        t3 = pya.Trans()
        pts = [pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius),
               pya.DPoint(-self.cpw_radius - self.lp[0], 0.0),
               pya.DPoint(self.wg_length + self.cpw_radius + self.lp[1], 0.0),
               pya.DPoint(self.wg_length + self.cpw_radius + self.lp[1], self.cpw_radius)]
        pts = round_corners(pts, self.cpw_radius, 2.0)
        wg = Waveguide(pts, self.cpw_width, 0, 0, -90.0, 90.0)
        poly1.append(wg.poly())
        wg = Waveguide(pts, self.cpw_width + self.cpw_gap * 2.0, 0, 0, -90.0, 90.0)
        poly2.append(wg.poly())

        taperL = 30.0 / self.dbu
        proble_w = 90.0 / self.dbu
        pts = [pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius),
               pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius + taperL)]
        taper = Taper(pts, self.cpw_width, proble_w)
        poly = taper.poly()
        poly1.append(poly)
        poly1.append(poly.transformed(t1).transformed(t2).transformed(t3))
        taper = Taper(pts, self.cpw_width + self.cpw_gap * 2.0, proble_w + self.cpw_gap * 2.0)
        poly = taper.poly()
        poly2.append(poly)
        poly2.append(poly.transformed(t1).transformed(t2).transformed(t3))

        probe_L = 80.0 / self.dbu
        pts = [pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius + taperL),
               pya.DPoint(-self.cpw_radius - self.lp[0], self.cpw_radius + taperL + probe_L)]
        wg = Waveguide(pts, proble_w)
        poly = wg.poly()
        poly1.append(poly)
        poly1.append(poly.transformed(t1).transformed(t2).transformed(t3))
        wg = Waveguide(pts, proble_w + self.cpw_gap * 2.0)
        poly = wg.poly()
        poly2.append(poly)
        poly2.append(poly.transformed(t1).transformed(t2).transformed(t3))
        nprobe_w = 90.0 / self.dbu
        tmp_w = -50.0 / self.dbu
        pts = [pya.DPoint(-self.cpw_radius - proble_w / 2.0 - self.cpw_gap - nprobe_w - self.lp[0],
                          self.cpw_radius + taperL + probe_L),
               pya.DPoint(-self.cpw_radius - proble_w / 2.0 - self.cpw_gap - nprobe_w - self.lp[0], tmp_w),
               pya.DPoint(self.wg_length + self.cpw_radius + proble_w / 2.0 + self.cpw_gap + nprobe_w + self.lp[1],
                          tmp_w),
               pya.DPoint(self.wg_length + self.cpw_radius + proble_w / 2.0 + self.cpw_gap + nprobe_w + self.lp[1],
                          self.cpw_radius + taperL + probe_L)]
        poly = pya.Polygon.from_dpoly(pya.DPolygon(pts))
        rpoly = poly.round_corners(0.0 / self.dbu, 5.0 / self.dbu, 128)
        ep = pya.EdgeProcessor()
        out = ep.boolean_p2p(poly2, [rpoly], pya.EdgeProcessor.ModeBNotA, False, False)
        for p in out:
            shape.insert(p)
        for p in poly1:
            shape.insert(p)

    def get_ports(self):
        return self.ports


class Eam_STW:
    def __init__(self, mesa_width_in=1.4,
                 mesa_width_hybrid=3.0,
                 mqw_width_in=1.8,
                 mqw_width_hybrid=4.0,
                 nInP_width=50.0,
                 nInP_length=300.0,
                 taper1=90.0,
                 taper2=15.0,
                 nmetal_gap=8.0,
                 cpw_gap=18.0,
                 cpw_radius=30.0,
                 cpw_width=10.0,
                 lay_mesa=None,
                 lay_mqw=None,
                 lay_nInP=None,
                 lay_nmetal=None,
                 lay_pvia=None,
                 lay_nvia=None,
                 lay_probe=None,
                 dbu=None,
                 len_arr=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if lay_mesa is None:
            lay_mesa = pya.CellView.active().layout().layer(1, 1)
        if lay_mqw is None:
            lay_mqw = pya.CellView.active().layout().layer(3, 1)
        if lay_nInP is None:
            lay_nInP = pya.CellView.active().layout().layer(4, 1)
        if lay_nmetal is None:
            lay_nmetal = pya.CellView.active().layout().layer(5, 1)
        if lay_pvia is None:
            lay_pvia = pya.CellView.active().layout().layer(8, 1)
        if lay_nvia is None:
            lay_nvia = pya.CellView.active().layout().layer(7, 1)
        if lay_probe is None:
            lay_probe = pya.CellView.active().layout().layer(9, 1)
        if len_arr is None:
            len_arr = [100.0, 50.0, 100.0, 100.0, 50.0, 200.0, 200.0, 100.0, 300.0]

        self.dbu = dbu
        self.mesa_width_in = mesa_width_in / self.dbu
        self.mesa_width_hybrid = mesa_width_hybrid / self.dbu
        self.mqw_width_in = mqw_width_in / self.dbu
        self.mqw_width_hybrid = mqw_width_hybrid / self.dbu
        self.nInP_width = nInP_width / self.dbu
        self.taper1 = taper1 / self.dbu
        self.taper2 = taper2 / self.dbu
        self.nmetal_gap = nmetal_gap / self.dbu
        self.lay_mesa = lay_mesa
        self.lay_mqw = lay_mqw
        self.lay_nInP = lay_nInP
        self.lay_nmetal = lay_nmetal
        self.lay_pvia = lay_pvia
        self.lay_nvia = lay_nvia
        self.lay_probe = lay_probe
        self.nprobe_w = (self.nInP_width - self.nmetal_gap - 6.0 / self.dbu) / 2.0
        self.nproble_l = 20.0 / self.dbu
        self.cpw_radius = cpw_radius / self.dbu
        self.cpw_gap = cpw_gap / self.dbu
        self.cpw_width = cpw_width / self.dbu
        self.ports = []
        self.len_arr = [l / self.dbu for l in len_arr]

    def shapes(self, cell):
        self.ports = []
        self.ports.append(Ports(width=self.mesa_width_hybrid,
                                direction=math.pi,
                                face_angle=math.pi + math.pi / 2.0,
                                point=pya.DPoint(0.0, 0.0)))
        shape = cell.shapes(self.lay_mesa)
        self._mesa(shape)
        shape = cell.shapes(self.lay_mqw)
        self._mqw(shape)
        shape = cell.shapes(self.lay_nInP)
        self._nInP(shape)
        shape = cell.shapes(self.lay_nmetal)
        self._nmetal(shape)
        shape = cell.shapes(self.lay_pvia)
        self._pvia(shape)
        shape = cell.shapes(self.lay_nvia)
        self._nvia(shape)
        shape = cell.shapes(self.lay_probe)
        self._probe(shape)

    def _mesa(self, shape):
        start_x = 0.0
        for iter_i in range(len(self.len_arr) // 3):
            tmpl = self.len_arr[iter_i * 3 + 1]
            pts = [pya.DPoint(start_x, 0.0), pya.DPoint(tmpl + start_x, 0.0)]
            wg = Waveguide(pts, self.mesa_width_hybrid)
            shape.insert(wg.poly())
            pts = [pya.DPoint(-self.taper2 + start_x, 0.0), pya.DPoint(start_x, 0.0)]
            taper = Taper(pts, self.mesa_width_in, self.mesa_width_hybrid)
            shape.insert(taper.poly())
            t1 = pya.Trans(pya.DTrans.M90)
            t2 = pya.Trans(tmpl + start_x * 2.0, 0.0)
            shape.insert(taper.poly().transformed(t1).transformed(t2))

            exten_length = 18.0 / self.dbu
            pts = [pya.DPoint(-self.taper2 - exten_length + start_x, 0.0),
                   pya.DPoint(-self.taper2 + start_x, 0.0)]
            wg = Waveguide(pts, self.mesa_width_in)
            shape.insert(wg.poly())
            t1 = pya.Trans(pya.DTrans.M90)
            t2 = pya.Trans(tmpl + start_x * 2.0, 0.0)
            shape.insert(wg.poly().transformed(t1).transformed(t2))
            start_x = tmpl + start_x + self.len_arr[iter_i * 3 + 2]

    def _mqw(self, shape):
        tmpl = 0
        for iter_i in range(len(self.len_arr) // 3):
            tmpl += self.len_arr[iter_i * 3 + 1] + self.len_arr[iter_i * 3 + 2]
        tmpl -= self.len_arr[-1]
        pts = [pya.DPoint(-self.taper2, 0.0), pya.DPoint(tmpl + self.taper2, 0.0)]
        wg = Waveguide(pts, self.mqw_width_hybrid)
        shape.insert(wg.poly())
        pts = [pya.DPoint(-self.taper1 - self.taper2, 0.0), pya.DPoint(-self.taper2, 0.0)]
        taper = Taper(pts, self.mqw_width_in, self.mqw_width_hybrid)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(tmpl, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))
        tip = Circle(pya.DPoint(-self.taper1 - self.taper2, 0.0), self.mqw_width_in / 2.0, 90.0, 270)
        shape.insert(tip.poly())
        shape.insert(tip.poly().transformed(t1).transformed(t2))

        tmpw = [(self.mqw_width_hybrid - 1.5 / self.dbu) / 2.0,
                self.mqw_width_hybrid - 1.5 / self.dbu,
                self.mqw_width_hybrid]
        offset = 220.0 / self.dbu
        for iter_i in range(1, 4):
            pts = [pya.DPoint(offset + self.nproble_l, -self.nInP_width / 2.0 - 10.0 * iter_i / self.dbu),
                   pya.DPoint(offset + 100.0 / self.dbu + self.nproble_l,
                              -self.nInP_width / 2.0 - 10.0 * iter_i / self.dbu)]
            wg = Waveguide(pts, tmpw[iter_i - 1])
            shape.insert(wg.poly())

    def _nInP(self, shape):
        tmpl = 0
        for iter_i in range(len(self.len_arr) // 3):
            tmpl += self.len_arr[iter_i * 3 + 1] + self.len_arr[iter_i * 3 + 2]
        tmpl -= self.len_arr[-1]
        # taper section
        pts = [pya.DPoint(-self.taper1 - self.taper2, 0.0), pya.DPoint(-self.taper2, 0.0)]
        taper = Taper(pts, self.mesa_width_in, 10.0 / self.dbu)
        shape.insert(taper.poly())
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(tmpl, 0.0)
        shape.insert(taper.poly().transformed(t1).transformed(t2))
        tip = Circle(pya.DPoint(-self.taper1 - self.taper2, 0.0), self.mesa_width_in / 2.0, 90.0, 270)
        shape.insert(tip.poly())
        shape.insert(tip.poly().transformed(t1).transformed(t2))

        start_x = 0.0
        for iter_i in range(len(self.len_arr) // 3):
            tmpl = self.len_arr[iter_i * 3 + 1]
            # wg section
            pts = [pya.DPoint(-self.taper2 + start_x, 0.0),
                   pya.DPoint(tmpl + self.taper2 + start_x, 0.0)]
            wg = Waveguide(pts, self.nInP_width)
            shape.insert(wg.poly())
            # wg section
            if iter_i > 0:
                pts = [pya.DPoint(start_x - self.len_arr[iter_i * 3] + self.taper2, 0.0),
                       pya.DPoint(-self.taper2 + start_x, 0.0)]
                wg = Waveguide(pts, 10.0 / self.dbu)
                shape.insert(wg.poly())
            # nprobe_section
            offset = 2.0 / self.dbu
            pts = [pya.DPoint(-self.nproble_l / 2.0 - offset + start_x,
                              -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
                   pya.DPoint(self.nproble_l / 2.0 + offset + start_x,
                              -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
            wg = Waveguide(pts, self.nprobe_w + offset)
            shape.insert(wg.poly())
            t1 = pya.Trans(pya.Trans.M0)
            t2 = pya.Trans(tmpl, 0.0)
            shape.insert(wg.poly().transformed(t1))
            shape.insert(wg.poly().transformed(t2))
            shape.insert(wg.poly().transformed(t1).transformed(t2))
            start_x = tmpl + start_x + self.len_arr[iter_i * 3 + 2]

    def _nmetal(self, shape):
        start_x = 0.0
        for iter_i in range(len(self.len_arr) // 3):
            tmpl = self.len_arr[iter_i * 3 + 1]
            offset = 3.0 / self.dbu
            pts = [pya.DPoint(start_x, -self.nmetal_gap / 2.0 - offset / 2.0),
                   pya.DPoint(start_x + tmpl, -self.nmetal_gap / 2.0 - offset / 2.0)]
            wg = Waveguide(pts, offset)
            shape.insert(wg.poly())
            t1 = pya.Trans(pya.Trans.M0)
            shape.insert(wg.poly().transformed(t1))

            nmetal_length = tmpl + self.nproble_l + 6.0 / self.dbu
            pts = [pya.DPoint(start_x + tmpl / 2.0 - nmetal_length / 2.0,
                              -self.nInP_width / 2.0 + self.nprobe_w / 2.0),
                   pya.DPoint(start_x + tmpl / 2.0 + nmetal_length / 2.0,
                              -self.nInP_width / 2.0 + self.nprobe_w / 2.0)]
            wg = Waveguide(pts, self.nprobe_w)
            shape.insert(wg.poly())
            t1 = pya.Trans(pya.Trans.M0)
            shape.insert(wg.poly().transformed(t1))

            offset = 1.5 / self.dbu
            pts = [pya.DPoint(start_x - self.nproble_l / 2.0 - offset,
                              -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
                   pya.DPoint(start_x + self.nproble_l / 2.0 + offset,
                              -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
            wg = Waveguide(pts, self.nprobe_w + offset)
            shape.insert(wg.poly())
            t1 = pya.Trans(pya.Trans.M0)
            t2 = pya.Trans(tmpl, 0.0)
            shape.insert(wg.poly().transformed(t1))
            shape.insert(wg.poly().transformed(t2))
            shape.insert(wg.poly().transformed(t1).transformed(t2))
            start_x = tmpl + start_x + self.len_arr[iter_i * 3 + 2]

    def _pvia(self, shape):
        start_x = 0.0
        for iter_i in range(len(self.len_arr) // 3):
            tmpl = self.len_arr[iter_i * 3 + 1]
            offset = 1.0 / self.dbu
            pts = [pya.DPoint(start_x + offset / 2.0, 0.0),
                   pya.DPoint(start_x + tmpl - offset / 2.0, 0.0)]
            wg = Waveguide(pts, self.mesa_width_hybrid - offset)
            shape.insert(wg.poly())
            t1 = pya.Trans(pya.Trans.M0)
            shape.insert(wg.poly().transformed(t1))

            offset = 1.0 / self.dbu
            pts = [pya.DPoint(start_x - self.nproble_l / 2.0 - offset,
                              -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
                   pya.DPoint(start_x + self.nproble_l / 2.0 + offset,
                              -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
            wg = Waveguide(pts, self.nprobe_w)
            shape.insert(wg.poly())
            t1 = pya.Trans(pya.Trans.M0)
            t2 = pya.Trans(tmpl, 0.0)
            shape.insert(wg.poly().transformed(t1))
            shape.insert(wg.poly().transformed(t2))
            shape.insert(wg.poly().transformed(t1).transformed(t2))
            start_x = tmpl + start_x + self.len_arr[iter_i * 3 + 2]

    def _nvia(self, shape):
        start_x = 0.0
        for iter_i in range(len(self.len_arr) // 3):
            tmpl = self.len_arr[iter_i * 3 + 1]
            offset = 1.0 / self.dbu
            smaller = 1.0 / self.dbu
            pts = [pya.DPoint(start_x - self.nproble_l / 2.0,
                              -self.nInP_width / 2.0 - self.nprobe_w / 2.0),
                   pya.DPoint(start_x + self.nproble_l / 2.0,
                              -self.nInP_width / 2.0 - self.nprobe_w / 2.0)]
            wg = Waveguide(pts, self.nprobe_w - 2.0 * smaller)
            shape.insert(wg.poly())
            t1 = pya.Trans(pya.Trans.M0)
            t2 = pya.Trans(tmpl, 0.0)
            shape.insert(wg.poly().transformed(t1))
            shape.insert(wg.poly().transformed(t2))
            shape.insert(wg.poly().transformed(t1).transformed(t2))
            start_x = tmpl + start_x + self.len_arr[iter_i * 3 + 2]

    def _probe(self, shape):
        tmpl = 0
        for iter_i in range(len(self.len_arr) // 3):
            tmpl += self.len_arr[iter_i * 3 + 1] + self.len_arr[iter_i * 3 + 2]
        tmpl -= self.len_arr[-1]
        poly1 = []
        poly2 = []
        t1 = pya.Trans(pya.DTrans.M90)
        t2 = pya.Trans(tmpl + self.len_arr[-1] - self.len_arr[0], 0.0)
        t3 = pya.Trans()
        pts = [pya.DPoint(-self.cpw_radius - self.len_arr[0], self.cpw_radius),
               pya.DPoint(-self.cpw_radius - self.len_arr[0], 0.0),
               pya.DPoint(tmpl + self.cpw_radius + self.len_arr[-1], 0.0),
               pya.DPoint(tmpl + self.cpw_radius + self.len_arr[-1], self.cpw_radius)]
        pts = round_corners(pts, self.cpw_radius, 2.0)
        wg = Waveguide(pts, self.cpw_width, 0, 0, -90.0, 90.0)
        poly1.append(wg.poly())
        wg = Waveguide(pts, self.cpw_width + self.cpw_gap * 2.0, 0, 0, -90.0, 90.0)
        poly2.append(wg.poly())

        taperL = 30.0 / self.dbu
        proble_w = 90.0 / self.dbu
        pts = [pya.DPoint(-self.cpw_radius - self.len_arr[0], self.cpw_radius),
               pya.DPoint(-self.cpw_radius - self.len_arr[0], self.cpw_radius + taperL)]
        taper = Taper(pts, self.cpw_width, proble_w)
        poly = taper.poly()
        poly1.append(poly)
        poly1.append(poly.transformed(t1).transformed(t2).transformed(t3))
        taper = Taper(pts, self.cpw_width + self.cpw_gap * 2.0, proble_w + self.cpw_gap * 2.0)
        poly = taper.poly()
        poly2.append(poly)
        poly2.append(poly.transformed(t1).transformed(t2).transformed(t3))

        probe_L = 80.0 / self.dbu
        pts = [pya.DPoint(-self.cpw_radius - self.len_arr[0], self.cpw_radius + taperL),
               pya.DPoint(-self.cpw_radius - self.len_arr[0], self.cpw_radius + taperL + probe_L)]
        wg = Waveguide(pts, proble_w)
        poly = wg.poly()
        poly1.append(poly)
        poly1.append(poly.transformed(t1).transformed(t2).transformed(t3))
        wg = Waveguide(pts, proble_w + self.cpw_gap * 2.0)
        poly = wg.poly()
        poly2.append(poly)
        poly2.append(poly.transformed(t1).transformed(t2).transformed(t3))
        nprobe_w = 90.0 / self.dbu
        tmp_w = -50.0 / self.dbu
        pts = [pya.DPoint(-self.cpw_radius - proble_w / 2.0 - self.cpw_gap - nprobe_w - self.len_arr[0],
                          self.cpw_radius + taperL + probe_L),
               pya.DPoint(-self.cpw_radius - proble_w / 2.0 - self.cpw_gap - nprobe_w - self.len_arr[0], tmp_w),
               pya.DPoint(tmpl + self.cpw_radius + proble_w / 2.0 + self.cpw_gap + nprobe_w + self.len_arr[-1],
                          tmp_w),
               pya.DPoint(tmpl + self.cpw_radius + proble_w / 2.0 + self.cpw_gap + nprobe_w + self.len_arr[-1],
                          self.cpw_radius + taperL + probe_L)]
        poly = pya.Polygon.from_dpoly(pya.DPolygon(pts))
        rpoly = poly.round_corners(0.0 / self.dbu, 5.0 / self.dbu, 128)
        ep = pya.EdgeProcessor()
        out = ep.boolean_p2p(poly2, [rpoly], pya.EdgeProcessor.ModeBNotA, False, False)
        for p in out:
            shape.insert(p)
        for p in poly1:
            shape.insert(p)

    def get_ports(self):
        return self.ports


if __name__ == "__main__":
    layout = pya.Layout()
    dbu = 0.001
    layout.dbu = dbu

    lay_mesa = layout.layer(1, 1)
    lay_mqw = layout.layer(3, 1)
    lay_nInP = layout.layer(4, 1)
    lay_nmetal = layout.layer(5, 1)
    lay_pvia = layout.layer(8, 1)
    lay_nvia = layout.layer(7, 1)
    lay_probe = layout.layer(9, 1)

    cell = layout.create_cell("Eam_TW_LUMP")
    wg35 = Eam_TW_LUMP(dbu=dbu, lay_mesa=lay_mesa, lay_mqw=lay_mqw, lay_nInP=lay_nInP,
                       lay_nmetal=lay_nmetal, lay_pvia=lay_pvia, lay_nvia=lay_nvia, lay_probe=lay_probe)
    wg35.shapes(cell)

    cell = layout.create_cell("Eam_STW")
    wg35 = Eam_STW(dbu=dbu, lay_mesa=lay_mesa, lay_mqw=lay_mqw, lay_nInP=lay_nInP,
                   lay_nmetal=lay_nmetal, lay_pvia=lay_pvia, lay_nvia=lay_nvia, lay_probe=lay_probe)
    wg35.shapes(cell)

    cell = layout.create_cell("Eam_TW")
    wg35 = Eam_TW(dbu=dbu, lay_mesa=lay_mesa, lay_mqw=lay_mqw, lay_nInP=lay_nInP,
                  lay_nmetal=lay_nmetal, lay_pvia=lay_pvia, lay_nvia=lay_nvia, lay_probe=lay_probe)
    wg35.shapes(cell)

    cell = layout.create_cell("Eam_Lump")
    wg35 = Eam_Lump(dbu=dbu, lay_mesa=lay_mesa, lay_mqw=lay_mqw, lay_nInP=lay_nInP,
                    lay_nmetal=lay_nmetal, lay_pvia=lay_pvia, lay_nvia=lay_nvia, lay_probe=lay_probe)
    wg35.wg_length_set(80.0 / dbu)
    wg35.wg_length_set(100.0 / dbu)
    wg35.shapes(cell)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
