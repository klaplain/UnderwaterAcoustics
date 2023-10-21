import customtkinter
import tkinter
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

import time
import spidev

import datetime

import RPi.GPIO as GPIO

import json

DIRECTORY = 0
RECORD = 1
STOP = 2
DATETIME = 3
LOCATION =4
SAVE = 5
FORMAT = 6
DELETE = 7
FILEXFER = 8

# Open the file for reading
with open("config.cfg", "r") as config_file:
    # Load the dictionary from the file
    config_dict = json.load(config_file)

# Print the contents of the dictionary
# print(config_dict)

#defaults for global variables
sampling_freq=config_dict.get("sampling_freq")
gain=config_dict.get("gain")
fourbytestoread=[0,0,0,0]
twobytestoread=[0,0]
onebytetoread=[0]
AcqSubSystemReady = "Busy"

# We only have SPI bus 0 available to us on the Pi
bus = 0

#Device is the chip select pin. Set to 0 or 1, depending on the connections
device = 1

# Enable SPI
spi = spidev.SpiDev()

# Open a connection to a specific bus and device (chip select pin)
spi.open(bus, device)

# Set SPI speed and mode
spi.max_speed_hz = 5000000
spi.mode = 0

def record():
    set_datetime()
    time.sleep(0.5)  # need to give the STM32 a break
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass 
    print("Recording Start")
    file_number = int(FileNumbertextbox.get("0.0","end"))
    duration = int(durationtextbox.get("0.0","end"))*1000
    msg= [RECORD,((sampling_freq >>8) & 0xff),(sampling_freq & 0xff),gain,((duration >>8) & 0xff),(duration & 0xff),((file_number >>8) & 0xff),(file_number & 0xff)]
    spi.writebytes(msg)
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass 
    print("Recording Complete")


def deletefile():
    print("Delete File")
    file_number = int(FileNumbertextbox.get("0.0","end"))
    msg= [DELETE,((file_number >>8) & 0xff),(file_number & 0xff),0,0,0,0,0,0]
    spi.writebytes(msg)
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass 
    print("Deletion Complete")
        
def stoprecord():
    print("stop record")
    msg= [STOP,0,0,0,0,0,0,0]
    spi.writebytes(msg)
   
        
def formatsd():
    print("format sd")
    msg= [FORMAT,0,0,0,0,0,0,0]
    spi.writebytes(msg)
   
def set_datetime():
    print("Set datetime")
    now=datetime.datetime.now()
    msg= [DATETIME,now.hour,now.minute,now.second,4,now.month,now.day,now.year-2000,0]
    spi.writebytes(msg)    

def gain_select_callback(choice):
    global gain
    print("gain select clicked:", choice)
    gain=int(choice)
    config_dict.update({"gain": gain})
    with open("config.cfg", "w") as config_file:
        json.dump(config_dict, config_file)  # encode dict into JSON
    

def duration_callback(choice):
    global duration
    print("duration changed:", choice)
    duration=int(choice)
    config_dict.update({"duration": duration})
    with open("config.cfg", "w") as config_file:
        json.dump(config_dict, config_file)  # encode dict into JSON
    
def sampling_freq_callback(choice):
    global sampling_freq
    print("sampling freq clicked:", choice)
    sampling_freq = int(choice)
    config_dict.update({"sampling_freq": sampling_freq})
    with open("config.cfg", "w") as config_file:
        json.dump(config_dict, config_file)  # encode dict into JSON
    
def radiobutton_event():
    print("radiobutton toggled, current value:", radio_var.get())

def save():
    print("Saving") 
    
    Tk().withdraw()
    filename = asksaveasfilename(filetypes=[("WAV file", ".wav")],initialdir="/home/underwater/WAV_Files")
    print(filename)
       
    file_number = int(FileNumbertextbox.get("0.0","end"))
    msg= [SAVE,((file_number >>8) & 0xff) ,(file_number & 0xff),0,0,0,0,0]
    spi.writebytes(msg)    
    
    #open file for writing on RASPI.  We can do this to kill time before the AcqSystem is ready
    f=open(filename,"wb")
        
    # AcqSystem is getting filelength
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass    
    spi.xfer(fourbytestoread)
    TotalBytes= (fourbytestoread[0])+(fourbytestoread[1]<<8)+(fourbytestoread[2]<<16)+(fourbytestoread[3]<<24)
    TotalInts=TotalBytes>>1
    print("Bytes =", TotalBytes,"Ints =",TotalInts)
    
    tic = time.perf_counter()
    
    #Get file data
    for this_int in range(TotalInts):
        while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
            pass 
        spi.xfer(twobytestoread)
        f.write(twobytestoread[0].to_bytes(1,'big'))
        f.write(twobytestoread[1].to_bytes(1,'little'))
    
    toc = time.perf_counter()
    print(f"Time to save {toc - tic:0.4f} seconds")
    
    f.close()
    print("save done")
    
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass

