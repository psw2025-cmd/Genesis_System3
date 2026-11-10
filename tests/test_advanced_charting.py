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
