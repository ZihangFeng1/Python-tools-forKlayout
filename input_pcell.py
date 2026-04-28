# PCell instantiation using Basic library

import pya
import os

if __name__ == "__main__":
    ly = pya.Layout()
    cell = ly.create_cell("TOP")

    # Find the lib
    lib = pya.Library.library_by_name("Basic")
    if not lib:
        raise Exception("Unknown lib 'Basic'")

    # Find the pcell
    pcell_decl = lib.layout().pcell_declaration("TEXT")
    if not pcell_decl:
        raise Exception("Unknown PCell 'TEXT'")

    # Set the parameters (text string, layer to 10/0, magnification to 2.5)
    param = {"text": "KLAYOUT RULES", "layer": pya.LayerInfo(10, 0), "mag": 2.5}

    # Build a param array using the param hash as a source.
    # Fill all remaining parameter with default values.
    pv = [param.get(p.name, p.default) for p in pcell_decl.get_parameters()]

    # Create a PCell variant cell
    pcell_var = ly.add_pcell_variant(lib, pcell_decl.id(), pv)

    # Instantiate that cell
    t = pya.Trans(pya.Trans.R90, 0, 0)
    cell.insert(pya.CellInstArray(pcell_var, t))
    cell.refresh()

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    ly.write(out_path)
    print(f"GDS written to {out_path}")
