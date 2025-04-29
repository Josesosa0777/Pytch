import measparser
import os

def searchBackup(path):
  for name in os.listdir(path):
    new_path = os.path.join(path, name)
    if os.path.isdir(new_path):
      try:
        renameBackup(new_path)
      except ValueError:
        searchBackup(new_path)
  pass

def renameBackup(path):
  backup = os.path.join(path, 'Devices')
  if os.path.isdir(backup):
    for name in os.listdir(backup):
      old_path = os.path.join(backup, name)
      if os.path.isdir(old_path):
        if '-' in name:
          head = name.replace('(', '')
          head = head.replace(')', '')
          if head == name:
            continue
          split = head.split('-')
          head  = split[0]
          tail  = '-'.join(split[1:])
        elif '(' in name:
          split = name.split('(')
          head  = split[0]
          tail  = ''.join(split[1:])
          tail  = tail.replace(')', '')
          tail  = tail.replace('(', '')
        else:
          split = name.split('_')
          head  = '_'.join(split[:-2])
          tail  = '_'.join(split[-2:])
        tail = tail.replace('_', '-')
        new_name = '%s-%s' %(head, tail) 
        new_path = os.path.join(backup, new_name)
        os.rename(old_path, new_path)
  else:
    raise ValueError
  pass

if __name__ == '__main__':
  import sys
  path = sys.argv[1]
  searchBackup(path)
  pass
