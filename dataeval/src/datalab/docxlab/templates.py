import collections
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


class TemplateLoader(object):

    def __init__(self, document):
        self.numbering_styles = collections.OrderedDict()
        self.paragraph_styles = collections.OrderedDict()
        self.margin_styles = collections.OrderedDict()
        self._init_built_in_styles()
        self._document = document

    def load_styles(self):
        # First the numbering styles has to be loaded
        for _, cn in self.numbering_styles.iteritems():
            cn.add_to_document(self._document)
        for _, ps in self.paragraph_styles.iteritems():
            ps.add_to_document(self._document)

        margin_style_key = '2.5'
        section = self._document.sections[0]
        section.left_margin = Inches(self.margin_styles[margin_style_key][0])
        section.right_margin = Inches(self.margin_styles[margin_style_key][1])
        section.top_margin = Inches(self.margin_styles[margin_style_key][2])
        section.bottom_margin = Inches(self.margin_styles[margin_style_key][3])

    def _init_built_in_styles(self):

        # paragraph_format, indentation_lvl, num_format, text_format, start_ind, hanging_ind
        self.numbering_styles['Heading'] = CustomAbstractNumberingStyle('Heading',
                                                                        [["Heading1", 0, 'decimal', "%1", 200, 200],
                                                                         ["Heading2", 1, 'decimal', "%1.%2", 400, 400],
                                                                         ["Heading3", 2, 'decimal', "%1.%2.%3", 600,
                                                                          600]], True)

        self.paragraph_styles['CNormal'] = CustomParagraphStyle(name='CNormal', space_after=0)

        self.paragraph_styles['Heading1'] = CustomParagraphStyle(level=0, nstyle='Heading', name='Heading1', bold=True,
                                                                 space_before=12, space_after=3,
                                                                 style_name_after='CNormal', page_break_before=True)
        self.paragraph_styles['Heading2'] = CustomParagraphStyle(level=1, nstyle='Heading', name='Heading2', bold=True,
                                                                 space_before=18, space_after=6,
                                                                 style_name_after='CNormal', keep_with_next=True)
        self.paragraph_styles['Heading3'] = CustomParagraphStyle(level=2, nstyle='Heading', name='Heading3', bold=True,
                                                                 space_before=12, space_after=3,
                                                                 style_name_after='CNormal', keep_with_next=True)

        self.margin_styles['1.27'] = [0.5, 0.5, 0.5, 0.5]
        self.margin_styles['2.5'] = [1.0, 1.0, 1.0, 1.0]

    def create_new_numbering_style(self, style):
        # Create new custom abstract style
        if style == 'bullet':
            abstract_name = 'ListBullet' + str(len(CustomAbstractNumberingStyle.custom_abstract_numberings) + 1)
            paragraph_styles = 'ListBullet' + str(len(CustomAbstractNumberingStyle.custom_abstract_numberings) + 1)
            new_as = CustomAbstractNumberingStyle(abstract_name,
                                                  [[paragraph_styles+str(1), 0, 'bullet', "l", 200, 720],  # Wingdings
                                                   [paragraph_styles+str(2), 1, 'bullet', "o", 200, 1440],  # CourierNew
                                                   [paragraph_styles+str(3), 2, 'bullet', "o", 200, 2160]])  # Wingdings
            abstract_num_id = new_as.add_to_document(self._document, abstract_name)
        elif style == 'number':
            abstract_name = 'ListNumber' + str(len(CustomAbstractNumberingStyle.custom_abstract_numberings) + 1)
            paragraph_styles = 'ListNumber' + str(len(CustomAbstractNumberingStyle.custom_abstract_numberings) + 1)
            new_as = CustomAbstractNumberingStyle(abstract_name,
                                                  [[paragraph_styles+str(1), 0, 'decimal', "%1.", 200, 720],
                                                   [paragraph_styles+str(2), 1, 'decimal', "%1.%2.", 400, 1440],
                                                   [paragraph_styles+str(3), 2, 'decimal', "%1.%2.%3.", 600, 2160]])
            abstract_num_id = new_as.add_to_document(self._document, abstract_name)
        else:
            raise TypeError("Unknown list type, only 'bullet' and 'number' is supported, not '{}'".format(style))

        # Create new custom numbering style
        num_of_numbering_stlyes = len(CustomNumberingStyle.custom_numberings)
        numbering_name = 'List' + str(num_of_numbering_stlyes + 1)
        new_custom_numbering_style = CustomNumberingStyle(numbering_name, abstract_num_id)
        numbering_id = new_custom_numbering_style.add_to_document_as_restarting(self._document)

        # TODO change hardcoded max_level
        for i in range(3):
            # TODO add paragraph format creation based on other format
            paragraph_style = paragraph_styles+str(i+1)
            # This is similar to CNormal
            CustomParagraphStyle(name=paragraph_style, space_after=0, level=i, nstyle=numbering_name,
                                 style_name_after=paragraph_style, hidden=True).add_to_document(self._document)

        return paragraph_styles, numbering_id