def filexfer():
    print("File Transfer") 
    
    filename = "test.wav"
           
    file_number = int(FileNumbertextbox.get("0.0","end"))
    msg= [FILEXFER,((file_number >>8) & 0xff) ,(file_number & 0xff),0,0,0,0,0]
    spi.writebytes(msg)    
    
    #open file for writing on RASPI.  We can do this to kill time before the AcqSystem is ready
    f=open(filename,"wb")
        
    # AcqSystem is getting filelength
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass    
    spi.xfer(fourbytestoread)
    TotalBytes= (fourbytestoread[0])+(fourbytestoread[1]<<8)+(fourbytestoread[2]<<16)+(fourbytestoread[3]<<24)
    TotalInts=TotalBytes>>1
    print("Bytes =", TotalBytes,"Ints =",TotalInts)
    
    tic = time.perf_counter()
    
    #Get file data
    for this_int in range(TotalInts):
        while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
            pass 
        spi.xfer(twobytestoread)
        f.write(twobytestoread[0].to_bytes(1,'big'))
        f.write(twobytestoread[1].to_bytes(1,'little'))
    
    toc = time.perf_counter()
    print(f"Time to save {toc - tic:0.4f} seconds")
    
    f.close()
    print("xfer done")
    
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass
    
def directory():
    print("Directory Request")  
    msg= [DIRECTORY,0,0,0,0,0,0,0]
    directory_listing=""
    dirtextbox.configure(state="normal")  # configure textbox to be updated
    dirtextbox.delete("0.0", "end")  # delete all text
    spi.writebytes(msg)
    while True:
        while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
            pass 
        spi.xfer(onebytetoread)
        directory_listing=directory_listing+chr(onebytetoread[0])
        if onebytetoread[0]==12:
            break
    dirtextbox.insert("0.0", directory_listing)  # insert at line 0 character 0         
    dirtextbox.configure(state="disabled")  # configure textbox to be read-only
    print("End of Directory")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
                                      
root = customtkinter.CTk();
root.geometry("600x1000")
root.title("BARN Underwater Acoustics")
      
frame = customtkinter.CTkFrame(master=root)
frame.grid(row=0,column=0,   padx=10,pady =10)

label = customtkinter.CTkLabel(master=frame, text="Acquisition Manager",anchor="center", font=("Roboto",24))
label.grid(row=0, column=0, padx=10, pady=10)

frame2 = customtkinter.CTkFrame(master=frame, border_width=5)
frame2.grid(row=1,column=0,  padx =10, pady=10)

frame5 = customtkinter.CTkFrame(master=frame2, border_width=5)
frame5.grid(row=1,column=0,  padx =10, pady=10)

BusyLabel = customtkinter.CTkLabel(master=frame2, text=AcqSubSystemReady)
BusyLabel.grid(row=1,column=1,  padx =10, pady=10)

def GPIO_Going_Ready(channel):
    AcqSubSystemReady="Ready"
    print("Ready")
    BusyLabel.configure(text="Ready")
    time.sleep(0.5)
    AcqSubSystemReady="Busy"
    BusyLabel.configure(text="Busy")
    print("Busy")
    
def Update_StatusReady():
    print("..Ready")
    BusyLabel.configure(text="Ready")

def Update_StatusBusy():
    print("..Busy")
    BusyLabel.configure(text="Busy")

    
radio_var = tkinter.IntVar(value=0)
radiobutton_1 = customtkinter.CTkRadioButton(master=frame5, text="Free Run",command=radiobutton_event, variable= radio_var, value=1)
radiobutton_1.grid(row=1,column=0,  padx=10, pady=10)
radiobutton_2 = customtkinter.CTkRadioButton(master=frame5, text="Duration (secs)",command=radiobutton_event, variable= radio_var, value=2)
radiobutton_2.grid(row=2, column=0, padx=10, pady=10)
radio_var.set(2)
durationtextbox = customtkinter.CTkTextbox(master=frame5, width=100, height =10, corner_radius=3)
durationtextbox.grid(row=2,column=1,  padx=10, pady=10)
durationtextbox.insert("0.0",config_dict.get("duration"))

freqLabel = customtkinter.CTkLabel(master=frame2, text="Sampling Freq (kHz)")
freqLabel.grid(row=4, column=0,sticky="e")

