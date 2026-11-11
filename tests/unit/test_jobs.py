# © 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.
"""job_kills_children() against REAL Windows job objects (the agy tool-call situation)."""

from __future__ import annotations

import subprocess
import sys
import textwrap

import pytest

from agymesh.jobs import CONTAINED_HINT, job_kills_children

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="job objects are Windows-only")

# Starts a child SUSPENDED, puts it in a job with the given limit flags, resumes it, and
# prints what job_kills_children() says from INSIDE that job.
PROBE = textwrap.dedent(r'''
    import ctypes, subprocess, sys
    from ctypes import wintypes as w
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateJobObjectW.restype = w.HANDLE
    class B(ctypes.Structure):
        _fields_ = [("a", ctypes.c_int64), ("b", ctypes.c_int64), ("LimitFlags", w.DWORD),
                    ("c", ctypes.c_size_t), ("d", ctypes.c_size_t), ("e", w.DWORD),
                    ("f", ctypes.c_size_t), ("g", w.DWORD), ("h", w.DWORD)]
    class X(ctypes.Structure):
        _fields_ = [("B", B), ("io", ctypes.c_uint64 * 6), ("p", ctypes.c_size_t * 4)]
    job = k.CreateJobObjectW(None, None)
    info = X(); info.B.LimitFlags = int(sys.argv[1])
    assert k.SetInformationJobObject(w.HANDLE(job), 9, ctypes.byref(info), ctypes.sizeof(info))
    code = "from agymesh.jobs import job_kills_children as f; print(f())"
    p = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True,
                         creationflags=0x4)  # CREATE_SUSPENDED
    assert k.AssignProcessToJobObject(w.HANDLE(job), w.HANDLE(int(p._handle)))
    ctypes.WinDLL("ntdll").NtResumeProcess(w.HANDLE(int(p._handle)))
    print(p.communicate()[0].strip())
''')


def probe(limit_flags: int) -> str:
    out = subprocess.run([sys.executable, "-c", PROBE, str(limit_flags)],
                         capture_output=True, text=True, timeout=60, check=True)
    return out.stdout.strip()


def test_detects_agy_style_job_that_kills_on_close():
    assert probe(0x2000) == "True"          # KILL_ON_JOB_CLOSE, no BREAKAWAY_OK (agy)


def test_job_without_kill_on_close_only_inherits_the_parents_verdict():
    # A job with BREAKAWAY_OK only is harmless by itself. Jobs nest, though: when the test
    # runner itself already sits in a killing job (e.g. an agent's shell tool), the child is
    # still doomed - so the answer must equal this process's own verdict.
    assert probe(0x0800) == str(job_kills_children())


def test_returns_a_bool_for_this_process_and_hint_names_the_fix():
    assert isinstance(job_kills_children(), bool)
    assert "agymesh up" in CONTAINED_HINT.format(what="hub")
