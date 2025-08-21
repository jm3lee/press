from collections import deque
import os
from typing import Any, Deque, Dict, List, Optional

from fabric import Connection, Config
from invoke import run as local_run


class RoundRobinBalancer:
    """Simple round-robin load balancer.

    Remote hosts are rotated first and the local machine is appended to the
    cycle, ensuring remote workers receive jobs before falling back to local
    execution.
    """

    def __init__(self, hosts: List[str]):
        self.hosts: Deque[Optional[str]] = deque(h for h in hosts if h)
        self.hosts.append(None)  # local fallback

    def next(self) -> Optional[str]:
        host = self.hosts[0]
        self.hosts.rotate(-1)
        return host


_BALANCER = RoundRobinBalancer(
    os.environ.get("WORKER_HOSTS", "").split(",")
)


def execute_commands(
    commands: List[str],
    host: Optional[str] = None,
    connect_kwargs: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Execute shell commands sequentially and collect their results.

    Commands are dispatched to hosts in a round-robin fashion with remote hosts
    prioritized. If ``host`` is provided it overrides the balancer selection.
    ``fabric`` (Paramiko) executes remote commands; local commands use
    ``invoke``.
    """

    results: List[Dict[str, Any]] = []
    connect_kwargs = connect_kwargs or {}

    if host is None:
        host = _BALANCER.next()

    if host:
        config = Config(overrides={"load_known_hosts": False})
        conn = Connection(
            host,
            user="root",
            connect_kwargs=connect_kwargs,
            config=config,
        )
        runner = lambda c: conn.run(c, hide=True, warn=True, pty=False, in_stream=False)
    else:
        runner = lambda c: local_run(c, hide=True, warn=True, pty=False, in_stream=False)

    for cmd in commands:
        completed = runner(cmd)
        results.append(
            {
                "cmd": cmd,
                "returncode": completed.exited,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
    return results

