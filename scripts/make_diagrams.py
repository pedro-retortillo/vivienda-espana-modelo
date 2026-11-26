"""Diagramas de Forrester y de lazos causales como SVG que usan variables CSS del tema."""
import math

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")

class D:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.o = []
    def stock(self, x, y, w, h, label, cls="st"):
        lines = label.split("\n")
        self.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" class="{cls}"/>')
        for i, l in enumerate(lines):
            self.o.append(f'<text x="{x+w/2}" y="{y+h/2+4-(len(lines)-1)*7+i*14}" text-anchor="middle" class="tx b">{esc(l)}</text>')
        return (x, y, w, h)
    def cloud(self, x, y):
        self.o.append(f'<path d="M{x-14} {y+6}a8 8 0 0 1 2-14a10 10 0 0 1 19-3a9 9 0 0 1 14 8a7 7 0 0 1-3 9z" class="cl"/>')
    def aux(self, x, y, label, cls="ax"):
        w = max(54, len(label) * 6.4 + 14)
        self.o.append(f'<rect x="{x-w/2}" y="{y-12}" width="{w}" height="24" rx="12" class="{cls}"/><text x="{x}" y="{y+4}" text-anchor="middle" class="tx">{esc(label)}</text>')
        return (x, y, w)
    def flow(self, x1, y1, x2, y2, label, lx=0, ly=-10, cls="fl"):
        self.o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}" marker-end="url(#ah)"/>')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        self.o.append(f'<path d="M{mx-6} {my-6}L{mx+6} {my+6}L{mx+6} {my-6}L{mx-6} {my+6}z" class="vl"/>')
        if label: self.o.append(f'<text x="{mx+lx}" y="{my+ly}" text-anchor="middle" class="tx s">{esc(label)}</text>')
    def link(self, x1, y1, x2, y2, sign="", curve=0, lbl_dx=0, lbl_dy=0, cls="lk"):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        cx, cy = mx - dy / L * curve, my + dx / L * curve
        self.o.append(f'<path d="M{x1} {y1}Q{cx} {cy} {x2} {y2}" class="{cls}" marker-end="url(#ah2)"/>')
        if sign:
            self.o.append(f'<text x="{(x1+2*cx+x2)/4+lbl_dx}" y="{(y1+2*cy+y2)/4+lbl_dy}" text-anchor="middle" class="tx sg">{sign}</text>')
    def text(self, x, y, s, cls="tx", anchor="middle"):
        self.o.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{esc(s)}</text>')
    def loop(self, x, y, kind):
        self.o.append(f'<text x="{x}" y="{y}" text-anchor="middle" class="tx lp">{kind}</text>')
    def svg(self):
        defs = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="ahp"/></marker>'
                '<marker id="ah2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="ah2p"/></marker></defs>')
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(self.title)}" class="dg">{defs}' + "".join(self.o) + "</svg>")

def parque():
    d = D(980, 470, "Diagrama de Forrester del parque de viviendas")
    d.stock(40, 200, 110, 50, "En\nconstrucción")
    d.stock(330, 200, 120, 50, "A la venta")
    d.stock(330, 40, 120, 50, "Uso propio")
    d.stock(640, 200, 130, 50, "Vacías\nretenidas")
    d.stock(640, 40, 130, 50, "Alquiladas")
    d.stock(330, 360, 120, 50, "Segundas\nresidencias")
    d.stock(780, 360, 130, 50, "Deterioradas", "st st2")
    d.cloud(10, 225); d.flow(18, 225, 40, 225, "")
    d.flow(150, 225, 330, 225, "Obra a venta", 0, -12)
    d.flow(95, 250, 330, 385, "Obra a segundas residencias", 30, 22)
    d.flow(375, 200, 375, 90, "Compra de hogares", -48, 0)
    d.flow(405, 90, 405, 200, "Reventa", 36, 0)
    d.flow(450, 212, 640, 212, "Compra inversora", 0, -10)
    d.flow(640, 238, 450, 238, "Venta del inversor", 0, 20)
    d.flow(700, 200, 700, 90, "Puesta en alquiler", -56, 0)
    d.flow(730, 90, 730, 200, "Fin de contrato", 52, 0)
    d.flow(390, 360, 390, 250, "Segundas a la venta", -60, 0)
    d.flow(770, 245, 800, 360, "Deterioro (de todos los stocks)", 70, -2, "fl thin")
    d.flow(780, 385, 450, 240, "Rehabilitación", 10, 38, "fl thin")
    d.stock(520, 400, 160, 44, "Parque retirado")
    d.flow(845, 410, 680, 422, "Demolición", 0, 22, "fl thin")
    d.text(490, 18, "Cada rectángulo es un nivel (viviendas); cada flecha gruesa, un flujo (viviendas al mes)", "tx s")
    return d.svg()

