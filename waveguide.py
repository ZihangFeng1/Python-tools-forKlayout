import pya
import math


# ============================================================
# Helper functions
# ============================================================

def vector_angle(v1, v2):
    """define the angle of the vector v1, v2"""
    vcross = v1.x * v2.y - v1.y * v2.x
    vdot = v1.x * v2.x + v1.y * v2.y
    val = vcross / math.sqrt(v1.sq_abs() * v2.sq_abs())
    if abs(val) > 1:
        val = val / abs(val) * 1
    if vdot >= 0:
        return math.asin(val)
    elif vcross != 0:
        return vcross / abs(vcross) * math.pi - math.asin(val)
    else:
        return math.pi - math.asin(val)


def line_angle(p1, p2):
    """define the angle of the vector p1->p2 with x axis"""
    v1 = pya.DPoint(1, 0)
    v2 = p2 - p1
    return vector_angle(v1, v2)


def cross_point(p1, dir1, p2, dir2):
    rad1 = dir1 / 180.0 * math.pi
    rad2 = dir2 / 180.0 * math.pi
    x0 = (p1.y - p2.y - math.tan(rad1) * p1.x + math.tan(rad2) * p2.x) / (math.tan(rad2) - math.tan(rad1))
    y0 = (p1.y * math.tan(rad2) - p2.y * math.tan(rad1) - math.tan(rad1) * math.tan(rad2) * (p1.x - p2.x)) / (math.tan(rad2) - math.tan(rad1))
    return x0, y0


def remove_straight_angles(pts):
    tmppts = []  # remove the same point
    for i, pt in enumerate(pts[:-1]):
        v1 = pt - pts[i + 1]
        if v1.sq_abs() < 1e-5:
            continue
        tmppts.append(pt)
    tmppts.append(pts[-1])

    newpts = [tmppts[0]]
    if 3 <= len(tmppts):
        for i, pt in enumerate(tmppts[1:-1]):
            v1 = pt - tmppts[i]
            v2 = tmppts[i + 2] - pt
            if abs(vector_angle(v1, v2)) < 1e-5:
                continue
            else:
                newpts.append(pt)
    elif 1 == len(tmppts):
        return newpts
    newpts.append(tmppts[-1])
    return newpts


def linearc(centre, radius, start_angle, end_angle, delta_angle=0.5):
    pts = []
    n = abs((end_angle - start_angle) / delta_angle)
    n = round(n)
    n = min(n, 1024)
    n = max(n, 1)
    if end_angle > start_angle:
        step = (end_angle - start_angle) / n
        current = start_angle
        for _ in range(int(n) + 1):
            pts.append(pya.DPoint(radius * math.cos(current * math.pi / 180.0),
                                  radius * math.sin(current * math.pi / 180.0)) + centre)
            current += step
    elif end_angle < start_angle:
        step = (start_angle - end_angle) / n
        current = start_angle
        for _ in range(int(n) + 1):
            pts.append(pya.DPoint(radius * math.cos(current * math.pi / 180.0),
                                  radius * math.sin(current * math.pi / 180.0)) + centre)
            current -= step
    return pts


def linearc_one_point_two_angle(p1, radius, start_angle, span_angle, delta_angle=0.5):
    """p1 on the curve"""
    end_angle = start_angle + span_angle
    centre = p1 - pya.DPoint(radius * math.cos(start_angle * math.pi / 180.0),
                              radius * math.sin(start_angle * math.pi / 180.0))
    return linearc(centre, radius, start_angle, end_angle, delta_angle)


def linearc_ellipse(f0, a, e, start_angle, end_angle, delta_angle=0.5):
    pts = []
    n = abs((end_angle - start_angle) / delta_angle)
    n = round(n)
    n = min(n, 1024)
    n = max(n, 1)
    if end_angle > start_angle:
        step = (end_angle - start_angle) / n
        current = start_angle
        for _ in range(int(n) + 1):
            r = a * (1 - e ** 2) / (1 - e * math.cos(current * math.pi / 180.0))
            x = r * math.cos(current * math.pi / 180.0)
            y = r * math.sin(current * math.pi / 180.0)
            pts.append(pya.DPoint(x, y) + f0)
            current += step
    elif end_angle < start_angle:
        step = (start_angle - end_angle) / n
        current = start_angle
        for _ in range(int(n) + 1):
            r = a * (1 - e ** 2) / (1 - e * math.cos(current * math.pi / 180.0))
            x = r * math.cos(current * math.pi / 180.0)
            y = r * math.sin(current * math.pi / 180.0)
            pts.append(pya.DPoint(x, y) + f0)
            current -= step
    return pts


