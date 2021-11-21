import time
import struct
import zmq
import threading


import sys
import socket
from PyQt5.QtCore import *
from PyQt5 import *
from PyQt5.QtWidgets import QApplication, QGridLayout, QPushButton, QLineEdit, QComboBox, QWidget
import xmlrpc.client
global xmlrpc_client_0
xmlrpc_client_0 = xmlrpc.client.ServerProxy('http://localhost:8080')

global varList
varList = []
global mainflag
mainflag = False


global logfilename

def opencfg():
	try:
		with open('var.cfg', 'r') as f:
			for line in f:
				l = line.split()
				name = l[0]
				vtype = l[1]
				defv = l[2]
				VariableWidget(name, vtype, defv)
			varSort()
	except socket.error:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setText("Connection error!")
			msg.setWindowTitle("Error!")
			retval = msg.exec_()
			exit()
	except IOError:
		pass

def savecfg():
	global varList
	with open('var.cfg', 'w') as f:
		for i in varList:
			f.write(i.name + ' ' + i.vtype + ' ' + i.defaultv + '\n')


class VariableWidget(QWidget):
	"""docstring for ClassName"""
	def __init__(self, name, vtype, defaultv, realval = 0):
		super(VariableWidget, self).__init__()
		self.name = name
		self.vtype = vtype
		self.defaultv = defaultv
		self.realval = realval
		self.setLayout(QGridLayout())
		self.lineEdit = QLineEdit(defaultv)
		self.lineEdit.returnPressed.connect(self._setValue)
		self.displ = QLineEdit(str(realval))
		self.displ.setReadOnly(True)
		self.label = QLabel(name + ':' + vtype)
		self.btn = QToolButton()
		myicon = QIcon()
		myicon.addPixmap(QPixmap("./trash-can.png"), QIcon.Normal, QIcon.Off)
		self.btn.setIcon(myicon)
		self.btn.setIconSize(QSize(24, 24))
		self.btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
		self.layout().addWidget(self.label, 0, 0)
		self.layout().addWidget(self.displ, 0, 1)
		self.layout().addWidget(self.lineEdit, 0, 2)
		self.layout().addWidget(self.btn, 0, 3)
		self.btn.clicked.connect(self._rmv)
		global xmlrpc_client_0
		tmp = str('get_'+self.name)
		self.getter = getattr(xmlrpc_client_0, tmp)
		tmp = str('set_'+self.name)
		self.setter = getattr(xmlrpc_client_0, tmp)
		try:
			self._updateVal()
		except xmlrpclib.Fault:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setText("Error! Perhaps a variable with '%s' name does not exist."%self.name)
			msg.setWindowTitle("Warning!")
			retval = msg.exec_()
			return			
			
		global varList
		varList.append(self)
	def _rmv(self, idkwtf):
		global varList
		varList.remove(self)
		self.close()
		varSort()

	def _updateVal(self):
		self.displ.setText(str(self.getter()))

	def _setValue(self):
		try:
			if self.vtype == 'float':
				self.setter(float(self.lineEdit.text()))
			else:
				self.setter(int(self.lineEdit.text()))
			self._updateVal()
		except socket.error:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setText("Connection error!")
			msg.setWindowTitle("Error!")
			retval = msg.exec_()
		except ValueError:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setText("Wrong value\nIt should be %s"%self.vtype)
			msg.setWindowTitle("Error!")
			retval = msg.exec_()

app = QApplication(sys.argv)

app.aboutToQuit.connect(savecfg)

mainWindow = QWidget()
mainGrid = QGridLayout()
mainWindow.setLayout(mainGrid)
mainWindow.setGeometry(100,100,800,600)
mainWindow.setWindowTitle("GUI test")


fileWidget = QWidget()
fileGrid = QGridLayout()
fileWidget.setLayout(fileGrid)

openLogBtn = QPushButton()
openLogBtn.setText("Open")

startstopLogBtn = QPushButton()
startstopLogBtn.setText("Start")
startstopLogBtn.setEnabled(False)

