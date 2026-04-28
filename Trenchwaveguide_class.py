# Trenchwaveguide_class.py - converted from Ruby to Python using Klayout pya API
import pya
import math
import os
from waveguide import *


class Trenchwaveguide:
    def __init__(self, pts,
                 wg_width=2.0,
                 trench_width=3.0,
                 start_face_angle=None,
                 end_face_angle=None,
                 start_angle=None,
                 end_angle=None,
                 lay_wg=None,
                 lay_trwg=None,
                 self_poly_flag=0,
                 dbu=None):
        if dbu is None:
            dbu = pya.CellView.active().layout().dbu
        if lay_wg is None:
            lay_wg = pya.CellView.active().layout().layer(1, 0)
        if lay_trwg is None:
            lay_trwg = pya.CellView.active().layout().layer(1, 1)

        self._dbu = dbu
        self._pts = [p * (1 / self._dbu) for p in pts]
        self._wg_width = wg_width / self.dbu
        self._trench_width = trench_width / self.dbu
        self._start_face_angle = start_face_angle
        self._end_face_angle = end_face_angle
        self.self_poly_flag = self_poly_flag
        self._start_angle = start_angle
        self._end_angle = end_angle
        self._lay_wg = lay_wg
        self._lay_trwg = lay_trwg
        self.ports = []

    @property
    def pts(self):
        return self._pts

    @pts.setter
    def pts(self, pt):
        self._pts = [p * (1 / self.dbu) for p in pt]

    @property
    def dbu(self):
        return self._dbu

    @dbu.setter
    def dbu(self, unit):
        self._dbu = unit
        self._pts = [p * (1 / self._dbu) for p in self._pts]
        self._wg_width = self._wg_width / self._dbu
        self._trench_width = self._trench_width / self._dbu

    def shapes(self, cell):
        wg = Waveguide(self._pts, self._wg_width, self._start_face_angle, self._end_face_angle,
                       self._start_angle, self._end_angle, self.self_poly_flag)
        self.ports = []
        self.ports.append(Ports(width=self._wg_width,
                                direction=wg.start_angle + math.pi if wg.start_angle is not None else math.pi,
                                face_angle=self._start_face_angle,
                                point=self._pts[0]))
        self.ports.append(Ports(width=self._wg_width,
                                direction=wg.end_angle if wg.end_angle is not None else 0,
                                face_angle=self._start_face_angle,
                                point=self._pts[-1]))
        wgshape = cell.shapes(self._lay_wg)
        trshape = cell.shapes(self._lay_trwg)
        wgshape.insert(wg.poly())
        wg.width = self._trench_width
        trshape.insert(wg.poly())

    def get_ports(self):
        return self.ports


if __name__ == "__main__":
    layout = pya.Layout()
    dbu = 0.001
    layout.dbu = dbu

    cell = layout.create_cell("Top")
    pts = [pya.DPoint(0.0, 0.0), pya.DPoint(10.0, 0.0), pya.DPoint(10.0, 10.0),
           pya.DPoint(20.0, 30.0), pya.DPoint(10.0, 60.0)]
    pts = round_corners(pts, 5.0)
    tr = Trenchwaveguide(pts, 2.0, 4.0, dbu=dbu, lay_wg=layout.layer(1, 0), lay_trwg=layout.layer(1, 1))
    tr.trench_width = 6.0 / dbu
    tr.shapes(cell)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
