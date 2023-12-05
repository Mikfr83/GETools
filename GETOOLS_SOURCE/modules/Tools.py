# Copyright 2023 by Eugene Gataulin (GenEugene). All Rights Reserved.

import maya.cmds as cmds
from functools import partial

from GETOOLS_SOURCE.utils import Baker
from GETOOLS_SOURCE.utils import Colors
from GETOOLS_SOURCE.utils import Locators
from GETOOLS_SOURCE.utils import Other
from GETOOLS_SOURCE.utils import Selector
from GETOOLS_SOURCE.utils import Timeline
from GETOOLS_SOURCE.utils import UI

from GETOOLS_SOURCE.modules import Settings

class ToolsAnnotations:
	# Other
	# printSelectedToConsole = "Just print all selected objects to console and count them"
	selectTransformHiererchy = "Select all children \"transform\" objects. \nWorks with multiple selected objects"

	# Locators
	hideParent = "Deactivate visibility on parent locator. \nUsually better to use with \"Sub Locator\" checkbox activated"
	subLocator = "Create an extra locator inside the main locator for additional local control"
	locatorSize = "Initial size of locator"
	locator = "Create new locator on the world origin"
	locatorMatch = "Create and match locators to selected objects"
	locatorParent = "Create and parent constraint locators to selected objects"
	locatorsBake = "Create locators on selected objects and bake animation"
	_reverseConstraint = "After that parent constrain original objects back to locators"
	locatorsBakeReverse = "{bake}\n{reverse}".format(bake = locatorsBake, reverse = _reverseConstraint)
	locatorsRelative = "{bake}\nThe last locator becomes the parent of other locators".format(bake = locatorsBake)
	locatorsRelativeReverse = "{relative}\n{reverse}\nRight click allows you to bake the same operation but with constrained last object.".format(relative = locatorsRelative, reverse = _reverseConstraint)
	locatorsBakeAim = "[IN DEVELOPMENT]\nLocators Bake Aim" # TODO
	locatorAimDistance = "[IN DEVELOPMENT]\nLocator Aim distance from original object. Need to use non-zero value" # TODO

	# Bake
	_bakeCutOutside = "Keys outside of time range or selected range will be removed"
	bakeClassic = "Regular maya bake \"Edit/Keys/Bake Simulation\""
	bakeClassicCut = "{0}.\n{1}".format(bakeClassic, _bakeCutOutside)
	bakeCustom = "Alternative way to bake.\nThe same if you just set key every frame on time range.\nAlso works with animation layers."
	bakeCustomCut = "{0}\n{1}".format(bakeCustom, _bakeCutOutside)
	bakeByLast = "Bake selected objects relative to the last selected object as if they were constrained"

	# Animation
	deleteNonkeyableKeys = "Delete animation on all nonkeyable attributes of selected objects"
	deleteAnimation = "Delete all animation from selected objects"
	deleteKeyRange = "Delete selected time range keys of selected objects. \nAlso works with selected attributes in Channel Box"

	timelineSetMinOuter = "Set minimal outer timeline value"
	timelineSetMinInner = "Set minimal inner timeline value"
	timelineSetMaxInner = "Set maximum inner timeline value"
	timelineSetMaxOuter = "Set maximum outer timeline value"
	timelineExpandOuter = "Expand timeline range to outer range"
	timelineExpandInner = "Expand timeline range to inner range"
	timelineFocusRange = "Set timeline inner range on selected range by mouse"

class ToolsSettings:
	# SLIDERS (field min/max, slider min/max)
	rangeLocatorAimOffset = (0, float("inf"), 0, 200)

