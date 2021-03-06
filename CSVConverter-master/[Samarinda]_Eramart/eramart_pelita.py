# -*- coding: utf-8 -*-
# @Author: ichadhr
# @Date:   2018-07-12 13:19:06
# @Last Modified by:   richard.hari@live.com
# @Last Modified time: 2018-10-08 17:21:13

import sys
import time
import os
import eramart_pelita_info as appinfo
import itertools
import string
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from gui import Ui_MainWindow
from pathlib import Path
import xlrd
import distutils.dir_util

# variabel for header CSV
HEAD_CODE_STORE = 'code_store'
HEAD_PO_NO      = 'po_no'
HEAD_BARCODE    = 'barcode'
HEAD_QTY        = 'qty'
HEAD_MODAL      = 'modal_karton'

NEWDIR     = 'CSV-output'
DELIM      = ';'

CODE_STORE = '443222'

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

        else :
            try :
                book = xlrd.open_workbook(pathXLS, ragged_rows=True)
                sheet = book.sheet_by_index(0)

                return sheet

            except xlrd.XLRDError as e:
                msg = "The '.xls' file has been corrupted."
                errorSrv = QMessageBox.critical(self, "Error", msg, QMessageBox.Abort)
                sys.exit(0)


    # create directory if not exist
    def CreateDir(self, cDIR, nDir, filename) :

        resPathFile =  Path(os.path.abspath(os.path.join(cDIR, nDir, "{}.csv".format(filename))))

        if os.path.exists(resPathFile) :
            os.remove(resPathFile)
        else :
            # os.makedirs(os.path.dirname(resPathFile), exist_ok=True)
            distutils.dir_util.mkpath(os.path.dirname(resPathFile))

        return resPathFile


    # open file
    def open_file(self, filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])


    # get cell range
    def get_cell_range(self, start_col, start_row, end_col, end_row):
        sheet = self.funcXLRD()
        return [sheet.row_values(row, start_colx=start_col, end_colx=end_col+1) for row in range(start_row, end_row+1)]


    # get PO Number
    def getPONO(self) :
        result = []
        fr = []

        accepted = ['PO']

        sheet = self.funcXLRD()

        totRow = sheet.nrows - 1

        newlist = self.get_cell_range(2, 0, 2, totRow)

        for sublist in newlist :
            fr.append([el for el in sublist if any(ignore in el for ignore in accepted)])

        for x in fr :
            for k in x :
                if k != "" :
                    result.append(k)

        return result



    # get Barcode
    def getBRC(self) :
        result = []
        fr = []

        rmoving = list(string.ascii_lowercase) + list(string.ascii_uppercase)

        sheet = self.funcXLRD()

        totRow = sheet.nrows - 1

        newlist = self.get_cell_range(1, 0, 1, totRow)

        for sublist in newlist :
            fr.append([el for el in sublist if not any(ignore in el for ignore in rmoving)])

        for x in fr :
            for k in x :
                if k != "" :
                    result.append(k)

        return result


    # get QTY
    def getQTY(self) :
        result = []
        fr = []

        alpha = list(string.ascii_lowercase) + list(string.ascii_uppercase)
        rmoving = ['/'] + alpha

        sheet = self.funcXLRD()

        totRow = sheet.nrows - 1

        newlist = self.get_cell_range(7, 0, 7, totRow)

        for sublist in newlist :
            fr.append([el for el in sublist if not any(ignore in el for ignore in rmoving)])

        for x in fr :
            for k in x :
                if k != "" :
                    result.append(k)

        return result


    # get Modal
    def getMDL(self) :
        result = []
        fr = []

        rmoving = list(string.ascii_lowercase) + list(string.ascii_uppercase)

        sheet = self.funcXLRD()

        totRow = sheet.nrows - 1

        newlist = self.get_cell_range(11, 0, 11, totRow)

        for sublist in newlist :
            fr.append([el for el in sublist if not any(ignore in el for ignore in rmoving)])

        for x in fr :
            for k in x :
                if k != "" :
                    res = str(k).split(',')[0]
                    result.append(res.replace(".", ""))

        return result


    def grouper(self, iterable, n, fillvalue=None) :
        "Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        args = [iter(iterable)] * n
        return itertools.zip_longest(fillvalue=fillvalue, *args)

    # button convert CSV
    def BtnCnv(self) :

        # current dir
        current_dir = os.getcwd()

        resultPath = Path(os.path.abspath(os.path.join(current_dir, NEWDIR)))

        # make as variabel
        ponum = self.getPONO()
        brc = self.getBRC()
        qty = self.getQTY()
        mdl = self.getMDL()

        # cut every 40 item
        brc40 = list(self.grouper(brc, 40))
        qty40 = list(self.grouper(qty, 40))
        mdl40 = list(self.grouper(mdl, 40))

        for x, (tmpBRC, tmpQTY, tmpMDL, tmpPONO) in enumerate(zip(brc40, qty40, mdl40, ponum)) :

            # convert from tuple to list
            tmpBRC = list(tmpBRC)
            tmpQTY = list(tmpQTY)
            tmpMDL = list(tmpMDL)

            # remove None value
            tmpBRC = [i for i in tmpBRC if i is not None]

            filename = tmpPONO.replace("/", "-")

            resPathFile = self.CreateDir(current_dir, NEWDIR, filename)

            # prepare write CSV
            with open(resPathFile, "w+") as csv :

            # write first header
                csv.write(HEAD_CODE_STORE + DELIM + HEAD_PO_NO + DELIM + HEAD_BARCODE + DELIM + HEAD_QTY + DELIM + HEAD_MODAL)

                # write new line
                csv.write("\n")


                for resCD, resBRC, resQTY, resMDL in zip(itertools.repeat(CODE_STORE, len(tmpBRC)), tmpBRC, tmpQTY, tmpMDL) :

                    resQTY = resQTY.strip()

                    csv.write(str(resCD)+DELIM+str(ponum[x])+DELIM+str(resBRC)+DELIM+str(resQTY)+DELIM+str(resMDL)+'\n')

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
