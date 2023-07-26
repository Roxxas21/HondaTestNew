import os

import wx
from eculib.honda import *

from .base import HondaECUAppPanel


class HondaECUHRCDataSettingsPanel(HondaECUAppPanel):

    def Build(self):
        self.wildcard = "HRC Data Settings File (*.Fsd;*.fsd)|*.Fsd;*.fsd"
        self.byts = None
        self.bootwait = False

        self.outerp = wx.Panel(self)
        self.mainp = wx.Panel(self.outerp)
        self.wfilel = wx.StaticText(self.mainp, label="File")
        self.readfpicker = wx.FilePickerCtrl(self.mainp, wildcard=self.wildcard,
                                             style=wx.FLP_SAVE | self.HONDAECU_FILE_STYLE)
        self.writefpicker = wx.FilePickerCtrl(self.mainp, wildcard=self.wildcard,
                                              style=wx.FLP_OPEN | wx.FLP_FILE_MUST_EXIST | self.HONDAECU_FILE_STYLE)
        self.optsp = wx.Panel(self.mainp)
        self.optsp.SetSizeHints((500, 32))
        self.namel = wx.StaticText(self.optsp, label="Data Name")
        self.name = wx.TextCtrl(self.optsp, size=(200, -1))

        self.gobutton = wx.Button(self.mainp, label="Read")
        self.gobutton.Disable()

        self.optsbox = wx.BoxSizer(wx.HORIZONTAL)
        self.optsbox.Add(self.namel, 0, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)
        self.optsbox.Add(self.name, 0, flag=wx.LEFT, border=5)
        self.optsp.SetSizer(self.optsbox)

        self.fpickerbox = wx.BoxSizer(wx.HORIZONTAL)
        self.fpickerbox.AddSpacer(5)
        self.fpickerbox.Add(self.readfpicker, 1)
        self.fpickerbox.Add(self.writefpicker, 1)

        self.lastpulse = time.time()
        self.progress = wx.Gauge(self.mainp, size=(400, -1), style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        self.progress.SetRange(100)

        self.modebox = wx.RadioBox(self.mainp, label="Mode", choices=["Read", "Write"])

        self.flashpsizer = wx.GridBagSizer()
        self.flashpsizer.Add(self.wfilel, pos=(0, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                             border=10)
        self.flashpsizer.Add(self.fpickerbox, pos=(0, 1), span=(1, 5), flag=wx.EXPAND | wx.RIGHT | wx.BOTTOM, border=10)
        self.flashpsizer.Add(self.optsp, pos=(1, 0), span=(1, 6))
        self.flashpsizer.Add(self.progress, pos=(2, 0), span=(1, 6),
                             flag=wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND | wx.TOP, border=20)
        self.flashpsizer.Add(self.modebox, pos=(3, 0), span=(1, 2), flag=wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.LEFT,
                             border=10)
        self.flashpsizer.Add(self.gobutton, pos=(3, 5), flag=wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.RIGHT, border=10)
        self.flashpsizer.AddGrowableRow(3, 1)
        self.flashpsizer.AddGrowableCol(5, 1)
        self.mainp.SetSizer(self.flashpsizer)

        self.outersizer = wx.BoxSizer(wx.VERTICAL)
        self.outersizer.Add(self.mainp, 1, wx.EXPAND | wx.ALL, border=10)
        self.outerp.SetSizer(self.outersizer)

        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(self.outerp, 1, wx.EXPAND)
        self.SetSizer(self.mainsizer)

        self.readfpicker.Hide()
        # self.mainsizer.Fit(self)
        self.Layout()

        self.OnModeChange(None)

        self.name.Bind(wx.EVT_TEXT, self.OnValidateMode)
        self.readfpicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnValidateMode)
        self.writefpicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnValidateMode)
        self.gobutton.Bind(wx.EVT_BUTTON, self.OnGo)
        self.modebox.Bind(wx.EVT_RADIOBOX, self.OnModeChange)

    def KlineWorkerHandler(self, info, value):
        if info == "state":
            if value == ECUSTATE.OFF:
                if self.bootwait:
                    if self.modebox.GetSelection() == 0:
                        self.parent.powercycle.ShowPowerOn("Preparing to read HRC data settings...")
                    else:
                        self.parent.powercycle.ShowPowerOn("Preparing to write HRC data settings...")
        elif info == "hrc.read.progress":
            if value[0] is not None and value[0] >= 0:
                self.progress.SetValue(value[0])
                print(value[1], 0)
        elif info == "hrc.read.result":
            self.progress.SetValue(0)
            self.parent.powercycle.ShowPowerOff("Read: complete (result=%s)" % value)

    def OnGo(self, _event):
        self.gobutton.Disable()
        self.bootwait = True
        if self.modebox.GetSelection() == 0:
            self.parent.powercycle.ShowPowerOff("Preparing to read HRC data settings...")
            dispatcher.send(signal="HRCSettingsPanel", sender=self, mode="read",
                            data=(self.readfpicker.GetPath(), self.name.GetValue()))
        else:
            self.parent.powercycle.ShowPowerOff("Preparing to write HRC data settings...")
            dispatcher.send(signal="HRCSettingsPanel", sender=self, mode="write", data=None)

    def OnModeChange(self, _event):
        if self.modebox.GetSelection() == 0:
            self.gobutton.SetLabel("Read")
            self.writefpicker.Hide()
            self.readfpicker.Show()
        else:
            self.gobutton.SetLabel("Write")
            self.writefpicker.Show()
            self.readfpicker.Hide()
        self.Layout()

    def OnValidateMode(self, _event):
        if self.modebox.GetSelection() == 0:
            if len(self.readfpicker.GetPath()) > 0 and len(self.name.GetValue()) > 0 and len(
                    self.name.GetValue()) <= 25:
                self.gobutton.Enable()
            else:
                self.gobutton.Disable()
        else:
            if len(self.writefpicker.GetPath()) > 0:
                #fbin = open(self.writefpicker.GetPath(), "rb")
                nbyts = os.path.getsize(self.writefpicker.GetPath())
                print(nbyts)
