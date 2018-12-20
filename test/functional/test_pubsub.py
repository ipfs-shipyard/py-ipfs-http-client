# _*_ coding: utf-8 -*-
import uuid

import pytest



@pytest.fixture
def pubsub_topic():
	"""
	Creates a unique topic for testing purposes
	"""
	return "{}.testing".format(uuid.uuid4())



def test_publish_subscribe(client, pubsub_topic):
	"""
	We test both publishing and subscribing at
	the same time because we cannot verify that
	something has been properly published unless
	we subscribe to that channel and receive it.
	Likewise, we cannot accurately test a subscription
	without publishing something on the topic we are subscribed
	to.
	"""
	# the message that will be published
	message = "hello"
	
	expected_data = "aGVsbG8="
	expected_topicIDs = [pubsub_topic]
	
	# get the subscription stream
	with client.pubsub.subscribe(pubsub_topic) as sub:
		# make sure something was actually returned from the subscription
		assert sub is not None
		
		# publish a message to topic
		client.pubsub.publish(pubsub_topic, message)
		
		# get the message
		sub_data = sub.read_message()
		
		# assert that the returned dict has the following keys
		assert "data" in sub_data
		assert "topicIDs" in sub_data
		
		assert sub_data["data"] == expected_data
		assert sub_data["topicIDs"] == expected_topicIDs


def test_ls(client, pubsub_topic):
	"""
	Testing the ls, assumes we are able
	to at least subscribe to a topic
	"""
	expected_return = {"Strings": [pubsub_topic]}
	
	# subscribe to the topic testing
	sub = client.pubsub.subscribe(pubsub_topic)
	
	channels = None
	try:
		# grab the channels we"re subscribed to
		channels = client.pubsub.ls()
	finally:
		sub.close()
	
	assert channels == expected_return


def test_peers(client):
	"""
	Not sure how to test this since it fully depends
	on who we"re connected to. We may not even have
	any peers
	"""
	peers = client.pubsub.peers()
	
	# make sure the Strings key is in the map thats returned
	assert "Strings" in peers
	
	# ensure the value of "Strings" is a list.
	# The list may or may not be empty.
	assert isinstance(peers["Strings"], list)