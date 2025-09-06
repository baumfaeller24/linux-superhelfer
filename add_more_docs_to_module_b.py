#!/usr/bin/env python3
"""
Add more comprehensive documentation to Module B for better testing.
"""

import asyncio
import base64
import httpx

async def add_comprehensive_docs():
    """Add comprehensive Linux administration documentation."""
    
    module_b_url = "http://localhost:8002"
    
    # Comprehensive documentation sets
    docs = [
        {
            "filename": "system_monitoring_guide.txt",
            "content": """System Monitoring and Performance Guide

Memory Management:
- free -h: Display memory usage in human-readable format
- vmstat 1 5: Show virtual memory statistics every second for 5 iterations
- cat /proc/meminfo: Detailed memory information from kernel
- ps aux --sort=-%mem: List processes sorted by memory usage
- top -o %MEM: Interactive process viewer sorted by memory
- htop: Enhanced interactive process and system monitor
- sar -r 1 10: System activity reporter for memory usage
- pmap -d PID: Show memory map of a specific process

Process Management:
- ps aux: Show all running processes with detailed information
- ps -ef: Alternative process listing format
- pstree: Display processes in tree format showing parent-child relationships
- jobs: Show active jobs in current shell session
- nohup command &: Run command immune to hangups
- kill -TERM PID: Send termination signal to process
- kill -KILL PID: Force kill process (use as last resort)
- killall process_name: Kill all processes with given name
- pkill -f pattern: Kill processes matching pattern
- nice -n 19 command: Start command with lowest priority
- renice -n 10 -p PID: Change priority of running process

System Services:
- systemctl status service_name: Check service status and recent logs
- systemctl start/stop/restart service_name: Control service state
- systemctl enable/disable service_name: Configure service autostart
- systemctl list-units --type=service: List all services
- systemctl list-units --failed: Show failed services only
- systemctl daemon-reload: Reload systemd configuration
- service --status-all: Legacy service status (SysV init)
- chkconfig --list: Legacy service configuration (older systems)"""
        },
        {
            "filename": "storage_management_guide.txt", 
            "content": """Storage and Filesystem Management Guide

Disk Space Analysis:
- df -h: Show filesystem disk space usage in human-readable format
- df -i: Show inode usage for filesystems
- du -sh directory/: Show total size of directory
- du -h --max-depth=1 directory/: Show size of subdirectories one level deep
- ncdu: Interactive disk usage analyzer with navigation
- find /path -type f -size +100M: Find files larger than 100MB
- find /path -type f -mtime +30: Find files older than 30 days
- lsof +L1: Find deleted files still held open by processes
- lsblk: List block devices in tree format
- fdisk -l: List all disk partitions
- parted -l: Alternative partition listing tool

Filesystem Operations:
- mount /dev/device /mount/point: Mount filesystem
- umount /mount/point: Unmount filesystem
- mount -o remount,rw /: Remount root filesystem as read-write
- fsck /dev/device: Check and repair filesystem
- tune2fs -l /dev/device: Show filesystem parameters
- resize2fs /dev/device: Resize ext2/3/4 filesystem
- xfs_growfs /mount/point: Grow XFS filesystem
- mkfs.ext4 /dev/device: Create ext4 filesystem
- mkfs.xfs /dev/device: Create XFS filesystem

Archive and Compression:
- tar -czf archive.tar.gz directory/: Create compressed archive
- tar -xzf archive.tar.gz: Extract compressed archive
- tar -tzf archive.tar.gz: List contents of archive
- zip -r archive.zip directory/: Create ZIP archive
- unzip archive.zip: Extract ZIP archive
- gzip file: Compress file with gzip
- gunzip file.gz: Decompress gzip file
- 7z a archive.7z directory/: Create 7-Zip archive"""
        },
        {
            "filename": "network_administration_guide.txt",
            "content": """Network Administration and Troubleshooting Guide

Network Configuration:
- ip addr show: Display network interface information
- ip route show: Show routing table
- ifconfig: Legacy network interface configuration
- netstat -tulpn: Show listening ports and connections
- ss -tulpn: Modern replacement for netstat
- lsof -i: Show network connections by process
- iptables -L: List firewall rules
- ufw status: Ubuntu firewall status
- systemctl status networking: Check network service status
- nmcli device status: NetworkManager device status
- iwconfig: Wireless interface configuration
- ping -c 4 hostname: Test network connectivity
- traceroute hostname: Trace network path to destination
- nslookup hostname: DNS lookup utility
- dig hostname: Advanced DNS lookup tool

Network Monitoring:
- iftop: Real-time network bandwidth usage by connection
- nethogs: Network bandwidth usage by process
- nload: Network interface bandwidth monitoring
- tcpdump -i interface: Packet capture and analysis
- wireshark: Graphical network protocol analyzer
- netstat -i: Network interface statistics
- cat /proc/net/dev: Network interface statistics from kernel
- sar -n DEV 1 10: Network interface statistics over time

Firewall Management:
- iptables -A INPUT -p tcp --dport 22 -j ACCEPT: Allow SSH
- iptables -A INPUT -j DROP: Drop all other input
- iptables-save > /etc/iptables/rules.v4: Save iptables rules
- ufw allow 22/tcp: Allow SSH through Ubuntu firewall
- ufw deny 80/tcp: Block HTTP through Ubuntu firewall
- firewall-cmd --list-all: List firewalld configuration (CentOS/RHEL)"""
        },
        {
            "filename": "security_hardening_guide.txt",
            "content": """Security Hardening and User Management Guide

User Account Management:
- useradd -m -s /bin/bash username: Create user with home directory
- usermod -aG sudo username: Add user to sudo group
- passwd username: Change user password
- chage -l username: Show password aging information
- userdel -r username: Delete user and home directory
- groups username: Show groups user belongs to
- id username: Show user ID and group information
- who: Show currently logged in users
- last: Show login history
- lastlog: Show last login for all users
- w: Show who is logged in and what they're doing

File Permissions and Security:
- chmod 755 file: Set file permissions (rwxr-xr-x)
- chmod u+x file: Add execute permission for owner
- chown user:group file: Change file ownership
- chattr +i file: Make file immutable
- lsattr file: List file attributes
- find /path -perm 777: Find files with 777 permissions
- find /path -type f -perm /u+s: Find SUID files
- umask 022: Set default file creation permissions

System Security:
- sudo -l: List sudo privileges for current user
- visudo: Edit sudo configuration safely
- fail2ban-client status: Check fail2ban status
- aureport: Generate audit reports (if auditd installed)
- rkhunter --check: Run rootkit hunter scan
- chkrootkit: Alternative rootkit detection tool
- lynis audit system: Comprehensive security audit
- ss -tulpn | grep :22: Check if SSH is listening"""
        },
        {
            "filename": "backup_recovery_guide.txt",
            "content": """Backup and Recovery Strategies Guide

Rsync Backup Strategies:
- rsync -av source/ destination/: Archive mode with verbose output
- rsync -av --delete source/ destination/: Sync and delete extra files
- rsync -av --dry-run source/ destination/: Test sync without changes
- rsync -av --exclude='*.tmp' source/ destination/: Exclude temporary files
- rsync -av --include='*.conf' --exclude='*' source/ destination/: Include only config files
- rsync -av -e ssh source/ user@host:/destination/: Sync over SSH
- rsync -av --progress source/ destination/: Show progress during sync
- rsync -av --bwlimit=1000 source/ destination/: Limit bandwidth to 1MB/s
- rsync -av --backup --backup-dir=../backup-$(date +%Y%m%d) source/ destination/: Keep backups

Database Backup:
- mysqldump -u user -p database > backup.sql: MySQL database backup
- pg_dump -U user database > backup.sql: PostgreSQL database backup
- mongodump --db database --out /backup/path: MongoDB backup
- sqlite3 database.db .dump > backup.sql: SQLite database backup

System Backup:
- tar -czf system-backup-$(date +%Y%m%d).tar.gz /etc /home /var/log: System backup
- dd if=/dev/sda of=/backup/disk-image.img bs=4M: Disk image backup
- fsarchiver savefs /backup/filesystem.fsa /dev/sda1: Filesystem backup
- rsnapshot daily: Automated snapshot backups (if configured)

Recovery Operations:
- tar -xzf backup.tar.gz -C /restore/path: Restore from tar archive
- mysql -u user -p database < backup.sql: Restore MySQL database
- dd if=/backup/disk-image.img of=/dev/sda bs=4M: Restore disk image
- testdisk: Interactive partition and file recovery tool
- photorec: File recovery tool for deleted files"""
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("📚 Adding comprehensive documentation to Module B...")
        
        for doc in docs:
            try:
                # Encode content
                base64_content = base64.b64encode(doc["content"].encode()).decode()
                
                # Upload document
                upload_data = {
                    "files": [base64_content],
                    "metadata": {
                        "source": doc["filename"],
                        "type": "txt",
                        "category": "linux_administration",
                        "description": f"Comprehensive guide: {doc['filename']}"
                    }
                }
                
                response = await client.post(
                    f"{module_b_url}/upload",
                    json=upload_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Uploaded {doc['filename']}: {result['total_chunks']} chunks")
                else:
                    print(f"   ❌ Failed to upload {doc['filename']}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error uploading {doc['filename']}: {e}")
        
        # Check final status
        try:
            status_response = await client.get(f"{module_b_url}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                total_docs = status_data.get("components", {}).get("vector_store", {}).get("total_documents", 0)
                print(f"\n📊 Total documents in knowledge base: {total_docs}")
            
        except Exception as e:
            print(f"   ⚠️ Could not get final status: {e}")

if __name__ == "__main__":
    asyncio.run(add_comprehensive_docs())