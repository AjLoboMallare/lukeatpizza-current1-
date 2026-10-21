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
