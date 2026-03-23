# Influencer Marketing Effectiveness Report

Analyses influencer campaign performance across platforms, content types, and creator tiers to determine what's actually working — and where to put budget next.

## What it does

- Calculates full-funnel metrics: views → clicks → signups → paid conversions
- Ranks influencers by ROAS and cost-per-conversion
- Compares platform performance (YouTube, TikTok, podcasts, Twitter)
- Breaks down results by content type (dedicated videos, integrations, threads, host-read ads)
- Analyses ROI differences across influencer tiers (macro / mid / micro)
- Generates prioritised recommendations for the next quarter

## Quick start

```bash
pip install -r requirements.txt
python influencer_analysis.py
```

## Sample output

```
===========================================================================
FULL-FUNNEL OVERVIEW
===========================================================================

Views:            8,343,000
Link clicks:        113,500  (1.36% CTR)
Signups:              4,488  (3.95% of clicks)
Paid conversions:       616  (13.73% of signups)
```

## How it works

1. **Data load**: Reads campaign-level CSV data into SQLite
2. **SQL analysis**: Runs queries to aggregate performance by influencer, platform, content type, and tier
3. **Engagement scoring**: Calculates engagement rates in pandas (likes + comments + shares / views)
4. **Funnel maths**: Computes step-by-step conversion rates through the full acquisition funnel
5. **Recommendations**: Outputs actionable next steps based on the data

## Data

Sample data in `/data/campaigns.csv` includes 24 campaigns across 8 influencers over H1 2025. Each record tracks:

| Field | Description |
|-------|-------------|
| `fee_usd` | Amount paid to the influencer |
| `views`, `likes`, `comments`, `shares` | Top-of-funnel engagement |
| `link_clicks` | Clicks to the product/landing page |
| `signups` | Free account registrations attributed |
| `paid_conversions` | Conversions to paid plans |
| `revenue_attributed_usd` | Revenue attributed to the campaign |

## Tech

- **Python** — pandas for data manipulation and engagement calculations
- **SQL** (SQLite) — aggregation queries for platform/tier/content-type breakdowns
- **No external APIs** — runs on local CSV data

## Context

Built as a practical example of the kind of analysis a growth team runs to evaluate influencer spend. The JD for a growth role I was applying to literally mentioned "build a report to analyse the efficacy of our influencer marketing" — so I built one.

## Other projects

- [b2b-pipeline-analyzer](https://github.com/anecdotal-trout/b2b-pipeline-analyzer) — Marketing spend → pipeline ROI analysis
- [saas-growth-dashboard](https://github.com/anecdotal-trout/saas-growth-dashboard) — SaaS growth metrics tracker
