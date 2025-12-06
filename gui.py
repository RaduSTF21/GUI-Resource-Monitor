import customtkinter as ctk
import psutil
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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
menu_frame=ctk.CTkFrame(root)
menu_frame.pack(side="left",fill="y")

def select_frame(frame_name):
    global home_frame, graph_frame
    home_frame.pack_forget()
    graph_frame.pack_forget()
    if frame_name == "home": home_frame.pack(side = "right", fill = "both", expand = True)
    elif frame_name == "graph":
        graph_frame.pack(side = "right", fill = "both", expand = True)


btn_home = ctk.CTkButton(menu_frame,text="Home",command=lambda: select_frame("home"))
btn_home.pack()
btn_graph = ctk.CTkButton(menu_frame,text="Graph",command=lambda: select_frame("graph"))
btn_graph.pack()

fig = plt.Figure(figsize=(5,5))
fig.set_facecolor("#242424")

ax = fig.add_subplot(111)
ax.set_facecolor("#242424")

canvas = FigureCanvasTkAgg(fig, graph_frame)

canvas.draw()

canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

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

    filter_frame = ctk.CTkFrame(history_window)

    start_time = ctk.CTkLabel(filter_frame, text="Start Time : ")
    start_entry = ctk.CTkEntry(filter_frame)


    scroll_frame = ctk.CTkScrollableFrame(history_window,width=680,height=480)
    scroll_frame.pack(padx=10,pady=10,fill = "both",expand=True)

    headers = ["Time", "CPU", "RAM", "Disk Read","Disk Write", "Net Sent", "Net Recv"]
    for col, row in enumerate(headers):
        ctk.CTkLabel(scroll_frame, text=row).grid(row=0,column=col,padx=5,pady=5)
    with open("log.csv", "r") as log:
     lines = log.readlines()
    #def monitor_log():
     #   with open("log.csv", "r") as log:
      #      lines = log.readlines()
       # line = lines[-1].strip()
        #line = line.split(",")
        #next_row = len(scroll_frame.winfo_children()) // 7

        #for col, info in enumerate(line):
         #   ctk.CTkLabel(scroll_frame, text=info).grid(row=next_row, column=col,padx=5,pady=5)

        #history_window.after(1000, monitor_log)
    #monitor_log()
    for index, row in enumerate(lines):
        line = row.strip().split(",")
        for index1, col in enumerate(line):
            ctk.CTkLabel(scroll_frame, text=col).grid(row=index+1,column=index1,padx=5,pady=5)



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
    global old_net,old_disk,cpu_history,ram_history,disk_history,net_history

    cpu_util = psutil.cpu_percent(interval=0)

    if cpu_util > 90:
        cpu_label.configure(text_color="red",text=f"CPU Utilization: {cpu_util}%")

    elif cpu_util > 80:
        cpu_label.configure(text_color="orange",text=f"CPU Utilization: {cpu_util}%")

    else:
        cpu_label.configure(text_color="white" ,text=f"CPU Utilization: {cpu_util}%")

    cpu_history.append(cpu_util)
    cpu_history = cpu_history[-60:]


    ram_util = psutil.virtual_memory().percent

    if ram_util > 90:
        ram_label.configure(text_color="red", text=f"RAM Utilization: {ram_util}%")

    elif ram_util > 80:
        ram_label.configure(text_color="orange", text=f"RAM Utilization: {ram_util}%")

    else:
        ram_label.configure(text_color="white",text=f"RAM Utilization: {ram_util}%")


    ram_history.append(ram_util)
    ram_history = ram_history[-60:]


    disk_util = psutil.disk_io_counters()

    disk_label.configure(text=f"Disk Utilization: {(disk_util.read_time-old_disk.read_time)/10+ (disk_util.write_time-old_disk.write_time)/10:.1f}%")

    disk_history.append(disk_util)
    disk_history = disk_history[-60:]

    net_stat = psutil.net_io_counters()

    net_label.configure(text=f"Network Utilization: {get_size(net_stat.bytes_recv-old_net.bytes_recv)}/s {get_size(net_stat.bytes_sent-old_net.bytes_sent)}/s")

    net_history.append(net_stat)
    net_history = net_history[-60:]

    details=f"{datetime.datetime.now()},{cpu_util},{ram_util},{disk_util.read_time-old_disk.read_time},{disk_util.write_time-old_disk.write_time},{net_stat.bytes_sent-old_net.bytes_sent},{net_stat.bytes_recv-old_net.bytes_recv}\n"

    old_disk = disk_util

    old_net = net_stat

    with open("log.csv", "a") as log:
        log.write(details)

    ax.clear()
    ax.grid(True,color="#404040")
    ax.tick_params( labelcolor="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")

    if var_cpu.get():
        ax.plot(cpu_history,label="CPU Utilization")
    if var_ram.get():
        ax.plot(ram_history,label="RAM Utilization")
    ax.legend()
    ax.set_ylim(0,100)
    canvas.draw()
    root.after(1000, update_stats)

update_stats()
select_frame("home")
root.mainloop()