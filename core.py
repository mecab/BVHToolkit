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
            index = self.node_list.index(index_or_node)
        
        return self.param_offset_list[index]


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
    __last_matrix = None

    def __init__(self, bone, frame):
        self.matrixes_global = []
        self.matrixes_local = []
        self.positions = []
        self.__last_matrix = mat4.identity()
        self.bone = bone
        self.frame = frame
        self.process_node(bone.root)
        print self.positions
        print "---"

    def process_node(self, node):
        if node.isRoot():
            rots = self.frame[3:6]
        elif node.isEndSite():
            rots = [0, 0, 0]
        else:
            index = self.bone.get_offset(node)
            rots = self.frame[index:index + 3]

        mat = mat4.rotation(rots[0] * math.pi / 180, [0, 0, 1]) * \
              mat4.rotation(rots[1] * math.pi / 180, [0, 1, 0]) * \
              mat4.rotation(rots[2] * math.pi / 180, [1, 0, 0])
        
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

    