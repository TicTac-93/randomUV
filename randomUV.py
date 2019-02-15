# --------------------------------
#   Bake All Anim v1.0.0 Release
# --------------------------------

# Destroys instances of the dialog before recreating it
# This has to go first, before modules are reloaded or the ui var is re-declared.
try:
    ui.close()
except:
    pass

# --------------------
#       Modules
# --------------------

# PySide 2
from PySide2.QtUiTools import QUiLoader
import PySide2.QtWidgets as QtW
from PySide2.QtCore import QFile

# Import PyMXS, MaxPlus, and set up shorthand vars
import pymxs
import MaxPlus

maxscript = MaxPlus.Core.EvalMAXScript

# Misc
import sys
import os


# --------------------
#      UI Class
# --------------------


class UVRandomizerUI(QtW.QDialog):

    def __init__(self, ui_file, pymxs, parent=MaxPlus.GetQMaxMainWindow()):
        """
        The Initialization of the main UI class
        :param ui_file: The path to the .UI file from QDesigner
        :param runtime: The pymxs runtime
        :param parent: The main Max Window
        """
        # Init QtW.QDialog
        super(UVRandomizerUI, self).__init__(parent)

        # ---------------------------------------------------
        #                    Variables
        # ---------------------------------------------------

        self._ui_file_string = ui_file
        self._pymxs = pymxs
        self._parent = parent

        # ---------------------------------------------------
        #                     Main Init
        # ---------------------------------------------------

        # UI Loader

        ui_file = QFile(self._ui_file_string)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self._widget = loader.load(ui_file)

        ui_file.close()

        # Attaches loaded UI to the dialog box

        main_layout = QtW.QVBoxLayout()
        main_layout.addWidget(self._widget)

        self.setLayout(main_layout)

        # Titling

        self._window_title = "UV Randomizer DEV BUILD"
        self.setWindowTitle(self._window_title)

        # ---------------------------------------------------
        #                   Widget Setup
        # ---------------------------------------------------

        # Options
        # Translate / Rotate / Scale
        self._chk_t = self.findChild(QtW.QCheckBox, 'chk_t')
        self._chk_r = self.findChild(QtW.QCheckBox, 'chk_r')
        self._chk_s = self.findChild(QtW.QCheckBox, 'chk_s')
        # Min / Max
        self._spn_t_min = self.findChild(QtW.QDoubleSpinBox, 'spn_t_min')
        self._spn_r_min = self.findChild(QtW.QDoubleSpinBox, 'spn_r_min')
        self._spn_s_min = self.findChild(QtW.QDoubleSpinBox, 'spn_s_min')
        self._spn_t_max = self.findChild(QtW.QDoubleSpinBox, 'spn_t_max')
        self._spn_r_max = self.findChild(QtW.QDoubleSpinBox, 'spn_r_max')
        self._spn_s_max = self.findChild(QtW.QDoubleSpinBox, 'spn_s_max')
        # Increment
        self._spn_t_inc = self.findChild(QtW.QDoubleSpinBox, 'spn_t_inc')
        self._spn_r_inc = self.findChild(QtW.QDoubleSpinBox, 'spn_r_inc')
        self._spn_s_inc = self.findChild(QtW.QDoubleSpinBox, 'spn_s_inc')

        # Randomizer
        self._lbl_status = self.findChild(QtW.QLabel, 'lbl_status')
        self._btn_hold = self.findChild(QtW.QPushButton, 'btn_hold')
        self._btn_randomize = self.findChild(QtW.QPushButton, 'btn_randomize')
        self._bar_progress = self.findChild(QtW.QProgressBar, 'bar_progress')

        # ---------------------------------------------------
        #                Function Connections
        # ---------------------------------------------------

        # ---------------------------------------------------
        #                  Parameter Setup
        # ---------------------------------------------------

        self._options = {}

        # Label color vars
        self._err = "color=#e82309"
        self._wrn = "color=#f7bd0e"
        self._grn = "color=#3cc103"

        # ---------------------------------------------------
        #                   End of Init

    # ---------------------------------------------------
    #                  Private Methods
    # ---------------------------------------------------


# --------------------
#    Dialog Setup
# --------------------

# Path to UI file
_uif = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\randomUV.ui"
_app = MaxPlus.GetQMaxMainWindow()
ui = UVRandomizerUI(_uif, pymxs, _app)

# Punch it
ui.show()

# DEBUG
print "\rTest Version 1"
