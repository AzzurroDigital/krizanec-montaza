# krizanec-montaza.hr

Statična stranica KRIŽANEC-MONTAŽA j.d.o.o. na tri jezika, svaki na svojoj adresi:
`/` (HR), `/de` (DE), `/en` (EN), povezane hreflang oznakama i sitemapom.

Hosting: Cloudflare Worker `krizanec` (static assets), domene krizanec-montaza.hr i www (wrangler.jsonc).
Svaki commit na `main` ide live. Izrada: Azzurro Digital.

## Uređivanje teksta

Uređuju se samo hrvatski izvornici. Hrvatski tekst stoji u elementima, a prijevodi u atributima
`data-de` / `data-en` na istom elementu. Njemačke i engleske stranice se generiraju i ne uređuju se ručno.

| Izvornik | Generira se | Adrese |
|---|---|---|
| `index.html` | `de.html`, `en.html` | `/`, `/de`, `/en` |
| `pravne-informacije.html` | `impressum.html`, `legal.html` | `/pravne-informacije`, `/impressum`, `/legal` |

Nakon svake izmjene izvornika:

    python3 build.py

pa commitati izvornik i generirane stranice zajedno. Naslov stranice, opisi, alt tekstovi
i placeholderi prevode se u rječniku `STRINGS` na vrhu `build.py`; skripta staje s greškom ako
se hrvatski izvornik promijenio, a prijevod nije.

## Obrazac za upit

Šalje se preko FormSubmita na krizanec.montaza@gmail.com. Ako slanje ne uspije, otvara se
program za e-poštu posjetitelja s ispunjenim upitom.
