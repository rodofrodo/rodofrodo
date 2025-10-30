import socket
import threading
import random

# my own imports
import poker_logic

clients = []
names = {}
money = {}
gameStarted = False

# betting variables
dealer = None
small_blind = None
big_blind = None

# cards
all_used_cards = []
community_cards = []
player_hands = {}

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        try:
            msg = conn.recv(1024).decode()
            reply = ''
            if not msg:
                break
            
            # set client name
            elif msg.startswith("name&"):
                name = msg.split("&", 1)[1]
                names[conn] = name
                print(f"[NAME SET] {addr} is now known as {name}.")
                money[name] = 1000  # Initial money
                print(f"[MONEY ASSIGNED] {name} has been assigned $1000.")
                
            # number of connected clients
            elif msg == "len":
                reply = f"Length&{len(clients)}"
                print(f"[LENGTH] There are currently {len(clients)} connected clients.")
                for client in clients:
                    if client != conn:
                        client.sendall(reply.encode())
                        
            # broadcast message to all clients
            elif msg.startswith("msg&"):
                content = msg.split("&", 1)[1]
                reply = f"Broadcast&{content}"
                print(f"[BROADCAST] From {addr}: {content}")
                for client in clients:
                    if client != conn:
                        client.sendall(reply.encode())
                        
            # info request
            elif msg == "info":
                print("[INFO REQUEST] Sending client info.")
                reply = f"Connected clients: {len(clients)}\nYour address: {addr}\nYour wallet: ${money[names[conn]]}\nYour name: {names[conn]}"
                
            # card request
            elif msg == "get_cards":
                conn.sendall(("CommunityCards&" + "#".join(str(card) for card in community_cards)).encode())
                add_player_hand(names[conn])
                conn.sendall((f"PlayerCards&{names[conn]}=" + "#".join(str(card) for card in player_hands[names[conn]])).encode())

            # default echo
            else:
                reply = f"Echo: {msg}"
                print(f"[MESSAGE] From {addr}: {msg}")
            conn.sendall(reply.encode())
        except:
            break
        
    # cleanup after client disconnects
    print(f"[DISCONNECTED] {addr}")
    for client in clients:
        if client != conn:
            client.sendall(f'Disconnected&Player named {names[conn]} at {addr} has disconnected!'.encode())
    clients.remove(conn)
    del money[names[conn]]
    del names[conn]
    conn.close()

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[LISTENING] Server on {host}:{port}")
    
    while True:
        try:
            conn, addr = server.accept()
            clients.append(conn)
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
            break

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't need to be reachable — just used to get your local IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# method to set community cards
def set_community_cards():
    all_used_cards.clear()
    community_cards.clear()
    while len(community_cards) < 5:
        card = poker_logic.Card(
            suit=poker_logic.Suit(random.randint(1, 4)),
            rank=poker_logic.Rank(random.randint(2, 14))
        )
        if card not in all_used_cards:
            all_used_cards.append(card)
            community_cards.append(card)

# method to add player hand
def add_player_hand(player_name):
    hand = []
    while len(hand) < 2:
        card = poker_logic.Card(
            suit=poker_logic.Suit(random.randint(1, 4)),
            rank=poker_logic.Rank(random.randint(2, 14))
        )
        if card not in all_used_cards:
            all_used_cards.append(card)
            hand.append(card)
    player_hands[player_name] = hand

def start_game():
    # TODO: change to >= 2
    global gameStarted, dealer, small_blind, big_blind
    if not gameStarted and len(clients) >= 3: # Minimum 3 players to start
        gameStarted = True
        playerString = ''
        for vname in names.values():
            playerString += f"{vname}*{money[vname]}#"
        for c in clients:
            c.sendall(f"StartGame&{playerString[:-1]}".encode())
        dealer = names[clients[0]]  # Set the dealer to the first client
        small_blind = names[clients[1]]  # Set small blind to second client
        big_blind = names[clients[2]]  # Set big blind to third client
        bettings = f"Bettings&Dealer:{dealer}#SmallBlind:{small_blind}#BigBlind:{big_blind}"
        for c in clients:
            c.sendall(bettings.encode())
        print("Game started.")
    else:
        print("Game has already started." if gameStarted else "Not enough players to start the game.")

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, args=(get_local_ip(), 5050), daemon=True)
    server_thread.start()

    # Main thread can handle server commands
    while True:
        cmd = input(">> ").strip().lower()
        if cmd == "exit" or cmd == "quit" or cmd == "stop":
            print("Shutting down server...")
            break
        elif cmd == "clients":
            print(f"Connected clients: {len(clients)}")
            for c in clients:
                name = names.get(c, "<unnamed>")
                print(f"  {name}")
        elif cmd == "clear":
            for c in clients:
                c.sendall("Clear".encode())
        elif cmd == "cards":
            set_community_cards()
            print("Community Cards:")
            for card in community_cards:
                print(f"  {card}")
        elif cmd == "start":
            start_game()
        else:
            print("Unknown command.")
