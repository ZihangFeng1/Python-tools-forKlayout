# Datamap visualization using sinc function

import pya
import math

app = pya.Application.instance()
mw = app.main_window()

# create a new layout
mw.create_layout(0)
view = mw.current_view()

# create a new layer in that layout
layout = view.cellview(0).layout()

layer_ids = []

for l in range(256):

    linfo = pya.LayerInfo()
    layer_id = layout.insert_layer(linfo)

    # create a layer view for that layer
    ln = pya.LayerPropertiesNode()
    ln.dither_pattern = 0
    if l >= 128:
        # red colors for the positive values
        c = (l - 128) * 2 * 0x10000
    elif l > 0:
        # blue colors for the negative values
        c = (128 - l) * 2
    else:
        c = 0xff
    ln.fill_color = c
    ln.frame_color = c
    ln.width = 1
    ln.source_layer_index = layer_id
    view.insert_layer(view.end_layers(), ln)

    layer_ids.append(layer_id)

# replicate last layer to allow values of 256 (mapped to 255) ..
layer_ids.append(layer_ids[255])

# create a top cell and start the recursion on this
topcell_id = layout.add_cell("top")
topcell = layout.cell(topcell_id)

# create an image

nx = 500
ny = 500
radius = 100
x = -nx / 2
for _ in range(nx):
    y = -ny / 2
    for _ in range(ny):
        r = math.sqrt(x * x + y * y) * math.pi * 2.0 / radius
        if abs(r) < 1e-6:
            v = 1.0
        else:
            v = math.sin(r) / r
        vi = int((v + 1.0) * 128.0 + 0.5)
        box = pya.Box(x * 100, y * 100, (x + 1) * 100, (y + 1) * 100)
        topcell.shapes(layer_ids[vi]).insert_box(box)
        y += 1
    x += 1

# select his cell as the top cell, fit all and switch on all hierarchy levels
view.select_cell_path([topcell_id], 0)
view.update_content()
view.zoom_fit()
view.max_hier()

# run the application
pya.Application.instance().exec_()
