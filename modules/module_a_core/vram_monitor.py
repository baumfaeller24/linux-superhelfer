"""
VRAM Monitor for intelligent model switching.
Monitors GPU memory usage and provides user warnings.
"""

import logging
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VRAMInfo:
    """VRAM usage information."""
    total_mb: int
    used_mb: int
    free_mb: int
    usage_percent: float
    device_name: str


class VRAMMonitor:
    """Monitors VRAM usage and provides warnings for model switching."""
    
    def __init__(self, warning_threshold: float = 0.8):
        """
        Initialize VRAM monitor.
        
        Args:
            warning_threshold: VRAM usage percentage to trigger warnings (0.0-1.0)
        """
        self.warning_threshold = warning_threshold
        self.pynvml_available = False
        self.device_count = 0
        
        # Try to initialize pynvml
        try:
            import pynvml
            pynvml.nvmlInit()
            self.pynvml = pynvml
            self.device_count = pynvml.nvmlDeviceGetCount()
            self.pynvml_available = True
            logger.info(f"VRAM monitoring initialized: {self.device_count} GPU(s) detected")
        except ImportError:
            logger.warning("pynvml not available - install with: pip install pynvml")
        except Exception as e:
            logger.warning(f"Failed to initialize VRAM monitoring: {e}")
    
    def get_vram_info(self, device_id: int = 0) -> Optional[VRAMInfo]:
        """
        Get VRAM information for specified device.
        
        Args:
            device_id: GPU device ID (default: 0)
            
        Returns:
            VRAMInfo object or None if monitoring unavailable
        """
        if not self.pynvml_available or device_id >= self.device_count:
            return None
        
        try:
            handle = self.pynvml.nvmlDeviceGetHandleByIndex(device_id)
            memory_info = self.pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            # Handle device name properly - it can be bytes or string
            try:
                device_name_raw = self.pynvml.nvmlDeviceGetName(handle)
                if isinstance(device_name_raw, bytes):
                    device_name = device_name_raw.decode('utf-8')
                else:
                    device_name = str(device_name_raw)
            except (UnicodeDecodeError, AttributeError):
                device_name = "Unknown GPU"
            
            total_mb = memory_info.total // (1024 * 1024)
            used_mb = memory_info.used // (1024 * 1024)
            free_mb = memory_info.free // (1024 * 1024)
            usage_percent = memory_info.used / memory_info.total
            
            return VRAMInfo(
                total_mb=total_mb,
                used_mb=used_mb,
                free_mb=free_mb,
                usage_percent=usage_percent,
                device_name=device_name
            )
        except Exception as e:
            logger.error(f"Failed to get VRAM info for device {device_id}: {e}")
            return None
    
    def get_usage_percentage(self, device_id: int = 0) -> float:
        """
        Get VRAM usage as percentage (0.0-1.0).
        
        Args:
            device_id: GPU device ID (default: 0)
            
        Returns:
            Usage percentage or 0.0 if monitoring unavailable
        """
        vram_info = self.get_vram_info(device_id)
        return vram_info.usage_percent if vram_info else 0.0
    
    def check_before_model_switch(
        self, 
        target_model: str, 
        estimated_vram_mb: int,
        device_id: int = 0,
        show_gui: bool = True
    ) -> bool:
        """
        Check VRAM usage before switching to a larger model.
        
        Args:
            target_model: Name of the target model
            estimated_vram_mb: Estimated VRAM usage in MB
            device_id: GPU device ID (default: 0)
            show_gui: Whether to show GUI warning dialog
            
        Returns:
            True if user confirms or usage is below threshold, False otherwise
        """
        vram_info = self.get_vram_info(device_id)
        
        if not vram_info:
            logger.warning("VRAM monitoring unavailable - proceeding without check")
            return True
        
        # Check if current usage is above threshold
        if vram_info.usage_percent <= self.warning_threshold:
            logger.info(f"VRAM usage OK: {vram_info.usage_percent:.1%} < {self.warning_threshold:.1%}")
            return True
        
        # Check if there's enough free VRAM for the new model
        if vram_info.free_mb < estimated_vram_mb:
            logger.warning(f"Insufficient VRAM: need {estimated_vram_mb}MB, have {vram_info.free_mb}MB free")
            
            if show_gui:
                return self._show_insufficient_vram_dialog(
                    target_model, estimated_vram_mb, vram_info
                )
            else:
                return False
        
        # Usage is high but might be manageable
        logger.warning(f"High VRAM usage: {vram_info.usage_percent:.1%}")
        
        if show_gui:
            return self._show_high_usage_dialog(target_model, vram_info)
        else:
            return False
    
    def _show_high_usage_dialog(self, target_model: str, vram_info: VRAMInfo) -> bool:
        """Show dialog for high VRAM usage warning."""
        try:
            # Create hidden root window
            root = tk.Tk()
            root.withdraw()
            
            message = (
                f"VRAM-Warnung\n\n"
                f"GPU: {vram_info.device_name}\n"
                f"Aktuelle VRAM-Nutzung: {vram_info.usage_percent:.1%}\n"
                f"Verwendet: {vram_info.used_mb:,} MB\n"
                f"Verfügbar: {vram_info.free_mb:,} MB\n\n"
                f"Wechsel zu '{target_model}' könnte andere Anwendungen beeinträchtigen.\n\n"
                f"Trotzdem fortfahren?"
            )
            
            result = messagebox.askokcancel(
                "VRAM-Warnung",
                message,
                icon='warning'
            )
            
            root.destroy()
            
            if result:
                logger.info(f"User confirmed model switch to {target_model}")
            else:
                logger.info(f"User cancelled model switch to {target_model}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to show VRAM warning dialog: {e}")
            # Default to allowing the switch if dialog fails
            return True
    
    def _show_insufficient_vram_dialog(
        self, 
        target_model: str, 
        estimated_vram_mb: int, 
        vram_info: VRAMInfo
    ) -> bool:
        """Show dialog for insufficient VRAM error."""
        try:
            # Create hidden root window
            root = tk.Tk()
            root.withdraw()
            
            message = (
                f"Unzureichender VRAM\n\n"
                f"GPU: {vram_info.device_name}\n"
                f"Benötigt für '{target_model}': {estimated_vram_mb:,} MB\n"
                f"Verfügbar: {vram_info.free_mb:,} MB\n"
                f"Fehlend: {estimated_vram_mb - vram_info.free_mb:,} MB\n\n"
                f"Bitte schließen Sie andere GPU-intensive Anwendungen und versuchen Sie es erneut.\n\n"
                f"Trotzdem versuchen? (Kann zu Fehlern führen)"
            )
            
            result = messagebox.askokcancel(
                "Unzureichender VRAM",
                message,
                icon='error'
            )
            
            root.destroy()
            
            if result:
                logger.warning(f"User forced model switch to {target_model} despite insufficient VRAM")
            else:
                logger.info(f"User cancelled model switch due to insufficient VRAM")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to show insufficient VRAM dialog: {e}")
            # Default to denying the switch if dialog fails
            return False
    
    def get_all_devices_info(self) -> Dict[int, VRAMInfo]:
        """Get VRAM info for all available devices."""
        devices = {}
        
        for device_id in range(self.device_count):
            vram_info = self.get_vram_info(device_id)
            if vram_info:
                devices[device_id] = vram_info
        
        return devices
    
    def log_vram_status(self, device_id: int = 0) -> None:
        """Log current VRAM status for debugging."""
        vram_info = self.get_vram_info(device_id)
        
        if vram_info:
            logger.info(
                f"VRAM Status - Device {device_id} ({vram_info.device_name}): "
                f"{vram_info.usage_percent:.1%} used "
                f"({vram_info.used_mb:,}/{vram_info.total_mb:,} MB)"
            )
        else:
            logger.info(f"VRAM monitoring unavailable for device {device_id}")


