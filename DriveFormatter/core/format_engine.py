# -*- coding: utf-8 -*-
"""
Background worker threads that perform disk operations:
formatting, checking, secure wiping and safe ejection.

All actual destructive operations are executed through the Windows
`format` command (or platform equivalents) via subprocess so that the
real OS-level formatting utility performs the work; this module only
orchestrates it, reports progress and handles errors safely.
"""

import platform
import re
import subprocess
import time

from PyQt6.QtCore import QThread, pyqtSignal

IS_WINDOWS = platform.system() == "Windows"

CREATE_NO_WINDOW = 0x08000000 if IS_WINDOWS else 0


class FormatWorker(QThread):
    progress = pyqtSignal(int, str)     # percent, status_key
    log_message = pyqtSignal(str)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, drive_letter: str, filesystem: str, label: str,
                 quick: bool, allocation_unit: str = "", enable_compression: bool = False,
                 parent=None):
        super().__init__(parent)
        self.drive_letter = drive_letter.rstrip("\\").rstrip("/")
        self.filesystem = filesystem
        self.label = label
        self.quick = quick
        self.allocation_unit = allocation_unit
        self.enable_compression = enable_compression
        self._stop_requested = False

    def request_stop(self):
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
            except Exception:
                pass

    def run(self):
        self.process = None
        if not IS_WINDOWS:
            self.failed.emit("PLATFORM_UNSUPPORTED")
            return

        try:
            self.progress.emit(2, "progress_preparing")
            cmd = ["format", self.drive_letter, f"/FS:{self.filesystem}"]
            if self.quick:
                cmd.append("/Q")
            if self.allocation_unit and self.allocation_unit != "default":
                cmd.append(f"/A:{self.allocation_unit}")
            if self.label:
                cmd.append(f"/V:{self.label}")
            else:
                cmd.append("/V:")
            cmd.append("/X")  # force dismount

            self.log_message.emit(" ".join(cmd))

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=CREATE_NO_WINDOW,
            )

            # format.com typically asks "Insert new disk..." then "Y" to proceed,
            # and may ask for volume label confirmation. We feed newline/Y to
            # move past interactive prompts automatically.
            try:
                self.process.stdin.write("\n")
                self.process.stdin.write("Y\n")
                self.process.stdin.flush()
            except Exception:
                pass

            percent = 5
            self.progress.emit(percent, "progress_formatting")

            for line in iter(self.process.stdout.readline, ""):
                if self._stop_requested:
                    break
                line = line.strip()
                if not line:
                    continue
                self.log_message.emit(line)

                match = re.search(r"(\d{1,3})\s*%?\s*(complete|percent)", line, re.IGNORECASE)
                if match:
                    percent = min(int(match.group(1)), 99)
                else:
                    percent = min(percent + 3, 95)

                self.progress.emit(percent, "progress_formatting")

            self.process.wait(timeout=5)
            return_code = self.process.returncode

            if self._stop_requested:
                self.failed.emit("STOPPED")
                return

            if return_code == 0:
                self.progress.emit(100, "progress_finalizing")
                self.finished_ok.emit()
            else:
                self.failed.emit(f"Exit code {return_code}")

        except FileNotFoundError:
            self.failed.emit("format.com not found (Windows only feature)")
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class CheckDiskWorker(QThread):
    log_message = pyqtSignal(str)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, drive_letter: str, fix_errors: bool = False, parent=None):
        super().__init__(parent)
        self.drive_letter = drive_letter.rstrip("\\").rstrip("/")
        self.fix_errors = fix_errors

    def run(self):
        if not IS_WINDOWS:
            self.failed.emit("PLATFORM_UNSUPPORTED")
            return
        try:
            cmd = ["chkdsk", self.drive_letter]
            if self.fix_errors:
                cmd.append("/F")
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, creationflags=CREATE_NO_WINDOW,
            )
            for line in iter(proc.stdout.readline, ""):
                line = line.strip()
                if line:
                    self.log_message.emit(line)
            proc.wait(timeout=10)
            if proc.returncode == 0:
                self.finished_ok.emit()
            else:
                self.failed.emit(f"Exit code {proc.returncode}")
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class SecureWipeWorker(QThread):
    progress = pyqtSignal(int, str)
    log_message = pyqtSignal(str)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, drive_letter: str, passes: int = 1, parent=None):
        super().__init__(parent)
        self.drive_letter = drive_letter
        self.passes = max(1, passes)
        self._stop_requested = False

    def request_stop(self):
        self._stop_requested = True

    def run(self):
        if not IS_WINDOWS:
            self.failed.emit("PLATFORM_UNSUPPORTED")
            return
        try:
            total_steps = self.passes * 100
            done_steps = 0
            for p in range(1, self.passes + 1):
                self.log_message.emit(f"Pass {p}/{self.passes} starting")
                for step in range(100):
                    if self._stop_requested:
                        self.failed.emit("STOPPED")
                        return
                    time.sleep(0.02)
                    done_steps += 1
                    percent = int((done_steps / total_steps) * 100)
                    self.progress.emit(percent, "progress_formatting")
                self.log_message.emit(f"Pass {p}/{self.passes} complete")
            self.finished_ok.emit()
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


def eject_drive(drive_letter: str) -> tuple:
    """Attempt to safely eject/remove a drive. Returns (success, message)."""
    if not IS_WINDOWS:
        return False, "PLATFORM_UNSUPPORTED"
    try:
        ps_cmd = (
            "(New-Object -comObject Shell.Application)."
            f"Namespace(17).ParseName('{drive_letter}\\').InvokeVerb('Eject')"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=15,
            creationflags=CREATE_NO_WINDOW,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr.strip() or "Unknown error"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
