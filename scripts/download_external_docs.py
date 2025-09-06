#!/usr/bin/env python3
"""
External Documentation Downloader
Downloads curated Linux documentation from various sources
"""

import requests
import os
from pathlib import Path
import time

class ExternalDocsDownloader:
    def __init__(self):
        self.docs_dir = Path("external_docs")
        self.docs_dir.mkdir(exist_ok=True)
        
    def download_arch_wiki_pages(self):
        """Download popular Arch Wiki pages"""
        arch_pages = [
            "System_maintenance",
            "Performance_tuning", 
            "Security",
            "Network_configuration",
            "Systemd",
            "Bash",
            "SSH_keys",
            "Cron",
            "Firewall"
        ]
        
        for page in arch_pages:
            try:
                url = f"https://wiki.archlinux.org/title/{page}?action=raw"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(self.docs_dir / f"arch_{page.lower()}.txt", 'w') as f:
                        f.write(response.text)
                    print(f"✅ Downloaded Arch Wiki: {page}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Failed to download {page}: {e}")
    
    def download_ubuntu_docs(self):
        """Download Ubuntu documentation"""
        ubuntu_topics = [
            "server-guide",
            "security-guide", 
            "networking-guide"
        ]
        
        # Note: This would need actual Ubuntu doc URLs
        print("📝 Ubuntu docs would be downloaded from official sources")
    
    def create_devops_guides(self):
        """Create DevOps and containerization guides"""
        
        docker_guide = """
Docker Commands Reference

CONTAINER MANAGEMENT:
docker run -it ubuntu bash     # Run interactive container
docker run -d nginx           # Run detached container
docker ps                     # List running containers
docker ps -a                  # List all containers
docker stop container_id      # Stop container
docker start container_id     # Start container
docker restart container_id   # Restart container
docker rm container_id        # Remove container
docker logs container_id      # View container logs
docker exec -it container_id bash  # Execute command in container

IMAGE MANAGEMENT:
docker images                 # List images
docker pull image:tag         # Pull image
docker build -t name .        # Build image from Dockerfile
docker rmi image_id           # Remove image
docker tag source target      # Tag image
docker push image:tag         # Push to registry

DOCKER COMPOSE:
docker-compose up -d          # Start services in background
docker-compose down           # Stop and remove services
docker-compose logs service   # View service logs
docker-compose exec service bash  # Execute in service
docker-compose build          # Build services
docker-compose ps             # List services

SYSTEM COMMANDS:
docker system df              # Show disk usage
docker system prune           # Clean up unused data
docker volume ls              # List volumes
docker network ls             # List networks
docker info                   # System information
docker version                # Version information

TROUBLESHOOTING:
docker logs --tail 50 container  # Last 50 log lines
docker inspect container     # Detailed container info
docker stats                  # Resource usage stats
docker events                 # Real-time events
"""
        
        kubernetes_guide = """
Kubernetes Commands Reference

CLUSTER MANAGEMENT:
kubectl cluster-info          # Cluster information
kubectl get nodes             # List nodes
kubectl describe node name    # Node details
kubectl top nodes             # Node resource usage

POD MANAGEMENT:
kubectl get pods              # List pods
kubectl get pods -o wide      # Detailed pod info
kubectl describe pod name     # Pod details
kubectl logs pod_name         # Pod logs
kubectl exec -it pod bash     # Execute in pod
kubectl delete pod name       # Delete pod

DEPLOYMENT MANAGEMENT:
kubectl get deployments      # List deployments
kubectl create deployment name --image=image  # Create deployment
kubectl scale deployment name --replicas=3    # Scale deployment
kubectl rollout status deployment/name        # Rollout status
kubectl rollout history deployment/name       # Rollout history
kubectl rollout undo deployment/name          # Rollback deployment

SERVICE MANAGEMENT:
kubectl get services          # List services
kubectl expose deployment name --port=80      # Expose deployment
kubectl describe service name # Service details
kubectl get endpoints         # List endpoints

CONFIGURATION:
kubectl get configmaps        # List config maps
kubectl get secrets           # List secrets
kubectl create configmap name --from-file=file  # Create config map
kubectl create secret generic name --from-literal=key=value  # Create secret

TROUBLESHOOTING:
kubectl get events            # Cluster events
kubectl describe pod name     # Pod troubleshooting
kubectl logs -f pod_name      # Follow logs
kubectl top pods              # Pod resource usage
kubectl get all               # All resources
"""
        
        with open(self.docs_dir / "docker_reference.txt", 'w') as f:
            f.write(docker_guide)
            
        with open(self.docs_dir / "kubernetes_reference.txt", 'w') as f:
            f.write(kubernetes_guide)
            
        print("✅ Created DevOps guides")

if __name__ == "__main__":
    downloader = ExternalDocsDownloader()
    downloader.create_devops_guides()
    # downloader.download_arch_wiki_pages()  # Uncomment to download