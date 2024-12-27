import asyncio
import subprocess
import platform
import time
import re

class NetworkOptimizer:
    def __init__(self):
        self.os_type = platform.system()
        self.original_settings = {
            'mtu': None,
            'tcp_udp': {},
            'buffer': {}
        }
        self.current_settings = {}
        
    async def optimize_mtu(self):
        """Optimize MTU size for better network performance"""
        try:
            # Store original MTU before optimization
            if self.os_type == "Windows":
                result = subprocess.run(["netsh", "interface", "ipv4", "show", "subinterface"], 
                                     capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if "Ethernet" in line:
                        try:
                            # Используем регулярное выражение для поиска числа в конце строки
                            mtu_match = re.search(r'\d+$', line.strip())
                            if mtu_match:
                                self.original_settings['mtu'] = int(mtu_match.group())
                                break
                        except ValueError:
                            continue
            
            # Test different MTU sizes
            mtu_sizes = [1500, 1492, 1472, 1452, 1442]
            optimal_mtu = 1500
            min_latency = float('inf')
            
            for mtu in mtu_sizes:
                # Set MTU size using OS-specific commands
                if self.os_type == "Windows":
                    # Получаем имя интерфейса
                    interfaces = subprocess.run(["netsh", "interface", "ipv4", "show", "interfaces"], 
                                             capture_output=True, text=True)
                    interface_id = None
                    for line in interfaces.stdout.split('\n'):
                        if "Ethernet" in line:
                            try:
                                interface_id = line.split()[0]
                                break
                            except IndexError:
                                continue
                    
                    if interface_id:
                        subprocess.run(["netsh", "interface", "ipv4", "set", "subinterface", 
                                      interface_id, f"mtu={mtu}", "store=persistent"])
                
                # Test latency with current MTU
                await asyncio.sleep(1)  # Даем время на применение настроек
                latency = await self.test_latency()
                if latency and latency < min_latency:
                    min_latency = latency
                    optimal_mtu = mtu
            
            # Set the optimal MTU
            return optimal_mtu
            
        except Exception as e:
            print(f"Error in MTU optimization: {e}")
            return None
    
    async def optimize_tcp_udp(self):
        """Optimize TCP/UDP parameters"""
        try:
            # Store original settings
            if self.os_type == "Windows":
                result = subprocess.run(["netsh", "int", "tcp", "show", "global"], 
                                     capture_output=True, text=True)
                self.original_settings['tcp_udp'] = result.stdout
                
                # Optimize settings for lower jitter
                try:
                    # Настраиваем TCP параметры
                    subprocess.run(["netsh", "int", "tcp", "set", "global", "autotuninglevel=restricted"])
                    subprocess.run(["netsh", "int", "tcp", "set", "global", "initialRto=1500"])
                    # Дополнительные оптимизации через реестр
                    subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", 
                                  "/v", "TcpAckFrequency", "/t", "REG_DWORD", "/d", "1", "/f"])
                    subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", 
                                  "/v", "TCPNoDelay", "/t", "REG_DWORD", "/d", "1", "/f"])
                except Exception as e:
                    print(f"Warning: Some TCP optimizations failed: {e}")
                
        except Exception as e:
            print(f"Error in TCP/UDP optimization: {e}")

    async def manage_buffer(self):
        """Manage network buffers"""
        try:
            if self.os_type == "Windows":
                # Windows buffer settings through registry
                try:
                    # Устанавливаем умеренные размеры буферов
                    subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", 
                                  "/v", "TcpWindowSize", "/t", "REG_DWORD", "/d", "65536", "/f"])
                    subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", 
                                  "/v", "GlobalMaxTcpWindowSize", "/t", "REG_DWORD", "/d", "65536", "/f"])
                    subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\AFD\\Parameters", 
                                  "/v", "DefaultReceiveWindow", "/t", "REG_DWORD", "/d", "65536", "/f"])
                    subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\AFD\\Parameters", 
                                  "/v", "DefaultSendWindow", "/t", "REG_DWORD", "/d", "65536", "/f"])
                except Exception as e:
                    print(f"Warning: Some buffer optimizations failed: {e}")
                
        except Exception as e:
            print(f"Error in buffer management: {e}")
    
    async def test_latency(self):
        """Test network latency"""
        try:
            # Send ICMP packets and measure response time
            ping_count = 5
            total_latency = 0
            successful_pings = 0
            
            for _ in range(ping_count):
                start_time = time.time()
                # Send ping
                if self.os_type == "Windows":
                    result = subprocess.run(["ping", "-n", "1", "8.8.8.8"], 
                                         capture_output=True, text=True)
                    if "bytes=32" in result.stdout:
                        successful_pings += 1
                        total_latency += (time.time() - start_time)
                await asyncio.sleep(0.2)  # Небольшая пауза между пингами
            
            if successful_pings > 0:
                return total_latency / successful_pings * 1000  # Convert to ms
            return None
            
        except Exception as e:
            print(f"Error in latency test: {e}")
            return None

    async def restore_mtu(self):
        """Restore original MTU settings"""
        try:
            if self.original_settings['mtu'] and self.os_type == "Windows":
                # Получаем имя интерфейса
                interfaces = subprocess.run(["netsh", "interface", "ipv4", "show", "interfaces"], 
                                         capture_output=True, text=True)
                interface_id = None
                for line in interfaces.stdout.split('\n'):
                    if "Ethernet" in line:
                        try:
                            interface_id = line.split()[0]
                            break
                        except IndexError:
                            continue
                
                if interface_id:
                    subprocess.run(["netsh", "interface", "ipv4", "set", "subinterface", 
                                  interface_id, f"mtu={self.original_settings['mtu']}", "store=persistent"])
                    return True
            return False
        except Exception as e:
            print(f"Error restoring MTU: {e}")
            return False

    async def restore_tcp_udp(self):
        """Restore original TCP/UDP settings"""
        try:
            if self.os_type == "Windows":
                # Восстанавливаем настройки TCP
                subprocess.run(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"])
                # Сбрасываем настройки реестра
                subprocess.run(["reg", "delete", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", 
                              "/v", "TcpAckFrequency", "/f"], stderr=subprocess.DEVNULL)
                subprocess.run(["reg", "delete", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", 
                              "/v", "TCPNoDelay", "/f"], stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Error restoring TCP/UDP settings: {e}")
            return False

    async def restore_buffer(self):
        """Restore original buffer settings"""
        try:
            if self.os_type == "Windows":
                # Удаляем настройки буферов из реестра
                subprocess.run(["reg", "delete", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", 
                              "/v", "TcpWindowSize", "/f"], stderr=subprocess.DEVNULL)
                subprocess.run(["reg", "delete", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", 
                              "/v", "GlobalMaxTcpWindowSize", "/f"], stderr=subprocess.DEVNULL)
                subprocess.run(["reg", "delete", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\AFD\\Parameters", 
                              "/v", "DefaultReceiveWindow", "/f"], stderr=subprocess.DEVNULL)
                subprocess.run(["reg", "delete", "HKLM\\SYSTEM\\CurrentControlSet\\Services\\AFD\\Parameters", 
                              "/v", "DefaultSendWindow", "/f"], stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Error restoring buffer settings: {e}")
            return False

    def restore_all_settings(self):
        """Restore all original network settings"""
        try:
            asyncio.create_task(self.restore_mtu())
            asyncio.create_task(self.restore_tcp_udp())
            asyncio.create_task(self.restore_buffer())
            return True
        except Exception as e:
            print(f"Error restoring all settings: {e}")
            return False