# Convenience functions for external use
def get_vram_usage() -> float:
    """Get current VRAM usage percentage."""
    monitor = VRAMMonitor()
    return monitor.get_usage_percentage()


def check_vram_before_switch(model_name: str, estimated_mb: int) -> bool:
    """Check VRAM before model switch with user confirmation."""
    monitor = VRAMMonitor()
    return monitor.check_before_model_switch(model_name, estimated_mb)


if __name__ == "__main__":
    # Test the VRAM monitor
    monitor = VRAMMonitor()
    
    print("VRAM Monitor Test")
    print("=" * 40)
    
    if monitor.pynvml_available:
        devices = monitor.get_all_devices_info()
        
        for device_id, info in devices.items():
            print(f"\nDevice {device_id}: {info.device_name}")
            print(f"Total VRAM: {info.total_mb:,} MB")
            print(f"Used VRAM: {info.used_mb:,} MB ({info.usage_percent:.1%})")
            print(f"Free VRAM: {info.free_mb:,} MB")
        
        # Test warning dialog (uncomment to test)
        # result = monitor.check_before_model_switch("qwen3-coder:30b-q4", 20000)
        # print(f"\nUser decision: {'Proceed' if result else 'Cancel'}")
        
    else:
        print("VRAM monitoring not available")
        print("Install pynvml: pip install pynvml")