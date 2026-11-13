import logging

from flask import current_app

logger = logging.getLogger(__name__)

SIMULATED_OUTPUT = {
    "uptime": "up 42 days, 07:13, load average: 0.14",
    "identity": "RadioNode RX-500 | firmware 8.2.1 | serial 00-DEMO",
    "links": "link0: up 1Gbps | link1: up 300Mbps",
}


def run_command(device, command: str) -> str:
    """Execute a read-only command on a network device.

    Production deployments open an SSH session with Paramiko. ``SIMULATE_SSH``
    keeps the demo runnable without access to real network hardware.
    """
    if current_app.config.get("SIMULATE_SSH", True):
        logger.info("simulated command execution device=%s command=%s", device.name, command)
        return SIMULATED_OUTPUT.get(command, "simulated output for '%s'" % command)

    import paramiko  # imported lazily so the demo only needs it in production

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=device.host,
        port=device.port,
        username=device.username,
        timeout=10,
        look_for_keys=True,
    )
    try:
        _, stdout, stderr = client.exec_command(command, timeout=15)
        output = stdout.read().decode(errors="replace")
        error = stderr.read().decode(errors="replace")
        return output or error
    finally:
        client.close()
