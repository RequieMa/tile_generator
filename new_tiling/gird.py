import py5_tools
py5_tools.add_jars('../jars')
from YuSan_PY5_Toolscode import *
from the_control import *
color=[py5.color(255,0,0),
           py5.color(0,255,0),
           py5.color(0,0,255),
           py5.color(0,255,255),
           py5.color(255,255,0),
           py5.color(255,0,255),
           py5.color(125,125,0),
           py5.color(125,0,125),
           py5.color(0,125,125),
           py5.color(125, 125, 255),
           py5.color(125, 255, 125),
           py5.color(255, 125, 125),
           py5.color(125, 0, 255),
           py5.color(255, 0, 125),
           py5.color(255, 125, 0),
           ] #颜色常量

def create_gird(sides, distance=0, zoom=100, center=(100,100), num_of_line=50):
    """
    此函数用于创建一组网格系统 例[{0:..,1:..,-1:..},{..},{..}]
    distance：初始向量取垂直线以后，相互远离的距离。
    zoom：每条网格线相隔的距离
    返回一个列表，每个列表中包含一个方向的平行网格线，由所有网格线组成一个gird
    """
    tools = Tools2D()
    # 在【0，0】创建一个多边形,返回点集到vector
    vector_origin = tools.regular_polygon(sides=sides, side_length=30)
    # 取vector的垂直向量vector_pen
    vector_origin_pen = tools.vector_rotate(vector_origin, 90)

    for times,i in enumerate(vector_origin_pen):
        origin_lines=tools.vector_to_line(i, center)# 把vector_pen换成直线,直线要经过center
        #按照vector的方向,改变vector的模长-->获得平移向量distance_vector
        # TODO 此处模长可以不用以相同数值平移,可以存在长度差,应该再增加一个参数调整长度差
        distance_vector = tools.vector_change_norm(vector_origin[times], distance)

        #通过把平移向量distance_vector的x, y叠加在直线上, 平移直线
        tools.line_shift(origin_lines,distance_vector,rewrite=True,drop=False)

    origin_lines_data = tools.get_line_dic() #取出的直线数据,准备平移
    tools.reset() #清除内容

    gird= {} #{ vector_origin[0]:{0:{},1:{},-1:{},2:{}..}, vector_origin[1]:{0:{},1:{}...}, ...] 数字是循环的次数
    # 平移gird_0，构建平行网格gird
    for t, (letter, line_dict) in enumerate(origin_lines_data.items()):#遍历原始gird每一条线

        the_key = tuple(vector_origin[t]) #字典的键是原始向量,但是需要不可变对象

        gird[the_key]={0:line_dict}
        #在首行加入gird_0(原始线)

        # (num_of_line-1)是因为去掉原始line的1, 最后(..)//2+1是因为range不包括最后一项
        for the_time,i in enumerate(range(1, (num_of_line - 1) // 2 + 1)):

            # vector_origin的顺序和origin_lines的方向是一致的, 长度取zoom的倍数即可
            positive_vector = tools.vector_change_norm(vector_origin[t],zoom* i)
            negative_vector = tools.vector_change_norm(vector_origin[t],zoom* -i)

            line_positive_detail = tools.line_shift(line_dict,positive_vector,rewrite=False, drop=False)
            line_negative_detail = tools.line_shift(line_dict,negative_vector,rewrite=False, drop=False)

            gird[the_key][the_time+1] = line_positive_detail
            gird[the_key][-(the_time+1)] = line_negative_detail
    print("========开始输出========")
    for i,value in gird.items():
        print(i,'\n',value,'\n')
    print("=======================")
    return gird


def setup():
    global gird_data
    py5.size(800,600)
    py5.frame_rate(144)
    load()
    slider('sides',[50,py5.height-120],value=5,range=[3,15])
    slider('distance',location=[50,py5.height-90],value=15,range=[0,500])
    slider('zoom',location=[50,py5.height-60],value=150,range=[0,500])
    slider('num',location=[50,py5.height-30],size=[500,20],value=1,range=[0,500])
    gird_data = create_gird(5, 15, zoom=150, num_of_line=1, center=screen_axis(0, 0))
    #print(f"初次生成the_gird:{the_gird}")

def draw():
    global gird_data
    back = slider_value()
    if back is not None:
        gird_data=create_gird(sides=back['sides'],
                              distance=back['distance'],
                              zoom=back['zoom'],
                              center=screen_axis(0,0),
                              num_of_line=back['num'])
    py5.background(255)
    the_lines_dict_list = list(gird_data.values()) #一个列表中 包含很多组字典

    the_vector = list(gird_data.keys())
    screen_draw_vector(the_vector,screen_axis(-50,-50))

    for times,line_dict in enumerate(the_lines_dict_list):
        screen_draw_lines(line_dict,color=color[times%len(color)])

    screen_draw_lines(get_o_gird(the_lines_dict_list),stroke_weight=5,color=py5.color(0,0,0,125))
    screen_print_fps()

def get_o_gird(the_gird_data):
    """
    从gird_list中取出键为0的 返回一个字典。
    """
    tools=Tools2D()
    for lines_dict in the_gird_data:
        tools.line_dic[tools.extract_letter()] = lines_dict[0]
    return tools.get_line_dic()

if __name__ == "__main__":
    gird_data:dict
    py5.run_sketch()



