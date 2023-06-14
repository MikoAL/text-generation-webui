import asyncio
import json
import sys

try:
	import websockets
except ImportError:
	print("Websockets package not found. Make sure it's installed.")

# For local streaming, the websockets are hosted without ssl - ws://
HOST = 'localhost:5005'
URI = f'ws://{HOST}/api/v1/stream'
your_name = 'User'
# For reverse-proxied streaming, the remote will likely host with ssl - wss://
# URI = 'wss://your-uri-here.trycloudflare.com/api/v1/stream'

# Please help update this so that it can use the files from the folder "characters"
# I have only been coding for 2 months, pretty much self-taught, 
# I don't know what I am doing.
# But I am trying my best QwQ 

class Character:
	def __init__(self, name, chat_history, example_dialogue, story, memory, filename=None, username=None, world_info=None):
		self.name = name
		self.chat_history = chat_history
		self.example_dialogue = example_dialogue
		self.story = story
		self.memory = memory
		self.filename = filename
		self.username = username
		self.world_info = world_info
		

async def run(context, stopping_strings):
	# Note: the selected defaults change from time to time.
	stopping_strings.append('<START>')
	stopping_strings.append('<END>')
	#print('Stopping Strings: \n', stopping_strings)
	request = {
		'prompt': context,
		'max_new_tokens': 250,
		'do_sample': True,
		'temperature': 0.95,
		'top_p': 0.1,
		'typical_p': 1,
		'repetition_penalty': 1.18,
		'top_k': 40,
		'min_length': 0,
		'no_repeat_ngram_size': 0,
		'num_beams': 1,
		'penalty_alpha': 0,
		'length_penalty': 1,
		'early_stopping': False,
		'seed': -1,
		'add_bos_token': True,
		'truncation_length': 2048,
		'ban_eos_token': False,
		'skip_special_tokens': True,
		'stopping_strings': []
	}

	async with websockets.connect(URI, ping_interval=None) as websocket:
		await websocket.send(json.dumps(request))

		yield context  # Remove this if you just want to see the reply

		while True:
			incoming_data = await websocket.recv()
			incoming_data = json.loads(incoming_data)

			event_type = incoming_data['event']
			if event_type == 'text_stream':
				yield incoming_data['text']
			elif event_type == 'stream_end':
				return



async def print_response_stream(prompt, stopping_strings):
	global current_ai_response
	#print('current_ai_response at line 64:\n\t'+current_ai_response)
	i = 1
	async for response in run(prompt, stopping_strings):
		if i != 1:
			current_ai_response += response
			#print('The response added: '+response)
		i += 1
		# 'i' is a word count
		sys.stdout.write(response)
		sys.stdout.flush()# If we don't flush, we won't see tokens in realtime.
		


if __name__ == '__main__':
	prompt = "In order to make homemade bread, follow these steps:\n1)"
	asyncio.run(print_response_stream(prompt))


def generate_response(character, text):
	
	chatHistory = "\n".join(character.chat_history)
	global your_name
	questionPrefix = your_name+': '
	formatted_text = text.strip()
	responsePrefix = f"{character.username}:"
	stopping_string_question_prefix = questionPrefix.strip()
	stopping_string_response_prefix = responsePrefix.strip()
	stopping_strings = [stopping_string_question_prefix, stopping_string_response_prefix]
	
	persistentData = "\n\n".join(
	 [
		character.memory,
		character.world_info,
		
		
		"\n\n".join(character.example_dialogue),
		"\n".join(character.story)
	]
							  )
	
	prompt = "".join([
		persistentData, "\n",
		chatHistory, "\n" if chatHistory else "",
		questionPrefix,
		formatted_text, "\n",
		responsePrefix
					])
	#send to AI
	asyncio.run(print_response_stream(prompt, stopping_strings))

	
 
	global current_ai_response 
	# Deletes the leftover text "User"
	delete_length = len(stopping_string_question_prefix) - 1
	current_ai_response = current_ai_response[:-delete_length]
 

	character.chat_history.append(
		responsePrefix + " " + current_ai_response )


	return current_ai_response.strip()