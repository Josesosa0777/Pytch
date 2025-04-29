import struct
import xml.dom.minidom
import codecs
from collections import OrderedDict
import re

from iParser import DEVICE_NAME_SEPARATOR

orders = {0: '<', 1: '>', 2: '<', 3: '>', 4: '<', 5: '>', 6: '<'}
formats = {0: 'u', 1: 'u', 2: 'i', 3: 'i', 4: 'f', 5: 'f', 6: 'a'}

union_type = '<u1'

DEVICE_NAME_LIST = ['MFC5xx Device', 'MFC5xx_Device', 'ARS4xx Device', 'SRR520', 'ARS620']


def extract(block, f, link):
    f.seek(link)
    s = f.read(block.size)
    return block.unpack(s)


def write(block, f, link, data):
    s = block.pack(*data)
    f.seek(link)
    f.write(s)
    return


def clean(f, link, empty):
    f.seek(link)
    f.write(empty)
    return


def getBlockType(f, link):
    f.seek(link)
    s = f.read(4)
    return s


def checkBlock(f, link, block_tag):
    return getBlockType(f, link) == block_tag


id_struct = struct.Struct('<8s8s8s4sH')


def extractID(f):
    f.seek(0)
    s = f.read(id_struct.size)

    id_file, \
        id_vers, \
        id_prog, \
        id_reserded1, \
        id_ver = id_struct.unpack(s)
    id_file = id_file.rstrip()
    id_vers = id_vers.rstrip()
    return id_file, \
        id_vers, \
        id_prog, \
        id_ver


hd_struct = struct.Struct('<4s4s2Q6qQ2h4B2d')


def extractHD(f):
    f.seek(64)
    s = f.read(hd_struct.size)

    id_name, \
        reserved, \
        lenght, \
        link_count, \
        hd_dg_first, \
        hd_fh_first, \
        hd_ch_first, \
        hd_at_first, \
        hd_ev_first, \
        hd_md_comment, \
        hd_start_time_ns, \
        hd_tz_offset_min, \
        hd_dst_offset_min, \
        hd_time_flags, \
        hd_time_class, \
        hd_flags, \
        hd_reserved, \
        hd_start_angle_rad, \
        hd_start_distance_m = hd_struct.unpack(s)
    return hd_dg_first, \
        hd_fh_first, \
        hd_ch_first, \
        hd_at_first, \
        hd_ev_first, \
        hd_md_comment, \
        hd_start_time_ns, \
        hd_tz_offset_min, \
        hd_dst_offset_min, \
        hd_time_flags, \
        hd_time_class, \
        hd_flags, \
        hd_start_angle_rad, \
        hd_start_distance_m


dg_struct = struct.Struct('<4s4s2Q4qB7s')


def extractDG(f, link):
    f.seek(link)
    s = f.read(dg_struct.size)

    id_name, \
        reserved, \
        length, \
        link_count, \
        dg_dg_next, \
        dg_cg_first, \
        dg_data, \
        dg_md_comment, \
        dg_rec_id_size, \
        dg_reserved = dg_struct.unpack(s)
    return dg_dg_next, \
        dg_cg_first, \
        dg_data, \
        dg_md_comment, \
        dg_rec_id_size


cg_struct = struct.Struct('<4s4s2Q6q2QH6s2I')


def extractCG(f, link):
    f.seek(link)
    s = f.read(cg_struct.size)

    id_name, \
        reserved, \
        lenght, \
        link_count, \
        cg_cg_next, \
        cg_cn_first, \
        cg_tx_acq_name, \
        cg_si_acq_source, \
        cg_sr_first, \
        cg_md_comment, \
        cg_record_id, \
        cg_cycle_count, \
        cg_flags, \
        cg_reserved, \
        cg_data_bytes, \
        cg_inval_bytes = cg_struct.unpack(s)
    return cg_cg_next, \
        cg_cn_first, \
        cg_tx_acq_name, \
        cg_si_acq_source, \
        cg_sr_first, \
        cg_md_comment, \
        cg_record_id, \
        cg_cycle_count, \
        cg_flags, \
        cg_data_bytes, \
        cg_inval_bytes


cn_struct = struct.Struct('<4s4s2Q8q4B4IB3s6d')


