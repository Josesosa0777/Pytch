import patterns


def merge_multiline_strings(original_lines):
    in_multiline = False
    filtered_lines = []
    for line in original_lines:
        if not in_multiline:
            if line.count('"') & 1:  # true when odd
                in_multiline = True
            filtered_lines.append(line)
        else:
            filtered_lines[-1] += line
            if line.count('"') & 1:  # true when odd
                in_multiline = False
    return filtered_lines

def remove_blank_lines(original_lines):
    filtered_lines = []
    for line in original_lines:
        blank_line_mo = patterns.blank_line.match(line)
        if blank_line_mo is None:  # not a blank line
            filtered_lines.append(line)
    return filtered_lines

def byteorder_dbc2py(bo):
    if bo == 1: return 'intel'
    elif bo == 0: return 'motorola'
    else: raise TypeError('invalid byteorder value: {} [0|1]'.format(bo))

def byteorder_py2dbc(bo):
    if bo == 'intel': return 1
    elif bo == 'motorola': return 0
    else: raise TypeError('invalid byteorder string: {} ["intel"|"motorola"]'.format(bo))

def sigtype_dbc2py(st):
    if st == '+': return 'unsigned'
    elif st == '-': return 'signed'
    elif st == 1: return 'float'
    elif st == 2: return 'double'
    else:
        print type(st), st
        raise TypeError('invalid sigtype value: {} ["+"|"-"|1|2]'.format(st))

def sigtype_py2dbc(st):
    if st == 'unsigned': return '+'
    elif st == 'signed': return '-'
    elif st == 'float': return 1
    elif st == 'double': return 2
    else: raise TypeError('invalid sigtype string: {} ["unsigned"|"signed"|"float"|"double"]'.format(st))
