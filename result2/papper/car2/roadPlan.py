# #!/usr/bin/python
# # -*- coding:utf8 -*-

# import mySocketClient
# import rospy
# from std_msgs.msg import String

# if __name__ == "__main__":
#     rospy.init_node('roadPlan_node', anonymous=True)
#     obj=mySocketClient.mySocketClient()
#     roadPlan_pub = rospy.Publisher('/roadPlan_pub', String, queue_size=10)

#     def receiveMessage(msg):
#         print("roadPlan get message:"+msg.data)
#         obj.SendMessage(msg.data)

#     roadPlan_sub = rospy.Subscriber('/roadPlan_sub', String, receiveMessage, queue_size=10)
#     startSecondCarFlag=False
#     while not rospy.is_shutdown():
#         rec_msg=obj.GetMessage()
#         if len(rec_msg) !=0 :
#             print(rec_msg)
#             if startSecondCarFlag is True :
#                 print("roadPlan send message:"+rec_msg)
#                 roadPlan_pub.publish(rec_msg)
#             if(rec_msg=="car1:ok"):
#                 startSecondCarFlag=True
#                 roadPlan_pub.publish(rec_msg)

            
        
        