from __future__ import annotations

import unittest
from pathlib import Path


class MobileSidebarContractTests(unittest.TestCase):
    def test_mobile_navigation_reclaims_workspace_width(self):
        source = Path("dashboard/frontend/src/components/Sidebar.tsx").read_text(encoding="utf-8")
        self.assertIn('@media (max-width: 767px)', source)
        self.assertIn('width: 58px !important', source)
        self.assertIn('data-dashboard-responsive="desktop-labels-mobile-icon-rail"', source)
        self.assertIn('data-dashboard-tab-label-text', source)
        self.assertIn('data-dashboard-group-label', source)
        self.assertIn('display: none !important', source)

    def test_mobile_navigation_preserves_accessible_tab_names(self):
        source = Path("dashboard/frontend/src/components/Sidebar.tsx").read_text(encoding="utf-8")
        self.assertIn('aria-label={label}', source)
        self.assertIn('title={label}', source)
        self.assertIn('aria-current={active ?', source)
        self.assertIn('data-dashboard-tab={id}', source)

    def test_mobile_navigation_does_not_change_tab_authority(self):
        source = Path("dashboard/frontend/src/components/Sidebar.tsx").read_text(encoding="utf-8")
        self.assertIn('export const DASHBOARD_TABS', source)
        self.assertIn('export const DASHBOARD_TAB_IDS', source)
        self.assertEqual(source.count("{ id: '"), 22)


if __name__ == "__main__":
    unittest.main()
