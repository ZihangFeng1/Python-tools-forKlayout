import pya
import os

if __name__ == "__main__":
    layout = pya.Layout()
    # set the database unit (shown as an example, the default is 0.001)
    layout.dbu = 0.001

    top = layout.add_cell("TOP")

    # find the lib
    lib = pya.Library.library_by_name("Basic")
    if lib is None:
        raise Exception("Unknown lib 'Basic'")

    # find the pcell
    pcell_decl = lib.layout().pcell_declaration("TEXT")
    if pcell_decl is None:
        raise Exception("Unknown PCell 'TEXT'")

    # set the parameters
    param = {
        "text": "KLAYOUT RULES2",
        "layer": pya.LayerInfo(10, 0),
        "mag": 2.5
    }

    # build a param array using the param hash as a source
    pv = [param[p.name] if p.name in param else p.default for p in pcell_decl.get_parameters()]

    # create a PCell variant cell
    pcell_var = layout.add_pcell_variant(lib, pcell_decl.id(), pv)

    # instantiate that cell
    t = pya.Trans(pya.Trans.R90, 0, 0)
    pcell_inst = layout.cell(top).insert(pya.CellInstArray(pcell_var, t))

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
