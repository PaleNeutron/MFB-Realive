"""
This module provides a macOS-specific implementation of the Window Manager using Quartz and AppKit.
It encapsulates calls for macOS window management, including finding game windows and getting
window geometry.

Classes:
- WindowMgrMacOS: A class that extends the base WindowMgr class and implements macOS-specific
  window management functions.

"""
import logging

from modules.platforms.window_managers.base import WindowMgr

log = logging.getLogger(__name__)

try:
    import Quartz
    from AppKit import (
        NSApplication,
        NSApplicationActivateIgnoringOtherApps,
        NSRunningApplication,
        NSWindow,
        NSWorkspace,
    )
    from ApplicationServices import (
        AXUIElementCopyAttributeValue,
        AXUIElementCreateApplication,
        AXUIElementIsAttributeSettable,
        AXUIElementSetAttributeValue,
        AXValueCreate,
        AXValueGetValue,
        kAXValueCGSizeType,
    )
except ImportError:
    log.error("Quartz and/or AppKit not installed. Ensure pyobjc is installed.")


class WindowMgrMacOS(WindowMgr):
    """
    This class provides functionalities to handle windows in macOS systems.
    It extends from the base WindowMgr class and implements macOS-specific methods.
    """

    def __init__(self):
        """Constructor"""
        self._win = None
        self.app: NSRunningApplication = None

    def find_game(self, WINDOW_NAME, *args, **kwargs):
        """
        Searches for the game window named 'WINDOW_NAME' on the screen and makes it active.
        If the game window is not found, prints a message and sets the target window as None.

        Args:
            WINDOW_NAME (str): The name of the game window to search for.

        Returns:
            win: Returns the identified game window if found, else returns None.
        """
        # workspace = NSWorkspace.sharedWorkspace()
        # apps = workspace.runningApplications()

        # for app in apps:
        #     if app.localizedName() == WINDOW_NAME:
        #         # Activate the application to bring it to the foreground
        #         app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
                
        #         # # Iterate over all windows and bring the desired one to the front
        #         for window in app.windows():
        #             if isinstance(window, NSWindow):
        #                 # Bring the window to the front
        #                 window.makeKeyAndOrderFront_(None)
        #                 self._win = window
        #                 break

        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID
        )

        for window_info in window_list:
            kAXErrorSuccess = 0
            owner_name = window_info.get("kCGWindowOwnerName", "")
            if owner_name == WINDOW_NAME:
                pid = window_info.get("kCGWindowOwnerPID")
                self._win = window_info
                # Activate the application to bring it to the foreground
                app = NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
                self.app = app
                self.activate_window()
                x, y, width, height = self.get_window_geometry()
                DEFAULT_WIDTH = 1920
                if abs(width - DEFAULT_WIDTH) > 3:
                    # resize window to 1080p
                    new_width = DEFAULT_WIDTH
                    # new_height = int(1080 * height / width)
                        # Get the accessibility element for the application
                    self.ref = AXUIElementCreateApplication(pid)
                    # Get the list of windows for the application
                    err, ax_windows = AXUIElementCopyAttributeValue(self.ref, "AXWindows", None)
                    if err != kAXErrorSuccess:
                        raise AttributeError(f"Error getting attribute value: {err}")
                    # Get the first window (you may need to adapt this for multiple windows)
                    win_obj = ax_windows[0]
                    attr = "AXSize"
                    err, settable = AXUIElementIsAttributeSettable(win_obj, attr, None)
                    if err != kAXErrorSuccess:
                        raise AttributeError(f"Error getting attribute settable: {err}")

                    if not settable:
                        raise AttributeError(f"Attribute {attr} is not settable")
                    err, origin_val = AXUIElementCopyAttributeValue(win_obj, attr, None)
                    success, cf = AXValueGetValue(origin_val, kAXValueCGSizeType, None)
                    if not success:
                        raise AttributeError(f"Error getting attribute value: {err}")
                    cf.width = new_width
                    # cf.height = new_height
                    new_val = AXValueCreate(kAXValueCGSizeType, cf)
                    err = AXUIElementSetAttributeValue(win_obj, attr, new_val)
                    if err != kAXErrorSuccess:
                        if err == 1:
                            raise ValueError("Invalid value for element attribute")
                        raise AttributeError(f"Error setting attribute value: {err}")
                return window_info

        if self._win is None:
            print(f"No '{WINDOW_NAME}' window found.")
        return None

    def get_window_geometry(self):
        """
        Fetches the window geometry of the target window.

        Returns:
            tuple: A tuple representing the window's geometry (x, y, width, height).
        """
        if self._win is None:
            raise ValueError("No window is currently selected.")

        window = self._win
        bounds = window.get("kCGWindowBounds", {})
        x = bounds.get("X", 0)
        y = bounds.get("Y", 0)
        width = bounds.get("Width", 0)
        height = bounds.get("Height", 0)
        return x, y, width, height
    
    def activate_window(self):
        """
        Activates the target window.
        """
        if self._win is None:
            raise ValueError("No window is currently selected.")
        self.app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)


if __name__ == '__main__':
    mgr = WindowMgrMacOS()
    win = mgr.find_game("MuMu安卓设备")
    print(win)
    print(mgr.get_window_geometry())