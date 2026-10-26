# Jayesh | Cybersecurity Progress Dashboard

🌐 **[Visit the live dashboard](https://jayeshchabukswar.github.io/)**

A clean, responsive portfolio and learning dashboard documenting my progress toward an entry-level SOC Analyst (L1) role.

## Links

- **Website:** https://jayeshchabukswar.github.io/
- **GitHub:** https://github.com/JayeshChabukswar
- **Learning journal:** https://github.com/JayeshChabukswar/cybersecurity.path
- **TryHackMe:** https://tryhackme.com/p/xbec

## Dashboard sections

- Manually recorded TryHackMe path progress and completed rooms
- Daily learning records linked to the learning journal
- Current learning topics and recorded projects/write-ups
- Recent commit activity from only the portfolio and learning-journal repositories
- Learning streak placeholder until enough dated records exist to calculate it accurately

The dashboard reads `data/progress.json` at runtime. TryHackMe data is **manual-only**; this project does not scrape TryHackMe or infer completion.

## Data and automation

- `data/progress.json` — the website's dashboard data, refreshed by the scheduled workflow.
- `scripts/update_progress.py` — reads the public progress JSON from `JayeshChabukswar/cybersecurity.path`, checks public GitHub commit activity for only the two approved repositories, and updates the website data file.
- `.github/workflows/daily-progress.yml` — runs daily at **23:00 India Standard Time (17:30 UTC)** and can also be run manually from the Actions tab.

The script is deterministic for unchanged inputs. The workflow commits only if `data/progress.json` actually changes. Failed fetches or validation errors fail the workflow visibly instead of silently publishing partial data. Public GitHub API requests do not require a personal access token; the workflow-provided `GITHUB_TOKEN` is available for rate-limit headroom.

### Update TryHackMe progress

1. Update the progress paths, room list, and learning-log references in `data/progress.json` in the `cybersecurity.path` repository.
2. Commit those changes to `main`.
3. The website workflow will read the updated public JSON on its next run, or you can run **Actions → Daily cybersecurity dashboard update → Run workflow**.

Only record room completions and progress percentages you have verified yourself. Daily learning entries remain in the learning-journal repository; the website links to them rather than creating duplicate copies.

## GitHub Pages

This repository is intended to publish from branch `main`, folder `/(root)`. Confirm the repository's **Settings → Pages** configuration if the site does not update after a commit. GitHub Pages deployment and scheduled workflow execution are controlled by GitHub; check the Pages deployment status and Actions run history to confirm each one.

*This is a learning portfolio, not a claim of professional experience.*
