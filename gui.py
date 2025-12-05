import customtkinter as ctk
import psutil
import datetime

ctk.set_appearance_mode("dark")
root = ctk.CTk()
var_cpu = ctk.BooleanVar()
var_ram = ctk.BooleanVar()
var_disk = ctk.BooleanVar()
var_net = ctk.BooleanVar()

cpu_history = []
disk_history = []
net_history = []
ram_history = []

home_frame=ctk.CTkFrame(root)
graph_frame=ctk.CTkFrame(root)

cpu_check = ctk.CTkCheckBox(graph_frame,text="CPU Utilization", variable=var_cpu)
cpu_check.pack()
ram_check = ctk.CTkCheckBox(graph_frame,text="RAM Utilization", variable=var_ram)
ram_check.pack()
disk_check = ctk.CTkCheckBox(graph_frame,text="Disk Read", variable=var_disk)
disk_check.pack()
net_check = ctk.CTkCheckBox(graph_frame,text="Net", variable=var_net)
net_check.pack()


root.title('GUI-Resource-Monitor')
cpu_label = ctk.CTkLabel(home_frame, text="CPU : 0%")
cpu_label.pack()
ram_label = ctk.CTkLabel(home_frame, text="RAM : 0%")
ram_label.pack()
disk_label = ctk.CTkLabel(home_frame, text="Disk : 0%")
disk_label.pack()
net_label = ctk.CTkLabel(home_frame, text="Network : 0%")
net_label.pack()
old_net = psutil.net_io_counters()
old_disk = psutil.disk_io_counters()
def show_history():
    history_window = ctk.CTkToplevel(root)
    history_window.title("History")
    history_window.geometry("700x500")

    scroll_frame = ctk.CTkScrollableFrame(history_window,width=680,height=480)
    scroll_frame.pack(padx=10,pady=10,fill = "both",expand=True)

    headers = ["Time", "CPU", "RAM", "Disk Read","Disk Write", "Net Sent", "Net Recv"]
    for col, row in enumerate(headers):
        ctk.CTkLabel(scroll_frame, text=row).grid(row=0,column=col,padx=5,pady=5)

    def monitor_log():
        with open("log.csv", "r") as log:
            lines = log.readlines()
        line = lines[-1].strip()
        line = line.split(",")
        next_row = len(scroll_frame.winfo_children()) // 7

        for col, info in enumerate(line):
            ctk.CTkLabel(scroll_frame, text=info).grid(row=next_row, column=col,padx=5,pady=5)

        history_window.after(1000, monitor_log)
    monitor_log()


history_button = ctk.CTkButton(home_frame,text="History",command=show_history)
history_button.pack()


def get_size(n):
    size_list = ['B', 'KB', 'MB', 'GB']
    for size in size_list:
        if (n < 1024):
            return (f"{n:.2f}{size}")
        else:
            n = n / 1024

def update_stats():
    global old_net,old_disk

    cpu_util = psutil.cpu_percent(interval=0)

    if cpu_util > 90:
        cpu_label.configure(text_color="red",text=f"CPU Utilization: {cpu_util}%")

    elif cpu_util > 80:
        cpu_label.configure(text_color="orange",text=f"CPU Utilization: {cpu_util}%")

    else:
        cpu_label.configure(text_color="white" ,text=f"CPU Utilization: {cpu_util}%")

    cpu_history.append(cpu_util)

    ram_util = psutil.virtual_memory().percent

    if ram_util > 90:
        ram_label.configure(text_color="red", text=f"RAM Utilization: {ram_util}%")

    elif ram_util > 80:
        ram_label.configure(text_color="orange", text=f"RAM Utilization: {ram_util}%")

    else:
        ram_label.configure(text_color="white",text=f"RAM Utilization: {ram_util}%")

    ram_history.append(ram_util)

    disk_util = psutil.disk_io_counters()

    disk_label.configure(text=f"Disk Utilization: {(disk_util.read_time-old_disk.read_time)/10+ (disk_util.write_time-old_disk.write_time)/10:.1f}%")

    disk_history.append(disk_util)

    net_stat = psutil.net_io_counters()

    net_label.configure(text=f"Network Utilization: {get_size(net_stat.bytes_recv-old_net.bytes_recv)}/s {get_size(net_stat.bytes_sent-old_net.bytes_sent)}/s")

    net_history.append(net_stat)

    details=f"{datetime.datetime.now()},{cpu_util},{ram_util},{disk_util.read_time-old_disk.read_time},{disk_util.write_time-old_disk.write_time},{net_stat.bytes_sent-old_net.bytes_sent},{net_stat.bytes_recv-old_net.bytes_recv}\n"

    old_disk = disk_util

    old_net = net_stat

    with open("log.csv", "a") as log:
        log.write(details)
    root.after(1000, update_stats)

update_stats()

root.mainloop()