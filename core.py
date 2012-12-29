# -*- coding: utf-8 -*-
import numpy as np
import math
from cgkit.bvh import Node
from cgkit.cgtypes import mat3, mat4


class Counter(object):
    index = None
    
    def __init__(self):
        self.index = 0


class Bone(object):
    root = None
    node_list = None
    param_offset_list = None
    
    def __init__(self, root):
        self.root = root
        self.node_list = []
        self.param_offset_list = []
        
        self.process_node(root)
        
    def process_node(self, node, counter=None):
        if counter is None:
            counter = Counter()
            
        self.node_list.append(node)
        self.param_offset_list.append(counter.index)
        counter.index += len(node.channels)
        
        for child in node.children:
            self.process_node(child, counter)
            
    def get_offset(self, index_or_node):
        if type(index_or_node) is int:
            index = index_or_node
        else:
            index = self.get_bone_index(index_or_node)
        return self.param_offset_list[index]
        
    def get_bone_index(self, node):
        return self.node_list.index(node)


class Animation(object):
    bone = None
    frames = None
    
    def __init__(self, bone, frames=None):
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
    matrixes_global = None
    matrixes_local = None
    positions = None
    frame = None
    bone = None
    _mat_funcs = {
        "Xrotation": lambda rot: mat4.rotation(rot * math.pi / 180, [1, 0, 0]),
        "Yrotation": lambda rot: mat4.rotation(rot * math.pi / 180, [0, 1, 0]),
        "Zrotation": lambda rot: mat4.rotation(rot * math.pi / 180, [0, 0, 1]),
        "Xposition": lambda pos: mat4.translation((pos, 0, 0)),
        "Yposition": lambda pos: mat4.translation((0, pos, 0)),
        "Zposition": lambda pos: mat4.translation((0, 0, pos)),
        }
    __last_matrix = None

    def __init__(self, bone, frame):
        self.matrixes_global = []
        self.matrixes_local = []
        self.positions = []
        self.__last_matrix = mat4.identity()
        self.bone = bone
        self.frame = frame
        self.process_node(bone.root)
        
    def _calc_mat(self, node):
        mat = mat4.identity()
        channels = node.channels
        param_offset = self.bone.get_offset(node)
        for i, channel in enumerate(channels):
            mat *= self._mat_funcs[channel](self.frame[param_offset + i])
        return mat

    def process_node(self, node):
        if node.isRoot():
            rots = self.frame[3:6]
        elif node.isEndSite():
            rots = [0, 0, 0]
        else:
            index = self.bone.get_offset(node)
            rots = self.frame[index:index + 3]

        mat = self._calc_mat(node)
        
        self.positions.append(self.__last_matrix * node.offset)
        self.matrixes_local.append(mat)
        mat_g = self.__last_matrix * mat4.translation(node.offset) * mat
        self.matrixes_global.append(mat_g)
        
        for child in node.children:
            self.__last_matrix = mat_g
            self.process_node(child)

    def get_position(self, index_or_node):
        if type(index_or_node) is int:
            index = index_or_node
        else:
            index = self.bone.node_list.indexof(node)
        return self.positions[index]

    