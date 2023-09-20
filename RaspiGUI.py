import customtkinter
import tkinter

import time
import spidev

import datetime

RECORD = 1
STOP = 2
DATETIME = 3
LOCATION =4

sampling_freq=700
gain=1

# We only have SPI bus 0 available to us on the Pi
bus = 0

#Device is the chip select pin. Set to 0 or 1, depending on the connections
device = 1

# Enable SPI
spi = spidev.SpiDev()

# Open a connection to a specific bus and device (chip select pin)
spi.open(bus, device)

# Set SPI speed and mode
spi.max_speed_hz = 500000
spi.mode = 0

# time.sleep(1)

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
                                      
root = customtkinter.CTk();
root.geometry("600x700")
root.title("BARN Underwater Acoustics")

def record():
    print("record", gain)
    file_number = 101
    msg= [RECORD]
    msg.append((sampling_freq >>8) & 0xff)
    msg.append(sampling_freq & 0xff)
    msg.append(gain)
    msg.append((file_number >>8) & 0xff)
    msg.append(file_number & 0xff)
    spi.writebytes(msg)
        
def stoprecord():
    print("stop record")
    msg= [STOP]
    spi.writebytes(msg)
    
def set_datetime():
    print("set datetime")
    now=datetime.datetime.now()
    msg= [DATETIME]
    msg.append(now.hour)
    msg.append(now.minute)
    msg.append(now.second)
    msg.append(4)
    msg.append(now.month)
    msg.append(now.day)
    msg.append((now.year >>8) & 0xff)
    msg.append(now.year & 0xff) 
    spi.writebytes(msg)    

frame = customtkinter.CTkFrame(master=root)
frame.grid(row=0,column=0,   padx=10,pady =10)

label = customtkinter.CTkLabel(master=frame, text="Acquisition Manager",anchor="center", font=("Roboto",24))
label.grid(row=0, column=0, padx=10, pady=10)

frame2 = customtkinter.CTkFrame(master=frame, border_width=5)
frame2.grid(row=1,column=0,  padx =10, pady=10)

frame5 = customtkinter.CTkFrame(master=frame2, border_width=5)
frame5.grid(row=1,column=0,  padx =10, pady=10)

def radiobutton_event():
    print("radiobutton toggled, current value:", radio_var.get())

radio_var = tkinter.IntVar(value=0)
radiobutton_1 = customtkinter.CTkRadioButton(master=frame5, text="Free Run",command=radiobutton_event, variable= radio_var, value=1)
radiobutton_1.grid(row=1,column=0,  padx=10, pady=10)
radiobutton_2 = customtkinter.CTkRadioButton(master=frame5, text="Duration",command=radiobutton_event, variable= radio_var, value=2)
radiobutton_2.grid(row=2, column=0, padx=10, pady=10)
radio_var.set(1)
duration = customtkinter.CTkEntry(master=frame5, placeholder_text="Duration in secs")
duration.grid(row=2,column=1,  padx=10, pady=10)

def gain_select_callback(choice):
    global gain
    print("gain select clicked:", choice)
    gain=int(choice)
    
def sampling_freq_callback(choice):
    global sampling_freq
    print("sampling freq clicked:", choice)
    sampling_freq = int(choice)

freqLabel = customtkinter.CTkLabel(master=frame2, text="Sampling Freq (kHz)")
freqLabel.grid(row=4, column=0)

freqmenu = customtkinter.CTkOptionMenu(master=frame2, values=["10", "50", "100", "500", "700"],command=sampling_freq_callback)
freqmenu.set("700")
freqmenu.grid(row=4,column=1,  padx=5, pady=10)

gainLabel = customtkinter.CTkLabel(master=frame2, text="Gain")
gainLabel.grid(row=5, column=0)

gainmenu = customtkinter.CTkOptionMenu(master=frame2, values=["1", "2", "4", "8", "16"],command=gain_select_callback)
gainmenu.set("1")
gainmenu.grid(row=5,column=1,  padx=5, pady=10)

button = customtkinter.CTkButton(master=frame2, text="Record", fg_color="red",command = record)
button.grid(row=6, column=0, padx=5, pady=10)
button = customtkinter.CTkButton(master=frame2, text="Stop",fg_color="black", border_color="white", text_color="white", command = stoprecord)
button.grid(row=6, column=1, padx=5, pady=10)

frame3 = customtkinter.CTkFrame(master=root, border_width=5)
frame3.grid(row=2, column=0,  padx=60,pady =20)

HydrophoneArrayNameLabel = customtkinter.CTkLabel(master=frame3, text="Hydrophone Array Name")
HydrophoneArrayNameLabel.grid(row=6, column=0, padx=10, pady=10)
HydrophoneArrayNametextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
HydrophoneArrayNametextbox.grid(row=6, column=1, padx=10, pady=10)

ProjectNameLabel = customtkinter.CTkLabel(master=frame3, text="Project Name")
ProjectNameLabel.grid(row=7, column=0)
ProjectNametextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
ProjectNametextbox.grid(row=7, column=1, padx=10, pady=10)

DateLabel = customtkinter.CTkLabel(master=frame3, text="Date")
DateLabel.grid(row=8, column=0)
Datetextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Datetextbox.grid(row=8, column=1, pady=10)

TimeLabel = customtkinter.CTkLabel(master=frame3, text="Time")
TimeLabel.grid(row=9, column=0)
Timetextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Timetextbox.grid(row=9, column=1, pady=10)

LatLabel = customtkinter.CTkLabel(master=frame3, text="Lat")
LatLabel.grid(row=10, column=0)
Lattextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Lattextbox.grid(row=10, column=1, pady=10)
LongLabel = customtkinter.CTkLabel(master=frame3, text="Long")
LongLabel.grid(row=10, column=2)
Longtextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Longtextbox.grid(row=10, column=3, padx=10, pady=10)

def save():
    print("save")

button = customtkinter.CTkButton(master=frame3, text="Save", fg_color="green", command = set_datetime)
button.grid(row=11, column=1, padx=10, pady=10)
root.mainloop()
