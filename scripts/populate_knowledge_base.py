#!/usr/bin/env python3
"""
Knowledge Base Population Script
Automatically fills RAG system with comprehensive Linux documentation
"""

import os
import requests
import subprocess
from pathlib import Path
from typing import List, Dict
import time

class KnowledgePopulator:
    def __init__(self, rag_url="http://localhost:8002"):
        self.rag_url = rag_url
        self.docs_dir = Path("knowledge_docs")
        self.docs_dir.mkdir(exist_ok=True)
        
    def create_man_pages(self):
        """Extract essential man pages"""
        essential_commands = [
            'ls', 'grep', 'find', 'awk', 'sed', 'ps', 'top', 'df', 'du',
            'free', 'netstat', 'ss', 'systemctl', 'journalctl', 'crontab',
            'chmod', 'chown', 'tar', 'rsync', 'ssh', 'scp', 'curl', 'wget'
        ]
        
        for cmd in essential_commands:
            try:
                result = subprocess.run(['man', cmd], capture_output=True, text=True)
                if result.returncode == 0:
                    # Clean man page output
                    clean_text = subprocess.run(['col', '-b'], 
                                              input=result.stdout, 
                                              capture_output=True, text=True)
                    
                    with open(self.docs_dir / f"man_{cmd}.txt", 'w') as f:
                        f.write(clean_text.stdout)
                    print(f"✅ Created man page for {cmd}")
                else:
                    print(f"⚠️  Man page not found for {cmd}")
            except Exception as e:
                print(f"❌ Error creating man page for {cmd}: {e}")
    
    def create_cheat_sheets(self):
        """Create comprehensive cheat sheets"""
        
        # System Administration Cheat Sheet
        sysadmin_content = """
Linux System Administration Cheat Sheet

PROCESS MANAGEMENT:
ps aux                    # List all processes
ps -ef                    # Alternative process listing
top                       # Real-time process monitor
htop                      # Enhanced process monitor
kill -9 PID              # Force kill process
killall process_name     # Kill by name
pgrep pattern            # Find process by pattern
pkill pattern            # Kill process by pattern
nohup command &          # Run immune to hangups
jobs                     # List active jobs
bg %1                    # Background job 1
fg %1                    # Foreground job 1

MEMORY MANAGEMENT:
free -h                  # Memory usage human readable
cat /proc/meminfo        # Detailed memory info
vmstat 1 5              # Virtual memory stats
top -o %MEM             # Sort by memory usage
ps aux --sort=-%mem     # Processes by memory
pmap -d PID             # Memory map of process
smem -t                 # Memory usage with totals

DISK MANAGEMENT:
df -h                   # Disk space usage
du -sh *                # Directory sizes
lsblk                   # List block devices
fdisk -l                # List partitions
mount                   # Show mounted filesystems
umount /path            # Unmount filesystem
fsck /dev/device        # Check filesystem

NETWORK COMMANDS:
netstat -tulpn          # Network connections
ss -tulpn               # Modern netstat alternative
iptables -L             # List firewall rules
ip addr show            # Show IP addresses
ip route show           # Show routing table
ping -c 4 host          # Ping 4 times
traceroute host         # Trace route to host
nslookup domain         # DNS lookup
dig domain              # Advanced DNS lookup

SERVICE MANAGEMENT:
systemctl status service    # Check service status
systemctl start service     # Start service
systemctl stop service      # Stop service
systemctl restart service   # Restart service
systemctl enable service    # Enable at boot
systemctl disable service   # Disable at boot
systemctl list-units       # List all units
journalctl -u service      # Service logs
journalctl -f              # Follow logs

FILE OPERATIONS:
find /path -name "*.txt"   # Find files by name
find /path -type f -size +100M  # Find large files
grep -r "pattern" /path    # Recursive search
sed 's/old/new/g' file     # Replace text
awk '{print $1}' file      # Print first column
sort file                  # Sort lines
uniq file                  # Remove duplicates
wc -l file                # Count lines
head -n 10 file           # First 10 lines
tail -f file              # Follow file changes

PERMISSIONS:
chmod 755 file            # Set permissions
chmod +x file             # Make executable
chown user:group file     # Change ownership
chgrp group file          # Change group
umask 022                 # Set default permissions

ARCHIVE OPERATIONS:
tar -czf archive.tar.gz dir/  # Create compressed archive
tar -xzf archive.tar.gz       # Extract compressed archive
zip -r archive.zip dir/       # Create zip archive
unzip archive.zip             # Extract zip archive
rsync -av source/ dest/       # Sync directories

SYSTEM INFORMATION:
uname -a                  # System information
lscpu                     # CPU information
lsmem                     # Memory information
lsusb                     # USB devices
lspci                     # PCI devices
uptime                    # System uptime
who                       # Logged in users
w                         # User activity
id                        # Current user info
groups                    # User groups
"""
        
        with open(self.docs_dir / "linux_sysadmin_cheatsheet.txt", 'w') as f:
            f.write(sysadmin_content)
        
        # Security Cheat Sheet
        security_content = """
Linux Security Administration Guide

USER MANAGEMENT:
useradd username          # Add new user
userdel username          # Delete user
usermod -aG group user    # Add user to group
passwd username           # Change password
chage -l username         # Password aging info
sudo -u user command      # Run as different user
su - username             # Switch user
visudo                    # Edit sudoers file

FILE SECURITY:
chmod 600 file            # Owner read/write only
chmod 644 file            # Owner rw, others read
chmod 755 file            # Owner rwx, others rx
find / -perm -4000        # Find SUID files
find / -perm -2000        # Find SGID files
find / -type f -perm 777  # Find world-writable files
lsattr file               # List file attributes
chattr +i file            # Make file immutable

FIREWALL MANAGEMENT:
iptables -L               # List rules
iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # Allow SSH
iptables -A INPUT -j DROP # Drop all other input
ufw enable                # Enable UFW firewall
ufw allow 22              # Allow SSH through UFW
ufw status                # Check UFW status

PROCESS SECURITY:
ps aux | grep suspicious  # Find suspicious processes
lsof -i                   # List open network connections
netstat -tulpn            # Network connections with PIDs
ss -tulpn                 # Modern netstat alternative
fuser -v /path            # Show processes using file/directory

LOG MONITORING:
tail -f /var/log/auth.log     # Monitor authentication
tail -f /var/log/syslog       # Monitor system log
journalctl -f                 # Follow systemd logs
last                          # Last logins
lastb                         # Failed login attempts
who                           # Currently logged in users

SYSTEM HARDENING:
fail2ban-client status        # Check fail2ban status
lynis audit system            # Security audit
rkhunter --check             # Rootkit hunter
chkrootkit                   # Check for rootkits
aide --check                 # File integrity check

NETWORK SECURITY:
nmap -sS target              # SYN scan
nmap -sV target              # Version detection
tcpdump -i eth0              # Packet capture
wireshark                    # GUI packet analyzer
arp -a                       # ARP table
"""
        
        with open(self.docs_dir / "linux_security_guide.txt", 'w') as f:
            f.write(security_content)
            
        print("✅ Created comprehensive cheat sheets")
    
    def create_troubleshooting_guides(self):
        """Create troubleshooting documentation"""
        
        troubleshooting_content = """
Linux Troubleshooting Guide

SYSTEM PERFORMANCE ISSUES:
Problem: High CPU usage
- Check: top, htop, ps aux --sort=-%cpu
- Solution: Kill resource-heavy processes, check for malware
- Prevention: Monitor with cron jobs, set resource limits

Problem: High memory usage
- Check: free -h, ps aux --sort=-%mem, /proc/meminfo
- Solution: Kill memory-heavy processes, clear cache
- Commands: echo 3 > /proc/sys/vm/drop_caches

Problem: Disk space full
- Check: df -h, du -sh /*, lsof +L1
- Solution: Clean logs, remove old files, expand partition
- Commands: find /var/log -name "*.log" -mtime +30 -delete

NETWORK CONNECTIVITY ISSUES:
Problem: Cannot connect to internet
- Check: ping 8.8.8.8, ip route show, cat /etc/resolv.conf
- Solution: Restart network, check DNS, verify routes
- Commands: systemctl restart networking

Problem: SSH connection refused
- Check: systemctl status ssh, netstat -tulpn | grep 22
- Solution: Start SSH service, check firewall rules
- Commands: systemctl start ssh, ufw allow 22

Problem: Slow network performance
- Check: iftop, nethogs, ss -i
- Solution: Check bandwidth usage, network configuration
- Commands: ethtool eth0, mtr target_host

SERVICE AND APPLICATION ISSUES:
Problem: Service won't start
- Check: systemctl status service, journalctl -u service
- Solution: Check configuration, dependencies, permissions
- Commands: systemctl daemon-reload, systemctl reset-failed

Problem: Application crashes
- Check: dmesg, /var/log/syslog, core dumps
- Solution: Check logs, update software, verify dependencies
- Commands: gdb application core, ldd application

Problem: Permission denied errors
- Check: ls -la, id, groups
- Solution: Fix permissions, add user to group
- Commands: chmod, chown, usermod -aG group user

BOOT AND FILESYSTEM ISSUES:
Problem: System won't boot
- Check: Boot from rescue disk, check /var/log/boot.log
- Solution: Repair GRUB, check filesystem, fix fstab
- Commands: grub-install, fsck, mount -o remount,rw /

Problem: Filesystem corruption
- Check: dmesg, fsck output
- Solution: Unmount and run fsck, restore from backup
- Commands: umount /dev/device, fsck -y /dev/device

Problem: Mount failures
- Check: /etc/fstab, dmesg, lsblk
- Solution: Fix fstab entries, check device names
- Commands: mount -a, blkid, findmnt

COMMON ERROR MESSAGES:
"No space left on device"
- Check: df -h, df -i (inodes)
- Solution: Free space or inodes

"Permission denied"
- Check: ls -la, SELinux context
- Solution: Fix permissions or SELinux labels

"Command not found"
- Check: which command, echo $PATH
- Solution: Install package or fix PATH

"Connection refused"
- Check: Service status, firewall rules
- Solution: Start service, open firewall ports

DIAGNOSTIC COMMANDS:
System Health Check:
uptime                    # System load and uptime
dmesg | tail             # Recent kernel messages
systemctl --failed       # Failed services
df -h                    # Disk usage
free -h                  # Memory usage
top                      # Real-time system stats

Network Diagnostics:
ping -c 4 8.8.8.8        # Internet connectivity
nslookup google.com      # DNS resolution
netstat -tulpn           # Network connections
ss -tulpn                # Modern network connections
iptables -L              # Firewall rules

Process Diagnostics:
ps aux                   # All processes
pstree                   # Process tree
lsof                     # Open files
strace -p PID            # System calls of process
ltrace -p PID            # Library calls of process
"""
        
        with open(self.docs_dir / "linux_troubleshooting_guide.txt", 'w') as f:
            f.write(troubleshooting_content)
            
        print("✅ Created troubleshooting guide")
    
    def upload_documents(self):
        """Upload all documents to RAG system"""
        uploaded_count = 0
        
        for doc_file in self.docs_dir.glob("*.txt"):
            try:
                with open(doc_file, 'r') as f:
                    content = f.read()
                
                files = {'files': (doc_file.name, content, 'text/plain')}
                response = requests.post(f"{self.rag_url}/upload", files=files)
                
                if response.status_code == 200:
                    print(f"✅ Uploaded {doc_file.name}")
                    uploaded_count += 1
                else:
                    print(f"❌ Failed to upload {doc_file.name}: {response.text}")
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error uploading {doc_file.name}: {e}")
        
        return uploaded_count
    
    def populate_all(self):
        """Complete knowledge base population"""
        print("🚀 Starting Knowledge Base Population...")
        
        print("\n1. Creating man pages...")
        self.create_man_pages()
        
        print("\n2. Creating cheat sheets...")
        self.create_cheat_sheets()
        
        print("\n3. Creating troubleshooting guides...")
        self.create_troubleshooting_guides()
        
        print("\n4. Uploading documents to RAG system...")
        uploaded = self.upload_documents()
        
        print(f"\n🎉 Population complete! Uploaded {uploaded} documents")
        
        # Verify upload
        try:
            response = requests.get(f"{self.rag_url}/status")
            if response.status_code == 200:
                status = response.json()
                total_docs = status.get('components', {}).get('vector_store', {}).get('total_documents', 0)
                print(f"📊 Total documents in knowledge base: {total_docs}")
        except Exception as e:
            print(f"⚠️  Could not verify upload: {e}")

if __name__ == "__main__":
    populator = KnowledgePopulator()
    populator.populate_all()