#!/usr/bin/python
# -*- coding:utf8 -*-
import rospy
from std_msgs.msg import Int32
from std_msgs.msg import String
import time
from threading import Thread,Lock

class Main():
    def __init__(self):
        rospy.init_node('roadPlan', anonymous=True)
        self.roadPlan_pub = rospy.Publisher('/roadPlan_pub', String, queue_size=10)
        self.roadPlan_sub = rospy.Subscriber('/roadPlan_sub', String, self.receiveMessage, queue_size=10)
        rospy.on_shutdown(self.my_shutdown)
        # 初始值均为 1
        self.A = 1
        self.B = 1
        self.C = 1
        self.flag = 0  # 取药成功为1，否则为0
        self.lock = Lock()  # 互斥锁
        self.startOkFlag=False

        self.time_flag=0#药品时间间隔不变
        # 记录取药的顺序
        self.window = []
        # 记录送药到哪个区域的顺序
        self.num = []
        self.peisong_dict = {}
        self.min3_flag=0 #未到3min
        # 放这合不合适
        # self.new_dict = {}
        self.running = False
        self.t = 0
        self.quyao_to_num = {'A': 1, 'C': 0, 'B': 2, '1': 6, '2': 5, '3': 4, '4': 3}
        self.list=['C','A','B']
        # 记录上次更新时间的时间戳
        self.last_update_A = time.time()
        self.last_update_B = time.time()
        self.last_update_C = time.time()
        self.min_jishi = time.time()  # 获取当前的时间戳
        #第一次开始计数
        self.one=1
        self.timeshengxiao_a=0#0-代表第一次变化世家，1-代表后面的计数
        self.timeshengxiao_b=0
        self.timeshengxiao_c=0
        self.current_time=0.0
        self.count=0


    def init(self):
        self.t = Thread(target=self.update_values)
        self.t.start()
        print('开始计数')
        # return self.last_update_A,self.last_update_B,self.last_update_C
    def update_values(self):
        # A=self.A
        # B=self.B
        # C=self.C
        if self.one==1:
            # 记录上次更新时间的时间戳
            self.last_update_A = time.time()
            self.last_update_B = time.time()
            self.last_update_C = time.time()
            self.min_jishi = time.time()  # 获取当前的时间戳
            self.one=0
        min_jishi = self.min_jishi
        # last_update_A = self.last_update_A
        # last_update_B = self.last_update_B
        # last_update_C = self.last_update_C
        self.a = 0.0
        self.b = 0.0
        self.c = 0.0
        self.running = True
        # self.a = (120 - (current_time - last_update_A)) / 2.0
        # self.b = (120 - (current_time - last_update_B)) / 2.0
        # self.c = (120 - (current_time - last_update_C)) / 2.0
        while self.running and not rospy.is_shutdown():
            # 获取当前时间戳
            if self.count == 6:
                print('比赛完成')
                self.toggle_thread()
            self.current_time = time.time()
            current_time = self.current_time
            if current_time - min_jishi >= 3*60  :# 60
                print('3min时间到')
                self.count+=1
                # self.min3_flag = 1
                #在这里发送信号
                print('3min is ok')
                self.roadPlan_pub.publish('3min is ok')
                min_jishi=current_time
            if self.time_flag == 0:
                # 如果距离上次更新 A 的时间已经超过 2 分钟，则将 A 的值加 1
                if current_time - self.last_update_A >= 2 * 60:
                    self.A += 1
                    self.last_update_A = current_time

                # 如果距离上次更新 B 的时间已经超过 1 分钟，则将 B 的值加 1
                if current_time - self.last_update_B >= 1 * 60:
                    self.B += 1
                    self.last_update_B = current_time

                # 如果距离上次更新 C 的时间已经超过 40 秒，则将 C 的值加 1
                if current_time - self.last_update_C >= 40:
                    self.C += 1
                    self.last_update_C = current_time

            if self.time_flag == 1:#时间变了
                # 如果距离上次更新 A 的时间已经超过 1 分钟，则将 A 的值加 1
                # self.a = (120 - (current_time - last_update_A)) / 2.0
                # self.b = (120 - (current_time - last_update_B)) / 2.0
                # self.c = (120 - (current_time - last_update_C)) / 2.0

                if self.timeshengxiao_a == 1 and current_time - self.last_update_A >= 1 * 60:
                    print('进入A的1min计数')
                    self.A += 1
                    self.last_update_A = current_time
                elif self.timeshengxiao_a == 0 and current_time - self.last_update_A >= self.a:#第一次生效
                    print('进入A的减半计数')
                    self.A += 1
                    self.timeshengxiao_a = 1
                    self.last_update_A = current_time
                # 如果距离上次更新 B 的时间已经超过 1 分钟，则将 B 的值加 1
                if self.timeshengxiao_b == 1 and current_time - self.last_update_B >= 0.5 * 60:
                    print('进入B的30s计数')
                    self.B += 1
                    self.last_update_B = current_time
                elif self.timeshengxiao_b == 0 and current_time - self.last_update_B >= self.b:#第一次生效
                    print('进入B的减半计数')
                    self.B += 1
                    self.timeshengxiao_b = 1
                    self.last_update_B = current_time
                # 如果距离上次更新 C 的时间已经超过 40 秒，则将 C 的值加 1
                if self.timeshengxiao_c == 1 and current_time - self.last_update_C >= 20:
                    print('进入C的20s计数')
                    self.C += 1
                    self.last_update_C = current_time
                elif self.timeshengxiao_c == 0 and current_time - self.last_update_C >= self.c:#第一次生效
                    print('进入C的减半计数')
                    self.C += 1
                    self.timeshengxiao_c = 1
                    self.last_update_C = current_time
            time.sleep(4)
            # 输出当前 A、B、C 的值以及时间戳
            print("A: {}, B: {}, C: {}, Time: {}".format(self.A,self.B,self.C,current_time))

    def parse_string(self, input_str):
        A = self.A
        B = self.B
        C = self.C
        quyao_to_num=self.quyao_to_num
        # 将字符串以 | 分割成列表
        str_list = input_str.split('|')

        # 将列表中的每个元素以 : 分割成键值对，存入字典中
        result_dict = {}

        for item in str_list:
            key, value = item.split(':')
            result_dict[key] = value

        keys1 = [key for key, value in result_dict.items() if value == 'A']  # 得到A要送的几个地方# 使用列表推导式筛选出值为 A 的键
        print(keys1)
        keys2 = [key for key, value in result_dict.items() if value == 'C']
        keys3 = [key for key, value in result_dict.items() if value == 'B']
        if len(keys1) != 0:
            print('有{}个A要送'.format(len(keys1)))
            for i in range(len(keys1)):
                # print('这是第 %d 次循环' % (i + 1))
                if '2' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['2'])
                    keys1.remove('2')
                elif '1' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['1'])
                    keys1.remove('1')
                elif '4' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['4'])
                    keys1.remove('4')
                elif '3' in keys1:
                    self.window.append(quyao_to_num['A'])
                    self.num.append(quyao_to_num['3'])
                    keys1.remove('3')
        if len(keys2) != 0:
            if keys2:
                print('有{}个C要送'.format(len(keys2)))
            for i in range(len(keys2)):
                # print('这是第 %d 次循环' % (i + 1))
                if '2' in keys2:
                    self.window.append(quyao_to_num['C'])
                    self.num.append(quyao_to_num['2'])
                    keys2.remove('2')
                elif '1' in keys2:
                    self.window.append(quyao_to_num['C'])
                    self.num.append(quyao_to_num['1'])
                    keys2.remove('1')

                elif '4' in keys2:
                    self.window.append(quyao_to_num['C'])
                    self.num.append(quyao_to_num['4'])
                    keys2.remove('4')
                elif '3' in keys2:
                    self.window.append(quyao_to_num['C'])
                    self.num.append(quyao_to_num['3'])
                    keys2.remove('3')
        if len(keys3) != 0:
            # while B != 0:
            if keys3:
                print('有{}个B要送'.format(len(keys3)))
            for n in range(len(keys3)):
                # print('这是第 %d 次循环' % (n + 1))
                if '2' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['2'])
                    keys3.remove('2')
                elif '1' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['1'])
                    keys3.remove('1')
                elif '4' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['4'])
                    keys3.remove('4')
                elif '3' in keys3:
                    self.window.append(quyao_to_num['B'])
                    self.num.append(quyao_to_num['3'])
                    keys3.remove('3')
        # if len(keys1) != 0 and A > 0:
        #     print('有{}个A要送'.format(len(keys1)))
        #     # for i in range(len(keys1)):
        #         # print('这是第 %d 次循环' % (i + 1))
        #     if '2' in keys1:
        #         self.window.append(quyao_to_num['A'])
        #         self.num.append(quyao_to_num['2'])
        #         keys1.remove('2')
        #     elif '1' in keys1:
        #         self.window.append(quyao_to_num['A'])
        #         self.num.append(quyao_to_num['1'])
        #         keys1.remove('1')
        #     elif '4' in keys1:
        #         self.window.append(quyao_to_num['A'])
        #         self.num.append(quyao_to_num['4'])
        #         keys1.remove('4')
        #     elif '3' in keys1:
        #         self.window.append(quyao_to_num['A'])
        #         self.num.append(quyao_to_num['3'])
        #         keys1.remove('3')
        print(self.window)
        print(self.num)

        # 用于实时更新取药之后，药物余量

    def judge(self):
        # new_dict = dict(list(zip(self.window, self.num)))
        # print(new_dict)
        # 判断是否前往取药区，若是，则相应药品减1，并将其从送货的列表中移除
        if self.flag == 1:
            # yao = next(key for key, value in new_dict.items() if value == self.num[0])
            yao = self.window[0]
            if yao == 1:
                self.lock.acquire()
                self.A -= 1
                self.lock.release()
                print('A以送达')
            elif yao == 2:
                self.lock.acquire()
                self.B -= 1
                self.lock.release()
                print('B以送达')
            elif yao == 0:
                self.lock.acquire()
                self.C -= 1
                self.lock.release()
                print('C以送达')

            del self.window[0]
            del self.num[0]
            print('window:', self.window)
            print('num:', self.num)
            self.flag = 0

    def toggle_thread(self):
        self.running = False
        # if not self.running:
        #     self.t.join()
    def sendCmd(self,msg):
        data = msg.data
        print(data)
        window=self.window
        num=self.num
        list=self.list

        if self.list[window[0]]=='C':
            rospy.sleep(1)
            if self.C<=0:
                if len(window)>1:
                    print("C不足,切换至其他任务")
                    if self.window[0]==self.window[1] and len(window)>2:
                        self.window[0],self.window[2] = self.window[2],self.window[0]
                        self.num[0], self.num[2] = self.num[2], self.num[0]
                    else:
                        self.window[0],self.window[1] = self.window[1],self.window[0]
                        self.num[0], self.num[1] = self.num[1], self.num[0]
                    self.sendCmd(msg)
                else:
                    print("C不足等待")
                    self.roadPlan_pub.publish("twaiting")
                    while self.C <= 0: rospy.sleep(0.1)
                    print("C补齐")
                    self.sendCmd(msg)
            else:
                
                self.roadPlan_pub.publish('w:{}|n:{}'.format(window[0], num[0]))
                print(self.list[window[0]])#c
                self.roadPlan_pub.publish(self.list[window[0]])
                self.w=list[window[0]]
                print("发送任务:"+'w:{}|n:{}'.format(window[0], num[0]))
        elif self.list[window[0]]=='A':
            rospy.sleep(1)
            if self.A<=0:
                if len(window)>1:
                    print("A不足,切换至其他任务")
                    if self.window[0]==self.window[1] and len(window)>2:
                        self.window[0],self.window[2] = self.window[2],self.window[0]
                        self.num[0], self.num[2] = self.num[2], self.num[0]
                    else:
                        self.window[0],self.window[1] = self.window[1],self.window[0]
                        self.num[0], self.num[1] = self.num[1], self.num[0]
                    self.sendCmd(msg)
                else :
                    print("A不足等待")
                    self.roadPlan_pub.publish("twaiting")
                    while self.A <= 0: rospy.sleep(0.1)
                    print("A补齐")
                    self.sendCmd(msg)
            else:
                print(self.list[window[0]])#c
                self.roadPlan_pub.publish(self.list[window[0]])
                self.w=list[window[0]]
                print("发送任务:"+'w:{}|n:{}'.format(window[0], num[0]))
                self.roadPlan_pub.publish('w:{}|n:{}'.format(window[0], num[0]))
        elif self.list[window[0]]=='B' :
            rospy.sleep(1)
            if self.B<=0:
                if len(window)>1:
                    print("B不足,切换至其他任务")
                    if self.window[0]==self.window[1] and len(window)>2:
                        self.window[0],self.window[2] = self.window[2],self.window[0]
                        self.num[0], self.num[2] = self.num[2], self.num[0]
                    else:
                        self.window[0],self.window[1] = self.window[1],self.window[0]
                        self.num[0], self.num[1] = self.num[1], self.num[0]
                    self.sendCmd(msg)
                else:
                    print("B不足等待")
                    self.roadPlan_pub.publish("twaiting")
                    while self.B <= 0 and not rospy.is_shutdown(): rospy.sleep(0.1)
                    print("B补齐")
                    self.sendCmd(msg)
            else:
                print(self.list[window[0]])#c
                self.roadPlan_pub.publish(self.list[window[0]])
                self.w=list[window[0]]
                print("发送任务:"+'w:{}|n:{}'.format(window[0], num[0]))
                self.roadPlan_pub.publish('w:{}|n:{}'.format(window[0], num[0]))
    #随时接收消息
    def receiveMessage(self,msg):
        data = msg.data
        print(data)
        window=self.window
        # 优先试探需要执行的任务
        if (len(data) == 10):
            print("配送完成需要下一次数据")
            if(len(window)>0):
                self.sendCmd(msg) # 发送任务成功后继续执行，否则堵塞
                rospy.sleep(1)
                self.flag=1
                self.judge()
            else:
                print("window length below 0")
                self.roadPlan_pub.publish("thisTermOver")
        window=self.window
        num=self.num
        quyao_to_num = self.quyao_to_num
        window=self.window
        num=self.num
        list=self.list
        # 1表示到达配药点，3表示到达答题区，5表示到达取药区，7表示到达起点

        if (len(data) == 15):
            # self.roadPlan_pub.publish("planok")
            self.window=[]
            self.num = []
            print(self.window)
            rospy.sleep(1)
            self.roadPlan_pub.publish("planok")
            self.parse_string(data)
            #补一句要发送的
            self.sendCmd(msg)
            self.flag=1
            self.judge()
            # pub_dispense = rospy.Publisher('dispense_window', Int32, queue_size=10)
            # pub_pick = rospy.Publisher('pick_up_num', Int32, queue_size=10)
            # self.roadPlan_pub.publish('w:{}|n:{}'.format(self.window[0],self.num[0]))
        elif (data == "start" and self.startOkFlag==False):
            # 开时钟,调用
            self.init()
            print("开时钟")
            rospy.sleep(1)
            self.roadPlan_pub.publish("startok")
            self.startOkFlag=True

                
            # rospy.sleep(0.5)
            # self.sound_out_pub.publish("Arrive at the dispensing point")
            # self.pick_up_pub.publish(self.roadWindow)  # 发布配药区窗口
            # self.cmd_pub.publish(1)  # 发布去配药区命令
            # self.arrivedFlag = True
        if (data == 'read number dec'):
            print("#时间变少")
            self.time_flag=1
            self.a = (120 - (self.current_time - self.last_update_A)) / 2.0
            self.b = (60 - (self.current_time - self.last_update_B)) / 2.0
            self.c = (40 - (self.current_time - self.last_update_C)) / 2.0
            # print(self.a)
            # print(self.b)
            # print(self.c)
            self.last_update_A = time.time()
            self.last_update_B = time.time()
            self.last_update_C = time.time()
        if (data == 'read number inc'):
            print("#时间变多")
            self.time_flag=1
            self.a = (120 - (self.current_time - self.last_update_A)) * 2.0
            self.b = (60 - (self.current_time - self.last_update_B)) * 2.0
            self.c = (40 - (self.current_time - self.last_update_C)) * 2.0
            # print(self.a)
            # print(self.b)
            # print(self.c)
            self.last_update_A = time.time()
            self.last_update_B = time.time()
            self.last_update_C = time.time()

        if(data == '3min ok'):
            print('收到3min ok')
            self.roadPlan_pub.publish('收到3min ok')
            self.min3_flag = 0




    def run(self):
        while not rospy.is_shutdown():
            rospy.sleep(0.1)

        # self.myRoadPlan.toggle_thread()


    def my_shutdown(self):
        rospy.loginfo("Task over!")


if __name__ == "__main__":
    obj = Main()
    obj.run()
    # try:
    #     obj.run()
    #     msg.data=input()
    # except ROSInterruptException:#rospy.
    #       pass

























#最后再来弄
    # def receiveMessage(self, msg):
    #     # 1表示到达配药点，3表示到达答题区，5表示到达取药区，7表示到达起点
    #     if (msg.data == "start"):
    #         # 开时钟,调用
    #         self.init()
    #         print("开时钟")
    #         rospy.sleep(0.5)
    #         # self.roadPlan_pub.publish("startok")
    #     if (len(msg.data) == 15):
    #         self.roadPlan_pub.publish("planok")
    #         print("planok")
    #         self.parse_string(msg.data)
    #     if (len(msg.data) == 10):
    #         print("配送完成需要下一次")
    #         rospy.sleep(0.5)
    #         self.sound_out_pub.publish("Arrive at the dispensing point")
    #         self.pick_up_pub.publish(self.roadWindow)  # 发布配药区窗口
    #         self.cmd_pub.publish(1)  # 发布去配药区命令
    #         self.arrivedFlag = True
    #     if (msg.data == 14):
    #         print("时间变少")
    #         self.time_flag=1