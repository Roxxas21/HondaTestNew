import wx

from pydispatch import dispatcher


class HondaECUAppPanel(wx.Panel):

    HONDAECU_FILE_STYLE = wx.FLP_USE_TEXTCTRL | wx.FLP_SMALL

    def __init__(self, parent, appid, appinfo, enablestates, *args, **kwargs):
        wx.Panel.__init__(self, parent.labelbook, *args, **kwargs)
        self.parent = parent
        self.appid = appid
        self.appinfo = appinfo
        self.enablestates = enablestates
        self.Build()
        dispatcher.connect(self.KlineWorkerHandler, signal="KlineWorker", sender=dispatcher.Any)
        dispatcher.connect(self.DeviceHandler, signal="FTDIDevice", sender=dispatcher.Any)
        dispatcher.connect(self.USBErrorHandler, signal="usberror", sender=dispatcher.Any)
        dispatcher.connect(self.USBErrorHandler, signal="ftdierror", sender=dispatcher.Any)

    def USBErrorHandler(self, errno, strerror):
        pass

    def KlineWorkerHandler(self, info, value):
        pass

    def DeviceHandler(self, action, device, config):
        pass

    def Build(self):
        pass
