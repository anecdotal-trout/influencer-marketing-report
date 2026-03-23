"""
Influencer Marketing Effectiveness Report
==========================================
Analyses influencer campaign data to determine:
- Which influencers and platforms deliver the best ROI?
- What content types convert best (dedicated videos vs integrations vs threads)?
- How does influencer tier (macro/mid/micro) affect cost-efficiency?
- Month-over-month performance trends

Outputs a structured report with metrics and recommendations.
"""

import sqlite3
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_data():
    """Load campaign data into SQLite for analysis."""
    df = pd.read_csv(os.path.join(DATA_DIR, "campaigns.csv"))
    conn = sqlite3.connect(":memory:")
    df.to_sql("campaigns", conn, if_exists="replace", index=False)
    return conn, df


# ---------------------------------------------------------------------------
# SQL QUERIES
# ---------------------------------------------------------------------------

INFLUENCER_PERFORMANCE_SQL = """
    SELECT
        influencer_name,
        platform,
        tier,
        COUNT(*)                                                AS campaigns,
        ROUND(SUM(fee_usd), 0)                                 AS total_spend,
        SUM(signups)                                            AS total_signups,
        SUM(paid_conversions)                                   AS total_conversions,
        ROUND(SUM(revenue_attributed_usd), 0)                   AS total_revenue,
        ROUND(SUM(fee_usd) * 1.0 / NULLIF(SUM(paid_conversions), 0), 2)
                                                                AS cost_per_conversion,
        ROUND(SUM(revenue_attributed_usd) * 1.0 / SUM(fee_usd), 2)
                                                                AS roas
    FROM campaigns
    GROUP BY influencer_name, platform, tier
    ORDER BY roas DESC
"""

PLATFORM_SUMMARY_SQL = """
    SELECT
        platform,
        COUNT(*)                                                AS campaigns,
        ROUND(SUM(fee_usd), 0)                                 AS total_spend,
        SUM(views)                                              AS total_views,
        SUM(link_clicks)                                        AS total_clicks,
        SUM(signups)                                            AS total_signups,
        SUM(paid_conversions)                                   AS total_conversions,
        ROUND(SUM(revenue_attributed_usd), 0)                   AS revenue,
        ROUND(SUM(link_clicks) * 100.0 / NULLIF(SUM(views), 0), 2)
                                                                AS ctr_pct,
        ROUND(SUM(paid_conversions) * 100.0 / NULLIF(SUM(signups), 0), 2)
                                                                AS signup_to_paid_pct,
        ROUND(SUM(revenue_attributed_usd) * 1.0 / SUM(fee_usd), 2)
                                                                AS roas
    FROM campaigns
    GROUP BY platform
    ORDER BY roas DESC
"""

CONTENT_TYPE_SQL = """
    SELECT
        content_type,
        COUNT(*)                                                AS campaigns,
        ROUND(AVG(fee_usd), 0)                                 AS avg_fee,
        ROUND(AVG(signups), 0)                                  AS avg_signups,
        ROUND(AVG(paid_conversions), 1)                         AS avg_conversions,
        ROUND(SUM(revenue_attributed_usd) * 1.0 / SUM(fee_usd), 2)
                                                                AS roas,
        ROUND(SUM(fee_usd) * 1.0 / NULLIF(SUM(paid_conversions), 0), 2)
                                                                AS cost_per_conversion
    FROM campaigns
    GROUP BY content_type
    ORDER BY roas DESC
"""

TIER_ANALYSIS_SQL = """
    SELECT
        tier,
        COUNT(*)                                                AS campaigns,
        ROUND(AVG(fee_usd), 0)                                 AS avg_fee,
        ROUND(AVG(follower_count), 0)                           AS avg_followers,
        SUM(signups)                                            AS total_signups,
        SUM(paid_conversions)                                   AS total_conversions,
        ROUND(SUM(revenue_attributed_usd) * 1.0 / SUM(fee_usd), 2)
                                                                AS roas,
        ROUND(SUM(fee_usd) * 1.0 / NULLIF(SUM(paid_conversions), 0), 2)
                                                                AS cost_per_conversion
    FROM campaigns
    GROUP BY tier
    ORDER BY roas DESC
"""

MONTHLY_TREND_SQL = """
    SELECT
        campaign_month                                          AS month,
        COUNT(*)                                                AS campaigns,
        ROUND(SUM(fee_usd), 0)                                 AS spend,
        SUM(signups)                                            AS signups,
        SUM(paid_conversions)                                   AS conversions,
        ROUND(SUM(revenue_attributed_usd), 0)                   AS revenue,
        ROUND(SUM(revenue_attributed_usd) * 1.0 / SUM(fee_usd), 2)
                                                                AS roas
    FROM campaigns
    GROUP BY campaign_month
    ORDER BY campaign_month
"""


# ---------------------------------------------------------------------------
# ANALYSIS HELPERS
# ---------------------------------------------------------------------------