def round_corners(pts, radius, delta_angle=0.5, ignore_flag=False):
    """pts is list of pya.DPoint"""
    pts = remove_straight_angles(pts)
    newpts = [pts[0]]
    if 2 <= len(pts):
        for i, pt in enumerate(pts[1:-1]):
            v1 = pt - pts[i]
            v2 = pts[i + 2] - pt
            beta = vector_angle(v1, v2)
            l1 = radius * math.tan(abs(beta) / 2.0)
            p1 = pya.DPoint(l1 / math.sqrt(v1.sq_abs()) * (pts[i].x - pt.x) + pt.x,
                            l1 / math.sqrt(v1.sq_abs()) * (pts[i].y - pt.y) + pt.y)
            p2 = pya.DPoint(l1 / math.sqrt(v2.sq_abs()) * (pts[i + 2].x - pt.x) + pt.x,
                            l1 / math.sqrt(v2.sq_abs()) * (pts[i + 2].y - pt.y) + pt.y)
            if ((p1 - pt).sq_abs() - (newpts[-1] - pt).sq_abs() <= 1e-3) and \
               ((p2 - pt).sq_abs() - (pts[i + 2] - pt).sq_abs() <= 1e-3):
                r = radius
            else:
                lv1 = math.sqrt(v1.sq_abs())
                lv2 = math.sqrt(v2.sq_abs())
                if lv1 >= lv2:
                    r = lv2 / math.tan(abs(beta) / 2.0)
                    p1 = pya.DPoint(lv2 / math.sqrt(v1.sq_abs()) * (pts[i].x - pt.x) + pt.x,
                                    lv2 / math.sqrt(v1.sq_abs()) * (pts[i].y - pt.y) + pt.y)
                else:
                    r = lv1 / math.tan(abs(beta) / 2.0)
                    p1 = newpts[-1]
                if not ignore_flag:
                    raise Exception(f"The Bend radius {radius} is too large, min Radius {r}.")
            xdir = pya.DPoint(1, 0)
            start_angle = vector_angle(xdir, v1) - beta / abs(beta) * math.pi / 2.0
            end_angle = start_angle + beta
            c0 = pya.DPoint(p1.x + r * math.cos(math.pi + start_angle),
                            p1.y + r * math.sin(math.pi + start_angle))
            temp_pts = linearc(c0, r, start_angle / math.pi * 180.0, end_angle / math.pi * 180.0, delta_angle)
            newpts = newpts + temp_pts
    newpts.append(pts[-1])
    return newpts


def counterclockwise_rotate(p, angle):
    """angle in rad"""
    return pya.DPoint(p.x * math.cos(angle) + p.y * math.sin(angle),
                      -p.x * math.sin(angle) + p.y * math.cos(angle))


