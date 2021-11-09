from tkinter import *
import time
import pandas as pd

df = pd.read_csv('config.csv')

print(df.to_dict())

dict_data = df.to_dict()

cloud_region=dict_data['cloud_region'][0]
num_messages=dict_data['num_messages'][0]
project_id=dict_data['project_id'][0]
device_id=dict_data['device_id'][0]

print(cloud_region)
print(num_messages)
print(project_id)
print(device_id)

window=Tk()
window.title("Device Config Tool")
window.geometry('600x400')

#button1=Button(window,text='Register Device', fg="#263D75", font=('Arial',14))
#button1.grid(row=0, column=1, sticky=E)


lable1=Label(window, text= 'Region Name', fg='blue', bg='white', font=('Arial',14))
lable1.grid(row=1, column=1, padx=5, pady=10)
        
dataRegion=StringVar()#Region name entry data type

textbox1=Entry(window, textvariable=dataRegion, fg='black', font=('Arial',14))
textbox1.grid(row=1, column=2)

lable2=Label(window, text= 'Project ID', fg='blue', bg='white', font=('Arial',14))
lable2.grid(row=2, column=1, padx=5, pady=10)

dataProjectID=StringVar()#Project ID name entry data type

textbox2=Entry(window,textvariable=dataProjectID, fg='black', font=('Arial',14))
textbox2.grid(row=2, column=2)

lable3=Label(window, text= 'Device ID', fg='blue', bg='white', font=('Arial',14))
lable3.grid(row=3, column=1, padx=5, pady=10)

dataDeviceID=StringVar()#Device ID name entry data type

textbox3=Entry(window, textvariable=dataDeviceID, fg='black', font=('Arial',14))
textbox3.grid(row=3, column=2)

lable4=Label(window, text= 'Number of Messages', fg='blue', bg='white', font=('Arial',14))
lable4.grid(row=4, column=1, padx=5, pady=10)

dataNumberofMessages=StringVar()#Number of messages to be output by edge sensor

textbox4=Entry(window, textvariable=dataNumberofMessages, fg='black', font=('Arial',14))
textbox4.grid(row=4, column=2)


dataRegion.set(cloud_region)
dataProjectID.set(project_id)
dataDeviceID.set(device_id)
dataNumberofMessages.set(num_messages)

def myFunction(): #Device Configuration
    i = 0
    while i<0xfffff:
        i=i+1

    configlabel.config(text='Device info entered is:'+str(dataRegion.get()+str(dataProjectID.get()+str(dataDeviceID.get()+str(dataNumberofMessages.get())))))

button2=Button(window, text='Start Detection', command=myFunction, bg='blue', fg="yellow", font=('Arial',14))
button2.grid(row=5, column=1, sticky=E)

configlabel=Label(window, fg='purple',font=('Arial',14))
configlabel.grid(row=6, column=1, sticky=W, pady=10)


window.mainloop()