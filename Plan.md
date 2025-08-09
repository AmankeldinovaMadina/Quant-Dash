# Project Plan: Real-Time Stock Dashboard with ML Predictions

## Overview and Objectives

This project aims to build a **web application** that streams live stock prices (covering U.S. and European markets) and displays them in real-time, with an integrated **machine learning model** providing stock price predictions. The application is intended for **educational purposes**, so we prioritize clear architecture and free/low-cost solutions. Key objectives include: real-time price updates, visualization of historical and live data, ML-based forecasting, and a modular, scalable design.

## Requirements and Constraints

* **Market Coverage:** Focus on stocks from **US and European exchanges** (e.g., NYSE/NASDAQ, LSE, Euronext, etc.). The system should be flexible to handle tickers from both regions.
* **Real-Time Data:** Provide **real-time or near real-time** streaming of stock prices. This implies using a streaming API or WebSocket to push updates instantly, rather than relying on slow polling.
* **Cost and Data APIs:** Prefer **free data APIs** for price feeds due to educational use, while noting low-cost upgrade options if needed. The chosen data source must support both US and EU stock markets.
* **Technology Stack:** Frontend will use **React** (a popular choice for dynamic UIs), backend will use **FastAPI** (a high-performance Python web framework), and the ML component will be implemented in Python (e.g., using libraries like scikit-learn or TensorFlow). This stack aligns with the provided repository and ensures a smooth integration of ML in the backend.
* **Real-Time Streaming:** The system should use **WebSockets** (or similar technology) for pushing live updates to the frontend. WebSockets allow persistent, full-duplex communication so both server and client can send data in real-time, making them ideal for streaming stock quotes.
* **Educational Emphasis:** The architecture should remain **simple and clear**, favoring readability and ease of understanding over complex optimizations. We will explain each design choice for learning purposes, and use widely adopted tools to maximize familiarity.

## Data Source Options for Stock Prices

Selecting a reliable data source is crucial. We need an API that provides live quotes for US and European stocks, ideally with a free tier. Below are some options:

* **Finnhub API:** A highly recommended choice for real-time stock data. Finnhub covers **global markets (60+ exchanges)** and provides both REST endpoints and a **WebSocket feed** for live prices. It offers a generous free tier (e.g. 60 API calls/min), making it suitable for streaming multiple stocks in real-time. (Requires a free API key signup.)
* **Financial Modeling Prep (FMP):** Provides free real-time stock data with global coverage and even has a WebSocket endpoint for live price updates (after API key login). The free plan allows a decent number of daily requests (about 250), which is useful for an educational app.
* **Alpha Vantage:** A well-known free API offering historical and **real-time data** for stocks (as well as forex/crypto). It’s free to use with an API key, though it has rate limits (around 5 calls per minute). Alpha Vantage is great for on-demand data (e.g., intraday time series), but since real-time streaming would require frequent calls, it might hit rate limits quickly on the free tier.
* **Twelve Data:** Another API with **real-time and historical stock data** and broad coverage (US & global). It supports WebSockets for live quotes and has a free tier (with limitations on number of symbols or requests). This is a good alternative if we need easy integration and a unified solution for streaming and historical data.
* **IEX Cloud:** Provides live and historical market data with a free tier, but note that free access is typically limited to U.S. stocks. It’s a robust solution for U.S. markets and widely used in developer projects.
* **Yahoo Finance (unofficial):** Yahoo’s API is unofficial but accessible via libraries like `yfinance`. It can retrieve historical and quasi-real-time data for many global stocks for free. However, it doesn’t provide a true streaming WebSocket; we would need to poll for updates (with some delay). For a truly **free** approach without API keys, one could parse Yahoo Finance data, but reliability can be an issue.

**Recommended Choice:** Given the requirements, **Finnhub** is an optimal choice for this project. It offers real-time streaming via WebSockets and covers both US and European stocks (and more). The free tier should suffice for a single-user educational dashboard, streaming a few tickers. We will use Finnhub’s WebSocket to get live tick data (trades/quotes) and its REST API for any additional info (e.g., historical data or company info if needed). As alternatives, we keep Alpha Vantage or FMP in mind in case we need backup data sources (for example, Alpha Vantage could provide historical prices or technical indicators via its API, which could be useful for the ML model training). All chosen APIs are either free or low-cost, aligning with the project’s budget constraints.

