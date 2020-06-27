from pyfcm import FCMNotification


'''
# Send a message to devices subscribed to a topic.
result = push_service.notify_topic_subscribers(topic_name="news", message_body=message)

# Conditional topic messaging
topic_condition = "'TopicA' in topics && ('TopicB' in topics || 'TopicC' in topics)"
result = push_service.notify_topic_subscribers(message_body=message, condition=topic_condition)
# FCM first evaluates any conditions in parentheses, and then evaluates the expression from left to right.
# In the above expression, a user subscribed to any single topic does not receive the message. Likewise,
# a user who does not subscribe to TopicA does not receive the message. These combinations do receive it:
# TopicA and TopicB
# TopicA and TopicC
# Conditions for topics support two operators per expression, and parentheses are supported.
# For more information, check: https://firebase.google.com/docs/cloud-messaging/topic-messaging
'''

SERVER_KEY = 'AAAAlf4IDNc:APA91bGYUv2ULlv5eoljoNcFgy9bhvdrlhaHW564P3HPs69i_htNJUCQs8JQGrkr3MGCHkRDj9cqwW4zAHDU7F9bwUP69UWkRBJ_HM2TMEdcYGXvyA8WKnbGybMELGSoio3y1LVFEvz7'

push_service = FCMNotification(api_key=SERVER_KEY)

topic = "MBC_pdnote"
message = 'TEST %s' % topic
# result = push_service.notify_topic_subscribers(topic_name=topic, message_body=message)
