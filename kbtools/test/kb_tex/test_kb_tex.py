"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\kb_tex.py
'''

import unittest

import kbtools
import numpy as np
import matplotlib.pyplot as pl


#========================================================================================
class TestSequenceFunctions(unittest.TestCase):


  #------------------------------------------------------------------------  
  def test_TC001(self): 
    ''' default init '''
    
    try:
      my_kb_tex = kbtools.cKB_TEX()
      d = {}
      my_kb_tex.init(d)
      self.assertTrue(True)
    except:
      self.assertTrue(False)

  #------------------------------------------------------------------------  
  def test_TC002(self): 
    ''' standard use case '''
    
    try:
      my_kb_tex = kbtools.cKB_TEX()

      #-----------------------------------------------
      # Step1 : Setting for the report

      # init 
      d = {}
      d["Folder"]     = 'my_report'  # directory, in which the report will be generated 
      d["ReportName"] = 'report_01'  # filename of the report
      d["Titel"]      = 'Big Spam'   # title of the report, upper line
      d["SubTitel"]   = 'Small Egg'  # title of the report, lower line
      d["Author"]     = 'Spam'       # title of the report, lower line
      d["Department"] = 'Egg'        # title of the report, lower line
    
      #print d
      my_kb_tex.init(d)

      # start of document
      # preface of the document
      preface = {}
      preface['title']             = 'Here you insert the Title of the Test Report'
      preface['project']           = 'Here you insert the Name of the Project'
      preface['objective']         = 'Here you insert your Objective'
      preface['tested_by']         = 'Here you insert your Name'
      preface['released_by']       = 'Here you insert the Name of your boss'
      preface['distribution_list'] = 'Here you insert the Name of the recipients'
      #print preface
      my_kb_tex.start(preface)

      #-----------------------------
      # step2: layout of the report

      # sequence important !!!

      # introduction
      my_kb_tex.tex_main('\n\\input{intro.tex}\n')

      # summary
      my_kb_tex.tex_main('\n\\input{summary.tex}\n')

      # examples 
      my_kb_tex.tex_main('\n\\input{my_examples.tex}\n')

      #-----------------------------
      # step3: filling the report 

      # introduction  
      # first select the working file
      my_kb_tex.workingfile('intro.tex')
  
      # then all output is written to 'intro.tex'
      my_kb_tex.tex('\n\\section{Introduction}')     # This is an section heading
      my_kb_tex.tex('\nThis document is about ...')

      my_kb_tex.tex('\n\\subsection{A Subsection}')
      my_kb_tex.tex('\nThis is a subsection...')

      my_kb_tex.tex('\n\\subsubsection{A Subsubection}')
      my_kb_tex.tex('\nThis is a subsubsection...')

      my_kb_tex.tex('\n\\paragraph{A Paragraph}')
      my_kb_tex.tex('\nThis is a paragraph...')


      # summary 
      # first select the working file
      my_kb_tex.workingfile('summary.tex')
      # then all output is written to 'summary.tex'
      my_kb_tex.tex('\n\n\\newpage')
      my_kb_tex.tex('\n\\section{Summary}')
      my_kb_tex.tex('\nYou should have learnt the basic elements of kb\\_tex')

      # my examples
      # first select the working file
      my_kb_tex.workingfile('my_examples.tex')
      # then all output is written to 'my_examples.tex'
      my_kb_tex.tex('\n\n\\newpage')
      my_kb_tex.tex('\n\\section{My Examples}')

      #====================================================
      #
      # examples for fill in elements
      # 

      #----------------------------------------------------
      # a) writing text 

      # headline 
      headline = 'versuch_1_2_3'   # contains understores
      my_kb_tex.tex('\n')
      my_kb_tex.tex('\n\\newpage')
      my_kb_tex.tex('\n\\subsection{%s}' % my_kb_tex.esc_bl(headline))    
      # esc_bl makes _ into \_ (important for tex)


      #----------------------------------------------------
      # b) including a plot

      # create a Matplotlib figure  
      N=1000; 
      t_abst = 0.001;

      # create time axis
      t = np.arange(0., N*t_abst, t_abst)
    
      # create sin and cos
      f0=5;
      y1 = np.sin(2*np.pi*f0*t)
      y2 = np.cos(2*np.pi*f0*t)

      FigNr = 1

      f=pl.figure(FigNr)
      f.suptitle('Matplotlib Example')

      sp=f.add_subplot(211)
      sp.grid()
      sp.plot(t,y1)
      sp.set_title('sin')

      sp=f.add_subplot(212)
      sp.grid()
      sp.plot(t,y2)
      sp.set_title('cos')

      #f.show()
  

      # and add it as a Postscript to the report  
      caption = 'This is the caption for the figure'
      label = my_kb_tex.epsfig(f, '%s' % my_kb_tex.esc_bl(caption) );


      #---------------------------------------------------
      # c) creating a table in summary 

      # heading
      table_array = []
      table_array.append(['first column',    'second column',     'third column'])
      table_array.append(['first row left',  'first row middle',  'first row right'])
      table_array.append(['second row left', 'second row middle', 'second row right'])
      table_array.append(['third row left',  'third row middle',  'third row right'])
    
      # select working file
      my_kb_tex.workingfile('summary.tex')
      label = my_kb_tex.table(table_array,1)
  
      # ------------------------------------------
      # last step: close report and generate pdf
      my_kb_tex.finish()
      my_kb_tex.gen()

      self.assertTrue(True)
    except:
      self.assertTrue(False)



#============================================================================================
# main
#============================================================================================
if __name__ == "__main__":
  print 'unittest for kb_tex'
  unittest.main()



  
