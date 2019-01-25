# -*- coding: utf-8 -*-
# @Author: ichadhr
# @Date:   2018-10-27 21:13:08
# @Last Modified by:   richard.hari@live.com
# @Last Modified time: 2018-10-30 11:54:15
import os
import sys
import time
import re
import itertools
import appinfo
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from gui import Ui_MainWindow
from pathlib import Path
import string

import distutils.dir_util

import xlrd

# variabel for header CSV
HEAD_CODE_STORE = 'code_store'
HEAD_PO_NO      = 'po_no'
HEAD_BARCODE    = 'barcode'
HEAD_QTY        = 'qty'
HEAD_MODAL      = 'modal_karton'

NEWDIR     = 'CSV-output'
DELIM      = ';'

# main class
class mainWindow(QMainWindow, Ui_MainWindow) :
    def __init__(self) :
        QMainWindow.__init__(self)
        self.setupUi(self)

        # app icon
        self.setWindowIcon(QIcon(':/resources/icon.png'))

        # centering app
        tr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        tr.moveCenter(cp)
        self.move(tr.topLeft())

        # button Open
        self.btOpen.clicked.connect(self.openXLS)

        # button convert
        self.btCnv.clicked.connect(self.BtnCnv)

        # status bar
        self.statusBar().showMessage('v'+appinfo._version)

        # hide label path
        self.lbPath.hide()
        self.lbPath.clear()

        # add item to combobox
        self.cbOutlet.addItem('CV. TEKSINDO LESTARI', '053312')
        self.cbOutlet.addItem('PT. TEMAS ALVINDO', '053313')


    # get last row
    def getLastRow(self) :
        res = []
        sheet = self.funcXLRD()

        return sheet.nrows


    # PATH FILE
    def openXLS(self) :
        fileName, _ = QFileDialog.getOpenFileName(self,"Open File", "","XLS Files (*.xls)")
        if fileName:
            self.lbPath.setText(fileName)
            x = QUrl.fromLocalFile(fileName).fileName()
            self.edFile.setText(x)
            self.edFile.setStyleSheet("""QLineEdit { color: green }""")


    # function xlrd
    def funcXLRD(self) :
        # PATH file
        pathXLS = self.lbPath.text()

        if len(pathXLS) == 0:

            QMessageBox.warning(self, "Warning", "Please select XLS file first!", QMessageBox.Ok)
            sys.exit(0)

        else :
            try :
                book = xlrd.open_workbook(pathXLS, ragged_rows=True)
                sheet = book.sheet_by_index(0)

                return sheet

            except xlrd.XLRDError as e:
                msg = "Unsupported format, or corrupt file !"
                errorSrv = QMessageBox.critical(self, "Error", msg, QMessageBox.Abort)
                sys.exit(0)

    # function get cell range
    def get_cell_range(self, start_col, start_row, end_col, end_row):
        sheet = self.funcXLRD()
        return [sheet.row_values(row, start_colx=start_col, end_colx=end_col+1) for row in range(start_row, end_row+1)]


    # open file
    def open_file(self, filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])


    # create directory if not exist
    def CreateDir(self, cDIR, nDir, filename) :

        resPathFile =  Path(os.path.abspath(os.path.join(cDIR, nDir, "{}.csv".format(filename))))

        if os.path.exists(str(resPathFile)) :
            os.remove(str(resPathFile))
        else :
            # os.makedirs(os.path.dirname(resPathFile), exist_ok=True)
            distutils.dir_util.mkpath(os.path.dirname(str(resPathFile)))

        return str(resPathFile)


    # Get Barcode
    def getPONO(self) :

        result = self.get_cell_range(29, 1, 29, 1)
        return result

    # Get Barcode
    def getBRC(self) :

        endrow = self.getLastRow() - 1
        newlist = self.get_cell_range(5, 0, 5, endrow)

        flat_list = []
        res = []

        for sublist in newlist :
            for item in sublist:
                flat_list.append(item)

        result = filter(None, flat_list)

        for i in result :
            res.append([i])

        res = self.checkListFloat(res)
        res = res[1:][::2]

        return res


    # Get Barcode
    def getQTY(self) :

        endrow = self.getLastRow() - 1
        newlist = self.get_cell_range(23, 0, 23, endrow)

        flat_list = []
        res = []

        for sublist in newlist :
            for item in sublist:
                if type(item) == float :
                    flat_list.append(item)

        result = filter(None, flat_list)

        for i in result :
            res.append([int(i)])

        return res


    # Get Barcode
    def getMDL(self) :

        endrow = self.getLastRow() - 1
        newlist = self.get_cell_range(27, 0, 27, endrow)

        flat_list = []
        res = []

        for sublist in newlist :
            for item in sublist:
                if type(item) == float :
                    flat_list.append(item)

        result = filter(None, flat_list)

        for i in result :
            res.append([int(i)])

        return res

    # check a list for float type value
    def checkListFloat(self, arList, key = True) :
        result = []
        for _i in arList:
            for _x in _i :
                if self.checkFLoat(_x) :
                    if key :
                        result.append([int(_x)])
                    else :
                        result.append([_x])

        return result


    # check float
    def checkFLoat(self, value) :
        try :
            return value.isdigit()
        except ValueError:
            return False


    # button convert CSV
    def BtnCnv(self) :
        current_dir = os.getcwd()
        # PATH file
        pathXLS = self.lbPath.text()
        resPath, resFilename = os.path.split(os.path.splitext(pathXLS)[0])
        resPathFile = self.CreateDir(current_dir, NEWDIR, resFilename)
        resultPath = Path(os.path.abspath(os.path.join(current_dir, NEWDIR)))

        # make as variabel
        code_store = str(self.cbOutlet.itemData(self.cbOutlet.currentIndex()))
        ponum = self.getPONO()
        responum = ponum[0][0]
        brc = self.getBRC()
        qty = self.getQTY()
        mdl = self.getMDL()

        # prepare write CSV
        with open(resPathFile, "w+") as csv :

            # write first header
            csv.write(HEAD_CODE_STORE + DELIM + HEAD_PO_NO + DELIM + HEAD_BARCODE + DELIM + HEAD_QTY + DELIM + HEAD_MODAL)

            # write new line
            csv.write("\n")

            for br, qt, md in zip(brc, qty, mdl) :
                for resCD, resPO, resBC, resQT, resMD in zip(itertools.repeat(code_store, len(br)), itertools.repeat(responum, len(br)), br, qt, md) :

                    resBC = str(resBC)
                    resQT = str(resQT)
                    resMD = str(resMD)

                    csv.write(resCD+DELIM+resPO+DELIM+resBC+DELIM+resQT+DELIM+resMD+'\n')

            csv.close()

        reply = QMessageBox.information(self, "Information", "Success!", QMessageBox.Ok)

        if reply == QMessageBox.Ok :
            self.open_file(str(resultPath))




if __name__ == '__main__' :
    app = QApplication(sys.argv)

    # create splash screen
    splash_pix = QPixmap(':/resources/unilever_splash.png')

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    splash.setEnabled(False)

    # adding progress bar
    progressBar = QProgressBar(splash)
    progressBar.setMaximum(10)
    progressBar.setGeometry(17, splash_pix.height() - 20, splash_pix.width(), 50)

    splash.show()

    for iSplash in range(1, 11) :
        progressBar.setValue(iSplash)
        t = time.time()
        while time.time() < t + 0.1 :
            app.processEvents()

    time.sleep(1)

    window = mainWindow()
    window.setWindowTitle(appinfo._appname)
    # window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
    # window.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
    window.show()
    splash.finish(window)
    sys.exit(app.exec_())
