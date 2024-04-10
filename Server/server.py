import socket
import sys
import threading

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
CHANNELS = ['#general'] # List of current channels
PACKET_SIZE = 2048 # default packet size
client_locks = {} # Dictionary to lock access to client data

    
def send_packet(conn, message: Message):
    # Encode message data and send it
    data = f"{message.command}|{message.nickname}|{message.channel}|{message.content}"
    
    print(f"SENT: To {conn.client_address[0]}, data: {data}") #DEBUG
    conn.request.sendall(data.encode()) 

def receive_packet(conn) -> Message:
    # Receive data from client and decode it
    data = conn.recv(PACKET_SIZE).decode()
    print(f"REQUEST: from {conn.client_address[0]}, data: {data}") #DEBUG
    # Split data into message components
    data = data.split('|')
    if len(data) != 4:
        return None
    command, nickname, channel, content = data
    return Message(command, nickname, channel, content)

def broadcast(message: Message):
    # Send message to all connected clients
    for conn, (nickname, _) in CLIENTS.items():
        with client_locks[conn]:
            if conn != message.nickname:  # Don't send to the sender itself
                send_packet(conn, message)

def broadcast_to_channel(message: Message):
    # Send message to all clients in the same channel
    for conn, (nickname, channel) in CLIENTS.items():
        with client_locks[conn]:
            if channel == message.channel and conn != message.nickname:
                send_packet(conn, message)                
                
def handle_quit(conn, nickname):
    # Remove client from list and broadcast leave message
    with client_locks[conn]:
        del CLIENTS[conn]
        del client_locks[conn]
    broadcast(Message('SERVER', None, None, f"{nickname} has left the chat!"))
    conn.close()  # Close the connection

def send_private_message(message: Message):
    # Find recipient and send message privately
    recipient = message.content.split(' ')[0]  # Assuming first word is recipient
    if recipient in [nickname for _, nickname in CLIENTS.values()]:
        for conn, (nickname_, _) in CLIENTS.items():
            if nickname_ == recipient:
                with client_locks[conn]:
                    send_packet(conn, message)
                break
    else:
        # Send message back to sender indicating recipient not found
        sender_conn = next(iter(CLIENTS))  # Get sender's connection
        with client_locks[sender_conn]:
            send_packet(sender_conn, Message('ERROR', None, None, f"User {recipient} not found!"))

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    client_locks[conn] = threading.Lock()  # Create lock for this client
    
    # Continuously receive messages
    while True:
        try:
            message = receive_packet(conn)
            if message is None:
                continue
            
            elif message.command == "CONNECT":
                # Error handling
                if message.nickname == "":
                    send_packet(Message("ERROR","","","Invalid Nickname!"))
                # Check if nickname is taken 
                if CLIENTS.get(message.nickname) != None:
                    send_packet(Message("ERROR","","","Nickname already in use!"))
                # assign nickname to client and give list of channels
                else: 
                    CLIENTS[message.nickname] = message.client_address
                    send_packet(Message("CHANNELS",message.nickname,"",str(CHANNELS)))
                
            elif message.command == "JOIN":
                # tries to find desired channel and if successful, checks if desired nick is taken
                for channel in CHANNELS:
                    if message.channel.lower() == channel.lower():
                        
                        # Broadcast join message
                        broadcast(Message('SERVER', None, None, f"{message.nickname} has joined the chat!"))
                        send_packet(Message("OK", message.nickname, channel, ""))
                        break
                        
                # self.send_packet(Message("ERROR","","","Invalid channel!"))

                break
            
            elif message.command == 'MESSAGE':
                broad_to_channel(message)
                break
            
            elif message.command == 'PRIVATE':
                send_private_message(message)
                break
            
            elif message.command == 'QUIT':
                handle_quit(message.nickname)
                break
            
            elif message.command == "DISCONNECT":
                # Server doesn't have to do anything since client already left 
                break
            
            else:
                print("mitä vittua")
                print(message.__str__)
                pass
        except ConnectionAbortedError as E:
            print(f"Client {addr} disconnected abruptly!")
            handle_quit(conn, CLIENTS[conn][0])

def main():
    HOST, PORT = "localhost", 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1) # in documentation it put 1 there :D
        print(f"Server listening on {HOST}:{PORT}")
        
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client,args=(conn,addr))
            thread.start()

if __name__ == '__main__':
    main()
