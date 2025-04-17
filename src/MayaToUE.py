from MayaUtils import IsJoint, QMayaWindow
from PySide2.QtWidgets import QLineEdit, QMessageBox, QPushButton, QVBoxLayout
import maya.cmds as mc
from pymel.core.general import selected 

class MayaToUE:
    def __init__(self): 
        self.rootJnt = ""

    def SetSelectedAsRootJnt(self):
        selection = mc.ls(sl=True)
        if not selection: 
            raise Exception("Nothing selected, please select the root joint of the rig")
        
        selectedJnt = selection[0]
        if not IsJoint(selectedJnt): 
            raise Exception(f"{selectedJnt} is not a joint, please select the root joint of the rig")
        self.rootJnt = selectedJnt

    def AddRootJoint(self): 
        if (not self.rootJnt) or (not mc.objExists()):
            raise Exception("No root joint assigned, please set the current root joint of the rig first")
        
        currentRootJntPosX, currentRootJntPosY, currentRootJntPosZ = mc.xform(self.rootJnt, q=True, t=True, ws=True)
        if currentRootJntPosX ==0 and currentRootJntPosY==0 and currentRootJntPosZ==0: 
            raise Exception("current root joint is already at origin, no need to make a new one!")
        self.rootJnt = selectedJnt

        
        mc.select(cl=True)
        rootJntName = self.rootJnt + "_root"
        mc.joint(n=rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName 


class MayaToUEWidget(QMayaWindow):
    def GetWindowHash(self):
        return "MayaToUE -"
    
    def __init__ (self): 
        super().__init__()
        self.MayaToUE = MayaToUE
        self.SetWindowTitle("Maya To UE")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootJntText = QLineEdit()
        self.rootJntText.setEnabled(False)
        self.masterLayout.addWidget(self.rootJntText)

        setSelectionAsRootJntBtn = QPushButton("Set Root Joint")
        setSelectionAsRootJntBtn.clicked.connect(self.SetSelectionAsRootJointBtnClicked)
        self.masterLayout.addWidget(setSelectionAsRootJntBtn)

        addRootJntBtn = QPushButton("Add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntButtonClicked)
        self.masterLayout.addWidget(addRootJntBtn)

    def AddRootJntButtonClicked(self):
        try: 
            self.MayaToUE.AddRootJoint()
            self.rootJntText.setText(self.MayaToUE.rootJnt)
        except Exception as e: 
            QMessageBox().critical(self, "Error", f"{e}")

    def SetSelectedASRootJointBtnClicked(self):
        try: 
            self.MayaToUE.SetSelectedAsRootJnt()
            self.rootJntText.setText(self.mayaToUE.rootJnt)
        except Exception as e: 
            QMessageBox().critical(self, "Error", f"{e}")
