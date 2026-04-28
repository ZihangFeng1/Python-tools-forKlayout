# Shape duplication and translation

import pya

app = pya.Application.instance()
mw = app.main_window()

lv = mw.current_view()
if lv is None:
    raise Exception("Shape Statistics: No view selected")

paths = 0
polygons = 0
boxes = 0
texts = 0
dbu = pya.CellView.active().layout().dbu
for sel in lv.each_object_selected():
    p1 = pya.DPoint(0, 1050 / dbu)
    p2 = pya.DPoint(0, -250 / dbu)
    p3 = pya.DPoint(0, -2450 / dbu)
    p4 = pya.DPoint(0, -250 / dbu)
    shape = sel.shape
    dup_shape1 = shape.dup()
    shape.shapes().insert(dup_shape1)
    dup_shape1.transform(pya.DCplxTrans(1, 0, False, p1))
    dup_shape2 = dup_shape1.dup()
    shape.shapes().insert(dup_shape2)
    dup_shape2.transform(pya.DCplxTrans(1, 0, False, p2))
    dup_shape3 = dup_shape2.dup()
    shape.shapes().insert(dup_shape3)
    dup_shape3.transform(pya.DCplxTrans(1, 0, False, p3))
    dup_shape4 = dup_shape3.dup()
    shape.shapes().insert(dup_shape4)
    dup_shape4.transform(pya.DCplxTrans(1, 0, False, p4))

# pya.MessageBox.info("Shape Statistics", s, pya.MessageBox.b_ok)
