# GETOOLS is under the terms of the MIT License
# Copyright (c) 2018-2024 Eugene Gataulin (GenEugene). All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Author: Eugene Gataulin tek942@gmail.com https://www.linkedin.com/in/geneugene
# Source code: https://github.com/GenEugene/GETools or https://app.gumroad.com/geneugene

import maya.cmds as cmds

from ..utils import Animation
from ..utils import Baker
from ..utils import Constraints
from ..utils import Other
from ..utils import Parent
from ..utils import Selector
from ..utils import Text
from ..values import Enums

nameBase = "gLoc"
nameAim = "{0}Aim".format(nameBase)
scale = 1.0
minSelectedCount = 1

# SIZE
def GetSize(locator):
	shape = Other.GetShapeType(element = locator, type = Enums.Types.locator)
	if (shape != None):
		return (
			cmds.getAttr(shape + "." + Enums.Attributes.scaleLocal[0]),
			cmds.getAttr(shape + "." + Enums.Attributes.scaleLocal[1]),
			cmds.getAttr(shape + "." + Enums.Attributes.scaleLocal[2]),
			)
	else:
		return None
def SetSize(locator, valueX, valueY, valueZ):
	if (valueX == 0 or valueY == 0 or valueZ == 0):
		cmds.warning("Target locator scale is ZERO. The lLocator scaler may have problems.")
	shape = Other.GetShapeType(element = locator, type = Enums.Types.locator)
	if (shape != None):
		cmds.setAttr(shape + "." + Enums.Attributes.scaleLocal[0], valueX)
		cmds.setAttr(shape + "." + Enums.Attributes.scaleLocal[1], valueY)
		cmds.setAttr(shape + "." + Enums.Attributes.scaleLocal[2], valueZ)
		return True
	else:
		return False
def ScaleSize(locator, valueX, valueY, valueZ):
	size = GetSize(locator)
	sizeX = size[0] * valueX
	sizeY = size[1] * valueY
	sizeZ = size[2] * valueZ
	SetSize(locator, sizeX, sizeY, sizeZ)

def SelectedLocatorsSizeScale(value, *args):
	selectedList = Selector.MultipleObjects(1)
	if (selectedList == None):
		return None
	
	for item in selectedList:
		shape = Other.GetShapeType(element = item, type = Enums.Types.locator)
		if (shape != None):
			ScaleSize(item, value, value, value)
def SelectedLocatorsSizeSet(value, *args):
	selectedList = Selector.MultipleObjects(1)
	if (selectedList == None):
		return None
	
	for item in selectedList:
		shape = Other.GetShapeType(element = item, type = Enums.Types.locator)
		if (shape != None):
			SetSize(item, value, value, value)

# CREATE
def Create(name=nameBase, scale=scale, hideParent=False, subLocator=False):
	locatorCurrent = cmds.spaceLocator(name = Text.SetUniqueFromText(name))[0]
	SetSize(locatorCurrent, scale, scale, scale)
	cmds.select(locatorCurrent)

	if hideParent:
		shape = Other.GetShapeType(element = locatorCurrent, type = Enums.Types.locator)
		if (shape != None):
			cmds.setAttr(shape + "." + Enums.Attributes.visibility, 0)
	
	if subLocator:
		subLocator = Create(locatorCurrent + "Secondary")
		SetSize(subLocator, scale, scale, scale)
		cmds.parent(subLocator, locatorCurrent)
		cmds.select(subLocator)
		return locatorCurrent, subLocator
	else:
		return locatorCurrent
def CreateOnSelected(name=nameBase, scale=scale, minSelectedCount=minSelectedCount, hideParent=False, subLocator=False, constraint=False, bake=False, parentToLastSelected=False, constrainReverse=False, constrainTranslate=True, constrainRotate=True):
	# Check selected objects
	selectedList = Selector.MultipleObjects(minSelectedCount)
	if (selectedList == None):
		return None
	
	locatorsList = []
	sublocatorsList = []

	# Create locators on selected
	for item in selectedList:
		nameCurrent = Text.GetShortName(item, removeSpaces = True) + "_" + name
		created = Create(name = nameCurrent, scale = scale, hideParent = hideParent, subLocator = subLocator)
		if subLocator:
			locatorsList.append(created[0])
			sublocatorsList.append(created[1])
		else:
			locatorsList.append(created)
		cmds.matchTransform(locatorsList[-1], item, position = True, rotation = True, scale = True)

	# Constrain locators to selected objects
	if (constraint):
		for i in range(len(selectedList)):
			Constraints.ConstrainSecondToFirstObject(selectedList[i], locatorsList[i], maintainOffset = False)

	# Parent locators to last or to last sublocator
	if (bake):
		if (parentToLastSelected):
			if subLocator:
				locatorsListWithLastSub = locatorsList[:-1]
				locatorsListWithLastSub.append(sublocatorsList[-1])
				Parent.ListToLastObjects(locatorsListWithLastSub)
			else:
				Parent.ListToLastObjects(locatorsList)

		# Bake locators and delete constraints
		cmds.select(locatorsList)
		Baker.BakeSelected()
		Animation.DeleteStaticCurves()
		Constraints.DeleteConstraints(locatorsList)

	# Reverse constrain original objects to new locators
	if constrainReverse:
		for i in range(len(selectedList)):
			if subLocator:
				firstObject = sublocatorsList[i]
			else:
				firstObject = locatorsList[i]
			Constraints.ConstrainSecondToFirstObject(firstObject, selectedList[i], maintainOffset = False, parent = constrainTranslate and constrainRotate, point = constrainTranslate, orient = constrainRotate)

	# Select objects and return
	if subLocator:
		cmds.select(sublocatorsList)
		return selectedList, locatorsList, sublocatorsList
	else:
		cmds.select(locatorsList)
		return selectedList, locatorsList
