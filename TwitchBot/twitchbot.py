#!/usr/bin/python
from twitch.api import v3 as twitch
import slackweb, boto3

def main(event, context):
	masterUser = 'Your Slack User'
		
	slack = slackweb.Slack('Your Slack Hook')

	result = twitch.follows.by_user(masterUser)

	name = 'a dude'	
	
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('twitchstreamercache')
	tableData = table.scan()
	
	existing = []
	for item in tableData['Items']:
		existing.append(item['name'])
	print "Streaming as of the last run: "+str(existing)
	
	for followed in result['follows']:
		name = followed['channel']['name']
		stream = twitch.streams.by_channel(name)['stream']
		
		if (stream):
			link = stream['channel']['url']
			preview = stream['preview']['medium']
			
			if name not in existing:
				print 'New streamer: ' + name
				r = table.put_item(Item={'name': name})
				attachment = [{'title': name+' is now streaming on Twitch', 'text': link, 'image_url': preview}]

				slack.notify(attachments=attachment)
			else:
				print 'Still streaming: '+name
				existing.remove(name)

	if existing:
		print 'No longer streaming: '+ str(existing)
		
	for e in existing:
		r = table.delete_item(Key = {'name': e})
		
	print 'Run completed'
	
if __name__ == "__main__":
	main('','')