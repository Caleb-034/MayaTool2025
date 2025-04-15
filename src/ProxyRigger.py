import importlib
from MayaUtils import GetAllConnectIn, GetUpperStream, IsJoint, IsMesh, IsSkin, QMayaWindow 
from PySide2.QWidgets import QPushButtton, QVBoxLayout
from PySide2.QtWidgets import QPushButton
from maya.app.mayabullet import MayaUtils
import maya.cmds as mc
importlib.reload(MayaUtils)

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

        jnts= GetAllConnectIn(modelShape, GetUpperStream,10, IsJoint)
        if not jnts: 
            raise Exception(f"{mesh} has no joint bound! this tool only works with a rigged model")
        self.jnts = jnts 

        print(f"start build with mesh:: {self.model,}, skin: {self.skin}, and joints: {self.jnts}")

        jntVertMap = self.GenerateJntVertDict()
        segments = []
        ctrls = []
        for jnt, verts in jntVertMap.items(): 
            print(f"joint {jnt} cotrols {verts} primarily")
            newSeg = self.CreateProxyModelForJntAndVerts(jnt, verts)
            if newSeg is None: 
                continue 

            newSkinCluster = mc.skincluster(self.jnts, newSeg)[0]
            mc.copySkinWeights(ss=self.skin, ds=newSkinCluster, nm=True, sa="closestPoint", ia="closestJoint")
            segments.append(newSeg)

            ctrlLocator = "ac_" + jnt + "_proxy"
            mc.spaceLocatorGrp = (n=ctrlLocator)
            ctrlLocatorGrp = ctrlLocator + "_grp"
            mc.group(ctrlLocator, n=ctrlLocatorGrp)
            mc.matchTransform(ctrlLocatorGrp, jnt)

            visibilityAttr = "vis"
            mc.addAttr(ctrlLocator, ln=visibilityAttr, min=0, max=1, dv=1, r=True)
            mc.connectAttr(ctrlLocator +"." + visibilityAttr, newSeg + ".v")
            ctrls.append(ctrlLocatorGrp)

        proxyTopGrp = self.model + "_proxy_grp"
        mc.group(segments, n=proxyTopGrp)

        ctrlLocatorGrp = "ac_" + self.model +"_proxy_grp"
        mc.group(ctrls, n=ctrlTopGrp)
        globalProxyCtrl = "ac_" +self.model + "_proxy_global_"
        mc.circle(n=globalProxyCtrl, r=30)
        mc.parent(proxyTopGrp, globalProxyCtrl)
        mc.parent(ctrlTopGrp, globalProxyCtrl)
        mc,setAttr(proxyTopGrp + ".inheritsTRansform", 0)

        visibilityAttr = "vis"
        mc.addAttr(ctrlLocator, ln=visibilityAttr, min= 0, max= 1. dv=1, r=True)
        mc.connectAttr(globalProcyCtrl + "." + visibilityAttr, proxyTopGrp, )



        def CreateProxyModelForJntAndVerts(self, jnt, verts):
            if not verts:
                return None 
            
            faces= mc.polyListComponentConversion(verts, fromVertex=True, toFace=True)
            faces = mc.ls(faces, fl=True)

            labels = set() #a set is like a list, but only holds unique elements, and it is not ordered, it is faster than list when it comes to looking for stuff inside. 
            for face in faces: 
                labels.add(face.replace(self.model, ""))
                
            dup=mc.duplicate(self.model)[0]

            allDupFaces = mc.ls(f"{dup}.f[*]",fl=True )
            facesToDelete = []
            for dupFace in allDupFaces: 
                label = dupFace.replace(dup, "")
                if label not in labels: 
                    facesToDelete.append(dupFace)

            mc.delete(facesToDelete)

            dupName = self.model + "_" + jnt + "_proxy"
            mc.rename(dup, dupName)
            return dupName

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

            for i in range(1, len(weights)):
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