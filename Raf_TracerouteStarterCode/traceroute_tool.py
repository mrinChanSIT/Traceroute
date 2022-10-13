from icmplib import traceroute
from tkinter import *
import statistics as s
from time import gmtime, strftime
import json

# Init window and gui
root = Tk()
root.title('Traceroute Program')
root.config(background="LIGHT GRAY")
root.geometry("1280x720")
root.resizable(False, False)

# Options Labels and Parameters
ip_input = Label(root, text="Destination Host", width=28, font=('Courier', 10, 'bold'), borderwidth=2,relief="ridge")
ip_input.place(x=5, y=657)
e = Entry(root, width=18, borderwidth=5, font=('Courier', 15, 'bold'))
e.insert(0, "1.1.1.1")
e.place(x=10, y=679)

ping_label = Label(root, text="ping count", width=10, font=('Courier', 10, 'bold'),borderwidth=2,relief="ridge")
ping_label.place(x=265, y=657)
count_ping = Entry(root, width=5, borderwidth=5, font=('Courier', 15, 'bold'))
count_ping.insert(0, "2")
count_ping.place(x=270, y=679)

inter_label = Label(root, text="interval", width=10, font=('Courier', 10, 'bold'),borderwidth=2, relief="ridge")
inter_label.place(x=360, y=657)
inter_e = Entry(root, width=5, borderwidth=5, font=('Courier', 15, 'bold'))
inter_e.insert(0, "0.05")
inter_e.place(x=370, y=679)

timeout_label = Label(root, text="timeout", width=10, font=('Courier', 10, 'bold'),borderwidth=2, relief="ridge")
timeout_label.place(x=460, y=657)
timeout_e = Entry(root, width=5, borderwidth=5, font=('Courier', 15, 'bold'))
timeout_e.insert(0, "2")
timeout_e.place(x=470, y=679)

max_hops_label = Label(root, text="max hops", width=10, font=('Courier', 10, 'bold'),borderwidth=2, relief="ridge")
max_hops_label.place(x=560, y=657)
max_hops_e = Entry(root, width=5, borderwidth=5, font=('Courier', 15, 'bold'))
max_hops_e.insert(0, "20")
max_hops_e.place(x=570, y=679)

# Display the main view of the program
displayed_message="---------------------- TRACEROUTE PROGRAM --------------------------\n>>> "
abel = Text(root,width=68,height=23, font=('Courier', 18, 'bold'), bg="LIGHT YELLOW",fg="BLACK", borderwidth=5, relief="ridge")
abel.insert(END, displayed_message)
abel.place(x=10, y=5)

# average list of round trips
avg_rtt_list = []
current_host = ""

# open log file for reading and appending any new info at the end
logfile = open("log.txt", "a+")

# Insert text to gui AND add finding to log file
def print_to_gui(widget: Text, _text):
    widget.insert(END, _text+"\n>>> ")
    t = strftime("%Y-%m-%d %H:%M:%S")
    logfile.write(f"[{t}] "+_text)

# updates json file with correct ip and the average times
def update_json(ip, avg, std):
    with open("ips.json", "r+") as jsonFile:
        data = json.load(jsonFile)

        time_of_day = strftime("%H:%M:%S")
        if ip in data:
            data[ip].append([time_of_day, avg, std])
        else:
            data[ip] = []
            data[ip].append([time_of_day, avg, std])
        jsonFile.seek(0)
        json.dump(data, jsonFile)
        jsonFile.truncate()

# Calculate the average of all round trips
def calculate_avg(should_print=True):
    if avg_rtt_list==[]:
        print_to_gui(abel, f"Error: no host provided.\n")
    else:    
        avg = sum(avg_rtt_list)/len(avg_rtt_list)
        if should_print:
            print_to_gui(abel, f"Average rtt for {current_host}\n\n{avg}\n")
        return avg

# Calculate the standard deviation
def calculate_sd(should_print=True):
    if avg_rtt_list==[]:
        print_to_gui(abel, f"Error: no host provided.\n")
    else:
        st = s.stdev(avg_rtt_list)
        if should_print:
            print_to_gui(abel, f"Standard Deviation of rtt's for {current_host}\n\n{st}\n")
        return st

# compare averages and standardDevs with previous runs
def show_avg_std_times_table():
    with open("ips.json", "r+") as jsonFile:
        data = json.load(jsonFile)
    
    if current_host=='':
        print_to_gui(abel, "Error: no hosts provided.\n")
        return

    gui_msg = f"Time-Of-Day, Averages, Standard Deviation Table for {current_host}\n"
    times_avarages_list = data[current_host]
    for time_avg_std in times_avarages_list:
        avg = format(time_avg_std[1], ".3f")
        std = format(time_avg_std[2], ".3f")
        gui_msg += f"{time_avg_std[0]} -------> {avg}    {std}\n"
    print_to_gui(abel, gui_msg)

# place the buttons
avg_button = Button(root, text ="calculate\naverage", command = calculate_avg, height=3, font=('Courier', 10, 'bold'),borderwidth=5, relief="raised")
avg_button.place(x=1000,y=10)

sd_button = Button(root, text ="calculate\nstandard\ndeviation", height=3 , command = calculate_sd, font=('Courier', 10, 'bold'),borderwidth=5, relief="raised")
sd_button.place(x=1000,y=90)

times_comp_button = Button(root, text ="compare\ntimes", height=3, command = show_avg_std_times_table, font=('Courier', 10, 'bold'),borderwidth=5, relief="raised")
times_comp_button.place(x=1000,y=170)


# Heart of the traceroute algorithm
def PressedEnter():
    global avg_rtt_list
    global current_host
    hops = traceroute(address=e.get(), count=int(count_ping.get()), interval=float(inter_e.get()), timeout=float(timeout_e.get()), max_hops=int(max_hops_e.get()))
    current_host = e.get()
    avg_rtt_list = []
    gui_mes = f'Traceroute for {e.get()}\nDistance/TTL   Address -> Average round-trip time\n'
    last_distance = 0
    for hop in hops:
        if last_distance + 1 != hop.distance:
            gui_mes = gui_mes + '**             Some Gateways are not responding\n'
        else:
            if hop.distance < 10:
                formatted_hop = '0' + str(hop.distance)
            else:
                formatted_hop = str(hop.distance)
            gui_mes = gui_mes + f'{formatted_hop}             {hop.address} -> {hop.avg_rtt} ms\n'
            avg_rtt_list.append(hop.avg_rtt)
        last_distance = hop.distance
    update_json(current_host, calculate_avg(False), calculate_sd(False))
    e.delete(0, END)
    print_to_gui(abel, gui_mes)

def func(event):
    PressedEnter()

root.bind('<Return>', func)

# Close the window and log file
def on_closing():
    logfile.close()
    root.destroy()

def endit(event):
    on_closing()

root.bind('<Escape>', endit)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()