# UnderwaterAcoustics
This is the code required for the Underwater Acoustics STM32 Acquisition SubSystem

main.c contains the necessary code to acquire an analog signal sampling at about 700kHz and storing the result to a .DAT file that contains the analog values.  Although the file has a WAV file header, the values are 16 bit unsigned values so the DAT file needs to be post-processed to convert it to a WAV file.  This post-processing can be done on a PC using the DATtoWAV.c program.

seeedtest15.ioc contains all the necessary CubeIDE configuration data to run main.c on the Seeed board

raspiGUI.py is a prototype of the GUI that could be used on a Raspberry Pi to control the acquisition subsystem
