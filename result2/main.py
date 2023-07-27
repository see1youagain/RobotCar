#! /usr/bin/python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import Int32
import identifyPic
import roadPlan


class Main():
    def __init__(self) -> None:
        rospy.init_node('lzzy_main', anonymous=True)
        self.rate = rospy.Rate(10)  # 设置发布频率为 10Hz
        self.dispense_pub = rospy.Publisher('/dispense_window', Int32, queue_size=10)
        self.pick_up_pub = rospy.Publisher('/pick_up_num', Int32, queue_size=10)
        self.cmd_pub = rospy.Publisher('/cmd_send', Int32, queue_size=10)
        self.cmd_sub=rospy.Subscriber('/arrive_flag', Int32, self.arriveSeccess,queue_size=10)
        self.arrivedFlag=False

        self.myIdentifyPic=identifyPic()
        self.myRoadPlan=roadPlan()
        self.myRoadPlan.init()
        rospy.on_shutdown(self.my_shutdown)
        while not rospy.is_shutdown():
            loopFlag=True
            picResult=""
            while loopFlag is True:
                picResult=self.myIdentifyPic.getPic()
                if(len(picResult) == 15):
                    loopFlag=False
            self.myRoadPlan.parse_string(picResult)
            roadWindow,roadNum=self.myRoadPlan.judge()
            dispense_pub.publish(roadWindow)  # 发布值为1的消息到 '/dispense_window' 话题
            cmd_pub.publish(1) # 配药
            while self.arrivedFlag is False:
                pass
            pick_up_pub.publish(roadNum)  # 发布值为2的消息到 '/pick_up_num' 话题
            cmd_pub.publish(5)      # 发布值为3的消息到 '/cmd_send' 话题
    def arriveSeccess(self):
        self.arrivedFlag=True
    
    def my_shutdown(self):
        rospy.loginfo("Task over!")

if __name__ == "__main__":
    obj=Main()




