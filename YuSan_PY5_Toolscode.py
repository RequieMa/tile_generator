import numpy as np
import py5
from collections import defaultdict
import math
import random


class Tools2D:
    """
    有向线段（Directed Segment）：它是一个具体的几何对象，表示从一个起点到一个终点的线段，并且明确指出了方向（从起点到终点）。
    """
    def __init__(self,screen_info=None):
        self.point_dic = {}  # 存储点的字典
        self.Segmentline_dic = {}  # 存储线段的字典
        self.surface_dic = {}  # 存储面的字典
        self.line_dic = {}  # 存储直线的字典
        self.reverse_point_dic = defaultdict(list) #创建储存点的反字典 便于倒查
        # 初始化字母表
        self.alphabetize_Capital = [chr(i) for i in range(65, 91)]  # ASCII 65-90 对应 A-Z
        self.alphabetize = [chr(i) for i in range(97, 123)]  # ASCII 范围 97 到 122
        # 初始化字母队列和索引
        self.letter_queue = self.alphabetize.copy()  # [a,b,c...z]
        self.letter_queue_capital = self.alphabetize_Capital.copy()  # [A,B,C,D...Z]
        self.letter_index = 0  # 字母的后缀序列
        self.letter_index_capital = 0  # 字母的后缀序列
        if screen_info:
            self.screeninfo=screen_info

    def reset(self):
        """
        调用_init_()重新初始化
        """
        self.__init__()
    def get_point_dic(self):
        return self.point_dic
    def get_Segmentline_dic(self):
        back_dic={}
        for i in self.Segmentline_dic.keys():
            back_dic[i]=self.Segmentline_get_info(i)
        return back_dic
    def get_line_dic(self):
        """
        line_dic格式:{字母代号:{a:int,k:int,b:int}, 字母代号:{...}, ...}
        """
        return self.line_dic
    def get_surface_dic(self):
        return self.surface_dic

    # ================点线面存取操作================
    # ////////////《点操作》////////////

    def point_drop(self, point_xy,specified=None):
        """
        如果point_xy格式不对会报错
        在reverse_pointdic创建一个(x,y)作为key的倒字典便于搜索
        pecified: 可以输入一个指定字符作为point的名称代号 NONE为自动指定
        :return: 返回新创建point的字母代号 例如：A
        """
        if not self.list_depth(point_xy) == 1 and len(point_xy) == 2:
            raise ValueError(f"输入的坐标异常,为:{point_xy}")  #输入格式[x,y]
        if specified is not None:
            if not isinstance(specified,str):
                raise ValueError(f"指定点名称错误,为:{specified}")  # 输入格式[x,y]
            letter = specified
            if specified in self.point_dic:
                #当前指定的已经创建,进行覆盖操作(先删除再申请)
                self.point_remove_by_letter(specified)
            self.apply_letter_capital(specified)#申请指定点
        else:
            letter = self.extract_letter_capital()
            #未指定点,自动指定一个点
        self.point_dic[letter] = point_xy #加入字典
        self.reverse_point_dic[tuple(point_xy)].append(letter) #加入反字典
        return letter
    def distance_2_points_matrix(self,Apoint,Bpoint):
        """
        矩阵方法求norm 使用的是np矩阵
        """
        A=self.point_get_info(Apoint)['location']
        B=self.point_get_info(Bpoint)['location']
        np_A = np.array(A)
        np_B = np.array(B)
        return np.linalg.norm(np_A - np_B)
    def distance_2_points(self,point1, point2):
        """
        计算两个点之间的距离 经典平方根方法

        参数:
        point1: 通用,既可以是'代号'也可是(x,y)
        point2: 通用,既可以是'代号'也可是(x,y)
        返回:
        两点之间的距离
        """
        x1, y1 = self.point_get_info(point1)['location']
        x2, y2 = self.point_get_info(point2)['location']
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    def point_remove_by_letter(self, aletter):
        """
        删除指定字母对应的点，并将其重新插入到 nowletterlist 中。
        失败返回 False。
        """
        self.back_letter_capital(aletter)
        value=self.point_dic[aletter]
        del self.point_dic[aletter]
        if len(self.reverse_point_dic[tuple(value)])>1:
            #如果列表中内容超过一项,那么有多个点名称同时存在
            re_write=self.reverse_point_dic[tuple(value)]
            re_write.remove(aletter) #从其中删除指定代号
            self.reverse_point_dic[tuple(value)]=re_write #重新覆写回去
        elif len(self.reverse_point_dic[tuple(value)])==1:
            del self.reverse_point_dic[tuple(value)]
        else:
            raise ValueError(f"删除reverse_pointdic时,发生未知错误altter:{aletter}")
    def point_remove_by_xy(self, point_xy):
        """
        通过调用point_get_info调用point_remove_by_letter
        失败返回False
        """
        info=self.point_get_info(point_xy)
        if info['letter'] is not None:
            return self.point_remove_by_letter(info['letter'])
        else:
            return False
    def point_drop_group(self, point_xy_group):
        """
        循环调用 point_drop
        :param point_xy_group: [a,b][c,d][e,f]格式不会会报错
        :return: 返回一个代号列表[A,B,C,D]
        """
        back = []
        for i in point_xy_group:
            if not isinstance(i, list):
                if not isinstance(i, tuple):
                    raise ValueError("data is not list or tuple")
            if len(i) == 2:
                back.append(self.point_drop(i))
            else:
                raise ValueError("data is not:([x,y],(x,y),(x,y))")
        return back
    def point_get_info(self, point_xy_or_letter):
        """
        如果还未创建,返回None
        无论输入的是 (x,y) or 字符代号
        统一返回一个字典 包括'type':返回'letter'或者'point_xy'
        'letter':字母代号 如果未找到此项会返回None
        'location':坐标值[x,y]
        """
        back_dict = {}
        if isinstance(point_xy_or_letter, str) and point_xy_or_letter:
            #如果输入的是字母:
            if point_xy_or_letter not in self.point_dic.keys():
                #输入的字母不在字典中
                raise ValueError(f"输入的字母{point_xy_or_letter}不在字典中:{self.point_dic}")
            detail_point = self.point_dic[point_xy_or_letter]
            point_x = detail_point[0]
            point_y = detail_point[1]
            letter = point_xy_or_letter
            input_type = 'letter'
        elif isinstance(point_xy_or_letter, (list, tuple, np.ndarray)) and len(point_xy_or_letter) == 2:
            point_x = point_xy_or_letter[0]
            point_y = point_xy_or_letter[1]
            input_type = 'point_xy'
            if tuple(point_xy_or_letter) in self.reverse_point_dic:
                letter = self.reverse_point_dic[tuple(point_xy_or_letter)][0]
            else:
                letter = None
        else:
            raise ValueError(f"未知错误,输入的点是{point_xy_or_letter}")
        back_dict['type']=input_type
        back_dict['letter']=letter
        back_dict['location']=[point_x,point_y]
        return back_dict
    def point2_to_vector(self, Apoint, Bpoint):
        """
        默认是自A向B出发的向量
        point既可以输入字符代号,也可以输入[x,y]
        返回值:vector[x,y]
        """
        A_x, A_y = self.point_get_info(Apoint)['location']
        B_x, B_y = self.point_get_info(Bpoint)['location']
        vector = [self.reduce_errors(B_x - A_x), self.reduce_errors(B_y - A_y)]
        return vector
    def point_shift(self, point, vector):
        """
        将point按照vector的方向平移
        此方法point只接受[x,y],或者point的列表[[x,y],[x,y]]
        vector:[x,y]
        返回值:平移后新的point坐标[x,y]
        """
        if not isinstance(vector, (tuple, list)) or len(vector) != 2:
            raise ValueError(f"平移向量错误,当前为{vector}")
        s_x, s_y = vector[0], vector[1]
        if self.list_depth(point)==2:
            #如果输入的是一组点而不是一个点
            back_list=[]
            for i in point:
                p_x, p_y = i[0], i[1]
                back_x = p_x + s_x
                back_y = p_y + s_y
                back_list.append([back_x, back_y])
            return back_list
        p_x, p_y = point[0], point[1]
        back_x = p_x + s_x
        back_y = p_y + s_y
        return [back_x, back_y]
    def vector_rotate(self, vector, theta):
        """
        把向量按照theta角度(度数)旋转
        vector接受单个点,也接受一组点
        返回:新的向量列表
        """
        # 将角度转换为弧度
        theta = np.radians(theta)
        # 旋转矩阵
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]])
        if self.list_depth(vector)==2:
            #如果输入的是一组点而不是一个点
            backlist=[]
            for i in vector:
                np_vector = np.array(i)
                backlist.append( list(np.dot(rotation_matrix, np_vector)) )
            return backlist
        np_vector = np.array(vector)
        rotated_vector = np.dot(rotation_matrix, np_vector)# 旋转向量

        x,y=list(rotated_vector) #防止无限接近0的情况
        return [self.reduce_errors(x),self.reduce_errors(y)]
    def vector_get_norm(self,vector):
        #math.hypot 函数可以正确处理负数
        back = math.hypot(vector[0],vector[1])
        return back
    def vector_change_norm(self, vector, norm=1):
        """
        调整向量的模长
        返回一个新的vector[x,y]
        """
        if not isinstance(vector, (tuple, list)) or len(vector) != 2:
            raise ValueError(f"平移向量错误,当前为{vector}")
        v_x, v_y = vector
        if v_x == 0 and v_y == 0:
            raise ValueError("无法修改0向量的模长")
        if v_x == 0:
            if vector[1]<0:
                #负数情况
                return [0, -norm]
            return [0, norm]
        if v_y == 0:
            if vector[0]<0:
                return [-norm,0]
            return [norm, 0]
        multiple = norm / math.hypot(v_x, v_y)
        back = [v_x * multiple, v_y * multiple]
        return back
    def reduce_errors(self, num, max_value=1e10, min_value=1e-10):
        """
        如果接近无穷大返回None，接近无穷小返回0
        """
        if abs(num)>max_value:
            return None
        elif abs(num)<min_value:
            return 0
        return num

    def vector_to_line(self,vector,passing_point=(0,0),temp=False):
        """
        passing_point,直线经过的点，默认(0，0)
        向量换直线,返回的是字母代号。如果temp=True 返回字典。
        """
        if self.reduce_errors(vector[0])==0 and self.reduce_errors(vector[1])==0:
            return None
        if self.reduce_errors(vector[0])==0:
            #垂直情况
            #x=b ; k=-1 a=0
            return self.line_drop(a=0,k=-1,b=passing_point[0])
        if self.reduce_errors(vector[1])==0:
            #水平情况
            #y=b ;a=1 k=0
            return self.line_drop(a=1,k=0,b=passing_point[1])

        k=self.reduce_errors(vector[1]/vector[0])
        if k is None:
            a=0 #无穷小
        else:
            a=1
        b=self.line_solve_general(a=a,x=passing_point[0],y=passing_point[1],k=k)['b']
        return self.line_drop(a=a,k=k,b=b,temp=temp)
    def line_shift(self,line_letter_or_dic, vector,rewrite=True,drop=True):
        """
            对line或directed_line进行平移操作。

            参数:
                line_letter_or_dic (str or dict): 直线的标识符（字符串）或直线的详细信息（字典）。
                vector (tuple or list): 平移向量[x,y]
                rewrite (bool): 是否更新 self.line_dic 中的直线信息。
                drop (bool): 当前直线还未创建,创建一个新的直线对象。
        """
        k=None
        if not isinstance(vector, (tuple, list)) or len(vector) != 2:
            raise ValueError(f"平移向量错误,当前为{vector}")

        if isinstance(line_letter_or_dic, str):
            detail = self.line_dic[line_letter_or_dic].copy()
            letter = line_letter_or_dic
        elif isinstance(line_letter_or_dic, dict):
            detail=line_letter_or_dic.copy()
            letter = None
        else:
            raise ValueError(f"输入直线错误,为{line_letter_or_dic}")

        if 'directed' in detail:#获取有向线段
            location_x,location_y=detail['location_point']
            detail['location_point']=[location_x+vector[0],location_y+vector[1]]

        elif 'a' in detail:
            #x=b
            a = detail['a']
            k = -1
            new_b = detail['b']+vector[0]
            detail['b'] = new_b
            detail['str'] = f'x={round(new_b,2)}'
            if drop:
                return self.line_drop(k=k, b=new_b,a=a)

        else:# 处理普通直线（y = kx + b 或水平线 y = b）
            b = detail['b']
            k = detail['k']

            if k == 0:# 水平线（y = original_b）
                # y=b
                new_b = detail['b'] + vector[1]
                detail['str'] = f'y={round(new_b, 2)}'
            else:
                new_b = b + vector[1] - k * vector[0] #(y-v1)=k(x-v0)+b-->y=kx - k*v0 + v1 +b -->b -k*v0 + v1
                if new_b > 0: detail['str'] = f'y={round(k, 2)}x+{round(new_b, 2)}'
                if new_b == 0: detail['str'] = f'y={round(k, 2)}x'
                if new_b < 0: detail['str'] = f'y={round(k, 2)}x{round(new_b, 2)}'
            detail['b']=new_b

        if letter and rewrite:
            # 更新 self.line_dic 中的直线信息
            self.line_dic[letter] = detail
            return letter

        if drop:#返回新的直线对象
            if 'directed' in detail:
                return self.directed_line_drop(detail['location_point'],detail['direction_vector'])
            if k:
                return self.line_drop(k=detail.get('k'), b=detail['b'], a=detail.get('a', 1))

        else: #返回更新后的直线详细信息
            return detail

    # ////////////《线操作》////////////
    def Segmentline_drop(self, Apoint, Bpoint, floor=0, color=py5.color(0, 0, 0, 255), stroke_weight=3,
                         visible=True):
        """
        :param floor: 图层高度
        :param color: 只接受py5.color()之后的数值 否则后面绘制会出错
        :param visible: 是否可视，在绘制辅助线时候可以设置为=False
        """
        A_info=self.point_get_info(Apoint)
        if A_info['letter'] is None:
            Aletter = self.point_drop(A_info['location'])
        else:
            #当前点已经存在 直接使用
            Aletter = A_info['letter']
        B_info=self.point_get_info(Bpoint)
        if B_info['letter'] is None:
            Bletter = self.point_drop(B_info['location'])
        else:
            #当前点已经存在 直接使用"
            Bletter= B_info['letter']
        #判断提供的点是否创建 如果没有创建就提前创建
        inf = {}
        inf["floor"] = floor
        inf["color"] = color
        inf["stroke_weight"] = stroke_weight
        inf["visible"] = visible
        self.Segmentline_dic[Aletter + "-" + Bletter] = inf
        return Aletter + "-" + Bletter

    def Segmentline_get_info(self,chain_or_2pointxy):
        """
        如果返回None 说明该直线还未创建
        返回一个字典 包括键location[[x1,y1],[x2,y2]],chain,还有绘制信息(floor,color,visible,stroke_weight)
        """
        if isinstance(chain_or_2pointxy,str):
            if not chain_or_2pointxy in self.Segmentline_dic:
                return None
            A_point,B_point=chain_or_2pointxy.split('-')
        elif isinstance(chain_or_2pointxy,(list,tuple))and len(chain_or_2pointxy)==2:
            A_point = chain_or_2pointxy[0]
            B_point = chain_or_2pointxy[1]
        else:
            raise ValueError(f"输入的值有问题,为:{chain_or_2pointxy}")
        A_info,B_info= self.point_get_info(A_point),self.point_get_info(B_point)
        if A_info['letter'] is None or B_info['letter'] is None:
            return None
        back_dic = {}
        back_dic['location'] = [A_info['location'],B_info['location']]
        back_dic['chain']=A_info['letter']+'-'+B_info['letter']
        more = self.Segmentline_dic[back_dic['chain']]
        back_dic = back_dic | more
        return back_dic

    def Segmentline_remove_by_chain(self, chain):
        del self.Segmentline_dic[chain]

    def line_drop(self, k, b, a=1, temp=False):
        """
        保存一个函数：ay=kx+b
        如果字典detail_dic中有'a'键: a肯定是0 k肯定是-1(自动化简) 储存的是x=b 是一个垂直线
        如果字典中 k=0 是y=b 是一个水平线
        :param a: 如果a不是1或0 会报错/#/内容:认定输入的是ay+bx+k=0
        :param temp: 如果为True 那么不创建到字典中 仅返回一个kba字典
        :return: temp=False 返回一个字母代号 例如：a temp=True 不创建到字典中 仅返回一个kba字典
        """
        detail_dic = {}
        if a == 0 and k == 0:
            raise ValueError("a和k不能同时为0，请检查输入")
        if a == 0:
            line_str = f"x={round(b / -k / -1, 2)}"
            detail_dic['str'] = line_str
            detail_dic['b'] = b / -k #0y=kx+b b/-k=x
            detail_dic['k'] = -1
            detail_dic['a'] = 0
        if k == 0:
            line_str = f"y={round(b,2)}"
            detail_dic['str'] = line_str
            detail_dic['k'] = 0
            detail_dic['b'] = b
        if a == 1 and k != 0:
            if b > 0:
                line_str = f"y={round(k,2)}x+{round(b,2)}"
            elif b < 0:
                line_str = f"y={round(k,2)}x{(round(b,2))}"
            elif b == 0:
                line_str = f"y={round(k,2)}x"
            else: raise ValueError(f"b值出现错误,b为:{b}")
            detail_dic['str'] = line_str
            detail_dic['k'] = k
            detail_dic['b'] = b
        if a != 0 and a != 1 and a is not None:
            raise ValueError(f"输入不符合要求,a只能是0或1,当前输入:{a}")
            # # ay+bx+c=0
            # k = b / a
            # b = k / a
            # if b > 0:
            #     line_str = f"y={k}x+{b}"
            # elif b < 0:
            #     line_str = f"y={k}x-{b}"
            # elif b == 0:
            #     line_str = f"y={k}x"
            #
            # detail_dic['str'] = line_str
            # detail_dic['k'] = k
            # detail_dic['b'] = b
        if temp:
            return detail_dic
        new_letter = self.extract_letter()
        self.line_dic[new_letter] = detail_dic
        return new_letter

    def line_remove(self, letter):
        """
        删除线
        失败返回False
        """
        if letter in self.line_dic:
            del self.line_dic[letter]
            self.back_letter(letter)
        else:
            return False

    def line_to_Segmentline(self, line, x_range=None, y_range=None, floor=0, color=py5.color(0, 0, 0, 255), stroke_weight=3,
                            visible=True):
        """
        line:可以接受 letter 或者 dict
        x_range,y_range:如果不提供默认使用屏幕尺寸
        """
        def xrange_to_Segline(range):
            range_min = range[0]
            range_max = range[1]
            back = self.Segmentline_drop(
                Apoint=[range_min, self.line_solve(line, x=range_min)],
                Bpoint=[range_max, self.line_solve(line, x=range_max)],
                **inputvalue
            )
            return back

        inputvalue = {'floor': floor, 'color': color, 'stroke_weight': stroke_weight, 'visible': visible}

        #如果提供的不是字典，那么在line_dic中查找
        if not isinstance(line,dict):
            if not line in self.line_dic:
                raise ValueError(f'没有找到给定line：{line}')
            line = self.line_dic[line]

        # 如果没有提供取值范围
        if x_range is None and y_range is None:
            print('没有提供 x_range 和 y_range 取值范围,使用屏幕范围')
            if self.screeninfo is None:
                raise ValueError("没有提供屏幕范围参数")
            x_range = self.screeninfo['xrange']
            y_range = self.screeninfo['yrange']
        if x_range is None and self.screeninfo is not None:
            # 没有提供x_range取值范围,但可以使用屏幕范围的x_range缩小计算量
            x_range = self.screeninfo['xrange']
        if y_range is None and self.screeninfo is not None:
            # 没有提供y_range取值范围,但可以使用屏幕范围的y_range缩小计算量
            y_range = self.screeninfo['yrange']

        # 如果是垂直线（ay=kx+b,其中a=0）
        if 'a' in line:
            if line['a'] != 0:
                raise ValueError(f'无法处理a不等于0的时刻，检查line：{line}')
            # 0=-x+b
            value_k = line['k']
            value_b = line['b']
            value_x = value_b / -value_k
            #垂直线的Y值(x=b/(-k))
            if y_range is None:
                raise ValueError(f'垂直线{line}没有y_range无法求解成直线，因为必须要屏幕范围')
            elif y_range[0] == y_range[1]:
                raise ValueError(f'垂直线{line}取值范围为一个点，无法生成直线')

            if x_range:
                x_min, x_max = sorted([x_range[0], x_range[1]])
                if x_min <= value_x <= x_max:  # 垂直线要在x的取值范围中
                    return self.Segmentline_drop(Apoint=[value_x, y_range[0]],
                                                 Bpoint=[value_x, y_range[1]],
                                                 **inputvalue)
                return False  # 不在范围中返回False
            else:
                return self.Segmentline_drop(Apoint=[value_x, y_range[0]],
                                             Bpoint=[value_x, y_range[1]],
                                             **inputvalue)

        #整理取值范围，返回x_min,x_max,y_to_x_min,y_to_x_max,y_min,y_max
        if x_range is not None:
            x_min, x_max = sorted([x_range[0], x_range[1]])
            if x_min==x_max: return False #上文已经判断过垂直线的情况，如果出现x取值范围是一个点，那么不可能有解
        if y_range is not None:
            y_min, y_max = sorted([y_range[0], y_range[1]])
            y_min_to_x=self.line_solve(line,y=y_min)
            y_max_to_x=self.line_solve(line,y=y_max)
            if y_min_to_x is None and y_max_to_x is None:
                # 处理水平线
                y_value = self.line_solve(line, x=0)  #获取水平线的固定 y 值
                if not (y_min <= y_value <= y_max):#校验 y 值是否在范围内
                    return False  # y 值超出允许范围
                # 返回水平线段
                return self.Segmentline_drop(
                    Apoint=[x_min, y_value],
                    Bpoint=[x_max, y_value],
                    **inputvalue
                )
            elif y_min_to_x is None or y_max_to_x is None:
                raise ValueError(f"取值{y_min_to_x,y_max_to_x}只出现一个是无穷大，未知错误")
            y_to_x_min,y_to_x_max=sorted([y_min_to_x,y_max_to_x])
            if y_to_x_min==y_to_x_max:return False #未知错误，此时是垂直线，因为y取任何值时x值都是相同的，但是上文已经判断过a=0的情况

        if x_range is None:
            #此时y_range必然存在。不存在赋值前引用
            # 因为上文存在判断：x_range is None and y_range is None
            return self.Segmentline_drop([y_min_to_x,y_min],[y_max_to_x,y_max],**inputvalue)
        if y_range is None:
            x_min_to_y=self.line_solve(line,x=x_min)
            x_max_to_y = self.line_solve(line, x=x_max)
            return self.Segmentline_drop([x_min, x_min_to_y], [x_max,x_max_to_y], **inputvalue)

        if x_range is not None and y_range is not None:
            #把y也换算成x的范围
            y_to_x_range = [y_to_x_min, y_to_x_max]
            new_range_x = self.get_inter_range(x_range, y_to_x_range)#调用get_inter_range找到交集
            if new_range_x is None:return False
            if new_range_x[0] == new_range_x[1]:return False
            return xrange_to_Segline(new_range_x)

    def directed_line_to_line(self,line_letter_or_detail_dic,temp=True):
        if isinstance(line_letter_or_detail_dic, dict):
            detail_dic = line_letter_or_detail_dic
        else:
            if line_letter_or_detail_dic not in self.line_dic:
                raise ValueError("没有找到直线，直线还未创建")
            detail_dic = self.line_dic[line_letter_or_detail_dic]

        if 'direction_vector' not in detail_dic or 'location_point' not in detail_dic:
            raise KeyError("有向直线的描述字典缺少必要的字段 'direction_vector' 或 'location_point'")

        vx,vy = detail_dic['direction_vector']
        lx,ly = detail_dic['location_point']
        if vx==0:#垂直线
            # 垂直线公式：0y = -1x + b → x = b
            # 参数k在此场景下仅为占位符，固定为-1
            return self.line_drop(a=0,k=-1,b=lx,temp=temp)
        else:#常规线(包括水平)
            k = vy/vx
            b=  ly - k * lx
            return self.line_drop(a=1,k=k,b=b,temp=temp)

    def line_solve(self, line_letter_or_detail_dic, x=None, y=None):
        """
        给定 x 或 y，解决直线方程 ay = kx + b 的问题。
        :param line_letter_or_detail_dic: 直线的标识字母（例：'a'），或者一个包含详细信息的字典。
        :param x: 已知的 x 值。
        :param y: 已知的 y 值。
        :return: 求解的另一个坐标值。
        如果返回None代表可以取任意值
        """
        # 获取直线的详细信息
        if isinstance(line_letter_or_detail_dic, dict):
            detail_dic = line_letter_or_detail_dic
        else:
            if line_letter_or_detail_dic not in self.line_dic:
                raise ValueError("没有找到直线，直线还未创建")
            detail_dic = self.line_dic[line_letter_or_detail_dic]

        # 检查是否提供了 x 或 y
        if x is None and y is None:
            raise ValueError("x 和 y 都没有输入值，无法计算")

        # 获取直线参数
        k = detail_dic['k']
        a = detail_dic.get('a', 1)  # 默认 a = 1
        b = detail_dic.get('b', 0)  # 默认 b = 0

        # 计算 y
        if y is None:
            if a == 0:
                return None #此时为垂直线,y可以取任意值
            return (k * x + b) / a  # y = (kx + b) / a

        # 计算 x
        if x is None:
            if k == 0:
                if a == 0:
                    raise ValueError("a = 0 且 k = 0 时，方程无意义，无法计算 x")
                return None #此时x取值为任意值
            return (a * y - b) / k  # x = (ay - b) / k

    def line_solve_general(self, a=1, y=None, k=None, x=None, b=None, A_point=None, B_point=None):
        """
        使用矩阵方法求解线性方程 ay = kx + b 或根据两点 (x1, y1) 和 (x2, y2) 计算 k 和 b。
        参数：
            a, y, k, x, b: 任意提供 ay = kx + b 的四个变量，求解第五个变量。
            A_point, B_point: 提供两点，求解 k 和 b，即使 x1 == x2 时也可以通过 a = 0 处理。
        返回：
            结果字典，包含已求解的变量及其值。
            当 a=0 且 k 都未给出时，函数将默认返回 k=1 ，即方程 x=-b
        """
        if a != 1 and a != 0:
            # 如果存在a值任意的话，把函数当作ay+kx+b=0来处理
            a = -a  # 我把这里添加了相反数是因为结尾输出的时候 是按照ay=kx+b书写的 所以-ay+kx+b=0
        # 1. 根据两点计算 k 和 b
        if A_point is not None and B_point is not None:
            if any(i is not None for i in (y, k, x, b)) and a != 1:
                raise ValueError("输入两点时候 请不要提供其它参数")
            if len(A_point) != 2 or len(B_point) != 2:
                raise ValueError("点格式不符合规范，A_point 和 B_point 应为 (x, y) 形式的元组或列表")
            x1, y1 = A_point
            x2, y2 = B_point
            if x1 == x2:  # 特殊情况：x1 == x2，垂直线
                return {
                    "a": 0,  # y 的系数为 0
                    "k": -1,  # 假设 k = -1
                    "b": x1,  # b = x1
                }
            else:  # 正常情况，使用矩阵方程计算 k 和 b
                A = np.array([[x1, 1], [x2, 1]])
                B = np.array([y1, y2])
                result = np.linalg.solve(A, B)
                return {"a": 1, "k": result[0], "b": result[1]}

        # 2. 特殊情况：a = 0
        if a == 0:
            # 方程退化为 kx + b = 0
            if k == 0:
                raise ValueError("0x+b=0")
            if k is not None and b is not None:
                return {"x": -b / k}
            elif x is not None:
                if k is None:
                    # 默认 k = 1
                    k = 1
                return {"b": -k * x}
            elif b is not None:
                if k is None:
                    # 默认 k = 1
                    k = 1
                return {"x": -b / k}
            else:
                raise ValueError("如果既没有 k，也没有 b，无解")

        # 3. 确保 y = kx + b 中有3个已知变量
        inputs = {"y": y, "k": k, "x": x, "b": b}
        known_values = {key: value for key, value in inputs.items() if value is not None}
        if len(known_values) != 3:
            raise ValueError("必须提供 y = kx + b 的3个变量才能求解")

        # 4. 根据未知变量求解，添加除零保护
        elif y is None:
            return {"y": (k * x + b) / a}
        elif k is None:
            if x == 0:
                raise ZeroDivisionError("x 不能为零")
            return {"k": (a * y - b) / x}
        elif x is None:
            if k == 0:
                raise ZeroDivisionError("k 不能为零")
            return {"x": (a * y - b) / k}
        elif b is None:
            return {"b": a * y - k * x}

        # 如果所有变量都已知，直接返回
        return known_values

    def intersection_2_Segmentline_Matrix(self, Aline, Bline):
        """
        使用矩阵方法 numpy 计算两条线段的交点
        :param A1: 线段 A 的起点 (x1, y1)
        :param A2: 线段 A 的终点 (x2, y2)
        :param B1: 线段 B 的起点 (x3, y3)
        :param B2: 线段 B 的终点 (x4, y4)
        :return: 交点坐标 (x, y)，如果没有交点返回 None
        """
        x1, y1 = Aline[0]
        x2, y2 = Aline[1]
        x3, y3 = Bline[0]
        x4, y4 = Bline[1]

        # 创建系数矩阵 A@缩小量=b
        A = np.array([[x2 - x1, x3 - x4], [y2 - y1, y3 - y4]])
        b = np.array([x3 - x1, y3 - y1])

        # 计算行列式
        det = np.linalg.det(A)

        # 判断是否平行或共线
        if abs(det) < 1e-10:  # 行列式接近 0，表示两条线段平行或共线
            return None

        # 解线性方程组
        t, s = np.linalg.solve(A, b)

        # 判断参数 t 和 s 是否在 [0, 1] 范围内
        if 0 <= t <= 1 and 0 <= s <= 1:
            # 计算交点坐标
            intersection_x = x1 + t * (x2 - x1)
            intersection_y = y1 + t * (y2 - y1)
            return (intersection_x, intersection_y)

        return None  # 如果 t 或 s 不在范围内，则没有交点

    def intersection_2_Segmentline(self, A_seg_Chain_or_2pointxy, B_seg_Chain_or_2pointxy):
        """
        返回 None 则没有交点
        可以混用Chain和2pointxy
        :param A_seg_Chain_or_2pointxy: 可以是Chain，也可以是列表：[ [a,b] , [c,d] ]
        :param B_seg_Chain_or_2pointxy: 可以是Chain，也可以是列表：[ [a,b] , [c,d] ]
        """
        A_info=self.Segmentline_get_info(A_seg_Chain_or_2pointxy)
        if A_info is None:
            raise ValueError(f"没有找到A线段{A_seg_Chain_or_2pointxy}")
        Ax1,Ay1=A_info['location'][0]
        Ax2,Ay2=A_info['location'][1]
        B_info = self.Segmentline_get_info(B_seg_Chain_or_2pointxy)

        if B_info is None:
            raise ValueError(f"没有找到线段{B_seg_Chain_or_2pointxy}")
        Bx1, By1 = B_info['location'][0]
        Bx2, By2 = B_info['location'][1]


        # 特殊输入情况 防止报错
        if Bx1 == Bx2 and By1 == By2 and Ax1 == Ax2 and Ay1 == Ay2:
            # raise ValueError('输入了一个点')
            return Ax1, Ay1
        if Bx1 == Bx2 and By1 == By2:
            # raise ValueError('B线是一个点')
            temp_line_letter = self.Segmentline_to_line([A_seg_Chain_or_2pointxy[0], A_seg_Chain_or_2pointxy[1]])
            if By1 == self.line_solve(temp_line_letter, x=Bx1) and Bx1 == self.line_solve(temp_line_letter, y=By1):
                self.line_remove(temp_line_letter)
                return Bx1, By1
            else:
                self.line_remove(temp_line_letter)
                return None
        if Ax1 == Ax2 and Ay1 == Ay2:
            # raise ValueError('A线是一个点')
            temp_line_letter = self.Segmentline_to_line([B_seg_Chain_or_2pointxy[0], B_seg_Chain_or_2pointxy[1]])
            if Ay1 == self.line_solve(temp_line_letter, x=Ax1) and Ax1 == self.line_solve(temp_line_letter, y=Ay1):
                self.line_remove(temp_line_letter)
                return Ax1, Ay1
            else:
                self.line_remove(temp_line_letter)
                return None

        # 检查线段投影范围是否重叠（快速排除法）
        rangeX = max(min(Ax1, Ax2), min(Bx1, Bx2)), min(max(Ax1, Ax2), max(Bx1, Bx2))
        rangeY = max(min(Ay1, Ay2), min(By1, By2)), min(max(Ay1, Ay2), max(By1, By2))
        if rangeX[0] > rangeX[1] or rangeY[0] > rangeY[1]:
            return None  # 没有重叠，线段不可能相交

        # 计算直线的斜率和截距
        if Ax1 == Ax2:  # 第一条线和y轴水平
            k_A, b_A = None, Ax1
        else:
            k_A = (Ay1 - Ay2) / (Ax1 - Ax2)
            b_A = Ay1 - k_A * Ax1
        if Bx1 == Bx2:  # 第二条线和y轴水平
            k_B, b_B = None, Bx1
        else:
            k_B = (By1 - By2) / (Bx1 - Bx2)
            b_B = By1 - k_B * Bx1

        # 检查是否平行
        if k_A is not None and k_B is not None:  # 两条线都不是垂直线
            if abs(k_A - k_B) < 1e-10:  # 斜率相等，平行，不可能有交点
                return None
            # 计算交点
            x = (b_B - b_A) / (k_A - k_B)
            y = k_A * x + b_A
        elif k_A is None:  # 第一条线垂直
            x = Ax1
            y = k_B * Ax1 + b_B
        elif k_B is None:  # 第二条线垂直
            x = b_B
            y = k_A * x + b_A

        # 检查交点是否在两条线段的范围内
        if rangeX[0] <= x <= rangeX[1] and rangeY[0] <= y <= rangeY[1]:
            return x, y
        else:
            return None  # 交点不在线段范围内

    def intersection_line_and_Segmentline(self, segline_chain, line='a'):
        """
        经典方法 查找两条线段交点，无交点返回None
        """
        Aletter, Bletter = segline_chain.split('-')
        A = self.point_dic[Aletter]
        B = self.point_dic[Bletter]
        Ax, Ay = A
        Bx, By = B
        seg_rangeX, seg_rangeY = [min([Ax, Bx]), max([Ax, Bx])], [min([Ay, By]), max([Ay, By])]

        # 根据投影判断是否可能存在交点
        if not 'a' in self.line_dic[line]:
            if self.line_dic[line]['k'] != 0:
                line_shadow_y1 = self.line_dic[line]['k'] * seg_rangeX[0] + self.line_dic[line]['b']
                line_shadow_y2 = self.line_dic[line]['k'] * seg_rangeX[1] + self.line_dic[line]['b']
                line_shadow_Rangey = [min([line_shadow_y1, line_shadow_y2]), max([line_shadow_y1, line_shadow_y2])]
                line_shadow_x1 = (seg_rangeY[0] - self.line_dic[line]['b']) / self.line_dic[line]['k']
                line_shadow_x2 = (seg_rangeY[1] - self.line_dic[line]['b']) / self.line_dic[line]['k']
                line_shadow_Rangex = [min([line_shadow_x1, line_shadow_x2]), max([line_shadow_x1, line_shadow_x2])]
                final_range_x = [max(line_shadow_Rangex[0], seg_rangeX[0]), min(line_shadow_Rangex[1], seg_rangeX[1])]
                final_range_y = [max(line_shadow_Rangey[0], seg_rangeY[0]), min(line_shadow_Rangey[1], seg_rangeY[1])]
                if final_range_x[0] > final_range_x[1] or final_range_y[0] > final_range_y[1]:
                    # 范围无效 不存在交点
                    return None
                else:
                    if final_range_x[0] == final_range_x[1] and final_range_y[0] == final_range_y[1]:
                        # raise ValueError('范围仅为一个点')
                        print('范围仅为一个点')
                        letter_theline = self.Segmentline_to_line(segline_chain)
                        if self.line_solve(letter_theline, x=final_range_x[0]) == final_range_y[0]:
                            # 如果把点的x坐标带入直线中，得到的y值刚好是点的y坐标

                            return [final_range_x[0], final_range_y[0]]
                        else:
                            return None
                    temp_Ax, temp_Bx = final_range_x[0], final_range_x[1]
                    temp_Ay = self.line_solve(line, x=temp_Ax)
                    temp_By = self.line_solve(line, x=temp_Bx)
                    temp_A, temp_B = [temp_Ax, temp_Ay], [temp_Bx, temp_By]
                    inter_point = self.intersection_2_Segmentline([temp_A, temp_B], [A, B])
                    return inter_point
            else:
                # k=0时候，y=b 只需要比较线段的y范围是否包含b
                if seg_rangeY[0] <= self.line_dic[line]['b'] <= seg_rangeY[1]:
                    value_y = self.line_dic[line]['b']
                    the_line = self.Segmentline_to_line(segline_chain)
                    value_x = self.line_solve(the_line, y=value_y)
                    return [value_x, value_y]
                else:
                    return None
        else:
            if self.line_dic[line]['k'] != 0:
                raise ValueError("a=0 且 k=0 ：输入的是一个点而不是线")
            # a=0时候,x=b/-k 是一条垂直线 只需要比较线段的x范围是否包含b/-k
            if seg_rangeY[0] <= self.line_dic[line]['b'] / -self.line_dic[line]['k'] <= seg_rangeY[1]:
                value_x = self.line_dic[line]['b'] / -self.line_dic[line]['k']
                the_line = self.Segmentline_to_line(segline_chain)
                value_y = self.line_solve(the_line, x=value_x)
                return [value_x, value_y]
            else:
                return None

    def intersection_2line(self, Aline_letter_or_kba_dic, Bline_letter_or_kba_dic):
        """
        :param Aline_letter_or_kba_dic: 可以是代号，也可以是save_line(temp=true)的返回值：一个包含k，b，a的字典
        :param Bline_letter_or_kba_dic: 可以是代号，也可以是save_line(temp=true)的返回值：一个包含k，b，a的字典
        返回值:[x,y]
        """
        x = None
        y = None
        if isinstance(Aline_letter_or_kba_dic, str):
            detail_dicA = self.line_dic[Aline_letter_or_kba_dic]
        else:
            detail_dicA = Aline_letter_or_kba_dic
        if isinstance(Bline_letter_or_kba_dic, str):
            detail_dicB = self.line_dic[Bline_letter_or_kba_dic]
        else:
            detail_dicB = Bline_letter_or_kba_dic
        k_A = detail_dicA['k']
        b_A = detail_dicA['b']
        k_B = detail_dicB['k']
        b_B = detail_dicB['b']
        if 'a' in detail_dicA:
            x = b_A / k_A
        if 'a' in detail_dicB:
            if x is not None:
                return None
            x = b_B / k_B
        # y1=k_A*x+b_A
        # y2=k_B*x+b_B
        if k_A == k_B:
            return None
        if x is None:
            x = (b_B - b_A) / (k_A - k_B)
        y = k_A * x + b_A
        return [x, y]

    def Segmentline_shadow_on_axis(self, Chain_or_2pointxy):
        """
        求一条线段分别在x轴和y轴的投影
        :param Chain_or_2pointxy: 既可以是A-B形式 也可以是[x,y][x,y]
        :return: 返回一个列表，包含两个范围[[x_min, x_max], [y_min, y_max]]
        """
        Seg_info=self.Segmentline_get_info(Chain_or_2pointxy)
        if Seg_info is None:
            raise ValueError(f"查找{Chain_or_2pointxy}失败")
        x1,y1=Seg_info['location'][0]
        x2,y2=Seg_info['location'][1]
        x_range = [min(x1, x2), max(x1, x2)]
        y_range = [min(y1, y2), max(y1, y2)]
        return [x_range, y_range]

    def Segmentline_to_line(self, chain_or_2pointxy, back_range=False, temp=False):
        """
        :param chain_or_2pointxy: 既可以是一个ChainA-B也可以是列表[[Ax,Ay], [Bx,By]]
        :return: 返回一个代号, 例如：a
        详细信息储存在字典line_dic[a]中
        如果back_range 额外返回一个列表[[xmin,xmax],[ymin,ymax]]

        """
        if isinstance(chain_or_2pointxy, str):
            Aletter, Bletter = chain_or_2pointxy.split('-')
            x1, x2 = self.point_dic[Aletter][0], self.point_dic[Bletter][0]
            y1, y2 = self.point_dic[Aletter][1], self.point_dic[Bletter][1]
        else:
            x1, y1 = chain_or_2pointxy[0]
            x2, y2 = chain_or_2pointxy[1]

        if x1 == x2 and y1 == y2:
            raise ValueError('is not a line,this is a point')
        if x1 == x2:
            a = 0
            b = x1
            k = -1
        else:
            a = 1
        if y1 == y2:
            k = 0
            b = y1
        if x1 != x2 and y1 != y2:
            k = (y1 - y2) / (x1 - x2)
            b = y1 - k * x1
        back = self.line_drop(k, b, a, temp)
        if back_range is True:
            range = self.Segmentline_shadow_on_axis(chain_or_2pointxy)
            back = back, range

        return back

    def line_chain_or_dic(self,line_chain_or_dic):
        """
        此方法无论输入的是dict还是'代号'
        统一会返回dict
        如果失败(输入的格式错误) 返回False
        """
        if isinstance(line_chain_or_dic, str):
            detail_line_dic = self.line_dic[line_chain_or_dic]
        elif isinstance(line_chain_or_dic, dict):
            detail_line_dic = line_chain_or_dic
        else:
            return False
        return detail_line_dic

    def distance_point_to_line(self,point,line):
        #linedic例子:{'a': {'str': 'y=3x+100', 'k': 3, 'b': 100}}
        point_x = point[0]
        point_y = point[1]
        if isinstance(line,dict): detail_line_dic = line
        elif isinstance(line,str): detail_line_dic = self.line_dic[line]
        else: raise ValueError(f"输入的line不合符规范，为：{line}")

        if detail_line_dic['k']==0:
            #输入的line是一条水平线
            return abs(detail_line_dic['b']-point_y)
        if 'a' in detail_line_dic:
            #输入的是一条垂直线
            #存在a键的时候 a必定为0 且k必定为-1(line_drop中就是这么规定的)
            return abs(detail_line_dic['b'] - point_x)
        k_orth = -1 / detail_line_dic['k']
        # 斜率是-1/k的时候垂直
        result=self.line_solve_general(a=1, k=k_orth, x=point_x, y=point_y)
        b=result['b']
        line_orth_dic = self.line_drop(temp=True,k=k_orth,b=b,a=1)
        point = [point_x, point_y]
        point_inter = self.intersection_2line(line_orth_dic, detail_line_dic)
        return self.distance_2_points(point,point_inter)

    def directed_line_drop(self, location_point=None, direction_vector=None, line_chain_or_dic=None):
        """
        保存有向直线, 也可以将直线转换为有向直线
        location_point:起点
        direction_vector:方向向量
        此处使用的line_dic的字典中是ay=kx+b (a取值仅为0或1,当a=0时,字典中不存在a的键)
        """
        if location_point and len(location_point) != 2:
            raise ValueError("location_point必须是包含两个元素的列表或元组")
        if direction_vector and len(direction_vector) != 2:
            raise ValueError("direction_vector必须是包含两个元素的列表或元组")
        the_location_point=None
        the_direction_vector=None
        line_dict=None
        if line_chain_or_dic:
            line_dict=self.line_chain_or_dic(line_chain_or_dic)
            if not line_dict:
                raise ValueError(f"提供的Line错误{line_chain_or_dic}")
            if 'a' in line_dict:#垂直情况 a取值仅为0或1,如果为1就不存在键a
                the_direction_vector=[0, 1]
                the_location_point = [line_dict['b']/(-line_dict['k']),0]
            else:
                the_direction_vector=[1, line_dict['k']] #常规情况

        if location_point:
            lo_x,lo_y=location_point
            if line_dict :#提供了起点,判断原点是否符合标准
                if self.line_solve(line_dict,lo_x)!=lo_y:
                    raise ValueError(f"提供的起点:{location_point}不在直线{line_dict}上")
            the_location_point = location_point
        if direction_vector:
            dr_x,dr_y=direction_vector
            if line_dict:
                if line_dict['k']!=0 and (dr_y==0 or not math.isclose(dr_x/dr_y,line_dict['k'])):
                    raise ValueError(f"提供的方向{direction_vector}和直线{line_dict}的斜率不匹配")
                if line_dict['k']==0 and dr_y!=0:
                    raise ValueError(f"提供的方向{direction_vector}和水平直线{line_dict}不匹配")
            the_direction_vector = direction_vector
        if the_direction_vector and direction_vector:
            detail_dic = {'directed': True, 'location_point': the_location_point,
                          'direction_vector': the_direction_vector}
            new_letter = self.extract_letter()
            self.line_dic[new_letter] = detail_dic
            return new_letter
        raise ValueError(f'缺少必要参数: location_point={location_point}, '
                         f'direction_vector={direction_vector},'
                         f' line_chain_or_dic={line_chain_or_dic}')




    # ////////////《面操作》////////////
    def surface_drop_by_chain(self, chain_of_point, floor=0, color=py5.color(200, 200, 20, 255), fill=False, stroke=None,
                              stroke_color=py5.color(0, 0, 0)):
        """
        【center】会自动生成在参数字典中：重心:是所有顶点坐标的平均值
        这里输入的链是不一定需要收尾相接的,如果不相接会自动补全
        """
        surf_pointgroup = []
        alist_of_point = chain_of_point.split('-')
        for aletter in alist_of_point:
            point_xy = self.point_dic.get(aletter, 0)
            if point_xy != 0:
                surf_pointgroup.append(point_xy)
            else:
                return "false:cant find point by letter"
        self.surface_chain_to_Segline_group(chain_of_point,visible=False) #确保线段都创建了
        nowdic = {}
        nowdic['floor'] = floor
        all_x, all_y = 0, 0
        for x, y in surf_pointgroup:
            all_x, all_y = all_x + x, all_y + y
        center = [all_x / len(surf_pointgroup), all_y / len(surf_pointgroup)]
        nowdic['center'] = center
        nowdic['local'] = surf_pointgroup
        nowdic['color'] = color
        nowdic['fill'] = fill
        nowdic['stroke'] = stroke
        nowdic['stroke_color'] = stroke_color
        self.surface_dic[chain_of_point] = nowdic
        return surf_pointgroup

    def surface_drop_by_pointlist(self, apointlist, floor=0, color=py5.color(200, 200, 20, 255), fill=False, stroke=None,
                                  stroke_color=py5.color(0, 0, 0)):
        """
        这里输入的链是不需要收尾相接的,如果不相接会自动补全
        """
        theletter = self.point_drop_group(apointlist)
        chain = "-".join(theletter)
        self.surface_drop_by_chain(chain, floor, color, fill, stroke, stroke_color)

    def surface_chain_to_Segline_group(self, chain, floor=0, color=py5.color(0, 0, 0, 255), stroke_weight=3,
                                       visible=True):
        """
        给定一个字符串A-B-C,返回[A-B][B-C][C-A](返回的是首尾相接的,输入的不一定需要收尾相接)
        如果seglinedic中不存在这个线段 那么就会自动创建
        :param chain: 文本型，一个字符串 例：A-B-C
        :return: [A-B][B-C][C-A]
        """
        nodes = chain.split("-")  # 将链式结构分解为节点列表["A", "B", "C"]
        # 生成相邻对
        pairs = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
        if nodes[0] != nodes[-1]:
            # 如果第一个点和最后一个点不一致,加入首尾连接
            pairs.append((nodes[-1], nodes[0]))  # 结果: [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]
        formatted_pairs = [f"{a}-{b}" for a, b in pairs]
        for i in formatted_pairs:
            # 检查是否已经创建了线段 如果不存在就创建线段
            if i in self.Segmentline_dic in self.Segmentline_dic:
                continue
            else:
                q = i.split('-')
                self.Segmentline_drop(q[0], q[1], floor=floor, color=color, stroke_weight=stroke_weight, visible=visible)
        return formatted_pairs

    def is_point_in_surface(self,polx,P):
        """
           polx接受列表型 也接受非齐次坐标矩阵
           判断点 P 是否在 polx 中（包括在边上）
           polx: 多边形的顶点矩阵 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
           P: 点的坐标 [x, y]
           return: 'inside' 如果点在内部, 'on_edge' 如果点在边上, 'outside' 如果点在外部
        """

        # 应当检查符号chain，给定的四边形是否已经闭合，若已经闭合 不可以用下文的
        # polx[(i + 1) % len(polx)]
        # 而应该改用
        # polx[i+1]
        def cross_product(A, B, P):
            # 计算叉积
            A = np.array(A)
            B = np.array(B)
            P = np.array(P)
            AB = B - A
            AP = P - A
            return np.cross(AB, AP)

        def is_point_on_segment(A, B, P):
            """
            判断点 P 是否在线段 AB 上
            :param A: 线段起点 [x1, y1]
            :param B: 线段终点 [x2, y2]
            :param P: 待检测点 [x, y]
            :return: True 如果 P 在线段 AB 上, 否则 False
            """
            # 叉积为 0 且点在线段范围内
            A = np.array(A)
            B = np.array(B)
            P = np.array(P)
            cross = cross_product(A, B, P)
            # 判断叉积是否为 0
            if abs(cross) > 1e-10:  # 允许微小误差
                return False
            # 判断是否在范围内
            dot_product = np.dot(P - A, B - A)  # 投影点是否在 A->B 的方向上
            squared_length = np.dot(B - A, B - A)  # AB 的平方长度
            return 0 <= dot_product <= squared_length

        # 检查每条边
        on_edge = False
        signs = []
        for i in range(len(polx)):
            A = polx[i]
            B = polx[(i + 1) % len(polx)]  # 四边形是闭合的
            if is_point_on_segment(A, B, P):  # 点在边上
                on_edge = True
            signs.append(cross_product(A, B, P))

        # 检查所有符号是否一致
        if all(s > 0 for s in signs) or all(s < 0 for s in signs):
            return 'inside' if not on_edge else 'on_edge'
        return 'on_edge' if on_edge else 'outside'

    def regular_polygon(self,sides, side_length):
        """。
        参数：
        - sides: 正多边形的边数。
        - side_length: 正多边形的边长。
        返回:
        多边形点的列表(顺时针方向)
        """

        def split_2pi(times):
            """
            将 2π 弧度 分成 times 等份。
            返回每份的弧度值。
            """
            return 2 * math.pi / times  # 360 度 = 2π 弧度

        if sides < 3:
            raise ValueError("边数必须大于或等于 3")
        if side_length <= 0:
            raise ValueError("边长必须大于 0")

        # 计算中心角的一半（theta / 2）
        theta = split_2pi(sides)  # 中心角的弧度值
        half_theta = theta / 2
        # 计算半径
        radius = (side_length / 2) / math.sin(half_theta)
        point_start = [0, radius]  # 第一个点是从原点出发沿着y轴正方向前进的
        back_list = [point_start]
        for i in range(1, sides):
            point = self.vector_rotate(point_start, math.degrees(theta) * i)
            back_list.append(point)
        return back_list



    # ////////////《常用操作》////////////
    def list_depth(self,lst):
        if not isinstance(lst, (list,tuple)):
            # 如果当前不是列表，层数为 0
            return 0
        if not lst:
            # 如果列表是空的，层数为 1（只有一层）
            return 1
        # 递归判断每个元素的嵌套深度，并取最大值
        return 1 + max(self.list_depth(item) for item in lst)
    def get_inter_range(self, a=None, b=None):
        """
        查找a和b的交集
        a和b的格式为[x,y]的范围
        无交集返回None
        """
        def get_range(interval):
            # 提取范围的辅助函数
            return min(interval[0], interval[1]), max(interval[0], interval[1])

        if a is not None and b is not None:
            if len(a) == 2 and len(b) == 2:
                amin, amax = get_range(a)
                bmin, bmax = get_range(b)
                new_max = min(amax, bmax)
                new_min = max(amin, bmin)
                # 检查是否有交集
                if new_min <= new_max:
                    return [new_min, new_max]
                else:
                    return None  # 无交集
            else:
                raise ValueError(f"输入{a}或{b}不是[x,y]形式")
        elif a is not None:
            if len(a) == 2:
                return list(get_range(a))
            else:
                raise ValueError(f"输入{a}不是[x,y]形式")
        elif b is not None:
            if len(b) == 2:
                return list(get_range(b))
            else:
                raise ValueError(f"输入{b}不是[x,y]形式")
        else:
            return None  # a 和 b 都为 None
    def clear_letter_mem_capital(self, used):
        """
        清理内存用
        输入已经使用的点的字母代号
        返回一个字典 每个代号对应一个新的名字
        """
        back_dic = {}
        if len(self.letter_queue) < len(used) * 2:
            return None
        for i in used:
            self.back_letter_capital(i)
        new_letter_index = []
        for i in used:
            new_letter = self.extract_letter_capital()
            new_letter_index.append(self.separate_letter(new_letter)[1])
            back_dic[i] = new_letter
        the_max_index = max(new_letter_index)  # 例如最大的是Z100 那么返回100
        for l, the_letter in enumerate(self.letter_queue_capital):
            the_ascii, the_index = self.separate_letter(the_letter)
            if the_index > the_max_index and the_ascii == ord('A'):
                # 如果是A开头的 例如当前遍历A100 我们的max是99 那么就通过
                # 当前遍历B99 我们的max是99 那么因为不是A开头的就会跳过 并且99<100
                del self.letter_queue_capital[l:]
                self.letter_index_capital = the_index - 1
                break
        return back_dic
    def extract_letter_capital(self):
        if not self.letter_queue_capital:
            # 如果字母队列中不够用了
            self.letter_queue_capital.extend([l + str(self.letter_index_capital + 1) for l in self.alphabetize_Capital])
            self.letter_index_capital += 1
        return self.letter_queue_capital.pop(0)  # 删除队列中的第一项并返回
    def back_letter_capital(self, letter):
        the_letter_ascii, the_letter_index = self.separate_letter(letter)
        for list_i, i in enumerate(self.letter_queue_capital):
            i_ascii, i_index = self.separate_letter(i)
            if i_index < the_letter_index:
                # 输入A100 当前查找到A51 列表为[A50,A51,...,A99]
                continue  # 此时应该跳过,寻找下一个
            if i_index == the_letter_index:
                # 输入F10 当前查找到A10 列表为[A10,B10,C10,D10]
                if i_ascii < the_letter_ascii:
                    continue
                if i_ascii > the_letter_ascii:  # 输入F10 当前查找为G10 那么应该插入在G前面
                    self.letter_queue_capital.insert(list_i, letter)  # 当前索引为i_index 插入会把当前项往后推移
                    return
            if i_index > the_letter_index:  # 当前输入A10 列表为[A12,A13,A14...]
                self.letter_queue_capital.insert(list_i, letter)  # 此时插入在当前项(之前)就可以
                return
        # 如果能到达此处 输入A100 当前查找到A51 列表为[A50,A51,...,A99]应该加入到末尾
        self.letter_queue_capital.append(letter)
    def apply_letter_capital(self, letter):
        """
        申请一个指定字母,并从字母表中删除它,成功返回True
        """
        the_ascii, the_index = self.separate_letter(letter)
        if the_index > self.letter_index_capital:
            # 队列不足开始创建
            for i in range(the_index - self.letter_index_capital):
                # 例如输入 A5 当前序号为3:[B3,C3....Z3]在添加两个循环(5-3) 得到[B3...Z5]
                self.letter_queue_capital.extend(
                    [l + str(self.letter_index_capital + 1) for l in self.alphabetize_Capital])
                self.letter_index_capital += 1
        if letter in self.letter_queue_capital:
            self.letter_queue_capital.remove(letter)
            return True
        raise ValueError(f"发生错误,队列为{self.letter_queue_capital},输入值为{letter}")

    def clear_letter_mem(self, used):
        back_dic = {}
        if len(self.letter_queue) < len(used) * 2:
            return None
        for i in used:
            self.back_letter(i)
        new_letter_index = []
        for i in used:
            new_letter = self.extract_letter()
            new_letter_index.append(self.separate_letter(new_letter)[1])
            back_dic[i] = new_letter
        the_max_index = max(new_letter_index)  # 例如最大的是Z100 那么返回100
        for l, the_letter in enumerate(self.letter_queue):
            the_ascii, the_index = self.separate_letter(the_letter)
            if the_index > the_max_index and the_ascii == ord('a'):
                # 如果是A开头的 例如当前遍历A100 我们的max是99 那么就通过
                # 当前遍历B99 我们的max是99 那么因为不是A开头的就会跳过 并且99<100
                del self.letter_queue[l:]
                self.letter_index = the_index - 1
                break
        return back_dic
    def extract_letter(self):
        """
        返回提取的字母
        同时从字母表中删除
        """
        if not self.letter_queue:
            # 如果字母队列中不够用了
            self.letter_queue.extend([l + str(self.letter_index + 1) for l in self.alphabetize])
            self.letter_index += 1
        return self.letter_queue.pop(0)  # 删除队列中的第一项并返回
    def back_letter(self, letter):
        the_letter_ascii, the_letter_index = self.separate_letter(letter)
        for list_i, i in enumerate(self.letter_queue):
            i_ascii, i_index = self.separate_letter(i)
            if i_index < the_letter_index:
                # 输入A100 当前查找到A51 列表为[A50,A51,...,A99]
                continue  # 此时应该跳过,寻找下一个
            if i_index == the_letter_index:
                # 输入F10 当前查找到A10 列表为[A10,B10,C10,D10]
                if i_ascii < the_letter_ascii:
                    continue
                if i_ascii > the_letter_ascii:  # 输入F10 当前查找为G10 那么应该插入在G前面
                    self.letter_queue.insert(list_i, letter)  # 当前索引为i_index 插入会把当前项往后推移
                    return
            if i_index > the_letter_index:  # 当前输入A10 列表为[A12,A13,A14...]
                self.letter_queue.insert(list_i, letter)  # 此时插入在当前项(之前)就可以
                return
        # 如果能到达此处 输入A100 当前查找到A51 列表为[A50,A51,...,A99]应该加入到末尾
        self.letter_queue.append(letter)

    def separate_letter(self, letter):
        """
        将输入拆分为两部分:
        第一个字符的ASCII值,数字的int值
        """
        the_letter_index = letter[1:]  # 从'a100'中切片得到index'100' 如果'a' 返回的是''
        the_letter_ascii = ord(letter[0])
        if the_letter_index != '':
            the_letter_index = int(the_letter_index)
        else:
            the_letter_index = 0
        return the_letter_ascii, the_letter_index

    # =========================================

