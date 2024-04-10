from time import sleep
import libary as lib

if __name__ == "__main__":
    while True:
        try:
            lib.connect()
            lib.test_message()
            lib.disconnect()
            sleep(5)
        except KeyboardInterrupt:
            print("\nThank you for using my software!\n")
            exit(0)