*(Note: If more real-time data or commercial use were needed, we’d consider paid options like Polygon.io or Morningstar. But for our scope, the free APIs above are sufficient.)*

## System Architecture Overview

The application will follow a **client–server architecture** with a clear separation of concerns between frontend, backend, and external services. Below we outline the main components and how they interact, along with the rationale for each choice:

* **Frontend (React Single Page App):** The user interface will be built in **React**. React is chosen for its popularity and strong ecosystem for building interactive dashboards. It’s an industry-standard for frontend development, with a broad range of libraries for charts and state management. The React app will provide:

  * **Live Data Visualization:** Display stock price charts that update in real-time. We will use a charting library (e.g., **Recharts**, **Chart.js**, or **Plotly**) to plot price data. These libraries integrate well with React and allow smooth updates on incoming data.
  * **User Controls:** Allow users to select a stock ticker (and possibly exchange), view current price, and toggle prediction overlays or other analytics. Since multiple markets are in scope, a dropdown for region/ticker can be provided.
  * **WebSocket Connection:** The React app will establish a WebSocket connection to the FastAPI backend to receive live price updates. React’s component lifecycle (e.g., using `useEffect` hooks) can manage opening the connection and handling incoming messages to update the state/chart. This approach ensures low-latency updates, as data is pushed immediately to the browser.
  * **Responsiveness and UX:** Given this is educational, we’ll keep the UI simple but use a component library like **Material-UI or Ant Design** for a clean look. This isn't strictly required, but it can speed up development of forms, buttons, layout, etc.

* **Backend (FastAPI Server):** The server side uses **FastAPI**, chosen for its high performance, modern features, and native support for asynchronous operations and WebSockets. FastAPI will serve multiple roles:

  * **REST API Endpoints:** Provide traditional HTTP endpoints for any needed data fetching or actions. For example, an endpoint could supply **historical price data** for a given stock (used to plot the initial chart or for ML model input). Another endpoint might list supported tickers or provide company info/news (if we extend features).
  * **WebSocket Endpoint:** FastAPI allows easy setup of WebSocket routes for real-time communication. We will implement a route (e.g., `/ws`) that clients connect to for live updates. FastAPI’s async nature means we can handle multiple concurrent connections efficiently. Once a client web app connects:

    * The backend will subscribe to the relevant stock’s feed (either by connecting to the external API’s WS or by beginning a polling loop).
    * The server will push price updates to the client over this socket. This design offloads update logic to the server, keeping the client simpler (the client just listens for updates).
    * If multiple clients connect or if one client subscribes to multiple tickers, the backend will manage these: potentially maintaining a **connection manager** that tracks clients and their subscribed tickers. Incoming data can be broadcast to all subscribers of that ticker (FastAPI can iterate over connections to send messages). This is similar to a chat server broadcasting messages, and FastAPI provides patterns for managing lists of WebSocket connections.
    * **Why WebSockets?** WebSockets provide a persistent, bidirectional channel that is ideal for streaming updates, unlike HTTP polling which would be slower and less efficient. By using WebSockets, we minimize latency and overhead for frequent updates, creating a smoother real-time experience for the user.
  * **Data Fetching & Ingestion:** The backend will handle integration with the stock data API (Finnhub or others):

    * If using Finnhub’s WebSocket: The FastAPI app itself might maintain a **background task** that runs an asynchronous WebSocket client to Finnhub. Upon connecting, it would send a subscribe message for the desired ticker(s) and then await incoming messages. Each message (trade/quote update) from Finnhub would be parsed and then forwarded to the relevant frontend clients via our WebSocket endpoint. This essentially makes our server a relay/proxy for data, possibly with some transformation or filtering if needed.
    * If using a REST API (like Alpha Vantage or Finnhub REST for some data): The backend can use an **async scheduler** (or FastAPI’s BackgroundTasks) to periodically fetch the latest price (e.g., every few seconds) and then push it to clients. However, this polling approach is less real-time and may be subject to rate limits. For true streaming, the preference is to use an external streaming API or at least a very frequent poll if limits allow.
    * We will design the data fetching in a modular way. For example, a Python module `data_feed.py` could contain logic to connect to external APIs and produce a stream of price updates. This can be started when the FastAPI app launches (perhaps in the startup event handler) so that data is flowing and ready to be sent to any client that connects.
  * **Machine Learning Integration:** FastAPI will also host the ML model for predictions (details in the ML section below). The server might expose a route like `/predict` or integrate predictions into the data stream (e.g., every time a new price comes in, compute the predicted next price and send that to the frontend as well). FastAPI’s high performance and async support mean it can handle inference calls without blocking other requests, especially if the model prediction is fast (if the model is heavier, we might execute it in a separate thread or process to keep the event loop free).
  * **Database or State Management:** For this project, a database is **optional**. We might not need a persistent DB for core features (since data can be fetched on the fly). However, we could use a lightweight database if needed for:

    * Caching historical data or recent quotes (to avoid repeated external calls and to provide data to the ML model). For example, a **Redis** cache or an in-memory store could keep the last N prices for each ticker.
    * Storing user preferences (if we had user accounts or saved watchlists) – likely unnecessary for an initial educational version.
    * Logging prices or model predictions for later analysis.
    * If we decide to persist data, something simple like **SQLite** or a time-series database could be used. But to keep the project simple, we will rely on API calls and in-memory data. (The repository’s context will also be considered to align with any existing storage mechanism.)
  * **CORS and Security:** FastAPI will be configured with CORS middleware to allow the React dev server (likely running on localhost:3000) to talk to the API (localhost:8000). For an educational app, we might not implement authentication. But if needed, FastAPI could secure certain endpoints or the WebSocket with tokens. For now, we assume an open setup since it’s a learning project.

