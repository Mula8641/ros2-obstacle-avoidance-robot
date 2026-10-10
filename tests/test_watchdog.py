from obstacle_avoidance.core.watchdog import scan_is_stale


def test_no_scan_yet_is_stale():
    assert scan_is_stale(None, 1.0)


def test_recent_scan_is_fresh():
    assert not scan_is_stale(0.4, 1.0)


def test_exactly_at_timeout_is_still_fresh():
    assert not scan_is_stale(1.0, 1.0)


def test_old_scan_is_stale():
    assert scan_is_stale(1.01, 1.0)
