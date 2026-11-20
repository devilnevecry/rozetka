import time

from rozetka.core.tracker import Session


def test_session_total_kwh_single_sample():
    s = Session(start_ts=0.0)
    s.samples.append(__import__("rozetka.core.tracker", fromlist=["PowerSample"]).PowerSample(timestamp=0.0, watts=100.0))
    s.end_ts = 3600.0
    # 100W for 1 hour = 0.1 kWh
    assert abs(s.total_kwh() - 0.1) < 1e-9


def test_session_total_kwh_two_samples():
    from rozetka.core.tracker import PowerSample
    s = Session(start_ts=0.0)
    s.samples.append(PowerSample(timestamp=0.0, watts=100.0))
    s.samples.append(PowerSample(timestamp=1800.0, watts=200.0))
    s.end_ts = 3600.0
    # trapezoid: (100+200)/2 * 1800 + 200 * 1800 = 270000 + 360000 = 630000 Wh*s? Actually W*s -> /3.6e6
    expected = (150.0 * 1800 + 200.0 * 1800) / 3_600_000.0
    assert abs(s.total_kwh() - expected) < 1e-9