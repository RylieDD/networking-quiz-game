import asyncio
import sys
from libclient import AsyncMessage

async def main(host, port, loop):
    reader, writer = await asyncio.open_connection(host, port)
    message = AsyncMessage(reader, writer, loop)

    #Start receiving and processing messages
    loop.create_task(message.receive_messages())
    #await asyncio.sleep(0.1)
    loop.create_task(message.process_messages())
    #await message.process_messages()

    #Send initial "connect" action
    await message.send_message({"action": "connect"})
    print("Sent 'connect' to the server.")

    #Wait for the response from server
    while not message.message_queue:
        await asyncio.sleep(0.1)  # Wait for the server response
    connect_response = message.message_queue.popleft()
    if connect_response.get("result") == "Connected to the quiz game.":
        print(connect_response["result"])

    await message.handle_user_inputs()

if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("Usage: python client.py -i <host> -p <port>")
        sys.exit(1)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(sys.argv[2], int(sys.argv[4]), loop))


