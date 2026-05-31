import os
import asyncio
import authentication
from dotenv import load_dotenv
from engine import StorageEngine

storage = StorageEngine()

if not os.path.exists(".env"):
    with open(".env", "w") as file:
        file.write("")

load_dotenv()

async def handle_request(reader, writer):
    client_address = writer.get_extra_info("peername")
    print(f"New connection: {client_address} has connected.")
    authenticated = False
    
    writer.write(f"Connected to ChronosKV as {client_address}.\n".encode("utf-8"))
    writer.write(f"Please authenticate yourself with command AUTH, if no password exists, AUTH <password> will set the password as <password>.\n".encode("utf-8"))
    await writer.drain()

    try:
        while True:
            command_bytes = await reader.readline()
            
            if not command_bytes:
                print(f"Disconnect: Client {client_address} has disconnected.")
                break
            
            command = command_bytes.decode("utf-8").strip()
            parts = command.split(" ", 2)
            
            if not authenticated:
                if parts[0].upper() == "AUTH":
                    if len(parts) < 2:
                         writer.write("Incorrect Command Usage.\n".encode("utf-8"))
                         await writer.drain()
                         continue
                         
                    load_dotenv()
                         
                    if os.getenv("CHRONOS_KV_HASH") is not None:
                        password_input = command.split(" ", 1)[1]
                        authenticated = authentication.verify_password(password_input)
                        
                        if authenticated:
                            writer.write("Authenticated Successfully.\n".encode("utf-8"))
                            await writer.drain()
                            continue
                        else:
                            writer.write("Incorrect password, try again\n".encode("utf-8"))
                            await writer.drain()
                            continue
                    else:
                        password_input = command.split(" ", 1)[1]
                        writer.write(f"No existing password found, setting {password_input} as password.\n".encode("utf-8"))
                        authentication.hash_password(password_input)
                        authenticated = True
                        continue
                else:
                    writer.write("Please authenticate before proceeding\n".encode("utf-8"))
                    await writer.drain()
                    continue
            
            if parts[0].upper() == "SET":
                if len(parts) < 3:
                    writer.write("Incorrect Command Usage.\n".encode("utf-8"))
                else:
                    result = await storage.set(parts[1], parts[2])
                    writer.write(f"{result}\n".encode("utf-8"))
            elif parts[0].upper() == "GET":
                if len(parts) < 2:
                    writer.write("Incorrect Command Usage.\n".encode("utf-8"))
                else:
                    result = storage.get(parts[1])
                    writer.write(f"{result}\n".encode("utf-8"))
            elif parts[0].upper() == "DEL":
                if len(parts) < 2:
                    writer.write("Incorrect Command Usage.\n".encode("utf-8"))
                else:
                    result = await storage.delete(parts[1])
                    writer.write(f"{result}\n".encode("utf-8"))
            elif parts[0].upper() == "MSET":
                pairs = command.split(" ", 1)
                if len(pairs) < 2 or pairs[1].strip() == "":
                    writer.write("Incorrect Command Usage.\n".encode("utf-8"))
                else:
                    result = await storage.mset(pairs[1])
                    writer.write(f"{result}\n".encode("utf-8"))
            elif parts[0].upper() == "MGET":
                keys = command.split(" ", 1)
                if len(keys) < 2 or keys[1].strip() == "":
                    writer.write("Incorrect Command Usage.\n".encode("utf-8"))
                else:
                    result = await storage.mget(keys[1])
                    writer.write(f"{result}\n".encode("utf-8"))
            else:
                writer.write("Invalid Command.\n".encode("utf-8"))
                
            await writer.drain()
            
    except asyncio.CancelledError:
        print(f"Task cancelled by client {client_address}")
    #except Exception as e:
    #    print(f"Error occured: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
            
async def main():
    log_status = storage.load_from_log("log.txt")
    server = await asyncio.start_server(handle_request, "127.0.0.1", 8888)
    
    server_address = server.sockets[0].getsockname()
    print(f"Server running on {server_address}")
    if log_status:
        storage.compact_logs("log.txt")
        print("Compacted logs and recovered storage successfully.")
    else:
        print("No log file found or error occured during log recovery. Proceeding with a fresh storage instance.")
    
    async with server:
        await server.serve_forever()
        
asyncio.run(main())
