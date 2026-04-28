# awg_340nm.py - converted from Ruby to Python using Klayout pya API
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

    cell = layout.create_cell("AWG_340nm")
    awg_200G = Awg()
    awg_200G.shapes(cell)

    gcoupler = GratingCoupler_340nmSOI_200nmetch_1550nm()
    gcell = layout.create_cell("GC_340")
    gcoupler.shapes(gcell)

    for port in awg_200G.get_ports():
        angle = (port.direction - gcoupler.get_ports()[0].direction - math.pi) / math.pi * 180.0
        disp = port.point - gcoupler.get_ports()[0].point
        tmp_trans = pya.DCplxTrans(1.0, angle, False, disp)
        cell.insert(pya.CellInstArray(gcell.cell_index, tmp_trans))
