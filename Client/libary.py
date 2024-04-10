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
    data =f"{message.command}|{message.nickname}|{message.channel}|{message.content}"
    print(f"sending: {data}") #DEBUG
    SOCK.sendall(data.encode())

def receive_packet() -> str:
    data = str(SOCK.recv(PACKET_SIZE).decode())
    print(f"received: {data}") #DEBUG
    return data

# Connect to server and send data
def connect(ip="localhost", port=8000, nickname="default"):
    try:
        global SOCK, PACKET_SIZE, NICKNAME
        ADDR = (ip, port)
        SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SOCK.bind(ADDR)
        SOCK.connect(ADDR)
        
        send_packet(Message("CONNECT", nickname, "", ""))
        recv = receive_packet().split('|')
        if recv[0] == "CHANNELS":
            NICKNAME = recv[1]
            print(f"Connection established, Channels:\n{recv[3]}")
        
        return
    except Exception as e:
        print("Error: ",e)

def join_channel(type: str, channel: str):
    global SOCK, CHANNEL
    
    send_packet(Message("JOIN", NICKNAME, channel, ""))
    recv = receive_packet().split('|')
    if recv[0] == "OK":
        CHANNEL = recv[2]
        
        # Start thread to receive messages
        receive_thread = threading.Thread(target=receive_message)
        receive_thread.start()

        # Send thread to send messages
        send_thread = threading.Thread(target=send_message)
        send_thread.start() 
        send_thread.join() # blocks the menu to run until this thread is terminated
    elif recv[0] == "ERROR":
        print(f"Server: {recv[3]}")
    else:
        print("something unexpected happened")


def disconnect():
    global SOCK
    if SOCK is None:
        print("\nNo connection to close")
        return
    
    send_packet(Message("DISCONNECT", "", "", ""))
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
        send_packet(Message("JOIN", NICKNAME, CHANNEL, msg))

def receive_message():
    global SOCK
    while True:
        # check if there is a connection
        if SOCK is None:
            print("Connection hasn't been established, use connect() first.")
            break
        
        # Receive message data and decode it
        data = receive_packet()
        if data == None:
            print("connection has been closed.")
            break
        
        print(f"data: {data}") # DEBUG
        
        # Split data into message components
        data = data.split('|')
        
        if len(data) != 4:
            continue
        else:
            command = data[0] if data[0] is not None else ""
            nickname = data[1] if data[1] is not None else ""
            channel = data[2] if data[2] is not None else ""
            content = data[3] if data[3] is not None else ""
            if command == "MESSAGE":
                print(f"{nickname}@{channel}: {content}") # DEBUG
            else:
                print(f"{command} ignored")
        
        # TODO: print the text to client

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