class CustomNumberingStyle(object):
    custom_numberings = dict()

    def __init__(self, name, abstract_num_id):
        self._name = name
        self._abstract_num_id = abstract_num_id
        self._numbering_id = None

    def add_to_document(self, document):
        numbering_xml = document.part.numbering_part.element

        numberings = numbering_xml.findall(qn('w:num'))
        self._numbering_id = self._get_first_valid(1, numberings, 'w:numId', 10)
        # Create w:num element - the document will use this
        num_xml = OxmlElement('w:num')
        num_xml.set(qn('w:numId'), str(self._numbering_id))
        abstract_num_id_xml = OxmlElement('w:abstractNumId')
        abstract_num_id_xml.set(qn('w:val'), str(self._abstract_num_id))
        num_xml.append(abstract_num_id_xml)
        # Add our new numbering element
        numbering_xml.append(num_xml)
        CustomNumberingStyle.custom_numberings[self._name] = self._numbering_id
        return self._numbering_id

    def add_to_document_as_restarting(self, document):
        numbering_xml = document.part.numbering_part.element

        numberings = numbering_xml.findall(qn('w:num'))
        self._numbering_id = self._get_first_valid(1, numberings, 'w:numId', 10)
        # Create w:num element - the document will use this
        num_xml = OxmlElement('w:num')
        num_xml.set(qn('w:numId'), str(self._numbering_id))
        abstract_num_id_xml = OxmlElement('w:abstractNumId')
        abstract_num_id_xml.set(qn('w:val'), str(self._abstract_num_id))
        num_xml.append(abstract_num_id_xml)
        # Add our new numbering element

        # NUMBERING MUST BE INSERTED AT THE END!
        # numbering element will not be recoognized before any abstract elements

        numbering_xml.append(num_xml)
        CustomNumberingStyle.custom_numberings[self._name] = self._numbering_id
        return self._numbering_id

    @staticmethod
    def _get_first_valid(current_id, xml_element, check_for, text_format):
        taken_ids = []
        for element in xml_element:
            abstract_num_id = element.get(qn(check_for))
            taken_ids += [int(abstract_num_id, text_format)]  # text_format: decimal - 10, hexadecimal - 16
        while current_id in taken_ids:
            current_id += 1
        return current_id


