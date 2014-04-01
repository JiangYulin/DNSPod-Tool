#coding:utf-8
#!/usr/bin/env python2

import sys
import json
import types
import requests
from PyQt4 import QtCore, QtGui
import Dnspod as dns
import User
import domain
import record
import pickle

import dialog

DomainListUrl = 'https://dnsapi.cn/Domain.List'
DomainDeleteUrl = "https://dnsapi.cn/Domain.Remove"
DomainCreateUrl = "https://dnsapi.cn/Domain.Create"
DomainRecordListUrl = "https://dnsapi.cn/Record.List"


class Login(QtGui.QWidget):
    def __init__(self):
        super(Login, self).__init__()
        self.setWindowTitle("DNSPod Login")
        self.__init_ui()
        self.resize(300, 150)

    def __init_ui(self):
        gridLayout = QtGui.QGridLayout()
        labelemail = QtGui.QLabel("email")
        labelpass = QtGui.QLabel("password")
        lineemail = QtGui.QLineEdit('')
        linepass = QtGui.QLineEdit('')
        linepass.setEchoMode(QtGui.QLineEdit.Password)
        buttonlogin = QtGui.QPushButton("Login")
        buttonlogin.clicked.connect(lambda: self.__login(unicode(lineemail.text()), unicode(linepass.text())))
        gridLayout.addWidget(labelemail, 0, 0)
        gridLayout.addWidget(lineemail, 0, 1)
        gridLayout.addWidget(labelpass, 1, 0)
        gridLayout.addWidget(linepass, 1, 1)
        gridLayout.addWidget(buttonlogin, 2, 1)
        self.setLayout(gridLayout)

    def __login(self, login_email, login_password):
        user = User.User(login_email, login_password)
        if user.logined():
            self.hide()
            domain = DomainWindow(user, parent = self)
            domain.show()
        else:
            dialog.WarningBox(parent=self, message=user.getstatus()['message'])




