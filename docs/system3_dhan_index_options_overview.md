# GENESIS SYSTEM 3 – Dhan Index Options Engine (Status + Roadmap)



## 1. Scope of this document



This document describes the **Dhan Index Options** sub-system inside **Genesis System3**:



- What components exist

- What is already working

- What is partially implemented / needs improvement

- What is still pending

- How everything connects end-to-end (data → features → models → signals)



This is only about **index options via Dhan**:



- NIFTY (NFO)

- BANKNIFTY (NFO)

- FINNIFTY (NFO)

- MIDCPNIFTY (NFO)

- SENSEX (BFO)



---



## 2. High-level architecture



Root project folder (current):



```text

C:\Genesis_System3\

  run_system3.py

  wait_and_run_live_watch.py

  venv/



  core/

    __init__.py

    brokers/

      ... (Dhan API client etc.)

    data/

      ... (candle / storage utilities)

    engine/

      dhan_index_watch.py            (live snapshot + logging logic – name indicative)

      analyze_dhan_index_log.py      (simple features + signals – name indicative)

      build_dhan_training_from_log.py (builds training CSV from live log – option 9)

      generate_synthetic_dhan_training.py

      train_dhan_models.py

      offline_dhan_ai_test.py

    models/

      dhan/

        NIFTY_model.pkl / _meta.json

        BANKNIFTY_model.pkl / _meta.json

        FINNIFTY_model.pkl / _meta.json

        MIDCPNIFTY_model.pkl / _meta.json

        SENSEX_model.pkl / _meta.json

    utils/

      ... (logging, config, time helpers etc.)



  storage/

    instruments/

      dhan_instruments.csv

    live/

      dhan_index_options_watch.csv        (live snapshot log – option 7)

    features/

      dhan_index_options_features.csv     (feature-level history – option 8)

    training/

      dhan_index_options_training.csv     (final training dataset – option 9 / synthetic)

    history/

      ... (index & candle history for other modules)

```


