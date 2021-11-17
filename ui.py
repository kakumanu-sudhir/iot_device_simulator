from tkinter import *
import time
import pandas as pd
import asyncio
import threading

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

async def myFunction(configlabel): #Device Configuration
    configlabel.config(text='Button pressed')
    print("myFunction")
    i = 0
    while i<0xfffffff:
        i=i+1

    #configlabel.config(text='Device info entered is:'+str(dataRegion.get()+str(dataProjectID.get()+str(dataDeviceID.get()+str(dataNumberofMessages.get())))))
    configlabel.config(text='Button processing done')
    return

def _asyncio_thread(async_loop, configlabel):
    print("_asyncio_thread")
    async_loop.run_until_complete(myFunction(configlabel))


def do_tasks(async_loop, configlabel):
    """ Button-Event-Handler starting the asyncio part. """
    print("do_tasks")
    threading.Thread(target=_asyncio_thread, args=(async_loop,configlabel, )).start()


def main(async_loop):
    # root = Tk()
    # Button(master=root, text='Asyncio Tasks', command= lambda:do_tasks(async_loop)).pack()
    # buttonX = Button(master=root, text='Freezed???', command=do_freezed).pack()
    # root.mainloop()

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

    configlabel=Label(window, fg='purple',font=('Arial',14))
    configlabel.grid(row=6, column=1, sticky=W, pady=10)

    #button2=Button(window, text='Start Detection', command=lambda:myFunction(configlabel), bg='blue', fg="yellow", font=('Arial',14))
    button2=Button(window, text='Start Detection', command=lambda:do_tasks(async_loop, configlabel), bg='blue', fg="yellow", font=('Arial',14))
    button2.grid(row=5, column=1, sticky=E)

    window.mainloop()


if __name__ == '__main__':
    async_loop = asyncio.get_event_loop()
    main(async_loop)