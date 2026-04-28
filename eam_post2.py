# eam_post2.py - converted from Ruby to Python using Klayout pya API
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
        cell_name = top_cell.name

        # Create target cell
        target_cell = layout.create_cell(cell_name + "_processed")

        # Copy shapes from source cell
        source_cell = source_layout.cell(cell_name)
        layer_indices = source_layout.layer_indices()
        for layer_index in layer_indices:
            layer_info = source_layout.get_info(layer_index)
            target_layer = layout.insert_layer(layer_info)
            for shape in source_cell.shapes(layer_index).each():
                target_cell.shapes(target_layer).insert(shape)

        # Process instances - reset transforms
        for inst in source_cell.each_inst():
            child_cell = source_layout.cell(inst.cell_index)
            new_inst = pya.CellInstArray(child_cell.cell_index, pya.Trans())
            target_cell.insert(new_inst)

        layout_view.select_cell(target_cell.cell_index, 0)
        layout_view.add_missing_layers()
        layout_view.zoom_fit()
