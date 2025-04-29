"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' Class cKB_TEX - clone of kb_tex.m '''


# python standard imports
import os
import shutil
import subprocess

# Utilities_DAS specific imports
import kbtools

# ============================================================================ 
class cKB_TEX:

  def __init__(self):
    self.cfg = {}

    # enable kb_tex
    self.enable = 0
    self.init_with_default_values()


  # ------------------------------------------------
  # interface
  
  def init(self,d):                       #  create report folder
    self.enable = 1 
    self.apply_config(d)
    self.Init_Tex_Verzeichnis()
    
  def start(self,preface):                #  start tex document
    if self.enable:
      self.Start_Tex_Document(preface)

  def workingfile(self,filename):         # change working file 
    self.working_file = filename

  def tex_main(self,txt):                 # Write Tex Text to Main document
    if self.enable:
      self.write_tex('main',txt)
    
  def tex(self,txt):                      # Write Tex Text to working document
    if self.enable:
      self.write_tex('tex',txt)

  def epsfig(self,fig,kommentar):         # include figure in eps format - deprecated
    if self.enable:
      return self.local_fig(fig,kommentar,img_format='eps')
    else:
      return None
      
  def fig(self,fig,kommentar,fig_size=[17, 20],img_format='png'):    # include figure in png format
    if self.enable:
      return self.local_fig(fig,kommentar,fig_size=fig_size,img_format=img_format)
    else:
      return None

  def table(self,table_array,opt=1):      # Write table to working document
    if self.enable:
      return self.local_table(table_array,opt)
    else:
      return None

  def finish(self):                       # finish tex document
    if self.enable:
      self.finish_document()
    else:  
      return None

  def gen(self, do_clean_up__f=1):                          # generate tex document
    if self.enable:
      self.generate_document( do_clean_up__f=do_clean_up__f)
      self.enable = 0
    pass

  def esc_bl(self,s):
    # [s] = esc_bl(s)
    # convert understore '_' into  backslash understore '\_'
    # e.g. esc_bl('delta_h') -> 'delta\_h'
    # s_out = strrep(s_in,'_','\_');
    s = s.replace('_','\_')
    return s


  # ============================================================================================  
  # internal usage
  
  # ------------------------------------------------
  def init_with_default_values(self):
    # init with default value     
    self.Folder        = 'report'
    self.ReportName    = 'report'
    self.Author        = 'T/BCD4.1'
    self.Department    = 'T/BCD~4.1'
    self.CoautorI      = ''
    self.TelDurchwahlI = ''
    self.Titel         = 'Title'
    self.TitelI        = 'Subfolder'
    self.dx            = 24 # cm     
    self.dy            = 26 # cm     
    self.dpi           = 100  # dpi
    self.working_file  = 'default.tex'
    self.Origin        = ''
    
    # it is assume that logo and stylefile are in the same folder of kb_tex.py
    tmp_dirname = os.path.dirname(os.path.abspath(__file__))
    self.logo          = os.path.join(tmp_dirname,'kb_tex_logo_default.ps')
    self.stylefile     = os.path.join(tmp_dirname,'kb_tex_stylefile_default.sty')
    
    self.lfd_nr = 1

  # ------------------------------------------------
  def apply_config(self, d):
    self.Folder      = d.get("Folder",     "my_report")
    self.ReportName  = d.get("ReportName", "my_report")
    self.Titel       = d.get("Titel",      "My Title")
    self.TitelI      = d.get("SubTitel",   "My Subtitle")
    self.Author      = d.get("Author",     "Myself")
    self.Department  = d.get("Department", "My Department")
   
  
  #-----------------------------------------------------
  def Init_Tex_Verzeichnis(self):
    ret = 0  # return

    # =============================================
    # 1. Tex-Generation Folder (create new or clean old)
    if not os.path.exists(self.Folder):
      # create Tex-Generation Folder
      os.makedirs(self.Folder)
    else:
      # clean Tex-Generation Folder
      #print "clean Tex-Generation Folder"
      extension_list = ['.tex','.eps','.ps','.aux','.dvi','.bat','.sty','.log','.out','.toc']
      kbtools.delete_files(self.Folder,extension_list)
      
    #=============================================
    # 2.1 create "action.bat"
    #print "create action.bat"
    action_dateiname = os.path.join(self.Folder,'action.bat');
    #print action_dateiname
    fid = open(action_dateiname,'w')
    fid.write('REM Generate Pdf-Document\n')
    fid.write('\ndel "%s.aux" /Q' % self.ReportName)
    fid.write('\ndel "%s.dvi" /Q' % self.ReportName)
    fid.write('\ndel "%s.log" /Q' % self.ReportName)
    fid.write('\ndel "%s.out" /Q' % self.ReportName)
    fid.write('\ndel "%s.pdf" /Q' % self.ReportName)
    fid.write('\ndel "%s.toc" /Q' % self.ReportName)

    #fid.write('\nlatex -quiet "%s"'  % self.ReportName)
    #fid.write('\nlatex -quiet "%s"'  % self.ReportName)
    #fid.write('\nlatex -quiet "%s"'  % self.ReportName)
    #fid.write('\ndvipdfm -p a4 "%s"' % self.ReportName)

    # 2013-09-13: taken over from kb_tex.m because miktex\bin\mgs.exe  Runtime Error R6016 - not enough space for thread data
    fid.write('\nlatex -quiet -interaction=nonstopmode "%s"'  % self.ReportName)
    fid.write('\nlatex -quiet -interaction=nonstopmode "%s"'  % self.ReportName)
    fid.write('\nlatex -quiet -interaction=nonstopmode "%s"'  % self.ReportName)
    fid.write('\ndvips -q -P pdf "%s.dvi"' % self.ReportName)
    fid.write('\ngswin64c -q -sPAPERSIZE=a4 -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile="%s.pdf" -c save pop -f "%s.ps"' %(self.ReportName,self.ReportName))
    
    fid.close()

    #=============================================
    # 2.2 create "_Clean.bat"  
    clean_dateiname = os.path.join(self.Folder,'_Clean.bat');
    #print clean_dateiname
    fid = open(clean_dateiname,'w')
    fid.write('REM Clean up (only Pdf-Document remains)\n');
    fid.write('\ndel "%s" /Q /F' % os.path.basename(self.logo));
    fid.write('\ndel "%s" /Q /F' % os.path.basename(self.stylefile));
    fid.write('\ndel action.bat /Q /F');
    fid.write('\ndel *.tex /Q /F');
    fid.write('\ndel *.eps /Q /F');
    fid.write('\ndel *.ps /Q /F');
    fid.write('\ndel *.aux /Q /F');
    fid.write('\ndel *.dvi /Q /F');
    fid.write('\ndel *.log /Q /F');
    fid.write('\ndel *.out /Q /F');
    fid.write('\ndel *.toc /Q /F');
    fid.write('\ndel *.bb /Q /F');
    fid.write('\ndel *.jpg /Q /F');
    fid.write('\ndel *.png /Q /F');
    fid.write('\ndel _Clean.bat /Q /F');

    fid.close()

    #=============================================
    # 3. Dateien ins Tex-Verzeichnis kopieren 

    #------------------------
    # 3.1 Logo  cfg.logo
    src_file = os.path.abspath(self.logo)
    dst_file = os.path.join(self.Folder,'KB_logo.ps');

    if os.path.isfile(src_file):
      shutil.copyfile(src_file, dst_file)
    else:  
      print 'warning  %s not found ' % src_file

    #------------------------------
    # 3.2 Style-File  cfg.stylefile
    src_file = os.path.abspath(self.stylefile)
    dst_file = os.path.join(self.Folder,os.path.basename(self.stylefile));

    if os.path.isfile(src_file):
      shutil.copyfile(src_file, dst_file)
    else:  
      print 'warning  %s not found ' % src_file


    #=============================================
    # 4. tex master erzeugen  (cfg.ReportName
    report_name_dateiname = os.path.join(self.Folder,self.ReportName + '.tex')
    #print report_name_dateiname
    fid = open(report_name_dateiname,'w')

    fid.write('\\documentclass[10pt,a4paper,fleqn,dvipdfm]{article}');
    fid.write('\n\\usepackage{german}');
    fid.write('\n\\usepackage[dvipdfm]{hyperref}');

    fid.write('\n\\usepackage[dvips]{graphicx}');
    fid.write('\n\\usepackage[usenames,dvipsnames]{color}');

    fid.write('\n\\usepackage{amsmath}');
    fid.write('\n\\usepackage{multicol}');
    fid.write('\n\\usepackage{longtable}');
    fid.write('\n\\usepackage{courier}');

    fid.write('\n\\usepackage[engl,copyright]{%s}' % os.path.splitext(os.path.basename(self.stylefile))[0])
    fid.write('\n%\\usepackage{bibgerm}');
    fid.write('\n\\usepackage{float}');
    fid.write('\n\\usepackage[hang,it]{caption}');
    fid.write('\n\\usepackage{epsfig}');
    fid.write('\n\\usepackage{hyperref}');
    
    fid.write('\n\\usepackage[figuresright]{rotating}');
    
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n\\author{%s}'       % self.Author);
    fid.write('\n\\Abteilung{%s}'    % self.Department);
    fid.write('\n\\CoautorI{%s}'     % self.CoautorI);
    fid.write('\n\\TelDurchwahlI{%s}'% self.TelDurchwahlI);
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n\\Titel{%s}'  % self.Titel);
    fid.write('\n\\TitelI{%s}' % self.TitelI);

    #if isfield(cfg,'Origin') & ~isempty(cfg.Origin)
    #fid.write('\n\\Origin{%s}',cfg.Origin);
    #end  

    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n% Gliederungstiefe im Inhaltsverzeichnis');
    fid.write('\n\\setcounter{tocdepth}{5}');
    fid.write('\n% Gliederunsgtiefe bis zu der die Unterkapitel gezaehlt werden');
    fid.write('\n\\setcounter{secnumdepth}{5}');
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n\\def\\IR{I\\hspace{-0.8ex}R}');
    fid.write('\n\\def\\inR#1{\\in\\IR^{#1}}');
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n\\makeatletter');
    fid.write('\n\\renewcommand\\paragraph{\\@startsection{paragraph}{4}{\\z@}%');
    fid.write('\n                                 {-3.25ex\\@plus -1ex \\@minus -.2ex}%');
    fid.write('\n                                 {1.5ex \\@plus .2ex}%');
    fid.write('\n                                 {\\normalfont\\normalsize\\bfseries}}');
    fid.write('\n\\makeatother');
    fid.write('\n\\setcounter{secnumdepth}{4}');
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n%---------------------------------------------------------------------------');


    
    fid.write('\n\\def\\figurename{Figure}')
    fid.write('\n\\def\\contentsname{\\hypertarget{href:toc}{Contents}}')
    fid.write('\n\\def\\newpageref{\\vfill \\begin{center} \\textit{Navigation: ')
    fid.write('\\hyperlink{href:toc}{Table of contents}\\qquad ')
    fid.write('\\hyperlink{href:sum}{Summary}\\qquad ')
    fid.write('\\hyperlink{href:overview}{Overview}}\\end{center}\\newpage}')
    fid.write('\n\\def\\navigation{\\vfill \\begin{center} \\textit{Navigation:\\qquad ')
    fid.write('\\hyperlink{href:toc}{Table of contents}\\qquad ')
    fid.write('\\hyperlink{href:sum}{Summary}\\qquad ')
    fid.write('\\hyperlink{href:overview}{Overview}}\\end{center} \\vspace{-0.2cm}}')
    fid.write('\n%');
    fid.write('\n%');
    fid.write('\n%');
    fid.write('\n%---------------------------------------------------------------------------');
    fid.write('\n%---------------------------------------------------------------------------');

    fid.close()
    
  #-----------------------------------------------------
  def Start_Tex_Document(self, preface):
    tex_filename = os.path.join(self.Folder,self.ReportName + '.tex')
    #print tex_filename
    fid = open(tex_filename,'a')
    
    fid.write('\n\\begin{document}')

    self.Write_Preface(preface)
    
    # Inhaltsverzeichnis einfuegen 
    fid.write('\n\\tableofcontents');
     
    fid.close()

  #-----------------------------------------------------
  def Write_Preface(self, preface):
    '''
    if ~isempty(preface)
        
      % --------------------------------------------------------------  
      % frontpage   
      % we have a frontpage is preface.frontpage exists and is not empty
      if isfield(preface,'frontpage') & ~isempty(preface.frontpage)
        % we have a frontpage   
        % no header on frontpage 
        fprintf(fid,'\n\\thispagestyle{empty}');
        %
        fprintf(fid,'\n\\input{%s}',preface.frontpage);
        % start a new page 
        fprintf(fid,'\n\\newpage');
        % frontpage has no number
        fprintf(fid,'\n\\setcounter{page}{1} \\renewcommand{\\thepage}{\\arabic{page}}');
      end 
        
      if isfield(preface,'title')
        fprintf(fid,'\n{\\Large \\bf %s}\n\n',preface.title);
      end    
        
      fprintf(fid,'\n \\bigskip \n');
      fprintf(fid,'\n \\bigskip \n');

      %---------------------------------------------
      if ( isfield(preface,'project') ...
         | isfield(preface,'distribution_list') ...
         | isfield(preface,'objective') ...
         | isfield(preface,'tested_by') ...
         | isfield(preface,'released_by') ...
         | isfield(preface,'distribution_list'))
            
        fprintf(fid,'\n\n{\\large');
        fprintf(fid,'\n \\begin{tabular}{ll}');
        if isfield(preface,'project')
          fprintf(fid,'\n                &    \\\\');
          fprintf(fid,'\n{\\bf Project:} & %s \\\\',s2tex(preface.project));
        end    
        if isfield(preface,'objective')
          fprintf(fid,'\n                &    \\\\');
          fprintf(fid,'\n{\\bf Objective:} & %s \\\\',s2tex(preface.objective));
        end    
        if isfield(preface,'tested_by')
          fprintf(fid,'\n                &    \\\\');
          fprintf(fid,'\n{\\bf Tested by:} & %s \\\\',s2tex(preface.tested_by));
        end    
        if isfield(preface,'released_by')
          fprintf(fid,'\n                &    \\\\');
          fprintf(fid,'\n{\\bf Released by:} & %s \\\\',s2tex(preface.released_by));
        end    
        if isfield(preface,'distribution_list')
          fprintf(fid,'\n                &    \\\\');
          fprintf(fid,'\n{\\bf Distribution list:} & %s \\\\',s2tex(preface.distribution_list));
        end    
        fprintf(fid,'\n \\end{tabular}\n');
          
        fprintf(fid,'\n \\bigskip \n');
        fprintf(fid,'\n \\bigskip \n');
        
        % Revision 
        fprintf(fid,'\n {\\bf Revisions:} \n');
       
        fprintf(fid,'\n}\n');  % end \large
        
        fprintf(fid,'\n \\medskip \n');
                
        fprintf(fid,'\n \\begin{tabular}{|c|c|c|c|c|} \\hline'); 
        fprintf(fid,'\n  {\\bf No.} &  {\\bf Date} & {\\bf Name}       & {\\bf Change} & {\\bf Checked by} \\\\\\hline');
        fprintf(fid,'\n     01      &  \\today     & machine generated & initial        &                   \\\\\\hline');
        fprintf(fid,'\n     02      &              & \\hspace{3.4cm}     & \\hspace{5.4cm}  & \\hspace{3.4cm} \\\\\\hline');
        fprintf(fid,'\n \\end{tabular} \n');

        fprintf(fid,'\n \\medskip \n');
        
        fprintf(fid,'\n This document is valid from the date of distribution, old revisions are no longer');
        fprintf(fid,'\n valid and must be identified as invalid');
        
        if isfield(preface,'EDM_link')
            fprintf(fid,'\n \\bigskip \n');
            fprintf(fid,'\n Link for EDM: \\newline \n');
            if strcmp(preface.EDM_link(1:2),'//')
                fprintf(fid,'\n \\href{file:/%s}{%s} \n',preface.EDM_link,s2tex(preface.EDM_link));
            else
                fprintf(fid,'\n \\href{%s}{%s} \n',preface.EDM_link,s2tex(preface.EDM_link));
            end
        end
        if isfield(preface,'document_link')
            fprintf(fid,'\n \\bigskip \n');
            fprintf(fid,'\n Link for Document: \\newline \n');
            if strcmp(preface.document_link(1:2),'//')
                fprintf(fid,'\n \\href{file:/%s}{%s} \n',preface.document_link,s2tex(preface.document_link));
            else
                fprintf(fid,'\n \\href{%s}{%s} \n',preface.document_link,s2tex(preface.document_link));
            end
        end
        if isfield(preface,'DR_link')
            fprintf(fid,'\n \\bigskip \n');
            fprintf(fid,'\n Link for Development Request: \\newline \n');
            if strcmp(preface.DR_link(1:2),'//')
                fprintf(fid,'\n \\href{file:/%s}{%s} \n',preface.DR_link,s2tex(preface.DR_link));
            else
                fprintf(fid,'\n \\href{%s}{%s} \n',preface.DR_link,s2tex(preface.DR_link));
            end
        end
        fprintf(fid,'\n\\newpage');
      end                
    end
    '''      
    pass

  #-----------------------------------------------------
  def write_tex(self, mode, txt):

    if  'main' == mode:
       tex_filename = os.path.join(self.Folder,self.ReportName + '.tex')
    else: # 'tex'  
       tex_filename = os.path.join(self.Folder,self.working_file)

    #print tex_filename
    fid = open(tex_filename,'a')
    fid.write(txt)
    fid.close()

  #-----------------------------------------------------
  def local_fig(self, fig, kommentar, fig_size=[17, 20], img_format='png'):
    #-----------------------------------
    # init return value 
    out1 = [];

    # -----------------------------------------
    # default   
    #fig_size  = [15, 12];
    #fig_size  = [17, 20];
    rename_text = [];
    
    # name of image
    img_name =  'fig%d' % self.lfd_nr
    self.lfd_nr = self.lfd_nr+1;

    
    # -----------------------------------
    # Tex-Figure-Umgebung in Datei cfg.dateiname abspeichern
    tex_filename = os.path.join(self.Folder,self.working_file)
    #print tex_filename
    fid = open(tex_filename,'a')

    fid.write('\n%------------------------------------------------')
    #fid.write('\n%- %s  ' % img_name)
    fid.write('\n\\begin{figure}[H]')
    fid.write('\n  \\begin{center}')

    '''    
    % rename text
    if ~isempty(rename_text)
       for k = 1:length(rename_text)
          if ~isempty(rename_text{k}{1}) && ~isempty(rename_text{k}{2})
             fprintf(fid,'\n    \\psfrag{%s}[c][l]{%s}',...
                     rename_text{k}{1}, rename_text{k}{2});
          end
       end
    end
    kscale = 1.7; % Faktor zum Anpassen des Groessenverhaeltnisses der Grafik zur Schrift
    if (max(size(fig_size)) < 2) | (fig_size(2) <= 0) %,angle=-90
        fprintf(fid,'\n    \\includegraphics[width=%gcm]{%s.eps}',...
                fig_size(1), img_name);
      %eval(sprintf('set(fig_nr, ''PaperSize'', [%g %g]);', kscale * in4(1), kscale * in4(1)));
      x = kscale * fig_size(1);
      y = kscale * fig_size(1);
      set(fig_nr,'PaperSize', [x y]);
    else
      fprintf(fid,'\n    \\includegraphics[width=%gcm,height=%gcm]{%s.eps}',...
              fig_size(1), fig_size(2), img_name);
     %eval(sprintf('set(fig_nr, ''PaperSize'', [%g %g]);', kscale * in4(1), kscale * in4(2)));
      x = kscale * fig_size(1);
      y = kscale * fig_size(2);
      set(fig_nr,'PaperSize', [x y]);
    end
    '''

   
    fid.write('\n    \\includegraphics[width=%gcm,height=%gcm]{%s.%s}' % (fig_size[0], fig_size[1], img_name, img_format))
    fid.write('\n  \\end{center} \\vspace{-0.5cm}');
    fid.write('\n  \\caption{%s \\label{%s}}' %  (kommentar, img_name));
    fid.write('\n\\end{figure}');
    fid.write('\n%------------------------------------------------\n');
    fid.close()

    # -----------------------------------
    # create image   
    dest_filename =  os.path.join(self.Folder, img_name + '.' + img_format)
    
    # enlarge figure image to obtain smaller fonts
    cm2inch = 1/2.54
    factor = 1.7
    fig.set_size_inches(factor*fig_size[0]*cm2inch,factor*fig_size[1]*cm2inch)
    
    # using bbox_inches='tight' and pad_inches=0  
    # I managed to remove most of the padding;  
    # but a small amount still persists 
    # fig.savefig('out.svg', transparent=True, bbox_inches='tight', pad_inches=0) 
    #fig.savefig(dest_filename, transparent=True, bbox_inches='tight', pad_inches=0.1)
    fig.savefig(dest_filename, transparent=True, papertype='a0')
    
    
     
    # -----------------------------------
    # return img_name 
    return img_name;

  
    pass

  #======================================================================================
  def local_table(self,table,opt=1):

    tex_filename = os.path.join(self.Folder,self.working_file)
   
    fid = open(tex_filename,'a')

    # local variables
    nrow = len(table)      # number of rows
    ncol = len(table[0])   # number of columns

    # style parameter - default setting
    tabalignchar = '|l';   # table align character
    lfchar = '\\';         # linefeed character
    lf1char = '\\';        # linefeed character first row     
    before = '';
    after = '';
    headline = 0;
 
    # Tex Text schreiben  
    if 0==opt:
      lfchar = '\\';
      tabalignchar = 'l';
    elif 1==opt:
      before = '\hline';
      after = '\endhead';
      headline = 1;
      lfchar = '\\\\\hline';
      lf1char = '\\\\\hline\hline';
    elif 2==opt:
      lfchar = '\\\\';
    else:
      pass    

    # built longtable parameter  
    tabpar = ''
    for k in xrange(0,ncol):
      tabpar = tabpar + tabalignchar
    tabpar = tabpar + tabalignchar[0]
    
    # table start
    fid.write('\n\\begin{longtable}{%s}' % tabpar);
    fid.write('\n%s\n' % before);

    first = 0
    for col in xrange(0,ncol):
      # print col  
      if 0==first:
        first = 1
      else:  
        fid.write(' & ');
      fid.write(' \\textbf{%s}' % table[0][col]);
    fid.write(' %s\n %s \n'  % (lf1char, after));
         
    for row in xrange(1,nrow):
      first = 0
      for col in xrange(0,ncol):
        if 0==first:
          first = 1
        else:  
          fid.write(' & ');
        fid.write(' %s' % table[row][col])
      fid.write(' %s\n' % lfchar);

    fid.write('\n\\end{longtable}')
    fid.close()

  
  
    '''
   % *******************************************************************
% insert table in Tex Master or normal tex text
%
% kb_tex('table_main');        : no action
% kb_tex('table_main',table);
% kb_tex('table_main',opt,table);
% kb_tex('table_main',table,options...);
% kb_tex('table_main',opt,table,options...);
% or
% kb_tex('table');        : no action
% kb_tex('table',table);
% kb_tex('table',opt,table);
% kb_tex('table',table,options...);
% kb_tex('table',opt,table,options...);
% *******************************************************************
function [out1] = kb_tex_table(mode,filename_cfg,inp_arg) 

  %-----------------------------------
  % init return value 
  out1 = [];

  %-----------------------------------
  % check if first argument is available
  if length(inp_arg) > 0 & ~isempty(inp_arg{1})
    
    % -----------------------------------------
    % different input argument constellations      
    if length(inp_arg) < 2
      opt   = 0;        % default
      table = inp_arg{1};
      options = [];
    elseif isnumeric(inp_arg{1}) 
      opt   = inp_arg{1};
      table = inp_arg{2};
      if length(inp_arg) > 2
        options = inp_arg(3:end);
      else  
        options = [];
      end  
    elseif iscell(inp_arg{1}) 
      opt   = 0;        % default
      table = inp_arg{1};
      options = inp_arg(2:end);
    end 

    % -----------------------------------------
    % Konfigurations-Struktur 'cfg' laden
    load(filename_cfg);
        
    % -----------------------------------------
    % Abspeichern
    if cfg.enable
      % Datei oeffnen zum Anhaengen   
      switch mode
      case 'table_main'    
        fid =fopen(fullfile(cfg.Folder,[cfg.ReportName,'.tex']),'at');
        if fid == -1
          error(sprintf('error open ''%s'',fullfile(cfg.Folder,[cfg.ReportName,'.tex'])))
        end
      case 'table'  
        fid =fopen(fullfile(cfg.Folder,cfg.dateiname),'at');
        if fid == -1
          error(sprintf('error open ''%s'',fullfile(cfg.Folder,cfg.dateiname)))
        end
      end  
      % Befehlscode der Tabelle in String ablegen
      create_tex_table(fid,opt,table,options);
      fclose(fid);
    end
  end 

    '''

    '''
function [] = create_tex_table(fid,opt,table,options)

  % ----------------------------------------------------------------
  % Eingangsparameter pruefen
  if nargin < 1
    error('wrong number of input arguments, at least create_tex_table(''table'', table[, opt])');
  end
  if nargin < 2
    table = opt;
    opt = 0;        % default
  end

  % ----------------------------------------------------------------
  % 'table' muss ein CELL-Array sein !
  if ~iscell(table)
    error('wrong input argument for table (must be cell array): kb_tex(''table'', table[, opt])');
  end

  % ----------------------------------------------------------------
  % Zeilenzahl 'nrow' und Spaltenzahl 'ncol' von 'table' bestimmen
  [nrow, ncol] = size(table);

  % ----------------------------------------------------------------
  % Optionen ueberpruefen  
  Spaltenoption = [];
  if nargin > 2 
    k=1;  
    while (k<=length(options))
      token = options{k};
      value = options{k+1};
      k=k+2;
      switch token
      case 'Spaltenoption'
         Spaltenoption = value; 
      end    
    end
  end
        
 
  
  % ----------------------------------------------------------------
  if (ncol > 0) & (nrow > 0)
    
    tabalignchar = '|l';
    lfchar = '\\';
    lf1char = '\\';
    before = '';
    after = '';
    headline = 0;
 
    % Tex Text schreiben  
    switch opt
    case 0
      lfchar = '\\';
      tabalignchar = 'l';
    case 1
      before = '\hline';
      after = '\endhead';
      headline = 1;
      lfchar = '\\\hline';
      lf1char = '\\\hline\hline';
    case 2
      lfchar = '\\';
    otherwise
    end
    
    % ------------------------------------------------------
    % Spaltenoption
    if isempty(Spaltenoption)
      % Spaltenoption zusammenbauen
      tabpar = tabalignchar;
      for i = 2:ncol
        tabpar = [tabpar, tabalignchar];
      end
      if size(tabalignchar, 2) > 1
        tabpar = [tabpar, tabalignchar(1)];
      end
    else
      % Spalteoption uebernehmen  
      tabpar = Spaltenoption;
    end
    
    % ------------------------------------------------------
    fprintf(fid,'\n\\begin{longtable}{%s}', tabpar);
    fprintf(fid,'\n%s\n',before);
    for ri = 1:nrow
      for ci = 1:ncol
        if ci > 1
          fprintf(fid,' & ');
        end
        if headline & (ri == 1)  % Kopfzeile fett
          fprintf(fid,' \\textbf{%s}', table{ri, ci});
        else
          fprintf(fid,' %s', table{ri, ci});
        end
      end
      if ri == 1
        fprintf(fid,' %s\n %s', lf1char, after);
      else
        if isempty(strfind(table{ri, ci},'cline'))
          fprintf(fid,' %s\n', lfchar);
        end
      end
    end
    
    fprintf(fid,'\n\\end{longtable}');
  end
return
    '''

    pass

  def finish_document(self):
    tex_filename = os.path.join(self.Folder,self.ReportName + '.tex')
    #print tex_filename
    fid = open(tex_filename,'a')
    fid.write('\n\\end{document}')
    fid.close()

  def generate_document(self, do_clean_up__f=1):
    #print 'generate pdf'
     
    # aktuelle Arbeitsverzeichnis merken 
    actual_working_Folder = os.getcwd()
     
    # ins Verzeichnis des Berichts wechseln 
    os.chdir(self.Folder)
     
    # Batchdatei ausfuehren 
    try:
        s = subprocess.call('action.bat')
        print "s", s
    except:
       print "error 'action.bat'"

    # if pdf was successfully created clean up the Folder 
    CleanBatFileName = '_Clean.bat'
    if do_clean_up__f and (s==0):
        print'  -> pdf created ... will clean up Folder'
        try:
            s = subprocess.call(CleanBatFileName)
            #os.remove(CleanBatFileName)
        except:
            print "error %s"%CleanBatFileName
     
    # Zurueckwechseln
    os.chdir(actual_working_Folder);
  
 
  

  #-----------------------------------------------------
  def method1(self):
    print(self.enable)
    print(self.Folder)
    print(self.ReportName)
    pass

