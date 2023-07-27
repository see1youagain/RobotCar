#!/usr/bin/python
# -*- coding:utf8 -*-
import rospy
from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient
from std_msgs.msg import String

def say_text(text):
    soundhandle = SoundClient()
    rospy.sleep(1)
    if(len(text)==5):
        # 使用say()方法播放文本
        soundhandle.say(text)
        # 等待语音播放完成
        rospy.sleep(5)
    elif(text=="dispense"):
        audio_file_path ="/home/EPRobot/robot_ws/src/eprobot_start/script/alphabet/dispense.wav"
        # 使用sound_play节点播放音频文件
        soundhandle.playWave(audio_file_path)
        # 给音频文件播放留出足够的时间
        rospy.sleep(2)
    elif(text=="pickup"):
        audio_file_path ="/home/EPRobot/robot_ws/src/eprobot_start/script/alphabet/pickup.wav"
        # 使用sound_play节点播放音频文件
        soundhandle.playWave(audio_file_path)
        # 给音频文件播放留出足够的时间
        rospy.sleep(2)

def getMsgs(data):
    rospy.loginfo("soundNode receive: %s",data.data)
    say_text(data.data)

if __name__ == '__main__':
    rospy.Subscriber('/my_sound_topic', String, getMsgs)
    rospy.init_node('sound_out_node')
    soundhandle = SoundClient()
    rospy.sleep(1)


    soundhandle.say("1 2 3")
    rospy.sleep(2)

