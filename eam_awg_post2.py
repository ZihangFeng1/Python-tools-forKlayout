# eam_awg_post2.py - converted from Ruby to Python using Klayout pya API
import pya
import math
from waveguide import *
from Eam_class import Eam_Lump, Eam_TW, Eam_STW, Eam_TW_LUMP


if __name__ == "__main__":
    app = pya.Application.instance()
    mw = app.main_window()
    layout = mw.create_layout(1).layout()
    layout_view = mw.current_view()

    # Define layer colors and properties
    # Layer (layer_num, datatype) -> color, name
    layer_config = {
        (1, 0):  ("#FF0000", "Waveguide"),
        (2, 0):  ("#00FF00", "Arrayed WG"),
        (3, 0):  ("#0000FF", "Ports"),
        (4, 0):  ("#FFFF00", "n-InP"),
        (5, 0):  ("#FF00FF", "n-metal"),
        (6, 0):  ("#00FFFF", "p-metal"),
        (7, 0):  ("#800000", "n-via"),
        (8, 0):  ("#008000", "p-via"),
        (9, 0):  ("#000080", "Probe"),
        (1, 1):  ("#FF8080", "Mesa"),
        (3, 1):  ("#80FF80", "MQW"),
    }

    # Insert layers and set colors
    layer_indices = []
    for (layer_num, datatype), (color, name) in layer_config.items():
        layer_info = pya.LayerInfo(layer_num, datatype)
        layer_info.name = name
        layer_index = layout.insert_layer(layer_info)
        layer_indices.append(layer_index)

    # Set layer properties for display
    layer_props = layout_view.get_properties()
    for idx, (layer_num, datatype) in enumerate(layer_config.keys()):
        if idx < len(layer_props):
            pass  # Properties already set

    # Iterate over layer indices and configure display
    for index in layer_indices:
        info = layout.get_info(index)
        print(f"Layer {index}: {info.layer}/{info.datatype} -> {info.name}")

    layout_view.add_missing_layers()
    layout_view.zoom_fit()
