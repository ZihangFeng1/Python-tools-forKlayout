# eam_awg_post.py - converted from Ruby to Python using Klayout pya API
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

    # Read R_GROUP1.gds
    source_layout = pya.Layout()
    source_layout.read("R_GROUP1.gds")

    # Get the '1st' cell from source layout
    source_cell = None
    for cell in source_layout.each_cell():
        if cell.name == "1st":
            source_cell = cell
            break

    if source_cell is None:
        print("Cell '1st' not found in R_GROUP1.gds")
    else:
        # Copy layers from source
        layer_map = {}
        for layer_index in source_layout.layer_indices():
            layer_info = source_layout.get_info(layer_index)
            target_layer = layout.insert_layer(layer_info)
            layer_map[layer_index] = target_layer

        # Create EAM_LUMP cells
        lump = Eam_TW_LUMP()
        lump_cell = layout.create_cell("EAM_LUMP_MASTER")
        lump.shapes(lump_cell)

        # Create target cell
        target_cell = layout.create_cell("EAM_AWG")
        for layer_index, target_layer in layer_map.items():
            for shape in source_cell.shapes(layer_index).each():
                target_cell.shapes(target_layer).insert(shape)

        # Place EAM_LUMP at positions from source
        pos_layer = source_layout.layer(1, 0)
        positions = []
        for shape in source_cell.shapes(pos_layer).each():
            if shape.is_box():
                positions.append(pya.DPoint(shape.box_center().x, shape.box_center().y))

        positions = sorted(positions, key=lambda p: p.y)

        for pos in positions:
            t = pya.CplxTrans(1.0, 0, False, pos.x, pos.y)
            target_cell.insert(pya.CellInstArray(lump_cell.cell_index, t))

        layout_view.select_cell(target_cell.cell_index, 0)
        layout_view.add_missing_layers()
        layout_view.zoom_fit()
