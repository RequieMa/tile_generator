# import gird
import py5
import json
import numpy as np
from YuSan_PY5_Toolscode import Tools2D


def distance_line_dict(line_dict, center=(250, 250)):
    """
    center：以某一点为中心求距离
    返回一个以距离作为key的line字典
    用于重新排序line字典便于进行tilling
    ！如果距离相同会返回列表型的Values
    """
    t = Tools2D()
    back_line_dict = {}
    rename = 0

    for key, value in line_dict.items():
        the_distance = t.distance_point_to_line(point=center, line=value)
        if the_distance in back_line_dict:
            if isinstance(back_line_dict[the_distance], list):
                # 如果已经是列表，将值添加到列表中
                back_line_dict[the_distance].append(value.copy())
            else:
                # 如果当前值不是列表，转换为列表
                back_line_dict[the_distance] = [back_line_dict[the_distance], value.copy()]
            continue
        back_line_dict[the_distance] = value.copy()
    back_line_dict = dict(sorted(back_line_dict.items()))  # 从小到大排序
    return back_line_dict

def setup():
    py5.size(500, 500)

def draw():
    py5.background(155)

def get_girds_interaction(girds_dict):
    """
    查找两个line字典之间的所有焦点
    输入值:((vector):{0:line_dict,1:xx,-1:xx},():{0:xx,1:xx,-1:xx})
    输出值:{ (p_x,p_y):[{v:v,n:n},{v_info}],[_x,_y]:[...],.. }
    """

    tools = Tools2D()
    vectors_list = list(girds_dict.keys())
    lines_dict_list = list(girds_dict.values())

    interaction_dict = {}
    for t_out, vector_A in enumerate(vectors_list[:-1]):  # 循环向量列表 切掉最后一项
        if vector_A not in interaction_dict:
            interaction_dict[vector_A] = {}
            # TODO 可以修改不用重新转换格式,而是一次性生成
        for t_in, vector_B in enumerate(vectors_list[t_out + 1:]):  # 循环向量列表 切掉当前项
            # {(vectorx,y):{}}
            if vector_B not in interaction_dict:
                interaction_dict[vector_B] = {}
            for number_A, line_detail_A in lines_dict_list[t_out].items():
                for number_B, line_detail_B in lines_dict_list[(t_out + 1) + t_in].items():
                    interaction_point = tools.intersection_2line(line_detail_A, line_detail_B)

                    if interaction_point is None: continue

                    if number_A not in interaction_dict[vector_A]:
                        interaction_dict[vector_A][number_A] = []
                    interaction_dict[vector_A][number_A].append(interaction_point)

                    if number_B not in interaction_dict[vector_B]:
                        interaction_dict[vector_B][number_B] = []
                    interaction_dict[vector_B][number_B].append(interaction_point)
                    # {(vectorx,y):{1:[[x,y],[x,y]],2:[...],..}..}
    # print('interaction_dict',interaction_dict)

    back_points_dict = {}
    for vector, num_dict in interaction_dict.items():
        for num, points_list in num_dict.items():
            for point in points_list:
                point = tuple(point)  # list不能做字典键
                if point not in back_points_dict:
                    back_points_dict[point] = []
                interaction_detail = {'vector': vector, 'num': num}
                back_points_dict[point].append(interaction_detail)
                # { (p_x,y):[{..},{..}],[p_x,y]:[...],.. }
    return back_points_dict

