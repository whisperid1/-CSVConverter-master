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

CODE_STORE = '397760'

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

        if os.path.exists(resPathFile) :
            os.remove(resPathFile)
        else :
            # os.makedirs(os.path.dirname(resPathFile), exist_ok=True)
            distutils.dir_util.mkpath(os.path.dirname(resPathFile))

        return resPathFile


    # Get Barcode
    def getPONO(self) :

        result = self.get_cell_range(0, 5, 0, 5)
        return result

    # Get Barcode
    def getBRC(self) :

        endrow  = self.getLastRow() - 1
        tmp = self.get_cell_range(1, 0, 1, endrow)

        result = self.checkListFloat(tmp)

        return result


    # Get Barcode
    def getQTY(self) :

        endrow = self.getLastRow() - 1
        tmp = self.get_cell_range(6, 0, 6, endrow)

        result = self.checkListFloat(tmp)

        return result


    # Get Barcode
    def getMDL(self) :

        endrow = self.getLastRow() - 1
        tmp = self.get_cell_range(7, 0, 7, endrow)

        result = self.checkListFloat(tmp)

        return result


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
            return float(value).is_integer()
        except ValueError:
            return False


    # format filename
    def format_filename(self, s) :
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in s if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        return filename


    def BtnCnv1(self) :
        x = self.getPONO()
        print(x)
        print(len(x))


    # button convert CSV
    def BtnCnv(self) :
        current_dir = os.getcwd()
        # PATH file
        pathXLS = self.lbPath.text()
        resPath, resFilename = os.path.split(os.path.splitext(pathXLS)[0])
        resPathFile = self.CreateDir(current_dir, NEWDIR, resFilename)
        resultPath = Path(os.path.abspath(os.path.join(current_dir, NEWDIR)))

        # make as variabel
        code_store = CODE_STORE
        ponum = self.getPONO()
        responum = self.format_filename(ponum[0][0])
        brc = self.getBRC()
        qty = self.getQTY()
        mdl = self.getMDL()

        # prepare write CSV
        with open((self.CreateDir(current_dir, NEWDIR, resFilename)), "w+") as csv :

            # write first header
            csv.write(HEAD_CODE_STORE + DELIM + HEAD_PO_NO + DELIM + HEAD_BARCODE + DELIM + HEAD_QTY + DELIM + HEAD_MODAL)

            # write new line
            csv.write("\n")

            for resCD, resPO, resBC, resQT, resMD in zip(itertools.repeat(code_store, len(brc)), itertools.repeat(ponum, len(brc)), brc, qty, mdl) :
                resPO = resPO[0][0]
                resBC = str(resBC[0])
                resQT = str(resQT[0])
                resMD = str(resMD[0])

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
