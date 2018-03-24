# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'control.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ControlForm(object):
    def setupUi(self, ControlForm):
        ControlForm.setObjectName("ControlForm")
        ControlForm.resize(529, 292)
        self.gridLayout = QtWidgets.QGridLayout(ControlForm)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(ControlForm)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.charts = QtWidgets.QWidget(self.splitter)
        self.charts.setObjectName("charts")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.charts)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.tabWidget = QtWidgets.QTabWidget(self.splitter)
        self.tabWidget.setObjectName("tabWidget")
        self.jupyter_console = QtWidgets.QWidget()
        self.jupyter_console.setObjectName("jupyter_console")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.jupyter_console)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_5.addLayout(self.verticalLayout)
        self.tabWidget.addTab(self.jupyter_console, "")
        self.tabWidgetPage1 = QtWidgets.QWidget()
        self.tabWidgetPage1.setObjectName("tabWidgetPage1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tabWidgetPage1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cmd = QtWidgets.QLineEdit(self.tabWidgetPage1)
        self.cmd.setObjectName("cmd")
        self.horizontalLayout.addWidget(self.cmd)
        self.enableServos = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.enableServos.setCheckable(True)
        self.enableServos.setObjectName("enableServos")
        self.horizontalLayout.addWidget(self.enableServos)
        self.pauseBtn = QtWidgets.QPushButton(self.tabWidgetPage1)
        self.pauseBtn.setCheckable(True)
        self.pauseBtn.setObjectName("pauseBtn")
        self.horizontalLayout.addWidget(self.pauseBtn)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.tabWidgetPage1)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.mode = QtWidgets.QComboBox(self.tabWidgetPage1)
        self.mode.setObjectName("mode")
        self.mode.addItem("")
        self.mode.addItem("")
        self.mode.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.mode)
        self.label_2 = QtWidgets.QLabel(self.tabWidgetPage1)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.const_p = QtWidgets.QDoubleSpinBox(self.tabWidgetPage1)
        self.const_p.setDecimals(8)
        self.const_p.setMinimum(-1e+18)
        self.const_p.setProperty("value", 0.0)
        self.const_p.setObjectName("const_p")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.const_p)
        self.label_4 = QtWidgets.QLabel(self.tabWidgetPage1)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.const_i = QtWidgets.QDoubleSpinBox(self.tabWidgetPage1)
        self.const_i.setDecimals(8)
        self.const_i.setObjectName("const_i")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.const_i)
        self.label_3 = QtWidgets.QLabel(self.tabWidgetPage1)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.const_d = QtWidgets.QDoubleSpinBox(self.tabWidgetPage1)
        self.const_d.setDecimals(8)
        self.const_d.setMinimum(-1e+18)
        self.const_d.setMaximum(1e+19)
        self.const_d.setObjectName("const_d")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.const_d)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.tabWidget.addTab(self.tabWidgetPage1, "")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(ControlForm)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(ControlForm)

    def retranslateUi(self, ControlForm):
        _translate = QtCore.QCoreApplication.translate
        ControlForm.setWindowTitle(_translate("ControlForm", "Form"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.jupyter_console), _translate("ControlForm", "Console"))
        self.enableServos.setText(_translate("ControlForm", "Enable servos"))
        self.pauseBtn.setText(_translate("ControlForm", "Pause"))
        self.label.setText(_translate("ControlForm", "mode"))
        self.mode.setItemText(0, _translate("ControlForm", "balance"))
        self.mode.setItemText(1, _translate("ControlForm", "stop"))
        self.mode.setItemText(2, _translate("ControlForm", "demo"))
        self.label_2.setText(_translate("ControlForm", "proportional"))
        self.label_4.setText(_translate("ControlForm", "integration"))
        self.label_3.setText(_translate("ControlForm", "derivative"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWidgetPage1), _translate("ControlForm", "Parameters"))