class CustomAbstractNumberingStyle(object):
    # When a paragraph is indexed then it will receive the last assigned numbering format
    custom_abstract_numberings = dict()

    def __init__(self, name, level_styles, create_numbering_style=False):
        self._abstract_numbering = OxmlElement('w:abstractNum')
        self._level_styles = level_styles
        self._name = name
        self._abstract_num_id = None
        self._create_numbering_style = create_numbering_style

    @staticmethod
    def _create_lvl(paragraph_format, indentation_lvl, num_format, text_format, start_ind, hanging_ind):
        """
        Create lvl element
        :param paragraph_format:
            The format of the numbered paragraph : Heading1, etc.
        :param indentation_lvl:
            assigned level (usually 0-2)
        :param num_format:
            Style of numbering can be :  bullet, upperRoman, lowerRoman, decimal, lowerLetter,
                                         decimalEnclosedCircle, etc. (search for numbering numFmt)

        :param text_format:
            Formatting the index :  "%1."  -   1.  II.  C.
                                    "%1,"  -   1,  I,  b,
                                    "%1-%2"  -   1-a  II-2  3-1
        :param start_ind:
            Indentation of the index
        :param hanging_ind:
            Indentation of the paragraph
        :return:
            OxmlElement of w:lvl

        Not implemented:
            w:start
            w:lvlJc
        """

        level = OxmlElement('w:lvl')
        level.set(qn('w:ilvl'), str(indentation_lvl))

        start_at = OxmlElement('w:start')
        start_at.set(qn('w:val'), str(1))  # Specifies starting value - hardcoded 1 now
        level.append(start_at)

        num_fit = OxmlElement('w:numFit')
        num_fit.set(qn('w:val'), num_format)
        level.append(num_fit)

        if paragraph_format is not None:
            style = OxmlElement('w:pStyle')
            style.set(qn('w:val'), paragraph_format)
            level.append(style)

        level_text = OxmlElement('w:lvlText')
        level_text.set(qn('w:val'), text_format)
        level.append(level_text)

        justification = OxmlElement('w:lvlJc')
        justification.set(qn('w:val'), 'start')
        level.append(justification)

        ppr = OxmlElement('w:pPr')
        ind = OxmlElement('w:ind')
        ind.set(qn('w:hanging'), str(start_ind))
        ind.set(qn('w:start'), str(hanging_ind))
        ppr.append(ind)
        level.append(ppr)

        if num_format == 'bullet':
            rpr = OxmlElement('w:rPr')
            r_fonts = OxmlElement('w:rFonts')
            d_bullet_styles = {0: 'Wingdings', 1: 'Courier New', 2: 'Wingdings'}
            d_bullet_sizes = {0: '13', 1: '16', 2: '13'}
            r_fonts.set(qn('w:hint'), 'default')
            r_fonts.set(qn('w:hAnsi'), d_bullet_styles[indentation_lvl])
            r_fonts.set(qn('w:ascii'), d_bullet_styles[indentation_lvl])
            sz = OxmlElement('w:sz')
            sz.set(qn('w:val'), d_bullet_sizes[indentation_lvl])
            szCs = OxmlElement('w:szCs')
            szCs.set(qn('w:val'), d_bullet_sizes[indentation_lvl])
            rpr.append(r_fonts)
            rpr.append(sz)
            rpr.append(szCs)
            level.append(rpr)
        return level

    def _generate_abstract_numbering(self, abstract_numbering_id, ns_id):
        self._abstract_numbering.set(qn('w:abstractNumId'), str(abstract_numbering_id))
        nsid = OxmlElement('w:nsid')
        nsid.set(qn('w:val'), '{0:08X}'.format(ns_id))
        self._abstract_numbering.append(nsid)
        multi_level_type = OxmlElement('w:multiLevelType')
        multi_level_type.set(qn('w:val'), 'multilevel')  # single level can be created as well
        self._abstract_numbering.append(multi_level_type)

        for s in self._level_styles:
            level = self._create_lvl(s[0], s[1], s[2], s[3], s[4], s[5])
            self._abstract_numbering.append(level)

    def add_to_document(self, document, name=None):
        if name is not None:
            self._name = name
        # Get numbering.xml
        numbering_xml = document.part.numbering_part.element
        # Get abstractNumberings
        abstract_numberings = numbering_xml.findall(qn('w:abstractNum'))
        self._abstract_num_id = self._get_first_valid(1, abstract_numberings, 'w:abstractNumId', 10)
        # Get nsids - unique identifier of the abstractNum
        nsids = [an.find(qn('w:nsid')) for an in abstract_numberings]
        current_nsid_id = self._get_first_valid(int('1F1F1F1F', 16), nsids, 'w:val', 16)  # random value
        # Create our abstract numbering element
        self._generate_abstract_numbering(self._abstract_num_id, current_nsid_id)
        # Add our new abstract numbering -  this will store the actual formatting

        # ABSTRACT NUMBERING MUST BE INSERTED AT THE BEGINNING!
        # numbering element will not be recoognized before any abstract elements
        numbering_xml.insert(0,self._abstract_numbering)

        CustomAbstractNumberingStyle.custom_abstract_numberings[self._name] = self._abstract_num_id
        if self._create_numbering_style:
            CustomNumberingStyle(self._name, self._abstract_num_id).add_to_document(document)
        return self._abstract_num_id

    @staticmethod
    def _get_first_valid(current_id, xml_element, check_for, text_format):
        taken_ids = []
        for element in xml_element:
            abstract_num_id = element.get(qn(check_for))
            taken_ids += [int(abstract_num_id, text_format)]  # text_format: decimal - 10, hexadecimal - 16
        while current_id in taken_ids:
            current_id += 1
        return current_id


