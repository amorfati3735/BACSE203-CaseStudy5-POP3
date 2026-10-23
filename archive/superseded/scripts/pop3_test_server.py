
import socket

HOST = "127.0.0.1"
PORT = 1110
TEST_USER = "branch_user1"
TEST_PASSWORD = "hello@123"
TARGET_BYTES = 820


def make_top_response():
    # Synthetic POP3 headers for a controlled lab test.
    status = b"+OK top of message follows\r\n"

    headers = (
        b"From: engineering-hq@enterprise.com\r\n"
        b"To: branch_user1@enterprise.com\r\n"
        b"Subject: Q4 Structural Blueprints Attachment\r\n"
        b"Date: Thu, 22 Oct 2026 12:00:00 +0000\r\n"
        b"MIME-Version: 1.0\r\n"
        b"Content-Type: multipart/mixed; boundary=lab-boundary\r\n"
    )

    prefix = status + headers + b"X-Lab-Padding: "
    suffix = b"\r\n\r\n.\r\n"
    padding_length = TARGET_BYTES - len(prefix) - len(suffix)

    if padding_length < 0:
        raise ValueError("Headers exceed the target size")

    response = prefix + (b"x" * padding_length) + suffix
    assert len(response) == TARGET_BYTES
    return response


def handle_client(conn):
    conn.sendall(b"+OK Lab POP3 server ready\r\n")
    username = None
    authenticated = False

    with conn.makefile("rb") as stream:
        while True:
            line = stream.readline(4096)
            if not line:
                break

            command = line.decode("ascii", "replace").strip()
            cmd, _, argument = command.partition(" ")
            cmd = cmd.upper()

            if cmd == "USER":
                username = argument
                conn.sendall(b"+OK User accepted\r\n")

            elif cmd == "PASS":
                if username == TEST_USER and argument == TEST_PASSWORD:
                    authenticated = True
                    conn.sendall(b"+OK Authentication successful\r\n")
                else:
                    conn.sendall(b"-ERR Authentication failed\r\n")

            elif cmd == "TOP" and argument == "4 0":
                if not authenticated:
                    conn.sendall(b"-ERR Authenticate first\r\n")
                else:
                    response = make_top_response()
                    conn.sendall(response)
                    print(f"Sent TOP response: {len(response)} bytes")

            elif cmd == "QUIT":
                conn.sendall(b"+OK Goodbye\r\n")
                break

            else:
                conn.sendall(b"-ERR Unsupported command\r\n")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"Lab POP3 test server listening on {HOST}:{PORT}")
    print("Waiting for a test client...")

    while True:
        conn, address = server.accept()
        print("Client connected:", address)
        with conn:
            handle_client(conn)
