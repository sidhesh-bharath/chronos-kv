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
        
    async def set(self, key, value=None):
        self._state[key] = value
        
        await asyncio.to_thread(self.append_log, "SET", key, value)
        return "OK.\n"
        
    def get(self, key):
        if key in self._state:
            return f"{self._state.get(key)}\n"
        else:
            return "Key not found.\n"
        
    async def delete(self, key):
        if key in self._state:
            self._state.pop(key)
            
            await asyncio.to_thread(self.append_log, "DEL", key)
            return "OK.\n"
        return "Key not found.\n"
        
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
        with open(file, "w") as log:
            log.write("")
            
        temp = self._state.copy()
        
        for key, value in temp.items():
            self.append_log("SET", key, value)
            
        return "Logs compacted.\n"
