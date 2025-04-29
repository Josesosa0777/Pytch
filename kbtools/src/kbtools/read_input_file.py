"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' procedure read_input_file - clone of read_input_file.m '''


# python standard imports
import string 


# ============================================================================ 
def read_input_file(Mode, FileName):
  '''
    [out] = read_input_file(Mode,FileName)
    read contents of a text file  
    mode :
     'tag_only' :
         file format : <tag> = <value>
         tags are taken as keys in a directory for output
         if a tag is repeated a list is created

     'list' : each row an entry (comment marked with  # or %) 
              -> return as cell array
           currently not implemented because no use case 
  '''

  # Mode is made non casesensitive
  Mode = Mode.lower()
  
  if 'list' == Mode:
    # currently not implemented because no use case 
    pass

    '''
    fid=fopen(dateiname,'rt');  
    if fid ~= -1
      k=1;
      while ~feof(fid)
        tmp = fgetl(fid);  
        tmp = deblank(tmp);
        if (length(tmp) > 0) & (tmp(1) ~= '#') & (tmp(1) ~= '%')
          out{k} = tmp;
          k=k+1;
        end
      end  
      fclose(fid);
    end
  '''
  
  elif 'tag_only' == Mode:
  
    
    try:

      # ---------------------------------------------------
      # open file and read all lines in that file at once
      lines = open(FileName,'rt').readlines()
      
      # ---------------------------------------------------
      # collect configuration elements in a dictionary
      cfg_dict ={};  
    
      # evaluate each line
      for line in lines:
        #print '<%s>' % line
        if len(line) > 0:
          if line[0] in ('#','%',';'):
            # current line is a comment  
            #print 'comment: <%s>'% line
            pass
          else:  
            parts = string.split(line,'=')
            if len(parts) >= 2:
              tag   = parts[0]
              value = "=".join(parts[1:])
            
              # trim left and right side
              tag = tag.strip()
              value = value.strip()
            
              #print '<%s>=<%s>'%(tag,value)

              if cfg_dict.has_key(tag):
                # tag already exists -> create a list
                if isinstance(cfg_dict[tag], list):
                  # cfg_dict[tag] is already a list -> just append the value
                  cfg_dict[tag].append(value)
                else:
                  # change cfg_dict[tag] to a list
                  cfg_dict[tag] = [cfg_dict[tag], value]
              else:
                # tag is new -> add key to directory
                cfg_dict[tag] = value
      # ---------------------------------------------------
      # return the dictionary with the elements of read file      
      return cfg_dict         

    except:
      return None
  
