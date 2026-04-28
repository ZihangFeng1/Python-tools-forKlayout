# eam_post.py - converted from Ruby to Python using Klayout pya API
import pya
import math
from waveguide import *
from Eam_class import Eam_Lump, Eam_TW, Eam_STW, Eam_TW_LUMP


if __name__ == "__main__":
    app = pya.Application.instance()
    mw = app.main_window()
    layout = mw.create_layout(1).layout()
    layout_view = mw.current_view()
    dbu = 0.001
    layout.dbu = dbu

    # Read source GDS file
    source_layout = pya.Layout()
    source_layout.read("source.gds")

    top_cell = source_layout.top_cell()
    if top_cell is None:
        print("No top cell found in source layout")
    else:
        # Get shapes from the top cell on a specific layer
        target_layer = source_layout.layer(1, 0)

        # Collect points from shapes
        vp0 = []
        for shape in source_layout.cell(top_cell.name).shapes(target_layer).each():
            if shape.is_box():
                vp0.append(pya.DPoint(shape.box_center().x, shape.box_center().y))

        # Sort points by y coordinate (descending, like Ruby's p2.y <=> p1.y)
        vp0_sorted = sorted(vp0, key=lambda p: p.y, reverse=True)

        # Create layout cells for EAM devices
        vlength = [100.0, 200.0, 300.0, 400.0, 500.0]
        cells = []
        lump = Eam_Lump()

        for iter in range(len(vlength)):
            cell_name = f"EAM_Lump_{int(vlength[iter])}"
            cell = layout.create_cell(cell_name)
            lump.wg_length_set(vlength[iter])
            lump.shapes(cell)
            cells.append(cell)

        # Create top cell and place EAM cells at sorted positions
        top = layout.create_cell("TOP")
        for iter in range(min(len(vp0_sorted), len(cells))):
            dx = vp0_sorted[iter].x
            dy = vp0_sorted[iter].y
            t = pya.CplxTrans(1.0, 0, False, dx, dy)
            top.insert(pya.CellInstArray(cells[iter].cell_index, t))

        layout_view.select_cell(top.cell_index, 0)
        layout_view.add_missing_layers()
        layout_view.zoom_fit()
