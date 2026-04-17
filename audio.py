#!/usr/bin/env python3
"""
audio.py — Cross-platform audio playback for voice-notify.

Supports macOS (afplay) and Linux (paplay, aplay, mpv).
Includes PID-based kill_previous logic and file-lock serialization.
"""

from __future__ import annotations

import fcntl
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

PID_FILE = Path(tempfile.gettempdir()) / "claude_voice_notify.pid"
LOCK_FILE = Path(tempfile.gettempdir()) / "claude_voice_notify.lock"


def _detect_player() -> list[str]:
    """Detect available audio player. Returns command prefix list."""
    if sys.platform == "darwin":
        return ["afplay"]

    # Linux: try paplay (PulseAudio), then aplay (ALSA), then mpv
    for cmd in ("paplay", "aplay", "mpv"):
        if shutil.which(cmd):
            if cmd == "mpv":
                return ["mpv", "--no-video", "--really-quiet"]
            return [cmd]

    print("audio: no audio player found (need afplay, paplay, aplay, or mpv)",
          file=sys.stderr)
    return []


def kill_previous() -> None:
    """Kill any still-running previous notification audio process."""
    try:
        if not PID_FILE.exists():
            return
        old_pid = int(PID_FILE.read_text().strip())
        # Check if the process is still running and is an audio player
        result = subprocess.run(
            ["ps", "-p", str(old_pid), "-o", "comm="],
            capture_output=True, text=True, timeout=2
        )
        comm = result.stdout.strip()
        audio_names = ("afplay", "paplay", "aplay", "mpv")
        if any(name in comm for name in audio_names):
            os.kill(old_pid, signal.SIGTERM)
    except (ValueError, ProcessLookupError, PermissionError, OSError):
        pass


def play_audio(path: str, timeout: float = 15) -> subprocess.Popen | None:
    """
    Play an audio file. Returns the Popen handle, or None on failure.

    Serialized via file lock to prevent overlapping playback.
    Kills any previous still-playing notification first.
    """
    player = _detect_player()
    if not player:
        return None

    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
    except OSError:
        pass

    proc = None
    try:
        kill_previous()
        proc = subprocess.Popen(player + [path])
        PID_FILE.write_text(str(proc.pid))
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("audio: playback timed out, killing", file=sys.stderr)
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except (subprocess.TimeoutExpired, OSError):
                proc.kill()
    except (FileNotFoundError, OSError) as e:
        print(f"audio: playback error: {e}", file=sys.stderr)
    finally:
        try:
            PID_FILE.unlink(missing_ok=True)
        except OSError:
            pass
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
        except OSError:
            pass

    return proc


def play_audio_fire_and_forget(path: str) -> None:
    """Play audio without waiting. Used by permission hook for snappy response."""
    player = _detect_player()
    if not player:
        return
    try:
        proc = subprocess.Popen(player + [path])
        PID_FILE.write_text(str(proc.pid))
    except (FileNotFoundError, OSError) as e:
        print(f"audio: playback error: {e}", file=sys.stderr)
