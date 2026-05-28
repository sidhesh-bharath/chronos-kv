import asyncio
from engine import StorageEngine

storage = StorageEngine()

async def handle_client(reader, writer):
    client_address = writer.get_extra_info("peername")
    print(f"New connection: {client_address} has connected.")
    
    writer.write(f"Connected to Redis Clone as {client_address}.")
    await writer.drain()
    
    try:
        while True:            
            command_bytes = await reader.readline()
            
            if not command_bytes:
                print(f"Disconnect: Client {client_address} closed the connection.")
                break
            
            command = command_bytes.decode("utf-8").strip()
            parts = command.split(" ", 2)
            
            if parts[0].upper() == "SET":
                result = storage.set(parts[1], parts[2])
                writer.write(result.encode("utf-8"))
            elif parts[0].upper() == "GET":
                result = storage.get(parts[1])
                writer.write(result.encode("utf-8"))
            elif parts[0].upper() == "DEL":
                result = storage.delete(parts[1])
                writer.write(result.encode("utf-8"))
            else:
                writer.write("Invalid Command.\n".encode())
                
            await writer.drain()
            
    except asyncio.CancelledError:
        print(f"Task cancelled by client {client_address}")
    except Exception as e:
        print(f"Error occured: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
            
async def main():
    log_status = storage.load_from_log("log.txt")
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8888)
    
    server_address = server.sockets[0].getsockname()
    print(f"Server running on {server_address}")
    if log_status:
        print("Recovered storage from log successfully")
    else:
        print("No log file found or error occured during log recovery. Proceeding with a fresh storage instance.")
    
    async with server:
        await server.serve_forever()
        
asyncio.run(main())