def sbend(p_in1, dir_in1, p_in2, dir_in2, bend_radius, delta_angle=0.5):
    # transform
    rotrad = dir_in1 * math.pi / 180.0
    p1 = pya.DPoint(0.0, 0.0)
    dir1 = 0
    tmp = p_in2 - p_in1  # Move
    p2 = counterclockwise_rotate(tmp, rotrad)  # counterclockwise Rotate
    dir2 = dir_in2 - dir_in1
    flag = 0  # 0 can be directly connected, 1 connected by one circle, 2 connect by two circles
    p0 = pya.DPoint(0.0, 0.0)  # cross point, when flag == 1

    if dir1 == dir2:  # parallel
        angle1 = line_angle(p1, p2) / math.pi * 180.0
        if 1e-6 > abs(angle1 - dir1):
            flag = 0
        else:
            flag = 2
    else:
        if 90.0 == dir2 % 180.0:
            xcross = p2.x
        elif 0 == dir2 % 180.0:
            xcross = -1
        else:
            xcross = p2.x - p2.y / math.tan(dir2 / 180.0 * math.pi)
        p0 = pya.DPoint(xcross, 0.0)
        if xcross > 0:
            dp1 = p2 - p0
            dp2 = pya.DPoint(math.cos(dir2 * math.pi / 180.0), math.sin(dir2 * math.pi / 180.0))
            dot = dp1.x * dp2.x + dp1.y * dp2.y
            if dot > 0:
                if abs(p2.y) - (bend_radius + bend_radius * abs(math.cos(dir2 / 180.0 * math.pi))) < 1e-3:
                    flag = 1
                else:
                    flag = 2
            else:
                flag = 2
        elif xcross <= 0:
            flag = 2
        else:
            raise Exception(f"angle2 error")

    if flag == 0:
        pts = [p1, p2]
    elif flag == 1:
        pts = [p1, p0, p2]
        pts = round_corners(pts, bend_radius, delta_angle)
    elif flag == 2:
        alpha = dir2 / 180.0 * math.pi
        dy = p2.y - p1.y
        dx = p2.x - p1.x
        if ((dy > 0) or (dy == 0 and dir2 < 0)) and (dx > 0):
            tmp_v = (1 + math.cos(alpha) - dy / bend_radius) / 2.0
            if tmp_v < 0:
                start_angle = 270.0
                span_angle = 90.0
                dir2_mod = dir2 % 360.0
                if dir2_mod < 90.0 and dir2_mod >= 0.0:
                    pt2 = pya.DPoint(p2.x - 2 * bend_radius + bend_radius * math.sin(alpha), 0.0)
                elif dir2_mod < 180.0 and dir2_mod >= 90.0:
                    pt2 = pya.DPoint(p2.x - bend_radius * math.sin(alpha), 0.0)
                elif dir2_mod < 270.0 and dir2_mod >= 180.0:
                    pt2 = pya.DPoint(p2.x - bend_radius * math.sin(alpha), 0.0)
                elif dir2_mod < 360.0 and dir2_mod >= 270.0:
                    pt2 = pya.DPoint(p2.x - 2 * bend_radius + bend_radius * math.sin(alpha), 0.0)
                if pt2.x < -1e-6:
                    raise Exception(f"Input 'Bend radius = {bend_radius}' is too large in sbend function.")
                pts1 = linearc_one_point_two_angle(pt2, bend_radius, start_angle, span_angle, delta_angle)
                p3 = pts1[-1]
                dir3 = 90.0
                pts2 = sbend(p3, dir3, p2, dir2, bend_radius, delta_angle)
                pts = [p1, pt2] + pts1 + pts2
            else:
                theta1 = math.acos((1 + math.cos(alpha) - dy / bend_radius) / 2.0)
                cdx = bend_radius * (2.0 * math.sin(theta1) - math.sin(alpha))
                dx = p2.x - p1.x
                if cdx > dx:
                    raise Exception(f"Input 'Bend radius = {bend_radius}' is too large in sbend function.")
                startp = pya.DPoint(dx - cdx, p1.y)
                pts1 = linearc_one_point_two_angle(startp, bend_radius, 270.0,
                                                    theta1 / math.pi * 180.0, delta_angle)
                theta2 = theta1 - alpha
                pts2 = linearc_one_point_two_angle(pts1[-1], bend_radius,
                                                    90.0 + theta1 / math.pi * 180.0,
                                                    -theta2 / math.pi * 180.0, delta_angle)
                pts = [p1] + pts1 + pts2 + [p2]
        elif ((dy < 0) or (dy == 0 and dir2 > 0)) and (dx > 0):  # mirror x = 0
            p2_mirror = pya.DPoint(p2.x, -p2.y)
            dir2_mirror = -dir2
            pts1 = sbend(p1, dir1, p2_mirror, dir2_mirror, bend_radius, delta_angle)
            pts1_mirrored = [pya.DPoint(pt.x, -pt.y) for pt in pts1]
            pts = [p1] + pts1_mirrored
        elif (dx <= 0) and abs(dy) > 2.0 * bend_radius:
            if dy > 0:
                start_angle = 270.0
                span_angle = 90.0
                pts1 = linearc_one_point_two_angle(p1, bend_radius, start_angle, span_angle, delta_angle)
                p3 = pts1[-1]
                dir3 = 90.0
                pts2 = sbend(p3, dir3, p2, dir2, bend_radius, delta_angle)
                pts = [p1] + pts1 + pts2
            elif dy < 0:
                p2_mirror = pya.DPoint(p2.x, -p2.y)
                dir2_mirror = -dir2
                pts1 = sbend(p1, dir1, p2_mirror, dir2_mirror, bend_radius, delta_angle)
                pts = [p1] + [pya.DPoint(pt.x, -pt.y) for pt in pts1]
        else:
            raise Exception(
                f"The Bend radius {bend_radius} is too large. Or, the two points are too close. "
                "To be continued in sbend function")

    pts = [counterclockwise_rotate(pt, -rotrad) for pt in pts]
    pts = [pt + p_in1 for pt in pts]
    return pts


