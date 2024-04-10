import libary as lib
"""
    Used documentation:
        https://docs.python.org/3.9/library/socketserver.html#module-socketserver    
        https://docs.python.org/3.9/library/threading.html
    
"""

def main():
    try:
        choice = lib.menu()
        
        if choice == 1:
            ip = str(input("give the servers ip address you want to connect: "))
            port = input("give the servers port you want to connect: ")
            
            if len(ip) == 0:
                # print("parameters incorrect, using default ip:port (localhost:8000)")
                ip="localhost" 
                port=8000
            nickname = input("Please enter your nickname: ")  
            lib.connect(ip,int(port), nickname)

        elif choice == 2:
            channel = input("what channel you want to join?: ")
            if len(channel) == 0:
                channel = "#general"
            lib.join_channel("PUBLIC", channel)
            
        elif choice == 3:
            target = input("who do you want to start private chat with?: ")
            lib.join_channel("PRIVATE", target)
            
        elif choice == 4:
            lib.disconnect()
            
        elif choice == 5:
            print("\nThank you for using my software!\n")
            lib.disconnect()
            exit(0)
            
        else:
            print("Unknown choice, try again.")
        
        
    except Exception as e:
        print("error: ",e)
    
    return

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("\nThank you for using my software!\n")
            exit(0)