class DomainWindow(QtGui.QDialog):
    def __init__(self, user, parent):
        #把dnspod 用户实例当作参数传入
        QtGui.QWidget.__init__(self, parent = parent)
        self.user = user
        self.setWindowTitle('DNSPod Domain Control')
        #主布局
        self.mainLayout = QtGui.QVBoxLayout()
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 10)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        #添加次级布局
        self.setLayout(self.mainLayout)

        self.domains = None
        self.domaintable = None

        self.menubar = None
        self.resize(400, 200)
        self.menubar = QtGui.QMenuBar(self)
        self.__initmenu()
        #添加菜单栏，和内容容器
        self.mainLayout.addWidget(self.menubar)
        self.mainLayout.addLayout(self.layout)
        self.__refreshlist()

    def __initmenu(self):
        if self.menubar is not None:
            file = self.menubar.addMenu("File")
            file.addAction('Export This Item', self.__handleexport)
            file.addAction("Import To This Item", self.__handleimport)
            file.addAction('Delete This Item', self.__delete)
            file.addAction('Add Domain', self.__add)
            file.addAction("Quit", sys.exit)

    def __ui(self, data):
        self.domains = data
        col = data.__len__()
        self.domaintable = QtGui.QTableWidget(col or 1, 1)
        self.domaintable.setHorizontalHeaderLabels(['Domain Name'])
        #隐藏表头
        self.domaintable.verticalHeader().setVisible(False)
        self.domaintable.horizontalHeader().setVisible(False)
        #隔行更改颜色
        self.domaintable.setAlternatingRowColors(True)
        self.domaintable.horizontalHeader().setStretchLastSection(True)
        #填充数据
        i = 0
        for item in data:
            self.domaintable.setItem(i, 0, QtGui.QTableWidgetItem(item['name']))
            i += 1
        self.domaintable.cellDoubleClicked.connect(self.__handledoubleclick)
        self.domaintable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.domaintable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.layout.addWidget(self.domaintable)


    def __handledoubleclick(self, x, y):
        self.__show_domain_record(self.domains[x]['id'])
        # 显示记录的界面

    def __show_domain_record(self, domain_id):
        __domain = domain.Domain(self.user, {'id':domain_id})
        record = RecordsWindow(user = self.user, parent=self, dnsdomain=__domain)
        record.show()


    def contextMenuEvent(self, event):
        self.menu = QtGui.QMenu(self)
        deleteAction = QtGui.QAction('delete', self)
        deleteAction.triggered.connect(self.__delete)
        exportAction = QtGui.QAction('export records', self)
        exportAction.triggered.connect(self.__handleexport)
        importAction = QtGui.QAction('import records', self)
        importAction.triggered.connect(self.__handleimport)
        self.menu.addAction(deleteAction)
        self.menu.addAction(exportAction)
        self.menu.addAction(importAction)
        self.menu.popup(QtGui.QCursor.pos())

    def __handleimport(self):
        self.__import()
    #导出函数

    def __handleexport(self):
        domain_id = self.domains[self.domaintable.currentRow()]['id']
        self.__export(domain_id)

    def __export(self, domain_id):
        data = dns.get_domain_records(self.user, domain_id)
        filebox = QtGui.QFileDialog(parent=self)
        filebox.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        file_name = filebox.getSaveFileName()
        if file_name != u'':
            try:
                fs_file = open(file_name, 'w')
            except IOError as e:
                dialog.WarningBox(parent=self, message=e.strerror)
            else:
                pickle.dump(data, fs_file)
                fs_file.close()
                try:
                    fs_file = open(file_name, 'r')
                except IOError as e:
                    dialog.WarningBox(self, u'校验失败')
                else:
                    b = pickle.loads(fs_file.read())
                    fs_file.close()
                    if b == data:
                        dialog.WarningBox(self, 'Export Success!', type=QtGui.QMessageBox.Information)
                    else:
                        dialog.WarningBox(self, "Export Failed! Data doesn't match")


    def __import(self):
        filebox = QtGui.QFileDialog(parent=self)
        current = self.domaintable.currentRow()
        filebox.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        file_name = filebox.getOpenFileName()
        print file_name
        if file_name != u'':
            try:
                fs_file = open(file_name,'r')
            except IOError as e:
                dialog.WarningBox(parent=self, message=e.strerror)
            else:
                try:
                    restoredata = pickle.loads(fs_file.read())
                except KeyError as e:
                    dialog.WarningBox(self, 'you might choose wrong file', QtGui.QMessageBox.Critical)
                    return False
                records = restoredata['records']
                i = 0
                if isinstance(records, types.ListType) is False:
                    dialog.WarningBox(self, "Input File Error")
                    return False
                need_keys = [
                    'id',
                    'line',
                    'type',
                    'name',
                    'NS',
                    'mx'
                ]
                for item in records:
                    for key in need_keys:
                        if item.has_key(key) is False:
                            dialog.WarningBox(self, 'Input File Error')
                            return False
                    #删除id值，记录将作为一个新的记录插入到记录列表中
                    param.pop('id')
                    param.update({
                        'domain_id':self.domains[current]['id']
                    })
                    temp = record.Record(self.user, param=param)
                    print param
                    #多线程ke用于提高速度
                    if temp.save() is False:
                        i += 1
                import_message = "Total: " + str(records.__len__()) + "Failed: " + str(i-2)
                dialog.WarningBox(self, message=import_message)



    # 菜单栏 file->add 调用此函数来增加域名

    def __add(self):
        addbox = dialog.AddDialog(self)
        if addbox.exec_():
            domain_name = unicode(addbox.get_domain())
            #result = dns.add_domain(self.user, domain_name)
            delete_domain = domain.Domain(self.user, {'name': domain_name})
            result = delete_domain.save()
            if result is not False:
                self.__refreshlist()
            else:
                dialog.WarningBox(parent=self, message = delete_domain.getstatus()['message'])

    def __delete(self):
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to delete this item?", QtGui.QMessageBox.Yes |
                                                                                QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            result = dns.delete_domain(self.user, self.domains[self.domaintable.currentRow()]['id'])
            if result['status']['code'] == '1':
                self.__refreshlist()
            else:
                dialog.WarningBox(parent=self, message = result['status']['message'])

    def __refreshlist(self):
        result = dns.getalldomains(self.user)
        if result is False:
            print "false"
            pass
        else:
            if result['status']['code'] != '1':
                #pop a dialog to show errorp
                print  result['status']['code']
            else:
                self.__clear_ui(self.layout)
                self.__ui(result['domains'])

    def __clear_ui(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.__clear_ui(child.layout)


class RecordsWindow(QtGui.QDialog):
    def __init__(self, parent, user, dnsdomain):
        super(RecordsWindow, self).__init__(parent = parent)
        self.user = user
        self.__domain = dnsdomain
        self.resize(520, 250)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        #create menu bar
        self.menubar = QtGui.QMenuBar()
        self.__init_menu()
        self.mainLayout.addWidget(self.menubar)
        self.layout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.layout)

        self.recordstable = None
        self.records = None

        self.__refreshlist()

    def __init_menu(self):
        file = self.menubar.addMenu("File")
        file.addAction("Add Record", self.__add)
        file.addAction("Refresh List", self.__refreshlist)


    def __showdata(self, data, domain_name = None):
        self.__clear_ui(self.layout)
        col = data.__len__()
        self.recordstable = QtGui.QTableWidget(col, 5)
        if domain_name is not None:
            self.setWindowTitle(domain_name+"'s Records")
        headers = [
            'record',
            'type',
            'line type',
            'value',
            'mx'
        ]
        self.recordstable.setHorizontalHeaderLabels(headers)
        self.recordstable.horizontalHeader().setStretchLastSection(True)
        self.recordstable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.recordstable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        i = 0
        for item in data:
            self.recordstable.setItem(i, 0, QtGui.QTableWidgetItem(item['name']))
            self.recordstable.setItem(i, 1, QtGui.QTableWidgetItem(item['type']))
            self.recordstable.setItem(i, 2, QtGui.QTableWidgetItem(item['line']))
            self.recordstable.setItem(i, 3, QtGui.QTableWidgetItem(item['value']))
            self.recordstable.setItem(i, 4, QtGui.QTableWidgetItem(item['mx']))
            i += 1
        self.records = data
        self.recordstable.cellDoubleClicked.connect(self.__handledoubleclick)
        self.layout.addWidget(self.recordstable)
        self.setLayout(self.mainLayout)

    def __handledoubleclick(self):
        self.__edit()

    def __edit(self):
        editBox = dialog.AddRecordsDialog(self.user, self.__domain, parent=self, edit_record=self.records[self.recordstable.currentRow()])
        if editBox.exec_():
            result =  editBox.getrecorddetaile()
            changed_record = record.Record(self.user, result)
            changed_record.save()
            self.__refreshlist()

    def __clear_ui(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.__clear_ui(child.layout)

    def contextMenuEvent(self, event):
        self.menu = QtGui.QMenu(self)
        deleteAction = QtGui.QAction('delete', self)
        deleteAction.triggered.connect(self.__delete)
        self.menu.addAction(deleteAction)
        self.menu.popup(QtGui.QCursor.pos())

    def __delete(self):
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to delete this item?", QtGui.QMessageBox.Yes |
                                                                                QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            new_param = self.records[self.recordstable.currentRow()]
            new_param.update({
                'domain_id':self.__domain.getid()
            })
            delete_record = record.Record(self.user, new_param)
            result = delete_record.delete()
            if result is not True:
                dialog.WarningBox(parent=self, message=result['message'])
            else:
                self.__refreshlist()

    def __refreshlist(self):
        result = self.__domain.getallrecords()
        if result is False:
            dialog.WarningBox(parent=self, message=self.__domain.getstatus()['message'])
        else:
            self.__clear_ui(self.layout)
            self.__showdata(result['records'])

    #functions menubar call

    def __add(self):
        recordBox = dialog.AddRecordsDialog(user = self.user, domain = self.__domain, parent=self)
        if recordBox.exec_():
            record_detail = recordBox.getrecorddetaile()
            #add domain_id to record_detail
            record_detail.update({
                'domain_id': self.__domain.getid()
            })
            #record_detail ,
            #
            new_record = record.Record(self.user, record_detail)
            if new_record.save():
                self.__refreshlist()
            else:
                status = new_record.getstatus()
                message = QtGui.QMessageBox(self)
                message.setIcon(QtGui.QMessageBox.Warning)
                message.setText(status['message'])
                message.exec_()



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    login = Login()
    login.show()
    sys.exit(app.exec_())

