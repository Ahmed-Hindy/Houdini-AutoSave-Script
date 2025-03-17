import logging
from typing import Optional
from PySide2.QtCore import QTimer, QThread
from PySide2.QtWidgets import QApplication, QMessageBox
import hou



class AutosaveManager:
    """
    A manager class for handling Houdini autosave functionality.
    """

    def __init__(self):
        # initialize logger
        self.logger = logging.getLogger('houdini_logger')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.debug("Autosave plugin loaded")

        # default variables:
        self.autosave_session_mute: bool = False
        self.autosave_timer: Optional[QTimer] = None
        self.autosave_msg: Optional[QMessageBox] = None
        self.autosave_interval = 0.2  # minutes


    def autosave_enabled(self):
        """
        Checks if autosave is enabled in the hipfile.

        Returns:
            bool: True if autosave is enabled, False otherwise.
        """
        result = hou.hscript("autosave")[0]
        return result == "autosave on\n"
    

    def save_scene(self):
        """
        Saves the current Houdini scene.

        Returns:
            bool: True if the scene was saved successfully, False otherwise.
        """
        try:
            hou.hipFile.save()
            self.logger.info("Scene saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving scene: {e}")
            return False
        

    def should_autosave_timer_run(self):
        """
        Determines whether the autosave timer should run.

        Returns:
            bool: True if the autosave timer should start, False otherwise.
        """
        if self.autosave_session_mute:
            self.logger.debug("Autosave session is muted")
            return False

        qapp = QApplication.instance()
        is_gui_thread = False
        if qapp is not None and qapp.thread() == QThread.currentThread():
            is_gui_thread = True
        return is_gui_thread
    

    def is_autosave_timer_active(self):
        """
        Checks if the autosave timer is active.

        Returns:
            bool: True if the autosave timer is active, False otherwise.
        """
        return self.autosave_timer is not None and self.autosave_timer.isActive()
    

    def start_autosave_timer(self, quit: bool = False):
        """
        Starts the autosave timer or stops it if required.

        Args:
            quit (bool, optional): If True, stops the timer without restarting. Defaults to False.
        """
        if self.is_autosave_timer_active():
            self.autosave_timer.stop()
            if self.autosave_msg:
                self.autosave_msg.close()

        if quit:
            self.logger.info("Quitting autosave timer")
            return

        if not self.should_autosave_timer_run():
            return

        try:
            self.autosave_interval = float(self.autosave_interval)
        except ValueError:
            self.logger.warning(f"Invalid autosave interval: {self.autosave_interval}")

        self.autosave_timer = QTimer()
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self.check_autosave)
        self.autosave_timer.start(int(self.autosave_interval * 60 * 1000))
        self.logger.debug(f"Started autosave timer: {self.autosave_interval}min")
        

    def check_autosave(self):
        """
        Triggered when the autosave timer fires. If autosave is disabled, prompts the user.
        """
        self.logger.debug("Autosave timer triggered")
        self.logger.debug(f"Autosave enabled: {self.autosave_enabled()}")

        if not self.autosave_enabled():
            self.autosave_msg = QMessageBox()
            self.autosave_msg.setWindowTitle("Autosave")
            self.autosave_msg.setText("Autosave is disabled. Would you like to save now?")
            self.autosave_msg.addButton("Save", QMessageBox.YesRole)
            b_no = self.autosave_msg.addButton("No", QMessageBox.YesRole)
            self.autosave_msg.addButton("No, don't ask again in this session", QMessageBox.YesRole)
            self.autosave_msg.setDefaultButton(b_no)
            self.autosave_msg.setEscapeButton(b_no)

            self.autosave_msg.finished.connect(self.auto_save_done)
            self.autosave_msg.setModal(False)
            self.autosave_msg.show()
            

    def auto_save_done(self, action: int = 2):
        """
        Callback for when the autosave prompt is responded to by the user.

        Args:
            action (int, optional): The default action index. Defaults to 2.
        """
        button = self.autosave_msg.clickedButton() if self.autosave_msg else None
        if button:
            if button.text() == "Save":
                self.save_scene()
            elif button.text() == "No, don't ask again in this session":
                self.autosave_session_mute = True
                self.start_autosave_timer(quit=True)
                return

        self.start_autosave_timer()

    def on_scene_file_saved(self):
        """
        Called after a scene file is saved to restart the autosave timer.
        """
        if self.should_autosave_timer_run():
            self.start_autosave_timer()

    def scene_event_callback(self, event_type: int):
        """
        Houdini event callback that triggers autosave logic after a scene save.

        Args:
            event_type (int): The type of Houdini hipFile event.
        """
        if event_type == hou.hipFileEventType.AfterSave:
            self.on_scene_file_saved()

    def setup(self):
        """
        Sets up the autosave manager by starting the timer and adding the Houdini event callback.
        """
        if self.should_autosave_timer_run():
            self.start_autosave_timer()
        hou.hipFile.addEventCallback(self.scene_event_callback)
        self.logger.debug("Added Houdini hipFile event callback")



# Instantiate and set up the module-level autosave manager
autosave_manager = AutosaveManager()
autosave_manager.setup()





