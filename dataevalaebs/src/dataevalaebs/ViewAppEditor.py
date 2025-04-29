import os
import sys
import Tkinter as tk
import tkFileDialog

class cViewAppEditor(tk.Frame):
    def __init__(self,root,functions):
        '''
        ViewAppEditor provides GUI for added functions.
        It can launch functions and appended parameters. While launching it stores the parameters in view_config.xml like this:
        Directory: params
        key: example_function.py_paramName
        It also drops params into console application as sys.argv=[example_function.py key value key value key value....]
        '''
        self.root=root
        tk.Frame.__init__(self, root)
        self.Frame = tk.Frame(root)
        self.Frame.pack()
        ButtonWidth = 20
        
        
        self.classes=["search","analyze","view"]
        """
        type: list
        substrings, to be searched for as ScriptClassification
        """
        self.launchfunctions={"search.py":["search"],"analyze.py":["analyze"]}
        """
        type: dict
        launchfunctions (keys) with substring (values) to attach functions as Checkbox-params to launchfunction.
        Provides multilaunching Scripts.
        In console application, only CheckboxNames are dropped as sys.argv
        """
        self.cl={}
        """
        type: dict
        key: function, vlaue: class of function depending on found substrings
        """
        functions.sort()
        self.InitialDir = os.curdir
        self.ConfigFile = os.path.join(self.InitialDir,"SAGUI_config.xml")
        """
        type: string
        full path of .\view_config.xml file
        """
        self.LastPath = ""
        """
        type: string
        Last Directory opened by user
        """
        self.params={}
        """
        type: dict
        stored params of each function, keys: function, vlaue: dict of params as keys with values
        """
        self.functions=[]
        """
        type: list
        attached functions
        """
        self.descriptions={}
        """
        type: dict
        dict of function descriptions, key: function, value: string
        """
        self.filetypes={}
        """
        type: dict
        key: function, value: list of tuples (ExtensionName <string>, Extension <string>)
        For exploring files with Open-Button
        """
        self.checkbox={}
        """
        type: dict
        key: function, value <string>: "True" means that params are displayed as Checkbox, ParamValues in [0,1]!
        """
        self.LastXML = ""
        """
        type: string
        last path of the XML-File
        """
        
        for function, Params in functions:
            self.loadFunction(function, **Params)
        self.add_search_analyse_params()
        
        
        #print self.functions, self.descriptions,self.typefiles
        self.actual_function = tk.StringVar(root)
        self.dropdownlist = tk.OptionMenu(root, self.actual_function, *self.functions)
        self.actual_function.set(self.functions[0])
        self.actual_function.trace('w', self.refresh)
        act_Func=self.actual_function.get()
        self.dropdownlist.pack()
        self.description_label = tk.Label(root, text="%s:\n%s"%(act_Func,self.descriptions[act_Func]),wraplength=200)
        self.description_label.pack()
        self.run = tk.Button(root, text="Run", command=self.run, width=ButtonWidth)
        self.run.pack()
        self.save = tk.Button(root, text="Save", command=self.saveConfig, width=ButtonWidth)
        self.save.pack()
        self.BrowseMDF = tk.Button(root, text="Open MDF", command=self.pressBrowseMDF, width=ButtonWidth)
        self.BrowseMDF.pack()
        self.BrowseDirectory = tk.Button(root, text="Open Directory", command=self.pressBrowseDirectory, width=ButtonWidth)
        self.BrowseDirectory.pack()
        self.label = tk.Label(root, text="Copy MDF- or Directory-Path here:")
        self.label.pack()
        self.textbox = tk.Text(root, width=25, height=6, bg='white', borderwidth=4 )
        self.textbox.pack()
        self.BrowseXML = tk.Button(root, text="Open XML", command=self.pressBrowseXML, width=ButtonWidth)
        self.BrowseXML.pack()
        self.XMLbox = tk.Text(root, width=25, height=2, bg='gray', borderwidth=4 )
        self.XMLbox.pack()
        self.Paramwidget=tk.Label(self.root, text='')
        self.Paramwidget.pack()
        
        
        self.entry_labels=[]
        """
        type: list
        labels subscribing entrys
        """
        self.entrys=[]
        """
        type: list
        list of entrys initialized to display function parameters
        """
        self.checkboxes=[]
        """
        type: list
        list of checkboxes initialized to display function parameters
        """
        
        self.refresh()
        """
        type: function
        called at each change of DropDownlist, to refresh Description label, function-params etc.
        """
        
        
    def checkclass(self, Function):
        '''
        Trys to seperate attached functions into classes by searching for substrings
        '''
        if Function in self.launchfunctions.keys():
            self.cl[Function]="launcher"
        else:
          for cl in self.classes:
            if cl in Function:
               self.cl[Function]=cl
          if not Function in self.cl.keys():
            self.cl[Function]="unknown"

    def refresh(self, name="", index=0, mode=None):
        '''
        refreshes Description label and function parameters etc.
        '''
        self.delEntrys()
        self.delCheckboxes()
        self.act_Func=self.actual_function.get()
        self.description_label.config(text="class:%s\n\nDescription (%s):\n\n%s\n\n"%(self.cl[self.act_Func],self.act_Func,self.descriptions[self.act_Func]))
        self.textbox.delete(1.0, tk.END)
        self.textbox.insert(tk.END, self.LastPath)
        self.XMLbox.delete(1.0, tk.END)
        self.XMLbox.insert(tk.END, self.LastXML)
        if self.checkbox[self.act_Func]=="False":
            self.packEntrys()
        elif self.checkbox[self.act_Func]=="True":
            self.packCheckboxes()
        else:
            pass
    
    def checkEntrysandCheckboxes(self):
        '''
        makes update of ViewAppEditor internal function-parameter-values and the user input on GUI
        '''
        if self.checkbox[self.act_Func]=="False":
            for x in xrange(len(self.entrys)):
                self.params[self.act_Func][self.entry_labels[x].text.get()]=self.entrys[x].get()
        elif self.checkbox[self.act_Func]=="True":
            for x in xrange(len(self.checkboxes)):
                self.params[self.act_Func][self.checkboxes[x].text.get()]=self.checkboxes[x].value.get()
        else:
          pass
    def delEntrys(self):
        '''
        deletes all Entrys and Entry_labels
        '''
        for entry in self.entrys:
            entry.destroy()
        for label in self.entry_labels:
            label.destroy()
        del self.entrys[:]
        del self.entry_labels[:]
        
    def packEntrys(self):
        '''
        packs all function parameters as entrys
        '''
        tk.Label(self.Paramwidget, text='\n~~~~~~~~~~~~~~\n').grid(row=0,columnspan=2)
        i=1
        for key, value in self.params[self.act_Func].iteritems():
            text = tk.StringVar()
            text.set(key)
            label = tk.Label(self.Paramwidget, textvariable=text)
            label.text=text
            label.grid(row=i, column=0)
            
            v = tk.StringVar()
            v.set(value)
            entry = tk.Entry(self.Paramwidget, textvariable=v)
            entry.grid(row=i, column=1)
            self.entrys.append(entry)
            self.entry_labels.append(label)
            i+=1
            
    
    def delCheckboxes(self):
        '''
        deletes all Checkboxes
        '''
        for checkbox in self.checkboxes:
            checkbox.destroy()
        del self.checkboxes[:]
    
    def packCheckboxes(self):
        '''
        packs all function parameters as checkboxes
        '''
        tk.Label(self.Paramwidget, text='\n~~~~~~~~~~~~~~\n').grid(row=0,columnspan=2)
        i=0
        
        for key, value in self.params[self.act_Func].iteritems():
            i+=1
            textvar = tk.StringVar()
            textvar.set(key)
            var = tk.IntVar()
            var.set(value)
            c = tk.Checkbutton(self.Paramwidget, textvariable=textvar, variable=var)
            c.value=var
            c.text=textvar
            if int(value)==0:
               c.deselect()
            else:
               c.select()
            c.grid(row=i, sticky=tk.W)
            self.checkboxes.append(c)
    
    
    def loadFunction(self, Function, Description=None, filetypes=[("MDF-files","*.mdf")], checkbox="False",params={}):
        '''
        loads all function info into internal variables and calls "loadConfig" to refresh values to last run parameterset
        '''
        self.functions.append(Function)
        self.descriptions[Function]=Description
        self.filetypes[Function]=filetypes
        self.checkbox[Function]=checkbox
        self.params[Function]={}
        for key, value in params.iteritems():
            self.params[Function][key]=value
        self.checkclass(Function)
        
        
        self.loadConfig(Function)
    
    def add_search_analyse_params(self):
        '''
        searches for launchfunctions specified at startup
        Adds all function as checkbox-parameter to function, that have specific substrings
        '''
        #append other functions as params for search/analyze function
        for key, values in self.launchfunctions.iteritems():
            for func in self.functions:
                if func==key:
                   self.checkbox[func]="True"
                   for function in self.functions:
                      for value in values:
                        if value in function:
                          if function!=key:
                            self.params[func][function]=0
    
    def loadConfig(self, Function):
        '''
        updates internal function-parameters to last run parameterset
        '''
        import xml.dom.minidom
        if os.path.exists(self.ConfigFile):
              Config = xml.dom.minidom.parse(self.ConfigFile)
              Directories, = Config.getElementsByTagName('Params')
              for key in self.params[Function].iterkeys():
                try:
                  self.params[Function][key]= Directories.getAttribute('%s_%s'%(Function, key))
                except ValueError:
                  pass
              try:
                self.LastPath = Directories.getAttribute('LastPath')
              except ValueError:
                pass
              try:
                self.LastXML = Directories.getAttribute('LastXML')
              except ValueError:
                pass
              
    
    def pressBrowseMDF(self):
        '''
        Called if OpenMDF Button is pressed
        '''
        MeasFile = tkFileDialog.askopenfilename(initialdir=r'\\Strs0003\measure1\DAS\benchmark\2010_10_22_release__AEBS_ACC_for_MAN_v2010-09-21__SchedulingBugfixFix_02', filetypes = self.filetypes[self.act_Func])
        if MeasFile:
            self.textbox.delete(1.0, tk.END)
            self.textbox.insert(tk.END, MeasFile)
    
    def pressBrowseDirectory(self):
        '''
        Called if OpenDirectory Button is pressed
        '''
        MeasFile = tkFileDialog.askdirectory(initialdir=r'\\Strs0003\measure1\DAS\benchmark\2010_10_22_release__AEBS_ACC_for_MAN_v2010-09-21__SchedulingBugfixFix_02')
        if MeasFile:
            self.textbox.delete(1.0, tk.END)
            self.textbox.insert(tk.END, MeasFile)
            
            
    def pressBrowseXML(self):
        '''
        Called if OpenXML Button is pressed
        '''
        XMLFile = tkFileDialog.askopenfilename(initialdir=r'\\Strs0003\measure1\DAS\benchmark\2010_10_22_release__AEBS_ACC_for_MAN_v2010-09-21__SchedulingBugfixFix_02', filetypes = [("XML-Files","*.xml")])
        if XMLFile:
            self.XMLbox.delete(1.0, tk.END)
            self.XMLbox.insert(tk.END, XMLFile)
    
    def prepareString(self, String, mark=True):
        String=String.replace("\n","")
        while String.endswith(" "):
          String = String[:-1]
        while String.startswith(" "):
          String = String[1:]
        if mark:
          String = "\"%s\""%String
        return String
    
    def run(self):
        '''
        run the function/functions
        '''
        self.checkEntrysandCheckboxes()
        MeasFile = self.textbox.get(1.0, tk.END)
        XMLFile = self.XMLbox.get(1.0, tk.END)
        MeasFile = self.prepareString(MeasFile, mark=False)
        XMLFile = self.prepareString(XMLFile, mark=False)
        argv = self.prepareargv()
        if len(MeasFile)>2 and len(XMLFile)>2:
          if "search" in self.act_Func:
            sys.argv.append(MeasFile)
            sys.argv.append(XMLFile)
            if self.act_Func=="search.py":
              for key, value in self.params["search.py"].iteritems():
                if value:
                  sys.argv.append(key.replace(".py",""))
            else:
              sys.argv.append(self.params["search.py"][self.act_Func])
            
          elif "analyze" in self.act_Func:
            sys.argv.append(XMLFile)
            if self.act_Func=="analyze.py":
              for key, value in self.params["analyze.py"].iteritems():
                if value:
                  sys.argv.append(key.replace(".py",""))
            else:
              sys.argv.append(self.params["analyze.py"][self.act_Func])
              
          __import__(self.act_Func.replace(".py",""))
          act_Func = sys.modules[self.act_Func.replace(".py","")]
            
            
        # if len(MeasFile)>2 and len(XMLFile)>2:
           
           # if self.cl[self.act_Func]=="None":
             # Popen = subprocess.Popen('%s %s%s'%(self.act_Func, MeasFile, argv), shell=True )
           # elif self.cl[self.act_Func]=="analyze.py":
               # Popen = subprocess.Popen('analyze.py %s%s'%(XMLFile, argv), shell=True )
           # elif self.cl[self.act_Func]=="search.py":
               # Popen = subprocess.Popen('search.py %s %s%s'%(MeasFile, XMLFile, argv), shell=True )
           # elif self.cl[self.act_Func] in ["launcher","view","unknown"]:
             # Popen = subprocess.Popen('%s %s %s%s'%(self.act_Func, MeasFile, XMLFile,argv), shell=True )
             # #print '\n%s %s %s%s'%(self.act_Func, MeasFile, XMLFile,argv)
           # else:
             # raise Error
             # pass
        else:
           top = tk.Toplevel(self.root)
           top.title("Save")
           msg = tk.Message(top, text="Run:\nPlease enter MDF- or Directory- and XML-Path")
           msg.pack()
           button = tk.Button(top, text="OK", command=top.destroy)
           button.pack()
       
    def prepareargv(self):
        '''
        Prepares sys.argv for console application
        Different classes can prepare different sys.argv.
        '''
        argv=""
        if self.cl[self.act_Func]=="launcher":
            for key in self.params[self.act_Func].iterkeys():
              if self.params[self.act_Func][key]==1:
                argv="%s %s"%(argv,key.replace(".py",""))
        else:
            for key in self.params[self.act_Func].iterkeys():
                argv="%s %s %s"%(argv,key,str(self.params[self.act_Func][key]))
        
        return argv
  
    def saveConfig(self):
        '''
        Called if Run/Save Button is pressed.
        You can Save without running by clearing MDF/Folder-Textbox.
        Saves actual parameterset into Config file.
        '''
        import xml.dom.minidom
        self.checkEntrysandCheckboxes()
        if os.path.exists(self.ConfigFile):
          Config = xml.dom.minidom.parse(self.ConfigFile)
        else:
          Config = xml.dom.minidom.Document()
        try:
            Directories, = Config.getElementsByTagName('Params')
        except ValueError:
            Directories = Config.createElement('Params')
        for function in self.functions:
            for key, value in self.params[function].iteritems():
                Directories.setAttribute('%s_%s'%(function,key), str(value))
        Config.appendChild(Directories)
        MeasFile = self.textbox.get(1.0, tk.END)
        if len(MeasFile)>2:
            Directories.setAttribute('LastPath', MeasFile)
        XMLFile = self.XMLbox.get(1.0, tk.END)
        if len(XMLFile)>2:
            Directories.setAttribute('LastXML', XMLFile)
        ViewConfigXml = Config.toprettyxml()
        open(self.ConfigFile, 'w').write(ViewConfigXml)
        
        top = tk.Toplevel(self.root)
        top.title("Save")
        msg = tk.Message(top, text="Saved to %s"%self.ConfigFile)
        msg.pack()
        button = tk.Button(top, text="OK", command=top.destroy)
        button.pack()
        pass

    
def test():

    root=tk.Tk()
    root.title("testGUI")
    SyncAppEditor = ctestviewer(root)
    SyncAppEditor.pack(side=tk.LEFT)
    root.mainloop()
    #SyncAppEditor.__del__()
    
if __name__=="__main__":
    
    test()