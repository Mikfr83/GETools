# Copyright 2023 by Eugene Gataulin (GenEugene). All Rights Reserved.

import maya.cmds as cmds
from functools import partial

from GETOOLS_SOURCE.utils import Colors
from GETOOLS_SOURCE.utils import Constraints
from GETOOLS_SOURCE.utils import Other
from GETOOLS_SOURCE.utils import Selector
from GETOOLS_SOURCE.utils import Skinning
from GETOOLS_SOURCE.utils import UI

from GETOOLS_SOURCE.modules import Settings

class RiggingAnnotations:
	# Constraints
	_textAllSelectedConstrainToLast = "All selected objects will be constrained to last selected object"
	constraintReverse = "Reverse the direction of operation from last to first selected"
	constraintMaintain = "Use maintain offset"
	constraintOffset = "[IN DEVELOPMENT]\nAdd extra locators structure with ability to make offset animation"
	constraintParent = "Parent constrain.\n{allToLast}".format(allToLast = _textAllSelectedConstrainToLast)
	constraintPoint = "Point constrain.\n{allToLast}".format(allToLast = _textAllSelectedConstrainToLast)
	constraintOrient = "Orient constrain.\n{allToLast}".format(allToLast = _textAllSelectedConstrainToLast)
	constraintScale = "Scale constrain.\n{allToLast}".format(allToLast = _textAllSelectedConstrainToLast)
	constraintAim = "[IN DEVELOPMENT]\nAim constrain.".format(allToLast = _textAllSelectedConstrainToLast) # TODO
	constraintDisconnectSelected = "Disconnect targets objects from last selected object. They will be deleted from constrain attributes."
	constraintDelete = "Delete all constraints on selected objects"

	# Utils
	_rotateOrder = "rotate order attribute in channel box for all selected objects"
	rotateOrderShow = "Show {0}".format(_rotateOrder)
	rotateOrderHide = "Hide {0}".format(_rotateOrder)
	_scaleCompensate = "segment scale compensate attribute for all selected joints"
	scaleCompensateOn = "Activate {0}".format(_scaleCompensate)
	scaleCompensateOff = "Deactivate {0}".format(_scaleCompensate)
	_jointDrawStyle = "selected joints draw style"
	jointDrawStyleBone = "Bone {0}".format(_jointDrawStyle)
	jointDrawStyleHidden = "Hidden {0}".format(_jointDrawStyle)
	copySkinWeights = "Copy skin weights from last selected object to all other selected objects"

