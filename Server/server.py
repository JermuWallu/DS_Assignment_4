from socketserver import *
import sys

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

CLIENTS = {} # List of connected clients with {nickname: channel} mapping
CHANNELS = ['#general'] # List of current channels
PACKET_SIZE = 2048 # default packet size

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    pass

class ChatServerHandler(BaseRequestHandler):
    
    def send_packet(self, message: Message):
        # Encode message data and send it
        data = f"{message.command}|{message.nickname}|{message.channel}|{message.content}"
        
        print(f"SENT: To {self.client_address[0]}, data: {data}")
        self.request.sendall(data.encode())
        
    def receive_packet(self) -> str:
        data = str(self.request.recv(PACKET_SIZE).decode())
        print(f"REQUEST: from {self.client_address[0]}, data: {data}")
        return data
    
    def receive_message(self) -> Message:
        # Receive message data and decode it
        self.data = self.receive_packet()
        
        # Split data into message components
        data = self.data.split('|')
        command = data[0] if data[0] is not None else ""
        nickname = data[1] if data[1] is not None else ""
        channel = data[2] if data[2] is not None else ""
        content = data[3] if data[3] is not None else ""
        
        return Message(command, nickname, channel, content)

    def broadcast(self, message: Message):
        # Send message to all connected clients
        for client, channel in CLIENTS.items():
            if channel == message.channel:
                self.send_message_to(client, message)

    def message_to_channel(self, message: Message):
        # Send message to all clients in the same channel
        self.broadcast(Message(message.command, message.nickname, message.channel, message.content))

    def send_private_message(self, message: Message):
        # Find recipient and send message privately
        recipient = message.content.split(' ')[0]  # Assuming first word is recipient
        if recipient in CLIENTS:
            self.send_message_to(recipient, message)
        else:
            self.send_packet(Message('SERVER', None, None, f"User {recipient} not found!"))

    def send_message_to(self, client, message: Message):
        # Find client by nickname and send message
        for sock, (nick, _) in CLIENTS.items():
            if nick == client:
                self.send_packet(message)
                break

    def handle_quit(self, nickname):
        # Remove client from list and broadcast leave message
        del CLIENTS[nickname]
        self.broadcast(Message('SERVER', None, None, f"{nickname} has left the chat!"))

    def handle(self):
        # Continuously receive messages
        while True:
            message = self.receive_message()
            if message.command == "CONNECT":
                #  here you would add security stuff 
                self.send_packet(Message("CHANNELS","","",str(CHANNELS)))
                
            elif message.command == "JOIN":
                # Error handling
                if message.nickname == "":
                    self.send_packet(Message("ERROR","","","Invalid Nickname!"))
                # tries to find desired channel and if successful, checks if desired nick is taken
                for channel in CHANNELS:
                    if message.channel.lower() == channel.lower():
                        if CLIENTS.get(message.nickname) == channel:
                            self.send_packet(Message("ERROR","","","Nickname already in use!"))
                        else:
                            CLIENTS[message.nickname] = message.channel
                            # Broadcast join message
                            self.broadcast(Message('SERVER', None, None, f"{message.nickname} has joined the chat!"))
                            self.send_packet(Message("OK", message.nickname, channel, ""))
                            break
                        
                # self.send_packet(Message("ERROR","","","Invalid channel!"))

                break
            
            elif message.command == 'MESSAGE':
                self.message_to_channel(message)
                break
            
            elif message.command == 'PRIVATE':
                self.send_private_message(message)
                break
            
            elif message.command == 'QUIT':
                self.handle_quit(message.nickname)
                break
            
            elif message.command == "DISCONNECT":
                # Server doesn't have to do anything since client already left 
                break
                
            elif message.command == 'TEST':
                self.test_message(message)
                break
            
            else:
                print("mitä vittua")
                print(message.__str__)
                pass

    def handle_timeout(self):
        print("no timeout") # doesen't work :DDDDDDDDDDDDDD

if __name__ == '__main__':
    HOST, PORT = "localhost", 8000
    with ThreadingTCPServer((HOST, PORT), ChatServerHandler) as server:
        print(f"Server listening on {HOST}:{PORT}")
        server.serve_forever()
