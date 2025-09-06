#!/usr/bin/env python3
"""
Add more test data to Module B for better search results.
"""

import asyncio
import base64
import httpx

async def add_test_data():
    """Add comprehensive Linux documentation to Module B."""
    
    documents = [
        {
            "filename": "memory_management.txt",
            "content": """Linux Memory Management Guide

Memory Commands:
- free -h: Display memory usage in human-readable format
- cat /proc/meminfo: Detailed memory information
- vmstat: Virtual memory statistics
- top: Real-time memory usage by processes
- htop: Enhanced process and memory viewer
- ps aux --sort=-%mem: Processes sorted by memory usage

Memory Types:
- Physical RAM: Actual hardware memory
- Virtual Memory: RAM + Swap space
- Swap: Disk space used as memory extension
- Buffers: Temporary storage for I/O operations
- Cache: Recently accessed files stored in memory

Memory Optimization:
- Clear caches: sync && echo 3 > /proc/sys/vm/drop_caches
- Adjust swappiness: sysctl vm.swappiness=10
- Monitor memory leaks: valgrind --leak-check=yes program
- Check memory limits: ulimit -m"""
        },
        {
            "filename": "process_management.txt", 
            "content": """Linux Process Management Guide

Process Commands:
- ps aux: List all running processes
- ps -ef: Full format process listing
- pstree: Display processes in tree format
- top: Real-time process monitoring
- htop: Interactive process viewer
- jobs: List active jobs in current shell
- nohup: Run commands immune to hangups

Process Control:
- kill PID: Terminate process by ID
- kill -9 PID: Force kill process
- killall name: Kill processes by name
- pkill pattern: Kill processes matching pattern
- bg: Put job in background
- fg: Bring job to foreground
- Ctrl+Z: Suspend current process

Process Priorities:
- nice -n 10 command: Run with lower priority
- renice 5 PID: Change process priority
- ionice: Set I/O scheduling priority

System Services:
- systemctl start service: Start service
- systemctl stop service: Stop service
- systemctl restart service: Restart service
- systemctl status service: Check service status
- systemctl enable service: Enable at boot
- systemctl disable service: Disable at boot"""
        },
        {
            "filename": "backup_strategies.txt",
            "content": """Linux Backup Strategies Guide

Backup Tools:
- rsync: Efficient file synchronization
- tar: Archive creation and extraction
- dd: Disk cloning and imaging
- cp: Simple file copying
- scp: Secure copy over network
- rdiff-backup: Incremental backups with history

Rsync Examples:
- rsync -av source/ dest/: Archive mode with verbose output
- rsync -avz source/ user@host:dest/: Compress during transfer
- rsync --dry-run: Test without making changes
- rsync --delete: Remove files not in source
- rsync --exclude='*.log': Exclude log files
- rsync --progress: Show transfer progress

Backup Types:
- Full Backup: Complete copy of all data
- Incremental: Only changed files since last backup
- Differential: Changed files since last full backup
- Snapshot: Point-in-time copy using filesystem features

Automation:
- crontab -e: Edit scheduled tasks
- 0 2 * * * /backup/script.sh: Run daily at 2 AM
- logrotate: Automatic log file rotation
- systemd timers: Modern alternative to cron

Best Practices:
- Test restore procedures regularly
- Store backups in multiple locations
- Encrypt sensitive backup data
- Monitor backup completion and errors
- Document backup and restore procedures"""
        },
        {
            "filename": "system_monitoring.txt",
            "content": """Linux System Monitoring Guide

System Information:
- uname -a: System information
- lscpu: CPU information
- lsmem: Memory information
- lsblk: Block device information
- lspci: PCI device information
- lsusb: USB device information
- dmidecode: Hardware information from BIOS

Performance Monitoring:
- iostat: I/O statistics
- sar: System activity reporter
- mpstat: CPU usage statistics
- pidstat: Process statistics
- iotop: I/O usage by process
- nethogs: Network usage by process

Resource Usage:
- df -h: Disk space usage
- du -sh: Directory size
- free -h: Memory usage
- uptime: System load and uptime
- w: Who is logged in and what they're doing
- last: Recent login history

Log Analysis:
- journalctl: SystemD journal logs
- tail -f /var/log/syslog: Follow system log
- grep ERROR /var/log/*: Search for errors
- logwatch: Automated log analysis
- rsyslog: System logging daemon configuration

Network Monitoring:
- netstat -tulpn: Network connections
- ss -tulpn: Modern netstat replacement
- iftop: Network bandwidth usage
- tcpdump: Network packet capture
- wireshark: Network protocol analyzer"""
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Adding comprehensive test data to Module B...")
        
        for doc in documents:
            try:
                base64_content = base64.b64encode(doc["content"].encode()).decode()
                
                upload_data = {
                    "files": [base64_content],
                    "metadata": {
                        "source": doc["filename"],
                        "type": "txt",
                        "category": "linux_administration"
                    }
                }
                
                response = await client.post(
                    "http://localhost:8002/upload",
                    json=upload_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Uploaded {doc['filename']}: {result['total_chunks']} chunks")
                else:
                    print(f"❌ Failed to upload {doc['filename']}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error uploading {doc['filename']}: {e}")
        
        print("Test data upload completed!")

if __name__ == "__main__":
    asyncio.run(add_test_data())