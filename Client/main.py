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
                print("parameters incorrect, using default ip:port (localhost:8000)")
                ip="localhost" 
                port=8000
            lib.connect(ip,int(port))

        elif choice == 2:
            nickname = input("Please enter your nickname: ")  
            lib.join_channel("PUBLIC", nickname, "#general")
            
        elif choice == 3:
            nickname = input("Please enter your nickname: ")
            target = input("who do you want to start private chat with?: ")
            lib.join_channel("PUBLIC", nickname, target)
            
        elif choice == 4:
            lib.disconnect()
            
        elif choice == 5:
            print("\nThank you for using my software!\n")
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