def extractCN(f, link):
    f.seek(link)
    s = f.read(cn_struct.size)

    id_name, \
        reserved, \
        lenght, \
        link_count, \
        cn_cn_next, \
        cn_composition, \
        cn_text_name, \
        cn_si_source, \
        cn_cc_conversion, \
        cn_data, \
        cn_md_unit, \
        cn_md_comment, \
        cn_type, \
        cn_sync_type, \
        cn_data_type, \
        cn_bit_offset, \
        cn_byte_offset, \
        cn_bit_count, \
        cn_flags, \
        cn_inval_bit_pos, \
        cn_precision, \
        cn_reserved, \
        cn_val_range_min, \
        cn_val_range_max, \
        cn_limit_min, \
        cn_limit_max, \
        cn_limit_ext_min, \
        cn_limit_ext_max = cn_struct.unpack(s)
    return cn_cn_next, \
        cn_composition, \
        cn_text_name, \
        cn_si_source, \
        cn_cc_conversion, \
        cn_data, \
        cn_md_unit, \
        cn_md_comment, \
        cn_type, \
        cn_sync_type, \
        cn_data_type, \
        cn_bit_offset, \
        cn_byte_offset, \
        cn_bit_count, \
        cn_flags, \
        cn_inval_bit_pos, \
        cn_precision, \
        cn_val_range_min, \
        cn_val_range_max, \
        cn_limit_min, \
        cn_limit_max, \
        cn_limit_ext_min, \
        cn_limit_ext_max


si_struct = struct.Struct('<4s4s2Q3q3B')


def extractSI(f, link):
    f.seek(link)
    s = f.read(si_struct.size)

    id_name, \
        reserved, \
        length, \
        link_count, \
        si_tx_name, \
        si_tx_path, \
        si_md_comment, \
        si_type, \
        si_bus_type, \
        si_flags = si_struct.unpack(s)
    return si_tx_name, \
        si_tx_path, \
        si_md_comment, \
        si_type, \
        si_bus_type, \
        si_flags


def procSI(f, link):
    si_tx_name, \
        si_tx_path, \
        si_md_comment, \
        si_type, \
        si_bus_type, \
        si_flags = extractSI(f, link)

    name = extractTX(f, si_tx_name)
    path = extractTX(f, si_tx_path)
    return name, \
        path, \
        si_type


struct_head = struct.Struct('<4s4s2Q')
link_str = '<%dq'
cc_data_struct = struct.Struct('<2B3H2d')
cc_val_str = '<%dd'


def extractCC(f, link):
    f.seek(link)
    s = f.read(struct_head.size)

    id_name, \
        reserved, \
        length, \
        link_count = struct_head.unpack(s)

    link_struct = struct.Struct(link_str % link_count)
    s = f.read(link_struct.size)
    links = link_struct.unpack(s)
    cc_tx_name, \
        cc_md_unit, \
        cc_md_comment, \
        cc_cc_inverse = links[:4]
    cc_ref = links[4:]

    s = f.read(cc_data_struct.size)
    cc_type, \
        cc_precision, \
        cc_flags, \
        cc_ref_count, \
        cc_val_count, \
        cc_phy_range_min, \
        cc_phy_range_max = cc_data_struct.unpack(s)

    val_struct = struct.Struct(cc_val_str % cc_val_count)
    s = f.read(val_struct.size)
    cc_val = val_struct.unpack(s)
    return cc_tx_name, \
        cc_md_unit, \
        cc_md_comment, \
        cc_cc_inverse, \
        cc_ref, \
        cc_type, \
        cc_precision, \
        cc_flags, \
        cc_phy_range_min, \
        cc_phy_range_max, \
        cc_val


def procCC(f, link):
    cc_tx_name, \
        cc_md_unit, \
        cc_md_comment, \
        cc_cc_inverse, \
        cc_ref, \
        cc_type, \
        cc_precision, \
        cc_flags, \
        cc_phy_range_min, \
        cc_phy_range_max, \
        cc_val = extractCC(f, link)

    unit = extractTX(f, cc_md_unit)
    return cc_type, \
        cc_val, \
        cc_ref, \
        unit


class Block:
    def __init__(self, block):
        self.block = OrderedDict(block)
        struct_str = self.block.values()
        struct_str.insert(0, '<')
        struct_str = ''.join(struct_str)
        self.struct = struct.Struct(struct_str)
        return

    def extract(self, f, link=None):
        if link is not None:
            f.seek(link)
        s = f.read(self.struct.size)

        block = self.struct.unpack(s)
        block = [item for item in zip(self.block, block)]
        return dict(block)


class RepBlock(Block):
    def __init__(self, tag, rep):
        struct_str = '<%d%s' % (rep, tag)
        self.struct = struct.Struct(struct_str)
        return

    def extract(self, f, link=None):
        if link is not None:
            f.seek(link)
        s = f.read(self.struct.size)
        return self.struct.unpack(s)


head_block = Block([('id', '4s'),
                    ('reserved', '4s'),
                    ('length', 'Q'),
                    ('link_count', 'Q')])

ca_data_block = Block([('ca_type', 'B'),
                       ('ca_storage', 'B'),
                       ('ca_ndim', 'H'),
                       ('ca_flags', 'I'),
                       ('ca_byte_offset_base', 'I'),
                       ('ca_inval_bit_pos_base', 'I')])


