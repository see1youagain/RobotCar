#!/usr/bin/python
# -*- coding:utf8 -*-
import rospy
from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient
from std_msgs.msg import String

class Sound():
    def __init__(self):
        self.soundhandle = SoundClient()
        rospy.sleep(1)
    def say_text(self,text):
        if(text[1]==' '):
            # 接收到数字
            self.soundhandle.say(text,volume=1)
            # 等待语音播放完成
            rospy.sleep(5)
        elif(text=="dispense"):
            audio_file_path ="/home/EPRobot/robot_ws/src/eprobot_start/script/alphabet/dispense.wav"
            # 使用sound_play节点播放音频文件
            self.soundhandle.playWave(audio_file_path)
            # 给音频文件播放留出足够的时间
            rospy.sleep(2)
        elif(text=="pickup"):
            audio_file_path ="/home/EPRobot/robot_ws/src/eprobot_start/script/alphabet/pickup.wav"
            # 使用sound_play节点播放音频文件
            self.soundhandle.playWave(audio_file_path)
            # 给音频文件播放留出足够的时间
            rospy.sleep(2)
        elif(text=="start"):
            audio_file_path ="/home/EPRobot/robot_ws/src/eprobot_start/script/alphabet/start.wav"
            # 使用sound_play节点播放音频文件
            self.soundhandle.playWave(audio_file_path)
            # 给音频文件播放留出足够的时间
            rospy.sleep(2)

    def getMsgs(self,data):
        rospy.loginfo("soundNode receive: %s",data.data)
        self.say_text(data.data)

if __name__ == '__main__':
    obj=Sound()
    rospy.Subscriber('/my_sound_topic', String, obj.getMsgs)
    rospy.init_node('sound_out_node')
    while True and not rospy.is_shutdown() :
        rospy.sleep(0.1)
