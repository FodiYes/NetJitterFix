import asyncio
import re
import numpy as np
import time
import statistics
import platform
import subprocess
from typing import Tuple, List, Dict, Callable, Optional


class JitterChecker:
    def __init__(self):
        self.target = "8.8.8.8"
        self.ping_count = 100
        self.timeout = 1000
        self._process = None
        self._cancel_requested = False
        self.os_type = platform.system()
    
    def set_target(self, target: str) -> None:
        self.target = target
    
    def set_ping_count(self, count: int) -> None:
        self.ping_count = count
    
    async def _run_ping(self, count=100):
        try:
            if self.os_type == "Windows":
                cmd = ["ping", "-n", str(count), self.target]
            else:
                cmd = ["ping", "-c", str(count), self.target]
            
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout_data, stderr_data = await self._process.communicate()
            
            for encoding in ['cp866', 'cp1251', 'cp1252', 'utf-8']:
                try:
                    stdout = stdout_data.decode(encoding, errors='ignore')
                    stderr = stderr_data.decode(encoding, errors='ignore')
                    return stdout, stderr
                except UnicodeDecodeError:
                    continue
                
            stdout = stdout_data.decode('utf-8', errors='ignore')
            stderr = stderr_data.decode('utf-8', errors='ignore')
            return stdout, stderr
            
        except Exception as e:
            print(f"Error running ping: {e}")
            return None, None
    
    async def _async_check_jitter(self, progress_callback: Optional[Callable[[int], None]] = None) -> Tuple[float, List[int], List[float]]:
        self._cancel_requested = False
        ping_times = []
        
        if self.ping_count <= 0:
            self.ping_count = 1
        
        try:
            if self.os_type == "Windows":
                cmd = ["ping", "-n", str(self.ping_count), self.target]
            else:
                cmd = ["ping", "-c", str(self.ping_count), self.target]
            
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            line_count = 0
            ping_pattern = re.compile(r"(time|время)[=<:]\s*(\d+)\s*(ms|мс)", re.IGNORECASE)
            timeout_pattern = re.compile(r"(timeout|timed out|превышен|истекло)", re.IGNORECASE)
            
            while True:
                if self._cancel_requested:
                    self._process.terminate()
                    return 0.0, [], []
                    
                line_bytes = await self._process.stdout.readline()
                if not line_bytes:
                    break
                
                for encoding in ['cp866', 'cp1251', 'cp1252', 'utf-8']:
                    try:
                        line = line_bytes.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    continue
                
                match = ping_pattern.search(line)
                if match:
                    ping_time = int(match.group(2))
                    ping_times.append(ping_time)
                    line_count += 1
                    
                    if progress_callback:
                        progress = min(100, int((line_count / self.ping_count) * 100))
                        progress_callback(progress)
                
                elif timeout_pattern.search(line):
                    line_count += 1
                    if progress_callback:
                        progress = min(100, int((line_count / self.ping_count) * 100))
                        progress_callback(progress)
            
            await self._process.wait()
            
        except Exception as e:
            print(f"Error during ping execution: {e}")
            if self._process:
                self._process.terminate()
            return 0.0, [], []
        
        if not ping_times:
            return 0.0, [], []
        
        time_stamps = np.linspace(0, len(ping_times) - 1, len(ping_times))
        
        jitter = np.std(ping_times) if len(ping_times) > 1 else 0.0
        
        return jitter, ping_times, time_stamps
    
    def check_jitter(self, progress_callback: Optional[Callable[[int], None]] = None) -> Tuple[float, List[int], List[float]]:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self._async_check_jitter(progress_callback))
            
            loop.close()
            
            return result
        except Exception as e:
            print(f"Error in check_jitter: {e}")
            return 0.0, [], []
    
    def cancel_check(self) -> None:
        self._cancel_requested = True
        if self._process:
            try:
                self._process.terminate()
            except:
                pass
    
    def get_detailed_network_stats(self) -> Dict:
        jitter, ping_times, _ = self.check_jitter()
        
        if not ping_times:
            return {
                "jitter": 0.0,
                "min_ping": 0,
                "max_ping": 0,
                "avg_ping": 0.0,
                "packet_loss": 100.0
            }
        
        received_packets = len(ping_times)
        packet_loss = 100 - (received_packets / self.ping_count * 100)
        
        return {
            "jitter": round(jitter, 2),
            "min_ping": min(ping_times) if ping_times else 0,
            "max_ping": max(ping_times) if ping_times else 0,
            "avg_ping": round(sum(ping_times) / len(ping_times), 2) if ping_times else 0.0,
            "packet_loss": round(packet_loss, 2)
        }
