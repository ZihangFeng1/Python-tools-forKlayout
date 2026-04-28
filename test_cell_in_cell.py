import pya
import math
import os
from waveguide import *
from Awg_class import Awg
from GratingCoupler_class import GratingCoupler

if __name__ == "__main__":
    layout = pya.Layout()
    # set the database unit (shown as an example, the default is 0.001)
    dbu = 0.001
    layout.dbu = dbu
    # create a cell
    # #################200G################
    cell = layout.create_cell("AWG_200G_width450")
    awg_200G = Awg(dbu=dbu, layer_fsr=layout.layer(1, 0), layer_arrayed=layout.layer(2, 0),
                   layer_ports=layout.layer(3, 0))
    awg_200G.narms = 40
    awg_200G.nchannel = 6
    awg_200G.ra = 54.0 / dbu
    awg_200G.theta_da = 0.9
    awg_200G.theta_cs = 1.4
    awg_200G.w_wg = 0.45 / dbu
    awg_200G.w_aperture = 2.0 / dbu
    awg_200G.array_aperture = 1.68 / dbu
    awg_200G.array_w = 0.45 / dbu
    awg_200G.array_R = 30.0 / dbu
    awg_200G.delta_L = 32.935 / dbu
    awg_200G.arrayed_taper = 30.0 / dbu
    awg_200G.w_taper = 30.0 / dbu
    awg_200G.arrayed_spacing = 2.8 / dbu
    awg_200G.ports_spacing = 100.0 / dbu
    awg_200G.overlap_fpr1 = 0.1 / dbu
    awg_200G.overlap_fpr2 = 0.25 / dbu
    awg_200G.overlap_array = 0.1 / dbu
    awg_200G.overlap_ports = 0.1 / dbu
    awg_200G.fsr_angle1 = 57.0
    awg_200G.fsr_angle2 = 53.0
    awg_200G.layer_fsr = layout.layer(1, 0)
    awg_200G.layer_arrayed = layout.layer(2, 0)
    awg_200G.layer_ports = layout.layer(3, 0)
    awg_200G.centre_line = 1
    # awg_200G.straight_neff = 2.82371
    # awg_200G.bend_neff = 2.824144
    awg_200G.shapes(cell)
    # #################Grating Coupler##############
    gccell = layout.create_cell("Grating_Coupler_340nm")
    gcoupler = GratingCoupler(dbu=dbu, layer_grating=layout.layer(1, 0))
    gcoupler.width_in = awg_200G.get_ports()[0].width
    gcoupler.period = 0.64 / dbu
    gcoupler.duty = 0.38
    gcoupler.shapes(gccell)

    for port in awg_200G.get_ports():
        angle = (port.direction - gcoupler.get_ports()[0].direction - math.pi) / math.pi * 180.0
        disp = port.point - gcoupler.get_ports()[0].point
        t = pya.DCplxTrans(1.0, angle, False, disp)
        tmp = pya.CellInstArray(gccell.cell_index(), t)
        cell.insert(tmp)

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
