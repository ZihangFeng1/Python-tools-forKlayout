# Python-tools-forKlayout
Transform from Ruby
这是一个关于Klayout版图的数据库，有一些常用的结构，这里我会说明一些详细的用法


## 关于GratingCoupler_Class.py的使用
--- 

out_path = "d:/code/" + os.path.splitext(os.path.basename(__file__))[0] + "_test.gds"

layout.write("E:\PKU\Project\GCP.gds")

print(f"GDS written to E:\PKU\Project\GCP.gds") 

**上方三段代码为生成gds文件，然后修改路径后在klayout中打开即可**
---
可修改为：
---

main_window = pya.Application.instance().main_window

layout_view = main_window.create_layout(0)

layout = layout_view.layout

layout.dbu = dbu

cell = layout.create_cell("Dual_GC")

gc.shapes(cell, layout)

layout_view.select_cell(cell.cell_index, 0)

layout_view.add_missing_layers()

layout_view.zoom_fit()

**修改为上述代码后即可在klayout中直接打开**
---