* **Machine Learning Module:** This is the component responsible for predicting stock trends or future prices:

  * **Choice of Model:** For time-series prediction of stock prices, a common approach is using an **LSTM (Long Short-Term Memory) neural network** or other sequence models, as these handle temporal data well. We could also consider simpler models (ARIMA, Prophet, or even a regression on technical indicators) depending on complexity. Given the educational aim, an LSTM deep learning model is attractive for learning purposes (and can yield interesting results). Alternatively, a **scikit-learn** regression or classification model might be used for simplicity (e.g., to predict if the price will go up or down in the next interval).
  * **Model Training:** We will likely **train the model offline** (outside the web app) using historical stock data. For instance, we can fetch past prices for a stock (e.g., last 60 days of minute-by-minute data) via the API and train an LSTM to predict the next price. This training could be done in a Jupyter notebook or script and the trained model saved (serialized) to a file.
  * **Model Serving:** The FastAPI backend will **load the trained model** at startup (for example, loading a PyTorch or TensorFlow model, or a pickled scikit-learn model). When a new price comes in, or upon a client request, the backend will feed the recent data to the model to get a prediction. The result could be:

    * Sent to the frontend via the WebSocket (e.g., alongside each real price update, send the predicted price for the next minute). The front-end can plot the prediction as a line alongside the actual price.
    * Or provided via a REST endpoint (e.g., client asks for a prediction for the next day, the server responds with the ML model’s forecast).
  * **Integration and Choice Justification:** Using Python for the backend means the ML model integration is straightforward — the model is just part of the FastAPI app’s code. This avoids complexity of deploying a separate ML service. FastAPI’s performance ensures that even with the ML inference, the app remains responsive. We choose an **LSTM with TensorFlow/Keras** for a more sophisticated example (students can learn about RNNs), but if that proves too slow or complex, we can switch to a simpler model (e.g., a moving average or linear model for demo purposes).
  * **Example Prediction Feature:** For instance, the ML component might compute a **1-minute ahead prediction** every time a new price arrives. If the stock is currently \$100, the model might predict \$100.5 for the next minute. We could also compute a trend (up/down) or a confidence score. These predictions would be clearly marked as “Model Prediction” in the UI to differentiate from actual prices (since the model could be very naive and is for learning, not actual trading!). This feature will demonstrate how real data and ML can be combined in one application.

* **External Services:** Aside from the stock data APIs, no other external services are strictly needed. However, a few could enhance the architecture if desired:

  * **Background Task Scheduler:** If using polling, we might use something like **Celery** or APScheduler to fetch data at intervals without blocking the main server. But for simplicity, FastAPI’s native background tasks or just an `asyncio` loop can be used.
  * **Deployment Environment:** The app can be containerized with **Docker** for easy deployment. The architecture is simple enough to run on a single VM or Heroku/DigitalOcean app. We will keep deployment in mind (ensuring environment variables for API keys, etc.), but as an educational project, running locally is the primary scenario.
  * **Logging & Monitoring:** We will add logging on the backend to observe the data flow (especially because dealing with external APIs and websockets can be tricky to debug). This will help in understanding how often data arrives and how the system behaves.

