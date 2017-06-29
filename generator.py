# Sobrescrevendo funções para suportar unicode e fonte colorida
import csv
import os
import re
from unicodedata import normalize

from lxml import etree

import svgutils.transform
from svgutils.transform import FigureElement, SVGFigure


def fromfile(fname):
    fig = SVGFigure()
    svg_file = etree.parse(fname)
    fig.root = svg_file.getroot()
    return fig


def save(self, fname):
    """Save figure to a file"""
    out = etree.tostring(self.root, xml_declaration=True,
                         standalone=True,
                         pretty_print=True, encoding="UTF-8")
    fid = open(fname, 'wb')
    fid.write(out)
    fid.close()


class Text(FigureElement):
    """Text element.

    Corresponds to SVG ``<text>`` tag."""
    def __init__(self, x, y, text, size=8, font="Verdana",
                 weight="normal", letterspacing=0, anchor='start', color="black"):
        from svgutils.transform import SVG
        txt = etree.Element(SVG+"text", {"x": str(x), "y": str(y),
                                         "font-size": str(size),
                                         "font-family": font,
                                         "font-weight": weight,
                                         "fill": color,
                                         "letter-spacing": str(letterspacing),
                                         "text-anchor": str(anchor)})
        txt.text = text
        FigureElement.__init__(self, txt)


TEMPLATE = 'template.svg'

svgutils.transform.SVG = ''

template = fromfile(TEMPLATE)
width, wunit = re.findall('([\d\.]+)(.*)', template.width)[0]
height, hunit = re.findall('([\d\.]+)(.*)', template.height)[0]

y = 1075
x = 2490

with open('certificados.csv', 'r', encoding='utf-8') as csvfile:
    iterador = iter(csv.reader(csvfile, delimiter=','))
    next(iterador)
    nomes = [(row[0], row[1]) for row in iterador]

if not os.path.exists("certificados"):
    os.mkdir("certificados")

for i, (nome, matricula) in enumerate(nomes):
    sem_acento = normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    sem_acento = sem_acento.lower()
    sem_acento = sem_acento.replace(' ', '_')
    svgpath = os.path.join("certificados", "{}.svg".format(sem_acento))
    if os.path.exists(svgpath):
        continue  # Pula o que já foi feito
    print(i, sem_acento)
    template = fromfile(TEMPLATE)
    texto = nome
    if matricula:
        template.append(Text(
            x, y - 60, "{}".format(nome),
            size=130,
            anchor="middle",
            font="Flux",
            weight="bold",
            color="#306a98",
            letterspacing=0
        ))
        template.append(Text(
            x, y + 50, "(Matrícula: {})".format(matricula),
            size=100,
            anchor="middle",
            font="Flux",
            weight="bold",
            color="#306a98",
            letterspacing=0
        ))
    else:
        template.append(Text(
            x, y, nome,
            size=150.6,
            anchor="middle",
            font="Flux",
            weight="bold",
            color="#306a98",
            letterspacing=0
        ))

    save(template, svgpath)

os.system(' mogrify -verbose -format pdf $PWD/certificados/*.svg')
