import datetime

def get_size(n):
    size_list = ['B', 'KB', 'MB', 'GB']
    for size in size_list:
        if n < 1024:
            return f"{n:.2f}{size}"
        else:
            n = n / 1024
    return f"{n:.2f} GB"

def format_log_line(cpu,ram, disk_read, disk_write,net_sent, net_recv):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp},{cpu},{ram},{disk_read},{disk_write},{net_sent},{net_recv}\n"

def append_to_file(filename,text):
    try:
        with open(filename, 'a') as f:
            f.write(text)
        return True
    except (FileNotFoundError, PermissionError):
        return False