class Tools:
	version = "v0.1.4"
	name = "TOOLS"
	title = name + " " + version

	def __init__(self):
		self.checkboxLocatorHideParent = None
		self.checkboxLocatorSubLocator = None
		self.floatLocatorSize = None
		self.floatLocatorAimOffset = None
	def UICreate(self, layoutMain):
		windowWidthMargin = Settings.windowWidthMargin
		lineHeight = Settings.lineHeight
		sliderWidth = Settings.sliderWidth
		sliderWidthMarker = Settings.sliderWidthMarker

		self.UILayoutSelect(layoutMain, windowWidthMargin, lineHeight)
		self.UILayoutLocators(layoutMain, windowWidthMargin, lineHeight, sliderWidth, sliderWidthMarker)
		self.UILayoutBake(layoutMain, windowWidthMargin, lineHeight)
		self.UILayoutAnimation(layoutMain, windowWidthMargin, lineHeight)
	def UILayoutSelect(self, layoutMain, windowWidthMargin, lineHeight):
		layoutLocators = cmds.frameLayout(parent = layoutMain, label = "SELECT", collapsable = True)
		#
		countOffsets = 1
		cmds.gridLayout(parent = layoutLocators, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "Select Transform\nHiererchy", command = Selector.SelectTransformHierarchy, backgroundColor = Colors.blue10, annotation = ToolsAnnotations.selectTransformHiererchy)
		# cmds.separator(style = "none")
		pass
	def UILayoutLocators(self, layoutMain, windowWidthMargin, lineHeight, sliderWidth, sliderWidthMarker):
		layoutLocators = cmds.frameLayout(parent = layoutMain, label = "LOCATORS", collapsable = True)
		#
		countOffsets = 3
		cmds.gridLayout(parent = layoutLocators, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		self.checkboxLocatorHideParent = UI.Checkbox(label = "Hide Parent", value = False, menuReset = False, annotation = ToolsAnnotations.hideParent)
		self.checkboxLocatorSubLocator = UI.Checkbox(label = "Sub Locator", value = False, menuReset = False, annotation = ToolsAnnotations.subLocator)
		self.floatLocatorSize = UI.FloatField(value = 5, precision = 3, annotation = ToolsAnnotations.locatorSize)
		#
		cmds.button(label = "Locator", command = self.CreateLocator, backgroundColor = Colors.green10, annotation = ToolsAnnotations.locator)
		cmds.button(label = "Locators match", command = self.CreateLocatorMatch, backgroundColor = Colors.green10, annotation = ToolsAnnotations.locatorMatch)
		cmds.button(label = "Locators parent", command = self.CreateLocatorParent, backgroundColor = Colors.green10, annotation = ToolsAnnotations.locatorParent)
		#
		countOffsets = 2
		cmds.gridLayout(parent = layoutLocators, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "Locators bake", command = self.CreateLocatorBake, backgroundColor = Colors.yellow10, annotation = ToolsAnnotations.locatorsBake)
		cmds.button(label = "Locators bake + reverse", command = self.CreateLocatorBakeReverse, backgroundColor = Colors.yellow50, annotation = ToolsAnnotations.locatorsBakeReverse)
		cmds.button(label = "Locators relative", command = self.BakeAsChildrenFromLastSelected, backgroundColor = Colors.orange10, annotation = ToolsAnnotations.locatorsRelative)
		cmds.button(label = "Locators relative + reverse", command = self.BakeAsChildrenFromLastSelectedReverse, backgroundColor = Colors.orange50, annotation = ToolsAnnotations.locatorsRelativeReverse)
		cmds.popupMenu()
		cmds.menuItem(label = "skip last object constrain", command = self.BakeAsChildrenFromLastSelectedReverseSkipLast)
		#
		layoutAim = cmds.gridLayout(parent = layoutLocators, numberOfColumns = 1, cellWidth = windowWidthMargin, cellHeight = lineHeight)
		countOffsets = 6
		cmds.gridLayout(parent = layoutAim, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "X-", command = partial(self.CreateLocatorBakeAim, 1), backgroundColor = Colors.red10, annotation = ToolsAnnotations.locatorsBakeAim) # TODO
		cmds.button(label = "X+", command = partial(self.CreateLocatorBakeAim, 2), backgroundColor = Colors.red50, annotation = ToolsAnnotations.locatorsBakeAim) # TODO
		cmds.button(label = "Y-", command = partial(self.CreateLocatorBakeAim, 3), backgroundColor = Colors.green10, annotation = ToolsAnnotations.locatorsBakeAim) # TODO
		cmds.button(label = "Y+", command = partial(self.CreateLocatorBakeAim, 4), backgroundColor = Colors.green50, annotation = ToolsAnnotations.locatorsBakeAim) # TODO
		cmds.button(label = "Z-", command = partial(self.CreateLocatorBakeAim, 5), backgroundColor = Colors.blue10, annotation = ToolsAnnotations.locatorsBakeAim) # TODO
		cmds.button(label = "Z+", command = partial(self.CreateLocatorBakeAim, 6), backgroundColor = Colors.blue50, annotation = ToolsAnnotations.locatorsBakeAim) # TODO
		self.floatLocatorAimOffset = UI.Slider(
			parent = layoutAim,
			widthWindow = windowWidthMargin,
			widthMarker = sliderWidthMarker,
			columnWidth3 = sliderWidth,
			# command = ,
			label = "Distance",
			annotation = ToolsAnnotations.locatorAimDistance,
			value = 100,
			minMax = ToolsSettings.rangeLocatorAimOffset,
			menuReset = True,
		)
	def UILayoutBake(self, layoutMain, windowWidthMargin, lineHeight):
		layoutBake = cmds.frameLayout(parent = layoutMain, label = "BAKE", collapsable = True)
		#
		countOffsets = 2
		cmds.gridLayout(parent = layoutBake, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "Bake Classic", command = self.BakeSelectedClassic, backgroundColor = Colors.orange10, annotation = ToolsAnnotations.bakeClassic)
		cmds.button(label = "Bake Classic\nCut Outer", command = self.BakeSelectedClassicCut, backgroundColor = Colors.orange10, annotation = ToolsAnnotations.bakeClassicCut)
		cmds.button(label = "Bake Custom", command = self.BakeSelectedCustom, backgroundColor = Colors.orange50, annotation = ToolsAnnotations.bakeCustom)
		cmds.button(label = "Bake Custom\nCut Outer", command = self.BakeSelectedCustomCut, backgroundColor = Colors.orange50, annotation = ToolsAnnotations.bakeCustomCut)
		cmds.button(label = "Bake Selected\nBy Last Object", command = self.BakeSelectedByLastObject, backgroundColor = Colors.orange100, annotation = ToolsAnnotations.bakeByLast)
	def UILayoutAnimation(self, layoutMain, windowWidthMargin, lineHeight):
		layoutRigging = cmds.frameLayout(parent = layoutMain, label = "ANIMATION", collapsable = True)
		#
		countOffsets = 3
		cmds.gridLayout(parent = layoutRigging, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "Delete\nAnimation", command = Other.DeleteKeys, backgroundColor = Colors.red100, annotation = ToolsAnnotations.deleteAnimation)
		cmds.button(label = "Delete\nKey Range", command = Other.DeleteKeyRange, backgroundColor = Colors.red50, annotation = ToolsAnnotations.deleteKeyRange)
		cmds.button(label = "Delete\nNonkeyable Keys", command = Other.KeysNonkeyableDelete, backgroundColor = Colors.red10, annotation = ToolsAnnotations.deleteNonkeyableKeys)
		#
		countOffsets = 7
		cmds.gridLayout(parent = layoutRigging, numberOfColumns = countOffsets, cellWidth = windowWidthMargin / countOffsets, cellHeight = lineHeight)
		cmds.button(label = "<<", command = partial(Timeline.SetTime, 3), backgroundColor = Colors.green10, annotation = ToolsAnnotations.timelineSetMinOuter)
		cmds.button(label = "<", command = partial(Timeline.SetTime, 1), backgroundColor = Colors.lightBlue10, annotation = ToolsAnnotations.timelineSetMinInner)
		cmds.button(label = ">", command = partial(Timeline.SetTime, 2), backgroundColor = Colors.lightBlue10, annotation = ToolsAnnotations.timelineSetMaxInner)
		cmds.button(label = ">>", command = partial(Timeline.SetTime, 4), backgroundColor = Colors.green10, annotation = ToolsAnnotations.timelineSetMaxOuter)
		cmds.button(label = "OUTER", command = partial(Timeline.SetTime, 5), backgroundColor = Colors.blue10, annotation = ToolsAnnotations.timelineExpandOuter)
		cmds.button(label = "INNER", command = partial(Timeline.SetTime, 6), backgroundColor = Colors.blue10, annotation = ToolsAnnotations.timelineExpandInner)
		cmds.button(label = "FOCUS", command = partial(Timeline.SetTime, 7), backgroundColor = Colors.orange10, annotation = ToolsAnnotations.timelineFocusRange)


	# LOCATORS
	def CreateLocator(self, *args):
		Locators.Create(scale = self.floatLocatorSize.Get(), hideParent = self.checkboxLocatorHideParent.Get(), subLocators = self.checkboxLocatorSubLocator.Get())
	def CreateLocatorMatch(self, *args):
		Locators.CreateOnSelected(scale = self.floatLocatorSize.Get(), hideParent = self.checkboxLocatorHideParent.Get(), subLocators = self.checkboxLocatorSubLocator.Get())
	def CreateLocatorParent(self, *args):
		Locators.CreateOnSelectedWithParentConstrain(scale = self.floatLocatorSize.Get(), hideParent = self.checkboxLocatorHideParent.Get(), subLocators = self.checkboxLocatorSubLocator.Get())
	def CreateLocatorBake(self, *args):
		Locators.CreateOnSelectedAndBake(scale = self.floatLocatorSize.Get(), hideParent = self.checkboxLocatorHideParent.Get(), subLocators = self.checkboxLocatorSubLocator.Get())
	def CreateLocatorBakeReverse(self, *args):
		Locators.CreateOnSelectedReverseConstrain(scale = self.floatLocatorSize.Get(), hideParent = self.checkboxLocatorHideParent.Get(), subLocators = self.checkboxLocatorSubLocator.Get())
	def BakeAsChildrenFromLastSelected(self, *args):
		Locators.BakeAsChildrenFromLastSelected(scale = self.floatLocatorSize.Get(), hideParent = self.checkboxLocatorHideParent.Get(), subLocators = self.checkboxLocatorSubLocator.Get())
	def BakeAsChildrenFromLastSelectedReverseSkipLast(self, *args):
		Locators.BakeAsChildrenFromLastSelectedReverse(scale = self.floatLocatorSize.Get(), hideParent = self.checkboxLocatorHideParent.Get(), subLocators = self.checkboxLocatorSubLocator.Get(), skipLastReverse = True)
	def BakeAsChildrenFromLastSelectedReverse(self, *args):
		Locators.BakeAsChildrenFromLastSelectedReverse(scale = self.floatLocatorSize.Get(), hideParent = self.checkboxLocatorHideParent.Get(), subLocators = self.checkboxLocatorSubLocator.Get(), skipLastReverse = False)
	def CreateLocatorBakeAim(self, axis, *args): # TODO
		axisString = ""
		scale = self.floatLocatorSize.Get()
		distance = self.floatLocatorAimOffset.Get()

		if (axis == 1): axisString = "X-"
		elif (axis == 2): axisString = "X+"
		elif (axis == 3): axisString = "Y-"
		elif (axis == 4): axisString = "Y+"
		elif (axis == 5): axisString = "Z-"
		elif (axis == 6): axisString = "Z+"
		print(f"Axis = {axisString} | Distance = {distance}")

		Locators.CreateAim(scale = scale, hideParent = self.checkboxLocatorHideParent.Get(), subLocators = self.checkboxLocatorSubLocator.Get())


	# BAKER
	def BakeSelectedClassic(self, *args):
		Baker.BakeSelected(classic = True, preserveOutsideKeys = True)
	def BakeSelectedClassicCut(self, *args):
		Baker.BakeSelected(classic = True, preserveOutsideKeys = False)
	def BakeSelectedCustom(self, *args):
		Baker.BakeSelected(classic = False, preserveOutsideKeys = True)
	def BakeSelectedCustomCut(self, *args):
		Baker.BakeSelected(classic = False, preserveOutsideKeys = False)
	def BakeSelectedByLastObject(self, *args):
		Baker.BakeSelectedByLastObject()