def get_tilling_information(gird_origin_vectors, vectors):
    """
    这是一个辅助函数,获得拼接图形的顺序,根据顺序可以拼接出闭合的多边形
    all_vectors_list是顺时针排列的origin_vector
    vector_list是当前交点的vectors信息
    返回一个列表,是拼接的顺序,可以按照这个顺序拼接出闭合多边形
    """
    # 例:1,2,3,4,5
    # 360/10=36-->180/36=5
    # 180/360/10-->5
    # 1,-4, 2,-5, 3,-1, 4,-2, 5,-3

    # 360/6=60-->180/60=3
    # 180/360/side*2=3
    #   ||
    # 间隔数目=sides
    #
    # 转换为:list[0]:1 list[2]:2 list[4]=3 list[6]=4 list[8]=5
    # list[(0+5)%10=5]=-1 list[(2+5)%10=7]=-2 list[(4+5)%10=9]=-3
    # list[(6+5)%10=1]=-4  list[(8+5)%10=3]=-5
    # TODO 目前all_vectors_list必须是顺时针排列,应该增加一个矩阵点乘来排列

    # 转换成元组方便使用集合方法
    the_origin_vectors = [tuple(vector) for vector in gird_origin_vectors]
    vectors_set = {tuple(vector) for vector in vectors}

    sides = len(the_origin_vectors)
    if sides % 2 != 0:  # 奇数
        print('进入奇数处理')
        temp_list = [None] * sides * 2
        for i, the_vector in enumerate(the_origin_vectors):
            if the_vector in vectors_set:
                temp_list[2 * i] = the_vector  # noqa
                temp_list[(2 * i + sides) % (sides * 2)] = (-the_vector[0], -the_vector[1])  # noqa
        tilling_vectors = [a_vector for a_vector in temp_list if a_vector is not None]

    else:  # 偶数
        back_list_positive = [the_vector for the_vector in the_origin_vectors if the_vector in vectors_set]
        back_list_negative = [(-the_vector[0], -the_vector[1])
                              for the_vector in the_origin_vectors if the_vector in vectors_set]
        # 考虑十字情况,有时正向量和反向量重复,合并的时候需要判断是否重复
        tilling_vectors = back_list_positive + [negative_v for negative_v in back_list_negative
                                                if negative_v not in back_list_positive]

    # tilling_vectors只是移动的路径,需要绘制成坐标点
    tilling_vectors_np = np.array(tilling_vectors)
    cumulative_sum = np.cumsum(tilling_vectors_np, axis=0)
    tilling = cumulative_sum.tolist()

    tem=Tools2D() #防止出现无穷小数
    tilling = [ [tem.reduce_errors(num=vector[0]),tem.reduce_errors(vector[1])] for vector in tilling]


    # 此处一并返回原vector,方便拼接.
    # vector_o[0]是 tilling[-1]和[0] (开头和末尾)
    # vector_o[1]是[0]和[1] (第一个和第二个)-->以此类推
    tilling_dict = {(tuple(vectors[0])): [tilling[-1], tilling[0]]}
    tilling_dict = tilling_dict | {(tuple(vector)): [tilling[t - 1], tilling[t]]  # noqa
                                   for t, vector in enumerate(tilling_vectors[1:], start=1)}  # 切掉了0 这样t不会超出index

    return tilling_dict

def splice_tilling(tilling_info_a, tilling_info_b, positive_direction):
    """
    start_interaction:某一个交点
    direction,拼接方向
    """
    # <think>一个交点具有两个向量,相应的具有:四个方向
    # TODO 在gird上面行走 例:一个交点是两条直线相交形成的,那么有4中行走方向(A正,A负,B正,B负)
    print()

