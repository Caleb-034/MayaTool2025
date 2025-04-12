from PySide2.QtGui import QColor
import maya.cmds as mc #imports maya's cmd module so we can use it to do stuff in maya
import maya.mel as mel 
import maya.OpenMayaUI as omui # this imports mayas open maya ui module, it can help finding the maya main window
from maya.OpenMaya import MVector 
import shiboken2 # this helps with converting the maya main window to the pyside type

from PySide2.QtWidgets import QColorDialog, QLineEdit, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton # imports all the widgets needed to buil our ui
from PySide2.QtCore import Qt # this has some values we can use to configure our widget, like their windowType, or orientation

def GetMayaMainWindow()->QMainWindow: #creates basic maya window
    mayaMainWindow = omui.MQtUtil.mainWindow() #retrieves the main window thing (maya)
    return shiboken2.wrapInstance(int(mayaMainWindow), QMainWindow)  #changes the main window(maya) to a PySide2 QMainWindow

def DeleteWindowWithName(name): #deletes current window 
    for window in GetMayaMainWindow().findChildren(QWidget, name): #looks for the window with this specific name 
        window.deleteLater() #deletes the window after it finds it 

class QMayaWindow(QWidget): #custom class to represent new window 
    def __init__(self):
        DeleteWindowWithName(self.GetWindowHash())  #deletes any existing window that has the same name
        super().__init__(parent=GetMayaMainWindow())  #starts QWidget with maya's main window as its parent(liteally like animation)
        self.setWindowFlags(Qt.WindowType.Window)  #sets window flags to make it like a  normal window
        self.setObjectName(self.GetWindowHash())  #sets windows object name with hash


    def GetWindowHash(self):  # creates hash
        return "sjdhfjhweuhajsdbflkhaweihfihdcvj"
   
class LimbRigger:  #class that sets the rigging of limbs with FK cntrls
    def __init__(self): #starts LimbRigger class
        self.root =""  #root joint of limb
        self.mid = ""  #middle joint of limb
        self.end =""  #end joint of the limb
        self.controllerSize = 5  #size of FK controllers
        self.controllerColor = QColor(0, 0, 0)

    def SetControllerColor(self, color):
        self.controllerColor=color 
        print(f"Controller color set to {set.controllerColor.name()}")

    def AutoFindJnts(self): # function is  to create FK controls for given joint
        self.root = mc.ls(sl=True, type="joint")[0]
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
        self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]

    def CreateFKControlForJnt(self, jntName): #function is to rig entire limb by creating FK controls per joint 
        ctrlName = "ac_fk_" + jntName
        ctrlGrpName = ctrlName + "_grp"
        mc.circle(n=ctrlName, r=self.controllerSize, nr = (1,0,0))

        mc.group(ctrlName, n=ctrlGrpName)
        mc.matchTransform(ctrlGrpName, jntName)
        mc.orientConstraint(ctrlName, jntName)
        mc.setAttr(f"{ctrlName}.overrrideEnabled", 1)
        mc.setAttr(f"{ctrlName}.overrrideRGBColors", 1)
        #should i specify all three colors in the rgb or nah?
        return ctrlName, ctrlGrpName
    
    def CreateBoxController(self, name): 
        mel.eval(f"curve -n{name} -d 1 -p 0.5 0.5 -0.5 -p 0.5 0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p 0.5 -0.5 -0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 ;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name,)
        mc.makeIdentity(name, apply =True) #this is freeze transformation)

        grpName = name +"_grp"
        mc.group(name, n=grpName)
        return name, grpName
    
    def GetObject(self, objectName)->MVector:
        x, y, z = mc.xform(objectName, q=True, t=True, was=True)# get worldspace translation of the objectName
        return MVector(x,y,z)
    
    def PrintMVector(self, vectorToPrint):
        print(f"v{vectorToPrint.x}, {vectorToPrint.y}, {vectorToPrint.z}>")
    

    def RigLimb(self): #creates 3 paretned FK controllers for all joints
        rootFKCtrl, rootFKCtrlGrp = self.CreateFKControlForJnt(self.root)
        midFKCtrl, midFKCtrlGrp = self.CreateFKControlForJnt(self.mid)
        endFKCtrl, endFKCtrlGrp = self.CreateFKControlForJnt(self.end)

        mc.parent(midFKCtrlGrp, rootFKCtrl)
        mc.parent(endFKCtrlGrp, midFKCtrl)

        ikEndCtrl = "ac_ik" + self.end 
        ikEndCtrl, ikEndCtrlGrp = self.CreateBoxController(ikEndCtrl)
        mc.setAttr(f"{ikEndCtrl}.overrideEnabled", 1)
        mc.setAttr(f"{ikEndCtrl}.overrideRGBColors", 1)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end[0])

        rootJntLoc = self.GetObject(self.root)
        endJntLoc = self.GetObject(self.end)

        rootToEndVec= endJntLoc - rootJntLoc 

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n=ikHandleName, sj=self.root, ee=self.end, sol="ikRPSolver")
        ikPoleVectorVals = mc.getAttr(ikHandleName + ".poleVector")
        ikPoleVector = MVector(ikPoleVectorVals[0], ikPoleVectorVals[1], ikPoleVectorVals[2])

        ikPoleVector.normalize()
        ikPoleVectorCtrlLoc= rootJntLoc + rootToEndVec / 2 + ikPoleVector + rootToEndVec.length()

        ikPoleVectorCtrlName= "ac_ik" + self.mid 
        mc.spaceLocator(n=ikPoleVectorCtrlName)
        ikPoleVectorCtrlGrp = ikPoleVectorCtrlName + "_grp"
        mc.group(ikPoleVectorCtrlName, n=ikPoleVectorCtrlGrp)
        mc.setAttr(ikPoleVectorCtrlGrp+".t", ikPoleVectorCtrlLoc.x, ikPoleVectorCtrlLoc.y, ikPoleVectorCtrlLoc.z, typ= "double 3")
        mc.poleVectorConstraint(ikPoleVectorCtrlName, ikHandleName)

        ikfkBlendCtrlName = "ac_ikfk_blend" + self.root 
        ikfkBlendCtrlName, ikfkBlendCtrlGrp = self.CreatePlusController(ikfkBlendCtrlName)
        ikfkBlendCtrlLoc= rootJntLoc + MVector(rootJntLoc.x,0, rootJntLoc.z, )
        mc.setAttr(ikfkBlendCtrlGrp+".t", ikfkBlendCtrlLoc.x, ikfkBlendCtrlLoc.y, ikfkBlendCtrlLoc.z, typ="double3")

        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikfkBlendCtrlName, ln=ikfkBlendAttrName, min=0, max=1, k=True)
        ikfkBlendAttr= ikfkBlendCtrlName +"."+ ikfkBlendCtrlName

        mc.expression(s=f"{ikHandleName}.ikBlend= {ikfkBlendAttr}")
        mc.expression(s=f"{ikEndCtrlGrp}.v={ikPoleVectorCtrlGrp}.v, = {ikfkBlendAttr}")
        mc.expresesion(s=f"{rootFKCtrlGrp}.v=1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.")
        mc.expression(s=f"{endOrientConstraint}.{ikEndCtrl}w1 = {ikfkBlendAttr}")

        mc.parent(ikHandleName, ikEndCtrl)
        mc.setAttr(ikHandleName+".v", 0)

        topGrpName = self.root + "_rig_grp"
        mc.group([rootFKCtrlGrp, ikEndCtrlGrp, ikPoleVectorCtrlGrp, ikfkBlendCtrlGrp], n=topGrpName)
        mc.setAttr(topGrpName+".overrideEnabled", 1)
        mc.setAttr(topGrpName+".overrideRBGColors", 1)
        mc.setAttr(topGrpName+".overrideColorRGB", r, g, b type="double3")
class ColorPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.colorPickerBtn= QPushButton("Pick Color")
        self.colorPickerBtn.setStyleSheet(f"background-color:black;")
        self.masterLayout.addWidget(self.colorPickerBtn)
        self.onColorChanged = onColorChanged 
        self.colorPickerBtn.clicked.connect(self.ColorPickerBtnClicked)
        self.color= QColor(0, 0, 0)

    def ColorPickerBtnClicked(self): 
        self.color = QColorDialog.getColor(self.color)
        if self.color.isValid():
            self.colorPickerBtn.setStyleSheet(f"background-color: {self.color.name()};")
            self.onColorChanged(self.color)

class LimbRigToolWidget(QMayaWindow): #creates widgets that are in LimbRigWindow
    def __init__(self): #creates button, texts, and slider widget
        super().__init__()
        self.rigger = LimbRigger()
        self.setWindowTitle("Limb Rigging Tool")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.tipLabel = QLabel("Select the First Joint of the Limb, and click on the Auto Find Button")
        self.masterLayout.addWidget(self.tipLabel)

        self.jointSelectionText = QLineEdit()
        self.masterLayout.addWidget(self.jointSelectionText)
        self.jointSelectionText.setEnabled(False)

        self.autoFindBttn = QPushButton("Auto Find")
        self.masterLayout.addWidget(self.autoFindBttn)
        self.autoFindBttn.clicked.connect(self.AutoFindBttnClicked)

        ctrlSliderLayout = QHBoxLayout()
        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeValueChanged)
        ctrlSizeSlider.setRange(1, 30)
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSliderLayout.addWidget(ctrlSizeSlider)
        self.ctrlSizeLabel = QLabel(f"{self.rigger.controllerSize}")
        ctrlSliderLayout.addWidget(ctrlSizeSlider)

        self.masterLayout.addLayout(ctrlSliderLayout)

        self.colorPicker = ColorPicker(self.onColorChanged)
        self.masterLayout.addWidget(self.colorPicker)

        self.rigLimbBttn = QPushButton("Rig Limb")
        self.masterLayout.addWidget(self.rigLimbBttn)
        self.rigLimbBttn.clicked.connect(self.RigLimbBttnClicked)

    def onColorChanged(self,color):
        self.rigger.SetControllerColor(color)

    def CtrlSizeValueChanged(self, newValue): #affects ctrl size
        self.rigger.controllerSize = newValue
        self.ctrlSizeLabel.setText(f"{self.rigger.controllerSize}")

    def RigLimbBttnClicked(self): #riglimb function
        self.rigger.RigLimb(self, ColorPicker.color.redF(), self.colorPicker.color.greenF(), self.colorPicker.color.blueF())

    def AutoFindBttnClicked(self): #finds/sets joints and gives an error message if selected incorrectly
        try: # finds/sets joints
            self.rigger.AutoFindJnts()
            self.jointSelectionText.setText(f"{self.rigger.root},{self.rigger.mid},{self.rigger.end}")
        except Exception as e: #gives error message
            QMessageBox.critical(self, "Error", "Wrong Selection, Please select the first joint of a limb!")


limbRigToolWidget = LimbRigToolWidget() #assigns variables
limbRigToolWidget.show() #shows the window
