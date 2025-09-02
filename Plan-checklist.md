I’ll answer as a **world-class real-time data architect, PhD in Streaming Systems, winner of the Fintech Dev Tools Award**.

**TL;DR**: Below is a **repo-aware, step-by-step checklist** you can follow. It references your folders (`backend/`, `frontend/`, `ml-models/`) and your current default branch (**master**) so CI actually triggers. I’ve included exact file paths, commands, and “done when” checks so you can move fast. ([GitHub][1])

---

## Phase 0 — Repo hygiene & CI (do this first)

* [ ] **Align CI triggers to your default branch**

  * In `.github/workflows/...yml`, set:

    ```yaml
    on:
      push: { branches: ["master"] }
      pull_request: { branches: ["master"] }
    ```
  * **Done when**: a new commit to `master` runs CI on GitHub Actions. ([GitHub][1])

* [ ] **Dev dependencies installation**

  * You already have `requirements-dev.txt` at repo root; either:

    * Move it to `backend/requirements-dev.txt`, **or**
    * Keep it at root and point CI to it explicitly.
  * In the backend job, replace ad-hoc installs with:

    ```yaml
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt  # or backend/requirements-dev.txt
    ```
  * **Done when**: CI installs `flake8` and `pytest` via the dev file (no separate `pip install pytest/flake8`). ([GitHub][1])

* [ ] **Frontend install determinism**

  * In the frontend job, prefer `npm ci` (uses `package-lock.json`):

    ```yaml
    - name: Install dependencies
      run: npm ci
    ```
  * **Done when**: Frontend step uses `npm ci` and passes tests. ([GitHub][1])

* [ ] **Secrets scaffold**

  * Create `backend/.env.example`:

    ```
    FINNHUB_API_KEY=changeme
    FMP_API_KEY=changeme
    ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
    ```
  * Add real keys to `backend/.env` (git-ignored).
  * In GitHub → **Settings → Secrets and variables → Actions**, add `FINNHUB_API_KEY`, `FMP_API_KEY`.
  * **Done when**: `git status` shows `.env` ignored; CI has the secrets.

---

## Phase 1 — FastAPI scaffold (backend/)

* [x] **Minimal app & CORS**

  * Files:

    ```
    backend/app/main.py
    backend/app/config.py
    backend/app/routes/health.py
    ```
  * `config.py` (pydantic-settings) reads envs; `main.py` adds CORS for `ALLOW_ORIGINS`.
  * `health.py`: `GET /healthz -> {"status":"ok"}`. ✅
  * **Done when**: `uvicorn app.main:app --reload` and `GET /healthz` returns OK.

* [ ] **Project structure**

  ```
  backend/app/
    ws/           # websockets hub
    data/         # providers (finnhub, fmp, simulator)
    ml/           # baseline/LSTM
    routes/       # health, market, predict
  ```

  * **Done when**: folders exist, imports resolve.

---

## Phase 2 — Provider interface & primary data source

* [ ] **Define a provider contract** (`backend/app/data/provider_base.py`)

  ```python
  from typing import Protocol, AsyncIterator

  class MarketProvider(Protocol):
      async def subscribe(self, symbol: str) -> None: ...
      async def unsubscribe(self, symbol: str) -> None: ...
      async def history(self, symbol: str, interval: str, limit: int): ...
      def stream(self) -> AsyncIterator[dict]: ...
  ```

  * **Done when**: type-checking passes.

* [ ] **Finnhub implementation** (`backend/app/data/finnhub.py`)

  * One process-wide **async WS client**; send `subscribe/unsubscribe` messages.
  * Normalize inbound data → `{"symbol":..., "price":..., "ts":...}`.
  * Add **auto-reconnect with backoff** and heartbeat handling.
  * **Done when**: a small async script can connect and print live ticks for `AAPL`.

* [ ] **Simulator** (`backend/app/data/simulator.py`)

  * Replays a CSV of candles at 1x/4x; yields the same normalized dicts.
  * **Done when**: you can flip a flag to run without internet/API quota.

---

## Phase 3 — WebSocket hub (browser <-> backend)

* [ ] **Message schema** (`backend/app/ws/protocol.py`)

  ```python
  # inbound
  {"type":"subscribe","symbol":"AAPL"}
  {"type":"unsubscribe","symbol":"AAPL"}

  # outbound
  {"type":"tick","symbol":"AAPL","price":100.42,"ts":1735900000000}
  {"type":"prediction","symbol":"AAPL","price":100.55,"horizon_sec":60,"ts":...}
  ```

* [ ] **Connection manager** (`backend/app/ws/hub.py`)

  * Keep `subscriptions: dict[str, set[WebSocket]]`.
  * On first subscriber → provider.subscribe; on last disconnect → provider.unsubscribe.
  * **Throttle** broadcasts to ≤10 msgs/sec per symbol.

* [ ] **Route** (`main.py`)

  ```python
  @app.websocket("/ws")
  async def ws_endpoint(ws: WebSocket):
      await hub.handle(ws, predictor)
  ```

  * **Done when**: with `wscat`/browser you can subscribe and receive tick JSON.

