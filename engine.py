import os
import asyncio
import threading

class StorageEngine:
    def __init__(self):
        self._state = {}
        self.log_lock = threading.Lock()
        
    def append_log(self, operation, key, value=None):
        with self.log_lock:
            with open("log.txt", "a") as log:
                log.write(f"{operation} {key} {value}\n")
        
    async def set(self, key, value):
        self._state[key] = value
        
        await asyncio.to_thread(self.append_log, "SET", key, value)
        return "OK."
        
    def get(self, key):
        if key in self._state:
            return self._state.get(key)
        else:
            return "None"
        
    async def delete(self, key):
        if key in self._state:
            self._state.pop(key)
            
            await asyncio.to_thread(self.append_log, "DEL", key)
            return "OK."
        return "Key not found."
        
    async def mset(self, pairs_string):
        pairs = pairs_string.split(" ")
        if len(pairs) % 2 != 0:
            return("Missing value for last key.")
            
        for i in range(0, len(pairs), 2):
            await self.set(pairs[i], pairs[i+1])
        return "OK."
            
    async def mget(self, keys_string):
        values = []
        keys = keys_string.split(" ")
        for key in keys:
            values.append(self.get(key))
        return " ".join(values)
        
    def get_all_data(self):
        return self._state.copy()
        
    def load_from_log(self, file):
        try:
            with open("log.txt", "r") as log:
                for line in log:
                    parts = line.strip().split(" ", 2)
                    if not parts or parts == [""]:
                        continue
                    
                    command = parts[0].upper()
                    
                    if command == "SET":
                        key, value = parts[1], parts[2]
                        self._state[key] = value
                    elif command == "DEL":
                        key = parts[1]
                        self._state.pop(key, None)
            return True
        except FileNotFoundError:
            with open("log.txt", "w") as file:
                file.write("")
                return False
                
    def compact_logs(self, file):
        with open("log.tmp", "w") as log:
            for key, value in self._state.items():
                log.write(f"SET {key} {value}\n")
        os.replace("log.tmp", "log.txt")
            
        return "Logs compacted."
