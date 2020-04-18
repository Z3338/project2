import socket
import struct
import pickle
import time
import os

server_ip = '192.168.1.2'
server_port = 5200
file_dir = os.path.dirname(os.path.abspath(__file__))
header_struct = struct.Struct('i1024s')
data_struct = struct.Struct('1024s')


def send(file_name, client):
    file_path = os.path.join(file_dir, file_name)
    if os.path.isfile(file_path) == 0:
        client.send(header_struct.pack(*(0, b'0')))
    else:
        # 文件头
        header = {
            'file_name': file_name,
            'file_size': os.path.getsize(file_path),
            'file_ctime': os.path.getctime(file_path),
            'file_atime': os.path.getatime(file_path),
            'file_mtime': os.path.getmtime(file_path)
        }
        # 序列化header
        header_str = pickle.dumps(header)
        # 把序列化的header长度和header正文打包发送
        client.send(header_struct.pack(*(len(header_str), header_str)))
        with open(file_path, 'rb') as f:
            for line in f:
                client.send(line)


def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)
    print('Server start on')
    print('-> ip: %s port: %d' % (server_ip, server_port))
    while True:
        client, client_addr = server.accept()
        print('A new connection from %s' % client_addr[0])
        while True:
            try:
                request = client.recv(1024).decode('utf-8')
                if request == 'end':
                    break
                print('Send %s to %s' % (request, client_addr[0]))
                send(request, client)
            except ConnectionResetError:
                break
        client.close()
    server.close()


if __name__ == '__main__':
    run()
