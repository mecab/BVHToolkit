# -*- coding: utf-8 -*-
import os
import math
import itertools
import unittest
import doctest
import BVHToolkit
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


bvh_serial_path = os.path.join(os.path.dirname(__file__), "testBVH.bvh")
bvh_parallel_path = os.path.join(os.path.dirname(__file__), "testBVH2.bvh")
bvh_serial = {"root": None, "frames": None}
bvh_parallel = {"root": None, "frames": None}


def setUpModule():

    class CustomBVHReader(BVHReader):
        def __init__(self, path=None):
            BVHReader.__init__(self, path)
            self.frames = []

        def onHierarchy(self, root):
            self.root = root

        def onFrame(self, frame):
            self.frames.append(frame)

    reader = CustomBVHReader(bvh_serial_path)
    reader.read()
    bvh_serial["root"] = reader.root
    bvh_serial["frames"] = reader.frames

    reader = CustomBVHReader(bvh_parallel_path)
    reader.read()
    bvh_parallel["root"] = reader.root
    bvh_parallel["frames"] = reader.frames


class BVHAnimationReaderTest(unittest.TestCase):

    def test_unloaded(self):
        reader = BVHToolkit.BVHAnimationReader(bvh_serial_path)
        self.assertIsNone(reader.bone)
        self.assertIsNone(reader.root)
        self.assertIsNone(reader.frames)

    def test_loaded(self):
        reader = BVHToolkit.BVHAnimationReader(bvh_parallel_path)
        reader.read()
        self.assertIsNotNone(reader.bone)
        self.assertEqual(reader.bone.root, reader.root)
        self.assertEqual(len(reader.animation.frames), 2)


class BoneTest(unittest.TestCase):

    def test_init_serial(self):
        bone = BVHToolkit.Bone(bvh_serial["root"])
        self.assertEqual(len(bone.node_list), 4)

        self.assertEqual(bone.node_list[0].name, "root_name")
        self.assertEqual(bone.node_list[1].name, "joint1")
        self.assertEqual(bone.node_list[2].name, "joint2")
        self.assertEqual(bone.node_list[3].name, "End Site")

    def test_init_parallel(self):
        bone = BVHToolkit.Bone(bvh_parallel["root"])
        self.assertEqual(len(bone.node_list), 5)

        self.assertEqual(bone.node_list[0].name, "root_name")
        self.assertEqual(bone.node_list[1].name, "joint1")
        self.assertEqual(bone.node_list[2].name, "End Site")
        self.assertEqual(bone.node_list[3].name, "joint2")
        self.assertEqual(bone.node_list[4].name, "End Site")

    def test_get_node_index(self):
        bone = BVHToolkit.Bone(bvh_serial["root"])
        self.assertEqual(bone.get_node_index(bone.node_list[0]), 0)
        self.assertEqual(bone.get_node_index(bone.node_list[3]), 3)

    def test_offset_serial(self):
        bone = BVHToolkit.Bone(bvh_serial["root"])
        self.assertEqual(bone.get_param_offset(0), 0)
        self.assertEqual(bone.get_param_offset(1), 6)
        self.assertEqual(bone.get_param_offset(2), 9)
        self.assertEqual(bone.get_param_offset(3), 12)
        self.assertEqual(bone.get_param_offset(bone.node_list[0]), 0)
        self.assertEqual(bone.get_param_offset(bone.node_list[1]), 6)
        self.assertEqual(bone.get_param_offset(bone.node_list[2]), 9)
        self.assertEqual(bone.get_param_offset(bone.node_list[3]), 12)

    def test_offset_parallel(self):
        bone = BVHToolkit.Bone(bvh_parallel["root"])
        self.assertEqual(bone.get_param_offset(0), 0)
        self.assertEqual(bone.get_param_offset(1), 6)
        self.assertEqual(bone.get_param_offset(2), 9)
        self.assertEqual(bone.get_param_offset(3), 9)
        self.assertEqual(bone.get_param_offset(4), 12)
        self.assertEqual(bone.get_param_offset(bone.node_list[0]), 0)
        self.assertEqual(bone.get_param_offset(bone.node_list[1]), 6)
        self.assertEqual(bone.get_param_offset(bone.node_list[2]), 9)
        self.assertEqual(bone.get_param_offset(bone.node_list[3]), 9)
        self.assertEqual(bone.get_param_offset(bone.node_list[4]), 12)


