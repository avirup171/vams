from __future__ import print_function
import sys
import os
from argparse import ArgumentParser
import cv2
import time
import logging as log
import numpy as np
import io
import detect as dt
from openvino.inference_engine import IENetwork, IEPlugin
from pathlib import Path
import json
sys.path.insert(0, str(Path().resolve().parent.parent))


class VideoCamera(object):
    def __init__(self):
        with open('config.json') as json_data_file:
            data=json.load(json_data_file)
        model=data["model_path"]
        device=data["device"]
        cpu_extension=data["cpu_extension"]
        plugin_dir=data["plugin_dir"]
        is_async_mode = True
        object_detection=dt.Detectors(device,model,cpu_extension,plugin_dir,is_async_mode)
        self.resultant_initialisation_object=object_detection.initialise_inference()
        input_stream = data["input"]
        
        
        print("Hello world")
        #Start video capturing process
        if input_stream==None or input_stream=="":
            self.cap = cv2.VideoCapture(0)
        else:
            self.cap = cv2.VideoCapture(input_stream)
        #Frame count
        self.video_len = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))
        self.out = cv2.VideoWriter("out_path.mp4", 0x00000021, 50.0, (frame_width, frame_height), True)
        self.cur_request_id = 0
        self.next_request_id = 1
        
        #self.cap = cv2.VideoCapture(input_stream)

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        #try:
        ret, frame = self.cap.read()

        initial_w = self.cap.get(3)
        initial_h = self.cap.get(4)
        res_inference=self.resultant_initialisation_object.process_frame(self.cur_request_id,self.next_request_id,frame,initial_h,initial_w,False)
        resultant_frame,count=self.resultant_initialisation_object.placeBoxes(res_inference,None,0.5,frame,initial_w,initial_h,False,self.cur_request_id)
        cv2.putText(resultant_frame, 'Number of vehicles detected: ' + ' ' + str(count), (20, 20), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,0,255), 1)
        #out.write(resultant_frame)
        #cv2.imshow('frame',resultant_frame)
        #key = cv2.waitKey(1)
        #print("Vehicles detected number:  "+str(count))
        resized_frame= cv2.resize(frame,(1024,560))
        _, jpeg = cv2.imencode('.jpg', resized_frame)
        return jpeg.tobytes()
        
        #finally:
        #    print("Exception")
        #    #del self.resultant_initialisation_object.exec_net

    
    
    
    