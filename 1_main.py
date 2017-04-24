# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiu
# Created:     04/16/2017
#
#-------------------------------------------------------------------------------
from __future__ import division
from Tkinter import *
from PIL import Image, ImageTk
import os
import glob
import random
import tkSimpleDialog
import tkFileDialog
import tkMessageBox

# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256
label_class = 15

class LabelTool():
    def __init__(self, master):

        #initialize global parameter
        self.labelEntry = ''
        self.label_class = 0
        self.OldimageDir = ''
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = True, height = True)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.labelfilename1 =''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        self.entry = Entry(self.frame)
        self.entry.grid(row = 0, column = 1, sticky = W+E)
        self.ldBtn = Button(self.frame, text = "Path", command = self.getPath)
        self.ldBtn.grid(row = 0, column = 2, sticky = W+E)
        self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        self.ldBtn.grid(row = 0, column = 3, sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("c", self.Closed)
        self.parent.bind("h",self.help)
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("d", self.nextImage) # press 'd' to go forward
        self.parent.bind("p",self.ChangeToXML)#press 'p' to produce the XML
        self.parent.bind("r",self.randSelectBtn)#press 'r'to produce the randSelectBtn
        self.parent.bind("l",self.labelSelect)#press 'l'to set the label
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 22, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)
        self.btnDel = Button(self.frame, text = 'Delete', command = self.delBBox)
        self.btnDel.grid(row = 3, column = 2, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'ClearAll', command = self.clearBBox)
        self.btnClear.grid(row = 4, column = 2, sticky = W+E+N)
        # the steps how to operate it
        self.listbox_ = Listbox(self.frame, width = 22, height = 6)
        self.listbox_.grid(row = 5, column = 2, sticky = N)
        self.listbox_.insert(END, ' The Operation Steps  ')
        self.listbox_.itemconfig(0, fg = 'black')
        self.listbox_.insert(END, '1 . Labeling the image')
        self.listbox_.itemconfig(1, fg = 'black')
        self.listbox_.insert(END, '2 . RandSelect the Samples')
        self.listbox_.itemconfig(2, fg = 'black')
        self.listbox_.insert(END, '3 . Enter the ClassLabel')
        self.listbox_.itemconfig(3, fg = 'black')
        self.listbox_.insert(END, '4 . Produce the XML files')
        self.listbox_.itemconfig(4, fg = 'black')
        self.listbox_.insert(END, '5 . Closed')
        self.listbox_.itemconfig(5, fg = 'black')
        #self.Labeling = Label(self.frame, text = "1.Labeling the image")
        #self.Labeling.grid(row = 5, column = 2, sticky = W+E+N)
        
        # control panel for image navigation

        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 6, column = 1, columnspan = 2, sticky = W+E)
        self.imgLabel = Label(self.ctrPanel, text = "   ")
        self.imgLabel.pack(side = LEFT, padx = 5)
        self.produBtn = Button(self.ctrPanel,text ='Closed',width = 10,command =self.Closed)
        self.produBtn.pack(side = LEFT, padx = 5)
        self.produBtn = Button(self.ctrPanel,text ='ProdXML',width = 10,command =self.ChangeToXML)
        self.produBtn.pack(side = LEFT, padx = 5)
        self.labelSelectbtn = Button(self.ctrPanel,text ='classLabel',width =10,command = self.labelSelect)
        self.labelSelectbtn.pack(side =LEFT,padx =5)
        self.randSelectBtn = Button(self.ctrPanel,text ='randSelect',width = 10,command =self.randSelectBtn)
        self.randSelectBtn.pack(side = LEFT, padx = 5)
        #self.labelSelectbtn = Button(self.ctrPanel,text ='classLabel',width =10,command = self.labelSelect)
        #self.labelSelectbtn.pack(side =LEFT,padx =5)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)
        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 10)
        self.egPanel.grid(row = 1, column = 0, rowspan = 5, sticky = N)
        self.tmpLabel2 = Label(self.egPanel, text = "Examples:")
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

        # for debugging
        #self.setImage()
        #self.loadDir()
    def getPath(self):

        self.imageDir=tkFileDialog.askdirectory()
        if self.OldimageDir != self.imageDir:
            self.OldimageDir = self.imageDir
            self.entry.delete(0,END)
        self.entry.insert(0,self.imageDir)
    #Re-naming the .png images 
    def reName(self):
        path =self.imageDir
        file_num =1
        file_extensions = 'jpg'
        self.file_extensions = file_extensions
        if not os.path.exists(path):
            tkMessageBox.showinfo('Warning','Dont find the direction%s'%(path))
        #files =
        for file in os.listdir(path):
            if file.split('.')[-1] == file_extensions:
                if os.path.isfile(os.path.join(path,file))==True:
                    new_name = file.replace(file,"%05d.%s"%(file_num,file_extensions))
                    os.rename(os.path.join(path,file),os.path.join(path,new_name))
                    file_num+=1
            else:
                tkMessageBox.showinfo('Tips',\
                                    'this file didnt re-Name %s'%(file))
                #print file

    def loadDir(self, dbg = False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            #self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
##        if not os.path.isdir(s):
##            tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
##            return

        # Get the label
        self.label_class=tkSimpleDialog.askinteger('classLabelNo', 'Input the classLabelNum:')
        if self.label_class < 0:
            tkMessageBox.showerror('Error','Please input a positive number!')
            return 0
        elif self.label_class == 0:
            tkMessageBox.showerror('Warnning','Using the default Label 0!')
        self.category = self.label_class
        self.imgLabel.config(text = "imgLabel = %s" %(self.label_class))
        #Get the imagePath
        #self.imageDir = os.path.join(r'./Images', '%03d' %(self.category))
        if not os.path.isdir(self.imageDir):
            tkMessageBox.showerror('Error','This Dir:%s doesnt exist!'%(self.imageDir))
            return 0;
        self.reName()
        #Delete the path load
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.%s'%(self.file_extensions)))
        if len(self.imageList) == 0:
            tkMessageBox.showerror('Warnning',\
                'No *.%s images in this Directory:%s'%(self.file_extensions,self.imageDir))
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.outDir = os.path.join(r'./Labels', '%03d' %(self.label_class))
        print self.outDir
        if not os.path.exists(self.outDir):
            os.makedirs(self.outDir)

        # load example bboxes
        #self.egDir = os.path.join(r'./Examples', '%03d' %(self.category))
        self.egDir = os.path.join(r'./Examples','001')
        if not os.path.exists(self.egDir):
            tkMessageBox.showerror('Error','This Dir:%s doesnt exist!Please check it!'%(self.egDir))
            return
        #Get the examples imagelist
        filelist = glob.glob(os.path.join(self.egDir, '*.JPEG'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        print filelist
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])

        self.loadImage()
        #print '%d images loaded from %s' %(self.total, s)
        tkMessageBox.showinfo('Loaded','%d images loaded from %s' %(self.total, self.imageDir))

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "Progress %04d/%04d" %(self.cur, self.total))
        #self.imgLabel.config(text = "imgLabel = %s" %())

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        #print self.imagename
        labelname = self.imagename + '.txt'
        labelname_= 'text.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        self.labelfilename1 = os.path.join(self.outDir, labelname_)
        bbox_cnt = 0
        self.listbox_.itemconfig(1, fg = 'green')
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    tmp = [int(t.strip()) for t in line.split()]
                    ##print tmp
                    self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                            tmp[2], tmp[3], \
                                                            width = 2, \
                                                            outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(tmp[0], tmp[1], tmp[2], tmp[3]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
    
    #store the label
    def saveImage(self):
        #print self.labelfilename1

        with open(self.labelfilename1, 'a+') as f:
            if len(self.bboxList):
                for bbox in self.bboxList:
                    f.write('%s ' %os.path.split(self.imageList[self.cur - 1])[-1].split('\\')[-1])
                    f.write('%d ' %self.label_class)
                    f.write(' '.join(map(str, bbox)) + '\n')
            '''
            else:
                f.write('%s ' %os.path.split(self.imageList[self.cur - 1])[-1].split('\\')[-1])
                f.write('%d ' %label_class)
                dot_x=0
                dot_y=0
                dot_x1=0
                dot_y1=0
                f.write('%d '%dot_x)
                f.write('%d '%dot_y)
                f.write('%d '%dot_x1)
                f.write('%d '%dot_y1+'\n')
            '''
        print 'Image No. %d saved' %(self.cur)


    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, \
                                                0, event.x,\
                                                self.tkimg.height(), \
                                                width = 2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def prevImage(self, event = None):
        #self.saveImage()
        if self.cur > 1:
            self.saveImage()
            self.cur -= 1
            self.loadImage()
        elif self.cur == 1:
            tkMessageBox.showinfo('Warnning','This is the first image!')

    def nextImage(self, event = None):
        #self.saveImage()
        self.count = 0
        if self.cur < self.total:
            self.saveImage()
            self.cur += 1
            self.loadImage()
        elif self.cur == self.total and self.count ==0:
            #tkMessageBox.showinfo("", message = "The specified dir doesn't exist!")
            self.saveImage()
            count = 1
            self.listbox_.itemconfig(1, fg = 'red')
            tkMessageBox.showinfo('Warnning','This is the last image!')

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()
        else:
            tkMessageBox.showinfo('Warnning','Please input the correct integer')
            #self.listbox_.itemconfig(1, fg = 'red')

    def gotoLabel(self):
        self.mainwin.withdraw()

    def Closed(self,event = None):
        result = tkMessageBox.askyesno(title="Warning",\
                                     message="Are you sure? ",\
                                     detail="Yes,you will quit!!!  No,you would return the mainframe.", \
                                     icon="warning")
        if result == True:
            root.destroy()

    def help(self,event=None):
        s=\
        '''
        --Purpose
            This software is write to help the people who work for the Box-Labeling,it can help them quickly get the training dataset.
        
        --Quickkey
            Escape:cancel current bbox
            s :cancel current bbox
            c :The function of the button "Closed"
            h :The help frame
            a :the last image
            d :the next image
            p :The function of the button "ChangeToXML"
            r :The function of the button "randSelect"
            l :The function of the button "labelSelect"
        --Operation Document website:
            https://github.com/OxInsky/VOCLabeling
            
        '''
        tkMessageBox.showinfo('HelpDocment','%s'%(s))
#######################################################################################
# *
# *
# *
#######################################################################################
    def labelSelect(self,event = None):

        self.listbox_.itemconfig(3, fg = 'green')
        BASE = sys.path[0]
        fileDir = BASE +r'\\Main'
        label =''
        #label_ ='person_'
        s1 = "{0}test.txt"
        s2 = "{0}train.txt"
        s3 ="{0}trainval.txt"
        s4 = "{0}val.txt"
        Labelname = tkSimpleDialog.askstring('Python Tkinter', 'Input the Labelname')
        print Labelname
        if (Labelname == None):
            Labelname = 'Default'
            #tkMessageBox.showerror('warnning',"Using the 'Default' as the label!")
            tkMessageBox.showinfo("warnning","Using the 'Default' as the label!")
            self.imgLabel.config(text = "imgLabel = %s" %(Labelname))
            return 0;
        label_ = Labelname+'_'
        self.imgLabel.config(text = "imgLabel = %s" %(Labelname))
        #print os.path.join(BASE,s1.format(label))
        #the Path of the txt
        testPath = os.path.join(fileDir,s1.format(label))
        trainPath = os.path.join(fileDir,s2.format(label))
        trainvalPath = os.path.join(fileDir,s3.format(label))
        valPath =os.path.join(fileDir,s4.format(label))

        #the Path of the labeling file
        _testPath = os.path.join(fileDir,s1.format(label_))
        _trainPath = os.path.join(fileDir,s2.format(label_))
        _trainvalPath = os.path.join(fileDir,s3.format(label_))
        _valPath =os.path.join(fileDir,s4.format(label_))

         #Get the label information
        #test = open(testPath)
        test = open(testPath)
        testlines = test.readlines()
        test.close()
        _test = open(_testPath,'w')
        for testline in testlines:
            _test.write(testline.split('\n')[0]+' 1\n')
        _test.close()

        #_train = open(_trainPath)
        train =open(trainPath)
        trainlines =train.readlines()
        train.close()
        _train =open(_trainPath,'w')
        for trainline in trainlines:
            _train.write(trainline.split('\n')[0]+' 1\n')
        _train.close()

        #_trainval = open(_trainvalPath)
        trainval = open(trainvalPath)
        trainvallines = trainval.readlines()
        trainval.close()
        _trainval = open(_trainvalPath,'w')
        for trainvalline in trainvallines:
            _trainval.write(trainvalline.split('\n')[0]+' 1\n')
        _trainval.close()

        #_val = open(_valPath)
        val = open(valPath)
        vallines = val.readlines()
        val.close()
        _val = open(_valPath,'w')
        for valline in vallines:
            _val.write(valline.split('\n')[0]+' 1\n')
        _val.close()
        tkMessageBox.showinfo("Success!","The files in%s:"%(fileDir))
        self.listbox_.itemconfig(3, fg = 'red')
############################################################################################
#
#
#
#
############################################################################################
    def ChangeToXML(self,event = None):
        self.listbox_.itemconfig(4, fg = 'green')
        s1="""
    <object>
        <name>{0}</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>{1}</xmin>
            <ymin>{2}</ymin>
            <xmax>{3}</xmax>
            <ymax>{4}</ymax>
        </bndbox>
    </object>"""
        s2=\
 """<annotation>
<folder>VOC2007</folder>
<filename>{0}</filename>
<source>
    <database>My Database</database>
    <annotation>VOC2007</annotation>
    <image>flickr</image>
    <flickrid>NULL</flickrid>
</source>
<owner>
    <flickrid>NULL</flickrid>
    <name>Jia</name>
</owner>
<size>
    <width>{7}</width>
    <height>{8}</height>
    <depth>3</depth>
</size>
<segmented>0</segmented>
<object>
    <name>{1}</name>
    <pose>Unspecified</pose>
    <truncated>0</truncated>
    <difficult>0</difficult>
    <bndbox>
        <xmin>{2}</xmin>
        <ymin>{3}</ymin>
        <xmax>{4}</xmax>
        <ymax>{5}</ymax>
    </bndbox>
</object>{6}
</annotation>
        """
        baseDir = sys.path[0]
        #outDir = os.path.join(baseDir, '\\Labels\\%03d\\text.txt' %(self.label_class))
        #textListPath = outDir
        #textlist="C:\\Users\\leafshadow\\Desktop\\Labels\\BBox-Label-Tool-master\\Labels\\001\\test.txt"
        #flabel = open("C:\\Users\\leafshadow\\Desktop\\Labels\\BBox-Label-Tool-master\\Labels\\001\\text.txt",'r')
        flabel = open(baseDir+'\\Labels\\%03d\\text.txt' %(self.label_class))
        lb = flabel.readlines()
        flabel.close()
        ob2 = ""
        '''
        if len(lb)<2:
            continue  # no annotation
        '''
        '''
        x1=2
        x2=lb[1].split(' ')
        '''
        Maker = self.label_class
        #x3 = [int(float(i) * 256) for i in x2]
        #if len(lb)>2:  # extra annotation
        i=0
        while (i<len(lb)):
            count = 0
            current_name = lb[i].split(' ')[0]
            j = i + 1
            RectObject = ''
            #Get the multi object information
            while(j < len(lb) and current_name == lb[j].split(' ')[0]):
                count = count +1
                object_ =lb[j].split(' ')
                RectObject+='\n'+s1.format(Maker,object_[2],object_[3],object_[4],object_[5].split('\n')[0])
                j = j + 1
            imagename_last = lb[i].split(' ')
            imagename = imagename_last[0].split('.')[0]

            #Store the xml file
            savenamePathDir =os.path.join(baseDir,'Annotations\\')
            if not os.path.isdir(savenamePathDir):
                os.mkdir(savenamePathDir)
            savename = 'Annotations\\'+imagename+'.xml'
            print savename
            #Get the imageSize
            imgpath = os.path.join(self.imageDir,imagename_last[0])
            img = Image.open(imgpath)
            imgSize = img.size
            f = open(savename,'w')
            ob1 = s2.format(imagename_last[0],imagename_last[1],imagename_last[2],imagename_last[3],imagename_last[4],imagename_last[5].split('\n')[0],RectObject,imgSize[0],imgSize[1])
            f.write(ob1)
            f.close()
            i = j
            xmlDir = os.path.join(baseDir,'Annotations')
        if i==len(lb):
            tkMessageBox.showinfo("Success","Run Succeed! the XMLfiles in %s"%(xmlDir))
        else:
            tkMessageBox.showinfo("Failed","Run Failed! Plesase check the file \
                %s"%(textListPath))
        self.listbox_.itemconfig(4, fg = 'red')
        self.listbox_.itemconfig(5, fg = 'green')
    #############################################################################################
    #
    #
    #
    #############################################################################################
    def randSelectBtn(self,event = None):
        self.listbox_.itemconfig(2, fg = 'green')
        root = sys.path[0]
        subDir = root+'\\Main' 
        if not os.path.isdir(subDir):
            os.makedirs(subDir)
        #print os.path.join(root, '\\Labels\\%03d' %(self.label_class))
        #outDir = os.path.join(root, '\\Labels\\%03d' %(self.label_class))
        #Devide the sample into different phrases
        fp = open(root+'\\Labels\\%03d\\text.txt' %(self.label_class))
        fp_trainval = open(root + '\\Main\\trainval.txt', 'w')
        fp_test = open(root + '\\Main\\test.txt', 'w')
        fp_train = open(root + '\\Main\\train.txt', 'w')
        fp_val = open(root + '\\Main\\val.txt', 'w')
        #Get the trainval.VS.Test gate
        trainTest_gate = tkSimpleDialog.askfloat('Trainval.VS.Test', 'Gate(0,1](Default=0.1)')
        if trainTest_gate <= 0 or trainTest_gate > 1:
            tkMessageBox.showerror('Error','Entering Error!')
            return 0;
        if trainTest_gate == None:
            trainTest_gate = 0.1

        #1 Get the label information
        #2 Get the trainval .VS. test samples 
        filenames = fp.readlines()
        i=0
        while(i<len(filenames)):
            pic_name = filenames[i]
            pic_name = pic_name.strip()
            x = random.uniform(0, 1)
            pic_info = pic_name.split('.')[0]
            #Get the Same information
            j = i + 1
            while(j<len(filenames)and (pic_info ==filenames[j].split('.')[0])):
                j = j + 1
            if x >= trainTest_gate:
                fp_trainval.writelines(pic_info + '\n')

            else:
                fp_test.writelines(pic_info + '\n')
            i = j 
        fp_trainval.close()
        fp_test.close()

        #Get the Train .VS. Val gate
        trainVal_gate = tkSimpleDialog.askfloat('Train.VS.Val', 'Gate(0,1](Default=0.1)')
        if trainVal_gate <=0 or trainVal_gate > 1:
            tkMessageBox.showerror('Error','Entering Error!')
            return 0;
        if trainVal_gate == None:
            trainVal_gate = 0.1

        #Split the information into train.txt and val.txt 
        fp = open(root + '\\Main\\trainval.txt')
        if (fp ==None):
            print "the Path doesn't exist!"
        #Get the samples from the trainval.txt    
        filenames = fp.readlines()
        for i in range(len(filenames)):
            pic_name = filenames[i]
            pic_name = pic_name.strip()
            pic_info = pic_name.split('.')[0]
            x = random.uniform(0, 1)
            if x >= trainVal_gate:
                fp_train.writelines(pic_info + '\n')
            else:
                fp_val.writelines(pic_info + '\n')
        fp_train.close()
        fp_val.close()
        self.imgLabel.config(text = "trainToTest=%f,trainToVal=%f" %(trainTest_gate,trainVal_gate))
        tkMessageBox.showinfo("Success","RandSelect run succeed，the files are in:%s"%(root + '\\Main'))
        self.listbox_.itemconfig(2, fg = 'red')
##    def setImage(self, imagepath = r'test2.png'):
##        self.img = Image.open(imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
    def classification(self):

        BASE = sys.path[0]+'\\Labels\\%03d'%(self.label_class)
        label =''
        label_ ='%s_'%()
        s1 = "{0}test.txt"
        s2 = "{0}train.txt"
        s3 ="{0}trainval.txt"
        s4 = "{0}val.txt"
        #print os.path.join(BASE,s1.format(label))

        testPath = os.path.join(BASE,s1.format(label))
        trainPath = os.path.join(BASE,s2.format(label))
        trainvalPath = os.path.join(BASE,s3.format(label))
        valPath =os.path.join(BASE,s4.format(label))

        _testPath = os.path.join(BASE,s1.format(label_))
        _trainPath = os.path.join(BASE,s2.format(label_))
        _trainvalPath = os.path.join(BASE,s3.format(label_))
        _valPath =os.path.join(BASE,s4.format(label_))

        #test = open(testPath)
        test = open(testPath)
        testlines = test.readlines()
        test.close()
        _test = open(_testPath,'w')
        for testline in testlines:
            _test.write(testline.split('\n')[0]+' 1\n')
        _test.close()

        #_train = open(_trainPath)
        train =open(trainPath)
        trainlines =train.readlines()
        train.close()
        _train =open(_trainPath,'w')
        for trainline in trainlines:
            _train.write(trainline.split('\n')[0]+' 1\n')
        _train.close()

        #_trainval = open(_trainvalPath)
        trainval = open(trainvalPath)
        trainvallines = trainval.readlines()
        trainval.close()
        _trainval = open(_trainvalPath,'w')
        for trainvalline in trainvallines:
            _trainval.write(trainvalline.split('\n')[0]+' 1\n')
        _trainval.close()

        #_val = open(_valPath)
        val = open(valPath)
        vallines = val.readlines()
        val.close()
        _val = open(_valPath,'w')
        for valline in vallines:
            _val.write(valline.split('\n')[0]+' 1\n')
        _val.close()


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()
