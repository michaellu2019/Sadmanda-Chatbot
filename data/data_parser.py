import json
import os

# load downloaded messages json data to convert
print('Loading Data...')

data_entries = os.listdir('../raw_data/')
data_objects = []

# put all json data in array
for friend_file_name in data_entries:
	for file_name in os.listdir('../raw_data/' + friend_file_name):
		if 'message' in file_name:
			with open('../raw_data/' + friend_file_name + '/' + file_name) as json_file:
				data_objects.append(json.load(json_file))

conversations = []

# iterate through json data objects
for data in data_objects:
	# make sure the conversation only has two participants
	participants = [participant['name'] for participant in data['participants']]
	print('Conversation between:', participants)

	if len(data['participants']) == 2:
		conversation = []
		speakers = {}
		msg_objs = [{'sender_name': 'dummy_message', 'timestamp_ms': data['messages'][0]['timestamp_ms'], 'content': '', 'type': 'Generic'}] + data['messages']
		current_msg_obj = {'speaker': '', 'msg': ''}

		print('Parsing messages JSON data...')

		# iterate through each text message
		for i in range(len(msg_objs) - 1, -1, -1):
			msg_obj = msg_objs[i]

			# because some people leave messenger chats, they're not listed in the participants array field, so they must be manually found in the chats
			if msg_obj['sender_name'] not in speakers:
				speakers[msg_obj['sender_name']] = 1
				if len(speakers) > 2:
					print('Too many participants (unlisted):', len(speakers));
					conversation = []
					break

			# make sure the message contains text and is not a default Facebook system message
			if msg_obj['type'] == 'Generic' and 'content' in msg_obj and 'Say hi to your new Facebook friend' not in msg_obj['content'] and 'You can now call each other and see information like Active Status and when you\'ve read messages' not in msg_obj['content']:
				# only append a message to the conversation array if a new speaker is texting, otherwise, aggregate a persons messages into one exchange
				if msg_obj['sender_name'] != current_msg_obj['speaker']:
					if current_msg_obj['msg'] != '' and current_msg_obj['msg'] != ' ':
						conversation.append(current_msg_obj.copy())

					current_msg_obj['speaker'] = msg_obj['sender_name']
					current_msg_obj['msg'] = ''


				current_msg_obj['msg'] += msg_obj['content'] + ' '

			# if a message is sent more than 20 hours from the last one, assume that a new conversation with a new subject has started
			if i < len(msg_objs) - 1 and abs(msg_objs[i - 1]['timestamp_ms'] - msg_obj['timestamp_ms']) > 20 * 60 * 60 * 1000:
				if current_msg_obj['msg'] != '' and current_msg_obj['msg'] != ' ':
					conversation.append(current_msg_obj.copy())

				current_msg_obj['speaker'] = msg_obj['sender_name']
				current_msg_obj['msg'] = ''

				if len(conversation) > 0:
					conversations.append(conversation.copy())
					conversation = []
	else:
		print('Too many participants:', len(data['participants']));

# write data to text and JSON file
print('Writing data to text file...')

output_txt_file = open('conversations.txt', 'w', encoding='utf-8')

for conversation in conversations:
	# print('\nConversation:')
	output_txt_file.write('\n\n\nConversation:')

	for msg_obj in conversation:
		# print(msg_obj['speaker'] + ': ' + msg_obj['msg'])
		output_txt_file.write('\n' + msg_obj['speaker'] + ': ' + msg_obj['msg'])

output_txt_file.close()

print('Writing data to JSON file...')
with open('conversations.json', 'w') as json_file:
	json.dump({'conversations': conversations}, json_file)

# write to JSON file with chopped data that is strictly formatted:
# 1. every conversation begins with a question from you
# 2. every conversation ends with a response from you
# 3. every conversation is a question followed by an answer

chopped_conversations = []
exchanges = 0
successes = 0
failures_odd = 0
failures_short = 0

for conversation in conversations:
	chopped_conversation = []
	if len(conversation) > 1:
		for i, msg_obj in enumerate(conversation):
			if len(chopped_conversation) == 0:
				if msg_obj['speaker'] != 'Michael Lu':
					chopped_conversation.append(msg_obj.copy())
			else:
				if msg_obj['speaker'] != chopped_conversation[-1]['speaker']:
					chopped_conversation.append(msg_obj.copy())

		if chopped_conversation[-1]['speaker'] != 'Michael Lu':
			last_msg_obj = chopped_conversation.pop()

		if len(chopped_conversation) % 2 == 0 and len(chopped_conversation) > 1:
			chopped_conversations.append(chopped_conversation.copy())
			print('Successfully chopped conversation with', chopped_conversation[0]['speaker'], '... Even number of exchanges:', len(chopped_conversation))
			exchanges += len(chopped_conversation)
			successes += 1
		elif len(chopped_conversation) % 2 != 0:
			print('Error chopping conversation with', chopped_conversation[0]['speaker'], '... Odd number of exchanges:', len(chopped_conversation))
			failures_odd += 1
		else:
			print('Error chopping conversation with', conversation[0]['speaker'], 'and', conversation[1]['speaker'], '... Not enough exchanges:', len(chopped_conversation))
			failures_short += 1

print(successes, 'successful chops...', failures_odd, 'failed chops from odd-length exchanges...', failures_short, 'failed chops from short exchanges...', str(int((successes/(successes + failures_short + failures_odd)) * 100)) + '%')

print('Writing chopped data to JSON file...')
with open('chopped_conversations.json', 'w') as json_file:
	json.dump({'conversations': chopped_conversations}, json_file)

print()
print(exchanges, 'exchanges parsed...')
print(len(chopped_conversations), 'chopped conversations parsed...')
print()