gird_dict = {
    (0, 25.519524250561197): {0: {'str': 'y=315.0', 'k': 0, 'b': 315.0}, 1: {'str': 'y=465.0', 'k': 0, 'b': 465.0},
                              -1: {'str': 'y=165.0', 'k': 0, 'b': 165.0}}, (-24.27050983124842, 7.885966681787004): {
        0: {'str': 'y=3.08x-882.53', 'k': 3.0776835371752527, 'b': -882.5323952076043},
        1: {'str': 'y=3.08x-397.12', 'k': 3.0776835371752527, 'b': -397.12219858263586},
        -1: {'str': 'y=3.08x-1367.94', 'k': 3.0776835371752527, 'b': -1367.9425918325728}},
    (-15.000000000000002, -20.6457288070676): {
        0: {'str': 'y=-0.73x+572.08', 'k': -0.7265425280053612, 'b': 572.0759915396478},
        1: {'str': 'y=-0.73x+386.67', 'k': -0.7265425280053612, 'b': 386.66579491467934},
        -1: {'str': 'y=-0.73x+757.49', 'k': -0.7265425280053612, 'b': 757.4861881646164}},
    (14.999999999999996, -20.645728807067602): {
        0: {'str': 'y=0.73x-9.16', 'k': 0.7265425280053607, 'b': -9.158030864641127},
        1: {'str': 'y=0.73x-194.57', 'k': 0.7265425280053607, 'b': -194.56822748960957},
        -1: {'str': 'y=0.73x+176.25', 'k': 0.7265425280053607, 'b': 176.25216576032733}},
    (24.270509831248425, 7.885966681786999): {
        0: {'str': 'y=-3.08x+1579.61', 'k': -3.0776835371752562, 'b': 1579.6144345325993},
        1: {'str': 'y=-3.08x+2065.02', 'k': -3.0776835371752562, 'b': 2065.0246311575684},
        -1: {'str': 'y=-3.08x+1094.2', 'k': -3.0776835371752562, 'b': 1094.2042379076304}}}
