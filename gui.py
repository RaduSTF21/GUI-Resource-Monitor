import customtkinter as ctk
import matplotlib
import psutil
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkcalendar import DateEntry
from collections import deque
from utils import get_size, format_log_line, append_to_file
from matplotlib.ticker import FuncFormatter

color_cpu = "#00BFFF"
color_ram = "#32CD32"
color_disk = "#FF8C00"
color_net = "#FF1493"

ctk.set_appearance_mode("dark")
root = ctk.CTk()
var_cpu = ctk.BooleanVar()
var_ram = ctk.BooleanVar()
var_disk = ctk.BooleanVar()
var_net = ctk.BooleanVar()

cpu_history = deque(maxlen=60)
disk_history = deque(maxlen=60)
net_history = deque(maxlen=60)
ram_history = deque(maxlen=60)

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
ax01 = ax.twinx()

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

def format_axis(x,pos):
    return get_size(x)


def show_history():
    history_window = ctk.CTkToplevel(root)
    history_window.title("History")
    history_window.geometry("800x700")



    hist_var_ram = ctk.BooleanVar(value=True)
    hist_var_cpu = ctk.BooleanVar(value=True)
    hist_var_disk = ctk.BooleanVar(value=True)
    hist_net_recv = ctk.BooleanVar(value=True)
    hist_net_sent = ctk.BooleanVar(value=True)

    filter_frame = ctk.CTkFrame(history_window)
    filter_frame.pack(pady=10)

    start_time = ctk.CTkLabel(filter_frame, text="Start Date : ")
    start_time.pack()
    start_entry = DateEntry(filter_frame, width = 12, background='dark blue', foreground='white', borderwidth = 2, date_pattern='y-mm-dd')
    start_entry.pack()
    end_time = ctk.CTkLabel(filter_frame, text="End Date : ")
    end_time.pack()
    end_entry = DateEntry(filter_frame, width = 12, background='dark blue', foreground='white', borderwidth = 2, date_pattern='y-mm-dd')
    end_entry.pack()
    end_check = ctk.BooleanVar()
    end_btn = ctk.CTkCheckBox(filter_frame, text="Present ", variable=end_check)
    end_btn.pack()
    filter_button = ctk.CTkButton(filter_frame, text="Filter")
    filter_button.pack()

    plot_frame = ctk.CTkFrame(history_window, width=680, height=400)
    plot_frame.pack(padx=10, pady=10, fill="both", expand=True)

    checkbox_frame = ctk.CTkFrame(history_window)
    checkbox_frame.pack(fill="x", padx=10, pady=5)

    cb_ram = ctk.CTkCheckBox(checkbox_frame, text="RAM", variable=hist_var_ram)
    cb_ram.pack(side="left",padx=10)
    cb_cpu = ctk.CTkCheckBox(checkbox_frame, text="CPU", variable=hist_var_cpu)
    cb_cpu.pack(side="left",padx=10)
    cb_disk = ctk.CTkCheckBox(checkbox_frame, text="Disk", variable=hist_var_disk)
    cb_disk.pack(side="left",padx=10)
    cb_net_sent = ctk.CTkCheckBox(checkbox_frame, text="Net sent", variable=hist_net_sent)
    cb_net_sent.pack(side="left",padx=10)
    cb_net_recv = ctk.CTkCheckBox(checkbox_frame, text="Net recv", variable=hist_net_recv)
    cb_net_recv.pack(side="left",padx=10)







    def on_end_typing(event):
        end_check.set(False)

    def on_present_toggled():
        if end_check.get():
            end_entry.delete(0, "end")
            apply_filter()

    end_entry.bind("<KeyRelease>", on_end_typing)
    end_btn.configure(command=on_present_toggled)

    def apply_filter():
        global first_date_str
        for child in plot_frame.winfo_children():
            child.destroy()

        fig1 = plt.Figure(figsize=(5, 5))
        fig1.set_facecolor("#242424")

        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor("#242424")
        canvas1 = FigureCanvasTkAgg(fig1, plot_frame)
        canvas1.draw()

        toolbar = NavigationToolbar2Tk(canvas1,plot_frame)
        toolbar.update()



        canvas1.get_tk_widget().pack(side="top", fill="both", expand=True)

        time = []
        ram_usage = []
        cpu_usage = []
        net_usage_sent = []
        net_usage_recv = []
        disk_usage = []
        try:
            with open("log.csv", "r") as log:
                lines = log.readlines()
        except FileNotFoundError:
            lines = []
        except PermissionError:
            lines = []

        filter_start = datetime.datetime.now()
        filter_end = datetime.datetime.now()
        default_start = datetime.datetime.now()
        if len(lines) > 0:
            try:
                first_date_str = lines[0].split(',')[0]
                default_start = datetime.datetime.strptime(first_date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass


        if start_entry.get() == "":
            filter_start = default_start
        else:
            filter_start = datetime.datetime.strptime(start_entry.get()+" 00:00:00", "%Y-%m-%d %H:%M:%S")

        if end_check.get() or end_entry.get() == "":
            filter_end = datetime.datetime.now()
        else:
            try :
                filter_end = datetime.datetime.strptime(end_entry.get()+" 23:59:59", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                filter_end = datetime.datetime.now()




        for line in lines:
            line = line.strip().split(',')
            if len(line) < 7 :
                continue
            try:
                current_time = datetime.datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S")
                if filter_start <= current_time <= filter_end:
                    val_ram = float(line[1])
                    val_cpu = float(line[2])
                    val_disk = (float(line[3]) + float(line[4])) /10
                    val_net_sent = float(line[5])
                    val_net_recv = float(line[6])

                    if len(time) > 0 and time[-1] is not None and (current_time - time[-1] > datetime.timedelta(seconds=5) ):
                        time.append(None)
                        ram_usage.append(None)
                        cpu_usage.append(None)
                        disk_usage.append(None)
                        net_usage_recv.append(None)
                        net_usage_sent.append(None)

                    time.append(current_time)
                    ram_usage.append(val_ram)
                    cpu_usage.append(val_cpu)
                    disk_usage.append(val_disk)
                    net_usage_sent.append(val_net_sent)
                    net_usage_recv.append(val_net_recv)
            except ValueError:
                continue


        ax1.clear()
        ax1.grid(True, color="#404040")
        ax1.tick_params(labelcolor="white")
        for spine in ax1.spines.values():
            spine.set_edgecolor("white")
        ax2 = ax1.twinx()
        ax2.clear()


        ax2.tick_params(labelcolor="white")
        for spine in ax2.spines.values():
            spine.set_edgecolor("white")
        if hist_var_ram.get():
            ax1.plot(time,ram_usage, label="Ram",color = color_ram)
        if hist_var_cpu.get():
            ax1.plot(time,cpu_usage, label="CPU", color = color_cpu)
        if hist_net_sent.get():
            ax2.plot(time,net_usage_sent, label="Net sent", color = color_net)
        if hist_net_recv.get():
            ax2.plot(time,net_usage_recv, label="Net recv",color = "red")
        if hist_var_disk.get():
            ax2.plot(time,disk_usage, label="Disk",color = color_disk)
        ax2.yaxis.set_major_formatter(FuncFormatter(format_axis))
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1+lines2,labels1+labels2,loc="upper left")
        ax1.set_ylim(0,100)
        canvas1.draw()

        # headers = ["Time", "CPU", "RAM", "Disk Read","Disk Write", "Net Sent", "Net Recv"]
        # for col, row in enumerate(headers):
        #     ctk.CTkLabel(scroll_frame, text=row).grid(row=0,column=col,padx=5,pady=5)
        # with open("log.csv", "r") as log:
        #     lines = log.readlines()
        # start = datetime.datetime.strptime(start_entry.get(), '%Y-%m-%d')
        # if end_check.get():
        #     end = datetime.datetime.now()
        # else :
        #     end = datetime.datetime.strptime(end_entry.get(), "%Y-%m-%d")
        # index = 2
        #
        # entries = 0
        #
        # for row in lines:
        #     row = row.strip().split(',')
        #     time = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        #     if start <= time <= end:
        #         entries = entries+1
        #
        # start_index = 0
        #
        # for ind, row in enumerate(lines):
        #     row = row.strip().split(',')
        #     time = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        #
        #     if time >= start :
        #         start_index = ind
        #         break
        #
        # for row in range(start_index,start_index+entries,max(1,entries//100)):
        #     if row >= len(lines): break
        #     line = lines[row].strip().split(',')
        #     for index1, col in enumerate(line):
        #         ctk.CTkLabel(scroll_frame, text=col).grid(row=index,column=index1,padx=5,pady=5)
        #     index = index+1









    cb_ram.configure(command=apply_filter)
    cb_disk.configure(command=apply_filter)
    cb_cpu.configure(command=apply_filter)
    cb_net_sent.configure(command=apply_filter)
    cb_net_recv.configure(command=apply_filter)
    filter_button.configure(command=apply_filter)
    history_window.after(100,apply_filter)


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
    #for index, row in enumerate(lines):
     #   line = row.strip().split(",")
      #  for index1, col in enumerate(line):
       #     ctk.CTkLabel(scroll_frame, text=col).grid(row=index+1,column=index1,padx=5,pady=5)



history_button = ctk.CTkButton(home_frame,text="History",command=show_history)
history_button.pack()




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



    ram_util = psutil.virtual_memory().percent

    if ram_util > 90:
        ram_label.configure(text_color="red", text=f"RAM Utilization: {ram_util}%")

    elif ram_util > 80:
        ram_label.configure(text_color="orange", text=f"RAM Utilization: {ram_util}%")

    else:
        ram_label.configure(text_color="white",text=f"RAM Utilization: {ram_util}%")


    ram_history.append(ram_util)



    disk_util = psutil.disk_io_counters()
    val_disk = (disk_util.read_time - old_disk.read_time)/10 + (disk_util.write_time- old_disk.write_time)/10

    disk_label.configure(text=f"Disk Utilization: {val_disk:.1f}%")

    disk_history.append(val_disk)


    net_stat = psutil.net_io_counters()
    current_speed = (net_stat.bytes_recv-old_net.bytes_recv) +(net_stat.bytes_sent-old_net.bytes_sent)
    net_label.configure(text=f"Network Utilization: {get_size(net_stat.bytes_recv-old_net.bytes_recv)}/s {get_size(net_stat.bytes_sent-old_net.bytes_sent)}/s")

    net_history.append(current_speed)


    details=format_log_line(cpu_util,ram_util,disk_util.read_time-old_disk.read_time,disk_util.write_time-old_disk.write_time,net_stat.bytes_sent-old_net.bytes_sent,net_stat.bytes_recv-old_net.bytes_recv)

    old_disk = disk_util

    old_net = net_stat
    append_to_file("log.csv",details)


    ax.clear()
    ax.grid(True,color="#404040")
    ax.tick_params( labelcolor="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")
    ax01.clear()
    ax01.tick_params(labelcolor="white")
    for spine in ax01.spines.values():
        spine.set_edgecolor("white")

    if var_cpu.get():
        ax.plot(cpu_history,label="CPU Utilization", color=color_cpu)
    if var_ram.get():
        ax.plot(ram_history,label="RAM Utilization",color=color_ram)
    if var_disk.get():
        ax01.plot(disk_history,label="Disk Utilization",color=color_disk)
    if var_net.get():
        ax01.plot(net_history,label="Network Utilization",color=color_net)
    ax01.yaxis.set_major_formatter(FuncFormatter(format_axis))

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax01.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    ax.set_ylim(0,100)
    canvas.draw()
    root.after(1000, update_stats)

update_stats()
select_frame("home")
root.mainloop()