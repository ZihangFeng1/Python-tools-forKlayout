# eam_awg_post4.py - converted from Ruby to Python using Klayout pya API
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
        source_cell = source_layout.cell(top_cell.name)

        # Create target cell
        target_cell = layout.create_cell("Rearranged_3col")

        # Copy layers from source
        layer_map = {}
        for layer_index in source_layout.layer_indices():
            layer_info = source_layout.get_info(layer_index)
            target_layer = layout.insert_layer(layer_info)
            layer_map[layer_index] = target_layer

        # Copy shapes
        for layer_index, target_layer in layer_map.items():
            for shape in source_cell.shapes(layer_index).each():
                target_cell.shapes(target_layer).insert(shape)

        # Process instances - rearrange in 3-column grid
        # Uses modulo(3) for column assignment, 3-column layout
        inst_list = list(source_cell.each_inst())
        ncols = 3

        for idx, inst in enumerate(inst_list):
            child_cell = source_layout.cell(inst.cell_index)
            if child_cell is None:
                continue

            iter = idx
            col = iter % 3
            row = iter // 3

            # Create child cell in target
            target_child = layout.create_cell(child_cell.name)
            for layer_index in source_layout.layer_indices():
                target_layer = layer_map.get(layer_index)
                if target_layer is not None:
                    for shape in child_cell.shapes(layer_index).each():
                        target_child.shapes(target_layer).insert(shape)

            # Position based on row/column
            dx = 6000.0 * row / dbu
            dy = -4500.0 * col / dbu
            child_inst = pya.CellInstArray(target_child.cell_index,
                                           pya.Trans(dx, dy))
            target_cell.insert(child_inst)

        layout_view.select_cell(target_cell.cell_index, 0)
        layout_view.add_missing_layers()
        layout_view.zoom_fit()
