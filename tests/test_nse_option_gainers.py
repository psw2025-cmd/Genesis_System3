import json
from datetime import datetime, timezone
import unittest
from scripts.nse_option_gainers import rank


class QuoteTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 24, 10, tzinfo=timezone.utc)
        self.q = dict(underlying='NIFTY', expiryDate='29-09-2026', strikePrice=23000,
                      lastPrice=40, change=30, totalTradedVolume=200,
                      buyPrice1=39, sellPrice1=41, pChange=300)

    def raw(self, q=None, timestamp='24-Sep-2026 15:30:00'):
        return json.dumps(dict(records=dict(timestamp=timestamp,
                          data=[dict(CE=self.q if q is None else q)]))).encode()

    def test_arithmetic_and_scope(self):
        r = rank(self.raw(), 'NIFTY', '29-Sep-2026', self.now)
        self.assertEqual(r['gainers'][0]['gain_pct'], 300)
        self.assertEqual(r['gainers'][0]['previous_close_derived'], 10)
        self.assertEqual(r['coverage'], 'REQUESTED_SYMBOL_EXPIRY_ONLY')
        self.assertIsNone(r['expected_next_open'])
        self.assertFalse(r['orders_allowed'])

    def test_stale(self):
        with self.assertRaises(ValueError):
            rank(self.raw(timestamp='23-Sep-2026 15:30:00'), 'NIFTY', '29-Sep-2026', self.now)

    def test_invalid_quotes(self):
        for change in [dict(lastPrice=float('nan')), dict(pChange=10),
                       dict(underlying='OTHER'), dict(sellPrice1=20),
                       dict(totalTradedVolume=0)]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                rank(self.raw({**self.q, **change}), 'NIFTY', '29-Sep-2026', self.now)

    def test_negative_return_not_a_gainer(self):
        r = rank(self.raw({**self.q, 'change': -10, 'pChange': -20}),
                 'NIFTY', '29-Sep-2026', self.now)
        self.assertEqual(r['gainers'], [])
        self.assertEqual(r['non_gainer_count'], 1)


if __name__ == '__main__':
    unittest.main()
