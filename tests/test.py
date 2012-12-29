# -*- coding: utf-8 -*-
import os
import unittest2
import core as target
from cgkit.bvh import Node
from cgkit.bvh import BVHReader
from cgkit.cgtypes import vec3
from cgkit._core import vec3 as _vec3

class CgTypesAssertionMixin(object):
    def assertVec3Equal(self, v1, v2):
        if not isinstance(v1, _vec3):
            raise AssertionError("First object is not vec3", v1)
        if not isinstance(v2, _vec3):
            raise AssertionError("Second object is not vec3", v2)
        
        for val1, val2 in zip(v1, v2):
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

    def test_offset(self):
        bone = target.Bone(self.root)
        self.assertEqual(bone.get_offset(0), 0)
        self.assertEqual(bone.get_offset(bone.node_list[0]), 0)
        self.assertEqual(bone.get_offset(1), 6)
        self.assertEqual(bone.get_offset(bone.node_list[1]), 6)
        self.assertEqual(bone.get_offset(3), 12)
        self.assertEqual(bone.get_offset(bone.node_list[3]), 12)

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
        
if __name__ == '__main__':
    unittest2.main()
    