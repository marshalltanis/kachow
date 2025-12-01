import threading
import socket
import time
import os
import pytest

from trading_brain.metatrader4 import MT4


def _start_test_server(host, port, payload, delay=0.05):
    """Start a simple TCP server in a background thread that sends `payload` once a client connects."""
    def server():
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(1)
        conn, addr = srv.accept()
        try:
            # small pause to let client get ready
            time.sleep(delay)
            conn.sendall(payload)
        finally:
            try:
                conn.close()
            except Exception:
                pass
            try:
                srv.close()
            except Exception:
                pass

    t = threading.Thread(target=server, daemon=True)
    t.start()
    return t


def test_mt4_receive_tick_parses_open_field():
    host = '127.0.0.1'
    port = 666
    # Compose a realistic tick payload terminated by the required sequence '\n\r'
    payload = b"time:2025-11-30 09:00:00,ask:1.2345,bid:1.2340,volume:100,spread:5,open:1.2330,close:1.2335\n\r"

    # Start test server
    _start_test_server(host, port, payload)

    # Build path to demo config relative to this test file
    config_path = os.path.join(os.path.dirname(__file__), '..', 'trading_brain', 'demo_config.json')

    mt4 = MT4(config_path)

    # connect() should succeed against our local test server
    connected = mt4.connect()
    assert connected is True

    # receive_tick_info should parse and return an object with an `open` attribute
    tick = mt4.receive_tick_info()
    assert tick is not None
    assert hasattr(tick, 'open')
    assert getattr(tick, 'open') == '1.2330'
