import os
import datetime
from collections import OrderedDict

from reportlab.lib import colors
from reportlab.lib.pagesizes import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus.flowables import Image, Spacer
from reportlab.platypus.tables import Table

from datalab.tygra import grid_table_style, get_index_link, Link, Paragraph
from reportgen.common.utils import conv_float

PIC_DIR = os.path.join(os.path.dirname(__file__), 'images')

class TableDict(OrderedDict):
    def __init__(self):
        OrderedDict.__init__(self)
        return

    def get_table(self, **kwargs):
        data = self.get_data(**kwargs)
        style = self.get_style()
        table = Table(data, style=style)
        return table

    def get_data(self, **kwargs):
        raise NotImplementedError()

    def get_style(self):
        return grid_table_style


class Summary(TableDict):
    font_name = 'Helvetica'
    font_size = 7
    title = ''

    def __init__(self, batch, view_name):
        TableDict.__init__(self)
        self.columns = OrderedDict()
        self.modules = OrderedDict()
        self.init(batch, view_name)
        self.colWidths = self.get_colwidth()
        return

    def get_colwidth(self, default=12 * cm):
        if self:
            colwidth = stringWidth(self.keys()[0], self.font_name, self.font_size + 1)
        else:
            colwidth = default
        colwidth = 220  # TODO Need to check this
        return colwidth

    def get_table(self, link_pattern, link_heading, **kwargs):
        data = self.get_data(link_pattern, link_heading, **kwargs)
        style = self.get_style()
        colWidths = [self.colWidths]
        colWidths.extend(None for e in self.columns)
        table = Table(data, style=style, colWidths=colWidths)
        return table

    def init(self):
        raise NotImplementedError()

    def get_data(self, link_pattern, link_heading):
        raise NotImplementedError()

    def get_style(self):
        raise NotImplementedError()


class EventSummary(Summary):
    explanation = ''
    legend_pics = []
    extra_modules = []
    extra_columns = []
    statuses = []
    groups = []

    stat_im = Image(os.path.join(PIC_DIR, 'flr20_stationary_legend.png'),
                    width=0.5 * cm, height=0.5 * cm)
    mov_im = Image(os.path.join(PIC_DIR, 'flr20_moving_legend.png'),
                   width=0.5 * cm, height=0.5 * cm)
    aeb_im = Image(os.path.join(PIC_DIR, 'flr20_aeb_legend.png'),
                   width=0.5 * cm, height=0.5 * cm)
    acc_im = Image(os.path.join(PIC_DIR, 'flr20_acc_legend.png'),
                   width=0.5 * cm, height=0.5 * cm)
    aebs_resim_im = Image(os.path.join(PIC_DIR, 'flr20_moving_legend.png'),
                          width=0.5 * cm, height=0.5 * cm)
    paebs_resim_im = Image(os.path.join(PIC_DIR, 'flr25_stationary.png'),
                           width=0.5 * cm, height=0.5 * cm)

    def __init__(self, batch, view_name):
        Summary.__init__(self, batch, view_name)
        self.modules.update(self.extra_modules)
        self.columns.update(self.extra_columns)
        return

    @staticmethod
    def show_position(client):
        client.showPosition = True
        return

    @staticmethod
    def conv_target_vx(target_vx, moving):
        target_vx = target_vx if moving in ('moving', 'unclassified') else moving
        return target_vx

    @staticmethod
    def conv_xbr_speed_red(xbr_speed_red, cm_status):
        return xbr_speed_red

    @staticmethod
    def conv_nan(value):
        value = 'n/a' if value is None else value
        return value

    @staticmethod
    def conv_ttc(ttc_min, accel_demand_min):
        if accel_demand_min is None:
            ttc_min = 'n/a'
        return ttc_min

    @staticmethod
    def conv_gps(latitude, longitude, fmt='%.5f'):
        if latitude is None or longitude is None:
            coord = "?, ?"
        else:
            lat_sign = 'N' if latitude >= 0 else 'S'
            long_sign = 'E' if longitude >= 0 else 'W'
            coord_fmt = ' '.join(['%s', fmt, '%s', fmt])
            coord = coord_fmt % (lat_sign, abs(latitude), long_sign, abs(longitude))
        return coord

    def get_data(self, link_pattern, link_heading):
        header = self.columns.values()
        header.insert(0, 'measurement')
        data = [header]
        for meas, warnings in self.iteritems():
            basename = os.path.basename(meas)
            for warning in warnings:
                row = [conv_float(warning[name]) for name in self.columns]
                # create sub table for link
                try:
                    if warning['event'] in ['Information Warning', 'VDP Warning', 'Collision Warning', 'NA Status',
                                            'Error State', 'LCDA Information Warning','LCDA VDP Warning',
                                            'LCDA Collision Warning','LCDA NA Status','LCDA Error State']:
                        # http://xiix.wordpress.com/2008/03/12/a-reportlab-link-in-table-cell-workaround/
                        link = get_index_link(link_pattern % (basename, warning['start'],
                                                              datetime.datetime.fromtimestamp(
                                                                  float(warning['start'])).strftime(
                                                                  '%Y-%b-%d %H:%M:%S')),
                                              link_heading)
                        self.colWidths = stringWidth(self.keys()[0], self.font_name, self.font_size - 3)
                    else:
                        link = get_index_link(link_pattern % (basename, warning['start']), link_heading)
                except:
                    link = get_index_link(link_pattern % (basename, warning['start']), link_heading)

                row.insert(0, Table([[Paragraph(Link(link, basename),
                                                fontSize=self.font_size,
                                                fontName=self.font_name)]],
                                    colWidths=self.colWidths))
                data.append(row)
        return data

    def get_style(self):
        style = [
            ('GRID', (0, 0), (-1, -1), 0.025 * cm, colors.black),
            ('FONT', (0, 0), (-1, 0), '%s-Bold' % self.font_name, self.font_size),
            ('FONT', (0, 1), (-1, -1), self.font_name, self.font_size),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ]
        return style

    def get_tracknav_legend(self):
        story = [
            Paragraph('Legend of the birdeye view picture', style='Heading3'),
            Paragraph('Meaning of the object shapes', style='Normal'),
            Table([pic for pic in self.legend_pics], hAlign='LEFT'),
            Spacer(width=1 * cm, height=0.2 * cm),
            Paragraph('Meaning of the colors', style='Normal'),
            Spacer(width=1 * cm, height=0.2 * cm),
            Table([['stationary or very slow'], ['ongoing'], ['oncoming']],
                  style=[('TEXTCOLOR', (0, 0), (0, 0), colors.red),
                         ('TEXTCOLOR', (0, 1), (0, 1), colors.green),
                         ('TEXTCOLOR', (0, 2), (0, 2), colors.blue)],
                  hAlign='LEFT'),
            Paragraph(r'Meaning of the object label: {track}({lat}|{long})',
                      style='Normal'),
            Spacer(width=1 * cm, height=0.2 * cm),
            Table([
                ['track', 'Name of the track.'],
                ['lat', 'Lateral distance from the ego vehicle. Left is positive'],
                ['long', 'Longitudinal distance from the ego vehicle.'],
            ], hAlign='LEFT'),
            Spacer(width=1 * cm, height=0.2 * cm),
        ]
        return story