def compute_engagement_rates(df):
    """Calculate engagement rate per campaign (likes + comments + shares / views)."""
    df = df.copy()
    df["engagement_rate"] = (
        (df["likes"] + df["comments"] + df["shares"])
        / df["views"].replace(0, pd.NA)
        * 100
    ).round(2)
    return df


def funnel_analysis(df):
    """Calculate conversion funnel: views → clicks → signups → paid."""
    totals = {
        "total_views": df["views"].sum(),
        "total_clicks": df["link_clicks"].sum(),
        "total_signups": df["signups"].sum(),
        "total_paid": df["paid_conversions"].sum(),
    }
    totals["click_rate"] = round(totals["total_clicks"] / max(totals["total_views"], 1) * 100, 2)
    totals["signup_rate"] = round(totals["total_signups"] / max(totals["total_clicks"], 1) * 100, 2)
    totals["conversion_rate"] = round(totals["total_paid"] / max(totals["total_signups"], 1) * 100, 2)
    return totals


# ---------------------------------------------------------------------------
# REPORT OUTPUT
# ---------------------------------------------------------------------------

def print_section(title):
    print(f"\n{'='*75}")
    print(f"  {title}")
    print(f"{'='*75}")


def main():
    conn, df = load_data()

    print("\n" + "="*75)
    print("  INFLUENCER MARKETING EFFECTIVENESS REPORT — H1 2025")
    print("="*75)

    # --- Overall Funnel ---
    print_section("FULL-FUNNEL OVERVIEW")
    funnel = funnel_analysis(df)
    print(f"  Views:           {funnel['total_views']:>12,}")
    print(f"  Link clicks:     {funnel['total_clicks']:>12,}   ({funnel['click_rate']}% CTR)")
    print(f"  Signups:         {funnel['total_signups']:>12,}   ({funnel['signup_rate']}% of clicks)")
    print(f"  Paid conversions:{funnel['total_paid']:>12,}   ({funnel['conversion_rate']}% of signups)")

    # --- Influencer Leaderboard ---
    print_section("INFLUENCER LEADERBOARD")
    inf_df = pd.read_sql(INFLUENCER_PERFORMANCE_SQL, conn)
    print(inf_df.to_string(index=False))

    # --- Platform Breakdown ---
    print_section("PLATFORM PERFORMANCE")
    plat_df = pd.read_sql(PLATFORM_SUMMARY_SQL, conn)
    print(plat_df.to_string(index=False))

    # --- Content Type ---
    print_section("CONTENT TYPE ANALYSIS")
    content_df = pd.read_sql(CONTENT_TYPE_SQL, conn)
    print(content_df.to_string(index=False))

    # --- Tier Analysis ---
    print_section("PERFORMANCE BY INFLUENCER TIER")
    tier_df = pd.read_sql(TIER_ANALYSIS_SQL, conn)
    print(tier_df.to_string(index=False))

    # --- Monthly Trend ---
    print_section("MONTHLY TREND")
    monthly_df = pd.read_sql(MONTHLY_TREND_SQL, conn)
    print(monthly_df.to_string(index=False))

    # --- Engagement Rates ---
    print_section("TOP CAMPAIGNS BY ENGAGEMENT RATE")
    eng_df = compute_engagement_rates(df)
    top_eng = eng_df.nlargest(10, "engagement_rate")[
        ["campaign_id", "influencer_name", "platform", "content_type",
         "engagement_rate", "signups", "paid_conversions"]
    ]
    print(top_eng.to_string(index=False))

    # --- Recommendations ---
    print_section("RECOMMENDATIONS FOR Q3 2025")
    recommendations = [
        "1. DOUBLE DOWN ON PODCASTS — Highest ROAS across platforms. Negotiate",
        "   multi-episode packages with StartupPodcast and TheAIPodcast.",
        "",
        "2. SCALE MICRO-INFLUENCER TWITTER THREADS — Best cost-per-conversion",
        "   despite low absolute volume. Test 5-8 new micro creators at low risk.",
        "",
        "3. RENEGOTIATE MACRO YOUTUBE RATES — TechReviewPro delivers consistent",
        "   volume but at premium pricing. Push for integration-only deals",
        "   ($10-12K) over dedicated videos ($15-18K) since ROAS is comparable.",
        "",
        "4. TEST TIKTOK → SIGNUP FUNNEL — SarahBuilds drives massive views",
        "   but conversion to paid is lower. Experiment with dedicated landing",
        "   pages and offer codes to improve attribution and conversion.",
        "",
        "5. CUT UNDERPERFORMERS — Drop any influencer with ROAS below 2.0x",
        "   after 2+ campaigns. Reallocate that budget to top performers.",
    ]
    for line in recommendations:
        print(f"  {line}")

    conn.close()
    print(f"\n{'='*75}")
    print("  Report complete.")
    print(f"{'='*75}\n")


if __name__ == "__main__":
    main()
