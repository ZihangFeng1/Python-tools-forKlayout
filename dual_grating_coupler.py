"""
dual_grating_coupler.py — 双边光栅耦合器
结构： 光栅 ← 锥形 ← [直波导] → 锥形 → 光栅
"""
import pya
import math
from waveguide import *


class DualGratingCoupler:
    def __init__(self,
                 period=0.64,        # 光栅周期 (μm)
                 duty=0.38,          # 占空比
                 width_in=0.45,      # 波导输入端宽度 (μm)
                 width_out=10.0,     # 光栅区宽度 (μm)
                 grating_length=15.0,  # 单侧光栅长度 (μm)
                 taper_length=150.0,   # 锥形长度 (μm)
                 wg_length=100.0,      # ★ 中间直波导长度 (μm) — 重点调整参数
                 layer=(1, 0),         # KLayout 层号
                 dbu=0.001):           # 数据库精度 (μm)
        self.dbu = dbu
        self.period = period / self.dbu
        self.duty = duty
        self.width_in = width_in / self.dbu
        self.width_out = width_out / self.dbu
        self.grating_length = grating_length / self.dbu
        self.taper_length = taper_length / self.dbu
        self.wg_length = wg_length / self.dbu
        self.behind_length = 5.0 / self.dbu
        self.layer = layer
        self.layer_index = None
        self.ports = []

    def _make_right_gc(self, cell, origin_x):
        """右侧光栅：锥形向左→x 正方向延伸"""
        x0 = origin_x
        # 锥形
        pts = [pya.DPoint(x0, 0.0), pya.DPoint(x0 + self.taper_length, 0.0)]
        self.ports.append(Ports(width=self.width_in,
                                direction=line_angle(pts[1], pts[0]),
                                face_angle=line_angle(pts[1], pts[0]) + math.pi / 2.0,
                                point=pts[0]))
        taper = Taper(pts, self.width_in, self.width_out, 'x')
        cell.shapes(self.layer_index).insert(taper.poly())

        # 光栅齿
        grtg_len = 0.0
        while grtg_len < self.grating_length:
            x_start = x0 + self.taper_length + grtg_len + self.period * (1 - self.duty)
            x_end = x0 + self.taper_length + grtg_len + self.period
            pts = [pya.DPoint(x_start, 0.0), pya.DPoint(x_end, 0.0)]
            wg = Waveguide(pts, self.width_out)
            cell.shapes(self.layer_index).insert(wg.poly())
            grtg_len += self.period

        # 尾部
        x_last = x0 + self.taper_length + grtg_len + self.period * (1 - self.duty)
        pts = [pya.DPoint(x_last, 0.0),
               pya.DPoint(x_last + self.behind_length, 0.0)]
        wg = Waveguide(pts, self.width_out)
        cell.shapes(self.layer_index).insert(wg.poly())

    def _make_left_gc(self, cell, origin_x):
        """左侧光栅：锥形向右→x 负方向延伸（镜像）"""
        x0 = origin_x
        # 锥形（从 x0 向左延伸）
        pts = [pya.DPoint(x0, 0.0), pya.DPoint(x0 - self.taper_length, 0.0)]
        self.ports.append(Ports(width=self.width_in,
                                direction=line_angle(pts[1], pts[0]),
                                face_angle=line_angle(pts[1], pts[0]) + math.pi / 2.0,
                                point=pts[0]))
        taper = Taper(pts, self.width_in, self.width_out, 'x')
        cell.shapes(self.layer_index).insert(taper.poly())

        # 光栅齿（向 -x 方向）
        grtg_len = 0.0
        while grtg_len < self.grating_length:
            x_start = x0 - self.taper_length - grtg_len - self.period * (1 - self.duty)
            x_end = x0 - self.taper_length - grtg_len - self.period
            pts = [pya.DPoint(x_start, 0.0), pya.DPoint(x_end, 0.0)]
            wg = Waveguide(pts, self.width_out)
            cell.shapes(self.layer_index).insert(wg.poly())
            grtg_len += self.period

        # 尾部
        x_last = x0 - self.taper_length - grtg_len - self.period * (1 - self.duty)
        pts = [pya.DPoint(x_last, 0.0),
               pya.DPoint(x_last - self.behind_length, 0.0)]
        wg = Waveguide(pts, self.width_out)
        cell.shapes(self.layer_index).insert(wg.poly())

    def shapes(self, cell, layout):
        self.layer_index = layout.layer(self.layer[0], self.layer[1])
        # 器件居中于 x=0, 总宽 = 2*(taper_length + grating_length) + wg_length
        half = self.taper_length + self.grating_length + self.wg_length / 2.0

        # 右侧光栅
        self._make_right_gc(cell, self.wg_length / 2.0)

        # 左侧光栅（镜像）
        self._make_left_gc(cell, -self.wg_length / 2.0)

        # 中间直波导：连接左右锥形的窄端
        pts_wg = [pya.DPoint(-self.wg_length / 2.0, 0.0),
                  pya.DPoint(self.wg_length / 2.0, 0.0)]
        wg_center = Waveguide(pts_wg, self.width_in)
        cell.shapes(self.layer_index).insert(wg_center.poly())

    def get_ports(self):
        return self.ports
