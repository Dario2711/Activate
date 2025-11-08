import socket
import json
import os
from typing import Tuple, Dict, Any

HOST = os.environ.get('TCP_PERSIST_HOST', '127.0.0.1')
PORT = int(os.environ.get('TCP_PERSIST_PORT', '6000'))

def _send_request(payload: Dict[str, Any], timeout: float = 3.0) -> Tuple[bool, Dict[str, Any]]:
    data = (json.dumps(payload) + "\n").encode('utf-8')
    with socket.create_connection((HOST, PORT), timeout=timeout) as s:
        s.sendall(data)
        # read until newline
        buf = b''
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"\n" in chunk:
                break
        try:
            resp = json.loads(buf.decode('utf-8').strip())
        except json.JSONDecodeError:
            return False, {"error": "invalid_response"}
        ok = bool(resp.get('success'))
        return ok, resp

def save_score_via_tcp(user_id: int, puntaje: int) -> Tuple[bool, Dict[str, Any]]:
    return _send_request({
        'action': 'save_score',
        'user_id': user_id,
        'puntaje': puntaje,
    })
