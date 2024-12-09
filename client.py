import asyncio
import sys
from libclient import Message
import ssl

#Application of TLS using the provided cert.pem
def create_tls_context():
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations("cert.pem") 
    context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 
    return context


async def main(host, port, loop):
    tls_context = create_tls_context()
    writer = None
    try:
        reader, writer = await asyncio.open_connection(host, port, ssl=tls_context)
        message = Message(reader, writer, loop)

        #Handles the receiving and processing messages
        loop.create_task(message.receive_messages())
        loop.create_task(message.process_messages())

        #Sends the initial "connect" action
        await message.send_message({"action": "connect"})
        print("Sent 'connect' to the server.")

        #Waits for the response from server
        while not message.message_queue:
            await asyncio.sleep(0.1)
        connect_response = message.message_queue.popleft()
        if connect_response.get("result") == "Connected to the quiz game.":
            print(connect_response["result"])
        
        #Handles the processing of user inputs
        await message.handle_user_inputs()
    except ConnectionResetError:
        print("The server disconnected unexpectedly. Exiting.")
        for task in asyncio.Task.all_tasks(loop):
            task.cancel()
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Shutting down client...")
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
        print("KeyboardInterrupt detected in the main loop. Exiting.")
        tasks = asyncio.Task.all_tasks(loop)
        for task in tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    finally:
        loop.close()