def screen_draw_surface(surfacedic,floor):
    surface_drawed={}
    allsurfacelist=surfacedic.keys()
    for sf in allsurfacelist:
        thedic = surfacedic[sf]
        if thedic['floor']!=floor:
            continue
        #=============读取位置信息（列表）===============
        weizhi = thedic['local']
        if not isinstance(weizhi, np.ndarray): #如果不是NP数组(矩阵)
            weizhi = np.array(weizhi,dtype=float)
        vertices = weizhi
        # ===========================================
        surface_drawed.append(sf)
        surface_drawed[-1] = py5.create_shape()

        surface_drawed[-1].begin_shape()
        surface_drawed[-1].fill(thedic['color'])
        if thedic['stroke'] == None:
            surface_drawed[-1].no_stroke()
        else:
            surface_drawed[-1].stroke(thedic['stroke_color'])
        if thedic['fill'] == False:
            surface_drawed[-1].no_fill()
        surface_drawed[-1].fill(thedic['color'])
        surface_drawed[-1].vertices(vertices)
        surface_drawed[-1].end_shape()
        py5.shape(surface_drawed[-1])

def screen_draw_SegmentLine(SegmentLine_dic, floor):
    """
    遍历segment_line_dict绘制线段
    """
    for key, val in SegmentLine_dic.items():
        if val['floor']!=floor:
            continue
        if val['visible']==False:
            continue
        color=val['color']
        py5.stroke(color)
        strokeweigh=val['stroke_weight']
        py5.stroke_weight(strokeweigh)
        local_group=[]
        for each_point in val['location']:
            for i in each_point:
                local_group.append(i)
        py5.line(*local_group)

