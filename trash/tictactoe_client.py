import socket
import threading

# ----------------------------
# Configuration
# ----------------------------
SERVER_IP = "192.168.1.165"  # Replace with your server PC IP
SERVER_PORT = 8888

# ----------------------------
# Function to receive messages
# ----------------------------
def receive_messages(sock):
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                print("Disconnected from server")
                break
            message = data.decode().strip()
            print(f"[Server] {message}")
    except Exception as e:
        print("Error receiving data:", e)
    finally:
        sock.close()

# ----------------------------
# Main
# ----------------------------
def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to {SERVER_IP}:{SERVER_PORT}")

        # Start thread to receive messages
        threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

        # Send messages from user input
        while True:
            msg = input()
            if msg.lower() in ("quit", "exit"):
                print("Closing connection...")
                sock.close()
                break
            sock.sendall(msg.encode())
    except Exception as e:
        print("Connection error:", e)

if __name__ == "__main__":
    main()
