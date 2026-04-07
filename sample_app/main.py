import os

def main():
    greeting = os.environ.get('GREETING', 'Hello')
    print(f"{greeting}, Docksmith World!")

if __name__ == '__main__':
    main()
