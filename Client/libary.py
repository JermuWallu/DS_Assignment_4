from time import sleep
import socket

# Class for message structure
class Message:
    def __init__(self, command, nickname, channel, content):
        self.command = command
        self.nickname = nickname
        self.channel = channel
        self.content = content


# Global variables
SOCK = None
CHANNELS = ['#general'] # List of current channels
PACKET_SIZE = 2048 # default packet size
NICKNAME = ""

# Connect to server and send data
def connect(ip="localhost", port=8000) -> list:
    try:
        global SOCK, PACKET_SIZE
        ADDR = (ip, port)
        SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCK.connect(ADDR)
        
        message = Message("JOIN", "", "", "")
        SOCK.sendall(f"{message.command}|{message.nickname}|{message.channel}|{message.content}".encode())
        recv_msg = str(SOCK.recv(PACKET_SIZE), "utf-8").split('|')
        print("Connection established,")
        
        return list(recv_msg[3])
    except Exception as e:
        print("Error: ",e)

def disconnect():
    global SOCK
    if SOCK is None:
        print("\nNo connection to close")
        return
    
    message = Message("DISCONNECT", "", "", "")
    SOCK.sendall(f"{message.command}|{message.nickname}|{message.channel}|{message.content}".encode())
    SOCK.close()
    SOCK = None
    print("\nDisconnected from server")
    return
    
def send_message(message):
    global SOCK
    
    # check if there is a connection
    if SOCK is None:
        print("Connection hasn't been established, use connect() first.")
        
    # Encode message and send it to the server
    data = message.encode()
    SOCK.sendall(data)

def receive_message() -> Message:
    global SOCK
    
    # check if there is a connection
    if SOCK is None:
        print("Connection hasn't been established, use connect() first.")
        return
    
    # Receive message data and decode it
    data = SOCK.request.recv(PACKET_SIZE).decode()
    
    # Split data into message components
    data.split('|')
    print(f"PACKET: from {SOCK.client_address[0]}, data: {data}")
    command = data[0] if data[0] is not None else ""
    nickname = data[1] if data[1] is not None else ""
    channel = data[2] if data[2] is not None else ""
    content = data[3] if data[3] is not None else ""
    
    return Message(command, nickname, channel, content)

def join_channel(type: str, nickname: str, channel: str):
    global SOCK, NICKNAME
    
    print(f"joined {type} channel D:DDD:D:D:D")
    # message = Message("SET", nickname, "#general", "")
    # SOCK.sendall(f"{message.command}|{message.nickname}|{message.channel}|{message.content}".encode())
    # recv_message = str(SOCK.recv(PACKET_SIZE), "utf-8").split('|')
    
def test_message():
    if SOCK is None:
        print("Connection hasn't been established, use connect() first.")
        return
    
    # Encode message data and send it
    message = Message("TEST", "test_nick", "#test_channel", "this is a test")
    data = f"{message.command}|{message.nickname}|{message.channel}|{message.content}".encode()
    SOCK.sendall(data)
    received = str(SOCK.recv(PACKET_SIZE), "utf-8")
    print(received)

def menu() -> int:
    print("\nHello and welcome to Jere's texter!")
    print("""
          Choices:
          1) Connect to a server
          2) join a text channel
          3) join a private chat
          4) disconnect fron server
          5) exit program
          """)
    
    return int(input("select: "))