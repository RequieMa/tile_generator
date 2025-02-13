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

def create_gird(sides,distance=0,zoom=100,center=(100,100),line_num=50):
    """
    此函数用于创建一组网格系统 例[{0:..,1:..,-1:..},{..},{..}]
    distance：初始向量取垂直线以后，相互远离的距离。
    zoom：每条网格线相隔的距离
    返回一个列表，每个列表中包含一个方向的平行网格线，由所有网格线组成一个gird
    """
    global vector
    org_v = Tools2D()
    # 在【0，0】创建一个多边形,返回点集到vector
    vector = org_v.regular_polygon(sides=sides, side_length=30)
    # 取vector的垂直向量vector_pen
    vector_pen = org_v.vector_rotate(vector, 90)

    o_gird = Tools2D()
    for times,i in enumerate(vector_pen):
        the_line=o_gird.vector_to_line(i, center)# 把vector_pen换成直线,直线要经过center

        distance_vector = o_gird.vector_change_norm(vector[times],distance)
        o_gird.line_shift(the_line,distance_vector,rewrite=True,drop=False)
        # 按照原始向量方向平移distance距离

    gird_0 = o_gird.get_line_dic()#取得原始gird

    gird=[]
    # 平移gird_0，构建平行网格
    for t, (letter, line_detail) in enumerate(gird_0.items()):#遍历原始gird每一条线
        gird.append(Tools2D()) #为每一个组平行网格创建一个对象
        direction_vector = vector[t]  # 平移方向为vector

        zero_letter=gird[t].extract_letter()
        gird[t].line_dic[zero_letter]=line_detail.copy()
        #在首行加入gird_0(原始线)

        for i in range(1, (line_num-1)//2+1):
            # 用vector_change_norm拉伸向量长度
            gird[t].line_shift(line_detail,
                            gird[t].vector_change_norm(direction_vector,zoom* i),
                                                       rewrite=False, drop=True)
            gird[t].line_shift(line_detail,
                            gird[t].vector_change_norm(direction_vector, zoom* -i),
                                                       rewrite=False, drop=True)
            # 首先创建的是朝向量方向移动的，为奇数（从1开始），其次创建的是朝向量反方向平移的，为偶数

    back_list=[] #back_list最终要返回[gird_dict-1，gird_dict-2...]
    for the_obj in gird:#gird是一个对象列表[Tools2D(),Tools2D(),...]
        the_gird_dict=the_obj.get_line_dic().copy()
        len_gird=len(the_gird_dict)
        key_list=list(the_gird_dict.keys())
        new_gird_dict={}
        new_gird_dict[0]=the_gird_dict[key_list[0]] #原始平行线
        for in_times,num in enumerate(range(1,len_gird,2)):#遍历奇数
            new_gird_dict[in_times+1]=the_gird_dict[key_list[num]] #正方向移动的平行线
        for in_times,num in enumerate(range(2,len_gird,2)):#遍历偶数
            new_gird_dict[-(in_times+1)] = the_gird_dict[key_list[num]] #负方向移动的平行线
        back_list.append(new_gird_dict.copy())
    #TODO 此处应该单独返回vector字典，字典内容要保证向量顺序
    back_dict={}
    back_keys=list(vector) #gird顺序 应该和vector(原始向量)顺序 是对应的
    for t,the_back_gird in enumerate(back_list):
        back_dict[tuple(back_keys[t])]=the_back_gird

    return back_dict

def setup():
    global the_gird_dict
    py5.size(800,600)
    py5.frame_rate(144)
    load()
    slider('sides',[50,py5.height-120],value=5,range=[3,15])
    slider('distance',location=[50,py5.height-90],value=15,range=[0,500])
    slider('zoom',location=[50,py5.height-60],value=150,range=[0,500])
    slider('num',location=[50,py5.height-30],size=[500,20],value=50,range=[0,500])
    the_gird_dict = create_gird(5, 15, zoom=150, line_num=50,center=screen_axis(0,0))
    #print(f"初次生成the_gird:{the_gird}")
def draw():
    global the_gird_dict
    back = slider_value()

    if back is not None:
        the_gird_dict=create_gird(sides=back['sides'],
                             distance=back['distance'],
                             zoom=back['zoom'],
                             center=screen_axis(0,0),
                             line_num=back['num'])
    py5.background(255)
    the_gird =list(the_gird_dict.values())
    the_vector = list(the_gird_dict.keys())
    screen_draw_vector(the_vector,screen_axis(-50,-50))
    for times,i in enumerate(the_gird):
        #TODO 此处由于字典很大 速度会变慢 需要解决
        screen_draw_lines(i,color=color[times%len(color)])
    screen_draw_lines(get_o_gird(the_gird),stroke_weight=5,color=py5.color(0,0,0,125))
    screen_print_fps()
def get_o_gird(gird_list):
    """
    从gird_list中取出键为0的 返回一个字典。
    """
    o_gird=Tools2D()
    for i in gird_list:
        #0理应存在于gird_list因为是原始直线
        o_gird.line_dic[o_gird.extract_letter()]=i[0]
    return o_gird.get_line_dic()

if __name__ == "__main__":
    the_gird_dict:dict
    py5.run_sketch()