class Rigging:
	version = "v0.0.3"
	name = "RIGGING"
	title = name + " " + version

	def __init__(self):
		self.checkboxConstraintReverse = None
		self.checkboxConstraintMaintain = None
		self.checkboxConstraintOffset = None
	def UICreate(self, layoutMain):
		windowWidthMargin = Settings.windowWidthMargin
		lineHeight = Settings.lineHeight


		# CONSTRAINTS
		layoutConstraints = cmds.frameLayout(parent = layoutMain, label = "CONSTRAINTS", collapsable = True)
		layoutColumnConstraints = cmds.columnLayout(parent = layoutConstraints, adjustableColumn = True)
		#
		countOffsets = 4
		cmds.gridLayout(parent = layoutColumnConstraints, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.separator(style = "none")
		self.checkboxConstraintReverse = UI.Checkbox(label = "Reverse", value = False, annotation = RiggingAnnotations.constraintReverse)
		self.checkboxConstraintMaintain = UI.Checkbox(label = "Maintain", value = False, annotation = RiggingAnnotations.constraintMaintain)
		# self.checkboxConstraintOffset = UI.Checkbox(label = "Offset", value = False, annotation = RiggingAnnotations.constraintOffset)
		cmds.separator(style = "none")
		#
		countOffsets = 5
		cmds.gridLayout(parent = layoutColumnConstraints, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "Parent", command = self.ConstrainParent, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintParent)
		cmds.button(label = "Point", command = self.ConstrainPoint, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintPoint)
		cmds.button(label = "Orient", command = self.ConstrainOrient, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintOrient)
		cmds.button(label = "Scale", command = self.ConstrainScale, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintScale)
		cmds.button(label = "Aim", command = self.ConstrainAim, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintAim, enable = False)
		#
		countOffsets = 2
		cmds.gridLayout(parent = layoutColumnConstraints, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "Disconnect", command = self.DisconnectTargetsFromConstraint, backgroundColor = Colors.red50, annotation = RiggingAnnotations.constraintDisconnectSelected)
		cmds.button(label = "Delete Constraints", command = self.DeleteConstraints, backgroundColor = Colors.red50, annotation = RiggingAnnotations.constraintDelete)


		# UTILS
		layoutUtils = cmds.frameLayout(parent = layoutMain, label = "UTILS", collapsable = True)
		layoutColumnUtils = cmds.columnLayout(parent = layoutUtils, adjustableColumn = True)
		#
		countOffsets = 2
		cmds.gridLayout(parent = layoutColumnUtils, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "Rotate order\nSHOW", command = partial(Other.RotateOrderVisibility, True), backgroundColor = Colors.green10, annotation = RiggingAnnotations.rotateOrderShow)
		cmds.button(label = "Rotate order\nHIDE", command = partial(Other.RotateOrderVisibility, False), backgroundColor = Colors.green10, annotation = RiggingAnnotations.rotateOrderHide)
		cmds.button(label = "Segment Scale\nCompensate ON", command = partial(Other.SegmentScaleCompensate, True), backgroundColor = Colors.yellow10, annotation = RiggingAnnotations.scaleCompensateOn)
		cmds.button(label = "Segment Scale\nCompensate OFF", command = partial(Other.SegmentScaleCompensate, False), backgroundColor = Colors.yellow10, annotation = RiggingAnnotations.scaleCompensateOff)
		cmds.button(label = "Joint\nBONE", command = partial(Other.JointDrawStyle, 0), backgroundColor = Colors.orange10, annotation = RiggingAnnotations.jointDrawStyleBone)
		cmds.button(label = "Joint\nHIDDEN", command = partial(Other.JointDrawStyle, 2), backgroundColor = Colors.orange10, annotation = RiggingAnnotations.jointDrawStyleHidden)
		#
		countOffsets = 1
		cmds.gridLayout(parent = layoutColumnUtils, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "Copy Skin Weights\nFrom Last Selected", command = Skinning.CopySkinWeightsFromLastMesh, backgroundColor = Colors.blue10, annotation = RiggingAnnotations.copySkinWeights)


	# CONSTRAINTS
	def ConstrainParent(self, *args):
		Constraints.ConstrainSelectedToLastObject(reverse = self.checkboxConstraintReverse.Get(), maintainOffset = self.checkboxConstraintMaintain.Get(), parent = True, point = False, orient = False, scale = False, aim = False)
	def ConstrainPoint(self, *args):
		Constraints.ConstrainSelectedToLastObject(reverse = self.checkboxConstraintReverse.Get(), maintainOffset = self.checkboxConstraintMaintain.Get(), parent = False, point = True, orient = False, scale = False, aim = False)
	def ConstrainOrient(self, *args):
		Constraints.ConstrainSelectedToLastObject(reverse = self.checkboxConstraintReverse.Get(), maintainOffset = self.checkboxConstraintMaintain.Get(), parent = False, point = False, orient = True, scale = False, aim = False)
	def ConstrainScale(self, *args):
		Constraints.ConstrainSelectedToLastObject(reverse = self.checkboxConstraintReverse.Get(), maintainOffset = self.checkboxConstraintMaintain.Get(), parent = False, point = False, orient = False, scale = True, aim = False)
	def ConstrainAim(self, *args): # TODO
		Constraints.ConstrainSelectedToLastObject(reverse = self.checkboxConstraintReverse.Get(), maintainOffset = self.checkboxConstraintMaintain.Get(), parent = False, point = False, orient = False, scale = False, aim = True)

	def DeleteConstraints(self, *args):
		selectedList = Selector.MultipleObjects(1)
		if (selectedList == None):
			return
		Constraints.DeleteConstraints(selectedList)
	def DisconnectTargetsFromConstraint(self, *args):
		selectedList = Selector.MultipleObjects(2)
		if (selectedList == None):
			return
		Constraints.DisconnectTargetsFromConstraint(selectedList)