def demanda_precio():
    d = D(980, 560, "Diagrama causal de las demandas y el precio")
    # financiacion
    d.aux(90, 60, "Renta del hogar"); d.aux(90, 110, "Tipo y plazo"); d.aux(90, 160, "Préstamo / valor"); d.aux(90, 210, "Ahorro para la entrada")
    d.aux(300, 135, "Capacidad de compra\n(años de renta)".replace("\n", " "))
    for y, s in ((60, "+"), (110, "−"), (160, "±"), (210, "+")):
        d.link(155, y + 2, 215, 132, s, 0)
    d.aux(530, 135, "Acceso", "ax ax2")
    d.link(380, 135, 495, 135, "+", 0)
    d.aux(530, 245, "Demanda de hogares", "ax ax2")
    d.link(530, 148, 530, 232, "+", 0)
    # inversores
    d.aux(300, 330, "Rentabilidad del alquiler"); d.aux(300, 380, "Expectativa de revalorización"); d.aux(300, 430, "Coste del dinero y riesgo")
    d.aux(530, 380, "Demanda inversora", "ax ax2")
    d.link(380, 330, 480, 368, "+", 0); d.link(420, 380, 465, 380, "+", 0); d.link(380, 430, 480, 392, "−", 0)
    # presion y precio
    d.aux(760, 310, "Presión de la demanda", "ax ax2")
    d.link(595, 250, 700, 300, "+", 0); d.link(600, 372, 700, 322, "+", 0)
    d.aux(760, 190, "Oferta en venta", "ax ax2")
    d.link(760, 202, 760, 298, "−", 0)
    d.aux(860, 460, "PRECIO", "ax pr")
    d.link(780, 322, 840, 448, "+", 0)
    # lazos
    d.link(830, 448, 560, 150, "−", 120, -6, -8)          # precio -> acceso
    d.link(840, 470, 410, 392, "+", -120, -20, 20)        # precio -> expectativa
    d.aux(640, 530, "Margen de obra"); d.aux(430, 530, "Inicios de obra"); d.aux(200, 530, "Viviendas terminadas")
    d.link(850, 472, 700, 520, "+", 0); d.link(575, 530, 490, 530, "+", 0); d.link(370, 530, 275, 530, "+", 0)
    d.link(150, 520, 700, 205, "+", -160, 20, 0)          # terminadas -> oferta
    d.loop(700, 430, "R: expectativas"); d.loop(560, 70, "B: acceso"); d.loop(130, 505, "B: obra nueva")
    d.text(490, 18, "Verde: el precio y lo que lo mueve. Los signos indican si el efecto va en el mismo sentido (+) o contrario (−)", "tx s")
    return d.svg()

def financiacion():
    d = D(980, 500, "Diagrama del subsistema de financiación")
    d.stock(430, 150, 150, 60, "Deuda\nhipotecaria", "st st2")
    d.cloud(130, 180); d.flow(140, 180, 430, 180, "Préstamos nuevos", 0, -12)
    d.flow(580, 180, 850, 180, "Amortización", 0, -12); d.cloud(870, 182)
    d.aux(215, 70, "Compras de hogares\ne inversores".replace("\n", " ")); d.aux(215, 110, "Precio × superficie")
    d.aux(325, 250, "Préstamo / valor"); d.aux(135, 250, "Fracción hipotecada")
    d.link(215, 82, 280, 168, "+"); d.link(215, 122, 300, 170, "+"); d.link(325, 238, 330, 190, "+"); d.link(160, 238, 250, 190, "+")
    d.aux(715, 250, "Plazo de las hipotecas")
    d.link(715, 238, 715, 192, "−")
    d.text(490, 290, "La deuda se compara con el crédito a hogares sobre PIB (BIS): es una comprobación, no un ajuste a mano", "tx s")
    # capacidad
    d.aux(150, 360, "Renta"); d.aux(150, 410, "Esfuerzo máximo")
    d.aux(330, 360, "Tipo de interés"); d.aux(330, 410, "Plazo")
    d.aux(520, 385, "Cuota por euro prestado")
    d.link(380, 362, 450, 380, "+"); d.link(380, 410, 450, 392, "−")
    d.aux(530, 450, "Capacidad por cuota", "ax ax2"); d.link(520, 398, 525, 438, "−")
    d.link(210, 412, 440, 450, "+")
    d.aux(760, 360, "Ahorro (años de renta)"); d.aux(790, 450, "Capacidad por entrada", "ax ax2")
    d.link(765, 372, 780, 438, "+")
    d.aux(940, 405, "Préstamo/valor", "ax"); d.link(930, 392, 835, 440, "−")
    d.aux(660, 480, "MÍNIMO de las dos: capacidad de compra", "ax pr")
    d.link(580, 452, 620, 470, "", 0); d.link(770, 462, 720, 472, "", 0)
    return d.svg()

