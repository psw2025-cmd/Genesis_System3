from datetime import date
from pathlib import Path
from scripts.cepe_chronological_evaluation import distribution,split_pairs


def test_split_excludes_future_outcome_and_unproven_weekend():
    files = [Path(x+"_fo_bhavcopy.csv") for x in ("20260330","20260331","20260401","20260402","20260406")]
    pairs,gaps = split_pairs(files,date(2026,4,1),date(2026,6,30))
    assert [(a,c) for a,b,c,d in pairs] == [(date(2026,4,1),date(2026,4,2))]
    assert len(gaps) == 1
    validation,_ = split_pairs(files,date(2026,1,1),date(2026,3,31))
    assert len(validation) == 1 and validation[0][2] == date(2026,3,31)


def test_distribution_keeps_losses_and_extreme_multiples_uncapped():
    result = distribution([0.1,1,3,10,20,30,58])
    assert result["quantiles"]["0"] == 0.1
    assert result["quantiles"]["1"] == 58
    assert result["thresholds"] == {"3":5,"10":4,"20":3,"30":2}
    assert result["full_uncapped_distribution_sha256"] == distribution([58,30,20,10,3,1,0.1])["full_uncapped_distribution_sha256"]
