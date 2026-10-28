import time

import pywintypes
import win32com.client


class TDTConnection:
    """
    TDevAcc connection to OpenWorkbench, used by the launcher only for
    startup work; the controller makes its own connection afterwards.
    """

    def __init__(self, server="Local", timeout=120, retry=5):
        self.server = server
        self.timeout = timeout  # seconds to wait for the workspace to load
        self.retry = retry      # seconds between connection attempts
        self.tdt = None

    def connect(self):
        """Retry until a device is reported or the timeout runs out."""
        deadline = time.time() + self.timeout
        attempt = 1
        while True:
            msg = self._try_connect()
            if not msg:
                return
            if time.time() > deadline:
                raise RuntimeError(f"Could not connect to OpenWorkbench after "
                                   f"{self.timeout}s: {msg}")
            print(f"[Launcher] Attempt {attempt}: {msg}, "
                  f"trying again in {self.retry}s")
            self.disconnect()
            time.sleep(self.retry)
            attempt += 1

    def _try_connect(self):
        """Return an error message, or '' once the TDT reports a device."""
        try:
            self.tdt = win32com.client.Dispatch("TDevAcc.X")
            if self.tdt.ConnectServer(self.server) != 1:
                return "OpenWorkbench server not answering"
            # ConnectServer can return 1 before the workspace is loaded, so
            # the device name is the real test
            time.sleep(1)
            if not self.tdt.GetDeviceName(0):
                return "no device yet (workspace still loading?)"
        except pywintypes.com_error as e:
            return f"COM error: {e}"
        return ""

    def set_tag(self, tag_path, value):
        # SetTargetVal returns 0 on failure, e.g. a misspelled tag, or the
        # circuit is not loaded because the system is still in Idle
        if not self.tdt.SetTargetVal(tag_path, value):
            raise RuntimeError(f"Could not set {tag_path} = {value}")

    def disconnect(self):
        if self.tdt is not None:
            try:
                self.tdt.CloseConnection()
            except pywintypes.com_error:
                pass
            self.tdt = None
