import aiohttp
import asyncio
from config import WEBHOOK_URL

async def _send_single_message(session, content, headers):

    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    
    try:
        async with session.post(WEBHOOK_URL, json=payload, headers=headers) as response:
            if response.status == 200:
                print(f"Message segment sent successfully! (Length: {len(content)})")
                return True
            else:
                print(f"Message segment failed to send: {response.status}, {await response.text()}")
                return False
    except Exception as e:
        print(f"Error occurred while sending message segment: {str(e)}")
        return False

def split_message(message, max_length=1000):
    if len(message) <= max_length:
        return [message]
    
    segments = []
    lines = message.split('\n')
    current_segment = ""
    
    for line in lines:

        if len(current_segment) + len(line) + 1 > max_length:
            if current_segment:
                segments.append(current_segment.strip())
                current_segment = ""
            
            if len(line) > max_length:
                while line:
                    segments.append(line[:max_length])
                    line = line[max_length:]
            else:
                current_segment = line
        else:
            if current_segment:
                current_segment += '\n'
            current_segment += line
    
    if current_segment:
        segments.append(current_segment.strip())
    
    total = len(segments)
    segments = [f"[{i+1}/{total}]\n{segment}" for i, segment in enumerate(segments)]
    
    return segments

async def send_message_async(message_content):
    segments = split_message(message_content)
    total_segments = len(segments)
    
    if total_segments > 1:
        print(f"The message will be sent in {total_segments} segments")
    
    headers = {'Content-Type': 'application/json'}
    
    async with aiohttp.ClientSession() as session:
        for i, segment in enumerate(segments):
            success = await _send_single_message(session, segment, headers)
            
            if not success:
                print(f"Segment {i+1}/{total_segments} Segment message sending failed")
                return
            
            if i < total_segments - 1:
                await asyncio.sleep(0.5)
    
    if total_segments > 1:
        print(f"All {total_segments} segments sent")
    else:
        print("Message sent successfully!")