## Detailed Architecture Flow

To clarify how components interact, here is the expected **data flow** in operation (from user action to data update):

1. **User opens the React app** in a browser. The app, upon load, may call a FastAPI REST endpoint to get some initialization data – for example, a list of available stock symbols or historical data to plot an initial graph.
2. **User selects a stock** (and a market if needed). This triggers the React app to:

   * Render the historical chart for that stock (using data from a REST API call like `GET /history?symbol=XYZ` which FastAPI serves by fetching from an external API or cache).
   * Establish a WebSocket connection to the backend: e.g., `ws://backend_url/ws?symbol=XYZ`. (We might include the symbol in the query or send a subscribe message after connecting.)
3. **FastAPI backend receives the WebSocket connection**. The connection handler will parse the requested symbol (from the URL or initial message). It will then **subscribe to that symbol’s live data**:

   * If using Finnhub WS: The server sends a subscription message to Finnhub’s WebSocket (already connected) for “XYZ”. Finnhub will start streaming trades/quotes for XYZ.
   * If using a polling approach: The server starts a loop (for that client or globally) to fetch the latest price every second or appropriate interval.
   * The server also registers this client in an internal list/map so it knows the client is interested in XYZ updates.
4. **Live data updates flow in:** Whenever a new price update for XYZ is received (from Finnhub or other source), the backend **processes the update**:

   * It may format the data into a simpler JSON (e.g., `{symbol: "XYZ", price: 100.42, time: "2025-08-08T11:35:00Z"}`).
   * It triggers the ML prediction module (if, say, we want a prediction at each step). The model could take recent prices and output a predicted next price, e.g., \$100.50. This result could be attached to the message (e.g., `{..., prediction: 100.50}`) or sent as a separate message/type.
   * The server then **sends the data via WebSocket** to the React client. If multiple clients are subscribed to XYZ, it broadcasts to all of them. FastAPI makes it easy to send JSON over websockets (using `websocket.send_json`).
5. **React frontend receives the update:** The React code, listening on the WebSocket, will get the message containing the new price (and prediction). It then updates the component state:

   * The current price display is updated (e.g., showing \$100.42).
   * The chart data series is extended with a new point at the current time and price. If a prediction was included, the UI can plot that as a point or a separate line. For example, we might show a small marker for the predicted next price.
   * Because React state change triggers re-render, the chart will smoothly update to include the new data point.
6. This cycle continues, sending a stream of updates. The result is a **real-time updating chart** on the frontend, and potentially some indicator of prediction. The user sees the price move tick by tick.
7. If the user switches to a different stock, the frontend will:

   * Close or reuse the WebSocket connection to request the new symbol’s data. We may implement this by sending an unsubscribe message for the old symbol and a subscribe message for the new one over the socket, or by closing and reconnecting the socket with a new query parameter. The backend will accordingly adjust its subscriptions to the external API (unsubscribe from the old ticker feed and subscribe to the new one).
   * Load historical data for the new symbol and update the chart accordingly.
8. **Error handling:** We must handle cases like API downtime or WebSocket disconnects. The backend should catch exceptions from the external API and maybe retry. The frontend should handle the socket closing by perhaps showing a "reconnecting..." message and attempting to reconnect. Since this is educational, we will include basic error logs and simple retry logic to keep the system robust enough for demonstration.

**Scalability considerations:** While our focus is a single-user educational app, the architecture can scale. FastAPI can handle many concurrent connections (it’s asynchronous), and with a proper deployment (Uvicorn workers, etc.), multiple clients can be served. If we were to scale further, we might separate the data ingestion into a microservice (for example, one service purely subscribes to market data and then pushes it via a message queue like Redis or Kafka, and the FastAPI app(s) consume from that queue to broadcast to websockets). For now, a single FastAPI application will perform all roles, but it’s good to note that the design is modular enough to split later: data feed, web API, and ML prediction could all be separate if needed.

## Development Plan and Milestones

To implement this project, we will proceed in stages, ensuring each part works correctly before integrating everything:

