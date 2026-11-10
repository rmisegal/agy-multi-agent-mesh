# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Native process snapshot: {pid: (ppid, exe name)} with no third-party dependency.

Windows uses CreateToolhelp32Snapshot through ctypes (one fast call, no PowerShell/WMI);
other systems use ``ps``.
"""

from __future__ import annotations

import subprocess
import sys

TH32CS_SNAPPROCESS = 0x00000002


def snapshot() -> dict[int, tuple[int, str]]:
    if sys.platform == "win32":
        return _windows_snapshot()
    return _posix_snapshot()  # pragma: no cover - exercised on Linux/macOS only


def _windows_snapshot() -> dict[int, tuple[int, str]]:  # pragma: no cover - platform API
    import ctypes
    from ctypes import wintypes

    class Entry(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_char * 260),
        ]

    kernel = ctypes.windll.kernel32
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    handle = kernel.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    table: dict[int, tuple[int, str]] = {}
    entry = Entry()
    entry.dwSize = ctypes.sizeof(Entry)
    ok = kernel.Process32First(handle, ctypes.byref(entry))
    while ok:
        name = entry.szExeFile.decode("utf-8", errors="replace")
        table[int(entry.th32ProcessID)] = (int(entry.th32ParentProcessID), name)
        ok = kernel.Process32Next(handle, ctypes.byref(entry))
    kernel.CloseHandle(handle)
    return table


def _posix_snapshot() -> dict[int, tuple[int, str]]:  # pragma: no cover - non-Windows
    out = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,comm="], capture_output=True, text=True, check=False
    ).stdout
    table: dict[int, tuple[int, str]] = {}
    for line in out.splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            table[int(parts[0])] = (int(parts[1]), parts[2].rsplit("/", 1)[-1])
    return table