def screen_draw_vector(vector_or_vector_list,start_point):
    tem = Tools2D()
    def arrow(vector):
        """
        返回两条线段,是从vector末端画的两条斜线,长度10,夹角30度
        返回格式[[x,y],[x,y]]
        """
        arrow_vector_A = tem.vector_rotate(vector,180-30)
        arrow_vector_B = tem.vector_rotate(vector,-(180-30))
        arrow_vector_A = tem.vector_change_norm(arrow_vector_A, norm=10)
        arrow_vector_B = tem.vector_change_norm(arrow_vector_B, norm=10)
        arrow_end_A = tem.point_shift(arrow_vector_A,vector=vector)
        arrow_end_B = tem.point_shift(arrow_vector_B, vector=vector)
        return arrow_end_A,arrow_end_B

    segline_group = []
    if tem.list_depth(vector_or_vector_list)==2:
        for each_vector in vector_or_vector_list:
            if each_vector[0]==0 and each_vector[1]==0:
                continue
            for i in arrow(each_vector):
                segline_group.append([tem.point_shift(each_vector,start_point),tem.point_shift(i,start_point)])
            segline_group.append([start_point,tem.point_shift(each_vector,start_point)])
    elif tem.list_depth(vector_or_vector_list)==1:
        for i in arrow(vector_or_vector_list):
            segline_group.append([tem.point_shift(vector_or_vector_list, start_point), tem.point_shift(i, start_point)])
        segline_group.append([start_point, tem.point_shift(vector_or_vector_list, start_point)])

    for i in segline_group:
        tem.Segmentline_drop(i[0], i[1])
    screen_draw_SegmentLine(tem.get_Segmentline_dic(),floor=0)