1. **Project Setup:** Initialize a FastAPI project and a React app (if not already in the provided repo). Ensure the development environment is configured (Python packages for FastAPI, Uvicorn, etc., and Node packages for React). We’ll allow CORS on the FastAPI app so the React dev server can communicate during development.
2. **Basic FastAPI Endpoints:** Start by creating a simple FastAPI endpoint (e.g., `/ping`) to test the setup. Then implement an endpoint to fetch historical stock data (e.g., `/api/history?symbol=XYZ`). For now, this can return dummy data or call a free API (like Alpha Vantage’s daily series or Yahoo via `yfinance`) to get some recent prices. This will also test external API integration and allow us to have data to display initially.
3. **WebSocket Implementation:** Implement a WebSocket route in FastAPI (e.g., `/ws`). Initially, just test it locally by making it send back a timestamp or echo messages to ensure it works. Then extend it to tie into real stock data:

   * Write a function to connect to the chosen streaming API (Finnhub or FMP). This could be done with Python’s `websockets` library or `aiohttp` for WebSocket client. Alternatively, use Finnhub’s Python SDK if available.
   * In FastAPI’s startup event, launch a background task that maintains the connection to the external WebSocket and awaits messages. When a message comes (say a trade for some symbol), put it into an async queue or directly broadcast to clients.
   * Manage subscriptions: perhaps maintain a dict of `{symbol: [client_connections]}`. When a client connects and requests a symbol, add them to that symbol’s list. When new data arrives for a symbol, broadcast to those clients. If no clients for a symbol, maybe unsubscribe from external feed to save bandwidth.
   * This part is tricky, so we’ll build gradually and log events (e.g., log when a message is received from external API and when we send to client).
   * **Testing:** We can open a browser (or use `wscat` CLI) to connect to our WebSocket and subscribe to a symbol, then see if data flows. Initially, we might test with a known volatile stock to see frequent updates.
4. **Frontend Real-Time Integration:** In the React app, implement a WebSocket client. For example, use the browser WebSocket API or a library like Socket.io (though for simplicity, the native WebSocket is fine since FastAPI speaks standard WS).

   * Create a React component for the live chart. On component mount, open the WebSocket connection to FastAPI. On receiving messages (JSON data), update the chart state.
   * Use a chart library to render the price data. Plot an initial static series (from the historical data endpoint) and then append new points as they arrive via WS. Ensure the chart auto-updates (most libraries can handle dynamic data sets).
   * Display current price, maybe change its color if price went up or down (for a nice touch).
   * Ensure UI remains responsive. Because updates can be frequent (multiple per second in fast markets), we might throttle rendering if needed. But likely, a point per second is fine for a basic chart.
   * Test the end-to-end: run FastAPI and React, select a symbol, and verify that the chart updates in real time with actual market data.
5. **Machine Learning Model Development:** Parallel to the above, work on the ML aspect:

   * Gather historical data for training. We can use the chosen API (Finnhub has REST for historical candles, Alpha Vantage has intraday series) to download e.g. 30 days of minute-by-minute prices for a sample stock (like AAPL). Use Python (pandas) to process this and create a training dataset.
   * Build a model (e.g., an LSTM using Keras or PyTorch). Train it on the data to predict the next time step’s price. Evaluate its performance (for learning purposes).
   * Once satisfied, save the model (e.g., as `model.h5` for Keras or a pickle for scikit-learn). Keep the model simple enough that inference is fast (<50 ms) to not bottleneck the streaming.
   * Integrate the model into FastAPI: in the app startup, load the saved model into memory. Implement a `/predict` endpoint for testing (client can hit it with a date range or last N data points and get a predicted next price).
   * Finally, update the WebSocket broadcasting logic: after receiving a new real price, call the model’s predict method on the recent sequence (e.g., last 10 minutes of prices) to forecast the next minute. Include that prediction in the data sent to frontend.
   * **Note:** If real-time model predictions prove unstable or too slow, we can simplify (e.g., predict using last price or a moving average as a dummy “ML” output) just to have something to show. The emphasis is on integrating an ML component, not on its accuracy.
