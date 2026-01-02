"""Bronze layer data quality expectations."""

BRONZE_EXPECTATIONS = {
    "events": {
        "expect_all_or_drop": {
            "valid_event_id": "event_id IS NOT NULL",
            "valid_timestamp": "event_timestamp IS NOT NULL",
        },
        "expect_all": {
            "reasonable_timestamp": "event_timestamp >= '2020-01-01'",
        },
    },
    "users": {
        "expect_all_or_drop": {
            "valid_user_id": "user_id IS NOT NULL",
        },
    },
}
