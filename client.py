import asyncio
import sys
from libclient import AsyncMessage

async def main(host, port, loop):
    writer = None
    try:
        reader, writer = await asyncio.open_connection(host, port)
        message = AsyncMessage(reader, writer, loop)

        #Start receiving and processing messages
        loop.create_task(message.receive_messages())
        loop.create_task(message.process_messages())

        #Send initial "connect" action
        await message.send_message({"action": "connect"})
        print("Sent 'connect' to the server.")

        #Wait for the response from server
        while not message.message_queue:
            await asyncio.sleep(0.1)
        connect_response = message.message_queue.popleft()
        if connect_response.get("result") == "Connected to the quiz game.":
            print(connect_response["result"])

        await message.handle_user_inputs()
    except ConnectionResetError:
        print("The server disconnected unexpectedly. Exiting.")
        for task in asyncio.Task.all_tasks(loop):
            task.cancel()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Shutting down client...")
        for task in asyncio.Task.all_tasks(loop):
            task.cancel()
    except Exception as e:
        print(f"Unhandled error: {e}")
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python client.py -i <host> -p <port>")
        sys.exit(1)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(sys.argv[2], int(sys.argv[4]), loop))
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected in the main loop. Exiting.")
        tasks = asyncio.Task.all_tasks(loop)
        for task in tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    finally:
        loop.close()