def draw_directed_line(line_detail_dict, color=py5.color(10, 10, 0, 255), stroke_weight=3,floor=0):
    #把direction_vector获取出来,通过set_norm来改变长度(细分程度),然后平移direction_vector,收尾相接,得到一条渐变线
    #1部分画虚线 ;2部分画实线 . . . .
    #从直线末端倒着画?如何取到直线末端?
    input_value={'color':color,'stroke_weight':stroke_weight,'floor':floor}
    screen_info = screen_get_info()
    x_range, y_range = screen_info['x_range'], screen_info['y_range']
    tem = Tools2D()
    if 'directed' not in line_detail_dict or line_detail_dict['directed'] is False:
        raise ValueError(f"输入的有向直线有误{line_detail_dict}")
    lx,ly=line_detail_dict['location_point']
    vx,vy=line_detail_dict['direction_vector']

    line_detail = tem.directed_line_to_line(line_detail_dict, temp=True)
    segment_line = tem.line_to_Segmentline(line_detail,x_range=x_range,y_range=y_range)
    segment_line_locations=tem.Segmentline_get_info(segment_line)['location']
    tem.Segmentline_remove_by_chain(segment_line)

    A_point,B_point = segment_line_locations
    Ax,Ay=A_point #直线和边界的交点A
    Bx,by=B_point #交点B

    # 优化方向判断：计算端点向量与方向向量的点积
    vec_to_A = np.array([Ax - lx, Ay - ly]) #把交点A移回原点
    direction_vec = np.array([vx, vy])
    dot_product_A = np.dot(vec_to_A, direction_vec) #通过点积判断方向

    # 根据点积符号判断正向端点
    if dot_product_A > 0:
        positive_point, negative_point = A_point, B_point
    else:
        positive_point, negative_point = B_point, A_point

    #正方向线段处理
    positive_segment_line = tem.Segmentline_drop(positive_point, line_detail_dict['location_point'], **input_value)
    positive_segment_line_dict = tem.Segmentline_get_info(positive_segment_line)
    screen_draw_SegmentLine({0:positive_segment_line_dict},positive_segment_line_dict['floor'])

    #负方向线段处理
    negative_segment_line = tem.Segmentline_drop(negative_point, line_detail_dict['location_point'], **input_value)
    negative_segment_line_get_info = tem.Segmentline_get_info(negative_segment_line)
    dotted_negative_segment_line_dicts = _dotted_segment_line(5,negative_segment_line_get_info,**input_value)
    screen_draw(Seglinedic=dotted_negative_segment_line_dicts)






