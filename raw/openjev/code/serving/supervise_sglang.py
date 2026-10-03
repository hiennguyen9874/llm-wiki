"""Keep systemd's watchdog alive only after a real successful classification."""
import argparse
import math
import os
from pathlib import Path
import signal
import subprocess
import time

import requests

from service_notify import notify


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu", required=True, type=int)
    a = ap.parse_args()
    root = Path(os.environ["OPENJEV_V100_ROOT"])
    port = int(os.environ.get("OPENJEV_PORT", 31010 + a.gpu))
    model = os.environ.get("OPENJEV_MODEL", str(root / "model"))
    ready_file = root / "ready" / f"{port}.ready"
    ready_file.parent.mkdir(parents=True, exist_ok=True)
    ready_file.unlink(missing_ok=True)
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(a.gpu))
    # Only the supervisor may satisfy the service watchdog.
    for key in ("NOTIFY_SOCKET", "WATCHDOG_USEC", "WATCHDOG_PID"):
        env.pop(key, None)
    command = ["bash", str(root / "app/serve_sglang_v100.sh"), model,
               str(port), "--schedule-policy", "lpm", "--random-seed", "42"]
    server = subprocess.Popen(command, env=env)

    def stop(*_):
        raise SystemExit(0)

    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):
        signal.signal(sig, stop)
    ready = False
    try:
        while server.poll() is None:
            try:
                response = requests.post(
                    f"http://127.0.0.1:{port}/classify",
                    json={"text": "Premise: A man is playing a guitar.\nHypothesis: Someone is making music."},
                    timeout=(3, 60),
                )
                response.raise_for_status()
                output = response.json()
                if isinstance(output, list):
                    output = output[0]
                logits = output["embedding"]
                if len(logits) != 3 or not all(math.isfinite(x) for x in logits) or logits[1] <= logits[0]:
                    raise ValueError("Classification health probe failed")
                if not ready:
                    if os.environ.get("OPENJEV_PREFILL_WARMUP") == "1":
                        max_running = int(os.environ.get("MAX_RUNNING_REQUESTS", "16"))
                        # HTTP tokenization can dispatch the first row separately;
                        # include an oversized request to fill all scheduler slots.
                        for length in (0, 12, 24, 96):
                            for count in [*range(1, max_running + 1), 2 * max_running]:
                                notify(f"STATUS=GPU {a.gpu}: warming prefill length {length}, batch {count}; not ready yet")
                                texts = [f"Premise: Warmup length {length}, batch {count}, row {j}. " +
                                         "A person plays music while a cat sits beside the window. " * length +
                                         "\nHypothesis: Someone is making music."
                                         for j in range(count)]
                                if length == 0:
                                    # Keep the whole 16-row batch below the
                                    # recurrent/chunked dispatch threshold.
                                    texts = [f"Premise: {count}/{j} sings.\nHypothesis: Someone sings."
                                             for j in range(count)]
                                # Both uncached and cached suffixes: long inputs
                                # also exercise checkpoint-producing GDN kernels.
                                for _ in range(2):
                                    warm = requests.post(f"http://127.0.0.1:{port}/classify",
                                                         json={"text": texts}, timeout=(3, 300))
                                    warm.raise_for_status()
                                    outputs = warm.json()
                                    if len(outputs) != count or not all(len(o["embedding"]) == 3 and
                                            all(math.isfinite(x) for x in o["embedding"]) for o in outputs):
                                        raise ValueError("Prefill warmup output invalid")
                    if os.environ.get("OPENJEV_VISION_WARMUP") == "1":
                        from warmup_vision import warmup_vision
                        notify(f"STATUS=GPU {a.gpu}: warming vision; not ready yet")
                        warmup_vision(f"http://127.0.0.1:{port}")
                    ready_file.write_text(str(os.getpid()) + "\n")
                    notify("READY=1")
                    ready = True
                notify(f"WATCHDOG=1\nSTATUS=GPU {a.gpu}: classification healthy on {port}")
                time.sleep(15)
            except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
                notify(f"STATUS=GPU {a.gpu}: probe failed: {type(exc).__name__}")
                print(f"classification health probe: {type(exc).__name__}: {exc}", flush=True)
                # No watchdog pulse on failure: systemd kills the whole cgroup.
                time.sleep(5)
        raise SystemExit(server.returncode or 1)
    finally:
        ready_file.unlink(missing_ok=True)
        if server.poll() is None:
            server.send_signal(signal.SIGQUIT)
            try:
                server.wait(timeout=30)
            except subprocess.TimeoutExpired:
                # systemd KillMode=control-group/TimeoutStopSec handles the tree.
                pass


if __name__ == "__main__":
    main()
