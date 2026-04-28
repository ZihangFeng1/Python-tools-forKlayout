# eam_post3.py - converted from Ruby to Python using Klayout pya API
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
        target_cell = layout.create_cell("Rearranged")

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

        # Process instances - rearrange in grid
        inst_list = list(source_cell.each_inst())
        ncols = 2

        for idx, inst in enumerate(inst_list):
            child_cell = source_layout.cell(inst.cell_index)
            i = idx // ncols
            j = idx % ncols

            # Copy shapes from child cell into target
            for layer_index in source_layout.layer_indices():
                target_layer = layer_map.get(layer_index)
                if target_layer is not None:
                    for shape in child_cell.shapes(layer_index).each():
                        # Apply position offset
                        dx = 6000.0 * i / dbu
                        dy = -4500.0 * j / dbu
                        t = pya.Trans(dx, dy)
                        target_cell.shapes(target_layer).insert(shape.transformed(t))

        layout_view.select_cell(target_cell.cell_index, 0)
        layout_view.add_missing_layers()
        layout_view.zoom_fit()
