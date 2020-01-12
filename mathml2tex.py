#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Convert mathml to math-tex

__author__  = 'David Chern'
__version__ = (0, 0, 1)
__date__    = (2016, 11, 11)

from bs4 import BeautifulSoup, NavigableString


class MathMLTeX(object):
    ''' 
    parse MathML back to Math-Tex
    '''
    mvalues = ['mo', 'mn', 'mi', 'mspace', 'mtext']  # nodes containing values
    msymbols = [(u'α', '\\alpha'), (u'β', '\\beta'), (u'γ', '\\gamma'),
                (u'δ', '\\delta'), (u'ε', '\\epsilon'), (u'ζ', '\\zeta'),
                (u'η', '\\eta'), (u'θ', '\\theta'), (u'ι', '\\iota'),
                (u'κ', '\\kappa'), (u'λ', '\\lambda'), (u'μ', '\\mu'),
                (u'ν', '\\nu'), (u'ξ', '\\xi'), (u'ο', '\\omicron'),
                (u'π', '\\pi'), (u'ρ', '\\rho'), (u'σ', '\\sigma'),
                (u'τ', '\\tau'), (u'υ', '\\upsilon'), (u'φ', '\\phi')]
    mtypes = {
        '{': 'Bmatrix',
        '}': 'Bmatrix',
        '[': 'bmatrix',
        ']': 'bmatrix',
        '(': 'pmatrix',
        ')': 'pmatrix',
        '|': 'vmatrix',
        '||': 'Vmatrix'
    }

    def __init__(self):
        self.istag = lambda x: not isinstance(x, NavigableString)
        self.cfns = {}
        # cache all converting methods
        for method in dir(self):
            cfn = getattr(self, method)
            if method.startswith('convert_') and callable(cfn):
                self.cfns[method[8:]] = cfn

    def convert(self, xml):
        if xml.find('<math') == -1:
            xml = '<math>%s</math>' % (xml)

        self.mtex = ''
        soup = BeautifulSoup(xml, "html.parser", from_encoding='utf-8')
        self.proc_tag(soup, children_only=True)

        for (c, m) in self.msymbols:
            self.mtex = self.mtex.replace(c, m)
        return self.mtex.encode('utf-8')

    def proc_tag(self, node, children_only=False):
        values = []
        for el in filter(self.istag, node.children):
            values.append(self.proc_tag(el))

        text = ''
        if not children_only:
            # prevent from output of ill-formed mathml
            if (not node.name in self.mvalues) and \
               (not any([v.strip() for v in values])):
                return ''
            cfn = self.cfns.get(node.name, None)
            if cfn:
                text = cfn(node, values)
        return text

    # final node for math-tex output
    def convert_math(self, el, values):
        self.mtex = ''.join(values)
        return ''

    # important math-tex unit for processing
    def convert_mrow(self, el, values):
        for (key, value) in enumerate(values):
            if 'matrix' in value:
                if key + 1 < len(values):
                    mark = '%s%s' % (values[key - 1].strip(),
                                     values[key + 1].strip())
                    # bmatrix, pmatrix, vmatrix, Vmatrix, matrix
                    if mark in ['[]', '()', '||', '||||', '{}']:
                        values[key - 1] = ''
                        values[key + 1] = ''
                # equation
                elif values[key - 1].strip() in ['{', '[', '(', '|']:
                    bquote = '\\' if values[key - 1].strip() == '{' else ''
                    values[key - 1] = '\\left%s%s' % (bquote, values[key - 1])
                    values[key] = values[key] + '\\right.'
        return ''.join(values)

    def convert_mo(self, el, values):
        value = el.text.strip()
        return ' %s ' % (value) if value else ' '

    def convert_mi(self, el, values):
        return el.text

    convert_mn = convert_mi
    convert_mtext = convert_mi

    def convert_mspace(self, e, values):
        return ' '

    def convert_msub(self, el, values):
        sub = '{%s}' % (values[1]) if len(values[1]) > 1 else values[1]
        return '%s_%s' % (values[0], sub)

    def convert_msup(self, el, values):
        sup = '{%s}' % (values[1]) if len(values[1]) > 1 else values[1]
        return '%s^%s' % (values[0], sup)

    def convert_msubsup(self, el, values):
        if len(values) < 3:
            return self.convert_msub(el, values)
        sub = '{%s}' % (values[1]) if len(values[1]) > 1 else values[1]
        sup = '{%s}' % (values[2]) if len(values[2]) > 1 else values[2]
        return '%s_%s^%s' % (values[0], sub, sup)

    def convert_munder(self, el, values):
        return '\\underline{%s}' % (values[0])

    def convert_mover(self, el, values):
        return '\\overline{%s}' % (values[0])

    def convert_mfenced(self, el, values):
        return '(%s)' % (','.join(values))

    def convert_mfrac(self, el, values):
        return '\\frac{%s}{%s}' % (values[0], values[1])

    def convert_msqrt(self, el, values):
        return '\\sqrt{%s}' % (''.join(values))

    def convert_mroot(self, el, values):
        times = '[%s]' % (values[1]) if len(values) > 1 else ''
        return '\\sqrt%s{%s}' % (times, values[0])

    def convert_mtd(self, el, values):
        return ''.join(values)

    def convert_mtr(self, el, values):
        return '&'.join(filter(None, values))

    def convert_mtable(self, el, values):
        # sibling nodes are nearest first.
        ps = filter(self.istag, el.previous_siblings)
        pt = self.mtypes.get(ps[0].text.strip(), 'bmatrix') if ps else 'align'
        ns = filter(self.istag, el.next_siblings)
        nt = self.mtypes.get(ns[0].text.strip(), 'bmatrix') if ns else 'align'
        mtype = pt if pt == nt else 'matrix'
        return '\\begin{%s}%s\\end{%s}' % (mtype, '\\\\'.join(values), mtype)