# def _draw_color_fade_segment_line(sampling_rate,speed,minimum)

def _dotted_segment_line(spacing, seg_line_get_info, color, stroke_weight, floor=0):
    """
    绘制均匀分布的虚线段（至少需要3段才能形成虚线）
    :param spacing: 每段虚线的目标间距
    :param seg_line_get_info: 输入线段信息
    """
    # 工具类实例化
    tem = Tools2D()

    # 获取线段信息
    # seg_line = tem.Segmentline_get_info(seg_line)
    # if not seg_line:
    #     raise ValueError(f"没有找到线段: {seg_line}")

    # 提取端点
    point_A, point_B = seg_line_get_info['location']
    x1, y1 = point_A
    x2, y2 = point_B

    # 转换为直线信息
    print('seg_line_get_info',seg_line_get_info)
    line = tem.Segmentline_to_line([point_A, point_B], temp=True)
    a = line.get('a', 1)  # 获取直线参数a
    k = line.get('k', 0)  # 获取斜率k，默认值为0（水平线）

    # 计算线段总长度
    total_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # 特殊处理垂直线的dx和dy
    if a == 0:  # 垂直线情况
        dx = 0
        dy = spacing * (1 if y2 > y1 else -1)  # 根据方向调整符号
    else:  # 非垂直线情况
        dx = spacing / math.sqrt(1 + k ** 2)  # 水平方向增量
        dy = k * dx  # 垂直方向增量
        # 根据线段方向调整dx的符号
        if x2 < x1:
            dx = -dx
            dy = -dy

    # 计算虚线段数和余数
    num_segments = int(total_length // spacing)  # 整数段数
    remainder = total_length % spacing  # 剩余长度（余数）

    # 如果虚线段数不足3段，直接绘制整条线段
    if num_segments < 3:
        tem.Segmentline_drop([x1, y1], [x2, y2], floor=floor, color=color, stroke_weight=stroke_weight)
        return tem.get_Segmentline_dic()

    # 如果余数存在，将其均摊到每段线段中
    adjusted_spacing = spacing + (remainder / num_segments)

    # 根据调整后的间距重新计算dx和dy
    if a == 0:  # 垂直线情况
        dx = 0
        dy = adjusted_spacing * (1 if y2 > y1 else -1)
    else:
        dx = adjusted_spacing / math.sqrt(1 + k ** 2)
        dy = k * dx
        if x2 < x1:
            dx = -dx
            dy = -dy

    # 循环绘制虚线段
    for i in range(num_segments):
        if i % 2 == 0:  # 偶数段绘制虚线（1:1比例，间隔为adjusted_spacing）
            start_x = x1 + i * dx
            start_y = y1 + i * dy
            end_x = start_x + dx
            end_y = start_y + dy
            tem.Segmentline_drop([start_x, start_y], [end_x, end_y], floor=floor, color=color,
                                 stroke_weight=stroke_weight)

    return tem.get_Segmentline_dic()


def screen_draw_lines(linedic,color=py5.color(10,10,0,255),stroke_weight=3):
    screen_info=screen_get_info()
    x_range,y_range=screen_info['x_range'],screen_info['y_range']
    tem=Tools2D()

    for key,de_dic in linedic.items():
        #TODO 这里计算量很大，导致单进程效率很低，需要进行多进程处理
        tem.line_to_Segmentline(de_dic,x_range=x_range,y_range=y_range)
    py5.stroke(color)
    py5.stroke_weight(stroke_weight)

    line_to_draw=[]

    for key, value in tem.Segmentline_dic.items():
        #整理输入参数格式,py5.line需要的格式[[x1 y1 x2 y2] [...]]
        a_point,b_point=tem.Segmentline_get_info(key)['location']
        the_line=a_point+b_point
        line_to_draw.append(the_line)
    py5.lines(np.array(line_to_draw, dtype=np.float32))

def screen_draw_points( pointdic,size=5,color=py5.color(255,0,0,255),fill=py5.color(0,0,0,255) ):
    """
    fill可以输入None 得到空心点
    """
    for key,value in pointdic.items():
        x,y=value
        py5.stroke_weight(2)
        py5.stroke(color)
        if fill is None: py5.no_fill()
        else:py5.fill(fill)
        py5.circle(x , y , size)

def screen_draw(f=3, Seglinedic=None, surfdic=None):
    """
    f是绘制的图层数
    """
    if surfdic is None and Seglinedic is None:
        raise ValueError ('没有输入surfdic或者seglinedic,无法绘制')
    for i in range(f):
        if surfdic is not None:
            screen_draw_surface(surfdic, i)
        if Seglinedic is not None:
            screen_draw_SegmentLine(Seglinedic, i)

def screen_print_fps():
    py5.fill(0)  # 设置文本颜色为黑色
    py5.text_size(16)  # 设置文本大小
    frame=py5.get_frame_rate()
    py5.text(f"FPS: {frame}", 10, 30)

def screen_get_info():
    """
    返回一个关于屏幕详细信息的字典
    包含:
    x_range,y_range
    rect:屏幕矩形(首尾相接)
    center:屏幕中心
    """
    in_dic={}
    right_top=[py5.width,0]
    right_down=[py5.width,py5.height]
    left_top=[0,0]
    left_down=[0,py5.height]
    x_range = [0, py5.width]
    y_range = [0, py5.height]
    in_dic['x_range']=x_range
    in_dic['y_range'] = y_range
    in_dic['rect'] = [left_top,right_top,right_down,left_down,left_top]
    in_dic['center']=[py5.width/2,py5.height/2]
    return in_dic

def screen_axis(x=0,y=0):
    """
    从屏幕中心建立坐标系,输入x,y 返回py5的正确坐标
    """
    x=py5.width/2+x
    y=py5.height/2-y
    return [x,y]

def random_point(creat_num=1500, del_num=1000, num=10):
    """
    随机创建一些点,返回point_dic
    creat_num:随机创建点数量
    del_num:随机删除点数量
    num:循环以上过程次数
    """
    p=Tools2D()
    the_screen=screen_get_info()
    for n in range(num):
        for i in range(creat_num):
            p.point_drop([random.randint(*screen_get_info()['x_range']), random.randint(*screen_get_info()['y_range'])])
        for i in range(del_num):
            p_letter = list(p.point_dic.keys())
            p.point_remove_by_letter(random.choice(p_letter))
    return p.point_dic

def random_segline(number=100):
    """
    随机生成number条线段
    返回线段字典Segmentline_dic
    """
    lines = Tools2D()
    for i in range(number):
        A = [random.randint(0, 400), random.randint(0, 300)]
        B = [random.randint(0, 400), random.randint(0, 300)]
        color = py5.color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # print(A,"/n",B)
        lines.Segmentline_drop(Apoint=A, Bpoint=B, color=color)
    # print(lines.get_Segmentline_dic())
    return lines.get_Segmentline_dic()

def line_in_extreme(num=500):
    lines = Tools2D()
    for i in range(num):
        a = random.randint(-3, 3)
        k = random.randint(-3, 3)
        if a==0 and k==0:
            continue
        lines.line_drop(k=k, b=random.randint(-100, 100), a=a)
    return lines.get_line_dic()