def extractCA(f, link):
    head = head_block.extract(f, link)

    link_block = RepBlock('q', head['link_count'])
    links = link_block.extract(f)

    ca = ca_data_block.extract(f)

    block = RepBlock('Q', ca['ca_ndim'])
    ca['ca_dim_size'] = block.extract(f)

    prod_d = calcCaDimProd(ca)
    sum_d = calcCaDimSum(ca)

    if ca['ca_flags'] & 32:
        block = RepBlock('d', sum_d)
        ca['ca_axis_value'] = block.extract(f)
    if ca['ca_storage']:
        block = RepBlock('Q', prod_d)
        ca['ca_cycle_count'] = block.extract(f)

    ca['ca_composition'] = links[0]
    start = 1
    if ca['ca_storage'] == 2:
        end = start + prod_d
        ca['ca_data'] = links[start:end]
        start = end
    if ca['ca_flags'] & 1:
        end = start + 3 * ca['ca_ndim']
        ca['ca_dynamic_size'] = links[start:end]
        start = end
    if ca['ca_flags'] & 2:
        end = start + 3 * ca['ca_ndim']
        ca['ca_input_quantity'] = links[start:end]
        start = end
    if ca['ca_flags'] & 4:
        end = start + 3
        ca['ca_output_quantity'] = links[start:end]
        start = end
    if ca['ca_flags'] & 8:
        end = start + 3
        ca['ca_comparison_quantity'] = links[start:end]
        start = end
    if ca['ca_flags'] & 16:
        end = start + ca['ca_ndim']
        ca['ca_cc_axis_conversion'] = links[start:end]
        start = end
    if ca['ca_flags'] & 16 and not ca['ca_flags'] & 32:
        end = start + 3 * ca['ca_ndim']
        ca['ca_axis'] = links[start:end]
        start = end
    return ca


def calcCaDimSum(ca):
    sum_d = 0
    for size in ca['ca_dim_size']:
        sum_d += size
    return sum_d


def calcCaDimProd(ca):
    prod_d = 1
    for size in ca['ca_dim_size']:
        prod_d *= size
    return prod_d


def extractDT(f, link):
    f.seek(link)
    s = f.read(struct_head.size)

    id_name, reservded, length, link_count = struct_head.unpack(s)
    return link + struct_head.size, length - struct_head.size


dl_data_struct = struct.Struct('<B3sI')
dl_equal_length_struct = struct.Struct('<Q')


def extractDL(f, link):
    f.seek(link)
    s = f.read(struct_head.size)

    id_name, reserved, length, link_count = struct_head.unpack(s)

    links = RepBlock('q', link_count)
    links = links.extract(f)
    dl_dl_next = links[0]
    dl_data = links[1:]

    s = f.read(dl_data_struct.size)

    dl_flags, dl_reversed, dl_count = dl_data_struct.unpack(s)

    dl_count = len(dl_data)
    dl_equal_length_flag = dl_flags & 1
    if dl_equal_length_flag:
        s = f.read(dl_equal_length_struct.size)
        dl_equal_length, = dl_equal_length_struct.unpack(s)
        dl_offset = range(0, dl_count * dl_equal_length, dl_equal_length)
    else:
        dl_offset_struct = RepBlock('Q', dl_count)
        dl_offset = dl_offset_struct.extract(f)
    return dl_dl_next, dl_data, dl_offset


def iterDL(f, link):
    while link:
        link, dl_data, dl_offset = extractDL(f, link)
        for data, offset in zip(dl_data, dl_offset):
            yield data, offset
    return


def iterDT(f, link):
    block_type = getBlockType(f, link)
    if not link:
        yield 0, 0
    elif block_type == '##DT':
        yield extractDT(f, link)
    elif block_type == '##DL':
        prev_dl_offset = None
        for dl_data, dl_offset in iterDL(f, link):
            if dl_data == 0:
                yield 0, 0
            elif checkBlock(f, dl_data, '##DT'):
                dt_data, dt_size = extractDT(f, dl_data)
                if prev_dl_offset is not None:
                    size = min(dt_size, dl_offset - prev_dl_offset)
                    size = max(size, 0)
                else:
                    size = dt_size
                yield dt_data, size
            else:
                raise AssertionError('invalid dl link: %d' % dl_data)
            prev_dl_offset = dl_offset
    else:
        raise AssertionError('invalid link: %d from %s block type'
                             % (link, block_type))
    return


empty_tx = struct_head.pack('\x00\x00\x00\x00',
                            '\x00\x00\x00\x00',
                            0,
                            0)


def extractTX(f, link):
    if link == 0:
        return ''
    f.seek(link)
    s = f.read(struct_head.size)
    id_name, \
        reserved, \
        length, \
        link_count = struct_head.unpack(s)
    if length == 0:
        return ''
    text = struct.Struct('<%ds' % (length - struct_head.size))
    s = f.read(text.size)
    t, = text.unpack(s)
    t = t.decode('utf-8', 'ignore')
    i = t.find('\0')
    if i != -1:
        t = t[:i]
    return t


