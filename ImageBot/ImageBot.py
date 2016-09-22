# @rentiak - 2016-08-12
#
# Based on the code in this SO answer:
# http://stackoverflow.com/questions/37083058/programmatically-searching-google-in-python-using-custom-search
from random import randint
import os
import sys
import re
import slackweb
import urllib
from googleapiclient.discovery import build

my_api_key = "Your API Key"
slackhookURL = "Your Slackhook URL"
my_cse_id = "Your Custom Search Engine ID"


def google_search(search_term, api_key, cse_id, **kwargs):
	service = build("customsearch", "v1", developerKey=api_key)
	images = []
	# try:
	res = service.cse().list(q=search_term, cx=cse_id, imgSize="large", safe="high", searchType="image", start=1).execute()

	for result in res['items']:
		images.append(result['link'])

	#Select a random image from the first 10
	selected_image = images[(randint(0,9))]

	# except HttpError, e:
	# 	print str(e)
	# 	selected_image = "http://i.imgur.com/s6io7c6.png"

	print "Selected image: " + selected_image
	
	return selected_image

def main():
	#We need to get the payload that Slack sent to the ironworker
	f = open(os.environ['PAYLOAD_FILE'], "r")
	data = f.read()
	f.close()
 	
	data = urllib.unquote_plus(data)
	print(data)

	#Pull out the trigger word so we can remove it from the sent text
	#Obviously we're not going to hard code this. Duh.
	trigger = re.search('&trigger_word=(.*)', data)
	if trigger:
		trigger=trigger.group(1)
	print 'Trigger word: ' + trigger

	#Pull the raw text out.
	query = re.search('&text=(.+?)&', data)
	if query:
		query=query.group(1)
	print 'Raw Query: ' + query

	#Remove the trigger word and the http request + delimiters to get our query
	query = query[len(trigger)+1:]
	query = query.replace("+", " ")
	print 'Query: ' + query

	#Get the first 30 google image results
	image = google_search(query, my_api_key, my_cse_id)

	#Pull out the channel we should send back to
	channel = re.search('&channel_name=(.+?)&', data)
	if channel:
		channel=channel.group(1)
	print 'Channel: ' + channel

	#Tell people about a rejection if we've hit our max
	if image == "http://i.imgur.com/s6io7c6.png":
		query = "Google API Limit has been hit for today"

	#Post back to slack in whatever channel we received it from
	slack = slackweb.Slack(slackhookURL)
	slack.notify(text = "<%s|%s>" % (str(image), str(query)), channel=channel)

if __name__ == "__main__":
	main()
