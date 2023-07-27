#!/usr/bin/python
# -*- coding:utf8 -*-
import rospy
from std_msgs.msg import Int32
import identifyPic
from std_msgs.msg import String
import mySocketClient
import os
import signal
import subprocess

def startCar():
    global roslaunch_process
    # 将工作目录切换到 "~/robot_ws"
    os.chdir(os.path.expanduser("~/robot_ws"))

    # 以子进程方式启动 roslaunch 和 rosrun
    roslaunch_process = subprocess.Popen(["roslaunch", "eprobot_start", "start_robot.launch"])
    rospy.sleep(25)
def EndCar():
    global roslaunch_process
    # 发送 SIGINT 信号以中断这两个进程
    roslaunch_process.send_signal(signal.SIGINT)

    # 确保这两个进程已经完全退出
    roslaunch_process.wait()


class Main():
    def __init__(self):
        rospy.init_node('lzzy_main', anonymous=True)
        print("startCaring...")
        # startCar()
        print("startCaring ok")

        self.dispense_pub = rospy.Publisher('/dispense_window', Int32, queue_size=10)
        self.pick_up_pub = rospy.Publisher('/pick_up_num', Int32, queue_size=10)
        self.cmd_pub = rospy.Publisher('/cmd_send', Int32, queue_size=10)
        self.arrive_sub=rospy.Subscriber('/arrive_flag', Int32, self.arriveSeccess,queue_size=10)
        self.roadPlan_pub = rospy.Publisher('/roadPlan_sub', String, queue_size=10)
        self.roadPlan_sub=rospy.Subscriber('/roadPlan_pub', String, self.receiveRoadPlan,queue_size=10)
        self.sound_out_pub = rospy.Publisher('/my_sound_topic', String, queue_size=10)
        self.socketClient=mySocketClient.mySocketClient()
        self.secondCarStartFlag=False
        self.thisTermOver=False
        self.loopCount=0
        self.blankLoopFlag=False
        self.threeMinOKFlag=False
        self.readNumFlag=True
        self.roadPlanStartOkFlag=False
        self.roadPlan_waiting=False
        self.nowPlan=""
        self.roadWindow=-1
        self.roadNum=-1
        self.status = 0 # 0:等待 1:识别1中 2:配药中 3:识别2中 4 取药中 5:起点中 6:空跑中 7:停车
        self.myIdentifyPic=identifyPic.IdentifyPic()
        
        rospy.on_shutdown(self.my_shutdown)
    
    def run(self):
        while not rospy.is_shutdown() and self.roadPlanStartOkFlag==False:
            self.roadPlan_pub.publish("start")
            rospy.sleep(0.5)
        while not rospy.is_shutdown():
            if self.threeMinOKFlag==True and self.status==0:
                # 3分钟到且等待
                self.status=1
                self.threeMinOKFlag=False
            while self.status==1 and not rospy.is_shutdown():
                picResult=""
                picResult=self.myIdentifyPic.getPic()
                if(len(picResult) == 15):
                    self.status=-1
                    self.roadPlan_pub.publish(picResult)
                    rospy.sleep(1) # 等待任务发放
                    self.loopCount+=1
            if(self.status==2 and self.roadWindow!=-1 and self.roadNum!=-1):
                print("配药中")
                rospy.sleep(0.5)
                self.dispense_pub.publish(self.roadWindow)
                self.cmd_pub.publish(1)
                self.roadWindow=-1
            if(self.status==0 and self.roadWindow==-1 and self.roadNum==-1 and self.threeMinOKFlag==False):
                self.blankLoopFlag=True
                self.status=6
                rospy.sleep(0.1)
                self.cmd_pub.publish(11)
        # EndCar()
        rospy.signal_shutdown("Task over!")
        rospy.spin()
        # self.myRoadPlan.toggle_thread()s

    def receiveRoadPlan(self,msg):
        rospy.loginfo("roadPlan"+msg.data)
        if self.secondCarStartFlag==False:
            if(msg.data=="startok"):
                self.status=1
                self.roadPlanStartOkFlag=True
                self.sound_out_pub.publish("start")
            if(msg.data[0]=="w"):
                if self.roadNum==-1 and self.roadWindow==-1:
                    self.nowPlan=msg.data
                    self.roadWindow=int(msg.data[2])
                    self.roadNum=int(msg.data[-1])
                    if self.status==-1:
                        self.dispense_pub.publish(self.roadWindow)
                        self.roadWindow=-1
                        self.cmd_pub.publish(1)
                        self.status=2
                else:
                    print("roadNum:{} roadWindow:{}".format(self.roadNum,self.roadWindow))
                    print("roadPlan error ... ...")
            if msg.data=="twaiting":
                self.roadPlan_waiting=True
            if(msg.data=="3min is ok"):
                self.threeMinOKFlag=True
            if msg.data=="thisTermOver":
                self.thisTermOver=True
        else :
            self.socketClient.SendMessage(msg.data)

    def arriveSeccess(self,msg):
        # 1表示到达配药点，3表示到达答题区，5表示到达取药区，7表示到达起点
        if(msg.data==1): 
            print("接收到 到达 配药区")
            rospy.sleep(0.5)
            if self.blankLoopFlag==True:
                self.cmd_pub.publish(11)
            elif(self.readNumFlag==True):
                self.cmd_pub.publish(3)
            else :
                self.pick_up_pub.publish(self.roadNum)
                rospy.sleep(0.1)
                self.roadNum=-1
                self.cmd_pub.publish(5)

        if(msg.data==3):
            # 打开摄像头识别数字
            identifyNumFlag=True
            identifyNum="0 4 8 6"
            if identifyNumFlag==True and self.readNumFlag==True:
                self.sound_out_pub.publish(identifyNum)
                # self.roadPlan_pub.publish("read number dec")
            self.readNumFlag=False
            rospy.sleep(2)
            self.pick_up_pub.publish(self.roadNum)
            rospy.sleep(1)
            self.roadNum=-1
            self.cmd_pub.publish(5)
        if(msg.data==5):
            rospy.sleep(0.3)
            print("接收到 到达 取药区")
            self.roadPlan_waiting=False
            self.thisTermOver = False
            self.roadPlan_pub.publish(self.nowPlan+" ok")
            self.status=-4
            
            if self.roadNum==-1 and self.loopCount>=1:
                while self.roadNum==-1 and self.roadPlan_waiting==False and not rospy.is_shutdown() and self.threeMinOKFlag==False and self.thisTermOver==False:
                    rospy.sleep(0.5)
                if self.roadNum!=-1 or self.roadPlan_waiting==True:
                    self.status=5
                    self.roadPlan_waiting=False
                    self.cmd_pub.publish(7)      # 发布去配药区命令
                else:
                    
                    print("car1结束,等待car2启动")
                    self.socketClient.SendMessage("car1:ok")
                    while not rospy.is_shutdown():
                        rospy.sleep(0.5)
                        msg=self.socketClient.GetMessage()
                        if(msg=="car2:ok"):
                            print("car2启动成功")
                            break
                    min3_flag=1 if self.threeMinOKFlag==True else 0
                    self.socketClient.SendMessage("car1:m:{}".format(min3_flag))
                    self.cmd_pub.publish(15)
                    self.secondCarStartFlag=True
                    while not rospy.is_shutdown():
                        socketMsg=self.socketClient.GetMessage()
                        if len(socketMsg)!=0 :
                            self.roadPlan_pub.publish(socketMsg)
            else:
                self.status=5
                self.cmd_pub.publish(7)      # 发布去配药区命令
                
        if(msg.data==7):
            rospy.sleep(1)
            print("接收到 到达 起点")
            self.blankLoopFlag=False
            if(self.threeMinOKFlag==True):
                self.status=1
                self.threeMinOKFlag=False
            elif(self.roadNum!=-1):
                self.status=2

            else:
                print("空跑中...")
                self.blankLoopFlag=True
                self.status=0
                
            
            # print("status:{}".format(self.status))
        if(msg.data==11):
            print("接收到 到达 空走配药区")
            rospy.sleep(0.5)
            self.cmd_pub.publish(13)
        if(msg.data==13):
            rospy.sleep(0.5)
            self.cmd_pub.publish(7)      # 发布去配药区命令


    
    def my_shutdown(self):
        rospy.loginfo("Task over!")

if __name__ == "__main__":
    obj=Main()
    try:
        obj.run()
    except rospy.ROSInterruptException:
        pass
