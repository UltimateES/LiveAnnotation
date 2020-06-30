import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Button
import matplotlib.image as mpimg
import cv2
import random
from shapely.geometry import Point, Polygon
from tkinter import filedialog
import pandas as pd
import os
import numpy as np
import time
import tkinter as tk
from datetime import datetime,timedelta
import pickle
import sys
from termcolor import colored, cprint
from tkinter import *
from tkinter import messagebox

def SelectFolder():
    root = tk.Tk()
    root.withdraw()
    global VideoDirectoryPath,TxtFile
    VideoDirectoryPath = filedialog.askopenfilename()
    print(VideoDirectoryPath)
    LoadAutomatedAnnotationData()
    GetVideoFile()
    GetPandasFile()
    os.system("echo >"+ os.path.join(VideoDirectoryPath.replace(".mp4","Annotation"),"TrackMapping.csv"))
    TxtFile = os.path.join(VideoDirectoryPath.replace(".mp4","Annotation"),"TrackMapping.csv")
    return "Selected Folder : " + str(VideoDirectoryPath)

def LoadAutomatedAnnotationData():
    global allPandasEntries
    allPandasEntries = []
    if(VideoDirectoryPath.endswith(".mp4")):
        VideoFile = VideoDirectoryPath
        xyz=pd.read_csv(VideoFile.replace(".mp4",".mp4.txttrack"))
        xyz=xyz[(xyz.CID == 1) | (xyz.CID == 2) | (xyz.CID == 3) | (xyz.CID == 5) | (xyz.CID == 7)]
        allPandasEntries.append(xyz)
    else:
        print("given file is not Video File with Expected Track File")
    print(allPandasEntries)
    try:
        os.mkdir(VideoDirectoryPath.replace(".mp4","Annotation"))
    except OSError:
        print ("Creation of the directory %s failed" % VideoDirectoryPath.replace(".mp4","Annotation"))
    else:
        print ("Successfully created the directory %s " % VideoDirectoryPath.replace(".mp4","Annotation"))
    CameraConfigurationFile = os.path.join(VideoDirectoryPath.replace(".mp4","Annotation"),"AllAnnotationFile.pickle")
    fileObject = open(CameraConfigurationFile,'wb')
    pickle.dump(allPandasEntries,fileObject)
    fileObject.close()

def GetVideoFile():
    global VideoBuffer
    VideoBuffer = cv2.VideoCapture(VideoDirectoryPath)
    print("Video Buffer Created Globally")
    return 1

def GetPandasFile():
    global PandasBuffer
    PandasBuffer = allPandasEntries[0]
    return 1

def GetCurrentFrameVehicle(vehindex):
    global CurrentFrameVehicle
    VehicleID = PandasBuffer["FrameID"]==int(vehindex)
    ff=PandasBuffer[VehicleID]
    CurrentFrameVehicle=[]
    for index, row in ff.iterrows():
        CurrentFrameVehicle.append([int(float(row[2])),int(float(row[3])), int(float(row[4])), int(float(row[5])), int(float(row[1])), int(float(row[8])), int(float(row[9]))])
    if(len(CurrentFrameVehicle)==0):
        return -1
    else:
        return len(CurrentFrameVehicle)


def func(Classification,VehicleID):
    PandasBuffer.loc[PandasBuffer['ID'] == VehicleID, 'b'] = 1
    with open(TxtFile, 'a') as configfile:
        configfile.write(str(Classification) + "," + str(VehicleID) + "\n")
    print(Classification)

