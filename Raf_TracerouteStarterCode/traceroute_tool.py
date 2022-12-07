from icmplib import traceroute
from tkinter import *
import statistics as s
from time import gmtime, strftime
import json
import requests
import plotly.express as px
import pandas as pd
import csv

# Init window and gui
root = Tk()
root.title('Traceroute Program')
root.config(background="LIGHT GRAY")
root.geometry("1180x720")
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

fhops_label = Label(root, text="first hop", width=10, font=('Courier', 10, 'bold'),borderwidth=2, relief="ridge")
fhops_label.place(x=660, y=657)
fhops_e = Entry(root, width=5, borderwidth=5, font=('Courier', 15, 'bold'))
fhops_e.insert(0, "1")
fhops_e.place(x=670, y=679)

fast_label = Label(root, text="fast", width=10, font=('Courier', 10, 'bold'),borderwidth=2, relief="ridge")
fast_label.place(x=760, y=657)
fast_e = Entry(root, width=5, borderwidth=5, font=('Courier', 15, 'bold'))
fast_e.insert(0, "0")
fast_e.place(x=770, y=679)

fam_label = Label(root, text="family", width=10, font=('Courier', 10, 'bold'),borderwidth=2, relief="ridge")
fam_label.place(x=860, y=657)
fam_e = Entry(root, width=5, borderwidth=5, font=('Courier', 15, 'bold'))
fam_e.insert(0, "4")
fam_e.place(x=870, y=679)

# Display the main view of the program
displayed_message="---------------------- TRACEROUTE PROGRAM --------------------------\n>>> "
abel = Text(root,width=68,height=23, font=('Courier', 18, 'bold'), bg="LIGHT YELLOW",fg="BLACK", borderwidth=5, relief="ridge")
abel.insert(END, displayed_message)
abel.place(x=10, y=5)

# average list of round trips
avg_rtt_list = []
current_host = ""

# Important for showing which average in 2d lists is fastest
def sort_averages(sub_li):
    l = len(sub_li)
    for i in range(0, l):
        for j in range(0, l-i-1):
            if (sub_li[j][1] > sub_li[j + 1][1]):
                tempo = sub_li[j]
                sub_li[j]= sub_li[j + 1]
                sub_li[j + 1]= tempo
    return sub_li

