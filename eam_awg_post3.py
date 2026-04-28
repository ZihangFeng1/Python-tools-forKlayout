# eam_awg_post3.py - converted from Ruby to Python using Klayout pya API
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

    # Read source GDS
    source_layout = pya.Layout()
    source_layout.read("R_GROUP1.gds")

    # Get the '1st' cell
    source_cell_name = "1st"
    source_cell = source_layout.cell(source_cell_name)
    if source_cell is None:
        print(f"Cell '{source_cell_name}' not found")
    else:
        # Create target cell
        target_cell = layout.create_cell("Modulator_AWG")

        # Copy shapes from specific layers: 1,3,4,5,7,8,9
        copy_layers = [1, 3, 4, 5, 7, 8, 9]
        layer_map = {}

        for layer_num in copy_layers:
            layer_index = source_layout.layer(layer_num, 0)
            layer_info = source_layout.get_info(layer_index)
            target_layer = layout.insert_layer(layer_info)
            layer_map[layer_index] = target_layer

        # Copy shapes with optional rotation
        angle = 0.0  # degrees
        for layer_index, target_layer in layer_map.items():
            for shape in source_cell.shapes(layer_index).each():
                # Apply transformation: copy with rotation
                disp = pya.DVector(0.0, 0.0)
                t = pya.DCplxTrans(1.0, angle, False, disp)
                target_cell.shapes(target_layer).insert(shape.transformed(t))

        # Process instances from source cell
        for inst in source_cell.each_inst():
            child_cell = source_layout.cell(inst.cell_index)
            if child_cell is not None:
                new_cell = layout.create_cell(child_cell.name)
                # Copy shapes from child cell
                for layer_index in source_layout.layer_indices():
                    child_layer = source_layout.get_info(layer_index)
                    target_layer = layout.insert_layer(child_layer)
                    for shape in child_cell.shapes(layer_index).each():
                        new_cell.shapes(target_layer).insert(shape)
                target_cell.insert(pya.CellInstArray(new_cell.cell_index, inst.trans))

        layout_view.select_cell(target_cell.cell_index, 0)
        layout_view.add_missing_layers()
        layout_view.zoom_fit()
