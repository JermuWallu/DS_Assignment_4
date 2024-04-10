import libary as lib
"""
    Used documentation:
        https://docs.python.org/3.9/library/socketserver.html#module-socketserver    
        https://docs.python.org/3.9/library/threading.html
    
"""

def main():
    try:
        print("Hello and welcome to Jere's texter!")
        choice = lib.menu()
        
        if choice == 1:
            ip = str(input("give the servers ip address you want to connect: "))
            port = input("give the servers port you want to connect: ")
            if len(ip) == 0:
                print("parameters incorrect, using default ip:port (localhost:8000)")
                ip="localhost" 
                port=8000
            
            nickname = input("Please enter your nickname: ")    
            lib.connect(ip,int(port))
            lib.set_nickname(nickname)
        elif choice == 2:
            lib.send_msg_to_channel()
        elif choice == 3:
            lib.send_private_msg()
        elif choice == 4:
            lib.disconnect()
        elif choice == 5:
            print("\nThank you for using my software!\n")
            exit(0)
        elif choice == 10:
            lib.test_message()
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