freqmenu = customtkinter.CTkOptionMenu(master=frame2, values=["12", "25","50", "100", "200", "266", "320","400","533", "800"],command=sampling_freq_callback)
freqmenu.set(config_dict.get("sampling_freq"))
freqmenu.grid(row=4,column=1,  padx=20, pady=10)

gainLabel = customtkinter.CTkLabel(master=frame2, text="Gain")
gainLabel.grid(row=5, column=0,sticky="e")

gainmenu = customtkinter.CTkOptionMenu(master=frame2, values=["1", "2", "4", "8", "16"],command=gain_select_callback)
gainmenu.set(config_dict.get("gain"))
gainmenu.grid(row=5,column=1,  padx=5, pady=10)

FileNumberLabel = customtkinter.CTkLabel(master=frame2, text="File Number", anchor = "e")
FileNumberLabel.grid(row=6, column=0, padx=10, pady=10,sticky="e")
FileNumbertextbox = customtkinter.CTkTextbox(master=frame2, width=100, height =10, corner_radius=3)
FileNumbertextbox.grid(row=6, column=1, padx=10, pady=10)
FileNumbertextbox.insert("0.0","0")

recordbutton = customtkinter.CTkButton(master=frame2, text="Record", fg_color="red",command = record)
recordbutton.grid(row=7, column=0, padx=5, pady=20)

stopbutton = customtkinter.CTkButton(master=frame2, text="Stop",fg_color="black", border_color="white", text_color="white", command = stoprecord)
stopbutton.grid(row=7, column=1, padx=5, pady=20)

frame3 = customtkinter.CTkFrame(master=root, border_width=5)
frame3.grid(row=2, column=0,  padx=60,pady =20)

HydrophoneArrayNameLabel = customtkinter.CTkLabel(master=frame3, text="Hydrophone Array Name")
HydrophoneArrayNameLabel.grid(row=6, column=0, padx=10, pady=10)
HydrophoneArrayNametextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
HydrophoneArrayNametextbox.grid(row=6, column=1, padx=10, pady=10)
HydrophoneArrayNametextbox.insert("0.0",config_dict.get("hydrophone_name"))

ProjectNameLabel = customtkinter.CTkLabel(master=frame3, text="Project Name")
ProjectNameLabel.grid(row=7, column=0)
ProjectNametextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
ProjectNametextbox.grid(row=7, column=1, padx=10, pady=10)
ProjectNametextbox.insert("0.0",config_dict.get("project_name"))

LatLabel = customtkinter.CTkLabel(master=frame3, text="Lat")
LatLabel.grid(row=8, column=0)
Lattextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Lattextbox.grid(row=8, column=1, pady=10)
Lattextbox.insert("0.0",config_dict.get("latitude"))
LongLabel = customtkinter.CTkLabel(master=frame3, text="Long")
LongLabel.grid(row=8, column=2)
Longtextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Longtextbox.grid(row=8, column=3, padx=10, pady=10)
Longtextbox.insert("0.0",config_dict.get("longitude"))

frame4 = customtkinter.CTkFrame(master=root, border_width=5)
frame4.grid(row=11, column=0,  padx=60,pady =20)

savebutton = customtkinter.CTkButton(master=frame4, text="Save", fg_color="green", command = save)
savebutton.grid(row=0, column=1, padx=10, pady=10)

deletebutton = customtkinter.CTkButton(master=frame4, text="Delete File",fg_color="black", border_color="white", text_color="white", command = deletefile)
deletebutton.grid(row=0, column=2, padx=5, pady=20)

formatbutton = customtkinter.CTkButton(master=frame4, text="Format SD",fg_color="black", border_color="white", text_color="white", command = formatsd)
formatbutton.grid(row=0, column=3, padx=5, pady=20)

directorybutton = customtkinter.CTkButton(master=frame4, text="Directory", fg_color="purple", command = directory)
directorybutton.grid(row=1, column=1, padx=10, pady=10)

filexferbutton = customtkinter.CTkButton(master=frame4, text="File transfer",fg_color="black", border_color="white", text_color="white", command = filexfer)
filexferbutton.grid(row=1, column=2, padx=5, pady=20)

dirtextbox = customtkinter.CTkTextbox(master=root, width=400, height =200,padx=10,corner_radius=3)
dirtextbox.grid(row=12, column=0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) # STM32 SPI Busy
#GPIO.setup(17, GPIO.OUT) # Record Enable
#GPIO.output(17, GPIO.LOW)
#GPIO.setup(22, GPIO.OUT) # STM RESET
#GPIO.output(17, GPIO.HIGH)


set_datetime()
time.sleep(0.5)  # need to give the STM32 a break
directory()

while False:
    record()
    time.sleep(1)

root.mainloop()
