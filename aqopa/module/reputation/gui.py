'''
Created on 06-09-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import os
import re
import wx
import wx.animate
import wx.lib.scrolledpanel as scrolled
import wx.lib.delayedresult

from aqopa.model import name_indexes
from aqopa.bin import gui as aqopa_gui
from aqopa.simulator.error import RuntimeException

class SingleVersionPanel(wx.Panel):
    """ 
    Frame presenting results for one simulation.  
    Simulator may be retrived from module, 
    because each module has its own simulator.
    """
    
    def __init__(self, module, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.module = module
        self.versionSimulator = {}

        self.hostChoosePanels       = []  # Panels used to choose hosts for energy consumptions results
        self.checkBoxInformations   = []  # Tuples with host name, and index ranges widget
        self.hostCheckBoxes         = []  # List of checkboxes with hosts names used for hosts' selection

        self.reputationResultsPanel       = None

        #################
        # VERSION BOX
        #################
        
        versionBox = wx.StaticBox(self, label="Version")
        self.versionsList = wx.ComboBox(self, style=wx.TE_READONLY)
        self.versionsList.Bind(wx.EVT_COMBOBOX, self.OnVersionChanged)
        
        versionBoxSizer = wx.StaticBoxSizer(versionBox, wx.VERTICAL)
        versionBoxSizer.Add(self.versionsList, 1, wx.ALL | wx.ALIGN_CENTER, 5)

        ##################################
        # ENERGY CONSUMPTION BOX
        ##################################
        
        self.consumptionsBox = wx.StaticBox(self, label="Reputation results")

        hostsBox, hostsBoxSizer = self._BuildHostsBoxAndSizer()

        reputationBoxSizer = wx.StaticBoxSizer(self.consumptionsBox, wx.VERTICAL)
        reputationHBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        reputationHBoxSizer.Add(hostsBoxSizer, 1, wx.ALL | wx.EXPAND)
        
        self.showReputationBtn = wx.Button(self, label="Show reputation results")
        self.showReputationBtn.Bind(wx.EVT_BUTTON, self.OnShowReputationButtonClicked)
        
        self.reputationResultBox = wx.StaticBox(self, label="Results")
        self.reputationResultBoxSizer = wx.StaticBoxSizer(self.reputationResultBox, wx.VERTICAL)
        
        reputationBoxSizer.Add(reputationHBoxSizer, 0, wx.ALL | wx.EXPAND)
        reputationBoxSizer.Add(self.showReputationBtn, 0, wx.ALL | wx.EXPAND)
        reputationBoxSizer.Add(self.reputationResultBoxSizer, 1, wx.ALL | wx.EXPAND)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(versionBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(reputationBoxSizer, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        
        self.SetVersionsResultsVisibility(False)
        
    #################
    # REACTIONS
    #################
        
    def AddFinishedSimulation(self, simulator):
        """ """
        version = simulator.context.version
        self.versionsList.Append(version.name)
        
        self.versionSimulator[version.name] = simulator
        
    def OnVersionChanged(self, event):
        """ """
        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        
        self._BuildHostsChoosePanel(simulator)
        self.SetVersionsResultsVisibility(True)
        
    def OnShowReputationButtonClicked(self, event):
        """ """
        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        hosts = self._GetSelectedHosts(simulator)
        
        if len(hosts) == 0:
            wx.MessageBox("Please select hosts.", 'Error', wx.OK | wx.ICON_ERROR)
            return

        self.ShowHostsReputation(simulator, hosts)

    def RemoveAllSimulations(self):
        """ """
        self.versionsList.Clear()
        self.versionsList.SetValue("")
        self.versionSimulator = {}

        self.hostChoosePanels = []
        self.checkBoxInformations = {}
        self.hostCheckBoxes = []
        self.hostsBoxSizer.Clear(True)

        self.SetVersionsResultsVisibility(False)

    #################
    # LAYOUT
    #################
    
    def _BuildHostsBoxAndSizer(self):
        """ """
        self.hostsBox = wx.StaticBox(self, label="Host(s)")
        self.hostsBoxSizer = wx.StaticBoxSizer(self.hostsBox, wx.VERTICAL)
        return self.hostsBox, self.hostsBoxSizer
    
    def _BuildHostsChoosePanel(self, simulator):
        """ """
        for p in self.hostChoosePanels:
            p.Destroy()
        self.hostChoosePanels = []
        self.checkBoxInformations = {}
        self.hostCheckBoxes = []
        
        self.hostsBoxSizer.Layout()
        
        hosts = simulator.context.hosts
        hostsIndexes = {} 
        for h in hosts:
            name = h.original_name()
            indexes = name_indexes(h.name)
            index = indexes[0]
            
            if name not in hostsIndexes or index > hostsIndexes[name]:
                hostsIndexes[name] = index
                
        for hostName in hostsIndexes:
            
            panel = wx.Panel(self)
            panelSizer = wx.BoxSizer(wx.HORIZONTAL)
            
            ch = wx.CheckBox(panel, label=hostName, size=(120, 20))
            textCtrl = wx.TextCtrl(panel)
            textCtrl.SetValue("0")
            
            rangeLabel = "Available range: 0"
            if hostsIndexes[hostName] > 0:
                rangeLabel += " - %d" % hostsIndexes[hostName] 
            maxLbl = wx.StaticText(panel, label=rangeLabel)
            
            panelSizer.Add(ch, 0, wx.ALL | wx.ALIGN_CENTER)
            panelSizer.Add(textCtrl, 0, wx.ALL | wx.ALIGN_CENTER)
            panelSizer.Add(maxLbl, 0, wx.ALL | wx.ALIGN_CENTER)
            panel.SetSizer(panelSizer)
            self.hostsBoxSizer.Add(panel, 1, wx.ALL)
            
            self.checkBoxInformations[ch] = (hostName, textCtrl)
            self.hostChoosePanels.append(panel)
            self.hostCheckBoxes.append(ch)
            
        self.hostsBoxSizer.Layout()
        self.Layout()

    def SetVersionsResultsVisibility(self, visible):
        """ """
        widgets = []
        widgets.append(self.consumptionsBox)
        widgets.append(self.hostsBox)
        widgets.append(self.showReputationBtn)
        widgets.append(self.reputationResultBox)
        
        for w in widgets:
            if visible:
                w.Show()
            else:
                w.Hide()
                
        self.Layout()
    
    #################
    # STATISTICS
    #################
        
    def _GetSelectedHosts(self, simulator):
        """ Returns list of hosts selected by user """
        
        def ValidateHostsRange(indexesRange):
            """ """
            return re.match(r'\d(-\d)?(,\d(-\d)?)*', indexesRange)
        
        def GetIndexesFromRange(indexesRange):
            """ Extracts numbers list of hosts from range text """
            indexes = []
            ranges = indexesRange.split(',')
            for r in ranges:
                parts = r.split('-')
                if len(parts) == 1:
                    indexes.append(int(parts[0]))
                else:
                    for i in range(int(parts[0]), int(parts[1])+1):
                        indexes.append(i)
            return indexes
        
        hosts = []
        for ch in self.hostCheckBoxes:
            if not ch.IsChecked():
                continue
            hostName, hostRangeTextCtrl = self.checkBoxInformations[ch]
            indexesRange = hostRangeTextCtrl.GetValue()
            if not ValidateHostsRange(indexesRange):
                wx.MessageBox("Range '%s' for host '%s' is invalid. Valid example: 0,12,20-25,30." 
                              % (indexesRange, hostName), 'Error', wx.OK | wx.ICON_ERROR)
                break
            else:
                indexes = GetIndexesFromRange(indexesRange)
                for h in simulator.context.hosts:
                    hostIndexes = name_indexes(h.name)
                    if h.original_name() == hostName and hostIndexes[0] in indexes:
                        hosts.append(h)
        return hosts
        
    
    def ShowHostsReputation(self, simulator, hosts):
        """ """
        if self.reputationResultsPanel:
            self.reputationResultsPanel.Destroy()
            self.reputationResultsPanel = None
            
        self.reputationResultsPanel = scrolled.ScrolledPanel(self)
        self.reputationResultBoxSizer.Add(self.reputationResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        for h in hosts:
            lblText = "%s: " % (h.name,)
            error = h.get_finish_error()
            if error is not None:
                lblText += " (Not Finished - %s)" % error
            lbl = wx.StaticText(self.reputationResultsPanel, label=lblText)
            sizer.Add(lbl)

            host_vars = self.module.get_host_vars(h)
            for var_name in host_vars:
                lblText = "%s: %s" % (var_name, unicode(host_vars[var_name]))
                lbl = wx.StaticText(self.reputationResultsPanel, label=lblText)
                sizer.Add(lbl)

        self.reputationResultsPanel.SetSizer(sizer)
        self.reputationResultsPanel.SetupScrolling(scroll_x=False)
        self.Layout()
    
class MainResultsNotebook(wx.Notebook):
    """ """
    def __init__(self, module, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)
        
        self.module = module
        
        self.oneVersionTab = SingleVersionPanel(self.module, self)
        self.AddPage(self.oneVersionTab, "Single Version")
        self.oneVersionTab.Layout()
        
    def OnParsedModel(self):
        """ """
        self.oneVersionTab.RemoveAllSimulations()
        
    def OnSimulationFinished(self, simulator):
        """ """
        self.oneVersionTab.AddFinishedSimulation(simulator)
        
    def OnAllSimulationsFinished(self, simulators):
        """ """
        pass
        
class ModuleGui(wx.EvtHandler):
    """
    Class used by GUI version of AQoPA.
    """
    
    def __init__(self, module):
        """ """
        wx.EvtHandler.__init__(self)
        
        self.module = module
        self.mainResultNotebook = None
        
    def get_name(self):
        return "Reputation"
    
    def get_configuration_panel(self, parent):
        """ Returns WX panel with configuration controls. """
        
        panel = wx.Panel(parent)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(panel, label="Module does not need to be configured.") 
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        text = wx.StaticText(panel, label="All result options will be available after results are calculated.")
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        
        panel.SetSizer(sizer)
        return panel
    
    def get_results_panel(self, parent):
        """
        Create main result panel existing from the beginning 
        which will be extended when versions' simulations are finished.
        """
        self.mainResultNotebook = MainResultsNotebook(self.module, parent)
        return self.mainResultNotebook
    
    def on_finished_simulation(self, simulator):
        """ """
        self.mainResultNotebook.OnSimulationFinished(simulator)
    
    def on_finished_all_simulations(self, simulators):
        """ 
        Called once for all simulations after all of them are finished.
        """
        self.mainResultNotebook.OnAllSimulationsFinished(simulators)
        
    def on_parsed_model(self):
        """ """
        self.mainResultNotebook.OnParsedModel()
        
        

        
        
        
        
