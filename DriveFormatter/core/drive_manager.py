# -*- coding: utf-8 -*-
"""
Drive detection and information gathering.
Uses Windows APIs when available, falls back to psutil for cross-platform listing.
"""

import ctypes
import os
import platform
import string
from dataclasses import dataclass, field
from typing import List, Optional

IS_WINDOWS = platform.system() == "Windows"

try:
    import psutil
except ImportError:
    psutil = None

DRIVE_TYPE_UNKNOWN = 0
DRIVE_TYPE_NO_ROOT_DIR = 1
DRIVE_TYPE_REMOVABLE = 2
DRIVE_TYPE_FIXED = 3
DRIVE_TYPE_REMOTE = 4
DRIVE_TYPE_CDROM = 5
DRIVE_TYPE_RAMDISK = 6

DRIVE_TYPE_LABELS = {
    DRIVE_TYPE_UNKNOWN: "unknown",
    DRIVE_TYPE_NO_ROOT_DIR: "unknown",
    DRIVE_TYPE_REMOVABLE: "removable",
    DRIVE_TYPE_FIXED: "fixed",
    DRIVE_TYPE_REMOTE: "network",
    DRIVE_TYPE_CDROM: "cdrom",
    DRIVE_TYPE_RAMDISK: "fixed",
}


@dataclass
class DriveInfo:
    path: str                  # e.g. "D:\\"
    letter: str                # e.g. "D:"
    label: str = ""
    filesystem: str = ""
    total_bytes: int = 0
    free_bytes: int = 0
    used_bytes: int = 0
    drive_type: int = DRIVE_TYPE_UNKNOWN
    drive_type_key: str = "unknown"
    serial_number: str = ""
    is_system: bool = False
    is_ready: bool = True

    @property
    def used_percent(self) -> float:
        if self.total_bytes <= 0:
            return 0.0
        return round((self.used_bytes / self.total_bytes) * 100, 1)


def _bytes_human(n: int) -> str:
    if n <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(n)
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    return f"{size:.2f} {units[idx]}"


def get_system_drive_letter() -> str:
    if IS_WINDOWS:
        sysdrive = os.environ.get("SystemDrive", "C:")
        return sysdrive.upper()
    return ""


def _win_drive_type(root_path: str) -> int:
    try:
        return ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(root_path))
    except Exception:
        return DRIVE_TYPE_UNKNOWN


def _win_volume_info(root_path: str):
    """Returns (label, filesystem, serial_number) using GetVolumeInformationW."""
    label_buf = ctypes.create_unicode_buffer(261)
    fs_buf = ctypes.create_unicode_buffer(261)
    serial = ctypes.c_uint(0)
    max_component_len = ctypes.c_uint(0)
    fs_flags = ctypes.c_uint(0)
    try:
        ok = ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(root_path),
            label_buf, ctypes.sizeof(label_buf),
            ctypes.byref(serial),
            ctypes.byref(max_component_len),
            ctypes.byref(fs_flags),
            fs_buf, ctypes.sizeof(fs_buf),
        )
        if ok:
            serial_str = f"{serial.value >> 16 & 0xFFFF:04X}-{serial.value & 0xFFFF:04X}"
            return label_buf.value, fs_buf.value, serial_str
    except Exception:
        pass
    return "", "", ""


def _win_free_space(root_path: str):
    free_bytes = ctypes.c_ulonglong(0)
    total_bytes = ctypes.c_ulonglong(0)
    total_free_bytes = ctypes.c_ulonglong(0)
    try:
        ok = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(root_path),
            ctypes.byref(free_bytes),
            ctypes.byref(total_bytes),
            ctypes.byref(total_free_bytes),
        )
        if ok:
            return total_bytes.value, free_bytes.value
    except Exception:
        pass
    return 0, 0


def list_windows_drives() -> List[DriveInfo]:
    drives = []
    system_letter = get_system_drive_letter()
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for i, letter in enumerate(string.ascii_uppercase):
        if not (bitmask >> i) & 1:
            continue
        root = f"{letter}:\\"
        drive_type = _win_drive_type(root)
        # Skip CD-ROM drives with no media / unknown types with no root
        if drive_type == DRIVE_TYPE_NO_ROOT_DIR:
            continue
        label, fs, serial = _win_volume_info(root)
        is_ready = bool(fs) or drive_type == DRIVE_TYPE_REMOVABLE
        total, free = (0, 0)
        if is_ready:
            total, free = _win_free_space(root)
        info = DriveInfo(
            path=root,
            letter=f"{letter}:",
            label=label,
            filesystem=fs,
            total_bytes=total,
            free_bytes=free,
            used_bytes=max(total - free, 0),
            drive_type=drive_type,
            drive_type_key=DRIVE_TYPE_LABELS.get(drive_type, "unknown"),
            serial_number=serial,
            is_system=(f"{letter}:" == system_letter),
            is_ready=is_ready,
        )
        drives.append(info)
    return drives


def list_psutil_drives() -> List[DriveInfo]:
    drives = []
    if psutil is None:
        return drives
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total, free, used = usage.total, usage.free, usage.used
        except (PermissionError, OSError):
            total, free, used = 0, 0, 0
        info = DriveInfo(
            path=part.mountpoint,
            letter=part.device,
            label=os.path.basename(part.mountpoint) or part.mountpoint,
            filesystem=part.fstype,
            total_bytes=total,
            free_bytes=free,
            used_bytes=used,
            drive_type=DRIVE_TYPE_FIXED if "fixed" in (part.opts or "") else DRIVE_TYPE_REMOVABLE,
            drive_type_key="fixed" if part.mountpoint == "/" else "removable",
            is_system=(part.mountpoint == "/"),
            is_ready=True,
        )
        drives.append(info)
    return drives


def list_drives() -> List[DriveInfo]:
    """Return a list of DriveInfo objects for all detected drives on this system."""
    if IS_WINDOWS:
        try:
            return list_windows_drives()
        except Exception:
            pass
    return list_psutil_drives()


def format_bytes(n: int) -> str:
    return _bytes_human(n)


def is_admin() -> bool:
    if IS_WINDOWS:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    try:
        return os.geteuid() == 0  # type: ignore[attr-defined]
    except AttributeError:
        return True


def relaunch_as_admin():
    """Attempt to relaunch the current script elevated (Windows only)."""
    if not IS_WINDOWS:
        return False
    try:
        import sys
        params = " ".join([f'"{a}"' for a in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        return True
    except Exception:
        return False
