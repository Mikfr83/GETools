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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Author: Eugene Gataulin tek942@gmail.com https://www.linkedin.com/in/geneugene https://discord.gg/heMxJhTqCz
# Source code: https://github.com/GenEugene/GETools or https://app.gumroad.com/geneugene

import os
import datetime
import maya.cmds as cmds
from functools import partial

from .. import Settings
from ..utils import Animation
from ..utils import Attributes
from ..utils import Baker
from ..utils import Colors
from ..utils import Constraints
from ..utils import File
from ..utils import Layers
from ..utils import MayaSettings
from ..utils import Selector
from ..utils import Text
from ..utils import Timeline
from ..utils import UI
from ..values import Enums
from ..values import Icons
from ..experimental import Physics
from ..experimental import PhysicsParticle


class OverlappyAnnotations:
	### Setup
	setupEnding = "Tweak values to preview the simulation.\nTo bake the rig, deselect all and press any bake button."
	setupPoint = "Simple particle rig for translation.\n" + setupEnding
	setupAim = "Aim rig for rotation using 2 particles: 1 for aim target, 1 for aim up.\n" + setupEnding
	setupCombo = "Combined rig for translation and rotation using 3 particles: 1 for translation, 1 for aim target, and 1 for aim up.\n" + setupEnding
	setupDelete = "Delete particle rig if it exists"

	### Baking
	bakeTranslation = "Bake point rig for translation attributes"
	bakeRotation = "Bake aim rig for rotation attributes"
	bakeCombo = "Bake combo rig for translation and rotation attributes"
	bakeCurrent = "Bake current rig if exist"
	# bakeScale = "Bake simulation for scale attributes"

	### Layers
	layerDeleteAll = "All animation layers will be deleted."
	layerDeleteTemp = "Only the Temp layer and its child layers will be deleted."
	layerDeleteSafe = "Only the Safe layer and its child layers will be deleted."
	layerMoveTemp = "Move Temp layer sublayers to the Safe layer."
	layerMoveSafe = "Move Safe layer sublayers to the Temp layer."

	### Options
	# checkboxHierarchy = "Bake simulation for all child hierarhy of selected objects"
	# checkboxLayer = "Bake animation into override layers. \nIf turned off animation will be baked directly to selected objects"
	# checkboxLoop = "Use for cycles. \nImportant to have cycle constant animation curves"
	# checkboxClean = "Remove particle setup after baking end"

	### Collisions
	# checkboxCollisions = "Use collisions"

	### Nucleus
	particleTimeScale = "Nucleus Time Scale"

	### Aim Offset
	aimOffset = "Particle offset from original object.\nHighly important to use non zero values for \"Aim\" and \"Combo\" modes."
	aimOffsetValue = "Offset value"
	aimOffsetAxis = "Positive axis for offset"
	aimOffsetReverse = "Reverse axis direction from positive to negative"

	### Particle
	particleRadius = "Particle sphere size. Just visual, no physics influence."
	particleGoalSmooth = "This value is used to control the \"smoothness\" of the change in the goal forces as the weight changes from 0.0 to 1.0.\nThis is purely an aesthetic effect, with no scientific basis.\nThe higher the number, the smoother the change."
	particleGoalWeight = "Particle Goal Weight. Value 1 means 100% of stiffness."
	particleConserve = "The Conserve value controls how much of a particle object's velocity is retained from frame to frame.\nSpecifically, Conserve scales a particle's velocity attribute at the beginning of each frame's execution.\nAfter scaling the velocity, Maya applies any applicable dynamics to the particles to create the final positioning at the end of the frame."
	particleDrag = "Specifies the amount of drag applied to the current nParticle object.\nDrag is the component of aerodynamic force parallel to the relative wind which causes resistance.\nDrag is 0.05 by default."
	particleDamp = "Specifies the amount the motion of the current nParticles are damped.\nDamping progressively diminishes the movement and oscillation of nParticles by dissipating energy."

class OverlappySettings:
	### NAMING
	prefix = "ovlp"
	nameGroup = prefix + "Group"
	prefixLayer = "_" + prefix
	nameLayers = (prefixLayer + "TEMP_", prefixLayer + "SAFE_", prefixLayer + "_")
		
	### SETTINGS CHECKBOXES
	optionCheckboxHierarchy = False
	optionCheckboxLayer = True
	optionCheckboxLoop = False
	optionCheckboxDeleteSetup = True
	optionCheckboxCollisions = True
	optionRadioButtonsLoop = [False, False, True, False, False]

	### SETTINGS NUCLEUS
	nucleusTimeScale = 1
	nucleusGravityActivated = False
	nucleusGravityValue = 9.81
	nucleusGravityDirection = [0, -1, 0]

	### PARTICLE AIM OFFSET
	particleAimOffsetValue = 10
	particleAimOffsetUpValue = 10
	particleAimOffsetRadioButtons = [True, False, False] # X
	particleAimOffsetUpRadioButtons = [False, True, False] # Y
	particleAimOffsetReverse = False
	particleAimOffsetUpReverse = False

	### SETTINGS DYNAMIC PROPERTIES
	particleRadius = 1
	particleGoalSmooth = 1
	particleGoalWeight = 0.3
	particleConserve = 1
	particleDrag = 0.01
	particleDamp = 0
		
	### SLIDERS (field min/max, slider min/max)
	sliderWidth = (60, 54, 10)
	sliderWidthMarker = 14
	rangeNucleusTimeScale = (0.001, float("inf"), 0.001, 1)
	rangePRadius = (0, float("inf"), 0, 10)
	rangeGSmooth = (0, float("inf"), 0, 2)
	rangeGWeight = (0, 1, 0, 1)
	rangePConserve = (0, 1, 0, 1)
	rangePDrag = (0, float("inf"), 0, 1)
	rangePDamp = (0, float("inf"), 0, 1)

class OverlappyVariables: # using for sava and load settings
	flagHierarchy = "flagHierarchy"
	flagLayer = "flagLayer"
	flagLoop = "flagLoop"
	flagDeleteSetup = "flagDeleteSetup"
	flagCollisions = "flagCollisions"
	
	menuRadioButtonLoopCycles0 = "menuRadioButtonLoopCycles0"
	menuRadioButtonLoopCycles1 = "menuRadioButtonLoopCycles1"
	menuRadioButtonLoopCycles2 = "menuRadioButtonLoopCycles2"
	menuRadioButtonLoopCycles3 = "menuRadioButtonLoopCycles3"
	menuRadioButtonLoopCycles4 = "menuRadioButtonLoopCycles4"
	
	nucleusTimeScale = "nucleusTimeScale"
	nucleusGravityActivated = "nucleusGravityActivated"
	nucleusGravityValue = "nucleusGravityValue"
	nucleusGravityDirection = "nucleusGravityDirection"
	
	particleAimOffsetFloat = "particleAimOffsetFloat"
	particleAimOffsetRadioCollection1 = "particleAimOffsetRadioCollection1"
	particleAimOffsetRadioCollection2 = "particleAimOffsetRadioCollection2"
	particleAimOffsetRadioCollection3 = "particleAimOffsetRadioCollection3"
	particleAimOffsetReverse = "particleAimOffsetReverse"
	
	particleAimOffsetUpFloat = "particleAimOffsetUpFloat"
	particleAimOffsetUpRadioCollection1 = "particleAimOffsetUpRadioCollection1"
	particleAimOffsetUpRadioCollection2 = "particleAimOffsetUpRadioCollection2"
	particleAimOffsetUpRadioCollection3 = "particleAimOffsetUpRadioCollection3"
	particleAimOffsetUpReverse = "particleAimOffsetUpReverse"
	
	particleRadius = "particleRadius"
	particleGoalSmooth = "particleGoalSmooth"
	particleGoalWeight = "particleGoalWeight"
	particleConserve = "particleConserve"
	particleDrag = "particleDrag"
	particleDamp = "particleDamp"

