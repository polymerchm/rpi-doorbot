"""
return a tuple of the host name and the ip address
"""
import socket

def getIPinfo():
    name = socket.gethostname() + ".local"
    ip = socket.gethostbyname(name)
    return (name,ip)

if __name__ == '__main__':
    name,ip = getIPinfo()
    print(f"Host name is {name}, IP address is {ip}")
    
