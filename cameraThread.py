# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 10:59:16 2020

a Python user interface for camera allied vison, ImgingSource, Balser 


install aliiedVision SDK (https://www.alliedvision.com/en/products/software.html)

on conda prompt :
    for allied vision camera :
pip install pymba (https://github.com/morefigs/pymba.git ) 
#  Encrease timeout :
  #change in File "C:\ProgramData\Anaconda3\lib\site-packages\pymba\camera.py
  #  def acquire_frame(self, timeout_ms: Optional[int] = 200000000) -> Frame: 

    for Basler camera :
pip install pypylon: https://github.com/basler/pypylon 

pip install qdarkstyle (https://github.com/ColinDuquesnoy/QDarkStyleSheet.git)
pip install pyqtgraph (https://github.com/pyqtgraph/pyqtgraph.git)
pip install visu




@author: juliengautier
version : 2019.4
"""

__author__='julien Gautier'
__version__='2020.04'
version=__version__

from PyQt5.QtWidgets import QApplication,QVBoxLayout,QHBoxLayout,QWidget
from PyQt5.QtWidgets import QComboBox,QSlider,QLabel,QSpinBox,QToolButton,QMenu,QInputDialog
from pyqtgraph.Qt import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui 
import sys,time
import pathlib,os
import qdarkstyle
import pyqtgraph as pg


class CAMERA(QWidget):
    dataSignal=QtCore.pyqtSignal(object) # signal to send to visualisation 
    def __init__(self,cam='choose',confFile='confCamera.ini',**kwds):
        '''
        Parameters
        ----------
        cam : TYPE str, optional
            DESCRIPTION. 
                cam='choose' : generate a input dialog box which the list of all the camera connected (allied,basler,imagingSource) 
                cam='cam1' : open the camera by the ID and type save in the confFile.ini 
                ncam='menu': generate a input dialog box with a menu with all the camera name present in the .ini file
                cam='firstGuppy' open the first allied vision camera
                cam='firstBasler' open the first Basler camera
                cam='firstImgSource' open the first ImagingSource camera
            The default is 'choose'.
        confFile : TYPE str, optional
            DESCRIPTION. 
                confFile= path to file.initr
                The default is 'confCamera.ini'.
        **kwds:
            affLight : TYPE boolean, optional
                DESCRIPTION.
                    affLight=False all the option are show for the visualisation
                    affLight= True only few option (save  open cross)
                    The default is True.
            
            all kwds of VISU class
            
        '''
        
        
        super(CAMERA, self).__init__()
        
        p = pathlib.Path(__file__)
        self.nbcam=cam
        
        self.kwds=kwds
        
        if "affLight" in kwds:
            self.light=kwds["affLight"]
        else:
            self.light=True
            
        if "multi"in kwds :
            self.multi=kwds["multi"]
        else:
            self.multi=False    
            
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5()) # qdarkstyle :  black windows style
        
        self.conf=QtCore.QSettings(str(p.parent / confFile), QtCore.QSettings.IniFormat) # ini file 
        self.confPath=str(p.parent / confFile) # ini file path
        sepa=os.sep
        self.icon=str(p.parent) + sepa+'icons'+sepa
        self.setWindowIcon(QIcon(self.icon+'LOA.png'))
        self.iconPlay=self.icon+'Play.png'
        self.iconSnap=self.icon+'Snap.png'
        self.iconStop=self.icon+'Stop.png'
        self.iconPlay=pathlib.Path(self.iconPlay)
        self.iconPlay=pathlib.PurePosixPath(self.iconPlay)
        self.iconStop=pathlib.Path(self.iconStop)
        self.iconStop=pathlib.PurePosixPath(self.iconStop)
        self.iconSnap=pathlib.Path(self.iconSnap)
        self.iconSnap=pathlib.PurePosixPath(self.iconSnap)
        self.nbShot=1
        self.isConnected=False
        self.version=__version__
        
        self.openCam()
        self.setup()
        self.setCamPara()
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        
    def openID(self):
        '''
        open a camera by id camera typ and ID must be known and saved in the ini file 

        '''
        self.ccdName=self.conf.value(self.nbcam+"/nameCDD")
        self.cameraType=self.conf.value(self.nbcam+"/camType")
        self.camID=self.conf.value(self.nbcam+"/camId")
        
        if self.cameraType=="guppy" :
            try :
                import guppyCam
                self.CAM=guppyCam.GUPPY(cam=self.nbcam,conf=self.conf)
                self.CAM.openCamByID(self.camID)
                self.isConnected=self.CAM.isConnected
            except :
                print("no allied vision camera detected or vimba is not installed")
                pass
          
        elif self.cameraType=="basler":
            try:
                import baslerCam
                
                self.CAM=baslerCam.BASLER(cam=self.nbcam,conf=self.conf,**self.kwds)
                
                self.CAM.openCamByID(self.camID)
                self.isConnected=self.CAM.isConnected
                
            except:
                print("no basler camera detected or pypylon is not installed ?")
                pass
        
        elif self.cameraType=="imgSource":
            try :
                import ImgSourceCamCallBack
                self.CAM=ImgSourceCamCallBack.IMGSOURCE(cam=self.nbcam,conf=self.conf,**self.kwds)
                self.CAM.openCamByID(self.camID)
                self.isConnected=self.CAM.isConnected
            except:
                print("no imaging source camera detected or Tisgrabber is not installed")
                pass
        else:
            print('no camera')
            
            
    def openCam(self):
        '''open a camera with different way  
        '''
        
        if self.nbcam=="choose": # create menu widget with all camera present 
        
            self.nbcam='camDefault'
            try :
                import guppyCam 
                self.itemsGuppy=guppyCam.camAvailable()
                # print(self.itemsGuppy)
                self.lenGuppy=len(self.itemsGuppy)
                
            except:
                print('No allied vision camera connected')
                self.itemsGuppy=[]
                self.lenGuppy=0
                pass
            try :
                import baslerCam
                self.itemsBasler=baslerCam.camAvailable()
                self.lenBasler=len(self.itemsBasler)
                
            except:
                print('No Basler camera connected')
                self.itemsBasler=()
                self.lenBasler=0
                pass 
            
            try :
                import ImgSourceCamCallBack
                self.itemsImgSource=ImgSourceCamCallBack.camAvailable()
                self.lenImgSource=len(self.itemsImgSource)
                
            except:
                print('No ImagingSource camera connected')
                self.itemsImgSource=[]
                self.lenImgSource=0
                pass 
            
            items=self.itemsGuppy+list(self.itemsBasler)+self.itemsImgSource
            
            item, ok = QInputDialog.getItem(self, "Select a camera","List of avaible camera", items, 0, False,flags=QtCore.Qt.WindowStaysOnTopHint)
            
            if ok and item:
                
                indexItem = items.index(item)
            
                if indexItem<self.lenGuppy:
                    indexItem=indexItem
                    self.cameraType="guppy"
                    self.camID=guppyCam.getCamID(indexItem)
                    
                    self.CAM=guppyCam.GUPPY(cam=self.nbcam,conf=self.conf)
                    self.CAM.openCamByID(self.camID)
                    self.isConnected=self.CAM.isConnected
                    self.ccdName=self.camID
                elif indexItem>=self.lenGuppy  and indexItem<self.lenBasler+self.lenGuppy:
                    indexItem=indexItem-self.lenGuppy
                    self.cameraType="basler"
                    self.camID=baslerCam.getCamID(indexItem)
                    self.CAM=baslerCam.BASLER(cam=self.nbcam,conf=self.conf,**self.kwds)
                    self.CAM.openCamByID(self.camID)
                    self.isConnected=self.CAM.isConnected
                    self.ccdName=self.camID
                    
                elif indexItem>=self.lenBasler+self.lenGuppy  and indexItem<self.lenBasler+self.lenGuppy+self.lenImgSource:
                    indexItem=indexItem-self.lenGuppy-self.lenBasler
                    self.cameraType="imgSource"
                    self.camID=ImgSourceCamCallBack.getCamID(indexItem)
                    self.camID=self.camID.decode()
                    self.CAM=ImgSourceCamCallBack.IMGSOURCE(cam=self.nbcam,conf=self.conf,**self.kwds)
                    self.CAM.openCamByID(self.camID)
                    self.isConnected=self.CAM.isConnected
                    self.ccdName=self.camID
                else:
                     self.isconnected=False
                     print('No camera choosen')
                     self.ccdName="no camera"
                     self.nbcam='camDefault'
            else :
                self.isconnected=False
                print('No camera choosen')
                self.ccdName="no camera"
                self.cameraType=""
                self.camID=""
                self.nbcam='camDefault'
            
        elif  self.nbcam==None:
            self.isconnected=False
            print('No camera')
            self.ccdName="no camera"
            self.cameraType=""
            self.camID=""
            self.nbcam='camDefault'
             
        elif self.nbcam=="firstGuppy": # open the first guppy cam in the list
            self.nbcam='camDefault'
            self.cameraType="guppy"
            self.ccdName='First guppy Cam'
            import guppyCam 
            self.CAM=guppyCam.GUPPY(cam=self.nbcam,conf=self.conf)
            self.CAM.openFirstCam()
            self.isConnected=self.CAM.isConnected
            
        elif self.nbcam=="firstBasler": # open the first basler cam in the list
            self.ccdName='First basler Cam'
            self.nbcam='camDefault'
            self.cameraType="basler"
            import baslerCam 
            self.CAM=baslerCam.BASLER(cam=self.nbcam,conf=self.conf,**self.kwds)
            self.CAM.openFirstCam()
            self.isConnected=self.CAM.isConnected   
            
        elif self.nbcam=="firstImgSource": # open the first imgSource cam in the list
            self.ccdName='First ImSource Cam'
            self.nbcam='camDefault'
            self.cameraType="imgSource"
            import ImgSourceCamCallBack 
            self.CAM=ImgSourceCamCallBack.IMGSOURCE(cam=self.nbcam,conf=self.conf,**self.kwds)
            self.CAM.openFirstCam()
            self.isConnected=self.CAM.isConnected  
            
            
        elif self.nbcam=='menu': # Qdialog with a menu with all the camera name present in the inifile
            self.groupsName=[]
            self.groups=self.conf.childGroups()
            for groups in self.groups:
                self.groupsName.append(self.conf.value(groups+"/nameCDD"))
            item, ok = QInputDialog.getItem(self, "Select a camera","List of avaible camera", self.groupsName, 0, False,flags=QtCore.Qt.WindowStaysOnTopHint)
            if ok and item:
                indexItem = self.groupsName.index(item)
                self.nbcam=self.groups[indexItem]
                self.openID()
        
        else :  #open the camera by ID : nbcam return ID of the ini file
            self.openID()
        
      
        
    def setCamPara(self):
        '''set min max adn value of cam in the widget
        '''
        
        if self.isConnected==True: # if camera is connected we address min and max value  and value to the shutter and gain box
            
            self.hSliderShutter.setValue(self.CAM.camParameter["exposureTime"])
            self.shutterBox.setValue(self.CAM.camParameter["exposureTime"])
            self.hSliderShutter.setMinimum(self.CAM.camParameter["expMin"]+1)
            self.shutterBox.setMinimum(self.CAM.camParameter["expMin"]+1)
            
            if self.CAM.camParameter["expMax"] >1500: # we limit exposure time at 1500ms
                self.hSliderShutter.setMaximum(1500)
                self.shutterBox.setMaximum(1500)
            else :
                self.hSliderShutter.setMaximum(self.CAM.camParameter["expMax"])
                self.shutterBox.setMaximum(self.CAM.camParameter["expMax"])
            
            self.hSliderGain.setMinimum(self.CAM.camParameter["gainMin"])
            self.hSliderGain.setMaximum(self.CAM.camParameter["gainMax"])
            self.hSliderGain.setValue(self.CAM.camParameter["gain"])
            self.gainBox.setMinimum(self.CAM.camParameter["gainMin"])
            self.gainBox.setMaximum(self.CAM.camParameter["gainMax"])
            self.gainBox.setValue(self.CAM.camParameter["gain"])
            
            self.actionButton()
            
        if  self.isConnected==False:
            self.setWindowTitle('Visualization         No camera connected      '   +  'v.  '+ self.version)
            self.runButton.setEnabled(False)
            self.snapButton.setEnabled(False)
            self.trigg.setEnabled(False)
            self.hSliderShutter.setEnabled(False)
            self.shutterBox.setEnabled(False)
            self.gainBox.setEnabled(False)
            self.hSliderGain.setEnabled(False)
            self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"%(self.iconPlay,self.iconPlay))
            self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"%(self.iconSnap,self.iconSnap))
            
            
            
    def setup(self):  
        
            """ user interface definition 
            """
            self.setWindowTitle('Visualization    '+ self.cameraType+"   " + self.ccdName+'       v.'+ self.version)
            
            self.cameraWidget=QWidget()
            
            self.vbox1=QVBoxLayout() 
            
            self.camName=QLabel(self.ccdName,self)
            self.camName.setAlignment(Qt.AlignCenter)
            self.camName.setStyleSheet('font :bold  12pt;color: white')
            self.vbox1.addWidget(self.camName)
            
            hbox1=QHBoxLayout() # horizontal layout pour run snap stop
            
            self.runButton=QToolButton(self)
            self.runButton.setMaximumWidth(40)
            self.runButton.setMinimumWidth(20)
            self.runButton.setMaximumHeight(70)
            self.runButton.setMinimumHeight(20)
            self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: green;}""QToolButton:pressed{image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}""QToolButton:!hover{border-image: url(%s);background-color: rgb(0, 0, 0,0) ""QToolButton:hover{border-image: url(%s);background-color: blue "% (self.iconPlay,self.iconPlay,self.iconPlay,self.iconPlay) )
            
            self.snapButton=QToolButton(self)
            self.snapButton.setPopupMode(0)
            menu=QMenu()
            #menu.addAction('acq',self.oneImage)
            menu.addAction('set nb of shot',self.nbShotAction)
            self.snapButton.setMenu(menu)
            self.snapButton.setMaximumWidth(40)
            self.snapButton.setMinimumWidth(20)
            self.snapButton.setMaximumHeight(70)
            self.snapButton.setMinimumHeight(20)
            self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: green;}""QToolButton:pressed{image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}"% (self.iconSnap,self.iconSnap) )
            
            self.stopButton=QToolButton(self)
            
            self.stopButton.setMaximumWidth(40)
            self.stopButton.setMinimumWidth(20)
            self.stopButton.setMaximumHeight(70)
            self.stopButton.setMinimumHeight(20)
            self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"% (self.iconStop,self.iconStop) )
            self.stopButton.setEnabled(False)
          
            
            hbox1.addWidget(self.runButton)
            hbox1.addWidget(self.snapButton)
            hbox1.addWidget(self.stopButton)
            
            self.vbox1.addLayout(hbox1)
            
            self.trigg=QComboBox()
            self.trigg.setMaximumWidth(80)
            self.trigg.addItem('OFF')
            self.trigg.addItem('ON')
            self.labelTrigger=QLabel('Trigger')
            self.labelTrigger.setMaximumWidth(50)
            self.itrig=self.trigg.currentIndex()
            hbox2=QHBoxLayout()
            hbox2.addWidget(self.labelTrigger)
            hbox2.addWidget(self.trigg)
            self.vbox1.addLayout(hbox2)
            
            self.labelExp=QLabel('Exposure (ms)')
            self.labelExp.setMaximumWidth(120)
            self.labelExp.setAlignment(Qt.AlignCenter)
            self.vbox1.addWidget(self.labelExp)
            self.hSliderShutter=QSlider(Qt.Horizontal)
            self.hSliderShutter.setMaximumWidth(80)
            self.shutterBox=QSpinBox()
            self.shutterBox.setMaximumWidth(60)
            hboxShutter=QHBoxLayout()
            hboxShutter.addWidget(self.hSliderShutter)
            hboxShutter.addWidget(self.shutterBox)
            self.vbox1.addLayout(hboxShutter)
            
            
            self.labelGain=QLabel('Gain')
            self.labelGain.setMaximumWidth(120)
            self.labelGain.setAlignment(Qt.AlignCenter)
            self.vbox1.addWidget(self.labelGain)
            hboxGain=QHBoxLayout()
            self.hSliderGain=QSlider(Qt.Horizontal)
            self.hSliderGain.setMaximumWidth(80)
            self.gainBox=QSpinBox()
            self.gainBox.setMaximumWidth(60)
            hboxGain.addWidget(self.hSliderGain)
            hboxGain.addWidget(self.gainBox)
            self.vbox1.addLayout(hboxGain)
            
            # self.TrigSoft=QPushButton('Trig Soft',self)
            # self.TrigSoft.setMaximumWidth(100)
            # self.vbox1.addWidget(self.TrigSoft)
            
            self.vbox1.addStretch(1)
            self.cameraWidget.setLayout(self.vbox1)
            self.cameraWidget.setMinimumSize(150,200)
            self.cameraWidget.setMaximumSize(200,900)
            
            hMainLayout=QHBoxLayout()
            
            if self.light==False:
                
                from visu import SEE
                self.visualisation=SEE(confpath=self.confPath,name=self.nbcam,**self.kwds) ## Widget for visualisation and tools  self.confVisu permet d'avoir plusieurs camera et donc plusieurs fichier ini de visualisation
                self.vbox2=QVBoxLayout() 
                self.vbox2.addWidget(self.visualisation)
                
                hMainLayout.addWidget(self.cameraWidget)
                hMainLayout.addLayout(self.vbox2)
                self.setLayout(hMainLayout)
                
            elif self.light=='ultra':
                
                self.visualisation=pg.GraphicsLayoutWidget()
                self.p1=self.visualisation.addPlot()
                self.imh=pg.ImageItem()
                self.p1.addItem(self.imh)
                self.vbox2=QVBoxLayout() 
                self.vbox2.addWidget(self.visualisation)
                hMainLayout.addWidget(self.cameraWidget)
                hMainLayout.addLayout(self.vbox2)
                self.setLayout(hMainLayout)
                
                
            else:
                from visu import SEELIGHTTHREAD
                self.visualisation=SEELIGHTTHREAD(self,confpath=self.confPath,name=self.nbcam,**self.kwds)
                self.visualisation.hbox0.addWidget(self.cameraWidget)
            
                hMainLayout.addWidget(self.visualisation)
                self.setLayout(hMainLayout)
                
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # set window on the top 
            self.activateWindow()
            self.raise_()
            self.showNormal()
            
    def actionButton(self): 
        '''action when button are pressed
        '''
        self.runButton.clicked.connect(self.acquireMultiImage)
        self.snapButton.clicked.connect(self.acquireOneImage)
        self.stopButton.clicked.connect(self.stopAcq)      
        self.shutterBox.editingFinished.connect(self.shutter)    
        self.hSliderShutter.sliderReleased.connect(self.mSliderShutter)
        
        self.gainBox.editingFinished.connect(self.gain)    
        self.hSliderGain.sliderReleased.connect(self.mSliderGain)
        self.trigg.currentIndexChanged.connect(self.trigger)
        if self.multi==True:
            
            self.CAM.newData.connect(self.Display,QtCore.Qt.DirectConnection) #,QtCore.Qt.QueuedConnection)#DirectConnection)
        else :
            self.CAM.newData.connect(self.Display)
            
        # self.TrigSoft.clicked.connect(self.softTrigger)
    
    
    def oneImage(self):
        #self.nbShot=1
        self.acquireOneImage()

    def nbShotAction(self):
        '''
        number of snapShot
        '''
        nbShot, ok=QInputDialog.getInt(self,'Number of SnapShot ','Enter the number of snapShot ')
        if ok:
            self.nbShot=int(nbShot)
            if self.nbShot<=0:
               self.nbShot=1
    
    
    def wait(self,seconds):
        time_end=time.time()+seconds
        while time.time()<time_end:
            QtGui.QApplication.processEvents()
    
    
    def Display(self,data):
        '''Display data with visualisation module
        
        '''
        self.wait(0.001)
        self.data=data
        if self.light=='ultra':
            self.imh.setImage(self.data.astype(float),autoLevels=True,autoDownsample=True)
        else:
            self.dataSignal.emit(self.data) # sent data to visualisation
            #self.visualisation.newDataReceived(self.data)
        if self.CAM.camIsRunnig==False:
            self.stopAcq()
              
    def shutter (self):
        '''
        set exposure time 
        '''
        
        sh=self.shutterBox.value() # 
        self.hSliderShutter.setValue(sh) # set value of slider
        time.sleep(0.1)
        self.CAM.setExposure(sh) # Set shutter CCD in ms
        self.conf.setValue(self.nbcam+"/shutter",float(sh))
        self.conf.sync()
    
    def mSliderShutter(self): # for shutter slider 
        sh=self.hSliderShutter.value() 
        self.shutterBox.setValue(sh) # 
        self.CAM.setExposure(sh) # Set shutter CCD in ms
        self.conf.setValue(self.nbcam+"/shutter",float(sh))
    
    def gain (self):
        '''
        set gain
        '''
        g=self.gainBox.value() # 
        self.hSliderGain.setValue(g) # set slider value
        time.sleep(0.1)
        self.CAM.setGain(g)
        self.conf.setValue(self.nbcam+"/gain",float(g))
        self.conf.sync()
    
    def mSliderGain(self):
        '''
        set slider

        '''
        g=self.hSliderGain.value()
        self.gainBox.setValue(g) # set valeur de la box
        time.sleep(0.1)
        self.CAM.setGain(g)
        self.conf.setValue(self.nbcam+"/gain",float(g))
        self.conf.sync()
        
    def trigger(self):
        
        ''' select trigger mode
         trigger on
         trigger off
        '''
        self.itrig=self.trigg.currentIndex()
        
        if self.itrig==1:
            self.CAM.setTrigger("on")
        else :
            self.CAM.setTrigger("off")
                
    def acquireOneImage(self):
        '''Start on acquisition
        '''
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"%(self.iconSnap,self.iconSnap))
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
    
        self.CAM.startOneAcq(self.nbShot)
        
    
    def acquireMultiImage(self):    
        ''' 
            start the acquisition thread
        '''
        self.runButton.setEnabled(False)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(False)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"%(self.iconSnap,self.iconSnap))
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(False)
        
        self.CAM.startAcq() # start mutli image acquisition thread 
        
        
    def stopAcq(self):
        '''Stop     acquisition
        '''
        self.CAM.stopAcq()
        
        self.runButton.setEnabled(True)
        self.runButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}"%(self.iconPlay,self.iconPlay))
        self.snapButton.setEnabled(True)
        self.snapButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: rgb(0, 0, 0,0) ;border-color: rgb(0, 0, 0)}"%(self.iconSnap,self.iconSnap))
        
        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet("QToolButton:!pressed{border-image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0,0);}""QToolButton:pressed{image: url(%s);background-color: gray ;border-color: rgb(0, 0, 0)}"%(self.iconStop,self.iconStop) )
        self.trigg.setEnabled(True)  
    
    
    def closeEvent(self,event):
        ''' closing window event (cross button)
        '''
        if self.isConnected==True:
             self.stopAcq()
             time.sleep(0.1)
             self.CAM.closeCamera()
            
            
            
if __name__ == "__main__":       
    
    appli = QApplication(sys.argv) 
    appli.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    pathVisu='C:/Users/loa/Desktop/Python/guppyCam/guppyCam/confVisuFootPrint.ini'
    # e = CAMERA('cam1',fft='off',meas='off',affLight='ultra')  
    # e.show()
    f = CAMERA('cam2',fft='off',meas='on',affLight=True,multi=False)  
    f.show()
    appli.exec_()       