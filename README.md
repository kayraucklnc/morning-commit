# The Morning Commit

A daily newspaper of what builders were playing with on X, GitHub and Hacker News, assembled by Grok Bot.

- Read it: https://kayraucklnc.github.io/morning-commit/ (installable as an app: Share → Add to Home Screen)
- Every past edition: https://kayraucklnc.github.io/morning-commit/archive/

Static site, no build step on GitHub. Editions live in `editions/YYYY-MM-DD/`, listed in `editions.json`;
`tools/sitegen.py` adds an edition and regenerates the home page, archive and navigation.
