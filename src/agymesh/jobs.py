# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""Is this process trapped in a Windows job that will kill what it starts?

agy runs every shell command inside a job object with KILL_ON_JOB_CLOSE and without
BREAKAWAY_OK: when the tool call returns, the job closes and every process started from it
dies - agy windows and a hub included. The launchers use this to refuse with a clear message
instead of starting something that is gone a moment later.
"""

from __future__ import annotations

import sys

JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9

CONTAINED_HINT = (
    "This command runs inside a Windows job that closes when the command ends and does not "
    "let new processes break away (agy runs every shell command this way), so the {what} "
    "would be killed as soon as this command returns. Run `agymesh up` in your OWN "
    "PowerShell window instead (not through an agy session); the agy sessions then join it."
)


def job_kills_children() -> bool:
    """True when the current process is in a job that kills its processes when it closes."""
    if sys.platform != "win32":  # pragma: no cover - job objects are Windows-only
        return False
    try:
        return _query_kill_on_close()
    except OSError:  # pragma: no cover - cannot tell: keep the old best-effort behaviour
        return False


def _query_kill_on_close() -> bool:  # pragma: no cover - platform API
    import ctypes
    from ctypes import wintypes

    class Basic(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                    ("PerJobUserTimeLimit", ctypes.c_int64), ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t),
                    ("ActiveProcessLimit", wintypes.DWORD), ("Affinity", ctypes.c_size_t),
                    ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]

    class Extended(ctypes.Structure):
        _fields_ = [("Basic", Basic), ("Io", ctypes.c_uint64 * 6),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    in_job = wintypes.BOOL()
    current = wintypes.HANDLE(-1)  # pseudo-handle of this process
    if not kernel32.IsProcessInJob(current, None, ctypes.byref(in_job)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not in_job.value:
        return False
    info = Extended()
    ok = kernel32.QueryInformationJobObject(None, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                                            ctypes.byref(info), ctypes.sizeof(info), None)
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    return bool(info.Basic.LimitFlags & JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
