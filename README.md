BvhToolKit
==========
A helper library for [cgkit]
This provides some useful function to handle BVH animation format with cgkit.
With this library, you can easily get node positions in the specific frame.

Requirements
------------
* Python 2.7
* cgkit>=2.0.0 (Currently it is not registered to PyPI, so please download from [sourceforge])

Usage
-----
    >>> from BVHToolkit import Animation, Pose, Bone
    >>> from cgkit.bvh import Node

    >>> """Load BVH and get node positions."""
    >>> animation = BVHToolkit.Animation("path_to_bvh.bvh")
    >>> pose = animation.get_pose(3)    # get pose at third frame
    >>> pose.get_position(0)    # get position of the root node
    (0, 0, 0)
    >>> pose.get_position(10)   # get position of the 10th node
    (123, 456, 789)
    
    >>> """Do same thing in nodes generated in the code"""
    >>> n0 = Node()
    >>> n0.channels = ["Xposition", "Yposition"]
    >>> n1 = Node()
    >>> n1.offset = (10, 0, 0)
    >>> n0.children.append(n1)

    >>> pose = Pose(Bone(n0), [0, 0]) # create Pose from Bone, which wraps Node, and frame parameters
    >>> pose.get_position(n1)
    (10, 0, 0)

    >>> pose = Pose(Bone(n0), [10, 10])
    >>> pose.get_position(n1)
    (20, 10, 0)

  [cgkit]: http://cgkit.sourceforge.net/
  [sourceforge]: http://sourceforge.net/projects/cgkit/files/cgkit/

ChangeLog
---------
* v0.81
    * Fixed critical bug that the node positions was not calculated correctly with the root node with xPosition channels.

* v0.8
    * Initial Release.
