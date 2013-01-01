# -*- coding: utf-8 -*-
import math
from cgkit.bvh import BVHReader
from cgkit.cgtypes import mat4


class BVHAnimationReader(BVHReader):
    """
    Custom BVHReader to create Animation
    """

    @property
    def bone(self):
        return self._bone

    @property
    def root(self):
        if self._bone is not None:
            return self._bone.root
        else:
            return None

    @property
    def frames(self):
        return self._frames

    @property
    def animation(self):
        if self._animation is None and self._bone is not None:
            self._animation = Animation(self._bone, self._frames)

        return self._animation

    def __init__(self, path=None):
        """
        :param str path: Path to a BVH file.
        """

        BVHReader.__init__(self, path)
        self._bone = None
        self._animation = None
        self._frames = None

    def onHierarchy(self, root):
        self._bone = Bone(root)

    def onFrame(self, frame):
        if self._frames is None:
            self._frames = []
        self._frames.append(frame)


class Bone(object):
    """
    A wrapper class of the Node class to handle it easily

    >>> from cgkit.bvh import Node
    >>> n0 = Node()
    >>> n0.channels = ["Xposition", "Yposition"]
    >>> n1 = Node()
    >>> n1.channels = ["Xrotation"]
    >>> n1_1 = Node()
    >>> n1_1.channels = ["Xrotation"]
    >>> n2 = Node()
    >>> n0.children.append(n1)
    >>> n0.children.append(n2)
    >>> n1.children.append(n1_1)
    >>> bone = Bone(n0)

    >>> bone.node_list == [n0, n1, n1_1, n2]
    True

    >>> bone.get_node_index(n0)
    0
    >>> bone.get_node_index(n1)
    1
    >>> bone.get_node_index(n1_1)
    2
    >>> bone.get_node_index(n2)
    3

    >>> bone.get_param_offset(n1)
    2
    >>> bone.get_param_offset(n1_1)
    3
    >>> bone.get_param_offset(n2)
    4
    """

    @property
    def root(self):
        return self._root

    @property
    def node_list(self):
        """
        A list which contains nodes. They are ordered by
        the same order which it described in the HIERARCHY part of the BVH.
        In other word, order of a depth first walk of the HIERARCHY.

        :rtype: list of cgkit.bvh.Node
        :return: list of depth first walked nodes
        """
        return self._node_list

    @property
    def param_offset_list(self):
        """
        A list of start index of channel parameters in frame, for the node
        correspond to the one in node_list.
        You can get channel parameters for the node node_list[i] by:

        frame[param_offset_list[i]:param_offset_list[i] + \
        len(node_list[i].channels)]

        :rtype: list of int
        :return: list of start index of channel parameters in frame
        """
        return self._param_offset_list

    def __init__(self, root):
        self._root = root
        self._node_list = []
        self._param_offset_list = []

        self.__counter = 0
        self._process_node(root)

    def _process_node(self, node):
        self._node_list.append(node)
        self._param_offset_list.append(self.__counter)
        self.__counter += len(node.channels)

        for child in node.children:
            self._process_node(child)

    def get_param_offset(self, index_or_node):
        """
        Shortcut to param_offset_list[i] or
        param_offset_list[node_list.index(node)]
        """

        if type(index_or_node) is int:
            index = index_or_node
        else:
            index = self.get_node_index(index_or_node)
        return self._param_offset_list[index]

    def get_node_index(self, node):
        """
        Shortcut to node_list.index(node)
        """

        return self._node_list.index(node)


class Animation(object):

    @classmethod
    def from_bvh(cls, path):
        reader = BVHAnimationReader(path)
        reader.read()

        return reader.animation

    def __init__(self, bone=None, frames=None):
        self.bone = bone
        if frames is not None:
            self.frames = frames
        else:
            self.frames = []

    def add_frame(self, frame):
        self.frames.append(frame)

    def get_pose(self, frame_num):
        return Pose(self.bone, self.frames[frame_num])


class Pose(object):
    """
    Represent the pose of the bone in the specific frame.

    >>> from cgkit.bvh import Node
    >>> n0 = Node()
    >>> n0.channels = ["Xposition", "Yposition"]
    >>> n1 = Node()
    >>> n1.offset = (10, 0, 0)
    >>> n0.children.append(n1)

    >>> pose = Pose(Bone(n0), [0, 0])
    >>> pose.get_position(n1)
    (10, 0, 0)

    >>> pose = Pose(Bone(n0), [10, 10])
    >>> pose.get_position(n1)
    (20, 10, 0)
    """

    @property
    def matrixes_global(self):
        return self._matrixes_global

    @property
    def matrixes_local(self):
        return self._matrixes_local

    @property
    def positions(self):
        return self._positions

    @property
    def bone(self):
        return self._bone

    @property
    def frame(self):
        return self._frame

    _mat_funcs = {
        "Xrotation": lambda rot: mat4.rotation(rot * math.pi / 180, [1, 0, 0]),
        "Yrotation": lambda rot: mat4.rotation(rot * math.pi / 180, [0, 1, 0]),
        "Zrotation": lambda rot: mat4.rotation(rot * math.pi / 180, [0, 0, 1]),
        "Xposition": lambda pos: mat4.translation((pos, 0, 0)),
        "Yposition": lambda pos: mat4.translation((0, pos, 0)),
        "Zposition": lambda pos: mat4.translation((0, 0, pos)),
    }

    def __init__(self, bone, frame):
        self._matrixes_global = []
        self._matrixes_local = []
        self._positions = []
        self.__last_matrix = mat4.identity()
        self._bone = bone
        self._frame = frame
        self._process_node(bone.root)

    def _calc_mat(self, node):
        mat = mat4.identity()
        channels = node.channels
        param_offset = self._bone.get_param_offset(node)
        for i, channel in enumerate(channels):
            mat *= self._mat_funcs[channel](self._frame[param_offset + i])
        return mat

    def _process_node(self, node):
        mat = self._calc_mat(node)

        self._positions.append(self.__last_matrix * node.offset)
        self._matrixes_local.append(mat)
        mat_g = self.__last_matrix * mat4.translation(node.offset) * mat
        self._matrixes_global.append(mat_g)

        for child in node.children:
            self.__last_matrix = mat_g
            self._process_node(child)

    def get_position(self, index_or_node):
        """
        Returns a global position of given node in the frame
        """

        if type(index_or_node) is int:
            index = index_or_node
        else:
            index = self._bone.node_list.index(index_or_node)
        return self._positions[index]


def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
