#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32

rospy.init_node('publisher_node')
rate = rospy.Rate(10)  # 设置发布频率为 10Hz

dispense_pub = rospy.Publisher('/dispense_window', Int32, queue_size=10)
pick_up_pub = rospy.Publisher('/pick_up_num', Int32, queue_size=10)
cmd_pub = rospy.Publisher('/cmd_send', Int32, queue_size=10)
count = 0
while not rospy.is_shutdown():
    dispense = Int32()
    pick_up = Int32()
    cmd = Int32()
    dispense.data = int(raw_input('发布配药区的点:0：C窗口,1：A窗口,2：B窗口 '))
    pick_up.data = int(raw_input('发布取药区的点:3：4号窗口,4：3号窗口,5：2号窗口,6：1号窗口'))
    cmd.data = int(raw_input('发布相应区域的点:1：去往配药区,3：去往答题区,5：去往取药区,7：去往起点'))
    count = 0
    while not rospy.is_shutdown() and count < 5:
        dispense_pub.publish(dispense)  # 发布值为1的消息到 '/dispense_window' 话题
        pick_up_pub.publish(pick_up)  # 发布值为2的消息到 '/pick_up_num' 话题
        cmd_pub.publish(cmd)      # 发布值为3的消息到 '/cmd_send' 话题
        count += 1
        rate.sleep()            # 等待发布周期结束


