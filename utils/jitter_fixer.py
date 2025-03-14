import subprocess
import ctypes
import os
from typing import List, Dict


class JitterFixer:
    def __init__(self):
        self.fixes_applied = []
        self.fixes_available = {
            "disable_nagle": "Disable Nagle's Algorithm (TCP_NODELAY)",
            "optimize_tcp": "Optimize TCP/IP parameters",
            "qos_priority": "Set QoS priority for games and applications",
            "dns_optimize": "Optimize DNS servers",
            "reset_winsock": "Reset Winsock settings",
            "reset_tcp_ip": "Reset TCP/IP stack",
            "disable_auto_tuning": "Disable TCP auto-tuning",
            "network_throttling": "Disable bandwidth limiting",
            "network_adapter": "Optimize network adapter"
        }
    
    def _is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def check_admin_rights(self) -> bool:
        return self._is_admin()
    
    def run_as_admin(self, command: str) -> subprocess.CompletedProcess:
        if not self._is_admin():
            return subprocess.CompletedProcess(args=command, returncode=1, stdout="Administrator rights required", stderr="")
        
        try:
            process = subprocess.Popen(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=False
            )
            stdout_bytes, stderr_bytes = process.communicate()
            
            stdout = ""
            stderr = ""
            
            for encoding in ['cp866', 'cp1251', 'cp1252', 'utf-8']:
                try:
                    stdout = stdout_bytes.decode(encoding, errors='ignore')
                    break
                except UnicodeDecodeError:
                    continue
            
            for encoding in ['cp866', 'cp1251', 'cp1252', 'utf-8']:
                try:
                    stderr = stderr_bytes.decode(encoding, errors='ignore')
                    break
                except UnicodeDecodeError:
                    continue
            
            return subprocess.CompletedProcess(args=command, returncode=process.returncode, stdout=stdout, stderr=stderr)
        except Exception as e:
            return subprocess.CompletedProcess(args=command, returncode=1, stdout="", stderr=str(e))
    
    def get_available_fixes(self) -> Dict[str, str]:
        return self.fixes_available
    
    def get_applied_fixes(self) -> List[str]:
        return self.fixes_applied
    
    def disable_nagle_algorithm(self) -> bool:
        cmd = 'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces" /v TcpNoDelay /t REG_DWORD /d 1 /f'
        cmd2 = 'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpNoDelay /t REG_DWORD /d 1 /f'
        
        result1 = self.run_as_admin(cmd)
        result2 = self.run_as_admin(cmd2)
        
        if result1.returncode == 0 and result2.returncode == 0:
            self.fixes_applied.append("disable_nagle")
            return True
        return False
    
    def optimize_tcp_settings(self) -> bool:
        commands = [
            'netsh int tcp set global autotuninglevel=normal',
            'netsh int tcp set global congestionprovider=ctcp',
            'netsh int tcp set global ecncapability=enabled',
            'netsh int tcp set global rss=enabled',
            'netsh int tcp set global chimney=disabled',
            'netsh int tcp set global dca=enabled',
            'netsh int tcp set global netdma=enabled',
            'netsh int tcp set global timestamps=disabled',
            'netsh int tcp set global initialRto=2000',
            'netsh int tcp set global rsc=disabled',
            'netsh int tcp set heuristics disabled',
            'netsh int tcp set global fastopen=enabled',
            'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v DefaultTTL /t REG_DWORD /d 64 /f',
            'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpMaxDupAcks /t REG_DWORD /d 2 /f',
            'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v SackOpts /t REG_DWORD /d 1 /f',
            'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v Tcp1323Opts /t REG_DWORD /d 3 /f',
            'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpTimedWaitDelay /t REG_DWORD /d 30 /f'
        ]
        
        success = True
        for cmd in commands:
            result = self.run_as_admin(cmd)
            if result.returncode != 0:
                success = False
        
        if success:
            self.fixes_applied.append("optimize_tcp")
        return success
    
    def set_qos_priority(self) -> bool:
        commands = [
            'reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\Psched" /v NonBestEffortLimit /t REG_DWORD /d 0 /f',
            'reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\Psched" /v TimerResolution /t REG_DWORD /d 1 /f',
            'reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\Psched" /v MaxOutstandingSends /t REG_DWORD /d 8 /f'
        ]
        
        success = True
        for cmd in commands:
            result = self.run_as_admin(cmd)
            if result.returncode != 0:
                success = False
        
        if success:
            self.fixes_applied.append("qos_priority")
        return success
    
    def optimize_dns(self) -> bool:
        commands = [
            'netsh interface ip set dns name="Ethernet" static 1.1.1.1 primary',
            'netsh interface ip add dns name="Ethernet" 8.8.8.8 index=2',
            'netsh interface ip set dns name="Wi-Fi" static 1.1.1.1 primary',
            'netsh interface ip add dns name="Wi-Fi" 8.8.8.8 index=2',
            'ipconfig /flushdns'
        ]
        
        success = True
        for cmd in commands:
            result = self.run_as_admin(cmd)
            if result.returncode != 0:
                success = False
        
        if success:
            self.fixes_applied.append("dns_optimize")
        return success
    
    def reset_winsock(self) -> bool:
        cmd = 'netsh winsock reset'
        result = self.run_as_admin(cmd)
        
        if result.returncode == 0:
            self.fixes_applied.append("reset_winsock")
            return True
        return False
    
    def reset_tcp_ip(self) -> bool:
        cmd = 'netsh int ip reset'
        result = self.run_as_admin(cmd)
        
        if result.returncode == 0:
            self.fixes_applied.append("reset_tcp_ip")
            return True
        return False
    
    def disable_auto_tuning(self) -> bool:
        cmd = 'netsh interface tcp set global autotuninglevel=disabled'
        result = self.run_as_admin(cmd)
        
        if result.returncode == 0:
            self.fixes_applied.append("disable_auto_tuning")
            return True
        return False
    
    def disable_network_throttling(self) -> bool:
        cmd = 'reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v NetworkThrottlingIndex /t REG_DWORD /d 0xffffffff /f'
        result = self.run_as_admin(cmd)
        
        if result.returncode == 0:
            self.fixes_applied.append("network_throttling")
            return True
        return False
    
    def optimize_network_adapter(self) -> bool:
        cmd = 'powershell -Command "& {Get-NetAdapter | ForEach-Object { Set-NetAdapterAdvancedProperty -Name $_.Name -RegistryKeyword \'*InterruptModeration\' -RegistryValue 0; Set-NetAdapterAdvancedProperty -Name $_.Name -RegistryKeyword \'*FlowControl\' -RegistryValue 0; Set-NetAdapterAdvancedProperty -Name $_.Name -RegistryKeyword \'*EEE\' -RegistryValue 0; Set-NetAdapterAdvancedProperty -Name $_.Name -RegistryKeyword \'*PriorityVLANTag\' -RegistryValue 1}}"'
        result = self.run_as_admin(cmd)
        
        if result.returncode == 0:
            self.fixes_applied.append("network_adapter")
            return True
        return False
    
    def apply_fix(self, fix_id: str) -> bool:
        fix_functions = {
            "disable_nagle": self.disable_nagle_algorithm,
            "optimize_tcp": self.optimize_tcp_settings,
            "qos_priority": self.set_qos_priority,
            "dns_optimize": self.optimize_dns,
            "reset_winsock": self.reset_winsock,
            "reset_tcp_ip": self.reset_tcp_ip,
            "disable_auto_tuning": self.disable_auto_tuning,
            "network_throttling": self.disable_network_throttling,
            "network_adapter": self.optimize_network_adapter
        }
        
        if fix_id in fix_functions:
            return fix_functions[fix_id]()
        return False
    
    def apply_all_fixes(self) -> Dict[str, bool]:
        results = {}
        for fix_id in self.fixes_available.keys():
            results[fix_id] = self.apply_fix(fix_id)
        return results
