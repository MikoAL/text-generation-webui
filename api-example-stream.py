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

# For reverse-proxied streaming, the remote will likely host with ssl - wss://
# URI = 'wss://your-uri-here.trycloudflare.com/api/v1/stream'

async def run(context):
    # Note: the selected defaults change from time to time.
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

    async with websockets.connect(URI) as websocket:
        await websocket.send(json.dumps(request))

        yield context # Remove this if you just want to see the reply

        while True:
            incoming_data = await websocket.recv()
            incoming_data = json.loads(incoming_data)

            event_type = incoming_data['event']
            if event_type == 'text_stream':
                yield incoming_data['text']
            elif event_type == 'stream_end':
                return



async def print_response_stream(prompt):
    async for response in run(prompt):
        print(response, end='')
        sys.stdout.flush() # If we don't flush, we won't see tokens in realtime.


if __name__ == '__main__':
    prompt = "In order to make homemade bread, follow these steps:\n1)"
    asyncio.run(print_response_stream(prompt))
