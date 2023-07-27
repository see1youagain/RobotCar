#!/usr/bin/env python
# -*- coding: utf-8 -*-
import roslib
import rospy
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler
from visualization_msgs.msg import Marker
from math import radians, pi
from std_msgs.msg import Int32,String
import os

class MoveBaseSquare():

    def __init__(self):
        rospy.init_node('nav_pharmacy', anonymous=False)
        rospy.on_shutdown(self.shutdown)
        os.system("amixer set Headphone 100%")  # 将小车的声音调大
        # Create a list to hold the target quaternions (orientations)
        # 创建一个列表，保存目标的角度数据
        quaternions = list()

        # First define the corner orientations as Euler angles
        # 定义四个顶角处机器人的方向角度（Euler angles:http://zh.wikipedia.org/wiki/%E6%AC%A7%E6%8B%89%E8%A7%92)
        # euler_angles = (0,pi/2, pi/2,-pi/2, -pi/2, pi/2,-pi/2,0,pi/4)
        euler_angles = (pi/2, pi/2 ,pi/2,-pi/2, -pi/2, -pi/2,-pi/2,0,pi,pi,pi/2,-pi/2,-pi/4,0)
        # Then convert the angles to quaternions
        # 将上面的Euler angles转换成Quaternion的格式
        for angle in euler_angles:
            q_angle = quaternion_from_euler(0, 0, angle, axes='sxyz')
            q = Quaternion(*q_angle)
            quaternions.append(q)

        # Create a list to hold the waypoint poses
        # 创建一个列表存储导航点的位置
        self.waypoints = list()
        self.waypoints.append(Pose(Point(1.355, 1.874, 1.553), quaternions[0]))  # //C
        self.waypoints.append(Pose(Point(0.483, 2.396, 1.564), quaternions[1]))  # //A
        self.waypoints.append(Pose(Point(1.380, 2.800, 1.539), quaternions[2]))  # //B
        self.waypoints.append(Pose(Point(-1.039, 0.732, -1.542), quaternions[3]))  # //4
        self.waypoints.append(Pose(Point(-1.830, 1.311, -1.586), quaternions[4]))  # //3
        self.waypoints.append(Pose(Point(-0.991, 1.824, -1.574), quaternions[5]))  # //2
        # self.waypoints.append(Pose(Point(-1.810 ,2.254 ,-1.598), quaternions[6]))  # //1
        self.waypoints.append(Pose(Point(-1.731, 2.366, - 1.564), quaternions[6]))  # //1
        self.waypoints.append(Pose(Point(0.008, -0.002, 0.011), quaternions[7]))  # 起点
        self.waypoints.append(Pose(Point(-0.329, 3.7521, 3.118), quaternions[8]))  # 终点
        # self.waypoints.append(Pose(Point(0.317, 3.7, 3.097), quaternions[9]))  #配药区到取药区的必经点
        self.waypoints.append(Pose(Point(0.253, 3.7558, 3.097), quaternions[9]))  # 配药区到取药区的必经点
        self.waypoints.append(Pose(Point(0.924, 2.396, 1.539), quaternions[10]))  # 配药中点
        self.waypoints.append(Pose(Point(-1.400, 1.834, -1.539), quaternions[11]))  # 取药中点
        self.waypoints.append(Pose(Point(-1.003, 0.058, -0.685), quaternions[12]))  # 配药区到取药区的必经点
        self.waypoints.append(Pose(Point(-1.840, -0.320, -1.542), quaternions[13]))  # 仓库
        # Publisher to manually control the robot (e.g. to stop it)
        # 发布TWist消息控制机器人

        self.target = 0; # 小车的目的地状态
        self.i = 0   # 配药区指令
        self.j = 0   # 取药区指令
        self.count = 0  # 发布去对应区域
        self.num = 0  # 计数后退次数
        self.flag = 0 # 导航重新尝试次数
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # 接受时间话题
        self.dispense_sub = rospy.Subscriber('/dispense_window', Int32, self.position, queue_size=10)
        self.pick_up_sub = rospy.Subscriber('/pick_up_num', Int32, self.position1, queue_size=10)
        self.cmd_sub = rospy.Subscriber('/cmd_send', Int32, self.cmd_get, queue_size=10)

        # 发布话题返回标志
        self.arrive_flag = rospy.Publisher('/arrive_flag', Int32, queue_size=10)
        self.sound_out_pub = rospy.Publisher('/my_sound_topic', String, queue_size=10)

        # Subscribe to the move_base action server
        # 订阅move_base服务器的消息
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Waiting for move_base action server...")
        self.move_base.wait_for_server(rospy.Duration(60))
        rospy.loginfo("Connected to move base server")
        rospy.loginfo("Starting navigation...")
        # Initialize a counter to track waypoints
        # 初始化一个计数器，记录到达的顶点号
    
        while (not rospy.is_shutdown()):  # 如果ros系统没有关机的话
            # 有限状态机
            if (self.count == 1 and self.flag <= 1):  # 从起点到配药区
                rospy.loginfo("从起点到配药区")
                # Intialize the waypoint goal
                # 初始化goal为MoveBaseGoal类型
                goal = MoveBaseGoal()
                self.flag += 1
                # Use the map frame to define goal poses
                # 使用map的frame定义goal的frame id
                goal.target_pose.header.frame_id = 'map'
                # Set the time stamp to "now"
                # 设置时间戳
                goal.target_pose.header.stamp = rospy.Time.now()
                self.target = self.i
                goal.target_pose.pose = self.waypoints[self.i]  # self.i
                if (self.move(goal) == True):
                    self.sound_out_pub.publish("dispense")
                    rospy.sleep(0.5)
                    rospy.loginfo("到达配药区。。。。。。。。")
                    rospy.loginfo("从配药区到必经点1")
                    goal = MoveBaseGoal()
                    # Use the map frame to define goal poses
                    # 使用map的frame定义goal的frame id
                    self.target = 8
                    goal.target_pose.header.frame_id = 'map'
                    # Set the time stamp to "now"
                    # 设置时间戳
                    goal.target_pose.header.stamp = rospy.Time.now()
                    goal.target_pose.pose = self.waypoints[9]
                    # Start the robot moving toward the goal
                    # 机器人移动
                    if (self.move(goal) == True):
                        rospy.sleep(1)
                        rospy.loginfo("到达必经点1")
                        self.flag = 0
                        self.arrive_flag.publish(1)
                        rospy.loginfo("返回成功")
                        self.count = 2
                # else:
                #     rospy.loginfo("导航超时，直接回到起点。。。。")
                #     self.arrive_flag.publish(1)
                #     rospy.loginfo("返回成功")
                #     self.count = 7

            elif (self.count == 3 and self.flag <= 1):  # 到屏幕识别点
                rospy.loginfo("去屏幕识别点")
                # Intialize the waypoint goal
                # 初始化goal为MoveBaseGoal类型
                goal = MoveBaseGoal()
                self.flag += 1
                self.target = 9
                # Use the map frame to define goal poses
                # 使用map的frame定义goal的frame id
                goal.target_pose.header.frame_id = 'map'
                # Set the time stamp to "now"
                # 设置时间戳
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[8]
                # Start the robot moving toward the goal
                # 机器人移动
                if (self.move(goal) == True):
                    rospy.sleep(0.5)
                    rospy.loginfo("到达屏幕识别点。。。。。。。。")
                    self.flag = 0
                    self.arrive_flag.publish(3)
                    rospy.loginfo("返回成功")
                    self.count = 4

            elif (self.count == 5 and self.flag <= 1):  # 到取药区
                # Intialize the waypoint goal
                # 初始化goal为MoveBaseGoal类型
                self.flag = 3
                rospy.loginfo("从必经点1到必经点2")
                # Intialize the waypoint goal
                # 初始化goal为MoveBaseGoal类型
                goal = MoveBaseGoal()
                # Use the map frame to define goal poses
                # 使用map的frame定义goal的frame id
                goal.target_pose.header.frame_id = 'map'
                # Set the time stamp to "now"
                # 设置时间戳
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[8]
                if (self.move(goal) == True):
                    rospy.sleep(0.5)
                    rospy.loginfo("到达必经点2")
                    rospy.loginfo("去取药区")
                    # Intialize the waypoint goal
                    # 初始化goal为MoveBaseGoal类型
                    goal = MoveBaseGoal()
                    # Use the map frame to define goal poses
                    # 使用map的frame定义goal的frame id
                    goal.target_pose.header.frame_id = 'map'
                    # Set the time stamp to "now"
                    # 设置时间戳
                    # self.flag = 2
                    goal.target_pose.header.stamp = rospy.Time.now()
                    goal.target_pose.pose = self.waypoints[self.j]  # self.j
                    self.target = self.j
                    # Start the robot moving toward the goal
                    # 机器人移动
                    if (self.move(goal) == True):
                        self.sound_out_pub.publish("pickup")
                        rospy.sleep(0.5)
                        rospy.loginfo("到达取药区。。。。。。。。")
                        self.flag = 0
                        self.arrive_flag.publish(5)
                        rospy.loginfo("返回成功")
                        self.count = 6
                        
            elif (self.count == 7 and self.flag <= 1):  # 起点
                rospy.loginfo("从取药区到必经点")
                # Intialize the waypoint goal
                # 初始化goal为MoveBaseGoal类型
                goal = MoveBaseGoal()
                self.flag += 1
                # Use the map frame to define goal poses
                # 使用map的frame定义goal的frame id
                goal.target_pose.header.frame_id = 'map'
                # Set the time stamp to "now"
                # 设置时间戳
                goal.target_pose.header.stamp = rospy.Time.now()
                self.target = 7
                goal.target_pose.pose = self.waypoints[12]
                if (self.move(goal) == True):
                    rospy.sleep(0.5)
                    rospy.loginfo("到达必经点")
                    rospy.loginfo("去起点")
                    # Intialize the waypoint goal
                    # 初始化goal为MoveBaseGoal类型
                    goal = MoveBaseGoal()
                    # Use the map frame to define goal poses
                    # 使用map的frame定义goal的frame id
                    goal.target_pose.header.frame_id = 'map'
                    # Set the time stamp to "now"
                    # 设置时间戳
                    goal.target_pose.header.stamp = rospy.Time.now()
                    goal.target_pose.pose = self.waypoints[7]
                    # Start the robot moving toward the goal
                    # 机器人移动
                    if (self.move(goal) == True):
                        rospy.sleep(1)
                        rospy.loginfo("到达起点。。。。。。。。")
                        self.flag = 0
                        self.arrive_flag.publish(7)
                        rospy.loginfo("返回成功")
                        self.count = 8


            elif (self.count == 9 and self.flag <= 1):  # 识别点
                rospy.loginfo("识别点")
                # Intialize the waypoint goal
                # 初始化goal为MoveBaseGoal类型
                goal = MoveBaseGoal()
                self.flag += 1
                # Use the map frame to define goal poses
                # 使用map的frame定义goal的frame id
                goal.target_pose.header.frame_id = 'map'
                # Set the time stamp to "now"
                # 设置时间戳
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[9]
                # Start the robot moving toward the goal
                # 机器人移动
                if (self.move(goal) == True):
                    rospy.sleep(1)
                    rospy.loginfo("到达识别点。。。。。。。。")
                    self.flag = 0
                    self.arrive_flag.publish(9)
                    rospy.loginfo("返回成功")
                    self.count = 8

            elif (self.count == 11 and self.flag <= 1):  # 配药中点
                rospy.loginfo("去配药中点")
                # Intialize the waypoint goal
                # 初始化goal为MoveBaseGoal类型
                goal = MoveBaseGoal()
                self.flag += 1
                # Use the map frame to define goal poses
                # 使用map的frame定义goal的frame id
                goal.target_pose.header.frame_id = 'map'
                # Set the time stamp to "now"
                # 设置时间戳
                goal.target_pose.header.stamp = rospy.Time.now()
                self.target = 11
                goal.target_pose.pose = self.waypoints[10]
                # Start the robot moving toward the goal
                # 机器人移动
                if (self.move(goal) == True):
                    # self.sound_out_pub.publish("dispense")
                    rospy.sleep(1)
                    rospy.loginfo("到达配药中点。。。。。。。。")
                    rospy.loginfo("从配药中点到必经点")
                    # Intialize the waypoint goal
                    # 初始化goal为MoveBaseGoal类型
                    goal = MoveBaseGoal()
                    # Use the map frame to define goal poses
                    # 使用map的frame定义goal的frame id
                    goal.target_pose.header.frame_id = 'map'
                    # Set the time stamp to "now"
                    # 设置时间戳
                    goal.target_pose.header.stamp = rospy.Time.now()
                    goal.target_pose.pose = self.waypoints[9]
                    if (self.move(goal) == True):
                        # self.sound_out_pub.publish("1 2 3")
                        rospy.sleep(0.5)
                        rospy.loginfo("到达必经点。。。。。。。。")
                        self.flag = 0
                        self.arrive_flag.publish(11)
                        rospy.loginfo("返回成功")
                        self.count = 10

            elif (self.count == 13 and self.flag <= 1):  # 取药中点
                rospy.loginfo("去取药中点")
                # Intialize the waypoint goal
                # 初始化goal为MoveBaseGoal类型
                goal = MoveBaseGoal()
                self.flag += 1
                # Use the map frame to define goal poses
                # 使用map的frame定义goal的frame id
                goal.target_pose.header.frame_id = 'map'
                # Set the time stamp to "now"
                # 设置时间戳
                self.target = 13
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[8]
                # Start the robot moving toward the goal
                # 机器人移动
                if (self.move(goal) == True):
                    # self.sound_out_pub.publish("pickup")
                    rospy.sleep(1)
                    rospy.loginfo("到达必经点1。。。。。。。。")
                    rospy.loginfo("从必经点1到取药中点")
                    # Intialize the waypoint goal
                    # 初始化goal为MoveBaseGoal类型
                    goal = MoveBaseGoal()
                    # Use the map frame to define goal poses
                    # 使用map的frame定义goal的frame id
                    goal.target_pose.header.frame_id = 'map'
                    # Set the time stamp to "now"
                    # 设置时间戳
                    goal.target_pose.header.stamp = rospy.Time.now()
                    goal.target_pose.pose = self.waypoints[11]
                    if (self.move(goal) == True):
                        rospy.sleep(0.5)
                        rospy.loginfo("到达取药中点")
                        rospy.loginfo("从取药中点到必经点2")
                        # Intialize the waypoint goal
                        # 初始化goal为MoveBaseGoal类型
                        goal = MoveBaseGoal()
                        # Use the map frame to define goal poses
                        # 使用map的frame定义goal的frame id
                        goal.target_pose.header.frame_id = 'map'
                        # Set the time stamp to "now"
                        # 设置时间戳
                        goal.target_pose.header.stamp = rospy.Time.now()
                        goal.target_pose.pose = self.waypoints[12]
                        if (self.move(goal) == True):
                            rospy.sleep(0.5)
                            rospy.loginfo("到达必经点2")
                            self.flag = 0
                            self.arrive_flag.publish(13)
                            rospy.loginfo("返回成功")
                            self.count = 12

            elif (self.count == 15 and self.flag <= 1):  # 仓库
                rospy.loginfo("去仓库")
                # Intialize the waypoint goal
                # 初始化goal为MoveBaseGoal类型
                goal = MoveBaseGoal()
                self.flag += 1
                # Use the map frame to define goal poses
                # 使用map的frame定义goal的frame id
                goal.target_pose.header.frame_id = 'map'
                # Set the time stamp to "now"
                # 设置时间戳
                goal.target_pose.header.stamp = rospy.Time.now()
                self.target = 13
                goal.target_pose.pose = self.waypoints[13]
                # Start the robot moving toward the goal
                # 机器人移动
                if (self.move(goal) == True):
                    rospy.sleep(0.5)
                    rospy.loginfo("到达仓库")
                    self.flag = 0
                    self.arrive_flag.publish(15)
                    rospy.loginfo("返回成功")
                    self.count = 16

    def move(self, goal):
        # Send the goal pose to the MoveBaseAction server
        # 把目标位置发送给MoveBaseAction的服务器
        self.move_base.send_goal(goal)
        # Allow 1 minute to get there
        # 设定1分钟的时间限制
        rospy.loginfo("等待25秒")
        finished_within_time = self.move_base.wait_for_result(rospy.Duration(25))
        rospy.loginfo("等待完成")
        print(not finished_within_time or self.flag == 2)
        # If we don't get there in time, abort the goal
        # 如果一分钟之内没有到达，重新尝试
        if not finished_within_time or self.flag == 2:
            self.move_base.cancel_goal()
            rospy.loginfo("取消目的地成功")
            self.flag = 0
            self.num = 1
            if(self.num):
                rospy.loginfo("重新尝试")
                self.back()  # 如果没在规定时间到达目的地,退回到相应区域中点，然后重新去往目的地
            # else: #如果重复5次还未到达,将会退回角落，重新启用另一辆车
            # 启用另一辆车
        else:
            state = self.move_base.get_state()
            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo("Goal succeeded!")
                return True
        return False

    def back(self):
        # 去配药区卡顿
        if (self.target == 0 or self.target == 1 or self.target == 2 or self.target == 9):
            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = 'map'
            goal.target_pose.header.stamp = rospy.Time.now()
            goal.target_pose.pose = self.waypoints[10] # 去配药中点
            if (self.move(goal) == True):
                rospy.loginfo("后退成功")
                rospy.sleep(0.1)
                # 重新到达目标点
                goal = MoveBaseGoal()
                self.flag = 0
                goal.target_pose.header.frame_id = 'map'
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[self.target]
                if (self.move(goal) == True):
                    self.sound_out_pub.publish("dispense")
                    rospy.sleep(0.3)
                    self.count = 0 # 重新置零
                    rospy.loginfo("重新到达配药")
                    self.arrive_flag.publish(1)
                    self.count = 2
        # 去取药区卡顿
        elif (self.target == 3 or self.target == 4 or self.target == 5 or self.target == 6):
            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = 'map'
            goal.target_pose.header.stamp = rospy.Time.now()
            goal.target_pose.pose = self.waypoints[11] # 去取药中点
            if (self.move(goal) == True):
                rospy.loginfo("后退成功")
                rospy.sleep(0.1)
                # 重新到达目标点
                goal = MoveBaseGoal()
                self.flag = 0
                goal.target_pose.header.frame_id = 'map'
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[self.target]
                if (self.move(goal) == True):
                    self.sound_out_pub.publish("pickup")
                    rospy.sleep(0.3)
                    self.count = 0 # 重新置零
                    rospy.loginfo("重新到达取药")
                    self.flag = 0
                    self.arrive_flag.publish(5)
                    self.count = 6
        # 去配药中点卡顿
        elif (self.target == 11):
            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = 'map'
            goal.target_pose.header.stamp = rospy.Time.now()
            goal.target_pose.pose = self.waypoints[7] # 去起点
            if (self.move(goal) == True):
                rospy.loginfo("后退成功")
                rospy.sleep(0.1)
                # 重新到达目标点
                goal = MoveBaseGoal()
                self.flag = 0
                goal.target_pose.header.frame_id = 'map'
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[self.target]
                if (self.move(goal) == True):
                    rospy.sleep(0.3)
                    self.count = 0 # 重新置零
                    rospy.loginfo("重新到达配药中点")
                    rospy.loginfo("从配药中点到必经点")
                    # Intialize the waypoint goal
                    # 初始化goal为MoveBaseGoal类型
                    goal = MoveBaseGoal()
                    # Use the map frame to define goal poses
                    # 使用map的frame定义goal的frame id
                    goal.target_pose.header.frame_id = 'map'
                    # Set the time stamp to "now"
                    # 设置时间戳
                    goal.target_pose.header.stamp = rospy.Time.now()
                    goal.target_pose.pose = self.waypoints[9]
                    if (self.move(goal) == True):
                        # self.sound_out_pub.publish("1 2 3")
                        rospy.sleep(0.5)
                        rospy.loginfo("到达必经点。。。。。。。。")
                        self.flag = 0
                        self.arrive_flag.publish(11)
                        rospy.loginfo("返回成功")
                        self.count = 10
        # 去取药中点卡顿
        elif (self.target == 13):
            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = 'map'
            goal.target_pose.header.stamp = rospy.Time.now()
            goal.target_pose.pose = self.waypoints[9] # 去配药区到取药区的必经点
            if (self.move(goal) == True):
                rospy.loginfo("后退成功")
                rospy.sleep(0.1)
                # 重新到达目标点
                goal = MoveBaseGoal()
                self.flag = 0
                goal.target_pose.header.frame_id = 'map'
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[self.target]
                if (self.move(goal) == True):
                    rospy.sleep(0.3)
                    self.count = 0  # 重新置零
                    rospy.loginfo("重新到达取药中点")
                    self.flag = 0
                    self.arrive_flag.publish(13)
                    self.count = 6
        # 去起点卡顿
        elif (self.target == 7):
            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = 'map'
            goal.target_pose.header.stamp = rospy.Time.now()
            goal.target_pose.pose = self.waypoints[11]  # 去取药中点
            if (self.move(goal) == True):
                rospy.loginfo("后退成功")
                rospy.sleep(0.1)
                # 重新到达目标点
                goal = MoveBaseGoal()
                self.flag = 0
                goal.target_pose.header.frame_id = 'map'
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[7]
                if (self.move(goal) == True):
                    rospy.sleep(0.3)
                    self.count = 0  # 重新置零
                    rospy.loginfo("重新到达起点")
                    self.flag = 0
                    self.arrive_flag.publish(7)
                    self.count = 6
        # 去配药必经点1卡顿
        elif (self.target == 8):
            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = 'map'
            goal.target_pose.header.stamp = rospy.Time.now()
            goal.target_pose.pose = self.waypoints[10]  # 去配药中点
            if (self.move(goal) == True):
                rospy.loginfo("后退成功")
                rospy.sleep(0.1)
                # 重新到达目标点
                goal = MoveBaseGoal()
                self.flag = 0
                goal.target_pose.header.frame_id = 'map'
                goal.target_pose.header.stamp = rospy.Time.now()
                goal.target_pose.pose = self.waypoints[9]
                if (self.move(goal) == True):
                    rospy.sleep(0.3)
                    self.count = 0  # 重新置零
                    rospy.loginfo("重新到达必经点")
                    self.flag = 0
                    self.arrive_flag.publish(7)
                    self.count = 6
    def cmd_get(self, msg):
        if msg.data > 0:
            self.count = msg.data
            rospy.loginfo("Get cmd:%d", self.count)

    def position(self, msg):
        self.i = msg.data
        rospy.loginfo("Get dispense_window:%d", self.i)

    def position1(self, msg1):
        self.j = msg1.data
        rospy.loginfo("Get pick_up_num:%d", self.j)

    def shutdown(self):
        rospy.loginfo("Stopping the robot...")
        # Cancel any active goals
        self.move_base.cancel_goal()
        rospy.sleep(2)
        # Stop the robot
        self.cmd_vel_pub.publish(Twist())
        rospy.sleep(1)

if __name__ == '__main__':
    try:
        MoveBaseSquare()
    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation test finished.")