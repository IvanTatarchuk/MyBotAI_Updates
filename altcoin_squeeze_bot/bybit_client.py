"""Minimal Bybit v5 REST client (stdlib only). Docs: https://bybit-exchange.github.io/docs/v5/intro"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.parse
import urllib.request

MAINNET = "https://api.bybit.com"
TESTNET = "https://api-testnet.bybit.com"
RECV_WINDOW = "5000"

# retCodes that just mean "nothing to change"
_BENIGN = {110043}  # leverage not modified


class BybitError(RuntimeError):
    def __init__(self, code: int, msg: str, path: str):
        super().__init__(f"Bybit {path} failed: {code} {msg}")
        self.code = code


def sign(secret: str, timestamp: str, api_key: str, recv_window: str, payload: str) -> str:
    raw = timestamp + api_key + recv_window + payload
    return hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()


class BybitClient:
    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = False, timeout: float = 10.0):
        self.base = TESTNET if testnet else MAINNET
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout

    # ---- transport -------------------------------------------------------------------------
    def _request(self, method: str, path: str, params: dict | None = None, private: bool = False) -> dict:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        headers = {"Content-Type": "application/json"}
        url = self.base + path
        body = None
        if method == "GET":
            payload = urllib.parse.urlencode(params)
            if payload:
                url += "?" + payload
        else:
            payload = json.dumps(params, separators=(",", ":"))
            body = payload.encode()
        if private:
            if not self.api_key or not self.api_secret:
                raise RuntimeError("API key/secret required for private endpoints")
            ts = str(int(time.time() * 1000))
            headers.update(
                {
                    "X-BAPI-API-KEY": self.api_key,
                    "X-BAPI-TIMESTAMP": ts,
                    "X-BAPI-RECV-WINDOW": RECV_WINDOW,
                    "X-BAPI-SIGN": sign(self.api_secret, ts, self.api_key, RECV_WINDOW, payload),
                }
            )

        last_exc: Exception | None = None
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, data=body, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode())
                break
            except (urllib.error.URLError, TimeoutError) as exc:
                last_exc = exc
                time.sleep(2**attempt)
        else:
            raise RuntimeError(f"Bybit {path} unreachable: {last_exc}")

        code = data.get("retCode", -1)
        if code != 0 and code not in _BENIGN:
            raise BybitError(code, data.get("retMsg", ""), path)
        return data.get("result", {})

    # ---- public market data ----------------------------------------------------------------
    def tickers(self) -> list[dict]:
        return self._request("GET", "/v5/market/tickers", {"category": "linear"})["list"]

    def instruments(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        cursor = None
        while True:
            res = self._request(
                "GET", "/v5/market/instruments-info", {"category": "linear", "limit": 1000, "cursor": cursor}
            )
            for it in res["list"]:
                out[it["symbol"]] = it
            cursor = res.get("nextPageCursor")
            if not cursor:
                return out

    def klines(self, symbol: str, interval: int, start: int | None = None, end: int | None = None, limit: int = 1000):
        """Returns [[start, open, high, low, close, volume, turnover], ...] oldest first."""
        res = self._request(
            "GET",
            "/v5/market/kline",
            {"category": "linear", "symbol": symbol, "interval": str(interval), "start": start, "end": end,
             "limit": limit},
        )
        return list(reversed(res["list"]))

    def open_interest(self, symbol: str, interval_min: int, start: int | None = None, end: int | None = None):
        """Returns [(timestamp_ms, oi), ...] oldest first, following pagination."""
        interval = {5: "5min", 15: "15min", 30: "30min", 60: "1h", 240: "4h", 1440: "1d"}[interval_min]
        rows: list[tuple[int, float]] = []
        cursor = None
        while True:
            res = self._request(
                "GET",
                "/v5/market/open-interest",
                {"category": "linear", "symbol": symbol, "intervalTime": interval, "startTime": start,
                 "endTime": end, "limit": 200, "cursor": cursor},
            )
            rows += [(int(r["timestamp"]), float(r["openInterest"])) for r in res["list"]]
            cursor = res.get("nextPageCursor")
            if not cursor or not res["list"] or start is None:
                break
        return sorted(set(rows))

    def funding_history(self, symbol: str, start: int, end: int) -> list[tuple[int, float]]:
        """Returns [(timestamp_ms, rate), ...] oldest first."""
        rows: list[tuple[int, float]] = []
        cur_end = end
        while True:
            res = self._request(
                "GET",
                "/v5/market/funding/history",
                {"category": "linear", "symbol": symbol, "startTime": start, "endTime": cur_end, "limit": 200},
            )
            batch = [(int(r["fundingRateTimestamp"]), float(r["fundingRate"])) for r in res["list"]]
            rows += batch
            if len(batch) < 200:
                break
            cur_end = min(t for t, _ in batch) - 1
        return sorted(set(rows))

    # ---- private trading -------------------------------------------------------------------
    def equity(self) -> float:
        res = self._request("GET", "/v5/account/wallet-balance", {"accountType": "UNIFIED"}, private=True)
        return float(res["list"][0]["totalEquity"])

    def positions(self) -> dict[str, dict]:
        res = self._request("GET", "/v5/position/list", {"category": "linear", "settleCoin": "USDT"}, private=True)
        return {p["symbol"]: p for p in res["list"] if float(p.get("size") or 0) > 0}

    def set_leverage(self, symbol: str, leverage: float) -> None:
        lev = str(leverage)
        self._request(
            "POST", "/v5/position/set-leverage",
            {"category": "linear", "symbol": symbol, "buyLeverage": lev, "sellLeverage": lev}, private=True,
        )

    def market_order(self, symbol: str, side: str, qty: str, stop_loss: str | None = None,
                     reduce_only: bool = False) -> dict:
        params = {"category": "linear", "symbol": symbol, "side": side, "orderType": "Market", "qty": qty,
                  "positionIdx": 0, "reduceOnly": reduce_only}
        if stop_loss:
            params.update({"stopLoss": stop_loss, "slTriggerBy": "MarkPrice", "tpslMode": "Full"})
        return self._request("POST", "/v5/order/create", params, private=True)

    def limit_reduce_only(self, symbol: str, side: str, qty: str, price: str) -> dict:
        return self._request(
            "POST", "/v5/order/create",
            {"category": "linear", "symbol": symbol, "side": side, "orderType": "Limit", "qty": qty,
             "price": price, "timeInForce": "GTC", "reduceOnly": True, "positionIdx": 0},
            private=True,
        )

    def set_stop(self, symbol: str, stop_loss: str) -> None:
        self._request(
            "POST", "/v5/position/trading-stop",
            {"category": "linear", "symbol": symbol, "stopLoss": stop_loss, "slTriggerBy": "MarkPrice",
             "tpslMode": "Full", "positionIdx": 0},
            private=True,
        )

    def cancel_all(self, symbol: str) -> None:
        self._request("POST", "/v5/order/cancel-all", {"category": "linear", "symbol": symbol}, private=True)