def CreateAndBakeAsChildrenFromLastSelected(scale=scale, minSelectedCount=2, hideParent=False, subLocator=False, constraintReverse=False, skipLastReverse=True):
	# Check selected objects
	objects = CreateOnSelected(scale = scale, minSelectedCount = minSelectedCount, hideParent = hideParent, subLocator = subLocator, constraint = True, bake = True, parentToLastSelected = True)
	if (objects == None):
		return None
	
	# Constrain objects to locators
	if (constraintReverse):
		for i in range(len(objects[0])):
			if (skipLastReverse and i == len(objects[0]) - 1):
				break
			if subLocator:
				Constraints.ConstrainSecondToFirstObject(objects[2][i], objects[0][i], maintainOffset = False)
			else:
				Constraints.ConstrainSecondToFirstObject(objects[1][i], objects[0][i], maintainOffset = False)

	# Select objects and return
	if subLocator:
		cmds.select(objects[2][-1])
	else:
		cmds.select(objects[1][-1])
	return objects
def CreateOnSelectedAim(name=nameAim, scale=scale, minSelectedCount=minSelectedCount, hideParent=False, subLocator=False, rotateOnly=False, aimVector=(1,0,0), distance=100, reverse=True):
	# Check selected objects
	objects = CreateOnSelected(name = name, scale = scale, minSelectedCount = minSelectedCount, hideParent = hideParent, subLocator = subLocator)
	if (objects == None):
		return None
	
	# Create aim locators
	groupsList = []
	locatorsOffsetsList = []
	locatorsTargetsList = []
	for i in range(len(objects[0])):
		aimGroup = cmds.group(empty = True, name = objects[0][i] + "_AimGroup")
		locOffset = Create(name = objects[1][i] + "Offset", scale = scale)
		locTarget = Create(name = objects[1][i] + "Target", scale = scale)

		cmds.matchTransform(locOffset, objects[1][i], position = True, rotation = True, scale = True)
		cmds.matchTransform(locTarget, objects[1][i], position = True, rotation = True, scale = True)

		cmds.parent(objects[1][i], aimGroup)
		cmds.parent(locOffset, objects[1][i])
		cmds.parent(locTarget, aimGroup)

		if subLocator:
			cmds.matchTransform(objects[2][i], locOffset, position = True, rotation = True, scale = True)
			cmds.parent(objects[2][i], locOffset)
		
		aimVectorScaled = (
			aimVector[0] * distance,
			aimVector[1] * distance,
			aimVector[2] * distance,
			)
		cmds.move(aimVectorScaled[0], aimVectorScaled[1], aimVectorScaled[2], locTarget, relative = True, objectSpace = True, worldSpaceDistance = True)

		groupsList.append(aimGroup)
		locatorsOffsetsList.append(locOffset)
		locatorsTargetsList.append(locTarget)

		Constraints.ConstrainListToLastElement(selected = (objects[1][i], objects[0][i]), parent = False, point = True, orient = True)
		Constraints.ConstrainListToLastElement(selected = (locTarget, objects[0][i]))
		
	# Bake animation from original objects
	cmds.select(objects[1] + locatorsTargetsList, replace = True)
	Baker.BakeSelected()
	Constraints.DeleteConstraints(objects[1])
	Constraints.DeleteConstraints(locatorsTargetsList)
	Animation.DeleteStaticCurves()

	# Create aim constraint
	for i in range(len(objects[0])):
		if (aimVector[2] == 0):
			upVector = (0, 0, 1)
		else:
			upVector = (0, 1, 0)
		cmds.aimConstraint(locatorsTargetsList[i], locatorsOffsetsList[i], maintainOffset = True, weight = 1, aimVector = aimVector, upVector = upVector, worldUpType = "objectrotation", worldUpVector = upVector, worldUpObject = objects[1][i])
	
	# Reverse constrain # TODO move constraint to temp group
	if (reverse):
		for i in range(len(objects[0])):
			parentObject = None
			if subLocator:
				parentObject = objects[2][i]
			else:
				parentObject = locatorsOffsetsList[i]
			
			# Constraints
			if (rotateOnly):
				Constraints.ConstrainSecondToFirstObject(objects[0][i], objects[1][i], maintainOffset = False, parent = False, point = True, orient = False)
				Constraints.ConstrainSecondToFirstObject(parentObject, objects[0][i], maintainOffset = False, parent = False, point = False, orient = True)
			else:
				Constraints.ConstrainSecondToFirstObject(parentObject, objects[0][i], maintainOffset = False, parent = False, point = True, orient = True)

	# Select objects and return
	cmds.select(locatorsTargetsList)
	if subLocator:
		return objects[0], aimGroup, objects[1], locatorsOffsetsList, locatorsTargetsList, objects[2]
	else:
		return objects[0], aimGroup, objects[1], locatorsOffsetsList, locatorsTargetsList

