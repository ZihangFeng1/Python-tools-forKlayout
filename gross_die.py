# gross_die.py - converted from Ruby to Python using Klayout pya API
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# DESCRIPTION: dice count : gross die , yield estimation and wafermap

import pya
import math


def gross_die():
    dialog = pya.QDialog(pya.Application.instance().main_window())
    dialog.windowTitle = "WAFER & DIE characteritics"
    layout = pya.QVBoxLayout(dialog)
    dialog.setLayout(layout)

    # Die name
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the die or project name :"
    layout_name = pya.QLineEdit(dialog)
    layout.addWidget(layout_name)
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "\n"

    # Layout width : X
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the layout width X (mm) :"
    layout_X = pya.QLineEdit(dialog)
    layout.addWidget(layout_X)

    # Layout heigth : Y
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the layout heigth Y (mm) :"
    layout_Y = pya.QLineEdit(dialog)
    layout.addWidget(layout_Y)

    # Scribe width : X
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the scribe width X (mm) :"
    scribe_X = pya.QLineEdit(dialog)
    layout.addWidget(scribe_X)
    scribe_X.text = "0.1"

    # Scribe heigth : Y
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the scribe heigth Y (mm) :"
    scribe_Y = pya.QLineEdit(dialog)
    layout.addWidget(scribe_Y)
    scribe_Y.text = "0.1"

    # Wafer diameter
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the wafer diameter (mm) / (inches)"
    waf_diam = pya.QComboBox(dialog)
    waf_diam.addItem("50 mm / 2 \" ")
    waf_diam.addItem("75 mm / 3 \" ")
    waf_diam.addItem("100 mm / 4 \" ")
    waf_diam.addItem("125 mm / 5 \" ")
    waf_diam.addItem("150 mm / 6 \" ")
    waf_diam.addItem("200 mm / 8 \" ")
    waf_diam.addItem("300 mm / 12 \" ")
    waf_diam.addItem("450 mm / 18 \" ")
    waf_diam.setCurrentIndex(5)
    layout.addWidget(waf_diam)

    # Wafer type : P-100
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the wafer type"
    waf_typ = pya.QComboBox(dialog)
    waf_typ.addItem("N-100")
    waf_typ.addItem("N-111")
    waf_typ.addItem("P-100")
    waf_typ.addItem("P-111")
    layout.addWidget(waf_typ)

    # Edging loss of the wafer
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the edging loss (mm) :"
    PEE = pya.QLineEdit(dialog)
    layout.addWidget(PEE)
    PEE.text = "3"

    # defects / cm^2
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the defects density D0 (/cm^2) :"
    defectsE = pya.QLineEdit(dialog)
    layout.addWidget(defectsE)
    defectsE.text = "0.12"

    # measure of manufacturing process complexity
    label = pya.QLabel(dialog)
    layout.addWidget(label)
    label.text = "Enter the manufacturing process complexity :"
    alphaE = pya.QLineEdit(dialog)
    layout.addWidget(alphaE)
    alphaE.text = "2.5"

    # OK button
    def on_ok_clicked():
        if float(layout_X.text) == 0.0:
            confirm = pya.MessageBox.info("WRONG INPUTS !!!",
                                          "Set the layout width X",
                                          pya.MessageBox.b_ok + pya.MessageBox.b_cancel)
            if confirm == pya.MessageBox.b_cancel:
                raise Exception("Operation aborted")
        elif float(layout_Y.text) == 0.0:
            confirm = pya.MessageBox.info("WRONG INPUTS !!!",
                                          "Set the layout heigth Y",
                                          pya.MessageBox.b_ok + pya.MessageBox.b_cancel)
            if confirm == pya.MessageBox.b_cancel:
                raise Exception("Operation aborted")
        else:
            dialog.accept()

    buttonOK = pya.QPushButton(dialog)
    layout.addWidget(buttonOK)
    buttonOK.text = " OK "
    buttonOK.clicked(on_ok_clicked)

    dialog.exec_()

    # Input data from string to float
    xlayout = float(layout_X.text)
    ylayout = float(layout_Y.text)
    xscribe = float(scribe_X.text)
    yscribe = float(scribe_Y.text)
    PE = float(PEE.text)
    defects = float(defectsE.text)
    alpha = float(alphaE.text)

    if waf_diam.currentText() == "50 mm / 2 \" ":
        diameter = 50.8
        OFL = 15.88
        CFL = 8.0
        RE = 2.0
        thick = 279
    elif waf_diam.currentText() == "75 mm / 3 \" ":
        diameter = 76.2
        OFL = 22.22
        CFL = 11.18
        RE = 2.0
        thick = 381
    elif waf_diam.currentText() == "100 mm / 4 \" ":
        diameter = 100.0
        OFL = 32.5
        CFL = 18.0
        RE = 2.0
        thick = "525 or 625"
    elif waf_diam.currentText() == "125 mm / 5 \" ":
        diameter = 125.0
        OFL = 42.5
        CFL = 27.5
        RE = 2.0
        thick = 625
    elif waf_diam.currentText() == "150 mm / 6 \" ":
        diameter = 150.0
        OFL = 57.5
        CFL = 37.5
        RE = 2.0
        thick = 675
    elif waf_diam.currentText() == "200 mm / 8 \" ":
        diameter = 200.0
        OFL = 0.0
        CFL = 0.0
        RE = 0.1
        thick = 725
    elif waf_diam.currentText() == "300 mm / 12 \" ":
        diameter = 300.0
        OFL = 0.0
        CFL = 0.0
        RE = 0.1
        thick = 775
    elif waf_diam.currentText() == "450 mm / 18 \" ":
        diameter = 450.0
        OFL = 0.0
        CFL = 0.0
        RE = 0.1
        thick = 925

    # Define common constants
    sqrt2 = math.sqrt(2)
    lne = 2.7183
    radius = diameter / 2.0

    height = xlayout + xscribe
    width = ylayout + yscribe

    # Formula 1: Anderson School at UCLA
    DieCount1 = 0
    h = height
    w = width
    if h > w:
        h = width
        w = height

    if w < diameter:
        rowmax = int(math.sqrt(diameter ** 2 - w ** 2) / h)
        columax = int(math.sqrt(diameter ** 2 - h ** 2) / w)

        for row in range(1, rowmax + 1):
            columns = int(math.sqrt(diameter ** 2 - (row * h) ** 2) / w)
            DieCount1 = DieCount1 + columns

    # Formula 2: www.cse.psu.edu/~mji
    diearea = height * width
    PreCount = math.pi * radius ** 2 / diearea
    Margin = math.pi * diameter / math.sqrt(2 * diearea)
    DieCount2 = round(PreCount - Margin)

    # Four yield models formula
    NegBinYield = 100.0 * (1.0 + (defects * diearea * 1e-2) / alpha) ** (alpha * -1.0)
    PoissonYield = 100.0 * 1.0 / (lne ** (diearea * 1e-2 * defects))
    MurphyYield = 100.0 * ((1.0 - (lne ** (-1.0 * diearea * 1e-2 * defects))) / (diearea * 1e-2 * defects)) ** 2
    SeedYield = 100.0 * 1.0 / (lne ** math.sqrt(diearea * 1e-2 * defects))

    if waf_typ.currentText() == "N-100":
        OFR = radius - math.sqrt(radius ** 2.0 - (OFL / 2.0) ** 2)
        CFR = radius - math.sqrt(radius ** 2.0 - (CFL / 2.0) ** 2)
        cutOFR = round(OFR / h + 1.0)
        cutCFR45 = 0.0
        cutCFR90 = 0.0
        cutCFR180 = round(CFR / w + 1.0)
    elif waf_typ.currentText() == "N-111":
        OFR = radius - math.sqrt(radius ** 2.0 - (OFL / 2.0) ** 2)
        CFR = radius - math.sqrt(radius ** 2.0 - (CFL / 2.0) ** 2)
        cutOFR = round(OFR / h + 1.0)
        cutCFR45 = 1.0
        cutCFR90 = 0.0
        cutCFR180 = 0.0
    elif waf_typ.currentText() == "P-100":
        OFR = radius - math.sqrt(radius ** 2.0 - (OFL / 2.0) ** 2)
        CFR = radius - math.sqrt(radius ** 2.0 - (CFL / 2.0) ** 2)
        cutOFR = round(OFR / h + 1.0)
        cutCFR45 = 0.0
        cutCFR90 = round(CFR / w + 1.0)
        cutCFR180 = 0.0
    elif waf_typ.currentText() == "P-111":
        OFR = radius - math.sqrt(radius ** 2.0 - (OFL / 2.0) ** 2)
        cutOFR = round(OFR / h + 1.0)
        cutCFR45 = 0.0
        cutCFR90 = 0.0
        cutCFR180 = 0.0

    # Draw the wafer
    app = pya.Application.instance()
    mw = app.main_window()
    mw.create_layout(0)
    layout_view = mw.current_view()

    cv_layout = layout_view.cellview(0).layout()
    layout_view.set_config("background-color", "0xFFFFFF")
    linfo = pya.LayerInfo()

    # Create a layer view for the wafer
    layer_id = cv_layout.insert_layer(linfo)
    ln = pya.LayerPropertiesNode()
    ln.dither_pattern = 1
    ln.frame_color = 0x000000
    ln.width = 3
    ln.source_layer_index = layer_id
    layout_view.insert_layer(layout_view.end_layers(), ln)

    # Create a layer view for the safe area
    layer_id2 = cv_layout.insert_layer(linfo)
    ln2 = pya.LayerPropertiesNode()
    ln2.dither_pattern = 1
    ln2.frame_color = 0x00FF00
    ln2.width = 1
    ln2.source_layer_index = layer_id2
    layout_view.insert_layer(layout_view.end_layers(), ln2)

    # Create a layer view for the die area
    layer_id3 = cv_layout.insert_layer(linfo)
    ln3 = pya.LayerPropertiesNode()
    ln3.dither_pattern = 1
    ln3.frame_color = 0xFF0000
    ln3.width = 2
    ln3.source_layer_index = layer_id3
    layout_view.insert_layer(layout_view.end_layers(), ln3)

    # Create a top cell
    wafer = cv_layout.add_cell("wafer")
    dbu = 1.0 / cv_layout.dbu
    RPE = radius - (RE + PE)

    # Convert to database units
    radius *= 1000.0 * dbu
    RPE *= 1000.0 * dbu
    xlayout *= 1000.0 * dbu
    ylayout *= 1000.0 * dbu
    xscribe *= 1000.0 * dbu
    yscribe *= 1000.0 * dbu

    # Draw wafers
    pts = []
    n = 128
    da = math.pi * 2 / n
    if (waf_diam.currentText() == "200 mm / 8 \" " or
        waf_diam.currentText() == "300 mm / 12 \" " or
        waf_diam.currentText() == "450 mm / 18 \" "):
        for i in range(n):
            if i == 0:
                pts.append(pya.Point.from_dpoint(pya.DPoint(radius * math.sin(i * da) + 1000 * dbu,
                                                            -radius * math.cos(i * da))))
            else:
                pts.append(pya.Point.from_dpoint(pya.DPoint(radius * math.sin(i * da),
                                                            -radius * math.cos(i * da))))
        pts.append(pya.Point.from_dpoint(pya.DPoint(-1000 * dbu, -radius)))
        pts.append(pya.Point.from_dpoint(pya.DPoint(-1000 * dbu, -radius + 1000 * dbu)))
        pts.append(pya.Point.from_dpoint(pya.DPoint(0, -radius + 1500 * dbu)))
        pts.append(pya.Point.from_dpoint(pya.DPoint(+1000 * dbu, -radius + 1000 * dbu)))
    else:
        flat = 0
        for i in range(n):
            if ((-math.cos(i * da) > 0) or
                (radius * math.sin(i * da) > OFL * 500 * dbu) or
                (radius * math.sin(i * da) < -OFL * 500 * dbu)):
                if ((waf_typ.currentText() == "N-111") and
                    ((i * da) < (math.asin((OFL * 500 * dbu) / radius) +
                                 2 * math.asin((CFL * 500 * dbu) / radius)))):
                    if flat == 0:
                        theta = (math.asin((OFL * 500 * dbu) / radius) +
                                 2 * math.asin((CFL * 500 * dbu) / radius))
                        pts.append(pya.Point.from_dpoint(
                            pya.DPoint(radius * math.sin(theta), -radius * math.cos(theta))))
                    flat = 1
                elif ((waf_typ.currentText() == "P-100") and
                      (math.sin(i * da) > 0) and
                      (radius * math.cos(i * da) < CFL * 500 * dbu) and
                      (radius * math.cos(i * da) > -CFL * 500 * dbu)):
                    flat = 1
                elif ((waf_typ.currentText() == "P-111") and
                      (-math.cos(i * da) > 0) and
                      (radius * math.sin(i * da) < CFL * 500 * dbu) and
                      (radius * math.sin(i * da) > -CFL * 500 * dbu)):
                    flat = 1
                else:
                    pts.append(pya.Point.from_dpoint(
                        pya.DPoint(radius * math.sin(i * da), -radius * math.cos(i * da))))
        pts.append(pya.Point.from_dpoint(
            pya.DPoint(-OFL * 500 * dbu,
                       -math.sqrt(radius ** 2 - (OFL * 500 * dbu) ** 2))))
        pts.append(pya.Point.from_dpoint(
            pya.DPoint(OFL * 500 * dbu,
                       -math.sqrt(radius ** 2 - (OFL * 500 * dbu) ** 2))))

    cv_layout.cell(wafer).shapes(layer_id).insert(pya.Polygon(pts))

    # Draw the safe circle
    pts = []
    for i in range(n):
        pts.append(pya.Point.from_dpoint(
            pya.DPoint(RPE * math.cos(i * da), RPE * math.sin(i * da))))
    cv_layout.cell(wafer).shapes(layer_id2).insert(pya.Polygon(pts))

    # Line function: Calculating an angle of 45 N-111 Cutaway
    linem = 1
    lineb1 = -radius * sqrt2
    lineb2 = sqrt2 * (radius - math.sqrt(radius ** 2 - (CFL / 2.0) ** 2))
    lineb = lineb1 + lineb2
    R0x = 0.0
    R0y = linem * R0x + lineb
    R1y = 0.0
    R1x = (R1y - lineb) / linem

    P2 = -1
    DieCount = 0
    row_min = int(cutOFR)
    row_max = int(rowmax - cutCFR180)
    col_max = int(columax - cutCFR90)

    for j in range(row_min, row_max + 1):
        for i in range(0, 2 * col_max + 1):
            gBLx = i * (xlayout + xscribe) + (xscribe / 2.0) - radius
            gBLy = j * (ylayout + yscribe) + (yscribe / 2.0) - radius
            gTRx = (i + 1) * (xlayout + xscribe) - (xscribe / 2.0) - radius
            gTRy = (j + 1) * (ylayout + yscribe) - (yscribe / 2.0) - radius

            # Point inside wafer: calculation falls in the circle die
            ptdisc1 = math.sqrt(gBLx ** 2 + gBLy ** 2)
            ptdisc2 = math.sqrt(gTRx ** 2 + gTRy ** 2)
            ptdisc3 = math.sqrt(gBLx ** 2 + gTRy ** 2)
            ptdisc4 = math.sqrt(gTRx ** 2 + gBLy ** 2)

            # In angle 45: 45 cutting angle calculation die within
            if cutCFR45 == 1:
                Rnx = gBLx
                Rny = gBLy
                P0 = (R1x - Rnx) * (R0y - Rny)
                P1 = (R0x - Rnx) * (R1y - Rny)
                P2 = P0 - P1

            # Create die rectangle
            if (ptdisc1 < RPE and ptdisc2 < RPE and
                ptdisc3 < RPE and ptdisc4 < RPE and P2 < 0):
                cv_layout.cell(wafer).shapes(layer_id3).insert(
                    pya.Box(gBLx, gBLy, gTRx, gTRy))
                DieCount += 1

    # Add text on the layout
    txt_size = str(round(radius / 50 / dbu))
    layout_view.set_config("default-text-size", txt_size)

    string = "Die / poject name :  %s" % layout_name.text
    cv_layout.cell(wafer).shapes(layer_id3).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * 0.85)))
    layout_size = xlayout * ylayout / 1000000 / dbu / dbu
    string = "Layout size : %s x %s = %.2f mm2" % (layout_X.text, layout_Y.text, layout_size)
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * 0.72)))
    string = "Scribe size :  X = %s :  Y %s  mm" % (scribe_X.text, scribe_Y.text)
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * 0.62)))
    die_size = (xlayout + xscribe) * (ylayout + yscribe) / 1000000 / dbu / dbu
    string = "Die size : %.3f x %.3f = %.2f mm2" % (
        float(layout_X.text) + float(scribe_X.text),
        float(layout_Y.text) + float(scribe_Y.text),
        die_size)
    cv_layout.cell(wafer).shapes(layer_id3).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * 0.52)))
    string = "Die count : (method 1) =  %d" % DieCount1
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * 0.37)))
    string = "Die count : (method 2) =  %d" % DieCount2
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * 0.27)))
    string = "Die count : (counted) =  %d  \nBest method: counted from the wafer map" % DieCount
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * 0.15)))
    string = " NegBin Yield =  %.2f %%" % NegBinYield
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * 0.07)))
    string = "Poisson Yield =  %.2f %%" % PoissonYield
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * -0.03)))
    string = " Murphy Yield =  %.2f %%" % MurphyYield
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * -0.13)))
    string = "   Seed Yield =  %.2f %%" % SeedYield
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * -0.23)))
    good_die = round((NegBinYield + PoissonYield + MurphyYield) * DieCount / 300)
    string = ("Expected good die / wafer = %d\n\nDepending on design, layout and test margins,\n"
              "foundry defects density D0 and process complexity" % good_die)
    cv_layout.cell(wafer).shapes(layer_id3).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * -0.43)))
    string = "Foundry defects density =  %s /cm^2\nProcess complexity assumed : %s" % (
        defectsE.text, alphaE.text)
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * -0.55)))
    string = "Wafer size =  %s" % waf_diam.currentText()
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * -0.65)))
    string = "Wafer type =  %s" % waf_typ.currentText()
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * -0.75)))
    string = "Wafer safety edge =  %.2f mm" % (RE + PE)
    cv_layout.cell(wafer).shapes(layer_id2).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * -0.85)))
    string = "Wafer thickness =  %s um-typ" % str(thick)
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Text(string, pya.Trans(radius * 1.1, radius * -0.95)))
    cv_layout.cell(wafer).shapes(layer_id).insert(
        pya.Box(radius * 1.05, -radius, radius * 2.2, radius * 0.95))

    # Adjust layout view to fit the drawings
    layout_view.select_cell(wafer, 0)
    layout_view.update_content()
    layout_view.add_missing_layers()
    layout_view.zoom_fit()
    layout_view.max_hier_levels = 2


# Add the command in the tools menu
app = pya.Application.instance()
mw = app.main_window()
menu = mw.menu()
menu.insert_separator("tools_menu.end", "name")
menu.insert_item("tools_menu.end", "gross_die", gross_die)


if __name__ == "__main__":
    gross_die()
