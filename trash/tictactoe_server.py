import socket
import threading

PORT = 8888
clients = []
clients_lock = threading.Lock()

# ----------------------------
# Show all available IPs
# ----------------------------
def show_ip_addresses():
    hostname = socket.gethostname()
    print(f"Hostname: {hostname}\n")

    addresses = set()

    for info in socket.getaddrinfo(hostname, None):
        family, _, _, _, sockaddr = info
        ip = sockaddr[0]

        # Filter out localhost duplicates
        if not ip.startswith("127.") and ip != "::1":
            addresses.add((family, ip))

    print("Available IP addresses:")
    for family, ip in addresses:
        if family == socket.AF_INET:
            print(f"  IPv4: {ip}")
        elif family == socket.AF_INET6:
            print(f"  IPv6: {ip}")
    print()

# ----------------------------
# Broadcast a message to all clients
# ----------------------------
def broadcast(message):
    with clients_lock:
        for c in clients:
            try:
                c.sendall((message + "\n").encode())
            except Exception as e:
                print("Error sending to client:", e)

# ----------------------------
# Client handler
# ----------------------------
def handle_client(client_socket, player_id):
    try:
        client_socket.sendall(f"ROLE:{player_id}\n".encode())

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            message = data.decode().strip()

            for c in clients:
                if c != client_socket:
                    c.sendall((f"{player_id}: {message}\n").encode())

    except Exception as e:
        print("Client error:", e)

    finally:
        print(f"Player {player_id} disconnected")
        client_socket.close()
        
# ----------------------------
# Command handler (server console)
# ----------------------------
def command_handler():
    while True:
        cmd = input("> ").strip()
        if cmd.lower().startswith("broadcast "):
            msg = cmd[len("broadcast "):]
            broadcast(f"SERVER: {msg}")
        elif cmd.lower() == "list":
            with clients_lock:
                print(f"Connected clients: {len(clients)}")
        elif cmd.lower() in ("quit", "exit"):
            print("Shutting down server...")
            with clients_lock:
                for c in clients:
                    c.close()
            break
        else:
            print("Commands: broadcast <msg>, list, quit")

# ----------------------------
# Server startup
# ----------------------------
def start_server():
    # Create IPv6 socket
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    # Allow IPv4 + IPv6 (dual stack)
    server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)

    server.bind(("::", PORT))
    server.listen(2)

    print(f"Server listening on port {PORT} (IPv4 + IPv6)\n")

    # Start command handler in a separate thread
    threading.Thread(target=command_handler, daemon=True).start()

    player_count = 0
    while True:
        client_socket, addr = server.accept()
        with clients_lock:
            clients.append(client_socket)
        player_count += 1
        player_id = "X" if player_count == 1 else "O"
        print(f"Player {player_id} connected from {addr}")

        threading.Thread(
            target=handle_client,
            args=(client_socket, player_id),
            daemon=True
        ).start()

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    show_ip_addresses()
    start_server()