origin_vectors = list(gird_dict.keys())
# back = get_girds_interaction(gird_dict)
# print(back)
back = {(389.10186207991956, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                      {'vector': (-24.27050983124842, 7.885966681787004), 'num': 0}],
        (231.38252844417948, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                      {'vector': (-24.27050983124842, 7.885966681787004), 'num': 1}],
        (546.8211957156598, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                     {'vector': (-24.27050983124842, 7.885966681787004), 'num': -1}],
        (353.83474694237145, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                      {'vector': (-15.000000000000002, -20.6457288070676), 'num': 0}],
        (98.63950443675957, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                     {'vector': (-15.000000000000002, -20.6457288070676), 'num': 1}],
        (609.0299894479834, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                     {'vector': (-15.000000000000002, -20.6457288070676), 'num': -1}],
        (446.16525305762883, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                      {'vector': (14.999999999999996, -20.645728807067602), 'num': 0}],
        (701.3604955632409, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                     {'vector': (14.999999999999996, -20.645728807067602), 'num': 1}],
        (190.97001055201676, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                      {'vector': (14.999999999999996, -20.645728807067602), 'num': -1}],
        (410.8981379200804, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                     {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (568.6174715558205, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                     {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (253.17880428434032, 315.0): [{'vector': (0, 25.519524250561197), 'num': 0},
                                      {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (437.8398165148555, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                     {'vector': (-24.27050983124842, 7.885966681787004), 'num': 0}],
        (280.12048287911546, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                      {'vector': (-24.27050983124842, 7.885966681787004), 'num': 1}],
        (595.5591501505957, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                     {'vector': (-24.27050983124842, 7.885966681787004), 'num': -1}],
        (147.37745887169552, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                      {'vector': (-15.000000000000002, -20.6457288070676), 'num': 0}],
        (-107.81778363391636, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                       {'vector': (-15.000000000000002, -20.6457288070676), 'num': 1}],
        (402.5727013773075, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                     {'vector': (-15.000000000000002, -20.6457288070676), 'num': -1}],
        (652.622541128305, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                    {'vector': (14.999999999999996, -20.645728807067602), 'num': 0}],
        (907.8177836339171, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                     {'vector': (14.999999999999996, -20.645728807067602), 'num': 1}],
        (397.4272986226929, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                     {'vector': (14.999999999999996, -20.645728807067602), 'num': -1}],
        (362.1601834851445, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                     {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (519.8795171208847, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                     {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (204.4408498494044, 465.0): [{'vector': (0, 25.519524250561197), 'num': 1},
                                     {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (340.3639076449836, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                     {'vector': (-24.27050983124842, 7.885966681787004), 'num': 0}],
        (182.64457400924354, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                      {'vector': (-24.27050983124842, 7.885966681787004), 'num': 1}],
        (498.08324128072377, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                      {'vector': (-24.27050983124842, 7.885966681787004), 'num': -1}],
        (560.2920350130474, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                     {'vector': (-15.000000000000002, -20.6457288070676), 'num': 0}],
        (305.0967925074355, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                     {'vector': (-15.000000000000002, -20.6457288070676), 'num': 1}],
        (815.4872775186593, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                     {'vector': (-15.000000000000002, -20.6457288070676), 'num': -1}],
        (239.70796498695273, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                      {'vector': (14.999999999999996, -20.645728807067602), 'num': 0}],
        (494.9032074925648, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                     {'vector': (14.999999999999996, -20.645728807067602), 'num': 1}],
        (-15.487277518659317, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                       {'vector': (14.999999999999996, -20.645728807067602), 'num': -1}],
        (459.6360923550163, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                     {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (617.3554259907564, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                     {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (301.91675871927623, 165.0): [{'vector': (0, 25.519524250561197), 'num': -1},
                                      {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (382.3664424312259, 294.27050983124866): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 0},
                                                  {'vector': (-15.000000000000002, -20.6457288070676), 'num': 0}],
        (333.62848799628995, 144.27050983124866): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 0},
                                                   {'vector': (-15.000000000000002, -20.6457288070676), 'num': 1}],
        (431.1043968661619, 444.27050983124866): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 0},
                                                  {'vector': (-15.000000000000002, -20.6457288070676), 'num': -1}],
        (371.4683045111454, 260.72949016875157): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 0},
                                                  {'vector': (14.999999999999996, -20.645728807067602), 'num': 0}],
        (292.60863769327534, 18.024391856267357): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 0},
                                                   {'vector': (14.999999999999996, -20.645728807067602), 'num': 1}],
        (450.32797132901544, 503.43458848123566): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 0},
                                                   {'vector': (14.999999999999996, -20.645728807067602), 'num': -1}],
        (400.0, 348.54101966249675): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 0},
                                      {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (478.8596668178701, 591.2461179749811): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 0},
                                                 {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (321.14033318212995, 105.83592135001254): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 0},
                                                   {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (254.7688211784199, 386.97560814373287): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 1},
                                                  {'vector': (-15.000000000000002, -20.6457288070676), 'num': 0}],
        (206.03086674348393, 236.97560814373287): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 1},
                                                   {'vector': (-15.000000000000002, -20.6457288070676), 'num': 1}],
        (303.50677561335584, 536.9756081437329): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 1},
                                                  {'vector': (-15.000000000000002, -20.6457288070676), 'num': -1}],
        (165.01101644046932, 110.72949016875151): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 1},
                                                   {'vector': (14.999999999999996, -20.645728807067602), 'num': 0}],
        (86.15134962259928, -131.97560814373264): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 1},
                                                   {'vector': (14.999999999999996, -20.645728807067602), 'num': 1}],
        (243.8706832583394, 353.4345884812358): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 1},
                                                 {'vector': (14.999999999999996, -20.645728807067602), 'num': -1}],
        (321.14033318213, 591.2461179749812): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 1},
                                               {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (400.0000000000001, 833.9512162874656): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 1},
                                                 {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (242.2806663642599, 348.54101966249686): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': 1},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (509.96406368403194, 201.56541151876445): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': -1},
                                                   {'vector': (-15.000000000000002, -20.6457288070676), 'num': 0}],
        (461.22610924909594, 51.56541151876422): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': -1},
                                                  {'vector': (-15.000000000000002, -20.6457288070676), 'num': 1}],
        (558.7020181189679, 351.56541151876445): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': -1},
                                                  {'vector': (-15.000000000000002, -20.6457288070676), 'num': -1}],
        (577.9255925818214, 410.7294901687512): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': -1},
                                                 {'vector': (14.999999999999996, -20.645728807067602), 'num': 0}],
        (499.06592576395144, 168.02439185626736): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': -1},
                                                   {'vector': (14.999999999999996, -20.645728807067602), 'num': 1}],
        (656.7852593996915, 653.4345884812358): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': -1},
                                                 {'vector': (14.999999999999996, -20.645728807067602), 'num': -1}],
        (478.85966681787005, 105.83592135001254): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': -1},
                                                   {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (557.7193336357401, 348.54101966249664): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': -1},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (400.0, -136.86917696247178): [{'vector': (-24.27050983124842, 7.885966681787004), 'num': -1},
                                       {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (400.00000000000006, 281.4589803375033): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 0},
                                                  {'vector': (14.999999999999996, -20.645728807067602), 'num': 0}],
        (527.597621252806, 188.75388202501904): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 0},
                                                 {'vector': (14.999999999999996, -20.645728807067602), 'num': 1}],
        (272.4023787471941, 374.1640786499875): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 0},
                                                 {'vector': (14.999999999999996, -20.645728807067602), 'num': -1}],
        (428.53169548885444, 260.72949016875185): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 0},
                                                   {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (634.9889835595304, 110.7294901687518): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 0},
                                                 {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (222.07440741817845, 410.7294901687519): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 0},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (272.4023787471941, 188.75388202501904): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 1},
                                                  {'vector': (14.999999999999996, -20.645728807067602), 'num': 0}],
        (400.00000000000006, 96.04878371253483): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 1},
                                                  {'vector': (14.999999999999996, -20.645728807067602), 'num': 1}],
        (144.80475749438813, 281.4589803375033): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 1},
                                                  {'vector': (14.999999999999996, -20.645728807067602), 'num': -1}],
        (507.39136230672443, 18.02439185626764): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 1},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (713.8486503774005, -131.97560814373247): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 1},
                                                   {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (300.93407423604845, 168.02439185626764): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': 1},
                                                   {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (527.5976212528061, 374.1640786499875): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': -1},
                                                 {'vector': (14.999999999999996, -20.645728807067602), 'num': 0}],
        (655.1952425056121, 281.45898033750325): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': -1},
                                                  {'vector': (14.999999999999996, -20.645728807067602), 'num': 1}],
        (400.00000000000017, 466.8691769624717): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': -1},
                                                  {'vector': (14.999999999999996, -20.645728807067602), 'num': -1}],
        (349.67202867098445, 503.4345884812361): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': -1},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (556.1293167416605, 353.43458848123606): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': -1},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (143.2147406003085, 653.4345884812362): [{'vector': (-15.000000000000002, -20.6457288070676), 'num': -1},
                                                 {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (417.6335575687742, 294.27050983124843): [{'vector': (14.999999999999996, -20.645728807067602), 'num': 0},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (545.2311788215803, 386.9756081437327): [{'vector': (14.999999999999996, -20.645728807067602), 'num': 0},
                                                 {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (290.0359363159682, 201.5654115187642): [{'vector': (14.999999999999996, -20.645728807067602), 'num': 0},
                                                 {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (466.3715120037101, 144.27050983124838): [{'vector': (14.999999999999996, -20.645728807067602), 'num': 1},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (593.9691332565161, 236.9756081437326): [{'vector': (14.999999999999996, -20.645728807067602), 'num': 1},
                                                 {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (338.7738907509041, 51.56541151876419): [{'vector': (14.999999999999996, -20.645728807067602), 'num': 1},
                                                 {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}],
        (368.8956031338382, 444.2705098312484): [{'vector': (14.999999999999996, -20.645728807067602), 'num': -1},
                                                 {'vector': (24.270509831248425, 7.885966681786999), 'num': 0}],
        (496.49322438664433, 536.9756081437326): [{'vector': (14.999999999999996, -20.645728807067602), 'num': -1},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': 1}],
        (241.29798188103226, 351.5654115187642): [{'vector': (14.999999999999996, -20.645728807067602), 'num': -1},
                                                  {'vector': (24.270509831248425, 7.885966681786999), 'num': -1}]}
print(origin_vectors)
print(get_tilling_information(origin_vectors, [(0, 25.519524250561197), (-24.27050983124842, 7.885966681787004)]))
# 输出结果:[[0, 25.519524250561197], [-24.27050983124842, 33.4054909323482], [-24.27050983124842, 7.8859666817870036], [0.0, -8.881784197001252e-16]]
