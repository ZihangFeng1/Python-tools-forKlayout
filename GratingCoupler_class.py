# GratingCoupler_class.py - converted from Ruby to Python using Klayout pya API
import pya
import math
import os
from waveguide import *


class GratingCoupler:
    def __init__(self, period=0.64,
                 duty=0.38,
                 width_in=0.45,
                 width_out=10.0,
                 grating_length=15.0,
                 taper_length=150.0,
                 layer_grating=None,
                 dbu=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if layer_grating is None:
            layer_grating = pya.CellView.active().layout().layer(1, 0)

        self.dbu = dbu
        self.period = period / self.dbu
        self.duty = duty
        self.width_in = width_in / self.dbu
        self.width_out = width_out / self.dbu
        self.grating_length = grating_length / self.dbu
        self.behind_length = 5.0 / self.dbu
        self.taper_length = taper_length / self.dbu
        self.layer_grating = layer_grating
        self.ports = []

    def shapes(self, cell):
        pts = [pya.DPoint(0.0, 0.0), pya.DPoint(self.taper_length, 0.0)]
        self.ports.append(Ports(width=self.width_in,
                                direction=line_angle(pts[1], pts[0]),
                                face_angle=line_angle(pts[1], pts[0]) + math.pi / 2.0,
                                point=pts[0]))
        taper = Taper(pts, self.width_in, self.width_out, 'x')
        cell.shapes(self.layer_grating).insert(taper.poly())

        grtg_len = 0
        while grtg_len < self.grating_length:
            pts = [pya.DPoint(self.taper_length + grtg_len + self.period * (1 - self.duty), 0.0),
                   pya.DPoint(self.taper_length + grtg_len + self.period, 0.0)]
            wg = Waveguide(pts, self.width_out)
            cell.shapes(self.layer_grating).insert(wg.poly())
            grtg_len = grtg_len + self.period

        pts = [pya.DPoint(self.taper_length + grtg_len + self.period * (1 - self.duty), 0.0),
               pya.DPoint(self.taper_length + grtg_len + self.behind_length, 0.0)]
        wg = Waveguide(pts, self.width_out)
        cell.shapes(self.layer_grating).insert(wg.poly())

    def get_ports(self):
        return self.ports


class FocusingGratingCoupler:
    """Reference: 'Reflectionless grating couplers for Silicon-on-Insulator photonic integrated circuits'
    Reference: 'Compact Focusing Grating Couplers for Silicon-on-Insulator Integrated Circuits'"""
    def __init__(self, period=0.64,
                 duty=0.50,
                 width_in=0.5,
                 width_out=0.5,
                 grating_length=15.5,
                 taper_length=1.0,
                 phi=10.0,  # incident angle
                 nc=1.0,  # cladding index
                 lambda0=1.55,  # centre wavelength
                 eta=36.56,  # aperture opening angle degree
                 r0=12.5,  # focusing length
                 layer_grating=None,
                 dbu=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if layer_grating is None:
            layer_grating = pya.CellView.active().layout().layer(1, 0)

        self.dbu = dbu
        self.period = period / self.dbu
        self.duty = duty
        self.width_in = width_in / self.dbu
        self.width_out = width_out / self.dbu
        self.grating_length = grating_length / self.dbu
        self.taper_length = taper_length / self.dbu
        self.phi = phi
        self.nc = nc
        self.lambda0 = lambda0 / self.dbu
        self.ns = self.lambda0 / self.period + self.nc * math.sin(self.phi / 180.0 * math.pi)
        self.eta = eta
        self.r0 = r0 / self.dbu
        self.layer_grating = layer_grating
        self.ports = []

    def shapes(self, cell):
        shape = []
        pts = [pya.DPoint(0.0, 0.0), pya.DPoint(self.taper_length, 0.0)]
        self.ports.append(Ports(width=self.width_in,
                                direction=line_angle(pts[1], pts[0]),
                                face_angle=line_angle(pts[1], pts[0]) + math.pi / 2.0,
                                point=pts[0]))
        taper = Taper(pts, self.width_in, self.width_out, 'x')
        shape.append(taper.poly())

        pts = [pya.DPoint(self.taper_length, self.width_out / 2.0),
               pya.DPoint(self.taper_length, -self.width_out / 2.0)]
        start_angle = -self.eta / 2.0
        end_angle = self.eta / 2.0
        f0 = pya.DPoint(self.taper_length, 0.0)
        q = self.r0 * (1 - self.nc / self.ns * math.sin(self.phi / 180.0 * math.pi)) * self.ns / self.lambda0
        a = q * self.lambda0 * self.ns / (self.ns ** 2 - (self.nc * math.sin(self.phi / 180.0 * math.pi)) ** 2)
        e = self.nc * math.sin(self.phi / 180.0 * math.pi) / self.ns
        pts = pts + linearc_ellipse(f0, a, e, start_angle, end_angle)
        poly = pya.DPolygon(pts)
        shape.append(pya.Polygon.from_dpoly(poly))

        grtg_len = 0
        q -= self.duty / 2.0
        while grtg_len < self.grating_length:
            q = q + 1.0
            a = q * self.lambda0 * self.ns / (self.ns ** 2 - (self.nc * math.sin(self.phi / 180.0 * math.pi)) ** 2)
            e = self.nc * math.sin(self.phi / 180.0 * math.pi) / self.ns
            pts_ellipse = linearc_ellipse(f0, a, e, start_angle, end_angle)
            shape.append(Waveguide(pts_ellipse, self.duty * self.period).poly())
            grtg_len = grtg_len + self.period

        for p in shape:
            cell.shapes(self.layer_grating).insert(p)

    def get_ports(self):
        return self.ports


class ReflectionlessFocusingGratingCoupler(FocusingGratingCoupler):
    def __init__(self, delta=30.0,
                 bend_radius=50.0,
                 straight_length=28.4,
                 period=0.551,
                 duty=0.40,
                 width_in=0.65,
                 width_out=1.0,
                 grating_length=21.5,
                 taper_length=30.0,
                 phi=10.0,
                 nc=1.543,
                 lambda0=1.55,
                 eta=56.0,
                 r0=16.54,
                 layer_grating=None,
                 dbu=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if layer_grating is None:
            layer_grating = pya.CellView.active().layout().layer(1, 0)
        super().__init__(period, duty, width_in, width_out, grating_length,
                         taper_length, phi, nc, lambda0, eta, r0, layer_grating, dbu)
        self.delta = delta
        self.bend_radius = bend_radius / self.dbu
        self.straight_length = straight_length / self.dbu
        self.ns = self.lambda0 / self.period + self.nc * math.sin(self.phi / 180.0 * math.pi) * \
            math.cos(self.delta / 180.0 * math.pi)

    def shapes(self, cell):
        shape = []
        pts = [pya.DPoint(0.0, 0.0), pya.DPoint(-self.straight_length, 0.0)]
        self.ports.append(Ports(width=self.width_in,
                                direction=line_angle(pts[1], pts[0]),
                                face_angle=line_angle(pts[1], pts[0]) + math.pi / 2.0,
                                point=pts[0]))
        centre = pya.DPoint(-self.straight_length, -self.bend_radius)
        pts += linearc(centre, self.bend_radius, 90.0, 120.0)
        offset = 2.0 / self.dbu
        pts += [pts[-1] - pya.DPoint(offset * math.cos(self.delta / 180.0 * math.pi),
                                      offset * math.sin(self.delta / 180.0 * math.pi))]
        wg = Waveguide(pts, self.width_in)
        shape.append(wg.poly())

        pts2 = [pts[-1], pts[-1] + pya.DPoint(-self.taper_length * math.cos(self.delta / 180.0 * math.pi),
                                               -self.taper_length * math.sin(self.delta / 180.0 * math.pi))]
        taper = Taper(pts2, self.width_in, self.width_out)
        shape.append(taper.poly())

        pts3 = [pts2[-1] + pya.DPoint(-self.width_out / 2.0 * math.sin(self.delta / 180.0 * math.pi),
                                       self.width_out / 2.0 * math.cos(self.delta / 180.0 * math.pi)),
                pts2[-1] + pya.DPoint(self.width_out / 2.0 * math.sin(self.delta / 180.0 * math.pi),
                                       -self.width_out / 2.0 * math.cos(self.delta / 180.0 * math.pi))]
        start_angle = -self.eta / 2.0 - self.delta
        end_angle = self.eta / 2.0 - self.delta
        f0 = pya.DPoint(-pts2[-1].x, pts2[-1].y)
        q = self.r0 * (1 - self.nc / self.ns * math.sin(self.phi / 180.0 * math.pi) *
                       math.cos(self.delta / 180.0 * math.pi)) * self.ns / self.lambda0
        a = q * self.lambda0 * self.ns / (self.ns ** 2 - (self.nc * math.sin(self.phi / 180.0 * math.pi)) ** 2)
        e = self.nc * math.sin(self.phi / 180.0 * math.pi) / self.ns
        tmp_pts = linearc_ellipse(f0, a, e, start_angle, end_angle)
        tmp_pts = [pya.DPoint(-p.x, p.y) for p in tmp_pts]
        pts_ellipse = pts3 + tmp_pts
        poly = pya.DPolygon(pts_ellipse)
        shape.append(pya.Polygon.from_dpoly(poly))

        q -= (self.duty / 2.0)
        grtg_len = 0
        while grtg_len < self.grating_length:
            q = q + 1.0
            a = q * self.lambda0 * self.ns / (self.ns ** 2 - (self.nc * math.sin(self.phi / 180.0 * math.pi)) ** 2)
            e = self.nc * math.sin(self.phi / 180.0 * math.pi) / self.ns
            pts_curve = linearc_ellipse(f0, a, e, start_angle, end_angle)
            pts_curve = [pya.DPoint(-p.x, p.y) for p in pts_curve]
            shape.append(pya.Polygon.from_dpoly(
                pya.DPath(pts_curve, self.duty * self.period,
                          self.duty * self.period / 2.0,
                          self.duty * self.period / 2.0, True).polygon()))
            grtg_len = grtg_len + self.period

        for p in shape:
            cell.shapes(self.layer_grating).insert(p)

    def get_ports(self):
        return self.ports


class ReflectionlessFocusingGratingCoupler_220nmSOI_70nmetch_1550nm(ReflectionlessFocusingGratingCoupler):
    def __init__(self, delta=30.0,
                 bend_radius=50.0,
                 straight_length=28.4,
                 period=0.551,
                 duty=0.40,
                 width_in=0.65,
                 width_out=1.0,
                 grating_length=21.5,
                 taper_length=30.0,
                 phi=10.0,
                 nc=1.543,
                 lambda0=1.55,
                 eta=56.0,
                 r0=16.54,
                 layer_grating=None,
                 dbu=None):
        super().__init__(delta, bend_radius, straight_length, period, duty,
                         width_in, width_out, grating_length, taper_length,
                         phi, nc, lambda0, eta, r0, layer_grating, dbu)


class FocusingGratingCoupler_220nmSOI_70nmetch_1550nm(FocusingGratingCoupler):
    def __init__(self, period=0.63,
                 duty=0.50,
                 width_in=0.5,
                 width_out=0.5,
                 grating_length=15.5,
                 taper_length=1.0,
                 phi=10.0,
                 nc=1.0,
                 lambda0=1.55,
                 eta=36.56,
                 r0=12.5,
                 layer_grating=None,
                 dbu=None):
        super().__init__(period, duty, width_in, width_out, grating_length,
                         taper_length, phi, nc, lambda0, eta, r0, layer_grating, dbu)


class GratingCoupler_340nmSOI_200nmetch_1550nm(GratingCoupler):
    def __init__(self, period=0.64,
                 duty=0.38,
                 width_in=0.45,
                 width_out=10.0,
                 grating_length=15.0,
                 taper_length=150.0,
                 layer_grating=None,
                 dbu=None):
        super().__init__(period, duty, width_in, width_out, grating_length,
                         taper_length, layer_grating, dbu)


if __name__ == "__main__":
    layout = pya.Layout()
    dbu = 0.001
    layout.dbu = dbu

    cell = layout.create_cell("GC_340nm")
    gcoupler = GratingCoupler_340nmSOI_200nmetch_1550nm(dbu=dbu, layer_grating=layout.layer(1, 0))
    gcoupler.shapes(cell)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
