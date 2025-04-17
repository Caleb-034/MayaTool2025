from MayaUtils import IsJoint, IsMesh, QMayaWindow
from PySide2.QtGui import QIntValidator, QRegExpValidator
from PySide2.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout, QWidget
import maya.cmds as mc


def TryAction(action): 
    def wrapper(*args, **kwards):
        try:
            action(*args, **kwards)
        except Exception as e: 
            QMessageBox().critical(None, "Error", f"{e}")

    return wrapper

#Data oriented class 
class AnimClip: 
     def __init__(self): 
          self.subfix =""
          self.frameMin = mc.playbackOptions(q=True, min=True)
          self.frameMax = mc.playbackOptions(q=True, max=True)
          self.shouldExport = True 




class MayaToUE:
    def __init__(self): 
        self.rootJnt = ""
        self.meshes = []
        self.animationClips : list[AnimClip] =[]

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
        
        mc.select(cl=True)
        rootJntName = self.rootJnt + "_root"
        mc.joint(n=rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName 

    def AddMeshes(self): 
        selection = mc.ls(sl=True)
        if not selection: 
            raise Exception("No mesh selected")
        
        meshes = set()

        for sel in selection: 
            if IsMesh(self): 
                meshes.add(sel)

            if len(meshes) ==0: 
                raise Exception("No mesh selected")
            
            self.meshes = list(meshes)

class AnimClipEntryWidget(QWidget): 
    def __init__(self, animClip: AnimClip): 
         super().__init__()
         self.animClip = animClip
         self.masterLayout = QHBoxLayout()
         self.setLayout(self.masterLayout)

         shouldExportCheckbox = QCheckBox()
         shouldExportCheckbox.setChecked(self.animClip.shouldExport)
         self.masterLayout.addWidget(shouldExportCheckbox)
         shouldExportCheckbox.toggled.connect(self.ShouldExportCheckboxToggled)

         self.masterLayout.addWidget(QLabel("Subfix: "))

         subfixLineEdit = QLineEdit()
         subfixLineEdit.setValidator(QRegExpValidator("[a-zA-z0-9_]+"))
         subfixLineEdit.setText(self.animClip.subfix)
         subfixLineEdit.textChanged.connect(self.SubfixTextchanged)
         self.masterLayout.addWidget(subfixLineEdit)

         self.masterLayout.addWidget(QLabel("Min: "))
         minFrameLineEdit = QLineEdit()
         minFrameLineEdit.setValidator(QIntValidator())
         minFrameLineEdit.setText(str(int(self.animClip.frameMin)))
         minFrameLineEdit.textChanged.connect(self.MinFrameChanged)
         self.masterLayout.addWidget(minFrameLineEdit)

         self.masterLayout.addWidget(QLabel("Max: "))
         maxFrameLineEdit = QLineEdit()
         maxFrameLineEdit.setValidator(QIntValidator())
         maxFrameLineEdit.setText(str(int(self.animClip.frameMax)))
         maxFrameLineEdit.textChanged.connect(self.MaxFrameChanged)
         self.masterLayout.addWidget(maxFrameLineEdit)

         setrangeBtn= QPushButton("[-]")
         setrangeBtn.clicked.connect(self.SetRangeBtnClicked)
         self.masterLayout.addWidget(maxFrameLineEdit)

         deleteBtn = QPushButton("X")
         deleteBtn.clicked.connect(self.DeleteButtonClicked)
         self.masterLayout.addWidget(deleteBtn)


    def DeleteButtonClicked(self): 
         self.deleteLater()

    def SetRangeBtnClicked(self): 
         mc.playbackOptions(e=True, min=self.animClip.frameMin, max= self.animClip.frameMax)
         mc.playbackOptions(e=True, ast=self.animClip.frameMin, aet= self.animClip.frameMax)

    def MaxFrameChanged(self, newVal): 
         self.animClip.frameMax = int(newVal)     

    def MinFrameChanged(self, newVal): 
         self.animClip.frameMin = int(newVal)

    def SubfixTextchanged(self, newText): 
         self.animClip.subfix = newText

    def ShouldExportCheckboxToggled(self): 
         self.animClip.shouldExport = not self.animClip.shouldExport
     

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

        self.meshList = QListWidget()
        self.masterLayout.addWidget(self.meshList)
        self.meshList.setFixedHeight(80)
        addMeshBtn = QPushButton("Add Meshes")
        addMeshBtn.clicked.connect(self.addMeshBtnClicked)
        self.masterLayout.addWidget(addMeshBtn)

        addNewAnimClipEntryBtn = QPushButton("Add Animation Clip")
        addNewAnimClipEntryBtn.clicked.connect(self.addNewAnimClipentryBtnClicked)

    def AddNewAnimClipEntryBtnClicked(self):
         newEntry = self.MayaToUE.AddNewAnimEntry()

    
    @TryAction
    def AddMeshBtnClicked(self):
            self.mayaToUE.AddMeshes()
            self.meshList.clear()
            self.meshList.addItems(self.MayaToUE.rootJnt)


    def AddRootJntButtonClicked(self):
            self.MayaToUE.AddRootJoint()
            self.rootJntText.setText(self.MayaToUE.rootJnt)


    def SetSelectedASRootJointBtnClicked(self):
            self.MayaToUE.SetSelectedAsRootJnt()
            self.rootJntText.setText(self.mayaToUE.rootJnt)

MayaToUEWidget().show()

#AnimClipEntryWidget(AnimClip()).show()