---

## Phase 4 — REST endpoints (history & symbols)

* [ ] **/api/history** (`backend/app/routes/market.py`)

  * `GET /api/history?symbol=BMW.DE&interval=1m&limit=1000`
  * Return compact OHLCV for the chart.

* [ ] **/api/symbols**

  * Start with a curated list: `["AAPL","MSFT","TSLA","BMW.DE","AIR.PA","VOD.L"]`.
  * **Done when**: `curl` returns arrays for both endpoints.

---

## Phase 5 — Frontend wiring (frontend/)

* [ ] **Env & base URL**

  * `VITE_API_URL=http://localhost:8000` (or your port).
  * Convert `http` → `ws` for the WS URL on the client.

* [ ] **Data hooks**

  * `useHistory(symbol)` → fetch `/api/history`.
  * `useLive(symbol)` → open `WebSocket(${API_URL.replace('http','ws')}/ws)`, send subscribe, maintain a **ring buffer** (last 1–2k points).

* [ ] **Chart & UI**

  * Render history + append live ticks (Recharts/Plotly).
  * Show current price badge; red/green flash on change.
  * Symbol picker calling `/api/symbols`.
  * **Done when**: switching symbols re-subscribes and chart updates continuously.

---

## Phase 6 — ML baseline (fast win)

* [ ] **EWMA predictor** (`backend/app/ml/baseline.py`)

  ```python
  class BaselinePredictor:
      def __init__(self, alpha=0.3): self.alpha, self._ewma = alpha, {}
      def update_and_predict(self, symbol, price):
          prev = self._ewma.get(symbol, price)
          ewma = self.alpha*price + (1-self.alpha)*prev
          self._ewma[symbol] = ewma
          return ewma
  ```

* [ ] **Push predictions in-stream**

  * In hub: after each tick, compute `pred = predictor.update_and_predict(...)` and broadcast a `{type:"prediction"}` message.
  * Frontend overlays a dotted “prediction” point/short line.
  * **Done when**: predictions render live with minimal lag.

---

## Phase 7 — Optional LSTM model (`ml-models/`)

* [ ] **Data collection script**

  * Download intraday history (respect rate limits); save to `ml-models/data/...`.

* [ ] **Training**

  * Keras/PyTorch LSTM → predict next minute close; save `model.h5`/`.pt`.

* [ ] **Serving**

  * Load at FastAPI startup; run inference in a **ThreadPoolExecutor** (don’t block event loop).
  * Fallback to EWMA on errors or high latency.
  * **Done when**: a config flag switches baseline↔LSTM.

---

## Phase 8 — Reliability & observability

* [ ] **Structured logging**

  * Log provider connects/disconnects, subscription counts, reconnects, inference latency.

* [ ] **Auto-reconnect & backoff**

  * Exponential backoff for provider WS; jitter; cap attempts; surface status on `/readyz`.

* [ ] **Rate-limit hygiene**

  * Debounce symbol changes (250–500 ms); avoid churn in subscribe/unsubscribe upstream.

* **Done when**: killing the provider connection shows clean auto-recovery and logs are readable.

---

## Phase 9 — Tests & CI

* [ ] **Backend unit tests**

  * JSON → tick parsing; EWMA correctness; protocol validation.

* [ ] **Integration test**

  * Simulator → hub → test client receives ticks + predictions.

* [ ] **Frontend tests**

  * Minimal render test for the chart; data hook buffer logic.

* [ ] **CI green**

  * Backend: `pytest`; Frontend: `npm test`; both pass on **master**. ([GitHub][1])

---

## Phase 10 — Packaging (optional, nice to have)

* [ ] **Docker**

  * `backend/Dockerfile` (uvicorn), `frontend/Dockerfile` (build → static).
  * `docker-compose.yml` to run both; route `/api` and `/ws` to backend.

* **Done when**: `docker compose up` starts a working stack with one command.

---

## Phase 11 — Docs & demo polish

* [ ] **README update (root)**

  * How to run, where to put API keys, feature list, limitations (“education only, data may be delayed”), and an architecture diagram.

* [ ] **Screenshots/GIF**

  * One GIF of a live chart with prediction overlay.

* **Done when**: a newcomer can run everything in <10 minutes from README.

---

### Extra repo-specific notes

* Your repo already has `backend/`, `frontend/`, `ml-models/`, and `requirements-dev.txt` — keep steps consistent with that layout to avoid path confusion. ([GitHub][1])
* Because the default branch is **master**, keep CI triggers on `master` (or change the repo’s default branch to `main` and update triggers accordingly). ([GitHub][1])

If you want, I can generate **starter files** (FastAPI hub, simulator, React hooks & minimal chart) matching these paths so you can commit them directly and see live updates immediately.

[1]: https://github.com/AmankeldinovaMadina/Quant-Dash "GitHub - AmankeldinovaMadina/Quant-Dash: Real-Time Financial Dashboard with MLOps-Powered Price Prediction"