6. **Frontend ML Visualization:** Update the React chart to also display the ML prediction. For instance, if the model predicts a future price, we can plot it as a different-colored point or line. Perhaps show a short dotted line ahead of current time for the forecast. Also possibly display a text like “Predicted next price: \$X”.

   * If the ML is predicting a longer term (say end-of-day price), we could show that separately. But likely a short-term prediction is easier to correlate with the live data.
   * Ensure the user understands this is a prediction. (Educationally, this can lead to discussion on model accuracy).
7. **Additional Features (if time permits):** After the core streaming and ML are working, we can add some polish or extras:

   * **Multiple Stocks or Dashboard View:** Show more than one stock’s data at once (e.g., side by side charts or a table of live quotes). This would test our ability to handle multiple subscriptions. We’d need to open multiple WS connections or multiplex one connection for multiple symbols. Finnhub’s API allows subscribing to multiple tickers on one connection. We can implement that and have the backend broadcast accordingly. The frontend could then manage an array of data streams.
   * **Technical Indicators:** For educational value, compute some technical indicators (like moving averages, RSI, etc.) either in backend or frontend using the price data and display them.
   * **News or Context:** Perhaps fetch latest news headlines for the selected stock (some APIs like Finnhub or FMP provide news feeds) and display on the dashboard. While not core to streaming, it enriches the dashboard concept.
   * **User Interaction:** Add ability for user to input, for example, a custom time range for historical data or manually trigger a prediction for X minutes ahead.
   * Keep these optional to avoid losing focus. The primary goal is streaming prices and ML prediction display.
8. **Testing and Validation:** Rigorously test the system:

   * Test with different symbols (including some from US and some from Europe like using appropriate ticker symbols and exchange codes if needed, e.g., “AAPL” vs “BMW\.DE” for a German stock on Yahoo or the API’s format).
   * Test the performance: does the app keep up with rapid updates? (We might simulate faster ticks or just observe a busy stock during market open.)
   * Ensure the system handles network interruptions gracefully (e.g., if the external API disconnects, our backend should reconnect; if the user loses internet, the frontend should retry connecting to WS).
   * Debug any memory or resource issues if the app runs for a long time (like ensure we don’t accumulate infinite data in memory — maybe limit chart to last N points).
   * Because it’s educational, we will also prepare some analysis of the system’s latency (maybe log timestamps when data received from API vs when sent to client).
9. **Documentation & Explanation:** Write clear documentation (in-code comments, a README update) explaining how each part works. This is important since the project is for learning. We will describe how to run the app, where to plug in API keys, and how the data flow works. If possible, include an architecture diagram to visualize the components (showing React in browser, FastAPI server, external data API, and the ML model).
10. **Review and Future Improvements:** Finally, reflect on the architecture. We will note any limitations (for example, **data quality**: free APIs might have slightly delayed or limited data, and **model accuracy**: a simple ML model on stock prices likely won’t be very accurate). We’ll suggest improvements such as using a paid real-time feed for truly live trading data or deploying the ML model as a separate service for scalability. We will also ensure each architectural choice is justified – for instance, if asked "why not Flask or Django instead of FastAPI," we can point out FastAPI’s async performance and built-in docs which are great for an API-centric project.

By following this plan, we will incrementally build a robust system. Each step ensures that when we integrate the next, we can identify where issues arise. The end result will be a **real-time stock dashboard** running on a React frontend, powered by a FastAPI backend that streams live prices and ML predictions. This project will demonstrate a full-stack application integrating data engineering, web development, and machine learning in a cohesive way.

## Architecture Choices Explained

To summarize and clarify, here are the key design choices and the reasoning behind each:

* **React (Frontend):** Chosen for its ability to create dynamic, stateful UI components and its widespread use in the industry. React’s rich ecosystem (chart libraries, UI components) accelerates development of a visually appealing dashboard. It is also well-suited for handling WebSocket events and updating the DOM efficiently on data changes. In 2025, React remains a top choice for frontend development due to its massive community support and proven scalability.
* **FastAPI (Backend):** We use FastAPI for building the REST and WebSocket backend due to its high performance (on par with Node.js in many cases) and modern features. FastAPI is built on Starlette and supports asynchronous I/O, which is crucial for handling multiple WebSocket connections and external API calls without blocking. It also automatically generates interactive docs (useful to test our endpoints during development). The ability to define pydantic models for data ensures our JSON payloads (stock data, predictions) are well-structured and validated. Overall, FastAPI’s design greatly simplifies combining API routes and realtime endpoints in one application.
* **WebSocket for Real-Time Updates:** Instead of polling every few seconds for new prices (which would introduce latency and unnecessary load), the backend pushes updates via WebSockets. This choice is driven by the need for **low-latency, bidirectional communication** – an essential for a smooth live-feed experience. With WebSockets, the server can instantly notify the client on price changes, and (if needed) the client could send messages to the server (for example, to change subscriptions or send user actions). This is superior to HTTP long-polling in efficiency and responsiveness for our use case.
* **Finnhub (Real-Time Data API):** After surveying various APIs, Finnhub’s free tier with global coverage and WebSocket support stood out. This influenced our architecture significantly – it means we can maintain a single persistent connection to Finnhub and get **streaming market data** without hammering a REST API. The free allowance (60 calls/min) and broad exchange coverage fit our educational scope (covering both US and EU stocks at a reasonable update frequency). Using Finnhub also simplifies getting additional info (they provide fundamentals, news, etc., which we might integrate later). The alternative (Alpha Vantage or similar) would have forced a polling mechanism due to lack of streaming, which we wanted to avoid. Thus, Finnhub is both a functional and educationally illustrative choice (students can see how real trading data streams work).
* **Machine Learning Model (LSTM time-series predictor):** We decided to include an ML model to predict stock prices to meet the project requirement of demonstrating ML integration. An LSTM neural network was chosen because it’s a popular model for time-series forecasting (stock prices being a classic example). This demonstrates a more advanced use of ML compared to, say, a linear regression. The architecture accommodates this by having the model loaded into the FastAPI app, ensuring predictions can be made on the fly as new data arrives. This choice also shows how data from an external source can be combined with a custom ML component in a cohesive system. We acknowledge that stock price prediction is a complex task and our model is likely simplistic, but the goal is to show the pipeline (data → model → prediction → UI). FastAPI’s performance means even with the model in the loop, we expect minimal overhead, especially if using optimized libraries (TensorFlow/PyTorch can utilize hardware acceleration if available, etc.).
* **No Heavy Database (Stateless Design):** For this prototype, we intentionally avoid introducing a complex database. Stock data will be transient (fetched and held in memory or on the client for charting). This keeps the system simpler and focuses the learning on streaming and ML aspects. If needed, adding a database (like PostgreSQL or TimescaleDB for time-series) is straightforward and could be an extension exercise. By keeping the backend largely stateless (except for in-memory subscription lists and maybe cached data), deployment and testing are easier. This choice also aligns with using free APIs – since we can fetch on demand or stream live, we don't strictly need to store large amounts of data locally.
* **Modularity and Extensibility:** The architecture is designed so each part could be independently modified or scaled. For example, we could swap the data source (to another API) with minimal changes isolated in the data fetching module. We could improve/replace the ML model without affecting how data is streamed. React frontend could be replaced with another framework (Angular, Vue) since it just consumes standard WebSocket/REST endpoints. This modular approach is a deliberate choice to make the project a learning tool for various components in a system. Each piece (data API, backend, frontend, ML) can be studied and improved in isolation.
* **Educational Clarity:** Finally, choices were made with clarity in mind. FastAPI and React both have good documentation and large communities, so a student can easily find resources to understand them. Using an API like Finnhub with clear documentation helps in learning how real financial data flows. Using WebSockets concretely demonstrates the difference from typical request/response workflows. Including an ML model shows how to bridge data science with web development. Each of these decisions contributes to a richer educational outcome, fulfilling the project’s aim.

In conclusion, this detailed plan lays out how to build the real-time stock dashboard, from technology selection to step-by-step implementation. We have justified each choice (React, FastAPI, WebSockets, Finnhub API, and an LSTM model) in terms of project needs and educational value. By following this architecture and plan, one should be able to develop a functional prototype that streams live stock prices for US and European markets, visualizes them on a web UI, and provides predictive insights via an integrated machine learning model. The end product will not only be a useful dashboard but also a demonstration of modern web and data engineering practices combined in a single project.

**Sources:**

* FastAPI WebSockets and performance benefits
* Finnhub free real-time API (global market coverage, 60+ exchanges)
* Alpha Vantage free stock API (global, historical & real-time data)
* Reddit discussion of free stock APIs (Twelve Data, etc., for alternatives)
* React popularity and ecosystem support in 2025
