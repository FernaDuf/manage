# mikrotik_utils.py - utilidades para MikroTik via SSH (paramiko)
import paramiko
import logging
from contextlib import contextmanager
from config import MT_HOST, MT_USER, MT_PASSWORD, MT_SSH_PORT, MT_BLOCK_LIST, MT_QUEUE_PREFIX, MT_QUEUE_PARENT

LOG = logging.getLogger("mikrotik_utils")
LOG.addHandler(logging.NullHandler())

@contextmanager
def _ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(MT_HOST, port=MT_SSH_PORT, username=MT_USER, password=MT_PASSWORD, timeout=10)
    try:
        yield ssh
    finally:
        ssh.close()

def _run(cmd: str) -> str:
    LOG.debug("MikroTik CMD: %s", cmd)
    with _ssh() as ssh:
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=15)
        out = stdout.read().decode(errors="ignore")
        err = stderr.read().decode(errors="ignore")
        if err and "expected" not in err.lower():
            raise RuntimeError(f"RouterOS error: {err.strip()} | cmd: {cmd}")
        return out

def queue_name(numero_cliente: int, nombre_cliente: str) -> str:
    base = f"{MT_QUEUE_PREFIX}{numero_cliente}_{nombre_cliente}".replace(" ", "_")
    return base[:60]

def block_ip(ip: str, numero_cliente: int, motivo: str = "mora") -> bool:
    comment = f"CLI:{numero_cliente} {motivo}"
    cmd = f'/ip firewall address-list add list="{MT_BLOCK_LIST}" address={ip} comment="{comment}"'
    try:
        _run(cmd)
        return True
    except Exception as e:
        LOG.exception("Error al bloquear IP %s: %s", ip, e)
        return False

def unblock_ip(ip: str) -> bool:
    cmd = f'/ip firewall address-list remove [find list="{MT_BLOCK_LIST}" and address={ip}]'
    try:
        _run(cmd)
        return True
    except Exception as e:
        LOG.exception("Error al desbloquear IP %s: %s", ip, e)
        return False

def create_queue(ip: str, up_kbps: int, down_kbps: int, numero_cliente: int, nombre_cliente: str) -> bool:
    qname = queue_name(numero_cliente, nombre_cliente)
    try:
        _run(f'/queue simple remove [find name="{qname}"]')
    except Exception:
        pass
    parent = f' parent="{MT_QUEUE_PARENT}"' if MT_QUEUE_PARENT else ""
    cmd = (f'/queue simple add name="{qname}" target={ip}{parent} '
           f'max-limit={up_kbps}k/{down_kbps}k comment="CLI:{numero_cliente}"')
    try:
        _run(cmd)
        return True
    except Exception as e:
        LOG.exception("Error creando queue %s: %s", qname, e)
        return False

def set_queue_rate(numero_cliente: int, nombre_cliente: str, up_kbps: int, down_kbps: int) -> bool:
    qname = queue_name(numero_cliente, nombre_cliente)
    cmd = f'/queue simple set [find name="{qname}"] max-limit={up_kbps}k/{down_kbps}k'
    try:
        _run(cmd)
        return True
    except Exception as e:
        LOG.exception("Error seteando rate de %s: %s", qname, e)
        return False

def delete_queue(numero_cliente: int, nombre_cliente: str) -> bool:
    qname = queue_name(numero_cliente, nombre_cliente)
    cmd = f'/queue simple remove [find name="{qname}"]'
    try:
        _run(cmd)
        return True
    except Exception as e:
        LOG.exception("No se pudo eliminar queue %s: %s", qname, e)
        return False

def test_connection():
    try:
        out = _run("/system resource print")
        return True, out[:1000]
    except Exception as e:
        return False, str(e)