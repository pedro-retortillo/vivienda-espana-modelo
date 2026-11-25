import sys, math, random, re
sys.path.insert(0, ".")
import v1_model as M

V = M.V; names = M.names; refs = M.refs; eq = M.eq
view_of = {n: v for n, e, u, c, v in V}
STOCK = {n for n in names if eq[n].startswith("INTEG(")}

def width(n): return max(40, len(n) * 6.6)
def size(n): return (110, 46) if n in STOCK else (width(n), 14)

# ------------------------------------------------------------------ especificacion de vistas
SPEC = {
 "01": dict(title="01 Parque",
  stocks={"Uso propio": (700, 200), "Alquiladas": (1400, 200), "Parque retirado": (1050, 80),
          "Deterioradas": (1050, 380), "Viviendas venta": (700, 640), "Vacias inversor": (1400, 640),
          "En construccion": (300, 640), "Edad media": (300, 200)},
  clouds={"c1": (80, 640), "c2": (80, 200), "c3": (520, 200)},
  flows={"Inicio obra": ("c1", "En construccion", 190, 640, 0, 22),
         "Obra terminada": ("En construccion", "Viviendas venta", 500, 640, 0, 22),
         "Compra hogares": ("Viviendas venta", "Uso propio", 660, 420, -90, 0),
         "Reventa propietarios": ("Uso propio", "Viviendas venta", 740, 420, 96, 0),
         "Compra inversora": ("Viviendas venta", "Vacias inversor", 1050, 610, 0, -22),
         "Venta inversor": ("Vacias inversor", "Viviendas venta", 1050, 670, 0, 22),
         "Puesta en alquiler": ("Vacias inversor", "Alquiladas", 1360, 420, -90, 0),
         "Fin de contrato": ("Alquiladas", "Vacias inversor", 1440, 420, 84, 0),
         "Deterioro uso propio": ("Uso propio", "Deterioradas", 874, 290, -70, -26),
         "Deterioro alquiladas": ("Alquiladas", "Deterioradas", 1226, 290, 70, -26),
         "Deterioro venta": ("Viviendas venta", "Deterioradas", 838, 498, -72, 0),
         "Rehabilitacion": ("Deterioradas", "Viviendas venta", 876, 548, 64, 14),
         "Deterioro vacias inversor": ("Vacias inversor", "Deterioradas", 1242, 522, 90, 0),
         "Demolicion": ("Deterioradas", "Parque retirado", 1050, 230, 70, 0),
         "Envejecimiento": ("c2", "Edad media", 190, 200, 0, 22),
         "Rejuvenecimiento": ("Edad media", "c3", 410, 200, 0, 22)}),
 "02": dict(title="02 Precio",
  stocks={"Precio": (600, 800), "Expectativa ge": (1200, 800)},
  clouds={"c1": (260, 800), "c2": (860, 800)},
  flows={"Cambio precio": ("c1", "Precio", 430, 800, 0, 22),
         "Cambio expectativa": ("c2", "Expectativa ge", 1000, 800, 0, 22)}),
 "03": dict(title="03 Hogares",
  stocks={"Hogares": (900, 500), "Poblacion familiar": (400, 500)},
  clouds={"c1": (900, 240), "c2": (900, 780), "c3": (100, 420), "c4": (100, 580)},
  flows={"Formacion hogares": ("c1", "Hogares", 900, 370, 90, 0),
         "Disolucion hogares": ("Hogares", "c2", 900, 640, 90, 0),
         "Saldo natural": ("c3", "Poblacion familiar", 250, 450, 0, -24),
         "Saldo migratorio": ("c4", "Poblacion familiar", 250, 550, 0, 24)}),
 "04": dict(title="04 Indicadores", stocks={}, clouds={}, flows={}),
}
FLOW_VIEW = {f: k for k, s in SPEC.items() for f in s["flows"]}
for f, k in FLOW_VIEW.items():
    assert view_of[f] == k, (f, view_of[f], k)