def logging():
	global mainflag
	while True:
		if mainflag:
			global updates
			global logfilename
			file = open(logfilename, 'a+')
			msg = updates.recv()
			msg2 = bytearray(msg)
			cfg = str(len(msg)/4) + 'f'
			tmp = struct.unpack(cfg, msg2)
			file.write(str(tmp) + '\n')
			file.close()

msgthread = threading.Thread(target=logging)
msgthread.daemon = True
msgthread.start()

def olb_clicked():
	global logfilename
	logfilename = QFileDialog.getSaveFileName()
	openLogLE.setText(logfilename)
	if logfilename:
		startstopLogBtn.setEnabled(True)
		ctx = zmq.Context()
		global updates
		updates = ctx.socket(zmq.SUB)
		updates.linger = 0
		updates.setsockopt(zmq.SUBSCRIBE, '')
		updates.connect("tcp://localhost:5556")
	else:
		startstopLogBtn.setEnabled(False)

def sslb_clicked():
	global mainflag
	if mainflag == False:
		mainflag = True
		startstopLogBtn.setText('Stop')
		
	else:
		mainflag = False
		startstopLogBtn.setText('Start')

openLogBtn.clicked.connect(olb_clicked)
startstopLogBtn.clicked.connect(sslb_clicked)

openLogLE = QLineEdit()
openLogLE.setPlaceholderText("Log filename (output)")
openLogLE.setReadOnly(True)
openLogLE.setFocusPolicy(0)

fileGrid.addWidget(openLogLE, 0, 0, 1, 4)
fileGrid.addWidget(openLogBtn, 0, 5, 1, 1)
fileGrid.addWidget(startstopLogBtn, 0, 6, 1, 1)

openInBtn = QPushButton()
openInBtn.setText("Open")

def oib_clicked():
	name = QFileDialog.getSaveFileName()
	openInLE.setText(name)


openInBtn.clicked.connect(oib_clicked)


openInLE = QLineEdit()
openInLE.setPlaceholderText("Data filename (input)")
openInLE.setReadOnly(True)
openInLE.setFocusPolicy(0)

fileGrid.addWidget(openInLE, 1, 0, 1, 4)
fileGrid.addWidget(openInBtn, 1, 5, 1, 1)




addWidget = QWidget()
addGrid = QGridLayout()
addWidget.setLayout(addGrid)

addNameLE = QLineEdit()
addNameLE.setPlaceholderText("Name")

addValLE = QLineEdit()
addValLE.setPlaceholderText("Value")

addCB = QComboBox()
addCB.addItem('float')
addCB.addItem('int')
addCB.addItem('short')
addCB.addItem('byte')

addBtn = QPushButton()
addBtn.setText("Add")


def testAdd():
	if addCB.currentText() == 'float':
		try:
			val = float(addValLE.text())
		except ValueError:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setText("That is not a float!")
			msg.setWindowTitle("Warning!")
			retval = msg.exec_()
			return
	else:
		try:
			val = int(addValLE.text())
		except ValueError:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setText("That is not a number!")
			msg.setWindowTitle("Warning!")
			retval = msg.exec_()
			return
	VariableWidget(addNameLE.text(), addCB.currentText(), addValLE.text())
	varSort()

addBtn.clicked.connect(testAdd)
addNameLE.returnPressed.connect(testAdd)
addValLE.returnPressed.connect(testAdd)

addGrid.addWidget(addNameLE, 0, 0, 1, 1)
addGrid.addWidget(addCB, 0, 1, 1, 1)
addGrid.addWidget(addValLE, 0, 2, 1, 1)
addGrid.addWidget(addBtn, 0, 3, 1, 1)


varWidget = QWidget()
varGrid = QGridLayout()
varWidget.setLayout(varGrid)


def varSort():
	for i in range(len(varList)):
		varGrid.addWidget(varList[i], i/2, i%2)

mainGrid.addWidget(addWidget, 0, 0, 1, 1)
mainGrid.addWidget(varWidget, 1, 0, 10, 1)
mainGrid.addWidget(fileWidget, 12, 0, 1, 1)

opencfg()

mainWindow.show()

sys.exit(app.exec_())