FileCounter=0
FileCOunterOffset=10000000000000000
def AddAnnotationinLibrary(Classification):
    for i in range(len(Polyline)):
        VideoBuffer.set(1, int(Polyline[i][0]))
        ret, frame = VideoBuffer.read()
        if ret == True:
            FileCounter = FileCounter + 1
            FilenameCreation=FileCOunterOffset+FileCounter
            SFilenameCreation1 = str(FilenameCreation)+ ".jpg"
            SFilenameCreation2 = str(FilenameCreation)+ ".txt"
            ImageFile = os.path.join(VideoDirectoryPath,"Annotation",SFilenameCreation1)
            TxtFile = os.path.join(VideoDirectoryPath,"Annotation",SFilenameCreation2)
            x1=((x+w)/2)/wx
            y1=((y+h)/2)/hx
            w1= w/wx
            h1= h/hx
            with open(TxtFile, 'w') as configfile:
                configfile.write(str(Classification) + " " + str(x1) + " " + str(y1) + " " + str(w1) + " " + str(h1))

def showchoices(VehicleID):
	root = tk.Tk();
	mylist = ['Bike', 'Car', 'Taxi','Van','PickUp','Labour Bus','RTA BUS','School Bus','Other Bus','2 Axle','3 Axle','4 Axle','More than 4 Axle','Multi Trailers']
	for Classification in mylist:
		button = Button(root, text=Classification, command=lambda x=Classification: func(x,VehicleID))
		button.pack()
	button1 = Button(root, text="Ok Submit", command=root.quit)
	button1.pack()
	root.mainloop()
	root.destroy()

def click_and_pop(event, x, y, flags, param):
    global refPt, croppinga
    if event == cv2.EVENT_LBUTTONDOWN:
        for i in range(0,framecount):
            if (x in range(CurrentFrameVehicle[i][0],CurrentFrameVehicle[i][0]+CurrentFrameVehicle[i][2])) and (y in range(CurrentFrameVehicle[i][1],CurrentFrameVehicle[i][1]+CurrentFrameVehicle[i][3])):
                showchoices(CurrentFrameVehicle[i][4])
                refPt = [(x, y)]
                break;



def trackbar_callback(idx, value):
    global trackval,VideoBuffer
    print(value)
    VideoBuffer.set(1, value)

SelectFolder()

trackval = 0;
totalframes=VideoBuffer.get(cv2.CAP_PROP_FRAME_COUNT)
FPS = VideoBuffer.get(cv2.CAP_PROP_FPS)
print(totalframes,FPS)

cv2.namedWindow('Frame')
cv2.createTrackbar('TimeLine', 'Frame', 0, int(50000), lambda v: trackbar_callback(2, v))
cv2.setMouseCallback("Frame", click_and_pop)

if (VideoBuffer.isOpened()== False): 
  print("Error opening video stream or file")
while(VideoBuffer.isOpened()):
  ret, frame = VideoBuffer.read()
  if ret == True:
    xcv=time.time()
    framenumber=VideoBuffer.get(cv2.CAP_PROP_POS_FRAMES);
    framecount=GetCurrentFrameVehicle(framenumber)
    for i in range(0,framecount):
        frame = cv2.rectangle(frame, (CurrentFrameVehicle[i][0],CurrentFrameVehicle[i][1]), (CurrentFrameVehicle[i][0]+CurrentFrameVehicle[i][2],CurrentFrameVehicle[i][1]+CurrentFrameVehicle[i][3]), (0, 0, 255) if (CurrentFrameVehicle[i][6] < 0) else (0, 255, 0), 2)
        #print(CurrentFrameVehicle[i][6])
        frame = cv2.putText(frame, str(CurrentFrameVehicle[i][4]), (CurrentFrameVehicle[i][0],CurrentFrameVehicle[i][1]), 1,1, (255, 0, 0), 2, cv2.LINE_AA) 
    frame = cv2.putText(frame, str(int(framenumber)), (50, 50) , 1,3, (255, 0, 0), 2, cv2.LINE_AA) 
    cv2.imshow('Frame',frame)
    pressedkey =  cv2.waitKey(10) & 0xFF
    if pressedkey == ord('q'):
      break
    elif pressedkey == ord(' '):
      cv2.waitKey(0)
  else:
    break
VideoBuffer.release()
cv2.destroyAllWindows()