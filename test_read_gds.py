import pya
import os

if __name__ == "__main__":
    layout = pya.Layout()

    filename = 'G:\\piaopiaotao\\400nmRUN_2015PDK_HOMEMADE\\GDS_library\\T_GRA.GDS'

    layout.read(filename)
    cell = layout.top_cell()

    out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"
    layout.write(out_path)
    print(f"GDS written to {out_path}")
