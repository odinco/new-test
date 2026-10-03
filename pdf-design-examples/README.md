# PDF Design Lookbook

Six letter-size PDF layouts that are fun but professional: a cover, an impact report, an invoice, an event flyer, a proposal, and a page of design rules.

- `lookbook.pdf`: the rendered result
- `lookbook.html`: the source (HTML + CSS)
- `fonts/`: Fraunces, Bricolage Grotesque, DM Sans, Space Grotesk, JetBrains Mono (Google Fonts, OFL), stored locally so the file renders offline

To re-render:

```sh
chromium --headless=new --no-pdf-header-footer --print-to-pdf=lookbook.pdf lookbook.html
```