class CustomParagraphStyle(object):
    def __init__(self, **kwargs):
        self._level = kwargs.pop('level', None)
        self._nstyle = kwargs.pop('nstyle', None)

        self._bold = kwargs.pop('bold', None)
        self._underline = kwargs.pop('underline', None)
        self._italic = kwargs.pop('italic', None)
        self._size = kwargs.pop('size', 12)
        self._font_name = kwargs.pop('font_name', "Times New Roman")

        self._name = kwargs.pop('name', 'NoName')

        self._alignment = kwargs.pop('alignment', 'LEFT')
        self._style_name_after = kwargs.pop('style_name_after', None)
        self._left_indent = kwargs.pop('left_indent', None)
        self._right_indent = kwargs.pop('right_indent', None)
        self._first_line_indent = kwargs.pop('first_line_indent', self._left_indent)
        self._space_before = kwargs.pop('space_before', None)
        self._space_after = kwargs.pop('space_after', None)
        self._line_spacing_rule = kwargs.pop('line_spacing_rule', 'single')
        self._page_break_before = kwargs.pop('page_break_before', False)
        self._keep_together = kwargs.pop('keep_together', False)
        self._keep_with_next = kwargs.pop('keep_with_next', False)

        self._hidden = kwargs.pop('hidden', False)  # should be added to final document

    def _generate_style(self, document, style):
        font = style.font
        font.name = self._font_name
        font.size = Pt(self._size)
        font.bold = self._bold
        font.italic = self._italic
        font.underline = self._underline

        if self._style_name_after is not None:
            style.next_paragraph_style = document.styles[self._style_name_after]
            # Note : does not seem to work

        d = {'LEFT': WD_PARAGRAPH_ALIGNMENT.LEFT, 'CENTER': WD_PARAGRAPH_ALIGNMENT.CENTER,
             'RIGHT': WD_PARAGRAPH_ALIGNMENT.RIGHT}
        d_line_spacing = {'single': WD_LINE_SPACING.SINGLE, 'double': WD_LINE_SPACING.DOUBLE,
             'one_point_five': WD_LINE_SPACING.ONE_POINT_FIVE}

        paragraph_format = style.paragraph_format
        paragraph_format.alignment = d[self._alignment]
        paragraph_format.line_spacing_rule = d_line_spacing[self._line_spacing_rule]

        paragraph_format.left_indent = Inches(self._left_indent) if self._left_indent is not None else None
        paragraph_format.right_indent = Inches(self._right_indent)  if self._right_indent is not None else None
        paragraph_format.first_line_indent = Inches(self._first_line_indent)  if self._first_line_indent is not None else None
        paragraph_format.space_before = Pt(self._space_before)  if self._space_before is not None else None
        paragraph_format.space_after = Pt(self._space_after)  if self._space_after is not None else None
        paragraph_format.page_break_before = self._page_break_before
        paragraph_format.keep_together = self._keep_together
        paragraph_format.keep_with_next = self._keep_with_next

    def add_to_document(self, document):
        if self._name in document.styles:
            document.styles[self._name].delete()
        style = document.styles.add_style(self._name, WD_STYLE_TYPE.PARAGRAPH)
        self._generate_style(document, style)
        # Add  it to word
        if not self._hidden:
            # By default it will be hidden
            style.hidden = False
            style.quick_style = True

        # Connect with numbering style
        if self._nstyle is not None:
            # Get nstyle numId
            n_id = CustomNumberingStyle.custom_numberings[self._nstyle]
            ppr = style.paragraph_format._element.pPr
            num_pr_xml = OxmlElement('w:numPr')
            num_id_xml = OxmlElement('w:numId')
            num_id_xml.set(qn('w:val'), str(n_id))
            num_pr_xml.append(num_id_xml)
            ilvl_xml = OxmlElement('w:ilvl')
            ilvl_xml.set(qn('w:val'), str(self._level))
            num_pr_xml.append(ilvl_xml)
            ppr.append(num_pr_xml)
