#!/usr/bin/env python2
#!coding:utf-8
#  __author__ = 'jiangyulin'

import getTypes

from PyQt4 import QtGui, QtCore

class WarningBox(QtGui.QMessageBox):
    def __init__(self, parent=None, message = None, type = QtGui.QMessageBox.Warning):
        QtGui.QMessageBox.__init__(self, parent=parent)
        self.setIcon(type)
        self.setText(message)
        self.exec_()


class AddDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.resize(100, 100)
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel(u'Domain', parent=self), 0, 0, 1, 1)
        self.domain = QtGui.QLineEdit(parent=self)
        grid.addWidget(self.domain, 0, 1, 1, 1)

        buttonBox = QtGui.QDialogButtonBox(parent=self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(grid)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def get_domain(self):
        # 注意 这里发那会是qt里面的Qstring
        return self.domain.text()


class AddRecordsDialog(QtGui.QDialog):
    def __init__(self, user, domain, parent=None, edit_record = None):
        QtGui.QDialog.__init__(self, parent=parent)
        self.resize(300, 100)
        grid = QtGui.QGridLayout()
        self.__domain = domain
        self.id = None
        anytype = getTypes.DnsTypesDetail(user, domain_grade= domain.getgrade(), domain_id=domain.getid())
        i = 0

        if edit_record is not None:
            self.id = QtGui.QLineEdit(edit_record['id'])
            grid.addWidget(QtGui.QLabel(u'id' ,parent=self), 0, 0)
            grid.addWidget(self.id, 0, 1)
            i = 1

        self.recordname = QtGui.QLineEdit(parent=self)
        self.recordtype = QtGui.QComboBox(parent=self)
        record_type = anytype.getRecordTypes()
        self.recordtype.addItems(record_type)
        self.linetype = QtGui.QComboBox(parent=self)
        line_type = anytype.getLineTypes()
        self.linetype.addItems(line_type)
        self.value = QtGui.QLineEdit(parent=self)
        self.ttl = QtGui.QLineEdit(parent=self)
        self.mx = QtGui.QLineEdit(parent=self)

        if edit_record is not None:
            self.recordname.setText(edit_record['name'])
            self.recordtype.setCurrentIndex(record_type.index(edit_record['type']))
            self.linetype.setCurrentIndex(line_type.index(edit_record['line']))
            self.value.setText(edit_record['value'])
            self.ttl.setText(edit_record['ttl'])
            self.mx.setText(edit_record['mx'])


        grid.addWidget(QtGui.QLabel(u'sub domain', parent=self), i, 0)
        grid.addWidget(self.recordname, i, 1,)
        grid.addWidget(QtGui.QLabel(u'Record Type', parent=self), i+1, 0)
        grid.addWidget(self.recordtype, i+1, 1)
        grid.addWidget(QtGui.QLabel(u'Line Type', parent=self), i+2, 0)
        grid.addWidget(self.linetype, i+2, 1)
        grid.addWidget(QtGui.QLabel(u'Value', parent=self), i+3, 0)
        grid.addWidget(self.value, i+3, 1)
        grid.addWidget(QtGui.QLabel(u'TTL', parent=self), i+4, 0)
        grid.addWidget(self.ttl, i+4, 1)
        grid.addWidget(QtGui.QLabel(u'mx', parent=self), i+5, 0)
        grid.addWidget(self.mx, i+5, 1)

        buttonBox = QtGui.QDialogButtonBox(parent=self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.layout = QtGui.QVBoxLayout()
        self.layout.addLayout(grid)
        self.layout.addWidget(buttonBox)
        self.setLayout(self.layout)

    def getrecorddetaile(self):
        return_value = {}
        if self.id is not None:
            return_value = {
                'record_id':unicode(self.id.text())
            }
        return_value.update({
            'domain_id':self.__domain.getid(),
            'sub_domain':unicode(self.recordname.text()),
            'record_type':unicode(self.recordtype.currentText()),
            'record_line':unicode(self.linetype.currentText()),
            'value':unicode(self.value.text()),
            'ttl':unicode(self.ttl.text()),
            'mx':unicode(self.mx.text())
        })
        return return_value