def hogares():
    d = D(980, 260, "Diagrama del subsistema de hogares")
    d.aux(130, 50, "Hogares de la EPA (dato)"); d.aux(130, 110, "Proyección del INE (después de 2024)")
    d.aux(330, 80, "Hogares objetivo", "ax ax2"); d.link(200, 55, 285, 74, "+"); d.link(230, 108, 290, 88, "+")
    d.stock(520, 130, 130, 56, "Hogares")
    d.cloud(330, 158); d.flow(340, 158, 520, 158, "Formación", 0, -12)
    d.flow(650, 158, 840, 158, "Disolución", 0, -12); d.cloud(860, 160)
    d.link(360, 92, 560, 132, "+", 0)
    d.text(490, 232, "Los hogares siguen a los datos con un retraso de dos años; en la demanda actúan como escala (más hogares, más compras deseadas)", "tx s")
    return d.svg()

def costes():
    d = D(1040, 630, "Diagrama causal de la composición del precio: costes de construcción y precio de coste")
    # entradas (datos y supuestos)
    d.aux(130, 50, "Índice real de materiales (INE)"); d.aux(130, 170, "Índice real de mano de obra (INE)")
    d.aux(130, 250, "Escalones normativos (CTE, DB-HE)"); d.aux(130, 320, "Sobrecoste por escalón (supuesto)", "ax ax3")
    # componentes
    d.aux(400, 50, "Materiales"); d.aux(400, 110, "Energía y transporte"); d.aux(400, 170, "Mano de obra")
    d.aux(400, 240, "Calidad y otros (fijo)"); d.aux(400, 320, "Normativa")
    d.link(235, 50, 355, 50, "+"); d.link(190, 62, 350, 106, "+"); d.link(235, 170, 355, 170, "+")
    d.link(235, 250, 358, 312, "+"); d.link(235, 320, 355, 320, "+")
    # coste de construccion
    d.aux(650, 190, "COSTE DE CONSTRUCCIÓN (€/m²)", "ax pr")
    for y, e, s_ in ((50, 178, "+"), (110, 182, "+"), (170, 190, "+"), (240, 198, "+"), (320, 204, "+")):
        d.link(465, y + (4 if y < 190 else -4), 538, e, s_, 0)
    d.aux(650, 70, "Política de costes (multiplicador)"); d.link(650, 82, 650, 176, "×")
    # precio de coste
    d.aux(890, 70, "Margen mínimo del promotor"); d.aux(890, 350, "Suelo: fracción del precio", "ax ax3")
    d.aux(890, 190, "PRECIO DE COSTE", "ax pr")
    d.link(765, 190, 828, 190, "+"); d.link(890, 82, 890, 176, "+"); d.link(890, 338, 890, 204, "+")
    d.text(904, 226, "(coste + margen)", "tx s", "start"); d.text(904, 241, "/ (1 − suelo)", "tx s", "start")
    # precio y suelo de coste
    d.aux(660, 455, "Brecha coste"); d.aux(890, 500, "PRECIO", "ax pr")
    d.link(840, 204, 700, 442, "−", 0, -14, 6)            # precio de coste -> brecha
    d.link(850, 492, 705, 462, "+")                          # precio -> brecha
    d.link(695, 468, 850, 508, "−", -26, 8, 16)              # brecha -> precio (empuja hacia arriba si cae bajo coste)
    d.link(890, 488, 890, 364, "+", 0, 14, 0)                # precio -> suelo
    # margen de obra y oferta
    d.aux(330, 470, "Margen de obra"); d.aux(330, 540, "Inicios de obra"); d.aux(580, 575, "Oferta en venta"); d.aux(830, 590, "Presión de la demanda")
    d.link(600, 202, 360, 458, "−", 30, -8, 0)               # coste construccion -> margen
    d.link(840, 505, 395, 474, "+", -100, 6, 14)             # precio -> margen
    d.link(330, 484, 330, 527, "+"); d.link(395, 543, 530, 569, "+"); d.link(640, 577, 765, 588, "−")
    d.link(850, 578, 890, 514, "+")
    d.loop(770, 330, "B: suelo de coste"); d.loop(445, 610, "B: obra nueva"); d.loop(975, 430, "B: suelo y precio")
    d.text(520, 18, "El coste entra por dos vías: abarata o encarece la obra nueva (margen) y fija el precio mínimo al que se construye (precio de coste)", "tx s")
    return d.svg()

if __name__ == "__main__":
    import sys
    open(sys.argv[1], "w", encoding="utf-8").write("\n<!--SEP-->\n".join([parque(), demanda_precio(), financiacion(), hogares(), costes()]))
    print("diagramas generados")
