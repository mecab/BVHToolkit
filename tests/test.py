# -*- coding: utf-8 -*-
import os
import math
import itertools
import unittest2
import core as target
from cgkit.bvh import Node
from cgkit.bvh import BVHReader
from cgkit.cgtypes import vec3
from cgkit.cgtypes import mat4
from cgkit._core import vec3 as _vec3
from cgkit._core import mat4 as _mat4

class CgTypesAssertionMixin(object):
    def assertVec3Equal(self, v1, v2):
        if not isinstance(v1, _vec3):
            raise AssertionError("First object is not vec3", v1)
        if not isinstance(v2, _vec3):
            raise AssertionError("Second object is not vec3", v2)
        
        for val1, val2 in zip(v1, v2):
            self.assertAlmostEqual(val1, val2)
            
    def assertMat4Equal(self, m1, m2):
        if not isinstance(m1, _mat4):
            raise AssertionError("First object is not mat4", m1)
        if not isinstance(m2, _mat4):
            raise AssertionError("Second object is not mat4", m2)
            
        for val1, val2 in zip(itertools.chain.from_iterable(m1),
                              itertools.chain.from_iterable(m2)):
            self.assertAlmostEqual(val1, val2)

class BoneTest(unittest2.TestCase):
    root = None
    def setUp(self):
        def onHierarchy(root):
            self.root = root
    
        reader = BVHReader(os.path.join(os.path.dirname(__file__), "testBVH.bvh"))
        reader.onHierarchy = onHierarchy
        reader.read()
        
    def test_init(self):
        bone = target.Bone(self.root)
        self.assertEqual(len(bone.node_list), 4)
        
        self.assertEqual(bone.node_list[0].name, "root_name")
        self.assertEqual(bone.node_list[1].name, "joint1")
        self.assertEqual(bone.node_list[2].name, "joint2")
        self.assertEqual(bone.node_list[3].name, "End Site")

    def test_get_bone_index(self):
        bone = target.Bone(self.root)
        self.assertEqual(bone.get_bone_index(bone.node_list[0]), 0)
        self.assertEqual(bone.get_bone_index(bone.node_list[3]), 3)
        
    def test_offset(self):
        bone = target.Bone(self.root)
        self.assertEqual(bone.get_offset(0), 0)
        self.assertEqual(bone.get_offset(bone.node_list[0]), 0)
        self.assertEqual(bone.get_offset(1), 6)
        self.assertEqual(bone.get_offset(3), 12)

class PoseTest(unittest2.TestCase, CgTypesAssertionMixin):
    root = None
    frames = None

    def setUp(self):
        self.root = None
        self.frames = []
    
        def onHierarchy(root):
            self.root = root
            
        def onFrame(frame):
            self.frames.append(frame)
    
        reader = BVHReader(os.path.join(os.path.dirname(__file__), "testBVH.bvh"))
        reader.onHierarchy = onHierarchy
        reader.onFrame = onFrame
        reader.read()


    def test_add_frame(self):
        anim = target.Animation(target.Bone(self.root))
        anim.add_frame(self.frames[0])
        self.assertEqual(len(anim.frames), 1)
        self.assertListEqual(anim.frames[0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        
    def test_pose(self):
        anim = target.Animation(target.Bone(self.root))
        anim.add_frame(self.frames[0])
        anim.add_frame(self.frames[1])
        pose = anim.get_pose(0)
        self.assertVec3Equal(pose.get_position(0), vec3(0, 0, 0))
        self.assertVec3Equal(pose.get_position(3), vec3(0, 60, 0))
        
        pose = anim.get_pose(1)
        self.assertVec3Equal(pose.get_position(3), vec3(0, -60, 0))
        
    def test_calc_matrix(self):
        n1 = Node()
        n1.channels = ["Xposition", "Yposition", "Zposition"]
        n2 = Node()
        n2.channels = []
        n3 = Node()
        n3.channels = ["Xrotation", "Yrotation", "Zrotation"]
        
        n1.children.append(n2)
        n2.children.append(n3)
        bone = target.Bone(n1)

        pose = target.Pose(bone, [10, 20, 30, 90, 90, 90])
        m1 = mat4.translation((10, 20, 30))
        m2 = mat4.rotation(math.pi / 2, (1, 0, 0)) * \
             mat4.rotation(math.pi / 2, (0, 1, 0)) * \
             mat4.rotation(math.pi / 2, (0, 0, 1))
             
        self.assertMat4Equal(pose._calc_mat(n1), m1)
        self.assertMat4Equal(pose._calc_mat(n2), mat4.identity())
        self.assertMat4Equal(pose._calc_mat(n3), m2)
        
        
if __name__ == '__main__':
    unittest2.main()
    