def clearTX(f, link):
    if link == 0:
        return
    f.seek(link)
    s = f.read(struct_head.size)
    id_name, \
        reserved, \
        length, \
        link_count = struct_head.unpack(s)
    f.write('\x00' * (length - struct_head.size))
    f.seek(link)
    f.write(empty_tx)
    return


def createDevName(cg_tx_acq_name, cg_si_name, cg_si_path, cg_acq_type, cn_si_name, cn_si_path, cn_name):
    name = ''
    if cg_acq_type == 1:
        if bool([True for item in DEVICE_NAME_LIST if item in cn_si_path]):
            index = [m.start() for m in
                     re.finditer(r'\.', cn_name.decode())]
            if bool(index):
                name = cn_name.decode()[:index[2]]
                name = re.split('\[\d+]', name)[0]
            else:
              if cn_name.startswith('MFC5xxDevice') or cn_name.startswith('Axiscamera'):
                cn_si_path = cn_name
              name = cn_si_path
        else:
            if cg_tx_acq_name.startswith('MFC5xxDevice') or cg_tx_acq_name.startswith('Axiscamera'):
              cg_si_path = cg_tx_acq_name
            name = cg_si_path
        ext = cg_tx_acq_name, cg_si_name, cn_si_name, cn_si_path
    elif cg_acq_type == 4:
        name = cn_si_path
        ext = cg_tx_acq_name, cg_si_name, cg_si_path, cn_si_name
    elif cg_acq_type == 2:
        name = cn_si_path + '_' + cg_tx_acq_name
        ext = cg_tx_acq_name, cg_si_name, cg_si_path, cn_si_name
    else:
        name = cg_tx_acq_name
        ext = cg_si_name, cg_si_path, cn_si_name, cn_si_path
    if name == '':
        if bool([True for item in DEVICE_NAME_LIST if item in cn_si_path]):
            index = [m.start() for m in
                     re.finditer(r'\.', cn_name.decode())]
            if bool(index):
                name = cn_name.decode()[:index[2]]
                name = re.split('\[\d+]', name)[0]
            else:
                name = cn_si_path
        else:
            name = 'NULL'
    # elif ' ' in name:
    #   name = name.replace(' ', '_')
    ext = DEVICE_NAME_SEPARATOR.join(ext)
    # name = name.replace(' ', '_')
    # name = name.replace('-','_')
    ext = ext.replace(' ', '_')
    return name, ext


def isMdfSorted(name):
    f = open(name, 'rb')
    is_sorted = False

    dg_link, \
        hd_fh_first, \
        hd_ch_first, \
        hd_at_first, \
        hd_ev_first, \
        hd_md_comment, \
        hd_start_time_ns, \
        hd_tz_offset_min, \
        hd_dst_offset_min, \
        hd_time_flags, \
        hd_time_class, \
        hd_flags, \
        hs_start_angle_rad, \
        hd_start_distance_m = extractHD(f)
    while dg_link:
        dg_link, \
            cg_link, \
            dg_data, \
            dg_md_comment, \
            dg_rec_id_size = extractDG(f, dg_link)
        if dg_rec_id_size != 0:
            break
    else:
        is_sorted = True

    f.close()
    return is_sorted


class ConversionError(BaseException):
    def __init__(self, msg, raw):
        BaseException.__init__(self, msg)
        self.raw = raw
        return

    pass


def convRawPhy(raw, cc_type, cc_val, cc_ref, factor=None, offset=None):
    if cc_type == 0:
        factor = 1 if factor is None else factor
        offset = 0 if offset is None else offset
        phy = raw * factor + offset
    elif cc_type == 1:
        offset_, factor_ = cc_val
        factor = factor_ if factor is None else factor
        offset = offset_ if offset is None else offset
        phy = raw * factor + offset
    elif cc_type == 7:
        phy = raw
    else:
        raise ConversionError('%d' % cc_type, raw)
    return phy


def parseFileComment(filecomment):
    if filecomment == '':
        return filecomment
    comment = []

    filecomment = filecomment.lstrip(unicode(codecs.BOM_UTF8, 'utf8', 'ignore'))
    doc = xml.dom.minidom.parseString(filecomment.encode('utf-8'))

    tx, = doc.getElementsByTagName('TX')
    if tx.firstChild is not None:
        comment.append(tx.firstChild.data)
    prop, = doc.getElementsByTagName('common_properties')
    for e in prop.getElementsByTagName('e'):
        name = e.getAttribute('name')
        child = e.firstChild
        if child is None:
            data = ''
        else:
            data = child.data
        line = '%s: %s' % (name, data)
        comment.append(line)
    return u'\n'.join(comment)
