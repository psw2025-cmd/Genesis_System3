# GENESIS SYSTEM 3 – Angel One Index Options Engine (Status + Roadmap)



## 1. Scope of this document



This document describes the **Angel One Index Options** sub-system inside **Genesis System3**:



- What components exist

- What is already working

- What is partially implemented / needs improvement

- What is still pending

- How everything connects end-to-end (data → features → models → signals)



This is only about **index options via Angel One**:



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

      ... (Angel One API client etc.)

    data/

      ... (candle / storage utilities)

    engine/

      angel_index_watch.py            (live snapshot + logging logic – name indicative)

      analyze_angel_index_log.py      (simple features + signals – name indicative)

      build_angel_training_from_log.py (builds training CSV from live log – option 9)

      generate_synthetic_angel_training.py

      train_angel_models.py

      offline_angel_ai_test.py

    models/

      angel_one/

        NIFTY_model.pkl / _meta.json

        BANKNIFTY_model.pkl / _meta.json

        FINNIFTY_model.pkl / _meta.json

        MIDCPNIFTY_model.pkl / _meta.json

        SENSEX_model.pkl / _meta.json

    utils/

      ... (logging, config, time helpers etc.)



  storage/

    instruments/

      angel_instruments.csv

    live/

      angel_index_options_watch.csv        (live snapshot log – option 7)

    features/

      angel_index_options_features.csv     (feature-level history – option 8)

    training/

      angel_index_options_training.csv     (final training dataset – option 9 / synthetic)

    history/

      ... (index & candle history for other modules)

```