# useful for extracting latitude and longitude of an ip addresses, and writing it the csv file
def write_locations(ip_addresses):
    csvfile = open('dataset.csv', 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(["Address", "Lat", "Long", "Listed"])
    #df = pd.read_csv("dataset.csv")
    i = 1
    for ip in ip_addresses:
        response = requests.get(f'https://ipapi.co/{ip}/json/').json()
        row = [i, response.get("latitude"), response.get("longitude"), 125000]
        writer.writerow(row)
        i+=1

# Show the different ip addresses in different parts of the world from the locations in the csv file
def show_world_trace():
    df = pd.read_csv("dataset.csv")
    df.dropna(
        axis=0,
        how='any',
        thresh=None,
        subset=None,
        inplace=True
    )
    color_scale = [(0, 'orange'), (1,'red')]
    fig = px.scatter_mapbox(df, 
                            lat="Lat", 
                            lon="Long", 
                            hover_name="Address", 
                            hover_data=["Address", "Listed"],
                            color="Listed",
                            color_continuous_scale=color_scale,
                            size="Listed",
                            zoom=0, 
                            height=800,
                            width=800)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()

# open log file for reading and appending any new info at the end
logfile = open("log.txt", "a+")

# Insert text to gui AND add finding to log file
def print_to_gui(widget: Text, _text):
    widget.insert(END, _text+"\n>>> ")
    t = strftime("%Y-%m-%d %H:%M:%S")
    logfile.write(f"[{t}] "+_text)

# updates json file with correct ip and the average times, and if there are any packages dropped we save their corresponding ip as well
def update_json(ip, avg, std, drpPackets):
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

    with open("dropped.json", "r+") as jsonFile1:
        dataDropped = json.load(jsonFile1)

        if ip in dataDropped:
            dataDropped[ip] = [*set(dataDropped[ip] + drpPackets)] #eliminates duplicates
        elif drpPackets!=[]:
            dataDropped[ip] = drpPackets
        else:
            return
        jsonFile1.seek(0)
        json.dump(dataDropped, jsonFile1)
        jsonFile1.truncate()

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
    times_avarages_list = sort_averages(times_avarages_list)
    for time_avg_std in times_avarages_list:
        avg = format(time_avg_std[1], ".3f")
        std = format(time_avg_std[2], ".3f")
        gui_msg += f"{time_avg_std[0]} -------> {avg}    {std}\n"
    print_to_gui(abel, gui_msg)

# This function will show the ips that usually drop packets
def show_ips_dropped():
    with open("dropped.json", "r+") as jsonFile:
        data = json.load(jsonFile)
    
    if current_host=='':
        print_to_gui(abel, "Error: no hosts provided.\n")
        return

    gui_msg = f"Hops with * for {current_host}\n"
    ips_list = data[current_host]
    for ip in ips_list:
        gui_msg += f"{ip}\n"
    print_to_gui(abel, gui_msg)

# place the buttons
offset = 145
initial = 10
wid = 10
hei = 3
letter_size = 18
avg_button = Button(root, text ="calculate\naverage", command = calculate_avg, height=hei,width=wid, font=('Courier', letter_size, 'bold'),borderwidth=5, relief="raised")
avg_button.place(x=1000,y=initial)

sd_button = Button(root, text ="calculate\nstandard\ndeviation", height=hei ,width=wid, command = calculate_sd, font=('Courier', letter_size, 'bold'),borderwidth=5, relief="raised")
sd_button.place(x=1000,y=initial+offset)

times_comp_button = Button(root, text ="compare\ntimes", height=hei,width=wid, command = show_avg_std_times_table, font=('Courier', letter_size, 'bold'),borderwidth=5, relief="raised")
times_comp_button.place(x=1000,y=initial+offset*2)

times_comp_button = Button(root, text ="show\ndropped", height=hei,width=wid, command = show_ips_dropped, font=('Courier', letter_size, 'bold'),borderwidth=5, relief="raised")
times_comp_button.place(x=1000,y=initial+offset*3)

world_button = Button(root, text ="WORLD\nTRACE", height=hei,width=wid, command = show_world_trace, font=('Courier', letter_size, 'bold'),borderwidth=5, relief="raised")
world_button.place(x=1000,y=initial+offset*4)

# Heart of the traceroute algorithm
def PressedEnter():
    global avg_rtt_list
    global current_host
    hops = traceroute(address=e.get(), count=int(count_ping.get()), interval=float(inter_e.get()), timeout=float(timeout_e.get()), first_hop=int(fhops_e.get()),max_hops=int(max_hops_e.get()),fast=bool(int(fast_e.get())), family=int(fam_e.get()))
    current_host = e.get()
    avg_rtt_list = []
    gui_mes = ''
    last_distance = 0
    last_addr = ''
    dropped_packets = []
    all_addrs = []
    for hop in hops:
        if last_distance + 1 != hop.distance:
            gui_mes = gui_mes + '**             Some Gateways are not responding\n'
            dropped_packets.append(last_distance+1)
        else:
            if hop.distance < 10:
                formatted_hop = '0' + str(hop.distance)
            else:
                formatted_hop = str(hop.distance)
            gui_mes = gui_mes + f'{formatted_hop}             {hop.address} -> {hop.avg_rtt} ms\n'
            avg_rtt_list.append(hop.avg_rtt)
            last_addr = hop.address
            all_addrs.append(hop.address)
        last_distance = hop.distance    
    update_json(current_host, calculate_avg(False), calculate_sd(False), dropped_packets)
    write_locations(all_addrs)
    e.delete(0, END)
    gui_mes = f'Traceroute for {last_addr}\nDistance/TTL   Address -> Average round-trip time\n' + gui_mes
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