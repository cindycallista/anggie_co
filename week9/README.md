# Week 9 / Laundry Queue

洪英佩 — 111211147

Laundry Queue is a dorm booking board for washers and dryers. It blocks overlapping reservations on the same machine, displays live booking states, filters by machine, and keeps the schedule in localStorage.

## Cloudflare Pages

```bash
npx wrangler pages deploy . --project-name anggie-laundry-week9
```

The app is plain HTML, CSS, and JavaScript. It has no build step and can be reviewed by opening `index.html`.
