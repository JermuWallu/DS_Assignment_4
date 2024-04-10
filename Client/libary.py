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
CHANNEL = None # List of current channels
PACKET_SIZE = 2048 # default packet size
NICKNAME = None # Current nickname

def send_packet(message: Message):
    data =f"{message.command}|{message.nickname}|{message.channel}|{message.content}"
    print(f"sending: '{data}'") #DEBUG
    SOCK.sendall(data.encode())

def receive_packet() -> str:
    try:
        data = str(SOCK.recv(PACKET_SIZE).decode())
        print(f"received: '{data}'") #DEBUG
        return data
    except Exception as e:
        print(f"failed receiving packets: {e}")
        return None

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

def disconnect():
    global SOCK
    if SOCK is None:
        print("\nNo connection to close")
        return
    
    send_packet(Message("DISCONNECT", "", "", ""))
    sleep(1)
    SOCK.close()
    SOCK = None
    NICKNAME = None
    print("\nDisconnected from server")
    return

def join_channel(channel: str):
    global SOCK, CHANNEL
    
    send_packet(Message("JOIN", NICKNAME, channel, ""))
    recv = receive_packet().split('|')
    if recv[0] == "OK":
        CHANNEL = recv[2]
        
        print(f"\nConnected to channel {channel}")
        print("Type 'quit' to leave\n")
        # Start thread to receive messages
        receive_thread = threading.Thread(target=receive_message)
        receive_thread.start()

        # Send thread to send messages
        send_thread = threading.Thread(target=send_message)
        send_thread.start() 
        send_thread.join() # blocks the menu to run until this thread is terminated
        
        # this happpens after leaving a channel
        send_packet(Message("QUIT",NICKNAME,CHANNEL,""))
        CHANNEL = None
        sleep(1) #sleep so menu would be printed propely
        return
    elif recv[0] == "ERROR":
        print(f"Server: {recv[3]}")
    else:
        print("something unexpected happened")
    
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
        if msg.lower() == "quit":
            break
        
        
        # Encode message and send it to the server
        send_packet(Message("MESSAGE", NICKNAME, CHANNEL, msg))
    # print("ending send_message()") #DEBUG
    return

def receive_message():
    global SOCK, CHANNEL
    running = True
    while running:
        # check if there is a connection
        if SOCK is None:
            print("Connection hasn't been established, use connect() first.")
            break
        
        # Receive message data and decode it
        data = receive_packet()
        if len(data) == 0 or not data or CHANNEL is None: 
            print("connection has been closed.")
            break
        
        # print(f"data: {data}") # DEBUG, also done in receive_packet()
        
        # Split data into message components
        data = data.split('|')
        
        if len(data) != 4:
            break # This means if anybody sends an invalid packet this thread closes
        else:
            command = data[0] if data[0] is not None else ""
            nickname = data[1] if data[1] is not None else ""
            channel = data[2] if data[2] is not None else ""
            content = data[3] if data[3] is not None else ""
            if command == "MESSAGE":
                print(f"{nickname}{channel}: {content}") # DEBUG
            elif command == "QUIT": # doesn't have any checks :DDDDD
                # Server might send a QUIT message upon disconnect
                print(f"[Server] {content}")
                running = False  # Stop the thread
            else:
                print(f"{command} ignored")
        
        # TODO: print the text to client
    # print("ending receive_message()") #DEBUG
    return

def private_channel(channel: str):
    global SOCK, CHANNEL
    CHANNEL = channel
    
    print(f"\You are now chatting with '{channel}'")
    print("Type 'quit' to leave\n")
    # Start thread to receive messages
    receive_thread = threading.Thread(target=receive_private_message)
    receive_thread.start()

    # Send thread to send messages
    send_thread = threading.Thread(target=send_private_message)
    send_thread.start() 
    send_thread.join() # blocks the menu to run until this thread is terminated
    
    # this happpens after leaving a channel
    CHANNEL = None
    sleep(1) #sleep so menu would be printed propely
    return

def send_private_message():
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
        if msg.lower() == "quit":
            break
        
        
        # Encode message and send it to the server
        send_packet(Message("PRIVATE", NICKNAME, CHANNEL, msg))
    # print("ending send_message()") #DEBUG
    return

def receive_private_message():
    global SOCK, CHANNEL
    running = True
    while running:
        # check if there is a connection
        if SOCK is None:
            print("Connection hasn't been established, use connect() first.")
            break
        
        # Receive message data and decode it
        data = receive_packet()
        if len(data) == 0 or not data or CHANNEL is None: 
            print("connection has been closed.")
            break
        
        # print(f"data: {data}") # DEBUG, also done in receive_packet()
        
        # Split data into message components
        data = data.split('|')
        
        if len(data) != 4:
            break # This means if anybody sends an invalid packet this thread closes
        else:
            command = data[0] if data[0] is not None else ""
            nickname = data[1] if data[1] is not None else ""
            channel = data[2] if data[2] is not None else ""
            content = data[3] if data[3] is not None else ""
            if command == "PRIVATE":
                print(f"{nickname}{channel}: {content}") # DEBUG
            elif command == "QUIT": # doesn't have any checks :DDDDD
                # Server might send a QUIT message upon disconnect
                print(f"[Server] {content}")
                running = False  # Stop the thread
            else:
                print(f"{command} ignored")
        
        # TODO: print the text to client
    # print("ending receive_message()") #DEBUG
    return

def menu() -> int:
    print("\nHello and welcome to Jere's texter!")
    print("""
          Choices:
          1) Connect to a server
          2) join a text channel
          3) enter a private chat
          4) disconnect fron server
          5) exit program
          """)
    
    return int(input("select: "))