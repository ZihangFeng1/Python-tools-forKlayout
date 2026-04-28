# Draw a circle using the active view

import pya
import math

view = pya.LayoutView.current()
cell = view.active_cellview().cell()
layer = view.current_layer().current().layer_index()

n = 200    # number of points
r = 10000  # radius
da = 2 * math.pi / n
pts = [pya.Point(r * math.cos(i * da), r * math.sin(i * da)) for i in range(n)]
poly = pya.Polygon(pts)
cell.shapes(layer).insert(poly)