# ============================================================
# Waveguide class
# ============================================================

class Waveguide:
    def __init__(self, pts, width, start_face_angle=None, end_face_angle=None,
                 start_angle=None, end_angle=None, self_poly_flag=0):
        pts = remove_straight_angles(pts)
        self._wg = pya.DPath(pts, width)
        self.self_poly_flag = self_poly_flag
        if 1 == self._wg.num_points():
            self._start_point = pts[0]
            self._end_point = pts[0]
            self._start_angle = None
            self._end_angle = None
            self._start_face_angle = None
            self._end_face_angle = None
        else:
            self._start_point = pts[0]
            self._end_point = pts[-1]
            self._start_angle = line_angle(pts[0], pts[1])
            self._end_angle = line_angle(pts[-2], pts[-1])
            if start_face_angle is not None:
                self._start_face_angle = start_face_angle / 180.0 * math.pi
                if start_angle is not None:
                    self._start_angle = start_angle / 180.0 * math.pi
                else:
                    raise Exception('start_angle without parameter!')
                if self._start_face_angle < self._start_angle:
                    self._start_face_angle += math.pi
                self.self_poly_flag = 1
            else:
                self._start_face_angle = self._start_angle + math.pi / 2 if self._start_angle is not None else None

            if end_face_angle is not None:
                self._end_face_angle = end_face_angle / 180.0 * math.pi
                if end_angle is not None:
                    self._end_angle = end_angle / 180.0 * math.pi
                else:
                    raise Exception('end_angle without parameter!')
                if self._end_face_angle < self._end_angle:
                    self._end_face_angle += math.pi
                self.self_poly_flag = 1
            else:
                self._end_face_angle = self._end_angle + math.pi / 2 if self._end_angle is not None else None

        self._polygon = None

    @property
    def start_point(self):
        return self._start_point

    @property
    def end_point(self):
        return self._end_point

    @property
    def start_angle(self):
        return self._start_angle

    @property
    def end_angle(self):
        return self._end_angle

    @property
    def start_face_angle(self):
        return self._start_face_angle

    @start_face_angle.setter
    def start_face_angle(self, angle):
        self._start_face_angle = angle / 180.0 * math.pi
        self.self_poly_flag = 1

    @property
    def end_face_angle(self):
        return self._end_face_angle

    @end_face_angle.setter
    def end_face_angle(self, angle):
        self._end_face_angle = angle / 180.0 * math.pi
        self.self_poly_flag = 1

    @property
    def wg(self):
        return self._wg

    @property
    def width(self):
        return self._wg.width

    @width.setter
    def width(self, w):
        self._wg.width = w

    @property
    def wg_length(self):
        return pya.Path.from_dpath(self._wg).length()

    def transformed(self, t=None):
        if t is None:
            t = pya.DCplxTrans(1, 0, False, 0, 0)
        if self._polygon is None:
            self.poly()
        return pya.Polygon.from_dpoly(self._polygon.transformed(t))

    def poly(self):
        if 0 == self._wg.width:
            self._polygon = self._wg
            return pya.Path.from_dpath(self._polygon)
        elif 0 == self.self_poly_flag:
            self._polygon = self._wg.polygon()
            return pya.Polygon.from_dpoly(self._polygon)
        else:
            pts = []
            for pt in self._wg.each_point():
                pts.append(pt)
            pt1s = []
            pt2s = []
            tmp_w = abs(self._wg.width / 2.0 / math.sin(self._start_face_angle - self._start_angle))
            pt1s.append(pya.DPoint(math.cos(self._start_face_angle) * tmp_w + pts[0].x,
                                   math.sin(self._start_face_angle) * tmp_w + pts[0].y))
            pt2s.append(pya.DPoint(-math.cos(self._start_face_angle) * tmp_w + pts[0].x,
                                   -math.sin(self._start_face_angle) * tmp_w + pts[0].y))
            if 2 <= len(pts):
                for i, pt in enumerate(pts[1:-1]):
                    v1 = pt - pts[i]
                    v2 = pts[i + 2] - pt
                    beta = vector_angle(v1, v2)
                    tmp_w = abs(self._wg.width / 2.0 / math.cos(beta / 2))
                    line_dir = line_angle(pts[i], pt)
                    theta = math.pi / 2.0 + beta / 2.0 + line_dir
                    pt1s.append(pya.DPoint(math.cos(theta) * tmp_w + pt.x,
                                           math.sin(theta) * tmp_w + pt.y))
                    pt2s.insert(0, pya.DPoint(-math.cos(theta) * tmp_w + pt.x,
                                              -math.sin(theta) * tmp_w + pt.y))
            tmp_w = abs(self._wg.width / 2.0 / math.sin(self._end_face_angle - self._end_angle))
            pt1s.append(pya.DPoint(math.cos(self._end_face_angle) * tmp_w + pts[-1].x,
                                   math.sin(self._end_face_angle) * tmp_w + pts[-1].y))
            pt2s.insert(0, pya.DPoint(-math.cos(self._end_face_angle) * tmp_w + pts[-1].x,
                                      -math.sin(self._end_face_angle) * tmp_w + pts[-1].y))
            self._polygon = pya.DPolygon(pt1s + pt2s)
            return pya.Polygon.from_dpoly(self._polygon)


