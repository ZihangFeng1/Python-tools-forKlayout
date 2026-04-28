# awg_340nm_post.py - converted from Ruby to Python using Klayout pya API
import pya
import math
from waveguide import *
from Awg_class import Awg
from GratingCoupler_class import GratingCoupler_340nmSOI_200nmetch_1550nm


if __name__ == "__main__":
    main_window = pya.Application.instance().main_window()
    layout = main_window.create_layout(1).layout()
    layout_view = main_window.current_view()
    dbu = 0.001
    layout.dbu = dbu

    # Create AWG cell
    cell_awg = layout.create_cell("AWG_340nm")
    awg_obj = Awg()
    awg_obj.shapes(cell_awg)

    # Create grating coupler cell
    gcoupler = GratingCoupler_340nmSOI_200nmetch_1550nm()
    gcell = layout.create_cell("GCoupler")
    gcoupler.shapes(gcell)

    # Place grating couplers at AWG ports
    for port in awg_obj.get_ports():
        angle = (port.direction - gcoupler.get_ports()[0].direction - math.pi) / math.pi * 180.0
        disp = port.point - gcoupler.get_ports()[0].point
        tmp_trans = pya.DCplxTrans(1.0, angle, False, disp)
        cell_awg.insert(pya.CellInstArray(gcell.cell_index, tmp_trans))

    # Create top-level cell and place multiple instances
    top = layout.create_cell("TOP")
    dx = 1000.0 / dbu
    dy = 1000.0 / dbu

    for i in range(3):
        for j in range(3):
            t = pya.CplxTrans(1.0, 0, False, dx * i, dy * j)
            top.insert(pya.CellInstArray(cell_awg.cell_index, t))

    layout_view.select_cell(top.cell_index, 0)
    layout_view.add_missing_layers()
    layout_view.zoom_fit()