def build_view(k, seeds=8):
    S = SPEC[k]
    real = [n for n in names if view_of[n] == k]
    stocks, flows, clouds = S["stocks"], S["flows"], S["clouds"]
    free = [n for n in real if n not in stocks and n not in flows]
    base = dict(stocks)
    for f, (s_, d_, vx, vy, dx, dy) in flows.items():
        base[f] = (vx + dx, vy + dy)
    xyc = dict(base); xyc.update(clouds)
    for f, (s_, d_, vx, vy, dx, dy) in flows.items():
        xyc["valve:" + f] = (vx, vy)

    attached = {}   # existencia -> flujos con valvula pegada
    for f, (s_, d_, *_r) in flows.items():
        for st in (s_, d_):
            attached.setdefault(st, set()).add(f)

    realedges, shadowedges = [], []     # (origen, destino)
    for n in real:
        e = eq[n]
        if n in stocks:
            m = re.match(r"INTEG\((.*),\s*([^,]*)\)$", e)
            for d in refs(m.group(1)):
                if d not in attached.get(n, set()):
                    shadowedges.append((d, n))
            continue
        for d in refs(e):
            if d == n: continue
            if d in STOCK or view_of[d] is None or view_of[d] != k:
                shadowedges.append((d, n))
            else:
                realedges.append((d, n))

    # obstaculos a lo largo de las tuberias
    OBST = []
    for f, (s_, d_, vx, vy, dx, dy) in flows.items():
        for end in (s_, d_):
            ex, ey = xyc[end]
            nn = max(1, int(math.hypot(ex - vx, ey - vy) // 25))
            for q in range(nn + 1):
                OBST.append((vx + (ex - vx) * q / nn, vy + (ey - vy) * q / nn))
    for st, (x, y) in stocks.items():
        for dx_ in (-60, -20, 20, 60): OBST.append((x + dx_, y))

    nb = {n: [] for n in list(base) + free}
    for a, b in realedges:
        nb[a].append(b); nb[b].append(a)

    def layout(seed):
        random.seed(seed)
        pos = dict(base)
        gx = 0
        for n in free:
            pts = [base[m] for m in nb[n] if m in base]
            if pts:
                cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
            else:
                cx, cy = 300 + (gx % 4) * 320, 300 + (gx // 4) * 170; gx += 1
            pos[n] = (cx + random.uniform(-200, 200), cy + random.uniform(-200, 200))
        for it in range(900):
            force = {n: [0.0, 0.0] for n in free}
            for a, b in realedges:
                for u, v in ((a, b), (b, a)):
                    if u in force:
                        pv = pos[v] if v in pos else xyc["valve:" + v]
                        dx = pv[0] - pos[u][0]; dy = pv[1] - pos[u][1]
                        d = math.hypot(dx, dy) + 1e-6
                        if d > 220:
                            f_ = 0.015 * (d - 220); force[u][0] += f_ * dx / d; force[u][1] += f_ * dy / d
            for u in free:
                wu, hu = size(u)
                for v in pos:
                    if u == v: continue
                    wv, hv = size(v)
                    dx = pos[u][0] - pos[v][0]; dy = pos[u][1] - pos[v][1]
                    ox = (wu + wv) / 2 + 90 - abs(dx); oy = (hu + hv) / 2 + 60 - abs(dy)
                    if ox > 0 and oy > 0:
                        if oy <= ox: force[u][1] += math.copysign(oy * 0.15, dy or 1)
                        else: force[u][0] += math.copysign(ox * 0.15, dx or 1)
                for (ox_, oy_) in OBST:
                    dx = pos[u][0] - ox_; dy = pos[u][1] - oy_
                    ox = (wu + 30) / 2 + 40 - abs(dx); oy = (hu + 30) / 2 + 30 - abs(dy)
                    if ox > 0 and oy > 0:
                        if oy <= ox: force[u][1] += math.copysign(oy * 0.3, dy or 1)
                        else: force[u][0] += math.copysign(ox * 0.3, dx or 1)
            for u in free:
                x = pos[u][0] + max(-10, min(10, force[u][0])); y = pos[u][1] + max(-10, min(10, force[u][1]))
                pos[u] = (min(1700, max(100, x)), min(1100, max(100, y)))
        for it in range(1500):
            moved = False
            for u in free:
                wu, hu = size(u)
                others = [(pos[v][0], pos[v][1], size(v)[0], size(v)[1]) for v in pos if v != u]
                others += [(a_, b_, 30, 30) for (a_, b_) in OBST]
                for (cx, cy, wv, hv) in others:
                    dx = pos[u][0] - cx; dy = pos[u][1] - cy
                    ox = (wu + wv) / 2 + 30 - abs(dx); oy = (hu + hv) / 2 + 24 - abs(dy)
                    if ox > 0 and oy > 0:
                        moved = True
                        if oy <= ox: pos[u] = (pos[u][0], pos[u][1] + math.copysign(oy / 2 + 1, dy or 1))
                        else: pos[u] = (pos[u][0] + math.copysign(ox / 2 + 1, dx or 1), pos[u][1])
            if not moved: break
        for n in free:
            pos[n] = (int(round(pos[n][0] / 2) * 2), int(round(pos[n][1] / 2) * 2))
        return pos

    def hit(p, q, c, w, h):
        for t in (0.15, 0.3, 0.45, 0.6, 0.75, 0.9):
            x = p[0] + (q[0] - p[0]) * t; y = p[1] + (q[1] - p[1]) * t
            if abs(x - c[0]) < w / 2 and abs(y - c[1]) < h / 2: return True
        return False
    def cost(pos):
        c = 0.0
        for u in free:
            wu, hu = size(u)
            for v in stocks:
                if abs(pos[u][0] - pos[v][0]) < (wu + 110) / 2 and abs(pos[u][1] - pos[v][1]) < (hu + 46) / 2: c += 1000
            for (ox_, oy_) in OBST:
                if abs(pos[u][0] - ox_) < (wu + 30) / 2 and abs(pos[u][1] - oy_) < (hu + 30) / 2: c += 200
        for a, b in realedges:
            pa = pos[a]; pb = xyc["valve:" + b] if b in flows else pos[b]
            c += math.hypot(pa[0] - pb[0], pa[1] - pb[1]) * 0.05
            for n in pos:
                if n in (a, b): continue
                w, h = size(n)
                if hit(pa, pb, pos[n], w, h): c += 30
        return c

    if free:
        best, bc = None, 1e18
        for s in range(seeds):
            p = layout(s); c = cost(p)
            if c < bc: best, bc = p, c
        pos = best
    else:
        pos = dict(base); bc = 0
    pos.update({k_: v_ for k_, v_ in xyc.items() if k_.startswith("valve:")})   # valvulas

    # sombras alrededor del consumidor
    boxes = [(pos[n][0], pos[n][1], size(n)[0], size(n)[1]) for n in list(base) + free]
    boxes += [(x, y, 20, 14) for (x, y) in clouds.values()]
    boxes += [(a_, b_, 30, 30) for (a_, b_) in OBST]
    def spot_ok(x, y, w, h, taken):
        for (cx, cy, bw, bh) in boxes + taken:
            if abs(x - cx) < (w + bw) / 2 + 6 and abs(y - cy) < (h + bh) / 2 + 6: return False
        return True
    shadows, taken, seen = [], [], set()
    bycons = {}
    for a, b in shadowedges:
        if (a, b) in seen: continue
        seen.add((a, b)); bycons.setdefault(b, []).append(a)
    cx0 = sum(p[0] for p in pos.values()) / len(pos); cy0 = sum(p[1] for p in pos.values()) / len(pos)
    for cons, srcs in bycons.items():
        cp = pos["valve:" + cons] if cons in flows else pos[cons]
        cw = size(cons)[0]
        base_ang = math.degrees(math.atan2(cp[1] - cy0, cp[0] - cx0))
        cand = [(r, ang) for r in (cw / 2 + 70, cw / 2 + 120, cw / 2 + 170, cw / 2 + 230, cw / 2 + 300) for ang in range(0, 360, 15)]
        cand.sort(key=lambda ra: (ra[0], abs(((ra[1] - base_ang + 180) % 360) - 180)))
        for s in srcs:
            sw = max(40, (len(s) + 2) * 6.6)
            for r, ang in cand:
                x = int(round((cp[0] + r * math.cos(math.radians(ang))) / 2) * 2)
                y = int(round((cp[1] + r * math.sin(math.radians(ang))) / 2) * 2)
                if x < 40 or y < 40: continue
                if spot_ok(x, y, sw, 14, taken):
                    taken.append((x, y, sw, 14)); shadows.append((s, cons, x, y)); break
            else:
                print("SIN HUECO", k, s, "->", cons)
    return dict(S=S, real=real, free=free, pos=pos, realedges=realedges, shadows=shadows, cost=bc)

def emit(k, B):
    S, pos = B["S"], B["pos"]
    flows, clouds, stocks = S["flows"], S["clouds"], S["stocks"]
    L = ["\\\\\\---/// Sketch information - do not modify anything except names",
         "V300  Do not put anything below this section - it will be ignored",
         "*" + S["title"],
         "$192-192-192,0,Times New Roman|12||0-0-0|0-0-0|0-0-255|-1--1--1|-1--1--1|96,96,100,0"]
    cid = [0]
    def new(): cid[0] += 1; return cid[0]
    nid, vid = {}, {}
    for n, (x, y) in stocks.items():
        i = new(); nid[n] = i
        L.append(f"10,{i},{n},{x},{y},100,40,3,3,0,0,0,0,0,0")
    for c, (x, y) in clouds.items():
        i = new(); nid[c] = i
        L.append(f"12,{i},48,{x},{y},10,8,0,3,0,0,-1,0,0,0")
    for f, (s_, d_, vx, vy, dx, dy) in flows.items():
        v = new(); vid[f] = v
        L.append(f"11,{v},0,{vx},{vy},6,8,34,3,0,0,1,0,0,0")
        i = new(); nid[f] = i
        L.append(f"10,{i},{f},{vx + dx},{vy + dy},90,11,40,3,0,0,-1,0,0,0")
    for n in B["free"]:
        i = new(); nid[n] = i; x, y = pos[n]
        L.append(f"10,{i},{n},{x},{y},{int(width(n))},11,8,3,0,0,0,0,0,0")
    sid = []
    for s, cons, x, y in B["shadows"]:
        i = new(); sid.append((i, s, cons, x, y))
        L.append(f"10,{i},{s},{x},{y},{int(width(s))},11,8,2,0,3,-1,0,0,0,128-128-128,0-0-0,|12||128-128-128")
    xy = dict(stocks); xy.update(clouds)
    for f, (s_, d_, vx, vy, dx, dy) in flows.items():
        xy[f] = (vx + dx, vy + dy)
    for n in B["free"]: xy[n] = pos[n]
    def mid(a, b):
        assert all(v % 2 == 0 for v in (a[0], a[1], b[0], b[1])), (a, b)
        return ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
    for f, (s_, d_, vx, vy, dx, dy) in flows.items():
        for nn, code in ((d_, 4), (s_, 100)):
            i = new(); mx, my = mid((vx, vy), xy[nn])
            L.append(f"1,{i},{vid[f]},{nid[nn]},{code},0,0,22,0,0,0,-1--1--1,,1|({mx},{my})|")
    for a_, b_ in B["realedges"]:
        i = new()
        to = vid[b_] if b_ in vid else nid[b_]
        pb = (flows[b_][2], flows[b_][3]) if b_ in flows else xy[b_]
        mx, my = mid(xy[a_], pb)
        L.append(f"1,{i},{nid[a_]},{to},1,0,0,22,0,0,0,-1--1--1,,1|({mx},{my})|")
    for i0, s, cons, x, y in sid:
        i = new()
        to = vid[cons] if cons in vid else nid[cons]
        pb = (flows[cons][2], flows[cons][3]) if cons in flows else xy[cons]
        mx, my = mid((x, y), pb)
        L.append(f"1,{i},{i0},{to},1,0,0,22,0,0,0,-1--1--1,,1|({mx},{my})|")
    return L

def eq_block():
    out = ["{UTF-8}"]
    for n, e, u, c, v in V:
        out.append(f"{n}=\n\t{e}\n\t~\t{u}\n\t~\t{c}\n\t|\n")
    out.append("""********************************************************
	.Control
********************************************************~
		Simulation Control Parameters
	|

FINAL TIME  = 240
	~	Month
	~	Fin de la simulacion: 20 anos.
	|

INITIAL TIME  = 0
	~	Month
	~	Inicio de la simulacion.
	|

SAVEPER  =
        TIME STEP
	~	Month [0,?]
	~	Frecuencia de almacenamiento.
	|

TIME STEP  = 0.25
	~	Month [0,?]
	~	Paso de integracion.
	|
""")
    return "\n".join(out)

if __name__ == "__main__":
    outdir = sys.argv[1]
    body = eq_block()
    open(outdir + "/Vivienda_V1_solo_ecuaciones.mdl", "w", encoding="utf-8", newline="\r\n").write(body)
    lines = []
    for k in SPEC:
        B = build_view(k)
        print("vista", k, "reales", len(B["real"]), "flechas", len(B["realedges"]), "sombras", len(B["shadows"]), "coste %.0f" % B["cost"])
        lines += emit(k, B)
    lines.append("///---\\\\\\")
    lines += [":L<%^E!@", "1:Current.vdf", "9:Current", "15:0,0,0,0,0,0", "19:100,0",
              "27:2,", "34:2,", "4:Time", "5:Viviendas venta", "35:Date", "36:YYYY-MM-DD",
              "37:2000", "38:1", "39:1", "40:2", "41:0", "42:1", "24:0", "25:240", "26:240"]
    open(outdir + "/Vivienda_V1.mdl", "w", encoding="utf-8", newline="\r\n").write(body + "\n" + "\n".join(lines) + "\n")
    print("variables:", len(V))
