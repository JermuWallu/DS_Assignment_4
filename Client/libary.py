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
    SOCK.wfile.write(f"{message.command}|{message.nickname}|{message.channel}|{message.content}".encode())

# Connect to server and send data
def connect(ip="localhost", port=8000):
    try:
        global SOCK, PACKET_SIZE
        ADDR = (ip, port)
        SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SOCK.connect(ADDR)
        
        send_packet(Message("CONNECT", "", "", ""))
        recv_msg = str(SOCK.rfile.readline(), "utf-8").split('|')
        print(f"Connection established, Channels:\n{recv_msg[3]}")
        
        return
    except Exception as e:
        print("Error: ",e)

def join_channel(type: str, nickname: str, channel: str):
    global SOCK, NICKNAME
    
    send_packet(Message("JOIN", nickname, channel, ""))
    recv = str(SOCK.rfile.readline(), "utf-8").split('|')
    if recv[0] == "OK":
        NICKNAME = recv[1]
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
        data = SOCK.rfile.readline().decode()
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
    
def test_message():
    if SOCK is None:
        print("Connection hasn't been established, use connect() first.")
        return
    
    # Encode message data and send it
    send_packet(Message("TEST", "test_nick", "#test_channel", "this is a test"))
    received = str(SOCK.rfile.readline(), "utf-8")
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