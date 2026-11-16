# The trees of science

A single web page that shows four classifications of science as trees that can be expanded, collapsed and
searched:

| Tab | Classification |
|---|---|
| Mathematics | Mathematics Subject Classification 2020 (MSC2020) |
| Physics | Physics Subject Headings (PhySH) |
| Software | ACM Computing Classification System 2012 |
| All sciences | Australian and New Zealand Standard Research Classification: Fields of Research 2020 (ANZSRC FoR) |

Teal marks topics judged useful for flood and debris-flow modelling, GIS, remote sensing, geohazards and
WebGIS development, based on <https://www.liaskos.eu/>. It is a personal selection, not part of the
classifications.

- Site: <https://liaskos.nkua.cloud/trees/>

## Repository

| Place | Contents |
|---|---|
| `site/index.html` | The page: its style, its script, the four trees (compressed and embedded in the page) and the subsets of its two typefaces |
| `nginx.conf` | The configuration of the web server in the container |
| `compose.yaml` | The file that starts the container on the server |
| `route.block` | The block of the front web server that forwards `/trees/` to the container |
| `tests/` | The checks of the page |
| `.github/workflows/` | The automatic checks |

The page needs no other file. It shows the number of recorded page visits, which it reads from
<https://evelpidou.nkua.cloud/api/visits/science-trees>. That address answers only the page at the address
of the site, so a copy opened elsewhere, for example on your own computer, shows a dash in place of the
number.

## Not included

- `index.html.before-visit-counter-20261116`: the copy of the page that was kept on the server before the
  visit counter was added on 16 November 2026. The current page replaces it.
- The program that converted the four classifications into the trees of the page. It was not found on the
  server, where the page is a single file.

## Running the page on your own computer

Open `site/index.html` in a browser, or serve the folder:

```sh
git clone https://github.com/AlexandrosLiaskos/science-trees
cd science-trees
python -m http.server --directory site 8000
```

The page is then at <http://localhost:8000/>. To run it with the web server of the site, in Docker:

```sh
docker run --rm -p 8080:80 -v "$PWD/site:/usr/share/nginx/html:ro" -v "$PWD/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.27-alpine
```

## Checks

The workflow `Checks` runs on every push and pull request. It runs the tests in `tests/` with Python 3.12
and Node.js 22: they decode the embedded trees and check that every tab has a tree and every entry a name,
check the syntax of the scripts of the page and check that the page needs no file outside it. The workflow
also validates `compose.yaml` with Docker Compose, tests `nginx.conf` and `route.block` with `nginx -t` in
the image `nginx:1.27-alpine`, and starts the container to check that it serves the page.

```sh
python -m unittest discover --start-directory tests --verbose
```

## Deployment

On the server, the folder `/opt/science-trees` holds `site/`, `nginx.conf`, `compose.yaml` and `route.block`.
The container `science-trees` runs the image `nginx:1.27-alpine`, serves `site/` read-only with
`nginx.conf`, and joins the Docker network `nkua-proxy`. The front web server of `liaskos.nkua.cloud`
forwards `/trees/` to it with the block in `route.block`. To deploy a change of the page, copy
`site/index.html` into `/opt/science-trees/site/`; the web server reads it at each request, so no restart
is needed.

## Third-party content

The page embeds material that remains under the terms of its owners, as the page itself states:

- MSC2020: Mathematical Reviews and zbMATH, licensed under the Creative Commons
  Attribution-NonCommercial-ShareAlike 4.0 licence (CC BY-NC-SA 4.0); adapted into a tree, with the
  notation converted.
- PhySH: American Physical Society, released under CC0 1.0; arranged by discipline and facet.
- The 2012 ACM Computing Classification System: Association for Computing Machinery, made available for
  educational and research purposes.
- ANZSRC Fields of Research 2020: Australian Bureau of Statistics and Stats NZ; division names set in
  sentence case.
- Subsets of two typefaces under the SIL Open Font License 1.1: a typeface of the Adobe Source family
  (© 2023 Adobe, Reserved Font Name 'Source') and EB Garamond (© 2017 The EB Garamond Project Authors).

## Citation and licence

To cite the page, use the entry in [CITATION.cff](CITATION.cff). The code of the page (its structure, style
and script), the web server configuration and the other files of this repository are licensed under the
[GNU Affero General Public License, version 3](LICENSE). The licence does not cover the classifications and
typefaces listed above, which keep their own terms.