class AnimationTest(unittest.TestCase):

    def test_add_frame(self):
        anim = BVHToolkit.Animation(BVHToolkit.Bone(bvh_serial["root"]))
        anim.add_frame(bvh_serial["frames"][0])
        self.assertEqual(len(anim.frames), 1)
        self.assertListEqual(anim.frames[0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                             
    def test_poses(self):
        anim = BVHToolkit.Animation(BVHToolkit.Bone(bvh_serial["root"]))
        anim.add_frame(bvh_serial["frames"][0])
        anim.add_frame(bvh_serial["frames"][1])
        self.assertEqual(len([x for x in anim.poses]), 2)
        self.assertEqual(type(anim.poses[0]), BVHToolkit.Pose)
        self.assertEqual(type(anim.poses[1]), BVHToolkit.Pose)

class PoseTest(unittest.TestCase, CgTypesAssertionMixin):

    def test_pose_serial(self):
        anim = BVHToolkit.Animation(BVHToolkit.Bone(bvh_serial["root"]))
        anim.add_frame(bvh_serial["frames"][0])
        anim.add_frame(bvh_serial["frames"][1])
        pose = anim.get_pose(0)
        self.assertVec3Equal(pose.get_position(0), vec3(0, 0, 0))
        self.assertVec3Equal(pose.get_position(3), vec3(0, 60, 0))

        pose = anim.get_pose(1)
        self.assertVec3Equal(pose.get_position(3), vec3(0, -60, 0))

    def test_pose_parallel(self):
        anim = BVHToolkit.Animation(BVHToolkit.Bone(bvh_parallel["root"]))
        anim.add_frame(bvh_parallel["frames"][0])
        anim.add_frame(bvh_parallel["frames"][1])
        pose = anim.get_pose(0)
        self.assertVec3Equal(pose.get_position(0), vec3(0, 0, 0))
        self.assertVec3Equal(pose.get_position(2), vec3(0, 30, 0))
        self.assertVec3Equal(pose.get_position(4), vec3(0, 0, 30))

        pose = anim.get_pose(1)
        self.assertVec3Equal(pose.get_position(2), vec3(0, -10, 0))
        self.assertVec3Equal(pose.get_position(4), vec3(0, 0, -10))

    def test_calc_matrix(self):
        n1 = Node()
        n1.channels = ["Xposition", "Yposition", "Zposition"]
        n2 = Node()
        n2.channels = []
        n3 = Node()
        n3.channels = ["Xrotation", "Yrotation", "Zrotation"]

        n1.children.append(n2)
        n2.children.append(n3)
        bone = BVHToolkit.Bone(n1)

        pose = BVHToolkit.Pose(bone, [10, 20, 30, 90, 90, 90])
        m1 = mat4.translation((10, 20, 30))
        m2 = mat4.rotation(math.pi / 2, (1, 0, 0)) * \
            mat4.rotation(math.pi / 2, (0, 1, 0)) * \
            mat4.rotation(math.pi / 2, (0, 0, 1))

        self.assertMat4Equal(pose._calc_mat(n1), m1)
        self.assertMat4Equal(pose._calc_mat(n2), mat4.identity())
        self.assertMat4Equal(pose._calc_mat(n3), m2)


def load_tests(loader, tests, ignore):
    """ Add doctests to the test suite. """

    tests.addTests(doctest.DocTestSuite(BVHToolkit._core))
    return tests

if __name__ == '__main__':
    unittest.main()
