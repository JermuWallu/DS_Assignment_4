import socket
import sys
import threading
from time import sleep

# TODO:
# - Accept incoming connection
# - let user save nickname 
# - let user to create channels
# - let user to type in channel
# - let user sen PM

# Class for message structure
class Message:
    def __init__(self, command: str, nickname: str, channel: str, content: str):
        self.command = command
        self.nickname = nickname
        self.channel = channel
        self.content = content
        
# Global variables:

CLIENTS = {} # List of connected clients with {nickname: ip} mapping
CHANNELS = ["#general", "#gaming", "#coding"] # List of current channels
PACKET_SIZE = 2048 # default packet size
CLIENT_THREADS = {} # Dictionary to lock access to client data

    
def send_packet(conn: socket.socket, message: Message):
    # Encode message data and send it
    data = f"{message.command}|{message.nickname}|{message.channel}|{message.content}"
    
    print(f"SENT: To '{conn.getsockname()}', data: '{data}'") #DEBUG
    conn.sendall(data.encode()) 

def receive_packet(conn, addr) -> Message:
    # Receive data from client and decode it
    data = conn.recv(PACKET_SIZE).decode()
    print(f"REQUEST: from '{addr}', data: '{data}'") #DEBUG
    # Split data into message components
    data = data.split('|')
    if len(data) != 4:
        return None
    command, nickname, channel, content = data
    return Message(command, nickname, channel, content)

def broadcast(message: Message):
    # Send message to all connected clients
    for conn, (nickname, _) in CLIENTS.items():
        with CLIENT_THREADS[conn]:
            if conn != message.nickname:  # Don't send to the sender itself
                send_packet(conn, message)

def broadcast_to_channel(message: Message):
    # Send message to all clients in the same channel
    for conn, (nickname, channel) in CLIENTS.items():
        with CLIENT_THREADS[conn]: # Tää kusee, ei löydä keyta
            if channel == message.channel and conn != message.nickname:
                send_packet(conn, message)                
                
def handle_quit(conn, nickname):
    # Remove client from list and broadcast leave message
    print(f"closing client '{nickname} Thread '{CLIENT_THREADS[conn]}'") 
    with CLIENT_THREADS[conn]:
        del CLIENTS[conn]
        del CLIENT_THREADS[conn]
    broadcast(Message("MESSAGE", "SERVER", "", f"{nickname} has left the chat!"))
    conn.close()  # Close the connection

def send_private_message(message: Message):
    # Find recipient and send message privately
    recipient = message.content.split(' ')[0]  # Assuming first word is recipient
    if recipient in [nickname for _, nickname in CLIENTS.values()]:
        for conn, (nickname_, _) in CLIENTS.items():
            if nickname_ == recipient:
                with CLIENT_THREADS[conn]:
                    send_packet(conn, message)
                break
    else:
        # Send message back to sender indicating recipient not found
        sender_conn = next(iter(CLIENTS))  # Get sender's connection
        with CLIENT_THREADS[sender_conn]:
            send_packet(sender_conn, Message("ERROR", None, None, f"User {recipient} not found!"))

def handle_client(conn: socket.socket, addr):
    print(f"Connected by {addr}")
    CLIENT_THREADS[conn] = threading.Lock()  # Create lock for this client
    
    # Continuously receive messages
    while True:
        try:
            message = receive_packet(conn, addr)
            if message is None:
                break
            
            elif message.command == "CONNECT":
                # Error handling
                if message.nickname == "":
                    send_packet(conn, Message("ERROR","","","Invalid Nickname!"))
                    continue
                # Check if nickname is taken TODO: fix
                # if CLIENTS[message.nickname] != None:
                #     send_packet(conn, Message("ERROR","","","Nickname already in use!"))
                #     break
                # assign nickname to client and give list of channels
                with CLIENT_THREADS[conn]:
                    nickname = message.nickname
                    CLIENTS[conn] = (nickname, "#general")  # Default channel
                    send_packet(conn, Message("CHANNELS",message.nickname,"",str(CHANNELS)))
                
            elif message.command == "JOIN":
                # tries to find desired channel and if successful, checks if desired nick is taken
                if message.channel in CHANNELS:
                    CLIENTS[conn] = (nickname, message.channel)  # Default channel
                    send_packet(conn, Message("OK", message.nickname, message.channel, ""))
                    
                    
                    # Broadcast join message
                    broadcast_to_channel(Message("MESSAGE", "SERVER", message.channel, f"'{message.nickname}' has joined the chat!"))
                    
                    
                else:    
                    send_packet(conn, Message("ERROR","","","Invalid channel!"))

                continue
            
            elif message.command == "MESSAGE":
                broadcast_to_channel(message)
                continue
            
            elif message.command == "PRIVATE":
                send_private_message(message)
                continue
            
            elif message.command == "QUIT":
                handle_quit(conn, message.nickname)
                break
            
            elif message.command == "DISCONNECT":
                # Server doesn't have to do anything since client already left 
                continue
            
            else:
                print("mitä vittua")
                print(message.__str__)
                continue
        except ConnectionAbortedError as E:
            print(f"Client {addr} disconnected abruptly!")
            handle_quit(conn, CLIENTS[conn][0])

    return

def clients_count():
    actives = 0
    while True:
        if actives != threading.activeCount():
            actives = threading.activeCount()
            print(f"current clients: {threading.activeCount()}\n")
            sleep(3)
def main():
    HOST, PORT = "localhost", 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1) # in documentation it put 1 there :D
        print(f"Server listening on {HOST}:{PORT}")
        threading.Thread(target=clients_count).start()
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client,args=(conn,addr))
            thread.start()
            threading.Thread
            
if __name__ == "__main__":
    main()
