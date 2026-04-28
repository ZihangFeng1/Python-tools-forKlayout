# just_eam_post.py - converted from Ruby to Python using Klayout pya API
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
        # Get cell from source
        source_cell = source_layout.cell(top_cell.name)

        # Collect points from shapes (layer 1/0)
        target_layer = source_layout.layer(1, 0)
        vp0 = []
        for shape in source_cell.shapes(target_layer).each():
            if shape.is_box():
                vp0.append(pya.DPoint(shape.box_center().x, shape.box_center().y))

        # Sort descending by y
        vp0_sorted = sorted(vp0, key=lambda p: p.y, reverse=True)

        # Create EAM cells with varying lengths
        vlength = [100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0]
        lump = Eam_Lump()
        eam_cells = []

        for iter in range(len(vlength)):
            cell_name = f"Laser_{int(vlength[iter])}"
            cell = layout.create_cell(cell_name)
            lump.wg_length_set(vlength[iter])
            lump.shapes(cell)
            eam_cells.append(cell)

        # Create top cell and place EAM at sorted positions
        top = layout.create_cell("Laser_Array")
        for iter in range(min(len(vp0_sorted), len(eam_cells))):
            dx = vp0_sorted[iter].x
            dy = vp0_sorted[iter].y
            t = pya.CplxTrans(1.0, 0, False, dx, dy)
            top.insert(pya.CellInstArray(eam_cells[iter].cell_index, t))

        layout_view.select_cell(top.cell_index, 0)
        layout_view.add_missing_layers()
        layout_view.zoom_fit()
