import customtkinter
import tkinter


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
                                      
root = customtkinter.CTk();
root.geometry("600x700")
root.title("BARN Underwater Acoustics")

def login():
    print("test")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady =20, padx=60, fill = "both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="Acquisition Manager",anchor="center", font=("Roboto",24))
label.pack(padx=10, pady=20)

frame2 = customtkinter.CTkFrame(master=root)
frame2.pack(pady =20, padx=60, fill = "both", expand=True)

def radiobutton_event():
    print("radiobutton toggled, current value:", radio_var.get())

radio_var = tkinter.IntVar(value=0)
radiobutton_1 = customtkinter.CTkRadioButton(master=frame2, text="Free Run",command=radiobutton_event, variable= radio_var, value=1)
radiobutton_1.grid(column=0, row=1, pady=10)
radiobutton_2 = customtkinter.CTkRadioButton(master=frame2, text="Duration",command=radiobutton_event, variable= radio_var, value=2)
radiobutton_2.grid(column=0, row=2)
radio_var.set(1)
duration = customtkinter.CTkEntry(master=frame2, placeholder_text="Duration in secs")
duration.grid(column=1, row=2, pady=10)

def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)

optionmenu = customtkinter.CTkOptionMenu(master=frame2, values=["10kHz", "50kHz", "100kHz", "500kHz", "700kHz"],command=optionmenu_callback)
optionmenu.set("700kHz")
optionmenu.grid(column=0, row=4, pady=10)

button = customtkinter.CTkButton(master=frame2, text="Record", fg_color="red",command = login)
button.grid(row=5, column=0, pady=10)
button = customtkinter.CTkButton(master=frame2, text="Stop",fg_color="black", border_color="white", text_color="white", command = login)
button.grid(row=5, column=1, pady=10)

# checkbox = customtkinter.CTkCheckBox(master=frame, text= "Remember Me")
# checkbox.pack(pady=12, padx=10)

frame3 = customtkinter.CTkFrame(master=root)
frame3.pack(pady =20, padx=60, fill = "both", expand=True)

HydrophoneArrayNameLabel = customtkinter.CTkLabel(master=frame3, text="Hydrophone Array Name")
HydrophoneArrayNameLabel.grid(row=6, column=0)
HydrophoneArrayNametextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
HydrophoneArrayNametextbox.grid(row=6, column=1, pady=10)

ProjectNameLabel = customtkinter.CTkLabel(master=frame3, text="Project Name")
ProjectNameLabel.grid(row=7, column=0)
ProjectNametextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
ProjectNametextbox.grid(row=7, column=1, pady=10)

DateLabel = customtkinter.CTkLabel(master=frame3, text="Date")
DateLabel.grid(row=8, column=0)
Datetextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Datetextbox.grid(row=8, column=1, pady=10)

TimeLabel = customtkinter.CTkLabel(master=frame3, text="Time")
TimeLabel.grid(row=9, column=0)
Timetextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Timetextbox.grid(row=9, column=1, pady=10)

TimeLabel = customtkinter.CTkLabel(master=frame3, text="Lat")
TimeLabel.grid(row=10, column=0)
Timetextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Timetextbox.grid(row=10, column=1, pady=10)
TimeLabel = customtkinter.CTkLabel(master=frame3, text="Long")
TimeLabel.grid(row=10, column=2)
Timetextbox = customtkinter.CTkTextbox(master=frame3, width=100, height =10, corner_radius=3)
Timetextbox.grid(row=10, column=3, pady=10)

button = customtkinter.CTkButton(master=frame3, text="Save", fg_color="green", command = login)
button.grid(row=11, column=1, pady=10)
root.mainloop()