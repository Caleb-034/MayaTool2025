import os 
from MayaUtils import *
from PySide2.QtCore import Signal
from PySide2.QtGui import QIntValidator, QRegExpValidator
from PySide2.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout, QWidget
import maya.cmds as mc

def TryAction(action):
    def wrapper(*args, **kwargs):
        try: 
            action(*args, **kwargs)
        except Exception as e:
            QMessageBox().critical(None, "Error", f"{e}")

    return wrapper

# Data oriented class
class AnimClip:
    def __init__(self):
        self.subfix = ""
        self.frameMin = mc.playbackOptions(q=True, min=True) 
        self.frameMax = mc.playbackOptions(q=True, max=True)
        self.shouldExport = True

class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.meshes = []
        self.animationClips : list[AnimClip] = []
        self.fileName = ""
        self. saveDir = ""

    def GetAllJoints(self): 
        jnts = []
        jnts.append(self.rootJnt)
        children = mc.listRElatives(self.rootJnt, c=True, ad=True, type="joint")
        if children: 
            jnts.extend(children) 

        return jnts 
    
    def SaveFiles(self): 
        allJnts = self.GetAllJoints()
        allMeshes = self.meshes 

    def SendToUnreal()
        ueUtilPath = os.path.join(MayaPluginSpring2025sec1.srcDir, "UnrealUtils.py")
        ueUtilPath = os.parth.normpath(ueUtilPath)

        meshPath = self.GetSkeletalMeshSavePath().replace("\\", "/")
        aimDir = self.getAnimDirPAth().replace("\\", "/")

        command = []
        with open (ueUtilPath, 'r') as ueUtilityFile: 
            commands = ueUtilityFile.readlines()

            commands.append(f"\nImportMeshAndAnimation(\'{meshPath}\', \'{aimDir}'\)")

            command = "".join(commands)
            print(command)

    def RemoveAnimClip(self, clipToRemove: AnimClip):
        self.animationClips.remove(clipToRemove)
        print(f"animation clip removed, now we have: {len(self.animationClips)} left")

    def AddNewAnimEntry(self):
        self.animationClips.append(AnimClip())
        print(f"animation clip added, now we have: {len(self.animationClips)} anim clips")
        return self.animationClips[-1]

    def SetSelectedAsRootJnt(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("Nothing Selected, Please Select the Root Joint of the Rig!")

        selectedJnt = selection[0]
        if not IsJoint(selectedJnt):
            raise Exception(f"{selectedJnt} is not a joint, Please Select the Root Joint of the Rig!")

        self.rootJnt = selectedJnt 

    def AddRootJoint(self):
        if (not self.rootJnt) or (not mc.objExists(self.rootJnt)):
            raise Exception("no Root Joint Assigned, please set the current root joint of the rig first")

        currentRootJntPosX, currentRootJntPosY, currentRootJntPosZ = mc.xform(self.rootJnt, q=True, t=True, ws=True)
        if currentRootJntPosX == 0 and currentRootJntPosY == 0 and currentRootJntPosZ == 0:
            raise Exception("current root joint is already at origin, no need to make a new one!")

        mc.select(cl=True)  
        rootJntName = self.rootJnt + "_root"
        mc.joint(n=rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName

    def AddMeshs(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("No Mesh Selected")

        meshes = set()

        for sel in selection:
            if IsMesh(sel):
                meshes.add(sel)

        if len(meshes) == 0:
            raise Exception("No Mesh Selected")

        self.meshes = list(meshes)

class AnimClipEntryWidget(QWidget):
    entryRemoved = Signal(AnimClip)
    def __init__(self, animClip: AnimClip):
        super().__init__()
        self.animClip = animClip
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        shouldExportCheckbox = QCheckBox()
        shouldExportCheckbox.setChecked(self.animClip.shouldExport)
        self.masterLayout.addWidget(shouldExportCheckbox)
        shouldExportCheckbox.toggled.connect(self.ShouldExportCheckboxToogled)

        self.masterLayout.addWidget(QLabel("Subfix: "))

        subfixLineEdit = QLineEdit()
        subfixLineEdit.setValidator(QRegExpValidator("[a-zA-Z0-9_]+"))
        subfixLineEdit.setText(self.animClip.subfix)        
        subfixLineEdit.textChanged.connect(self.SubfixTextChanged)
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

        setRangeBtn = QPushButton("[-]")
        setRangeBtn.clicked.connect(self.SetRangeBtnClicked)
        self.masterLayout.addWidget(setRangeBtn)

        deleteBtn = QPushButton("X")
        deleteBtn.clicked.connect(self.DeleteButtonClicked)
        self.masterLayout.addWidget(deleteBtn)

    
    def DeleteButtonClicked(self):
        self.entryRemoved.emit(self.animClip)
        self.deleteLater()


    def SetRangeBtnClicked(self):
        mc.playbackOptions(e=True, min=self.animClip.frameMin, max=self.animClip.frameMax)
        mc.playbackOptions(e=True, ast=self.animClip.frameMin, aet=self.animClip.frameMax)


    def MaxFrameChanged(self, newVal):
        self.animClip.frameMax = int(newVal)


    def MinFrameChanged(self, newVal):
        self.animClip.frameMin = int(newVal)


    def SubfixTextChanged(self, newText):
        self.animClip.subfix = newText


    def ShouldExportCheckboxToogled(self):
        self.animClip.shouldExport = not self.animClip.shouldExport

class MayaToUEWidget(QMayaWindow):
    def GetWindowHash(self):
        return "MayaToUEJL4172025745"


    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()
        self.setWindowTitle("Maya to UE")

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
        addMeshBtn.clicked.connect(self.AddMeshBtnClicked)
        self.masterLayout.addWidget(addMeshBtn)

        addNewAnimClipEntryBtn = QPushButton("Add Animation Clip")
        addNewAnimClipEntryBtn.clicked.connect(self.AddNewAnimClipEntryBtnClicked)
        self.masterLayout.addWidget(addNewAnimClipEntryBtn)

        self.animEntryLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.animEntryLayout)

        self.saveFileLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.SaveFileLayout)
        fileNameLabel = QLabel("File Name: ")
        self.saveFileLayout.addwidget(fileNameLabel)
        


    def AddNewAnimClipEntryBtnClicked(self):
        newEntry = self.mayaToUE.AddNewAnimEntry()
        newEntryWidget = AnimClipEntryWidget(newEntry)
        newEntryWidget.entryRemoved.connect(self.AnimClipEntryRemoved)
        self.animEntryLayout.addWidget(newEntryWidget)

    @TryAction
    def AnimClipEntryRemoved(self, animClip: AnimClip):
        self.mayaToUE.RemoveAnimClip(animClip)

    @TryAction
    def AddMeshBtnClicked(self):
        self.mayaToUE.AddMeshs()
        self.meshList.clear()
        self.meshList.addItems(self.mayaToUE.meshes)


    @TryAction
    def AddRootJntButtonClicked(self):
        self.mayaToUE.AddRootJoint()
        self.rootJntText.setText(self.mayaToUE.rootJnt)


    @TryAction
    def SetSelectionAsRootJointBtnClicked(self):
        self.mayaToUE.SetSelectedAsRootJnt()
        self.rootJntText.setText(self.mayaToUE.rootJnt)

MayaToUEWidget().show()   
# AnimClipEntryWidget(AnimClip()).show()

