import sys
import sympy as sym
import py5
import numpy as np
import time

start_time = time.time()
#我需要一个python函数 给定一个A列表（这是一个多边形的各个内角度数），给定一个列表B（是一组点坐标，这些点刚好是多边形的顶点，只是一部分），返回他的所有可能解（解是完整的这个形状的点坐标列表）
def getdegree_Polygon (Side):
    AddShapeDegree = np.pi * (Side-2)
    Degree=AddShapeDegree/Side
    Angle=np.degrees(Degree)
    print (Side,"角形 的每个角度是：", round(Angle,10))
    print("弧度:",Degree)
    return (Degree)
#↑给定一个【边数】可以求解这个正多边形的内角Cos弧度

def convert_points_to_lines(pointtuple):
    # 将点的列表转换为线段的列表
    lines = []
    for i in range(len(pointtuple) - 1):  # 遍历相邻点
        x1, y1 = pointtuple[i]
        x2, y2 = pointtuple[i + 1]
        lines.append([x1, y1, x2, y2])
    return lines
#py5.lines需要特殊输入格式x,y,x,y
#此函数是为了转换格式

def draw_tup_shape (pointtuple):
  if pointtuple[0] != pointtuple[len(pointtuple)-1]:
    print ("输入的点集收尾不相接","自动补充","[",len(pointtuple)+1,"]=",pointtuple[0])
    pointtuple.append(pointtuple[0])
    print(pointtuple)
  ou=range(0, len(pointtuple)-1, 2)
  ji=range(1, len(pointtuple)-1, 2)
  ji=ji[::-1]
  linb=list(ou)+list(ji)
  linb.append(len(pointtuple)-1)
  linb.append(len(pointtuple)-1)
  print(linb)
  newlist=[]

  for i in range(len(pointtuple)):
      newlist.append(pointtuple[linb[i]])
  print(newlist)
  py5.lines(convert_points_to_lines(newlist))
  for i in range(len(pointtuple)):
      py5.fill(255, 0, 0)
      py5.text_size(44)
      py5.text(i, pointtuple[i][0], pointtuple[i][1])
#给定一个点集可以自动画出
#规整数据格式应该放在下面的get_everypoint

def get_nextpot(A,B,cosR):
        VeA = sym.Matrix([[A[0]], [A[1]]])  # 列向量
        VeB = sym.Matrix([[B[0]], [B[1]]])  # 列向量
        VeC = sym.Matrix([sym.symbols('x', real=True), sym.symbols('y', real=True)])  # 列向量 (x, y)
        R = (VeA - VeB).norm()
        print("R:",R.evalf())
        eq1 = sym.Eq((VeA - VeC).norm(), (VeA - VeB).norm())  # AB=AC=R
        eq2 = sym.Eq((VeA - VeC).dot(VeA - VeB), R * R * cosR)  # 向量点积公式：（A - C）dot(A - B) =∣AC∣*∣AB∣⋅cos(Angel)
        C = sym.solve([eq1, eq2], VeC)
        return (C)
#给定点A和B，AB,AC之间夹角cosR 求解C
#【准备拓展】：给定点A和B，存在一些可能的夹角（一组列表），求所有可能解
# for cosR in cosR_list:
#如果A,B不是四（多）边形临边而是对边的情况下↑↑↑↑无法求解


def get_everypoint(A,B,ang):
    jieguo = []
    jieguo.append(B)

    def cal_times(ang):
        times=(ang-1+2-1)//2
        return (times)
    times=cal_times(ang)
    print(ang,"角(边)形需要计算次数：",times)
    eachradio=2*np.pi/ang
    for i in range(1,cal_times(ang)+1):
        inputcosR=np.cos(eachradio*i)
        back=get_nextpot(A,B,inputcosR)
        jieguo.append(back[0])
        if len(back)!=1:
            jieguo.append(back[1])
        print("循环：",i,"计算结果：",back)
    return (jieguo)
#↑通过给定【Center】：A，【AskPoint】：B，ang:【边数】
#返回一个列表型，这个ang边形的点集

def creat_anybianxing(center=None,radio=None,ask_point=None,any=3):
    if not center and not ask_point and not radio:
        print("空参数无法计算")
        return ("err")
    if not center and not ask_point and radio:
        print("缺少center坐标，存在r，输出以原点为center的")
    if center and ask_point and not radio:
        if (len(ask_point)>1):
            print("存在多个point,需要验证是否满足条件")
            return ("err")
        else:
            print(ask_point)
            dianji=get_everypoint(center[0],ask_point[0],any)
            print("dianji=",dianji)
            draw_tup_shape(dianji)
    if not center and ask_point and radio:
        print("存在point和radio，可以计算Center位置，若point数量≤2，会存在多个可能的Center")
#根据输入量创建多边形【center】中心点，radio半径（中心点到角的举例），【any】几边形

def setup():
    py5.size(800, 600)  # 设置窗口尺寸为 800x600 像素
    py5.background(240)  # 设置背景颜色为浅灰色

def draw():
    py5.fill(50, 100, 200)  # 设置文字颜色
    py5.translate(800/2,600/2)
    py5.stroke(0)  # 设置线条颜色为黑色
    py5.stroke_weight(2)  # 设置线条宽度为 2 像素
    creat_anybianxing(((10, 15),), None, ((100, 200),),6)
    py5.point(10,15)
    py5.text("reg",10,15)

    # 停止 draw 循环
    py5.no_loop()

# 启动 py5 草图
py5.run_sketch()


'''
def 创建一组倾斜直线（度数，间隔，次数）
循环（次数）：
  y=tan(？度数)（x+b间隔*次数）
  把以上加入元组A
返回（元组A）

def 求交点（A,B）
  #A=k1x+g1b
  #B=k2x+g2b
  求X（k1x+g1b=k2x+g2b）
  以上加入元组X
  带入求Y（）
  以上加入元组Y
  循环(a，求上述元组项数)
    元组综合=append（元组X[a],元组Y[a]）
  返回（元组综合）

循环（N，5次）
  循环（K，平铺次数）
    创建一组倾斜直线(360/5*N，间隔*K)
    ALL=以上加入dic型

求交点（ALL）
求夹角（ALL）
加入元组（焦点，夹角）
取出夹角数列表即可
根据夹角列表的顺序 创建PENROSE形状网络
'''




