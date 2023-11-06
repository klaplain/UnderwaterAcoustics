#  Import libraries
import customtkinter
import tkinter
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename
import time
import spidev
import datetime
import RPi.GPIO as GPIO
import json

# SPI Command IDs for Acquisition Subsystem
DIRECTORY = 0
RECORD = 1
STOP = 2
DATETIME = 3
LOCATION =4
SAVE = 5
FORMAT = 6
DELETE = 7
FILEXFER = 8

# Read config file to get last used settings for slections and drop downs
with open("config.cfg", "r") as config_file:
    # Load the dictionary from the file
    config_dict = json.load(config_file)


# Set defaults for global variables
sampling_freq=config_dict.get("sampling_freq")
gain=config_dict.get("gain")
fourbytestoread=[0,0,0,0]
twobytestoread=[0,0]
onebytetoread=[0]
AcqSubSystemReady = "Busy"

# Initialize SPI interface
bus = 0  # We only have SPI bus 0 available to us on the Pi
device = 1 #Device is the chip select pin. Set to 0 or 1, depending on the connections
spi = spidev.SpiDev() # Enable SPI
spi.open(bus, device) # Open a connection to a specific bus and device (chip select pin)
spi.max_speed_hz = 5000000  # Set SPI speed and mode
spi.mode = 0

def record():  # Function to initiate recording on Acquisition Subsystem
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


def deletefile():  # Function to delete file on Acquisition Subsystem
    print("Delete File")
    file_number = int(FileNumbertextbox.get("0.0","end"))
    msg= [DELETE,((file_number >>8) & 0xff),(file_number & 0xff),0,0,0,0,0,0]
    spi.writebytes(msg)
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass 
    print("Deletion Complete")
        
def stoprecord(): # Function to stop recording (not currently implemented)
    print("stop record")
    msg= [STOP,0,0,0,0,0,0,0]
    spi.writebytes(msg)
   
        
def formatsd(): # Function to format SD card on Acquisition Subsystem
    print("format sd")
    msg= [FORMAT,0,0,0,0,0,0,0]
    spi.writebytes(msg)
   
def set_datetime(): # Function to set date and time on Acquisition Subsystem
    print("Set datetime")
    now=datetime.datetime.now()
    msg= [DATETIME,now.hour,now.minute,now.second,4,now.month,now.day,now.year-2000,0]
    spi.writebytes(msg)    

def gain_select_callback(choice): # Callback function for selection of Gain
    global gain
    print("gain select clicked:", choice)
    gain=int(choice)
    config_dict.update({"gain": gain})
    with open("config.cfg", "w") as config_file:
        json.dump(config_dict, config_file)  # encode dict into JSON
    

def duration_callback(choice):  # Callback function for selection of Duration
    global duration
    print("duration changed:", choice)
    duration=int(choice)
    config_dict.update({"duration": duration})
    with open("config.cfg", "w") as config_file:
        json.dump(config_dict, config_file)  # encode dict into JSON
    
def sampling_freq_callback(choice): # Callback function for selection of Sampling Frequency
    global sampling_freq
    print("sampling freq clicked:", choice)
    sampling_freq = int(choice)
    config_dict.update({"sampling_freq": sampling_freq})
    with open("config.cfg", "w") as config_file:
        json.dump(config_dict, config_file)  # encode dict into JSON
    
def radiobutton_event():
    print("radiobutton toggled, current value:", radio_var.get())

def save():   # Function to save Acquisition Subsystem file to raspi
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
    
    f.write(createwavmetadata())
    
    f.close()
    print("save done")
    
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass

def filexfer():  # testing only
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
    
    
    lst = [1] *16384
    op = [None] * 10000000
    
    while True:
        tic = time.perf_counter()
        rcvd = spi.xfer3(lst)
        toc = time.perf_counter()
        print(f"Time to save {toc - tic:0.4f} seconds")
    
    
    #Get file data
    for this_int in range(TotalInts):
        while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
            pass 
        spi.xfer(twobytestoread)
        f.write(twobytestoread[0].to_bytes(1,'big'))
        f.write(twobytestoread[1].to_bytes(1,'little'))
    
    toc = time.perf_counter()
    print(f"Time to save {toc - tic:0.4f} seconds")
    
    addwavemetadata()
    
    f.close()
    print("xfer done")
    
    while GPIO.input(27) == GPIO.HIGH  :   #loop while still Busy
        pass
    
def directory():   # Function to request SD card directory from Acquisition Subsystem
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

def createwavmetadata(): # Function to create Subchunk3 meta data string
    INAM = pad_odd(HydrophoneArrayNametextbox.get("0.0","end"))
    IPRD = pad_odd(ProjectNametextbox.get("0.0","end"))
    IART = pad_odd("UW Acoustics Investigator")  # Placeholder
    ICMT = pad_odd("UW Acoustics Comments") # Placeholder
    ICRD = pad_odd(str(datetime.datetime.now()))
    IGNR = pad_odd(Lattextbox.get("0.0","end")+"  "+Longtextbox.get("0.0","end"))
    ITRK = pad_odd(str(gain))

    INFO_byte_string = b"INFO"

    INAM_length_string = (len(INAM)+1).to_bytes(4, 'little')
    INAM_byte_string =b''.join([b'INAM',INAM_length_string,INAM.encode('utf-8'),bytes([0])])

    IPRD_length_string = (len(IPRD)+1).to_bytes(4, 'little')
    IPRD_byte_string =b''.join([b'IPRD',IPRD_length_string,IPRD.encode('utf-8'),bytes([0])])

    IART_length_string = (len(IART)+1).to_bytes(4, 'little') 
    IART_byte_string =b''.join([b'IART',IART_length_string,IART.encode('utf-8'),bytes([0])])

    ICMT_length_string = (len(ICMT)+1).to_bytes(4, 'little') 
    ICMT_byte_string =b''.join([b'ICMT',ICMT_length_string,ICMT.encode('utf-8'),bytes([0])])

    ICRD_length_string = (len(ICRD)+1).to_bytes(4, 'little') 
    ICRD_byte_string =b''.join([b'ICRD',ICRD_length_string,ICRD.encode('utf-8'),bytes([0])])

    IGNR_length_string = (len(IGNR)+1).to_bytes(4, 'little') 
    IGNR_byte_string =b''.join([b'IGNR',IGNR_length_string,IGNR.encode('utf-8'),bytes([0])])

    ITRK_length_string = (len(ITRK)+1).to_bytes(4, 'little') 
    ITRK_byte_string =b''.join([b'ITRK',ITRK_length_string,ITRK.encode('utf-8'),bytes([0])])

    FINAL_byte_string= b''.join([INFO_byte_string,INAM_byte_string,IPRD_byte_string,IART_byte_string,ICMT_byte_string,ICRD_byte_string,IGNR_byte_string,ITRK_byte_string])

    SCK3_length = len(FINAL_byte_string)
    SCK3=b''.join([b'LIST',len(FINAL_byte_string).to_bytes(4, 'little'), FINAL_byte_string])

    return SCK3

def pad_odd(input_string):  # Function to ensure string is an odd number of characters long ready for use in WAV file meta data
    if (len(input_string) % 2) == 0:
        return input_string + ' '
    else:
        return input_string
    
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
