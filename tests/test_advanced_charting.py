from dashboard.backend.advanced_charting import AdvancedCharting


def test_greeks_chart_preserves_missing_values_as_unavailable():
    chart = AdvancedCharting().generate_greeks_chart(
        {
            "spot": 100,
            "contracts": [
                {"strike": 100, "option_type": "CE", "delta": 0.62},
                {"strike": 100, "option_type": "PE"},
            ],
        },
        "delta",
    )

    assert chart["strikes"] == [100]
    assert chart["ce_data"] == [0.62]
    assert chart["pe_data"] == [None]


def test_iv_surface_keeps_the_backend_series_shape():
    chart = AdvancedCharting().generate_iv_surface(
        {
            "spot": 100,
            "contracts": [
                {"strike": 100, "expiry": "2026-12-31", "option_type": "CE", "iv": 18.5},
                {"strike": 100, "expiry": "2026-12-31", "option_type": "PE", "iv": 19.5},
            ],
        }
    )

    assert chart["strikes"] == [100]
    assert chart["surface"] == [{"expiry": "2026-12-31", "iv_values": [19.0]}]


def test_heatmap_preserves_missing_metrics_and_unmatched_cells():
    chart = AdvancedCharting().generate_option_chain_heatmap(
        {
            "contracts": [
                {"strike": 100, "expiry": "2026-12-31", "oi": 10},
                {"strike": 110, "expiry": "2026-12-31"},
                {"strike": 100, "expiry": "2027-01-31", "oi": 0},
            ]
        }
    )

    assert chart["heatmap"] == [
        {"expiry": "2026-12-31", "values": [10.0, None]},
        {"expiry": "2027-01-31", "values": [0.0, None]},
    ]


def test_pcr_chart_preserves_missing_or_undefined_ratios():
    chart = AdvancedCharting().generate_pcr_chart(
        {
            "contracts": [
                {"strike": 100, "option_type": "CE", "oi": 0},
                {"strike": 100, "option_type": "PE", "oi": 10},
                {"strike": 110, "option_type": "CE", "oi": 5},
                {"strike": 110, "option_type": "PE", "oi": 10},
                {"strike": 120, "option_type": "PE", "oi": 3},
                {"strike": 130, "option_type": "CE"},
                {"strike": 130, "option_type": "PE", "oi": 5},
                {"strike": 140, "option_type": "CE", "oi": 5},
                {"strike": 140, "option_type": "PE", "oi": 0},
            ]
        }
    )

    assert chart["strikes"] == [100, 110, 120, 130, 140]
    assert chart["pcr_data"] == [None, 2.0, None, None, 0.0]
    assert chart["overall_pcr"] is None