# ============================================================
# Taper class
# ============================================================

class Taper:
    def __init__(self, pts, width_in, width_out, eq='x', step=0.01):
        self._pts = pts
        if 2 == len(pts):
            self._start_point = pts[0]
            self._end_point = pts[1]
            self._start_angle = line_angle(pts[0], pts[1])
            self._end_angle = self._start_angle
            self._width_in = width_in
            self._width_out = width_out
            self._eq = eq
            self._step = step
        else:
            raise Exception("Only need 2 points")

    @property
    def start_point(self):
        return self._start_point

    @property
    def end_point(self):
        return self._end_point

    @property
    def start_angle(self):
        return self._start_angle

    @property
    def end_angle(self):
        return self._end_angle

    @property
    def width_in(self):
        return self._width_in

    @property
    def width_out(self):
        return self._width_out

    @property
    def eq(self):
        return self._eq

    @property
    def polygon(self):
        return self._polygon

    def poly(self):
        if 'x' == self._eq:
            pt1 = pya.DPoint(0, self._width_in / 2.0)
            pt2 = pya.DPoint(math.sqrt((self._pts[1] - self._pts[0]).sq_abs()), self._width_out / 2.0)
            pt3 = pya.DPoint(math.sqrt((self._pts[1] - self._pts[0]).sq_abs()), -self._width_out / 2.0)
            pt4 = pya.DPoint(0, -self._width_in / 2.0)
            self._polygon = pya.DPolygon([pt1, pt2, pt3, pt4])
        else:
            length = math.sqrt((self._pts[1] - self._pts[0]).sq_abs())
            pt1s = []
            pt2s = []
            x = 0.0
            while x <= 1.0:
                width = self._width_in + eval(self._eq) * (self._width_out - self._width_in)
                pt1s.append(pya.DPoint(x * length, width / 2.0))
                pt2s.insert(0, pya.DPoint(x * length, -width / 2.0))
                x += self._step
            self._polygon = pya.DPolygon(pt1s + pt2s)
        t = pya.DCplxTrans(1, self._start_angle / math.pi * 180, False, self._pts[0])
        self._polygon = self._polygon.transformed(t)
        return pya.Polygon.from_dpoly(self._polygon)


