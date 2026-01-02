"""Gold layer data quality expectations."""

GOLD_EXPECTATIONS = {
    "daily_metrics": {
        "expect_all": {
            "positive_counts": "event_count > 0",
            "valid_amounts": "total_amount >= 0",
        },
    },
    "user_ltv": {
        "expect_all": {
            "positive_ltv": "lifetime_value >= 0",
            "valid_dates": "last_activity_date >= first_activity_date",
        },
    },
}
