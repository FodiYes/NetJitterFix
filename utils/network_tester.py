import asyncio
import time
import statistics
from PyQt5.QtCore import QObject, pyqtSignal
import platform

class NetworkTester(QObject):
    test_complete = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.pre_test_results = {}
        self.post_test_results = {}
        self.os_type = platform.system()
        
    async def run_pre_test(self):
        """Run network tests before optimization"""
        results = await self.run_network_tests()
        self.pre_test_results = results
        self.test_complete.emit(results)
        return results
    
    async def run_post_test(self):
        """Run network tests after optimization"""
        results = await self.run_network_tests()
        self.post_test_results = results
        self.test_complete.emit(results)
        return results
    
    async def run_network_tests(self):
        """Run comprehensive network tests"""
        results = {}
        try:
            results['packet_loss'] = float(await self.test_packet_loss() or 0)
            results['jitter'] = float(await self.test_jitter() or 0)
            results['latency'] = float(await self.test_latency() or 0)
            results['bandwidth'] = float(await self.test_bandwidth() or 0)
        except Exception as e:
            print(f"Error in network tests: {e}")
            results = {
                'packet_loss': 0.0,
                'jitter': 0.0,
                'latency': 0.0,
                'bandwidth': 0.0
            }
        return results
    
    async def run_ping(self, count=1, size=None):
        """Run ping command asynchronously"""
        try:
            if self.os_type == "Windows":
                cmd = ["ping", "-n", str(count), "8.8.8.8"]
                if size:
                    cmd.extend(["-l", str(size)])
            else:
                cmd = ["ping", "-c", str(count), "8.8.8.8"]
                if size:
                    cmd.extend(["-s", str(size)])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout_data, stderr_data = await process.communicate()
            
            try:
                stdout = stdout_data.decode('cp866', errors='ignore')
                stderr = stderr_data.decode('cp866', errors='ignore')
            except:
                try:
                    stdout = stdout_data.decode('cp1251', errors='ignore')
                    stderr = stderr_data.decode('cp1251', errors='ignore')
                except:
                    stdout = stdout_data.decode('utf-8', errors='ignore')
                    stderr = stderr_data.decode('utf-8', errors='ignore')
                
            return stdout, stderr
            
        except Exception as e:
            print(f"Error running ping: {e}")
            return None, None
    
    async def test_packet_loss(self, packets=10):
        """Test packet loss rate"""
        try:
            stdout, _ = await self.run_ping(count=packets)
            if not stdout:
                return 0.0
                
            sent = packets
            received = 0
            
            # Parse ping output
            if self.os_type == "Windows":
                for line in stdout.split('\n'):
                    if "bytes=" in line:
                        received += 1
            else:
                if "packets transmitted" in stdout:
                    stats = stdout.split('\n')[-2]
                    received = int(stats.split(',')[1].split()[0])
            
            loss_rate = ((sent - received) / sent) * 100
            return loss_rate
            
        except Exception as e:
            print(f"Error in packet loss test: {e}")
            return 0.0
    
    async def test_jitter(self, samples=10):
        """Test network jitter"""
        try:
            stdout, _ = await self.run_ping(count=samples)
            if not stdout:
                return 0.0
                
            latencies = []
            
            # Parse ping output
            for line in stdout.split('\n'):
                if "time=" in line or "время=" in line:
                    try:
                        if self.os_type == "Windows":
                            time_str = line.split("время=")[-1].split("мс")[0].strip()
                            time_ms = float(time_str)
                        else:
                            time_str = line.split("time=")[-1].split("ms")[0].strip()
                            time_ms = float(time_str)
                        latencies.append(time_ms)
                    except:
                        continue
            
            # Calculate jitter as standard deviation of latencies
            if latencies:
                jitter = statistics.stdev(latencies)
                return jitter
            return 0.0
            
        except Exception as e:
            print(f"Error in jitter test: {e}")
            return 0.0
    
    async def test_latency(self, samples=5):
        """Test network latency"""
        try:
            stdout, _ = await self.run_ping(count=samples)
            if not stdout:
                return 0.0
                
            latencies = []
            
            # Parse ping output
            for line in stdout.split('\n'):
                if "time=" in line or "время=" in line:
                    try:
                        if self.os_type == "Windows":
                            time_str = line.split("время=")[-1].split("мс")[0].strip()
                            time_ms = float(time_str)
                        else:
                            time_str = line.split("time=")[-1].split("ms")[0].strip()
                            time_ms = float(time_str)
                        latencies.append(time_ms)
                    except:
                        continue
            
            if latencies:
                avg_latency = statistics.mean(latencies)
                return avg_latency
            return 0.0
            
        except Exception as e:
            print(f"Error in latency test: {e}")
            return 0.0
    
    async def test_bandwidth(self, packets=20):
        """Test network bandwidth"""
        try:
            # Use large packets for bandwidth estimation
            stdout, _ = await self.run_ping(count=packets, size=1400)
            if not stdout:
                return 0.0
                
            times = []
            
            # Parse ping output
            for line in stdout.split('\n'):
                if "time=" in line or "время=" in line:
                    try:
                        if self.os_type == "Windows":
                            time_str = line.split("время=")[-1].split("мс")[0].strip()
                            time_ms = float(time_str)
                        else:
                            time_str = line.split("time=")[-1].split("ms")[0].strip()
                            time_ms = float(time_str)
                        times.append(time_ms)
                    except:
                        continue
            
            if times:
                avg_time = statistics.mean(times)
                # Rough bandwidth estimation in Mbps
                bandwidth = (1400 * 8) / (avg_time / 1000) / 1000000
                return bandwidth
            
            return 0.0
            
        except Exception as e:
            print(f"Error in bandwidth test: {e}")
            return 0.0
    
    def get_comparison(self):
        """Compare pre and post optimization results"""
        if not self.pre_test_results or not self.post_test_results:
            return None
            
        comparison = {}
        for metric in self.pre_test_results.keys():
            if self.pre_test_results[metric] and self.post_test_results[metric]:
                improvement = ((self.pre_test_results[metric] - self.post_test_results[metric]) 
                             / self.pre_test_results[metric] * 100)
                comparison[metric] = improvement
                
        return comparison