# ============================================================
# Circle class
# ============================================================

class Circle:
    def __init__(self, p0, radius, start_angle=0, end_angle=360, delta_angle=0.5):
        self.p0 = p0
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.delta_angle = delta_angle

    def poly(self):
        pts = linearc(self.p0, self.radius, self.start_angle, self.end_angle, self.delta_angle)
        polygon = pya.DPolygon(pts)
        return pya.Polygon.from_dpoly(polygon)


# ============================================================
# Ellipse class
# ============================================================

class Ellipse:
    def __init__(self, f0, a, e, start_angle=0, end_angle=360, delta_angle=0.5):
        self.f0 = f0
        self.a = a
        self.e = e
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.delta_angle = delta_angle

    def poly(self):
        pts = linearc_ellipse(self.f0, self.a, self.e, self.start_angle, self.end_angle, self.delta_angle)
        polygon = pya.DPolygon(pts)
        return pya.Polygon.from_dpoly(polygon)


# ============================================================
# Ports class
# ============================================================

class Ports:
    def __init__(self, width=450.0, direction=0.0, face_angle=90,
                 point=None, trench_width=0.0):
        if point is None:
            point = pya.DPoint(0.0, 0.0)
        self.width = width
        self.direction = direction
        self.face_angle = face_angle
        self.point = point
        self.trench_width = trench_width


# ============================================================
# Standalone test (headless mode - writes GDS file)
# ============================================================

if __name__ == "__main__":
    layout = pya.Layout()
    layout.dbu = 0.001
    cell = layout.create_cell("TOP")
    layer_index1 = layout.insert_layer(pya.LayerInfo(1, 0))
    layer_index2 = layout.insert_layer(pya.LayerInfo(2, 0))
    layer_index3 = layout.insert_layer(pya.LayerInfo(3, 0))

    if True:
        # add a taper shape
        taper_length = 100 / layout.dbu
        pts = [pya.DPoint(0, 0), pya.DPoint(taper_length, taper_length)]
        width_in = 5 / layout.dbu
        width_out = 30 / layout.dbu
        taper = Taper(pts, width_in, width_out, 'x**3')
        cell.shapes(layer_index1).insert(taper.poly())

        taper_length = 100 / layout.dbu
        pts = [pya.DPoint(0, 0), pya.DPoint(taper_length * math.sqrt(2), 0)]
        width_in = 5 / layout.dbu
        width_out = 30 / layout.dbu
        taper2 = Taper(pts, width_in, width_out, 'x**3')
        cell.shapes(layer_index2).insert(taper2.poly())

        pt = pya.DPoint(0, 0)
        circle = Circle(pt, taper_length * math.sqrt(2), 0, 270)
        cell.shapes(layer_index3).insert(circle.poly())

    if True:
        lengths = list(range(1000, 20001, 1000))
        wg = []
        for i, alength in enumerate(lengths):
            if 0 == i:
                vec = [pya.DPoint(0, 0), pya.DPoint(3 * (alength - 1000), alength)]
            else:
                vec = [pya.DPoint(0, 0) + wg[-1].end_point,
                       pya.DPoint(3 * (alength - 1000), alength) + wg[-1].end_point]
            wg.append(Waveguide(vec, 2000))
            cell.shapes(layer_index1).insert(wg[-1].poly())

        wg = []
        for alength in lengths:
            vec = [pya.DPoint(0, -20000), pya.DPoint(3 * (alength - 1000), alength - 10000)]
            wg.append(Waveguide(vec, 2000))
            cell.shapes(layer_index1).insert(wg[-1].poly())

        vec = [pya.DPoint(0, 20000.0), pya.DPoint(0, 10000.0), pya.DPoint(0, 10000.0)]
        wg = Waveguide(vec, 0.0)
        cell.shapes(layer_index1).insert(wg.poly())

    # Write GDS file
    layout.write("d:/code/waveguide_test.gds")
    print("GDS written to d:/code/waveguide_test.gds")
