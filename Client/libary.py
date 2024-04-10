import socket
import threading
from time import sleep


# Class for message structure
class Message:
    def __init__(self, command, nickname, channel, content):
        self.command = command
        self.nickname = nickname
        self.channel = channel
        self.content = content


# Global variables
SOCK = None
CHANNEL = "" # List of current channels
PACKET_SIZE = 2048 # default packet size
NICKNAME = "" # Current nickname

def send_packet(message: Message):
    SOCK.sendall(f"{message.command}|{message.nickname}|{message.channel}|{message.content}".encode())

# Connect to server and send data
def connect(ip="localhost", port=8000):
    try:
        global SOCK, PACKET_SIZE
        ADDR = (ip, port)
        SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCK.connect(ADDR)
        
        message = Message("JOIN", "", "", "")
        send_packet(message)
        recv_msg = str(SOCK.recv(PACKET_SIZE), "utf-8").split('|')
        print(f"Connection established, Channels:\n{recv_msg[3]}")
        
        return
    except Exception as e:
        print("Error: ",e)

def join_channel(type: str, nickname: str, channel: str):
    global SOCK, NICKNAME
    

    message = Message("JOIN", nickname, channel, "")
    send_packet(message)
    recv = str(SOCK.recv(PACKET_SIZE), "utf-8").split('|')
    if recv[0] == "OK":
        NICKNAME = recv[1]
        CHANNEL = recv[2]
        
        # Start thread to receive messages
        receive_thread = threading.Thread(target=receive_message)
        receive_thread.start()

        # Send thread to send messages
        send_thread = threading.Thread(target=send_message)
        send_thread.start() 
        # send_thread.join() # Wait for the send thread to finish
    elif recv[0] == "ERROR":
        print(f"Server: {recv[3]}")
    else:
        print("something unexpected happened")


def disconnect():
    global SOCK
    if SOCK is None:
        print("\nNo connection to close")
        return
    
    message = Message("DISCONNECT", "", "", "")
    send_packet(message)
    SOCK.close()
    SOCK = None
    print("\nDisconnected from server")
    return
    
def send_message():
    global SOCK, NICKNAME, CHANNEL
    while True:
        # check if there is a connection
        if SOCK is None:
            print("Connection hasn't been established, use connect() first.")
            break
            
        msg = input()
        if msg == None:
            continue
        
        # Handles leaving, easier to implement than keyboard shortcut
        if msg.lower() == "Quit":
            break
        
        
        # Encode message and send it to the server
        message = Message("JOIN", NICKNAME, CHANNEL, msg)
        send_packet(message)

def receive_message() -> Message:
    global SOCK
    while True:
        # check if there is a connection
        if SOCK is None:
            print("Connection hasn't been established, use connect() first.")
            break
        
        # Receive message data and decode it
        data = SOCK.request.recv(PACKET_SIZE).decode()
        if data == None:
            print("connection has been closed.")
            break
        
        
        print(f"PACKET: from {SOCK.client_address[0]}, data: {data}") # DEBUG
        
        
        # Split data into message components
        data = data.split('|')
        command = data[0] if data[0] is not None else ""
        nickname = data[1] if data[1] is not None else ""
        channel = data[2] if data[2] is not None else ""
        content = data[3] if data[3] is not None else ""
        
        # TODO: print the text to client
    
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