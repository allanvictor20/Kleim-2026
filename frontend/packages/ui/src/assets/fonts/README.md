# Plus Jakarta Sans

`plus-jakarta-sans-latin.woff2` — the latin subset of the variable font, one file
covering weights 400 to 800 (27 KB). Self-hosted rather than loaded from Google
Fonts: NFR-07 caps the customer app's first load at 1.5 MB over 3G, and a
third-party font request costs an extra DNS lookup, connection and round trip on
the critical path.

Source: Google Fonts (`fonts.gstatic.com`, v12). Licence: SIL Open Font License
1.1 — see <https://fonts.google.com/specimen/Plus+Jakarta+Sans/license>.

To refresh, fetch the `latin` `@font-face` block's URL from
`https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400..800&display=swap`
with a modern browser User-Agent (Google serves woff2 only to browsers that
support it) and keep the `unicode-range` in `tokens.css` in step.
