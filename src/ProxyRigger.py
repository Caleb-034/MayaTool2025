from MayaUtils import QMayaWindow 
from PySide2.QWidgets import QPushButtton, QVBoxLayout
import maya.cmds as mc
importlib.reload(MayaUtils)
import ImportLin

class ProxyRigger: 
    def __init__(self): 
        self.skin = ""
        self.model = ""
        self.jnts = []

    def CreateProxyRigFromSelectedMesh(self): 
        mesh = mc.ls(sl=True)[0]
        if not IsMesh(mesh):
            raise TypeError(f"{mesh} is not a mesh! please select a mesh")
        
        self.model = mesh 
        modelShape = mc.listRelatives(self.mocel, s=True)[0]
        print(f"found mesh {mesh} and shape {modelShape}")

        skin = GetAllConnectIn(modelShape, GetUpperStream,10, IsSkin)
        if not skin: 
            raise Exception(f"{mesh} has no skin! this tool only works with a rigged model")
        self.skin = skin[0]

        jnts= GetAllConnnectIn(modelShape, GetUpperStream,10, IsJoint)
        if not jnts: 
            raise Exception(f"{mesh} has no joint bound! this tool only works with a rigged model")
        self.jnts = jnts 

        print(f"start build with mesh:: {self.model,}, skin: {self.skin}, and joints: {self.jnts}")

        jntVertMap = self.GenerateJntVertDict()
        segments = []
        ctrls = []
        for jnt, verts in jntVertMap.items(): 
            print(f"joint {jnt} cotrols {verts} primarily")

        def GenerateJntVerDict(self):
            dict = {}
            for jnt in self.jnts: 
                dict[jnt] = []

                verts = mc.ls(f"{self.model}".vtx[*]*, fl= True)
                for vert in verts: 
                    owningJnt = self.GetJntWithMaxInfluence(vert, vert, self.skin)
                    dict[owningJnt].append(vert)

        def GetJntWithMaxInfluence(self, vert, skin): 
            weights = mc.skinPercent(skin, vert, q=True, v=True)
            jnts= mc.skinPercent(skin, vert, q=True, t=None)

            maxWeightIndex = 0 
            maxWeight = weights[0]

            for i in range(1, len(Weights)):
                if  weights[i] >  maxWeight: 
                    maxWeight = weights [i]
                    maxWeightIndex = i 

                    return jnts[maxWeightIndex]





class ProxyRiggerWidget(QMayaWindow):
    def __init__(self):
        super().__init__()
        self.proxyRigger = ProxyRigger()
        self.proxyRigger ("Proxy Rigger")
        self.masterLayout = QVBoxLayout()
        self.setLayout(masterLayout)
        generateProxyRigBtn = QPushButton("Generate Proxy Rig")
        self.masterLayout.addWidget(generateProxyRigBtn)
        generateProxyRigBtn.clicked.connect(self.GenerateProxyRigButton)

    def GenerateProxyRigButtonClicked(self):
        self.proxyRigger.CreateProxyRigFromSelectedMesh()

    def GetWindowHash(self): 
        return "adsjkfhoaefahdkjafhhaeu"#replace with hash fr later later 
    
proxyRiggerWidget = ProxyRiggerWidget()
proxyRiggerWidget.show()