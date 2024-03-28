import socket

IP = "localhost"
SEND_PORT = 8085
RECV_PORT = 8086

send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rec_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rec_socket.bind((IP,RECV_PORT))

def send_signal(device_name, signal):
    """Send signal to device"""
    send_socket.sendto(f"{device_name}:{signal:10.6f}".encode(),(IP,SEND_PORT))


def getReading(device_name):
    send_socket.sendto(f"{device_name}:0".encode(),(IP,SEND_PORT))
    data, _ = rec_socket.recvfrom(1024)
    data = data.decode()
    return float(data)