class Overlappy:
	_version = "v3.6"
	_name = "OVERLAPPY"
	_title = _name + " " + _version

	def __init__(self, options):
		self.optionsPlugin = options
		### Check Maya version to avoid cycle import, Maya 2020 and older can't use cycle import
		if cmds.about(version = True) in ["2022", "2023", "2024", "2025"]:
			from ..modules import Options
			if isinstance(options, Options.PluginVariables):
				self.optionsPlugin = options

		self.directoryPresets = self.optionsPlugin.directory + Settings.pathPresets # TODO temporary solution, need to unify this logic for other modules and simply reuse

		### VALUES
		self.setupCreated = False
		self.setupCreatedPoint = False
		self.setupCreatedAim = False
		self.setupCreatedCombo = False

		self.time = Timeline.TimeRangeHandler()
		
		### OBJECTS
		self.selectedObjects = None
		self.selectedObjectsFiltered = ""
		self.selectedObjectsStartPosition = [0, 0, 0]

		self.layers = [OverlappySettings.nameLayers[0], OverlappySettings.nameLayers[1]]
		self.nucleus1 = ""
		self.nucleus2 = ""
		self.bakingObject = ""
		## self.colliderObjects = [] # TODO
		## self.colliderNodes = [] # TODO

		### PARTICLE SIMULATION OBJECTS
		self.particleAimOffsetTarget = [0, 0, 0]
		self.particleAimOffsetUp = [0, 0, 0]
		self.particleBase = ""
		self.particleTarget = ""
		self.particleUp = ""
		self.particleLocator = ""
		self.particleLocatorGoalOffset = ""
		self.particleLocatorGoalOffsetUp = ""
		self.particleLocatorAim = ""
		self.particleLocatorGoalOffsetStartPosition = [0, 0, 0]
		self.particleLocatorGoalOffsetUpStartPosition = [0, 0, 0]

		### UI LAYOUTS
		# self.layoutLayers = None
		# self.layoutCollisions = None # TODO
		# self.layoutChainMode = None # TODO
		# self.layoutChainButtons = None # TODO
		# self.layoutChainDynamicProperties = None # TODO
		# self.layoutNucleusProperties = None
		self.layoutFrame = None
		# self.layoutParticleButtons = None
		# self.layoutParticleOffset = None
		# self.layoutParticleDynamicProperties = None
		
		### UI MENU OPTIONS
		self.menuCheckboxHierarchy = None
		self.menuCheckboxLayer = None
		self.menuCheckboxLoop = None
		self.menuCheckboxDeleteSetup = None
		# self.menuCheckboxCollisions = None # TODO
		self.menuRadioButtonsLoop = [None, None, None, None, None]

		### UI NUCLEUS PROPERTIES
		self.nucleusTimeScaleSlider = None
		self.nucleusGravityCheckbox = None
		self.nucleusGravityFloatField = None
		self.nucleusGravityDirectionFloatFieldGrp = None

		### UI AIM OFFSET
		## self.checkboxAutoOffset = None # TODO
		self.aimOffsetFloatGroup = [None, None] # text, float
		self.aimOffsetRadioCollection = [None, None, None]
		self.aimOffsetCheckbox = None
		self.aimOffsetUpFloatGroup = [None, None] # text, float
		self.aimOffsetUpRadioCollection = [None, None, None]
		self.aimOffsetUpCheckbox = None
		
		### UI PARTICLE DYNAMIC PROPERTIES
		self.sliderParticleRadius = None
		self.sliderParticleGoalSmooth = None
		self.sliderParticleGoalWeight = None
		self.sliderParticleConserve = None
		self.sliderParticleDrag = None
		self.sliderParticleDamp = None

		### UI SCROLL LISTS
		self.scrollListColliders = None
	
	def UICreate(self, layoutMain):
		self.UILayoutMenuBar(layoutMain)
		self.UILayoutLayers(layoutMain)
		self.UILayoutNucleus(layoutMain)
		## self.UILayoutChainMode(layoutMain) # TODO
		self.UILayoutParticle(layoutMain)
		## self.UILayoutCollisions(layoutMain) # TODO
		cmds.separator(parent = layoutMain, height = Settings.separatorHeight, style = "none")
		self.InitPresetOnStart()

	### MAIN UI
	def UILayoutMenuBar(self, layoutMain):
		cmds.menuBarLayout(parent = layoutMain)

		cmds.menu(label = "Edit", tearOff = True)
		cmds.menuItem(label = "Save Preset", command = self.SavePresetWindow, image = Icons.save)
		cmds.menuItem(label = "Save Default Preset", command = self.SavePresetDefault, image = Icons.save)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "Load Preset", command = self.LoadPresetWindow, image = Icons.load)
		cmds.menuItem(label = "Load Default Preset", command = self.LoadPresetDefault, image = Icons.load)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "Load Built-in Preset", command = self.LoadPresetBuiltin, image = Icons.rotateClockwise)
		
		cmds.menu(label = "Options", tearOff = True)
		self.menuCheckboxHierarchy = UI.MenuCheckbox(label = "Use Hierarchy")
		self.menuCheckboxLayer = UI.MenuCheckbox(label = "Bake To Override Layer")
		self.menuCheckboxDeleteSetup = UI.MenuCheckbox(label = "Delete Setup After Bake")
		# self.menuCheckboxCollisions = UI.MenuCheckbox(label = "Collisions")

		cmds.menuItem(dividerLabel = "Pre Loop Cycles", divider = True)
		self.menuCheckboxLoop = UI.MenuCheckbox(label = "Loop")
		cmds.radioMenuItemCollection()
		self.menuRadioButtonsLoop[0] = cmds.menuItem(label = "0", radioButton = True)
		self.menuRadioButtonsLoop[1] = cmds.menuItem(label = "1", radioButton = True)
		self.menuRadioButtonsLoop[2] = cmds.menuItem(label = "2", radioButton = True)
		self.menuRadioButtonsLoop[3] = cmds.menuItem(label = "3", radioButton = True)
		self.menuRadioButtonsLoop[4] = cmds.menuItem(label = "4", radioButton = True)

		cmds.menu(label = "Utils", tearOff = True)
		cmds.menuItem(label = "Select Nucleus", command = self.SelectNucleus, image = Icons.nucleus)
		cmds.menuItem(label = "Select Particles", command = self.SelectParticles, image = Icons.particle)

	def UILayoutLayers(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "LAYERS", collapsable = True, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)

		cmds.rowLayout(parent = layoutColumn, adjustableColumn = 1, numberOfColumns = 3, columnWidth3 = (120, 75, 75), columnAlign = [(1, "center"), (2, "center"), (3, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0)]) # recomputeSize = True
		cmds.button(label = "Delete All Layers", command = partial(Layers.Delete, "BaseAnimation"), backgroundColor = Colors.red50, annotation = OverlappyAnnotations.layerDeleteAll)
		cmds.button(label = "Delete Temp", command = partial(Layers.Delete, OverlappySettings.nameLayers[0]), backgroundColor = Colors.red10, annotation = OverlappyAnnotations.layerDeleteTemp)
		cmds.button(label = "Delete Safe", command = partial(Layers.Delete, OverlappySettings.nameLayers[1]), backgroundColor = Colors.red10, annotation = OverlappyAnnotations.layerDeleteSafe)

		cmds.rowLayout(parent = layoutColumn, adjustableColumn = 1, numberOfColumns = 2, columnWidth2 = (135, 135), columnAlign = [(1, "center"), (2, "center"), (3, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0)])
		cmds.button(label = "Move To Safe Layer", command = partial(self.LayerMoveToSafeOrTemp, True), backgroundColor = Colors.blue10, annotation = OverlappyAnnotations.layerMoveTemp)
		cmds.button(label = "Move To Temp Layer", command = partial(self.LayerMoveToSafeOrTemp, False), backgroundColor = Colors.blue10, annotation = OverlappyAnnotations.layerMoveSafe)
	# def UILayoutCollisions(self, layoutMain): # TODO
	# 	self.layoutCollisions = cmds.frameLayout("layoutCollisions", label = Settings.frames2Prefix + "COLLISIONS - WORK IN PROGRESS", parent = layoutMain, collapsable = True, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
	# 	layoutColumn = cmds.columnLayout(parent = self.layoutCollisions, adjustableColumn = True)
		
	# 	count = 4
	# 	cmds.gridLayout(parent = layoutColumn, numberOfColumns = count, cellWidth = Settings.windowWidthMargin / count, cellHeight = Settings.lineHeight)
	# 	cmds.button(label = "Add", backgroundColor = Colors.green10)
	# 	cmds.button(label = "Remove", backgroundColor = Colors.red10)
	# 	cmds.button(label = "Refresh", backgroundColor = Colors.yellow10)
	# 	cmds.button(label = "Clear", backgroundColor = Colors.red50)

	# 	# TODO Scroll list with colliders
	# 	## https://help.autodesk.com/cloudhelp/2023/ENU/Maya-Tech-Docs/CommandsPython/textScrollList.html
	# 	layoutScroll = cmds.frameLayout("layoutScroll", label = "Colliders List", labelIndent = 80, parent = self.layoutCollisions, collapsable = False, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
	# 	self.scrollListColliders = cmds.textScrollList(parent = layoutScroll, allowMultiSelection = True, height = 120)

	# 	for i in range(20): # test list items
	# 		cmds.textScrollList(self.scrollListColliders, edit = True, append = "item {0}".format(i)) # append, selectItem, deselectAll, removeAll, doubleClickCommand
	def UILayoutNucleus(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "NUCLEUS PROPERTIES", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)

		### Time Scale
		self.nucleusTimeScaleSlider = UI.Slider(
			parent = layoutColumn,
			widthWindow = Settings.windowWidthMargin,
			widthMarker = OverlappySettings.sliderWidthMarker,
			columnWidth3 = OverlappySettings.sliderWidth,
			command = self.UpdateParticleSettings,
			label = "Time Scale",
			annotation = OverlappyAnnotations.particleTimeScale,
			value = OverlappySettings.nucleusTimeScale,
			minMax = OverlappySettings.rangeNucleusTimeScale,
			menuReset = True,
		)

		### Gravity
		layoutRow = cmds.rowLayout(parent = layoutColumn, adjustableColumn = 2, numberOfColumns = 3, columnWidth3 = (55, 40, 100))
		self.nucleusGravityCheckbox = cmds.checkBox(parent = layoutRow, label = "Gravity", changeCommand = self.UpdateParticleSettings, value = OverlappySettings.nucleusGravityActivated)
		self.nucleusGravityFloatField = cmds.floatField(parent = layoutRow, changeCommand = self.UpdateParticleSettings, value = OverlappySettings.nucleusGravityValue, precision = 2)
		self.nucleusGravityDirectionFloatFieldGrp = cmds.floatFieldGrp(parent = layoutRow, changeCommand = self.UpdateParticleSettings, numberOfFields = 3, columnWidth4 = [48, 40, 40, 40], label = "Direction", value = (OverlappySettings.nucleusGravityDirection[0], OverlappySettings.nucleusGravityDirection[1], OverlappySettings.nucleusGravityDirection[2], 0))
		self.nucleusGravityDirectionFloatFieldGrp = self.nucleusGravityDirectionFloatFieldGrp.replace(Settings.windowName + "|", "") # HACK fix for docked window only. Don't know how to avoid issue


	### CHAIN UI
	# def UILayoutChainMode(self, layoutMain): # TODO
		# self.layoutChainMode = cmds.frameLayout("layoutChainMode", label = Settings.frames2Prefix + "CHAIN MODE - WORK IN PROGRESS", parent = layoutMain, collapsable = True, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
		
		# cmds.menuBarLayout()
		# cmds.menu(label = "Edit")
		# cmds.menuItem(label = "Reset Settings", command = self._ResetAllChainValues, image = Icons.rotateClockwise)
				
		## self.UILayoutChainButtons(self.layoutChainMode)
		# self.UILayoutChainDynamicProperties(self.layoutChainMode)
		# pass
	# def UILayoutChainButtons(self, layoutMain): # TODO
		## SETUP
		# self.layoutChainButtons = cmds.frameLayout("layoutChainButtons", label = "Buttons", labelIndent = 100, parent = layoutMain, collapsable = False, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
		# layoutColumn = cmds.columnLayout(parent = self.layoutChainButtons, adjustableColumn = True)

		## count = 2
		## cmds.gridLayout(parent = layoutColumn, numberOfColumns = count, cellWidth = Settings.windowWidthMargin / count, cellHeight = Settings.lineHeight)
		##
		## cmds.button(label = "Create", command = PhysicsHair.CreateNHairOnSelected, backgroundColor = Colors.green10)
		## cmds.button(label = "Remove", command = self._SetupDelete, backgroundColor = Colors.red10, annotation = OverlappyAnnotations.setupDelete)
		# pass
	# def UILayoutChainDynamicProperties(self, layoutMain): # TODO
		# self.layoutChainDynamicProperties = cmds.frameLayout("layoutChainDynamicProperties", label = "Dynamic Properties", labelIndent = 70, parent = layoutMain, collapsable = False, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
	

	### PARTICLE UI
	def UILayoutParticle(self, layoutMain):
		self.layoutFrame = cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "PARTICLE SIMULATION", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		self.UILayoutParticleSetup(self.layoutFrame)
		self.UILayoutParticleAimOffset(self.layoutFrame)
		self.UILayoutParticleDynamicProperties(self.layoutFrame)
	def UILayoutParticleSetup(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = "Setup And Bake", labelIndent = 87, collapsable = False, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		count = 4
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = count, cellWidth = Settings.windowWidthMargin / count, cellHeight = Settings.lineHeight)
		cmds.button(label = "Point", command = partial(self.ParticleSetupLogic, 1), backgroundColor = Colors.green10, annotation = OverlappyAnnotations.setupPoint)
		cmds.button(label = "Aim", command = partial(self.ParticleSetupLogic, 2), backgroundColor = Colors.green10, annotation = OverlappyAnnotations.setupAim)
		cmds.button(label = "Combo", command = partial(self.ParticleSetupLogic, 3), backgroundColor = Colors.green10, annotation = OverlappyAnnotations.setupCombo)
		cmds.button(label = "Remove", command = partial(self.ParticleSetupDelete, False, True), backgroundColor = Colors.red10, annotation = OverlappyAnnotations.setupDelete)

		count = 4
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = count, cellWidth = Settings.windowWidthMargin / count, cellHeight = Settings.lineHeight)
		cmds.button(label = "Bake Point", command = partial(self.BakeParticleVariants, 1), backgroundColor = Colors.orange10, annotation = OverlappyAnnotations.bakeTranslation)
		cmds.button(label = "Bake Aim", command = partial(self.BakeParticleVariants, 2), backgroundColor = Colors.orange10, annotation = OverlappyAnnotations.bakeRotation)
		cmds.button(label = "Bake Combo", command = partial(self.BakeParticleVariants, 3), backgroundColor = Colors.orange10, annotation = OverlappyAnnotations.bakeCombo)
		cmds.button(label = "Bake Current", command = partial(self.BakeParticleVariants, 0), backgroundColor = Colors.orange50, annotation = OverlappyAnnotations.bakeCurrent)
	def UILayoutParticleAimOffset(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = "Aim Offset", labelIndent = 100, collapsable = False, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		def CustomRadioButtonGroup(label="label", value=0):
			layout = cmds.rowLayout(parent = layoutColumn, adjustableColumn = 2, numberOfColumns = 6, columnWidth6 = (40, 40, 28, 28, 28, 60), columnAlign = [1, "center"], columnAttach = [(1, "both", 0)])
			text = cmds.text(label = label, annotation = OverlappyAnnotations.aimOffset)
			floatField = cmds.floatField(value = value, changeCommand = self.UpdateParticleAimOffsetSettings, precision = 1, minValue = 0, annotation = OverlappyAnnotations.aimOffsetValue)
			cmds.radioCollection()
			radioButton1 = cmds.radioButton(label = "X", onCommand = self.UpdateParticleAimOffsetSettings, annotation = OverlappyAnnotations.aimOffsetAxis)
			radioButton2 = cmds.radioButton(label = "Y", onCommand = self.UpdateParticleAimOffsetSettings, annotation = OverlappyAnnotations.aimOffsetAxis)
			radioButton3 = cmds.radioButton(label = "Z", onCommand = self.UpdateParticleAimOffsetSettings, annotation = OverlappyAnnotations.aimOffsetAxis)
			checkbox = cmds.checkBox(label = "Reverse", value = False, changeCommand = self.UpdateParticleAimOffsetSettings, annotation = OverlappyAnnotations.aimOffsetReverse)
			return layout, text, floatField, radioButton1, radioButton2, radioButton3, checkbox
		
		radioGroup1 = CustomRadioButtonGroup(label = "Aim", value = OverlappySettings.particleAimOffsetValue)
		self.aimOffsetFloatGroup[0] = radioGroup1[1]
		self.aimOffsetFloatGroup[1] = radioGroup1[2]
		self.aimOffsetRadioCollection[0] = radioGroup1[3]
		self.aimOffsetRadioCollection[1] = radioGroup1[4]
		self.aimOffsetRadioCollection[2] = radioGroup1[5]
		self.aimOffsetCheckbox = radioGroup1[6]

		radioGroup2 = CustomRadioButtonGroup(label = "Up", value = OverlappySettings.particleAimOffsetUpValue)
		self.aimOffsetUpFloatGroup[0] = radioGroup2[1]
		self.aimOffsetUpFloatGroup[1] = radioGroup2[2]
		self.aimOffsetUpRadioCollection[0] = radioGroup2[3]
		self.aimOffsetUpRadioCollection[1] = radioGroup2[4]
		self.aimOffsetUpRadioCollection[2] = radioGroup2[5]
		self.aimOffsetUpCheckbox = radioGroup2[6]
	def UILayoutParticleDynamicProperties(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = "Dynamic Properties", labelIndent = 80, collapsable = False, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)

		self.sliderParticleRadius = UI.Slider(
			parent = layoutColumn,
			widthWindow = Settings.windowWidthMargin,
			widthMarker = OverlappySettings.sliderWidthMarker,
			columnWidth3 = OverlappySettings.sliderWidth,
			command = self.UpdateParticleSettings,
			label = "Radius",
			annotation = OverlappyAnnotations.particleRadius,
			value = OverlappySettings.particleRadius,
			minMax = OverlappySettings.rangePRadius,
			menuReset = True,
		)

		cmds.separator(parent = layoutColumn, style = "in")
		
		self.sliderParticleGoalSmooth = UI.Slider(
			parent = layoutColumn,
			widthWindow = Settings.windowWidthMargin,
			widthMarker = OverlappySettings.sliderWidthMarker,
			columnWidth3 = OverlappySettings.sliderWidth,
			command = self.UpdateParticleSettings,
			label = "G.Smooth",
			annotation = OverlappyAnnotations.particleGoalSmooth,
			value = OverlappySettings.particleGoalSmooth,
			minMax = OverlappySettings.rangeGSmooth,
			menuReset = True,
		)
		
		self.sliderParticleGoalWeight = UI.Slider(
			parent = layoutColumn,
			widthWindow = Settings.windowWidthMargin,
			widthMarker = OverlappySettings.sliderWidthMarker,
			columnWidth3 = OverlappySettings.sliderWidth,
			command = self.UpdateParticleSettings,
			label = "G.Weight",
			annotation = OverlappyAnnotations.particleGoalWeight,
			value = OverlappySettings.particleGoalWeight,
			minMax = OverlappySettings.rangeGWeight,
			menuReset = True,
		)
		
		cmds.separator(parent = layoutColumn, style = "in")

		self.sliderParticleConserve = UI.Slider(
			parent = layoutColumn,
			widthWindow = Settings.windowWidthMargin,
			widthMarker = OverlappySettings.sliderWidthMarker,
			columnWidth3 = OverlappySettings.sliderWidth,
			command = self.UpdateParticleSettings,
			label = "Conserve",
			annotation = OverlappyAnnotations.particleConserve,
			value = OverlappySettings.particleConserve,
			minMax = OverlappySettings.rangePConserve,
			menuReset = True,
		)
		
		self.sliderParticleDrag = UI.Slider(
			parent = layoutColumn,
			widthWindow = Settings.windowWidthMargin,
			widthMarker = OverlappySettings.sliderWidthMarker,
			columnWidth3 = OverlappySettings.sliderWidth,
			command = self.UpdateParticleSettings,
			label = "Drag",
			annotation = OverlappyAnnotations.particleDrag,
			value = OverlappySettings.particleDrag,
			minMax = OverlappySettings.rangePDrag,
			menuReset = True,
		)
		
		self.sliderParticleDamp = UI.Slider(
			parent = layoutColumn,
			widthWindow = Settings.windowWidthMargin,
			widthMarker = OverlappySettings.sliderWidthMarker,
			columnWidth3 = OverlappySettings.sliderWidth,
			command = self.UpdateParticleSettings,
			label = "Damp",
			annotation = OverlappyAnnotations.particleDamp,
			value = OverlappySettings.particleDamp,
			minMax = OverlappySettings.rangePDamp,
			menuReset = True,
		)


	### PARTICLE LOGIC
	def CompileParticleAimOffset(self):
		### Get aim offset values from UI
		valueAimFloat = cmds.floatField(self.aimOffsetFloatGroup[1], query = True, value = True)
		valueAimAxisX = cmds.radioButton(self.aimOffsetRadioCollection[0], query = True, select = True)
		valueAimAxisY = cmds.radioButton(self.aimOffsetRadioCollection[1], query = True, select = True)
		valueAimAxisZ = cmds.radioButton(self.aimOffsetRadioCollection[2], query = True, select = True)
		valueAimCheckbox = cmds.checkBox(self.aimOffsetCheckbox, query = True, value = True)
		
		valueAimUpFloat = cmds.floatField(self.aimOffsetUpFloatGroup[1], query = True, value = True)
		valueAimUpAxisX = cmds.radioButton(self.aimOffsetUpRadioCollection[0], query = True, select = True)
		valueAimUpAxisY = cmds.radioButton(self.aimOffsetUpRadioCollection[1], query = True, select = True)
		valueAimUpAxisZ = cmds.radioButton(self.aimOffsetUpRadioCollection[2], query = True, select = True)
		valueAimUpCheckbox = cmds.checkBox(self.aimOffsetUpCheckbox, query = True, value = True)

		### Compile aim target value
		self.particleAimOffsetTarget = [0, 0, 0]
		valueAimTarget = valueAimFloat * (-1 if valueAimCheckbox else 1)
		if (valueAimAxisX):
			self.particleAimOffsetTarget = [valueAimTarget, 0, 0]
		if (valueAimAxisY):
			self.particleAimOffsetTarget = [0, valueAimTarget, 0]
		if (valueAimAxisZ):
			self.particleAimOffsetTarget = [0, 0, valueAimTarget]
		
		### Compile aim up value
		self.particleAimOffsetUp = [0, 0, 0]
		valueAimUp = valueAimUpFloat * (-1 if valueAimUpCheckbox else 1)
		if (valueAimUpAxisX):
			self.particleAimOffsetUp = [valueAimUp, 0, 0]
		if (valueAimUpAxisY):
			self.particleAimOffsetUp = [0, valueAimUp, 0]
		if (valueAimUpAxisZ):
			self.particleAimOffsetUp = [0, 0, valueAimUp]
	def ParticleSetupInit(self, *args):
		### Get selected objects
		self.selectedObjectsFiltered = Selector.MultipleObjects(minimalCount = 1)
		if self.selectedObjectsFiltered is None:
			return False
		
		### Remove previous setup if exists
		self.ParticleSetupDelete(clearCache = True)
		
		### Get min/max anim range time and reset time slider
		self.time.Scan()
		self.time.SetCurrent(self.time.values[2])
		
		### Get first selected object
		self.selectedObjectsFiltered = self.selectedObjectsFiltered[0] # HACK is it ok to limit only by first element?

		### Create group
		cmds.select(clear = True)
		if (cmds.objExists(OverlappySettings.nameGroup)):
			cmds.delete(OverlappySettings.nameGroup)
		cmds.group(empty = True, name = OverlappySettings.nameGroup)

		### Create nucleus node
		self.nucleus1 = Physics.CreateNucleus(name = OverlappySettings.prefix + PhysicsParticle._defaultNameNucleus + "_01", parent = OverlappySettings.nameGroup)
		cmds.select(clear = True)

		# TODO Need to define colliderObject before this logic
		### TODO Connect collision nRigid nodes to nucleus
		# self.colliderNodes[0] = cmds.createNode("nRigid", name = "myNRigid")
		# cmds.connectAttr("time1.outTime", self.colliderNodes[0] + ".currentTime")
		# cmds.connectAttr(self.colliderObjects[0] + ".worldMesh[0]", self.colliderNodes[0] + ".inputMesh")
		# cmds.connectAttr(self.colliderNodes[0] + ".currentState", self.nucleus1 + ".inputPassive[0]")
		# cmds.connectAttr(self.colliderNodes[0] + ".startState", self.nucleus1 + ".inputPassiveStart[0]")
		# cmds.connectAttr(self.nucleus1 + ".startFrame", self.colliderNodes[0] + ".startFrame")
		return True
	def ParticleSetupLogic(self, mode=0, *args): # modes: [1 - Point], [2 - Aim], [3 - Combo]
		isInitDone = self.ParticleSetupInit()
		if (not isInitDone):
			return
		
		### Create particle base setup
		if mode in [1, 3]: # Point or Combo
			particleSetupBase = PhysicsParticle.CreateParticleSetup(targetObject = self.selectedObjectsFiltered, nucleusNode = self.nucleus1, parentGroup = OverlappySettings.nameGroup)
			self.particleBase = particleSetupBase[4]
			self.particleLocator = particleSetupBase[6]
			self.bakingObject = self.particleLocator
			
		if mode in [2, 3]: # Aim or Combo
			self.CompileParticleAimOffset()
			targetObject = self.selectedObjectsFiltered
			nucleusAim = self.nucleus1
			if (mode == 3): # Combo
				### Create second nucleus node
				self.nucleus2 = Physics.CreateNucleus(name = OverlappySettings.prefix + PhysicsParticle._defaultNameNucleus + "_02", parent = OverlappySettings.nameGroup)
				cmds.select(clear = True)
				targetObject = particleSetupBase[6]
				nucleusAim = self.nucleus2
			
			### Create particle aim setup
			particleSetupOffset = PhysicsParticle.CreateParticleSetup(targetObject = targetObject, nucleusNode = nucleusAim, parentGroup = OverlappySettings.nameGroup, positionOffset = self.particleAimOffsetTarget)
			particleAimSetup = PhysicsParticle.CreateAimSetup(particleSetupOffset, positionOffset = self.particleAimOffsetUp)
			
			### Cache setup elements names
			self.particleTarget = particleSetupOffset[4]
			self.particleUp = particleAimSetup[1][4]
			self.particleLocator = particleSetupOffset[6]
			### Cache target position
			self.particleLocatorGoalOffset = particleSetupOffset[7]
			self.particleLocatorGoalOffsetStartPosition = cmds.xform(self.particleLocatorGoalOffset, query = True, translation = True, worldSpace = True)
			### Cache up position
			self.particleLocatorGoalOffsetUp = particleAimSetup[1][7]
			self.particleLocatorGoalOffsetUpStartPosition = cmds.xform(self.particleLocatorGoalOffsetUp, query = True, translation = True, worldSpace = True)
			### Cache other
			self.particleLocatorAim = particleAimSetup[0]
			self.bakingObject = self.particleLocatorAim
		
		### Set flags
		self.setupCreated = True
		self.setupCreatedPoint = mode == 1
		self.setupCreatedAim = mode == 2
		self.setupCreatedCombo = mode == 3

		### End
		self.UpdateParticleSettings()
		cmds.select(self.selectedObjectsFiltered, replace = True)
	def ParticleSetupDelete(self, deselect=False, clearCache=True, *args):
		### Deselect objects
		if (deselect):
			cmds.select(clear = True)
		
		### Delete group
		if (cmds.objExists(OverlappySettings.nameGroup)):
			cmds.delete(OverlappySettings.nameGroup)
		
		### Reset flags
		if (clearCache):
			self.setupCreated = False
			self.setupCreatedPoint = False
			self.setupCreatedAim = False
			self.setupCreatedCombo = False


	### SELECT
	def SelectNucleus(self, *args):		
		if (cmds.objExists(self.nucleus1)):
			cmds.select(self.nucleus1, replace = True)
		if (cmds.objExists(self.nucleus2)):
			cmds.select(self.nucleus2, add = True)
	def SelectParticles(self, *args):
		if (cmds.objExists(self.particleBase)):
			cmds.select(self.particleBase, replace = True)
		if (cmds.objExists(self.particleTarget)):
			cmds.select(self.particleTarget, add = True)
		if (cmds.objExists(self.particleUp)):
			cmds.select(self.particleUp, add = True)
	

	### SETTINGS
	def RefreshParticlePosition(self, *args): # TODO rework particle offset logic and add refresh method
		currentPosition = cmds.xform(self.selectedObjects[0], query = True, translation = True, worldSpace = True)
		offset = [currentPosition[0] - self.selectedObjectsStartPosition[0], currentPosition[1] - self.selectedObjectsStartPosition[1], currentPosition[2] - self.selectedObjectsStartPosition[2]]

		if (cmds.objExists(self.particleBase)):
			cmds.xform(self.particleBase, translation = offset, worldSpace = True)
		
		if (cmds.objExists(self.particleTarget)):
			cmds.xform(self.particleTarget, translation = offset, worldSpace = True)
		
		if (cmds.objExists(self.particleUp)):
			cmds.xform(self.particleUp, translation = offset, worldSpace = True)

	def UpdateParticleAllSettings(self, *args):
		self.UpdateParticleAimOffsetSettings()
		self.UpdateParticleSettings()
	def UpdateParticleAimOffsetSettings(self, *args):
		if (not self.setupCreated or self.setupCreatedPoint):
			return

		def SetParticleAimOffset(nameLocator, nameParticle, goalStartPosition, offset=(0, 0, 0)):
			if (cmds.objExists(nameLocator)):
				cmds.setAttr(nameLocator + ".translateX", offset[0])
				cmds.setAttr(nameLocator + ".translateY", offset[1])
				cmds.setAttr(nameLocator + ".translateZ", offset[2])
			
			if (cmds.objExists(nameParticle)):
				goalPosition = cmds.xform(nameLocator, query = True, translation = True, worldSpace = True)
				cmds.setAttr(nameParticle + ".translateX", goalPosition[0] - goalStartPosition[0])
				cmds.setAttr(nameParticle + ".translateY", goalPosition[1] - goalStartPosition[1])
				cmds.setAttr(nameParticle + ".translateZ", goalPosition[2] - goalStartPosition[2])
		
		self.CompileParticleAimOffset()
		
		self.time.SetCurrent(self.time.values[2])

		SetParticleAimOffset(nameLocator = self.particleLocatorGoalOffset, nameParticle = self.particleTarget, goalStartPosition = self.particleLocatorGoalOffsetStartPosition, offset = self.particleAimOffsetTarget)
		SetParticleAimOffset(nameLocator = self.particleLocatorGoalOffsetUp, nameParticle = self.particleUp, goalStartPosition = self.particleLocatorGoalOffsetUpStartPosition, offset = self.particleAimOffsetUp)
	def UpdateParticleSettings(self, *args):
		### Nucleus
		def SetNucleusAttributes(name):
			if (cmds.objExists(name)):
				cmds.setAttr(name + ".timeScale", self.nucleusTimeScaleSlider.Get())
				cmds.setAttr(name + ".gravity", cmds.floatField(self.nucleusGravityFloatField, query = True, value = True))
				direction = cmds.floatFieldGrp(self.nucleusGravityDirectionFloatFieldGrp, query = True, value = True)
				cmds.setAttr(name + ".gravityDirectionX", direction[0])
				cmds.setAttr(name + ".gravityDirectionY", direction[1])
				cmds.setAttr(name + ".gravityDirectionZ", direction[2])
		SetNucleusAttributes(self.nucleus1)
		SetNucleusAttributes(self.nucleus2)

		### Particles
		def SetParticleDynamicAttributes(name):
			if (cmds.objExists(name)):
				useGravity = not cmds.checkBox(self.nucleusGravityCheckbox, query = True, value = True)
				cmds.setAttr(name + "Shape.ignoreSolverGravity", useGravity)
				cmds.setAttr(name + "Shape.radius", self.sliderParticleRadius.Get())
				cmds.setAttr(name + "Shape.goalSmoothness", self.sliderParticleGoalSmooth.Get())
				cmds.setAttr(name + "Shape.goalWeight[0]", self.sliderParticleGoalWeight.Get())
				cmds.setAttr(name + "Shape.conserve", self.sliderParticleConserve.Get())
				cmds.setAttr(name + "Shape.drag", self.sliderParticleDrag.Get())
				cmds.setAttr(name + "Shape.damp", self.sliderParticleDamp.Get())
		SetParticleDynamicAttributes(name = self.particleBase)
		SetParticleDynamicAttributes(name = self.particleTarget)
		SetParticleDynamicAttributes(name = self.particleUp)
	
	### PRESET
	def InitPresetOnStart(self, *args):
		filepath = self.directoryPresets + Settings.overlappyDefaultPreset
		data = File.ReadLogic(filepath)
		if data is None:
			self.LoadPresetBuiltin()
		else:
			self.LoadPresetDefault()

	def LoadPresetBuiltin(self, *args):
		dictionary = self.GetBuiltinPresetDictionary()
		self.ApplyPresetDictionary(dictionary)
		print("Overlappy Preset loaded from Built-in data")
	def SavePresetDefault(self, *args):
		data = self.SavePresetGetDictionaryAndTitle()
		filepath = self.directoryPresets + Settings.overlappyDefaultPreset
		variablesDictionary = data[0]
		title = data[1]
		File.SaveLogic(filepath, variablesDictionary, title)
		self.RefreshSlidersDefault()
		print("Overlappy Default Preset saved to \"{0}\"".format(filepath))
	def LoadPresetDefault(self, *args):
		filepath = self.directoryPresets + Settings.overlappyDefaultPreset
		data = File.ReadLogic(filepath)
		if data is None:
			cmds.warning("Overlappy Default Preset doesn't exist: \"{0}\"".format(filepath))
			return
		dictionary = data[0]
		self.ApplyPresetDictionary(dictionary)
		self.RefreshSlidersDefault()
		print("Overlappy Default Preset loaded from \"{0}\"".format(filepath))

	def SavePresetWindow(self, *args):
		data = self.SavePresetGetDictionaryAndTitle()
		dictionary = data[0]
		titleText = data[1]
		File.SaveDialog(startingDirectory = self.directoryPresets, variablesDict = dictionary, title = titleText)
	def LoadPresetWindow(self, *args): # TODO MERGE PATH CHECK LOGIC
		### Check if the directory exists; if not, create it
		if not os.path.exists(self.directoryPresets):
			os.makedirs(self.directoryPresets) # Create the directory, including any intermediate directories
		
		readDialogResult = File.ReadDialog(startingDirectory = self.directoryPresets)
		if readDialogResult is None:
			return

		dictionary = readDialogResult[0]
		self.ApplyPresetDictionary(dictionary)

	def SavePresetGetDictionaryAndTitle(self): # TODO MERGE PATH CHECK LOGIC
		dictionary = self.GetCurrentPresetDictionary()

		### Check if the directory exists; if not, create it
		if not os.path.exists(self.directoryPresets):
			os.makedirs(self.directoryPresets) # Create the directory, including any intermediate directories

		currentDate = datetime.datetime.now().strftime("%Y-%m-%d") # hours, minutes, seconds %H:%M:%S
		titleText = "{0} | {1} | {2}".format(self.optionsPlugin.titleGeneral, Overlappy._title, currentDate)

		return dictionary, titleText

	def GetBuiltinPresetDictionary(self): # TODO how to simplify and merge dictionary creation logic?
		dictionary = {
			# "directory": self.options.directory, # TODO move to general preset save
			OverlappyVariables.flagHierarchy: OverlappySettings.optionCheckboxHierarchy,
			OverlappyVariables.flagLayer: OverlappySettings.optionCheckboxLayer,
			OverlappyVariables.flagLoop: OverlappySettings.optionCheckboxLoop,
			OverlappyVariables.flagDeleteSetup: OverlappySettings.optionCheckboxDeleteSetup,
			# OverlappyVariableNames.flagCollisions: OverlappySettings.optionCheckboxCollisions, # TODO add later

			OverlappyVariables.menuRadioButtonLoopCycles0: OverlappySettings.optionRadioButtonsLoop[0],
			OverlappyVariables.menuRadioButtonLoopCycles1: OverlappySettings.optionRadioButtonsLoop[1],
			OverlappyVariables.menuRadioButtonLoopCycles2: OverlappySettings.optionRadioButtonsLoop[2],
			OverlappyVariables.menuRadioButtonLoopCycles3: OverlappySettings.optionRadioButtonsLoop[3],
			OverlappyVariables.menuRadioButtonLoopCycles4: OverlappySettings.optionRadioButtonsLoop[4],

			OverlappyVariables.nucleusTimeScale: OverlappySettings.nucleusTimeScale,
			OverlappyVariables.nucleusGravityActivated: OverlappySettings.nucleusGravityActivated,
			OverlappyVariables.nucleusGravityValue: OverlappySettings.nucleusGravityValue,
			OverlappyVariables.nucleusGravityDirection: OverlappySettings.nucleusGravityDirection,

			OverlappyVariables.particleAimOffsetFloat: OverlappySettings.particleAimOffsetValue,
			OverlappyVariables.particleAimOffsetRadioCollection1: OverlappySettings.particleAimOffsetRadioButtons[0],
			OverlappyVariables.particleAimOffsetRadioCollection2: OverlappySettings.particleAimOffsetRadioButtons[1],
			OverlappyVariables.particleAimOffsetRadioCollection3: OverlappySettings.particleAimOffsetRadioButtons[2],
			OverlappyVariables.particleAimOffsetReverse: OverlappySettings.particleAimOffsetReverse,

			OverlappyVariables.particleAimOffsetUpFloat: OverlappySettings.particleAimOffsetUpValue,
			OverlappyVariables.particleAimOffsetUpRadioCollection1: OverlappySettings.particleAimOffsetUpRadioButtons[0],
			OverlappyVariables.particleAimOffsetUpRadioCollection2: OverlappySettings.particleAimOffsetUpRadioButtons[1],
			OverlappyVariables.particleAimOffsetUpRadioCollection3: OverlappySettings.particleAimOffsetUpRadioButtons[2],
			OverlappyVariables.particleAimOffsetUpReverse: OverlappySettings.particleAimOffsetUpReverse,

			OverlappyVariables.particleRadius: OverlappySettings.particleRadius,
			OverlappyVariables.particleGoalSmooth: OverlappySettings.particleGoalSmooth,
			OverlappyVariables.particleGoalWeight: OverlappySettings.particleGoalWeight,
			OverlappyVariables.particleConserve: OverlappySettings.particleConserve,
			OverlappyVariables.particleDrag: OverlappySettings.particleDrag,
			OverlappyVariables.particleDamp: OverlappySettings.particleDamp,
		}
		return dictionary
	def GetCurrentPresetDictionary(self):
		dictionary = {
			# "directory": self.options.directory, # TODO move to general preset save
			OverlappyVariables.flagHierarchy: self.menuCheckboxHierarchy.Get(),
			OverlappyVariables.flagLayer: self.menuCheckboxLayer.Get(),
			OverlappyVariables.flagLoop: self.menuCheckboxLoop.Get(),
			OverlappyVariables.flagDeleteSetup: self.menuCheckboxDeleteSetup.Get(),
			# OverlappyVariableNames.flagCollisions: self.menuCheckboxCollisions.Get(), # TODO add later

			OverlappyVariables.menuRadioButtonLoopCycles0: cmds.menuItem(self.menuRadioButtonsLoop[0], query = True, radioButton = True), # TODO get current radio button index
			OverlappyVariables.menuRadioButtonLoopCycles1: cmds.menuItem(self.menuRadioButtonsLoop[1], query = True, radioButton = True),
			OverlappyVariables.menuRadioButtonLoopCycles2: cmds.menuItem(self.menuRadioButtonsLoop[2], query = True, radioButton = True),
			OverlappyVariables.menuRadioButtonLoopCycles3: cmds.menuItem(self.menuRadioButtonsLoop[3], query = True, radioButton = True),
			OverlappyVariables.menuRadioButtonLoopCycles4: cmds.menuItem(self.menuRadioButtonsLoop[4], query = True, radioButton = True),

			OverlappyVariables.nucleusTimeScale: self.nucleusTimeScaleSlider.Get(),
			OverlappyVariables.nucleusGravityActivated: cmds.checkBox(self.nucleusGravityCheckbox, query = True, value = True),
			OverlappyVariables.nucleusGravityValue: cmds.floatField(self.nucleusGravityFloatField, query = True, value = True),
			OverlappyVariables.nucleusGravityDirection: cmds.floatFieldGrp(self.nucleusGravityDirectionFloatFieldGrp, query = True, value = True),

			OverlappyVariables.particleAimOffsetFloat: cmds.floatField(self.aimOffsetFloatGroup[1], query = True, value = True),
			OverlappyVariables.particleAimOffsetRadioCollection1: cmds.radioButton(self.aimOffsetRadioCollection[0], query = True, select = True), # TODO get current radio button index
			OverlappyVariables.particleAimOffsetRadioCollection2: cmds.radioButton(self.aimOffsetRadioCollection[1], query = True, select = True),
			OverlappyVariables.particleAimOffsetRadioCollection3: cmds.radioButton(self.aimOffsetRadioCollection[2], query = True, select = True),
			OverlappyVariables.particleAimOffsetReverse: cmds.checkBox(self.aimOffsetCheckbox, query = True, value = True),

			OverlappyVariables.particleAimOffsetUpFloat: cmds.floatField(self.aimOffsetUpFloatGroup[1], query = True, value = True),
			OverlappyVariables.particleAimOffsetUpRadioCollection1: cmds.radioButton(self.aimOffsetUpRadioCollection[0], query = True, select = True), # TODO get current radio button index
			OverlappyVariables.particleAimOffsetUpRadioCollection2: cmds.radioButton(self.aimOffsetUpRadioCollection[1], query = True, select = True),
			OverlappyVariables.particleAimOffsetUpRadioCollection3: cmds.radioButton(self.aimOffsetUpRadioCollection[2], query = True, select = True),
			OverlappyVariables.particleAimOffsetUpReverse: cmds.checkBox(self.aimOffsetUpCheckbox, query = True, value = True),

			OverlappyVariables.particleRadius: self.sliderParticleRadius.Get(),
			OverlappyVariables.particleGoalSmooth: self.sliderParticleGoalSmooth.Get(),
			OverlappyVariables.particleGoalWeight: self.sliderParticleGoalWeight.Get(),
			OverlappyVariables.particleConserve: self.sliderParticleConserve.Get(),
			OverlappyVariables.particleDrag: self.sliderParticleDrag.Get(),
			OverlappyVariables.particleDamp: self.sliderParticleDamp.Get(),
		}
		return dictionary
	
	def ApplyPresetDictionary(self, dictionary):
		if dictionary is None:
			cmds.warning("Preset dictionary is None")
			return

		# filePath = readDialogResult[1]

		### Read preset version and check
		# with open(filePath, 'r') as file:
		# 	first_line = file.readline().strip() # Read first line
		# parts = first_line.split(" | ")
		# if len(parts) >= 2:
		# 	getools_version = parts[0]
		# 	overlappy_version = parts[1]
		# else:
		# 	cmds.warning("No version info in loaded file")
		# isGetoolsVersionCorrect = getools_version == self.options.titleGeneral
		# isOverlappyVersionCorrect = overlappy_version == Overlappy._title
		# if (not isGetoolsVersionCorrect or not isOverlappyVersionCorrect):
		# 	messageResult = ""
		# 	if (not isGetoolsVersionCorrect):
		# 		messageResult += "Getools version is not matched. Current version {0}, Preset version {1}\n".format(getools_version, self.options.titleGeneral)
		# 	if (not isOverlappyVersionCorrect):
		# 		messageResult += "Overlappy version is not matched. Current version {0}, Preset version {1}".format(overlappy_version, Overlappy._title)
		# 	cmds.warning(messageResult)
		
		### Apply loaded values
		self.menuCheckboxHierarchy.Set(dictionary[OverlappyVariables.flagHierarchy])
		self.menuCheckboxLayer.Set(dictionary[OverlappyVariables.flagLayer])
		self.menuCheckboxLoop.Set(dictionary[OverlappyVariables.flagLoop])
		self.menuCheckboxDeleteSetup.Set(dictionary[OverlappyVariables.flagDeleteSetup])

		cmds.menuItem(self.menuRadioButtonsLoop[0], edit = True, radioButton = dictionary[OverlappyVariables.menuRadioButtonLoopCycles0])
		cmds.menuItem(self.menuRadioButtonsLoop[1], edit = True, radioButton = dictionary[OverlappyVariables.menuRadioButtonLoopCycles1])
		cmds.menuItem(self.menuRadioButtonsLoop[2], edit = True, radioButton = dictionary[OverlappyVariables.menuRadioButtonLoopCycles2])
		cmds.menuItem(self.menuRadioButtonsLoop[3], edit = True, radioButton = dictionary[OverlappyVariables.menuRadioButtonLoopCycles3])
		cmds.menuItem(self.menuRadioButtonsLoop[4], edit = True, radioButton = dictionary[OverlappyVariables.menuRadioButtonLoopCycles4])
		
		self.nucleusTimeScaleSlider.Set(dictionary[OverlappyVariables.nucleusTimeScale])
		cmds.checkBox(self.nucleusGravityCheckbox, edit = True, value = dictionary[OverlappyVariables.nucleusGravityActivated])
		cmds.floatField(self.nucleusGravityFloatField, edit = True, value = dictionary[OverlappyVariables.nucleusGravityValue])
		cmds.floatFieldGrp(self.nucleusGravityDirectionFloatFieldGrp, edit = True, value = dictionary[OverlappyVariables.nucleusGravityDirection] + [0]) # HACK used because floatFieldGrp weird behavior, it requires [0, 0, 0, 0] format

		cmds.floatField(self.aimOffsetFloatGroup[1], edit = True, value = dictionary[OverlappyVariables.particleAimOffsetFloat])
		cmds.radioButton(self.aimOffsetRadioCollection[0], edit = True, select = dictionary[OverlappyVariables.particleAimOffsetRadioCollection1])
		cmds.radioButton(self.aimOffsetRadioCollection[1], edit = True, select = dictionary[OverlappyVariables.particleAimOffsetRadioCollection2])
		cmds.radioButton(self.aimOffsetRadioCollection[2], edit = True, select = dictionary[OverlappyVariables.particleAimOffsetRadioCollection3])
		cmds.checkBox(self.aimOffsetCheckbox, edit = True, value = dictionary[OverlappyVariables.particleAimOffsetReverse])

		cmds.floatField(self.aimOffsetUpFloatGroup[1], edit = True, value = dictionary[OverlappyVariables.particleAimOffsetUpFloat])
		cmds.radioButton(self.aimOffsetUpRadioCollection[0], edit = True, select = dictionary[OverlappyVariables.particleAimOffsetUpRadioCollection1])
		cmds.radioButton(self.aimOffsetUpRadioCollection[1], edit = True, select = dictionary[OverlappyVariables.particleAimOffsetUpRadioCollection2])
		cmds.radioButton(self.aimOffsetUpRadioCollection[2], edit = True, select = dictionary[OverlappyVariables.particleAimOffsetUpRadioCollection3])
		cmds.checkBox(self.aimOffsetUpCheckbox, edit = True, value = dictionary[OverlappyVariables.particleAimOffsetUpReverse])

		self.sliderParticleRadius.Set(dictionary[OverlappyVariables.particleRadius])
		self.sliderParticleGoalSmooth.Set(dictionary[OverlappyVariables.particleGoalSmooth])
		self.sliderParticleGoalWeight.Set(dictionary[OverlappyVariables.particleGoalWeight])
		self.sliderParticleConserve.Set(dictionary[OverlappyVariables.particleConserve])
		self.sliderParticleDrag.Set(dictionary[OverlappyVariables.particleDrag])
		self.sliderParticleDamp.Set(dictionary[OverlappyVariables.particleDamp])

		self.UpdateParticleAllSettings()
	def RefreshSlidersDefault(self):
		self.nucleusTimeScaleSlider.RefreshDefaultValue()
		self.sliderParticleRadius.RefreshDefaultValue()
		self.sliderParticleGoalSmooth.RefreshDefaultValue()
		self.sliderParticleGoalWeight.RefreshDefaultValue()
		self.sliderParticleConserve.RefreshDefaultValue()
		self.sliderParticleDrag.RefreshDefaultValue()
		self.sliderParticleDamp.RefreshDefaultValue()


	### GET VALUES
	def GetLoopCyclesIndex(self):
		for i, item in enumerate(self.menuRadioButtonsLoop):
			if cmds.menuItem(item, query = True, radioButton = True):
				return i
		return -1


	### BAKE ANIMATION
	def BakeParticleLogic(self):
		### Check created setups
		if (not self.setupCreated):
			cmds.warning("Particle setup is not created")
			return False

		### Get raw attributes
		attributesType = ()
		if (self.setupCreatedPoint):
			attributesType = Enums.Attributes.translateLong
		elif (self.setupCreatedAim):
			attributesType = attributesType + Enums.Attributes.rotateLong
		elif (self.setupCreatedCombo):
			attributesType = Enums.Attributes.translateLong + Enums.Attributes.rotateLong
		if (len(attributesType) == 0):
			cmds.warning("No baking attributes specified")
			return False

		### Construct attributes with object name
		attributes = []
		for i in range(len(attributesType)):
			attributes.append("{0}.{1}".format(self.selectedObjectsFiltered, attributesType[i]))
		
		### Filter attributes
		attributesFiltered = Attributes.FilterAttributesAnimatable(attributes = attributes, skipMutedKeys = True)
		if attributesFiltered is None:
			self.ParticleSetupDelete(clearCache = True)
			return False
		attributesFilteredForKey = Attributes.FilterAttributesWithoutAnimation(attributesFiltered)
		
		### Cut object name from attributes
		for i in range(len(attributesFiltered)):
			attributesFiltered[i] = attributesFiltered[i].replace(self.selectedObjectsFiltered + ".", "")
		
		### Cut object name from attributes and Set keys for target object attributes
		if attributesFilteredForKey is not None:
			for i in range(len(attributesFilteredForKey)):
				attributesFilteredForKey[i] = attributesFilteredForKey[i].replace(self.selectedObjectsFiltered + ".", "")
			cmds.setKeyframe(self.selectedObjectsFiltered, attribute = attributesFilteredForKey)
		
		### Set time range
		self.time.Scan()
		startTime = self.time.values[2]
		self.time.SetCurrent(startTime)
		if self.menuCheckboxLoop.Get():
			startTime = self.time.values[2] - self.time.values[3] * self.GetLoopCyclesIndex()
			self.time.SetMin(startTime)
			self.time.SetCurrent(startTime)
			self.RefreshParticlePosition()
		cmds.setAttr(self.nucleus1 + ".startFrame", startTime)
		if cmds.objExists(self.nucleus2):
			cmds.setAttr(self.nucleus2 + ".startFrame", startTime)

		### Start logic
		name = "_rebake_" + Text.ConvertSymbols(self.selectedObjectsFiltered)
		objectDuplicate = cmds.duplicate(self.selectedObjectsFiltered, name = name, parentOnly = True, transformsOnly = True, smartTransform = True, returnRootsOnly = True)[0]
		cmds.select(clear = True)
		for attributeTranslate in Enums.Attributes.translateLong:
			cmds.setAttr(objectDuplicate + "." + attributeTranslate, lock = False)
		for attributeRotate in Enums.Attributes.rotateLong:
			cmds.setAttr(objectDuplicate + "." + attributeRotate, lock = False)
		Constraints.ConstrainSecondToFirstObject(self.bakingObject, objectDuplicate, maintainOffset = True, parent = True)
		cmds.select(objectDuplicate, replace = True)

		### Bake animation
		Baker.BakeSelected(classic = True, preserveOutsideKeys = True, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
		Constraints.DeleteConstraints(objectDuplicate)

		### Copy keys, create layers and paste keys
		cmds.copyKey(objectDuplicate, time = (self.time.values[2], self.time.values[3]), attribute = attributesFiltered)
		useLayers = self.menuCheckboxLayer.Get()
		if (useLayers):
			name = OverlappySettings.nameLayers[2] + self.selectedObjectsFiltered
			animLayer = self.LayerCreate(name)
			attrsLayer = []
			for attributeFiltered in attributesFiltered:
				attrsLayer.append("{0}.{1}".format(self.selectedObjectsFiltered, attributeFiltered))
			cmds.animLayer(animLayer, edit = True, attribute = attrsLayer)
			cmds.pasteKey(self.selectedObjectsFiltered, option = "replace", attribute = attributesFiltered, animLayer = animLayer)
		else:
			cmds.pasteKey(self.selectedObjectsFiltered, option = "replaceCompletely", attribute = attributesFiltered)
		cmds.delete(objectDuplicate)

		### Set nucleus time range
		if (self.menuCheckboxLoop.Get()):
			startTime = self.time.values[2]
			cmds.setAttr(self.nucleus1 + ".startFrame", startTime)
			if (cmds.objExists(self.nucleus2)):
				cmds.setAttr(self.nucleus2 + ".startFrame", startTime)
			self.time.Reset()
			Animation.SetInfinityCycle(self.selectedObjectsFiltered)
		else:
			Animation.SetInfinityConstant(self.selectedObjectsFiltered)
		
		### Delete setup
		if (self.menuCheckboxDeleteSetup.Get()):
			self.ParticleSetupDelete(clearCache = True)
		return True
	def BakeParticleVariants(self, variant, *args):
		self.selectedObjects = Selector.MultipleObjects(minimalCount = 1)
		if self.selectedObjects is None:
			if (not self.setupCreated):
				cmds.warning("Can't bake animation. Nothing selected and particle setup is not created")
				return

		### Check zero particle offset
		self.CompileParticleAimOffset()
		sumOffsetTarget = self.particleAimOffsetTarget[0] + self.particleAimOffsetTarget[1] + self.particleAimOffsetTarget[2]
		sumOffsetUp = self.particleAimOffsetUp[0] + self.particleAimOffsetUp[1] + self.particleAimOffsetUp[2]
		isBakingAimOrCombo = variant in [2, 3]
		isBakingCurrent = variant == 0 and (self.setupCreatedAim or self.setupCreatedCombo)
		if (isBakingAimOrCombo or isBakingCurrent):
				if (sumOffsetTarget == 0 or sumOffsetUp == 0):
					dialogResult = cmds.confirmDialog(
						title = "Zero particle aim offset detected",
						message = "For baking using aim, set the aim offset to non-zero values.\nIf aim or up offsets are zero, the particle probably will stay in the same position as the original object, and no rotation will occur.\n",
						messageAlign = "left",
						icon = "warning",
						button = ["Continue anyway", "Cancel"],
						annotation = ["Proceed with zero offset, no useful animation will be baked", "Cancel baking operation"],
						defaultButton = "Cancel",
						cancelButton = "Cancel",
						dismissString = "TODO: dismissString"
						)
					if (dialogResult == "Cancel"):
						cmds.warning("Overlappy Rotation Baking cancelled")
						self.selectedObjects = None
						return

		MayaSettings.CachedPlaybackDeactivate()
		
		### Cache initial position for the first selected object
		self.time.Scan()
		self.time.Reset()
		self.selectedObjectsStartPosition = cmds.xform(self.selectedObjects[0], query = True, translation = True, worldSpace = True)

		### Run baking process
		if (variant == 0 or self.selectedObjects is None):
			wasBakedSuccessfully = self.BakeParticleLogic()
			if (wasBakedSuccessfully):
				cmds.select(self.selectedObjectsFiltered, replace = True)
		else:
			### Check hierarchy and get objects
			if (self.menuCheckboxHierarchy.Get()):
				self.selectedObjects = Selector.SelectHierarchyTransforms()
			### Bake
			for i in range(len(self.selectedObjects)):
				cmds.select(self.selectedObjects[i], replace = True)
				self.ParticleSetupLogic(variant)
				self.BakeParticleLogic()
			### Select original objects
			cmds.select(self.selectedObjects, replace = True)
		self.RefreshParticlePosition()
		self.selectedObjects = None


	### LAYERS
	def LayerCreate(self, name):
		### Create main layer
		if (not cmds.objExists(OverlappySettings.nameLayers[0])):
			self.layers[0] = Layers.Create(layerName = OverlappySettings.nameLayers[0])
		
		### Create layers on selected
		layerName = Text.ConvertSymbols(name) + "_1"
		return Layers.Create(layerName = layerName, parent = self.layers[0])
	def LayerMoveToSafeOrTemp(self, safeLayer=True, *args): # TODO rework
		id = [0, 1]
		
		if (not safeLayer):
			id = [1, 0]
		
		nameLayer1 = OverlappySettings.nameLayers[id[0]]
		nameLayer2 = OverlappySettings.nameLayers[id[1]]

		### Check source layer
		if (not cmds.objExists(nameLayer1)):
			cmds.warning("Layer \"{0}\" doesn't exist".format(nameLayer1))
			return
		
		### Get selected layers
		selectedLayers = []
		for animLayer in cmds.ls(type = "animLayer"):
			if cmds.animLayer(animLayer, query = True, selected = True):
				selectedLayers.append(animLayer)
				
		### Check selected count
		childrenLayers = cmds.animLayer(self.layers[id[0]], query = True, children = True)
		filteredLayers = []
		if (len(selectedLayers) == 0):
			if childrenLayers is None:
				cmds.warning("Layer \"{0}\" is empty".format(nameLayer1))
				return
			else:
				for layer in childrenLayers:
					filteredLayers.append(layer)
		else:
			if childrenLayers is None:
				cmds.warning("Layer \"{0}\" is empty".format(nameLayer1))
				return
			else:
				for childLayer in childrenLayers:
					for selectedLayer in selectedLayers:
						if (childLayer == selectedLayer):
							filteredLayers.append(childLayer)
			if (len(filteredLayers) == 0):
				cmds.warning("Nothing to move")
				return
		
		### Create safe layer
		if (not cmds.objExists(nameLayer2)):
			self.layers[id[1]] = cmds.animLayer(nameLayer2, override = True)
		
		### Move children or selected layers
		for layer in filteredLayers:
			cmds.animLayer(layer, edit = True, parent = self.layers[id[1]])
		
		### Delete TEMP layer if no children
		if (len(filteredLayers) == len(childrenLayers)):
			Layers.Delete(nameLayer1)

