import BruijnsSystem
from the_control import *
from PY5_2DToolkit import *
import pandas as pd
start_location:list
def setup():
    global start_location
    py5.size(1280, 768)
    start_location= sd.screen_axis(0,0)
    load()
    slider('num1', [50, py5.height - 130], value=0, range_val=[0, 10],size=[400,30])
    slider('num2', [50, py5.height - 90], value=0, range_val=[0, 100], size=[400, 30])
    slider('num3', [50, py5.height - 50], value=0, range_val=[0, 1000], size=[400, 30])
    for k,v in tool.point_dic.items():
        tool.point_dic[k]=tool.point_shift(v,start_location)

def draw():
    global  tilling_data
    py5.background(155)
    back = slider_value()
    if back is not None:
        i_seg_group = till.WFS(back['num1']+back['num2']+back['num3'])
        tool.reset()
        for seg in i_seg_group:
            tool.Segmentline_drop(seg[0], seg[1], color=py5.color(0, 0, 0, 100))
        for k, v in tool.point_dic.items():
            tool.point_dic[k] = tool.point_shift(v, start_location)

    sd.screen_draw_SegmentLine(tool.get_Segmentline_dic(),0)

if __name__ == "__main__":
    tool = Tools2D()
    a = BruijnsSystem.BruijnsSystem(shifted_distance=6,origin_norm=20,max_num_of_line=500)
    print('Gird-finish')
    till = a.tilling
    print('Tilling-finish')
    seg_group = till.WFS(0)
    print('WFS-finish')
    for i in seg_group:
        tool.Segmentline_drop(i[0],i[1],color=py5.color(0,0,0,100))

    sd = Screen_draw(py5)
    py5.run_sketch()
