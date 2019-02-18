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
import random
import math
import os

rand_uniform = random.uniform
radians = math.radians


# --------------------
#      UI Class
# --------------------


class UVRandomizerUI(QtW.QDialog):

    def __init__(self, ui_file, pymxs, parent=MaxPlus.GetQMaxMainWindow()):
        """
        The Initialization of the main UI class
        :param ui_file: The path to the .UI file from QDesigner
        :param pymxs: The pymxs library
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
        self._rt = pymxs.runtime

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

        self._window_title = 'UV Randomizer DEV BUILD'
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
        self._btn_hold.clicked.connect(self.hold)
        self._btn_randomize.clicked.connect(self.randomize)

        # ---------------------------------------------------
        #                  Parameter Setup
        # ---------------------------------------------------

        self._settings = {'translate': False,
                         'rotate': False,
                         'scale': False,
                         't-range': [],
                         'r-range': [],
                         's-range': []}

        self._elements = None
        self._object = None

        # Label color vars
        self._err = '<font color=#e82309>Error:</font>'
        self._wrn = '<font color=#f7bd0e>Warning:</font>'
        self._grn = '<font color=#3cc103>Status:</font>'

        # Status label modes
        self._status = ['%s In Unwrap UVW, select elements to randomize and click Hold Selection.' % self._grn,
                        '%s Set options above, then click Randomize UVs.  This is undo-able.' % self._grn,
                        '%s The current modifier MUST be an Unwrap UVW with some elements selected!' % self._wrn,
                        '%s Holding UV Selection...' % self._grn,
                        '%s Randomizing UVs...' % self._grn,
                        '%s See Max Listener for details' % self._err]
        # Set initial status label
        self._lbl_status.setText(self._status[0])

        # ---------------------------------------------------
        #                   End of Init

    # ---------------------------------------------------
    #                  Private Methods
    # ---------------------------------------------------

    def _get_settings(self):
        print '_get_settings()'

        self._settings['translate'] = self._chk_t.isChecked()
        self._settings['rotate'] = self._chk_r.isChecked()
        self._settings['scale'] = self._chk_s.isChecked()
        self._settings['t-range'] = [self._spn_t_min.value(),
                                     self._spn_t_max.value(),
                                     self._spn_t_inc.value()]
        self._settings['r-range'] = [self._spn_r_min.value(),
                                     self._spn_r_max.value(),
                                     self._spn_r_inc.value()]
        self._settings['s-range'] = [self._spn_s_min.value(),
                                     self._spn_s_max.value(),
                                     self._spn_s_inc.value()]

    # def _rt.b2a(b)  --  Convert Max Bitarray to Array
    maxscript("fn b2a b = (return b as Array)")


    # ---------------------------------------------------
    #                  Public Methods
    # ---------------------------------------------------

    def hold(self):
        rt = self._rt

        # ----------------
        #  Hold selection
        # ----------------
        if self._btn_hold.isChecked():
            try:
                # First, check that the current modifier is an Unwrap_UVW
                # We use rt.classOf() to get the actual MaxScript class
                uv = rt.modPanel.getCurrentObject()
                if rt.classOf(uv) != rt.Unwrap_UVW:
                    self._lbl_status.setText(self._status[2])
                else:
                    self._lbl_status.setText(self._status[3])

                    # Check UVW selection mode - None, Vert, Edge, Face
                    # If it's not None, then convert it to face selection and build an array of unique elements
                    uv_mode = uv.getTVSubObjectMode()
                    if uv_mode == 0:
                        self._lbl_status.setText(self._status[2])
                        return
                    elif uv_mode == 1:
                        uv.expandSelection()  # This lets us get an element with a single vert selection
                        uv.vertToFaceSelect()
                    elif uv_mode == 2:
                        uv.expandSelection()  # This lets us get an element with a single edge selection
                        uv.edgeToFaceSelect()
                    faces = uv.getSelectedFaces()
                    # If the selection is empty, show an error and cancel.  isEmpty is a Max bitarray property
                    if faces.isEmpty:
                        self._lbl_status.setText(self._status[2])
                        return

                    # Initialize progress bar
                    self._bar_progress.setMaximum(len(rt.b2a(faces)))
                    self._bar_progress.setValue(0)

                    # Build an array of unique elements
                    elements = []
                    while not faces.isEmpty:
                        # Convert faces from bitarray to array so we can index it, then back to bitarray to use in selectFaces()
                        uv.selectFaces(rt.bitarray(rt.b2a(faces)[0]))
                        uv.selectElement()
                        element = uv.getSelectedFaces()
                        # Append this element bitarray to our elements list
                        elements.append(element)
                        # Subtract this element from our selected faces list, both bitarrays
                        # This isn't strictly necessary, but should help prevent redundancy.
                        faces = faces - element
                        # Update progress bar - progress is how many faces were removed from the original list
                        self._bar_progress.setValue(self._bar_progress.maximum() - len(rt.b2a(faces)))

                    # Record our array of element bitarrays, as well as the object for sanity checking
                    self._elements = elements
                    self._object = rt.getCurrentSelection()[0]

                    # DEBUG - Re-select all elements
                    elements = rt.bitarray()
                    for e in self._elements:
                        elements = elements + e
                    uv.selectFaces(elements)

                # Update status and max out progress bar
                self._bar_progress.setValue(self._bar_progress.maximum())
                self._lbl_status.setText(self._status[1])

            except Exception as e:
                print e
                self._lbl_status.setText(self._status[5])

        # -------------------
        #  Release selection
        # -------------------
        else:
            self._elements = []
            self._object = None
            self._lbl_status.setText(self._status[0])

    def randomize(self):
        rt = self._rt

        try:
            # Check that the current modifier is an Unwrap_UVW
            # We use rt.classOf() to get the actual MaxScript class
            uv = rt.modPanel.getCurrentObject()
            if rt.classOf(uv) != rt.Unwrap_UVW:
                self._lbl_status.setText(self._status[2])
            else:
                self._lbl_status.setText(self._status[4])

                # Randomize UV transforms
                with self._pymxs.undo(True, 'Randomize UVs'), self._pymxs.redraw(False):

                    # Update settings from GUI
                    self._get_settings()

                    # Copy _elements list and iterate over it
                    elements = self._elements
                    for element in elements:

                        # Select this element and apply selected transforms
                        uv.selectFaces(element)

                        if self._settings['translate']:
                            # Shorthand var
                            t_range = self._settings['t-range']
                            # Generate random numbers in translation range
                            tu = rand_uniform(t_range[0], t_range[1])
                            tv = rand_uniform(t_range[0], t_range[1])
                            # If Increment is not 0, round down to increment using some Modulo math
                            if t_range[2] > 0:
                                tu = tu - (tu % t_range[2])
                                tv = tv - (tv % t_range[2])
                            t_uvw = rt.Point3(tu, tv, 0)
                            uv.moveSelected(t_uvw)
                            print 'Translate %s' % t_uvw

                        if self._settings['rotate']:
                            # Shorthand var
                            r_range = self._settings['r-range']
                            # Generate random numbers in translation range
                            angle = rand_uniform(r_range[0], r_range[1])
                            # If Increment is not 0, round down to increment using some Modulo math
                            if r_range[2] > 0:
                                angle = angle - (angle % r_range[2])
                            # rotateSelectedCenter expects radians
                            angle = radians(angle)
                            uv.rotateSelectedCenter(angle)
                            print 'Rotate %sdeg' % angle

                        if self._settings['scale']:
                            # Shorthand var
                            s_range = self._settings['s-range']
                            # Generate random numbers in translation range
                            scale = rand_uniform(s_range[0], s_range[1])
                            # If Increment is not 0, round down to increment using some Modulo math
                            if s_range[2] > 0:
                                scale = scale - (scale % s_range[2])
                            # scaleSelectedCenter 0-1 == 0-100 percent, so scale these values accordingly
                            scale = scale / 100
                            uv.scaleSelectedCenter(scale, 0)
                            print 'Scale %s' % scale


        except Exception as e:
            print e
            self._lbl_status.setText(self._status[5])


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
print "\rTest Version 35"
