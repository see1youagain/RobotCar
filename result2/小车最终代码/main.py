#!/usr/bin/python
# -*- coding:utf8 -*-
import rospy
from std_msgs.msg import Int32
import identifyPic
import roadPlan
from std_msgs.msg import String


class Main():
    def __init__(self):
        rospy.init_node('lzzy_main', anonymous=True)
        self.dispense_pub = rospy.Publisher('/dispense_window', Int32, queue_size=10)
        self.pick_up_pub = rospy.Publisher('/pick_up_num', Int32, queue_size=10)
        self.cmd_pub = rospy.Publisher('/cmd_send', Int32, queue_size=10)
        self.arrive_sub=rospy.Subscriber('/arrive_flag', Int32, self.arriveSeccess,queue_size=10)
        self.roadPlan_pub = rospy.Publisher('/roadPlan_sub', String, queue_size=10)
        self.roadPlan_sub=rospy.Subscriber('/roadPlan_pub', String, self.receiveRoadPlan,queue_size=10)
        self.descNumFlag=True
        self.arriveOKFlag=True
        self.nowPlan=""
        self.threeMinOKFlag=False
        self.roadWindow=-1
        self.roadNum=-1
        self.status = -1 # 0 起点 1 图片识别成功，配药 2方案完毕 3答题区 4取药区
        self.myIdentifyPic=identifyPic.IdentifyPic()
        self.roadPlan_pub.publish("start")
        rospy.on_shutdown(self.my_shutdown)
    
    def run(self):
        loopCount=5
        while not rospy.is_shutdown() and loopCount>0:
            loopFlag=True
            picResult=""
            while loopFlag is True and not rospy.is_shutdown() and self.status==0:
                picResult=""
                picResult=self.myIdentifyPic.getPic()
                if(len(picResult) == 15):
                    loopFlag=False
                    self.status=1
                    rospy.sleep(0.5)
                    self.roadPlan_pub.publish(picResult)
            if(self.status==2 and self.roadWindow!=-1 and self.roadNum!=-1 and self.arriveOKFlag==True):
                self.dispense_pub.publish(self.roadWindow)
                rospy.sleep(0.1)
                self.cmd_pub.publish(1)
                self.roadWindow=-1
                self.arriveOKFlag=False

            while not rospy.is_shutdown() and self.status != 0 and self.status!=2:
                rospy.sleep(0.1)
        rospy.signal_shutdown("Task over!")
        rospy.spin()
        # self.myRoadPlan.toggle_thread()s

    def receiveRoadPlan(self,msg):
        rospy.loginfo("roadPlan"+msg.data)
        if(msg.data=="startok" and self.status==-1):
            self.status=0
        if(msg.data[0]=="w"):
            self.nowPlan=msg.data
            self.roadWindow=int(msg.data[2])
            self.roadNum=int(msg.data[-1])
            self.status=2
            
        if(msg.data=="3min is ok"):
            self.threeMinOKFlag=True
            if(self.arriveOKFlag==True):
                self.status=0
                self.threeMinOKFlag=False
            




    def arriveSeccess(self,msg):
        # 1表示到达配药点，3表示到达答题区，5表示到达取药区，7表示到达起点
        if(msg.data==1): 
            print("接收到 到达 配药区")
            rospy.sleep(1)
            if(self.descNumFlag==False):
                self.cmd_pub.publish(3)
            else :
                self.pick_up_pub.publish(self.roadNum)
                self.roadNum=-1
                self.cmd_pub.publish(5)

        if(msg.data==3):
            # 打开摄像头识别数字
            identifyNumFlag=False
            self.descNumFlag=True
            if(identifyNumFlag==True):
                self.roadPlan_pub.publish("read number ok")
            rospy.sleep(1)
            self.pick_up_pub.publish(self.roadNum)
            self.roadNum=-1
            self.cmd_pub.publish(5)
        if(msg.data==5):
            print("接收到 到达 取药区")
            rospy.sleep(1)
            self.roadPlan_pub.publish(self.nowPlan+" ok")
            self.status=4
            rospy.sleep(1)
            self.cmd_pub.publish(7)      # 发布去配药区命令
        if(msg.data==7):
            print("接收到 到达 起点")
            self.arriveOKFlag=True
            if(self.threeMinOKFlag==True):
                self.status=0
                self.threeMinOKFlag=False


    
    def my_shutdown(self):
        rospy.loginfo("Task over!")

if __name__ == "__main__":
    obj=Main()
    try:
        obj.run()
    except rospy.ROSInterruptException:
        pass


