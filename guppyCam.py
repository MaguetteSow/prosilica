# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 10:23:01 2020

@author: LOA
"""
from PyQt5.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QWidget,QPushButton
from PyQt5.QtWidgets import QComboBox,QSlider,QLabel,QSpinBox
from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys,time
import numpy as np
import pathlib,os

try:
    from pymba import Vimba  ## pip install pymba https://github.com/morefigs/pymba.git  on conda prompt
    Vimba().startup()
    system=Vimba().system()
    cameraIds=Vimba().camera_ids()
    print( "Cam available:",cameraIds)
    
  #  Encrease timeout :
  #change in File "C:\ProgramData\Anaconda3\lib\site-packages\pymba\camera.py
  #  def acquire_frame(self, timeout_ms: Optional[int] = 200000000) -> Frame: :
except:
    print ('No pymba module installed see : https://github.com/morefigs/pymba.git ')
    
    
    
class GUPPY (QWidget):
    newData=QtCore.pyqtSignal(object)
    
    def __init__(self,cam='camDefault',conf=None):
        
        super(GUPPY,self).__init__()
        
        self.nbcam=cam
        self.itrig='off'
        self.conf=conf
        self.camParameter=dict()
        self.camIsRunnig=False
        self.nbShot=1
        self.initCam()
        
        
        
    def initCam(self):
        
        '''initialisation of camera parameter : 
        '''
        
        if self.nbcam=='camDefault': # camDefaul we take the fisrt one
            try:
                self.cam0=Vimba().camera(cameraIds[0])
                self.ccdName='CAMDefault'
                self.camID=cameraIds[0]
                self.isConnected=True
            except:
                self.isConnected=False
                self.ccdName='no camera'
        else :
            self.camID=self.conf.value(self.nbcam+"/camID") ## read cam serial number
            self.ccdName=self.conf.value(self.nbcam+"/nameCDD")
            try :
                self.cam0=Vimba().camera(self.camID)
                self.isConnected=True
                print('connected')
            except:# if id number doesn't work we take the first one
                try:
                    self.nbcam='camDefault'
                    self.cam0=Vimba().camera(cameraIds[0])
                    self.ccdName='CAMdefault'
                    self.camID=cameraIds[0]
                    self.isConnected=True
                except:
                    print('not ccd connected')
                    self.isConnected=False
                    self.ccdName='no camera'
                    
        if self.isConnected==True:
            print(self.ccdName, 'is connected @:'  ,self.camID )
            self.cam0.open()
            # for feature_name in self.cam0.feature_names():
            #     feature = self.cam0.feature(feature_name)
            #     print(feature_name)
            #     print(" ")
            #     print(" ")
            ## init cam parameter##
            self.LineTrigger=str(self.conf.value(self.nbcam+"/LineTrigger")) # line2 for Mako Line 1 for guppy (not tested)
            self.cam0.feature('ExposureTime').value=float(self.conf.value(self.nbcam+"/shutter"))*1000
            
            self.cam0.feature('TriggerMode').value='Off'
            self.cam0.feature('TriggerActivation').value='RisingEdge'
            #self.cam0.feature('TriggerSelector').value='FrameStart'
            self.cam0.feature('TriggerSource').value='Software'
            self.cam0.feature('ExposureAuto').value='Off'
            self.cam0.feature('GainAuto').value='Off'
            
            self.cam0.feature('Height').value=self.cam0.feature('HeightMax').value
            self.cam0.feature('Height').value=self.cam0.feature('HeightMax').value
            self.cam0.feature('Width').value=self.cam0.feature('WidthMax').value
            self.cam0.feature('Width').value=self.cam0.feature('WidthMax').value
            
            self.camParameter["exposureTime"]=int(self.cam0.feature('ExposureTime').value)/1000
            self.camParameter["expMax"]=float(self.cam0.feature('ExposureTime').range[1])/1000
            self.camParameter["expMin"]=float(self.cam0.feature('ExposureTime').range[0])/1000
            
            
            self.camParameter["gainMax"]=self.cam0.feature('Gain').range[1]
            self.camParameter["gainMin"]=self.cam0.feature('Gain').range[0]
            
            
            if self.camParameter["gainMin"] <=int(self.conf.value(self.nbcam+"/gain"))<=self.camParameter["gainMax"]:
                self.cam0.feature('Gain').value=int(self.conf.value(self.nbcam+"/gain"))
            else:
                print('gain error: gain set to minimum value')
                self.cam0.feature('Gain').value=int(self.camParameter["gainMin"])
            
            self.camParameter["gain"]=self.cam0.feature('Gain').value
            self.camParameter["trigger"]=self.cam0.feature('TriggerMode').value
            
            
            
            
            self.threadRunAcq=ThreadRunAcq(self)
            self.threadRunAcq.newDataRun.connect(self.newImageReceived)
            
            self.threadOneAcq=ThreadOneAcq(self)
            self.threadOneAcq.newDataRun.connect(self.newImageReceived)
            self.threadOneAcq.newStateCam.connect(self.stateCam)
            
            
    def setExposure(self,sh):
        ''' 
            set exposure time in ms
        '''
        self.cam0.feature('ExposureTime').value=float(sh*1000) # in gyppy ccd exposure time is microsecond
        self.camParameter["exposureTime"]=int(self.cam0.feature('ExposureTime').value)/1000
        print("exposure time is set to",self.cam0.feature('ExposureTime').value,' micro s')
        
    def setGain(self,g):
        ''' 
            set gain 
        '''
        self.cam0.feature('Gain').value=g # in gyppy ccd exposure time is microsecond
        print("Gain is set to",self.cam0.feature('Gain').value)   
        self.camParameter["gain"]=self.cam0.feature('Gain').value
    
    def softTrigger(self):
        '''to have a sofware trigger
        '''
        print('trig soft')
        self.cam0.feature('TriggerSource').value='Software'
        self.cam0.run_feature_command('TriggerSoftware') 

    def setTrigger(self,trig='off'):
        '''
            set trigger mode on/off
        '''
        
        if trig=='on':
            self.cam0.feature('TriggerMode').value='On'
            self.cam0.feature('TriggerSource').value=self.LineTrigger
            self.itrig='on'
        else:
            self.cam0.feature('TriggerMode').value='Off'
            self.cam0.feature('TriggerSource').value=self.LineTrigger
            self.itrig='off'
        
        self.camParameter["trigger"]=self.cam0.feature('TriggerMode').value
        
    def startAcq(self):
        self.camIsRunnig=True
        self.threadRunAcq.newRun() # to set stopRunAcq=False
        self.threadRunAcq.start()
    
    def startOneAcq(self,nbShot):
        self.nbShot=nbShot 
        self.camIsRunnig=True
        self.threadOneAcq.newRun() # to set stopRunAcq=False
        self.threadOneAcq.start()
        
    def stopAcq(self):
        
        self.threadRunAcq.stopThreadRunAcq()
        self.threadOneAcq.stopThreadOneAcq()
        self.camIsRunnig=False  
            
    def newImageReceived(self,data):
        
        self.data=data
        self.newData.emit(self.data)
    
        
    def stateCam(self,state):
        self.camIsRunnig=state
    
class ThreadRunAcq(QtCore.QThread):
    
    '''Second thread for controling continus acquisition independtly
    '''
    newDataRun=QtCore.Signal(object)
    
    def __init__(self, parent):
        
        super(ThreadRunAcq,self).__init__(parent)
        self.parent=parent
        self.cam0 = parent.cam0
        self.stopRunAcq=False
        self.itrig= parent.itrig
        self.LineTrigger=parent.LineTrigger
        
    def newRun(self):
        self.stopRunAcq=False
        
    def run(self):
        while self.stopRunAcq is not True :
            self.cam0.feature('TriggerSource').value='Software'
            
            self.cam0.arm('SingleFrame')
            dat1=self.cam0.acquire_frame()  
            if self.itrig=='off':
                self.cam0.run_feature_command('TriggerSoftware')
                
            if dat1 is not None:
                data=dat1.buffer_data_numpy()
                data=np.rot90(data,3)
                if self.stopRunAcq==True:
                    pass
                else :
                    self.newDataRun.emit(data)
            self.cam0.disarm()
            
    def stopThreadRunAcq(self):
        
        #self.cam0.send_trigger()
        
        self.stopRunAcq=True
        
        self.cam0.run_feature_command('TriggerSoftware')
            
            
        #self.cam0.feature('TriggerSource').value=self.LineTrigger
        #self.cam0.run_feature_command ('AcquisitionAbort')
        #self.cam0.disarm()
        # if self.itrig=='on': # in hardward trig mode disarm to get out
             
        #     self.cam0.end_capture()
        #     self.cam0.stop_frame_acquisition()
        
        
class ThreadOneAcq(QtCore.QThread):
    
    '''Second thread for controling one acquisition independtly
    '''
    newDataRun=QtCore.Signal(object)
    newStateCam=QtCore.Signal(bool)
    
    def __init__(self, parent):
        
        super(ThreadOneAcq,self).__init__(parent)
        self.parent=parent
        self.cam0 = parent.cam0
        self.stopRunAcq=False
        self.itrig= parent.itrig
        self.LineTrigger=parent.LineTrigger
        
    
    def newRun(self):
        self.stopRunAcq=False
        
    def run(self):
        
        self.cam0.feature('TriggerSource').value='Software'
        self.newStateCam.emit(True)
        
        for i in range (self.parent.nbShot):
            if self.stopRunAcq is not True :
                self.cam0.arm('SingleFrame')
                dat1=self.cam0.acquire_frame()  
                if self.itrig=='off':
                    self.cam0.run_feature_command('TriggerSoftware')
                
                
            
                
                if i<self.parent.nbShot-1:
                    self.newStateCam.emit(True)
                else:
                    self.newStateCam.emit(False)
                    time.sleep(0.1)
                    
                if dat1 is not None:
                    data=dat1.buffer_data_numpy()
                    data=np.rot90(data,3)    
                    self.newDataRun.emit(data)
                    
                self.cam0.disarm()
                
            else:
                break
        self.newStateCam.emit(False)
        
        
        
    def stopThreadOneAcq(self):
        
        #self.cam0.send_trigger()
        
        self.stopRunAcq=True
        
        self.cam0.run_feature_command('TriggerSoftware')       
        
        
        
        
        
        
        
        