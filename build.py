#!/usr/bin/env python3
"""Generira njemačke i engleske stranice iz hrvatskih izvornika.

  index.html              ->  de.html, en.html
  pravne-informacije.html ->  impressum.html, legal.html

Hrvatski izvornik je jedini izvor: tekst stoji u elementima, a prijevodi u
atributima data-de / data-en. Tekstovi koji nisu u elementima (naslov, opisi,
alt, placeholder, poveznice) prevode se u rječnicima STRINGS / LEGAL_STRINGS.

Pokretanje:  python3 build.py
Skripta staje s greškom ako neki hrvatski izvorni tekst iz rječnika više ne
postoji u izvorniku, da se prijevodi ne bi tiho razišli s njim.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://krizanec-montaza.hr"
OG_LOCALE = {"hr": "hr_HR", "de": "de_DE", "en": "en_GB"}

# index.html: hrvatski izvornik -> prijevod. Svaki ključ mora postojati u izvorniku.
STRINGS = {
    "de": {
        "<title>Montaža industrijskih strojeva — KRIŽANEC-MONTAŽA</title>":
            "<title>Industriemontage und Maschinenverlagerung — KRIŽANEC-MONTAŽA</title>",
        '<meta property="og:title" content="Montaža industrijskih strojeva — KRIŽANEC-MONTAŽA">':
            '<meta property="og:title" content="Industriemontage und Maschinenverlagerung — KRIŽANEC-MONTAŽA">',
        'content="Montaža, demontaža i selidba industrijskih strojeva i proizvodnih linija. Od 2014., ekipa od 14 ljudi, izlasci u Hrvatskoj i zemljama EU."':
            'content="Montage, Demontage und Verlagerung von Industriemaschinen und Produktionslinien. Seit 2014, Team von 14 Monteuren, Einsätze in Kroatien und in der EU."',
        'content="Montaža, demontaža i selidba industrijskih strojeva i proizvodnih linija. Od 2014., izlasci u Hrvatskoj i zemljama EU."':
            'content="Montage, Demontage und Verlagerung von Industriemaschinen und Produktionslinien. Seit 2014, Einsätze in Kroatien und in der EU."',
        '"description":"Montaža, demontaža i selidba industrijskih strojeva i proizvodnih linija. Hrvatska i EU."':
            '"description":"Montage, Demontage und Verlagerung von Industriemaschinen und Produktionslinien. Kroatien und EU."',
        '{"@type":"Country","name":"Hrvatska"},{"@type":"Place","name":"Europska unija"}':
            '{"@type":"Country","name":"Kroatien"},{"@type":"Place","name":"Europäische Union"}',
        'href="/pravne-informacije': 'href="/impressum',
        'placeholder="npr. Graz, AT"': 'placeholder="z. B. Graz, AT"',
        'placeholder="npr. 11/2026"': 'placeholder="z. B. 11/2026"',
        'alt="Montaža industrijskog stroja u proizvodnoj hali"':
            'alt="Montage einer Industriemaschine in einer Produktionshalle"',
        'alt="Dvojica montera s pojasevima postavljaju solarne panele na krov hale"':
            'alt="Zwei Monteure mit Sicherungsgurten montieren Solarmodule auf einem Hallendach"',
        'alt="Dvojica montera sastavljaju aluminijsku ogradu uz transportnu liniju"':
            'alt="Zwei Monteure montieren ein Aluminiumgeländer an einer Förderlinie"',
        'alt="Dvojica montera uz motor na transportnom postolju u pogonu"':
            'alt="Zwei Monteure an einem Motor auf einem Transportgestell im Werk"',
        'alt="Ekipa Križanec-montaže postavlja lančanu transportnu liniju u proizvodnoj hali"':
            'alt="Das Team von Križanec-Montaža montiert einen Kettenförderer in einer Produktionshalle"',
        'alt="Hala s nizom industrijskih robota na postoljima tijekom montaže linije"':
            'alt="Halle mit einer Reihe von Industrierobotern auf Sockeln während der Linienmontage"',
        'alt="Monter Križanec-montaže radi akumulatorskim alatom unutar čelične konstrukcije"':
            'alt="Ein Monteur von Križanec-Montaža arbeitet mit Akkuwerkzeug in einer Stahlkonstruktion"',
        'alt="Motor s dijelovima obojenima u različite boje, na transportnom postolju"':
            'alt="Motor mit farbig markierten Bauteilen auf einem Transportgestell"',
        'alt="Postavljeni solarni paneli na krovu zgrade"':
            'alt="Montierte Solarmodule auf einem Gebäudedach"',
        'alt="Stezna naprava na stupovima usidrenima u pod hale"':
            'alt="Spannvorrichtung auf im Hallenboden verankerten Stützen"',
        'alt="Tehnički kanal s cijevima i kabelskim policama"':
            'alt="Technikkanal mit Rohrleitungen und Kabeltrassen"',
        'alt="Valjkasti transporter s pneumatskim cilindrima i lančanim pogonom"':
            'alt="Rollenförderer mit Pneumatikzylindern und Kettenantrieb"',
        'alt="Vertikalni podizač sa žutom nosivom platformom u proizvodnoj hali"':
            'alt="Vertikalheber mit gelber Tragplattform in einer Produktionshalle"',
    },
    "en": {
        "<title>Montaža industrijskih strojeva — KRIŽANEC-MONTAŽA</title>":
            "<title>Industrial machine assembly and relocation — KRIŽANEC-MONTAŽA</title>",
        '<meta property="og:title" content="Montaža industrijskih strojeva — KRIŽANEC-MONTAŽA">':
            '<meta property="og:title" content="Industrial machine assembly and relocation — KRIŽANEC-MONTAŽA">',
        'content="Montaža, demontaža i selidba industrijskih strojeva i proizvodnih linija. Od 2014., ekipa od 14 ljudi, izlasci u Hrvatskoj i zemljama EU."':
            'content="Assembly, dismantling and relocation of industrial machines and production lines. Since 2014, a team of 14, on site in Croatia and across the EU."',
        'content="Montaža, demontaža i selidba industrijskih strojeva i proizvodnih linija. Od 2014., izlasci u Hrvatskoj i zemljama EU."':
            'content="Assembly, dismantling and relocation of industrial machines and production lines. Since 2014, on site in Croatia and across the EU."',
        '"description":"Montaža, demontaža i selidba industrijskih strojeva i proizvodnih linija. Hrvatska i EU."':
            '"description":"Assembly, dismantling and relocation of industrial machines and production lines. Croatia and the EU."',
        '{"@type":"Country","name":"Hrvatska"},{"@type":"Place","name":"Europska unija"}':
            '{"@type":"Country","name":"Croatia"},{"@type":"Place","name":"European Union"}',
        'href="/pravne-informacije': 'href="/legal',
        'placeholder="npr. Graz, AT"': 'placeholder="e.g. Graz, AT"',
        'placeholder="npr. 11/2026"': 'placeholder="e.g. 11/2026"',
        'alt="Montaža industrijskog stroja u proizvodnoj hali"':
            'alt="Assembly of an industrial machine in a production hall"',
        'alt="Dvojica montera s pojasevima postavljaju solarne panele na krov hale"':
            'alt="Two fitters in safety harnesses install solar panels on a hall roof"',
        'alt="Dvojica montera sastavljaju aluminijsku ogradu uz transportnu liniju"':
            'alt="Two fitters assemble an aluminium guard rail along a conveyor line"',
        'alt="Dvojica montera uz motor na transportnom postolju u pogonu"':
            'alt="Two fitters beside an engine on a transport frame in the plant"',
        'alt="Ekipa Križanec-montaže postavlja lančanu transportnu liniju u proizvodnoj hali"':
            'alt="The Križanec-Montaža crew installs a chain conveyor line in a production hall"',
        'alt="Hala s nizom industrijskih robota na postoljima tijekom montaže linije"':
            'alt="Hall with a row of industrial robots on pedestals during line assembly"',
        'alt="Monter Križanec-montaže radi akumulatorskim alatom unutar čelične konstrukcije"':
            'alt="A Križanec-Montaža fitter works with a cordless tool inside a steel structure"',
        'alt="Motor s dijelovima obojenima u različite boje, na transportnom postolju"':
            'alt="Engine with parts painted in different colours on a transport frame"',
        'alt="Postavljeni solarni paneli na krovu zgrade"':
            'alt="Installed solar panels on a building roof"',
        'alt="Stezna naprava na stupovima usidrenima u pod hale"':
            'alt="Clamping fixture on columns anchored to the hall floor"',
        'alt="Tehnički kanal s cijevima i kabelskim policama"':
            'alt="Service duct with piping and cable trays"',
        'alt="Valjkasti transporter s pneumatskim cilindrima i lančanim pogonom"':
            'alt="Roller conveyor with pneumatic cylinders and chain drive"',
        'alt="Vertikalni podizač sa žutom nosivom platformom u proizvodnoj hali"':
            'alt="Vertical lift with a yellow load platform in a production hall"',
    },
}

# pravne-informacije.html: hrvatski izvornik -> prijevod.
LEGAL_STRINGS = {
    "de": {
        "<title>Pravne informacije — KRIŽANEC-MONTAŽA</title>":
            "<title>Impressum und Datenschutz — KRIŽANEC-MONTAŽA</title>",
        'content="Podaci o društvu KRIŽANEC-MONTAŽA j.d.o.o. i obavijest o zaštiti osobnih podataka."':
            'content="Angaben zum Unternehmen KRIŽANEC-MONTAŽA j.d.o.o. und Hinweise zum Datenschutz."',
        '<a class="logo" href="/">': '<a class="logo" href="/de">',
        '<a class="home" href="/" ': '<a class="home" href="/de" ',
    },
    "en": {
        "<title>Pravne informacije — KRIŽANEC-MONTAŽA</title>":
            "<title>Legal notice and privacy — KRIŽANEC-MONTAŽA</title>",
        'content="Podaci o društvu KRIŽANEC-MONTAŽA j.d.o.o. i obavijest o zaštiti osobnih podataka."':
            'content="Company details of KRIŽANEC-MONTAŽA j.d.o.o. and privacy notice."',
        '<a class="logo" href="/">': '<a class="logo" href="/en">',
        '<a class="home" href="/" ': '<a class="home" href="/en" ',
    },
}

PAGES = [
    {
        "source": "index.html",
        "out": {"de": "de.html", "en": "en.html"},
        "urls": {"hr": SITE + "/", "de": SITE + "/de", "en": SITE + "/en"},
        "strings": STRINGS,
        "home": True,  # ima Open Graph oznake i preusmjeravanje po jeziku
    },
    {
        "source": "pravne-informacije.html",
        "out": {"de": "impressum.html", "en": "legal.html"},
        "urls": {"hr": SITE + "/pravne-informacije", "de": SITE + "/impressum", "en": SITE + "/legal"},
        "strings": LEGAL_STRINGS,
        "home": False,
    },
]

# <tag ... data-hr="…" data-de="…" data-en="…">hrvatski tekst</tag>
ELEMENT = re.compile(
    r'<(?P<tag>[a-z0-9]+)(?P<pre>[^<>]*?) data-hr="(?P<hr>[^"]*)" data-de="(?P<de>[^"]*)" data-en="(?P<en>[^"]*)"(?P<post>[^<>]*)>'
    r'(?P<body>.*?)</(?P=tag)>',
    re.S,
)


def fail(message):
    sys.exit("build.py: " + message)


def build(source, lang, page):
    out = source
    urls = page["urls"]
    name = page["source"]

    for old, new in page["strings"][lang].items():
        if out.count(old) < 1:
            fail(f"[{name} {lang}] izvorni tekst nije pronađen: {old[:70]}…")
        out = out.replace(old, new)

    def swap(match):
        # Atribut se čita kao u pregledniku (entiteti -> znakovi), pa ispisuje kao sadržaj.
        value = html.unescape(match.group(lang)).replace("&", "&amp;")
        return f'<{match.group("tag")}{match.group("pre")}{match.group("post")}>{value}</{match.group("tag")}>'

    out, swapped = ELEMENT.subn(swap, out)
    expected = source.count(' data-hr="')
    if swapped != expected or " data-hr=" in out or " data-de=" in out or " data-en=" in out:
        fail(f"[{name} {lang}] zamijenjeno {swapped} od {expected} prevedenih elemenata; provjeriti redoslijed atributa data-hr/data-de/data-en")

    head = [
        ('<html lang="hr">', f'<html lang="{lang}">'),
        (f'<link rel="canonical" href="{urls["hr"]}">', f'<link rel="canonical" href="{urls[lang]}">'),
        ('data-lang="hr" aria-current="page"', 'data-lang="hr"'),
        (f'data-lang="{lang}"', f'data-lang="{lang}" aria-current="page"'),
    ]
    if page["home"]:
        # samo početna (hrvatska) stranica preusmjerava po spremljenom izboru jezika
        out, n = re.subn(r"<!--hr-only-->.*?<!--/hr-only-->\n?", "", out, flags=re.S)
        if n != 1:
            fail("oznaka <!--hr-only--> nije pronađena")
        head += [
            (f'<meta property="og:url" content="{urls["hr"]}">', f'<meta property="og:url" content="{urls[lang]}">'),
            ('<meta property="og:locale" content="hr_HR">', f'<meta property="og:locale" content="{OG_LOCALE[lang]}">'),
            (f'<meta property="og:locale:alternate" content="{OG_LOCALE[lang]}">', '<meta property="og:locale:alternate" content="hr_HR">'),
        ]
    for old, new in head:
        if out.count(old) != 1:
            fail(f"[{name} {lang}] očekivan točno jedan: {old}")
        out = out.replace(old, new)

    out, n = re.subn(
        r"<!-- IZVOR.*?-->",
        f"<!-- GENERIRANO iz {name} skriptom build.py — ne uređivati ručno. -->",
        out,
        count=1,
        flags=re.S,
    )
    if n != 1:
        fail("uvodni komentar nije pronađen")
    return out


def main():
    for page in PAGES:
        source = (ROOT / page["source"]).read_text(encoding="utf-8")
        for lang, target in page["out"].items():
            html_out = build(source, lang, page)
            (ROOT / target).write_text(html_out, encoding="utf-8")
            print(f"{target:<16} {len(html_out.encode('utf-8'))} B")


if __name__ == "__main__":
    main()
