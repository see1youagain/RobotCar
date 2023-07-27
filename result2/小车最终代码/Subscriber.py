#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32
class Sub():
    def __init__(self):
        rospy.init_node('publisher_node')
        rate = rospy.Rate(10)  # 设置发布频率为 10Hz
        self.dispense_pub = rospy.Publisher('/dispense_window', Int32, queue_size=10)
        self.pick_up_pub = rospy.Publisher('/pick_up_num', Int32, queue_size=10)
        self.cmd_pub = rospy.Publisher('/cmd_send', Int32, queue_size=10)
        # window=0,cmd=1;cmd=3;pickup=2,cmd=5;window=1,cmd=1;pickup=6,cmd=5;window=1,cmd=1;pickup=6,cmd=5
        count = 0
        self.status = 0
        self.arrive_sub = rospy.Subscriber('/arrive_flag', Int32, self.arriveSeccess, queue_size=10)


        while not rospy.is_shutdown():
            if (self.status == 0):
                self.dispense_pub.publish(0)
                self.cmd_pub.publish(1)   # 配药
            rospy.sleep(0.1)


    def arriveSeccess(self,msg):
        status = self.status
        self.status = 1
        cmd_pub=self.cmd_pub
        pick_up_pub=self.pick_up_pub
        dispense_pub=self.dispense_pub
        
        if (status == 0 and msg.data==1):  # 答题
            rospy.sleep(1)
            cmd_pub.publish(3)
            status += 1
        if (status == 1 and msg.data==3):  # 取药
            rospy.sleep(1)
            pick_up_pub.publish(3)
            cmd_pub.publish(5)
            status += 1
        if (status == 2 and msg.data==5):  # 起点
            rospy.sleep(1)
            cmd_pub.publish(7)
            status += 1
        if (status == 3 and msg.data==7):  # 配药
            rospy.sleep(1)
            dispense_pub.publish(1)
            cmd_pub.publish(1)
            status += 1
        if (status == 4 and msg.data==1):  # 取药
            rospy.sleep(1)
            pick_up_pub.publish(6)
            cmd_pub.publish(5)
            status += 1
        if (status == 5 and msg.data==5):  # 起点
            rospy.sleep(1)
            cmd_pub.publish(7)
            status += 1
        if (status == 6 and msg.data==7):  # 配药
            rospy.sleep(1)
            dispense_pub.publish(2)
            cmd_pub.publish(1)
            status += 1
        if (status == 7 and msg.data==1):  # 取药
            rospy.sleep(1)
            pick_up_pub.publish(4)
            cmd_pub.publish(5)
            status += 1
        if (status == 8 and msg.data==5):  # 起点
            rospy.sleep(1)
            cmd_pub.publish(7)
            status += 1
        self.status = status

if __name__ == "__main__":
    obj=Sub()


