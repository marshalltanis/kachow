**Project**: Kachow — Forex prediction & trading brain
- **Description**: This repository contains a small trading brain that connects to a local MT4-like socket feed, ingests tick data, and (intended to) predict next prices using a model. The project currently wires up socket I/O and model invocation; model training/prediction code lives under `models/`.

**Current State**:
- **Socket client**: `trading_brain/metatrader4.py` implements an `MT4` client that connects to a TCP server (configured by `trading_brain/demo_config.json`) and reads tick messages terminated by the bytes sequence `\n\r`.
- **Control & receiver loop**: `trading_brain/trading_logic.py` provides a command-driven CLI which can create a session, start a receive process (`recv_handler`) that reads ticks and pushes them into a multiprocessing queue, and a `model_controller` which (when a model is provided) will call `model.predict_next_open()` for each tick.
- **Model code**: `models/RNN.py` contains an RNN (LSTM) `Model` class which loads/trains a Keras model and exposes `predict_next_open()`; the trading logic currently initializes `model = None` (model initialization is present but commented out in `trading_logic.py`).

**What this README documents**:
- How the pieces are wired together
- How to run a simple socket integration test (provided in `tests/`)

**Files of interest**:
- `trading_brain/demo_config.json`: socket host/port (default `127.0.0.1:666`).
- `trading_brain/metatrader4.py`: `MT4` class used by the trading brain to connect and receive ticks.
- `trading_brain/trading_logic.py`: CLI & process orchestration; starts receiver and model controller processes.
- `models/RNN.py`: model implementation (Keras LSTM). Heavy dependencies; tests avoid instantiating it.

**How to run (development)**:
- Install test/dev dependencies (recommended):

```
pip install pytest
```

- Run the unit/integration test that starts a local fake MT4 server and verifies `MT4.receive_tick_info()`:

```
pytest -q
```

**Notes & caveats**:
- The repository contains a Keras model that may require GPU drivers and large dependencies. The tests supplied do not instantiate the model — they only validate the socket receive flow and parsing.
- `trading_brain/trading_logic.py` is interactive: running it will block on `input()` and will spawn multiprocessing processes when you use the console commands documented inside the file.
- The code currently uses Windows-style paths in some places (e.g., `TRAINING_DATA = "..\\data\\EURUSD_H1.csv"`) — be mindful when running on Linux; adjust paths if necessary.

If you'd like, I can:
- Add more tests that exercise `model_controller` with a lightweight fake model, or
- Wire the model initialization back in and add end-to-end tests that exercise prediction.
