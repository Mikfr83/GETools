# Copyright 2023 by Eugene Gataulin (GenEugene). All Rights Reserved.

import maya.cmds as cmds
import maya.mel as mel

from GETOOLS_SOURCE.utils import Selector

def RotateOrderVisibility(on = True, *args):
	selected = cmds.ls(selection = True, type = "transform")
	for item in selected:
		cmds.setAttr(item + ".rotateOrder", channelBox = on)

def SegmentScaleCompensate(value = 0, *args):
	selected = cmds.ls(selection = True, type = "joint")
	for item in selected:
		cmds.setAttr(item + ".segmentScaleCompensate", value)

def JointDrawStyle(mode = 0, *args):
	selected = cmds.ls(selection = True, type = "joint")
	for item in selected:
		cmds.setAttr(item + ".drawStyle", mode)

def DeleteKeys(*args):
	if (Selector.MultipleObjects(1) == None):
		return
	cmds.cutKey()

def DeleteKeyRange(*args):
	mel.eval('timeSliderClearKey')

def KeysNonkeyableDelete(*args):
	selected = cmds.ls(selection = True)
	counter = 0
	for item in selected:
		attributes = cmds.listAttr(item, channelBox = 1)
		if attributes != None:
			for j in range(len(attributes)):
				cmds.cutKey(item + "." + attributes[j])
				counter += 1
	print ("\nNonkeyable attributes deleted: {0}".format(counter))

def SelectJointsInScene(): # TODO make universal for other types
	selected = cmds.ls(type = "joint")
	cmds.select(selected)

def SetInfinityConstant(selected): # TODO move to new animation class and expose
	cmds.setInfinity(selected, preInfinite = "constant", postInfinite = "constant")

def SetInfinityCycle(selected): # TODO move to new animation class and expose
	cmds.setInfinity(selected, preInfinite = "cycle", postInfinite = "cycle")

def DeleteConstraints(selected, skipLast = False):
	count = len(selected)

	for i in range(count):
		if (skipLast and i == count - 1):
			break
		
		children = cmds.listRelatives(selected[i], type = "constraint")
		for child in children:
			cmds.delete(child)

