"""Forno Nove: shared Python (loaded on every page before the page's own inline script)."""
import json
from math import cos, sin
from pyscript import document, window, when
from pyscript.ffi import create_proxy


def q(s):
    return document.querySelector(s)


SIZES = ['Small 10"', 'Large 14"']
DELIVERY = 50  # Updated flat localized delivery fee in PHP


def money(n):
    return "₱" + (f"{n:.2f}" if n % 1 else f"{int(n)}")


def _m(id, cat, name, desc, p, tags, sauce, dots, n, **x):
    return dict(id=id, cat=cat, name=name, desc=desc, p=p, tags=tags,
                art=dict(sauce=sauce, dots=dots, n=n, **x))


# 100% fixed price array syntax maps [Small 10", Large 14"]
MENU = [
    _m("margherita", "Classics", "Margherita", "San Marzano tomato, fior di latte, basil, olive oil.", [249, 399], ["veg"], 1, ["#2f6b3a"], 6),
    _m("marinara", "Classics", "Marinara", "Tomato, raw garlic, oregano, olive oil. No cheese.", [199, 329], ["veg", "vegan"], 1, ["#2f6b3a", "#e8dfb0"], 5, nocheese=1),
    _m("pepperoni", "Classics", "Pepperoni", "Tomato, fior di latte, cup-and-char pepperoni, hot honey.", [299, 479], ["hot"], 1, ["#9e1d12"], 11),
    _m("diavola", "Classics", "Diavola", "Tomato, spicy salami, fior di latte, chilli oil.", [329, 529], ["hot"], 1, ["#b3261a", "#e0662b"], 10),
    _m("quattro", "Bianche", "Quattro Formaggi", "Fior di latte, gorgonzola, parmesan, fontina, black pepper.", [349, 549], ["veg"], 0, ["#d9b44a", "#f7f0d8", "#7d8b9a"], 9),
    _m("funghi", "Bianche", "Funghi e Tartufo", "Roasted mushrooms, fontina, thyme, truffle oil.", [369, 579], ["veg"], 0, ["#8b6b4a", "#b79a74"], 10),
    _m("salsiccia", "Bianche", "Salsiccia", "Fennel sausage, broccolini, fior di latte, chilli flake.", [349, 549], ["hot"], 0, ["#a0522d", "#3f7d46"], 10),
    _m("ortolana", "Vegetarian", "Ortolana", "Tomato, zucchini, roasted peppers, red onion, olives.", [299, 479], ["veg"], 1, ["#3f7d46", "#d9822b", "#7b3f6e", "#2b2b2b"], 12),
    _m("pesto", "Vegetarian", "Pesto e Pomodorini", "Basil pesto, blistered cherry tomatoes, burrata.", [349, 569], ["veg"], 0, ["#3f7d46", "#d93a24", "#f7f0d8"], 10, green=1),
    _m("knots", "Sides & drinks", "Garlic knots", "Six knots from the same dough, garlic butter, parsley.", [129], ["veg"], 0, ["#d8a45e"], 6, plain=1),
    _m("burrata", "Sides & drinks", "Burrata & tomato", "Burrata, heirloom tomato, basil, flaky salt.", [229], ["veg"], 0, ["#d93a24", "#3f7d46"], 7, plain=1),
    _m("tiramisu", "Sides & drinks", "Tiramisu", "Espresso-soaked ladyfingers, mascarpone, cocoa.", [149], ["veg"], 0, ["#5b3a29"], 4, plain=1),
    _m("soda", "Sides & drinks", "Sparkling lemon soda", "Bottled, served cold.", [69], ["veg", "vegan"], 0, ["#e6cf4a"], 3, plain=1),
    _m("ginger", "Sides & drinks", "Ginger beer", "Sharp, spicy, not too sweet.", [79], ["veg", "vegan"], 0, ["#c9a24a"], 3, plain=1),
]
BY_ID = {m["id"]: m for m in MENU}


# ---- pizza drawing (Original working closure state kept intact) ----
def rng(seed):
    s = [seed]

    def f():
        s[0] = (s[0] * 9301 + 49297) % 233280
        return s[0] / 233280
    return f


def pizzaSVG(a, seed, size):
    r = rng(seed * 97 + 13)
    plain = a.get("plain")
    if plain:
        o = '<circle cx="50" cy="50" r="46" fill="var(--surface)" stroke="var(--line)" stroke-width="2"/><circle cx="50" cy="50" r="36" fill="none" stroke="var(--line)" stroke-width="1.5"/>'
    else:
        fill = "#7fa35a" if a.get("green") else ("var(--sauce)" if a.get("sauce") else "var(--cheese)")
        o = '<circle cx="50" cy="50" r="47" fill="var(--crust)"/><circle cx="50" cy="50" r="47" fill="none" stroke="rgba(0,0,0,.18)" stroke-width="1.5" stroke-dasharray="3 5"/>'
        o += f'<circle cx="50" cy="50" r="38" fill="{fill}"/>'
        if not a.get("nocheese") and a.get("sauce"):
            for _ in range(7):
                t = r() * 6.28
                d = r() * 26
                rx = 7 + r() * 5
                ry = 5 + r() * 4
                o += f'<ellipse cx="{50 + cos(t) * d:.1f}" cy="{50 + sin(t) * d:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="var(--cheese)" opacity=".92"/>'
    dots = a["dots"]
    for i in range(a["n"]):
        t = r() * 6.28
        d = r() * 30 if plain else 6 + r() * 26
        rad = 3.5 if plain else 3 + r() * 2.5
        o += f'<circle cx="{50 + cos(t) * d:.1f}" cy="{50 + sin(t) * d:.1f}" r="{rad:.1f}" fill="{dots[i % len(dots)]}"/>'
    return f'<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false" width="{size}" height="{size}">{o}</svg>'


# ---- cart (Original layout evaluation logic fully preserved) ----
try:
    cart = json.loads(window.localStorage.getItem("fn-cart") or "{}")
except Exception:
    cart = {}
cart = {k: v for k, v in cart.items() if k.split(":")[0] in BY_ID and isinstance(v, int) and v > 0}


def save_cart():
    try:
        window.localStorage.setItem("fn-cart", json.dumps(cart))
    except Exception:
        pass


def is_delivery():
    el = q("#modeDelivery")
    return bool(el) and bool(el.checked)


def totals():
    lines, sub, n = [], 0, 0
    for k, qty in cart.items():
        i, s = k.split(":")
        m, s = BY_ID[i], int(s)
        unit = m["p"][s]
        lines.append(dict(key=k, m=m, s=s, q=qty, unit=unit))
        sub += unit * qty
        n += qty
    dl = DELIVERY if is_delivery() and n > 0 else 0
    return dict(lines=lines, sub=sub, n=n, dl=dl, total=sub + dl)


def render_bar():
    t = totals()
    q("#bar").hidden = t["n"] == 0
    q("#barText").textContent = f'{t["n"]} {"item" if t["n"] == 1 else "items"} · {money(t["total"])}'


# ---- theme toggle (saved in localStorage) ----
root = document.documentElement
try:
    _saved = window.localStorage.getItem("fn-theme")
    if _saved:
        root.setAttribute("data-theme", _saved)
except Exception:
    pass


@when("click", "#theme")
def toggle_theme(event):
    cur = root.getAttribute("data-theme") or ("dark" if window.matchMedia("(prefers-color-scheme: dark)").matches else "light")
    nxt = "light" if cur == "dark" else "dark"
    root.setAttribute("data-theme", nxt)
    try:
        window.localStorage.setItem("fn-theme", nxt)
    except Exception:
        pass


render_bar()
