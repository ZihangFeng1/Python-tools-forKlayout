# Shape statistics macro

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

for sel in lv.each_object_selected():

    shape = sel.shape

    if shape.is_path():
        paths += 1
    elif shape.is_box():
        boxes += 1
    elif shape.is_polygon():
        polygons += 1
    elif shape.is_text():
        texts += 1

s = f"Paths: {paths}\n"
s += f"Polygons: {polygons}\n"
s += f"Boxes: {boxes}\n"
s += f"Texts: {texts}\n"

pya.MessageBox.info("Shape Statistics", s, pya.MessageBox.b_ok)
