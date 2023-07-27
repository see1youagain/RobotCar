#!/usr/bin/python
# -*- coding:utf8 -*-
import rospy

def run(channel_in, channel_out):
    while not rospy.is_shutdown():
        # receive a message
        message = channel_in.receive_message()
        if message is not None:  # make sure message is not None before printing
            rospy.loginfo(message)
        # send a message
        channel_out.send_message('Hello from script 1')
        rospy.sleep(0.2)  # add a sleep to prevent the loop from running too fast


# if __name__=="__main__":
#     while not rospy.is_shutdown():
#         rospy.sleep(0.2)