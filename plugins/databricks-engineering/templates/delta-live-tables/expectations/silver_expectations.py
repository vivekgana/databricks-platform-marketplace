"""Silver layer data quality expectations."""

SILVER_EXPECTATIONS = {
    "events": {
        "expect_all": {
            "valid_event_type": "event_type IN ('click', 'view', 'purchase', 'search')",
            "valid_amount": "amount IS NULL OR amount >= 0",
            "valid_user_id": "user_id IS NOT NULL",
        },
        "expect_or_drop": {
            "valid_event_id": "event_id IS NOT NULL",
        },
    },
    "users": {
        "expect_all": {
            "valid_email": "email IS NOT NULL AND email LIKE '%@%.%'",
            "valid_signup_date": "signup_date IS NOT NULL",
        },
    },
}
