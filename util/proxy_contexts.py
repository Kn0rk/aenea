"""provides proxy contexts for currently active application matching"""

import proxy
import types

try:
  import dragonfly
except ImportError:
  import dragonfly_mock as dragonfly

communications = proxy.communications

class ProxyAppContext(dragonfly.Context):
  """matches based on the properties of the currently active window.
     use subclasses ProxyAppContextOr, ProxyAppContextAnd."""
  def __init__(self,
               window_class = None,
               window_class_name = None,
               max_depth = None,
               visible = None,
               pid = None,
               screen = None,
               desktop = None):
    arguments = []
    if window_class is not None:
      arguments.append("class " + window_class)
    if window_class_name is not None:
      arguments.append("classname " + window_class_name)
    if max_depth is not None:
      arguments.append("maxdepth %i" % int(max_depth))
    if visible is not None:
      arguments.append("onlyvisible")
    if pid is not None:
      arguments.append("pid %i" % int(pid))
    if screen is not None:
      arguments.append("screen %i" % int(screen))
    if desktop is not None:
      arguments.append("desktop %i" % int(desktop))
    dragonfly.Context.__init__(self)
    self._str = "proxy app context"
    self.arguments = ["--%s" % argument for argument in arguments]
    self._custom_parse()

    def _custom_parse(self):
      pass

    def _get_proxy_matches(self):
      with communications as proxy:
        response = proxy.callReadRawCommand("search " + " ".join(self.arguments))
        window_id, window_title = proxy.callGetActiveWindow()
        return ([window_id for window_id in response.split("\n") if window_id.strip()],
                window_id,
                window_title)

  def matches(self, windows_executable, windows_title, windows_handle):
    matching_windows, window_id, window_title = self._get_proxy_matches()
    return window_id is not None and window_id in matching_windows

class ProxyAppContextOr(ProxyAppContext):
  def _custom_parse(self):
    self.arguments.append("--any")

class ProxyAppContextAnd(ProxyAppContext):
  def _custom_parse(self):
    self.arguments.append("--all")

class ProxyAnyWindowActive(dragonfly.Context):
  def __init__(self):
    self._str = "proxy any window open"

  def matches(self, windows_executable, windows_title, windows_handle):
    window_id, window_title = proxy.callGetActiveWindow()
    return window_id is not None

class ProxyNoWindowActive(dragonfly.Context):
  def __init__(self):
    self._str = "proxy no windows open"

  def matches(self, windows_executable, windows_title, windows_handle):
    with communications as proxy:
      window_id, window_title = proxy.callGetActiveWindow()
      return window_id is None
