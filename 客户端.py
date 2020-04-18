import socket
import struct
import pickle
import time
import os
import zipfile

server_ip = '192.168.1.2'
server_port = 5200
file_dir = os.path.dirname(os.path.abspath(__file__))
header_struct = struct.Struct('i1024s')
data_struct = struct.Struct('1024s')


def print_file(header):
    file_name = header['file_name']
    file_size = header['file_size']
    file_ctime = header['file_ctime']
    file_atime = header['file_atime']
    file_mtime = header['file_mtime']
    print('文件名：%s' % file_name)
    print('文件大小：%s' % file_size)
    print('文件创建时间：%s' % time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(file_ctime)))
    print('文件最近访问时间：%s' % time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(file_atime)))
    print('文件最近修改时间：%s' % time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(file_mtime)))


def print_progress(percent, width=50):
    if percent >= 100:
        percent = 100
    # 字符串拼接的嵌套使用
    show_str = ('[%%-%ds]' % width) % (int(width * percent / 100) * '>')
    print('\r%s %d%%' % (show_str, percent), end='')


def get(client):
    # 接受序列化的header数据包
    packed_header = client.recv(1024 + 4)
    # 解包得到序列化的header的长度和header正文
    header_size, header_s = header_struct.unpack(packed_header)
    # 大小为0则说明查无此文件
    if header_size == 0:
        return False
    # 否则开始传
    else:
        # 反序列化得到header正文
        header = pickle.loads(header_s)
        file_name = header['file_name']
        file_size = header['file_size']
        print_file(header)
        with open('%s\\%s' % (file_dir, 'x.zip'), 'wb') as f:
            recv_size = 0
            while recv_size < file_size:
                res = client.recv(1024)
                f.write(res)
                recv_size += len(res)
                recv_per = int(recv_size / file_size * 100)
                print_progress(recv_per)
        return True


def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')

        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()


def unzip_file(zip_src, dst_dir):
    zipfile.is_zipfile(zip_src)
    fz = zipfile.ZipFile(zip_src, 'r')

    for file in fz.namelist():
        fz.extract(file, dst_dir)


def run():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    while True:
        file_name = input("你想传输的文件叫什么名字呢[输入end断开连接]: ").strip()
        zipDir(file_name, file_name + '.zip')
        client.send((file_name + '.zip').encode('utf-8'))
        start = time.time()
        print('-' * 80)
        if not get(client):
            print('文件名错误')
        else:
            end = time.time()
            print('\n传输完成')
            print('传输时间：', end - start)
        print('-' * 80)
        unzip_file(r"E:\vs\pycharm\项目二\x.zip", r"E:\vs\pycharm\项目二")
        os.remove(file_name + '.zip')
        os.remove(r"E:\vs\pycharm\项目二\x.zip")
    client.close()


if __name__ == '__main__':
    run()
