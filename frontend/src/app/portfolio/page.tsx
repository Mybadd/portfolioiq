"use client";

import { useEffect, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Plus,
  Trash2,
  Wallet,
  PieChart,
  Landmark,
} from "lucide-react";

type InputMode = "shares" | "amounts" | "weights";

interface Holding {
  id: number;
  symbol: string;
  shares: string;
  buyPrice: string;
  amount: string;
  weight: string;
}

interface StoredPortfolio {
  inputMode: InputMode;
  holdings: Holding[];
  calculatedWeights?: Record<string, number>;
  assetCount?: number;
  totalWeight?: number;
}

const emptyHolding = (id: number): Holding => ({
  id,
  symbol: "",
  shares: "",
  buyPrice: "",
  amount: "",
  weight: "",
});

export default function PortfolioPage() {
  const [mode, setMode] = useState<InputMode>("shares");

  const [holdings, setHoldings] = useState<Holding[]>([
    emptyHolding(1),
  ]);

  const [error, setError] = useState("");

  /*
   * Restore previously entered portfolio data.
   *
   * This allows the user to move between Portfolio and Dashboard
   * without losing the holdings that were already entered.
   */
  useEffect(() => {
    const storedPortfolio = sessionStorage.getItem(
      "portfolioiq-portfolio"
    );

    if (!storedPortfolio) {
      return;
    }

    try {
      const portfolio: StoredPortfolio = JSON.parse(
        storedPortfolio
      );

      if (portfolio.inputMode) {
        setMode(portfolio.inputMode);
      }

      if (
        Array.isArray(portfolio.holdings) &&
        portfolio.holdings.length > 0
      ) {
        setHoldings(portfolio.holdings);
      }
    } catch {
      console.error(
        "Unable to restore saved portfolio."
      );
    }
  }, []);

  const updateHolding = (
    id: number,
    field: keyof Holding,
    value: string
  ) => {
    setHoldings((current) =>
      current.map((holding) =>
        holding.id === id
          ? { ...holding, [field]: value }
          : holding
      )
    );
  };

  const addHolding = () => {
    const nextId =
      holdings.length > 0
        ? Math.max(...holdings.map((h) => h.id)) + 1
        : 1;

    setHoldings((current) => [
      ...current,
      emptyHolding(nextId),
    ]);
  };

  const removeHolding = (id: number) => {
    if (holdings.length === 1) {
      return;
    }

    setHoldings((current) =>
      current.filter((holding) => holding.id !== id)
    );
  };

  const changeMode = (newMode: InputMode) => {
    setMode(newMode);
    setError("");
    setHoldings([emptyHolding(1)]);
  };

  const validatePortfolio = () => {
    setError("");

    if (holdings.length === 0) {
      setError("Add at least one holding.");
      return false;
    }

    for (const holding of holdings) {
      if (!holding.symbol.trim()) {
        setError(
          "Every holding must have a stock symbol."
        );
        return false;
      }

      if (mode === "shares") {
        if (
          Number(holding.shares) <= 0 ||
          Number(holding.buyPrice) <= 0
        ) {
          setError(
            `Enter valid shares and average buy price for ${holding.symbol.toUpperCase()}.`
          );
          return false;
        }
      }

      if (mode === "amounts") {
        if (Number(holding.amount) <= 0) {
          setError(
            `Enter a valid investment amount for ${holding.symbol.toUpperCase()}.`
          );
          return false;
        }
      }

      if (mode === "weights") {
        if (
          Number(holding.weight) <= 0 ||
          Number(holding.weight) > 100
        ) {
          setError(
            `Enter a valid portfolio weight for ${holding.symbol.toUpperCase()}.`
          );
          return false;
        }
      }
    }

    if (mode === "weights") {
      const totalWeight = holdings.reduce(
        (sum, holding) =>
          sum + Number(holding.weight),
        0
      );

      if (Math.abs(totalWeight - 100) > 0.01) {
        setError(
          `Portfolio weights must equal 100%. Current total: ${totalWeight.toFixed(
            2
          )}%.`
        );
        return false;
      }
    }

    return true;
  };

  const handleContinue = async () => {
    if (!validatePortfolio()) {
      return;
    }

    setError("");

    try {
      /*
       * DMAT Holdings
       *
       * Send the number of shares to the Python backend.
       * The backend retrieves current market prices and
       * calculates the portfolio weights.
       */
      if (mode === "shares") {
        const holdingsPayload = holdings.reduce(
          (result, holding) => {
            result[
              holding.symbol.trim().toUpperCase()
            ] = Number(holding.shares);

            return result;
          },
          {} as Record<string, number>
        );

        const response = await fetch(
          "http://127.0.0.1:8000/api/portfolio/from-shares",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              holdings: holdingsPayload,
            }),
          }
        );

        if (!response.ok) {
          let errorMessage =
            "Failed to create portfolio.";

          try {
            const errorData = await response.json();

            if (errorData.detail) {
              errorMessage = errorData.detail;
            }
          } catch {
            // Keep default error message.
          }

          throw new Error(errorMessage);
        }

        const portfolioResult = await response.json();

        const portfolio: StoredPortfolio = {
          inputMode: mode,
          holdings,
          calculatedWeights:
            portfolioResult.weights,
          assetCount:
            portfolioResult.asset_count,
          totalWeight:
            portfolioResult.total_weight,
        };

        sessionStorage.setItem(
          "portfolioiq-portfolio",
          JSON.stringify(portfolio)
        );

        window.location.href = "/dashboard";

        return;
      }

      /*
       * Investment Amounts and Portfolio Weights
       *
       * These will be connected to dedicated backend
       * endpoints later.
       */
      const portfolio: StoredPortfolio = {
        inputMode: mode,
        holdings,
      };

      sessionStorage.setItem(
        "portfolioiq-portfolio",
        JSON.stringify(portfolio)
      );

      window.location.href = "/dashboard";
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to connect to PortfolioIQ backend."
      );
    }
  };

  return (
    <main className="min-h-screen bg-[#080b10] text-zinc-100">
      {/* Header */}
      <header className="border-b border-white/10">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 lg:px-10">
          <div>
            <div className="text-lg font-semibold tracking-[0.18em]">
              PORTFOLIO
              <span className="text-emerald-400">
                IQ
              </span>
            </div>

            <div className="mt-0.5 text-[9px] uppercase tracking-[0.28em] text-zinc-500">
              Quantitative Portfolio Intelligence
            </div>
          </div>

          <div className="flex items-center gap-3 text-[10px] uppercase tracking-[0.18em] text-zinc-500">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            System Ready
          </div>
        </div>
      </header>

      {/* Progress */}
      <div className="border-b border-white/10 bg-[#0b0f15]">
        <div className="mx-auto flex max-w-7xl items-center overflow-x-auto px-6 lg:px-10">
          {[
            ["01", "Profile", "/"],
            ["02", "Portfolio", "/portfolio"],
            ["03", "Dashboard", "/dashboard"],
            ["04", "Risk", "/risk"],
            ["05", "Optimize", "/optimize"],
            ["06", "Stress Test", "/stress-test"],
            ["07", "Report", "/report"],
          ].map(([number, label, route]) => {
            const active = number === "02";

            return (
              <button
                type="button"
                key={number}
                onClick={() => {
                  window.location.href = route;
                }}
                className={`flex shrink-0 items-center gap-2 border-r border-white/10 px-4 py-3 first:pl-0 ${
                  active
                    ? "text-zinc-100"
                    : "text-zinc-600 hover:text-zinc-300"
                }`}
              >
                <span
                  className={`font-mono text-[10px] ${
                    active
                      ? "text-emerald-400"
                      : "text-zinc-600"
                  }`}
                >
                  {number}
                </span>

                <span className="text-[10px] uppercase tracking-[0.14em]">
                  {label}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main */}
      <section className="mx-auto max-w-7xl px-6 py-10 lg:px-10 lg:py-14">
        {/* Page heading */}
        <div className="mb-10">
          <div className="mb-4 flex items-center gap-2 text-[10px] uppercase tracking-[0.25em] text-emerald-400">
            <Wallet size={14} />
            Portfolio Input
          </div>

          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
            Tell us what you own.
          </h1>

          <p className="mt-4 max-w-2xl text-sm leading-7 text-zinc-500">
            Provide your current holdings or desired allocation.
            PortfolioIQ will use this information to construct
            your portfolio and perform quantitative risk analysis.
          </p>
        </div>

        {/* Input mode selector */}
        <div className="mb-8 grid grid-cols-1 gap-px border border-white/10 bg-white/10 md:grid-cols-3">
          {/* DMAT */}
          <button
            type="button"
            onClick={() => changeMode("shares")}
            className={`group p-6 text-left transition ${
              mode === "shares"
                ? "bg-[#111820]"
                : "bg-[#0b0f15] hover:bg-[#10151c]"
            }`}
          >
            <div className="mb-5 flex items-center justify-between">
              <Landmark
                size={20}
                className={
                  mode === "shares"
                    ? "text-emerald-400"
                    : "text-zinc-600"
                }
              />

              {mode === "shares" && (
                <span className="text-[9px] uppercase tracking-[0.2em] text-emerald-400">
                  Recommended
                </span>
              )}
            </div>

            <div className="text-xs font-semibold uppercase tracking-[0.15em]">
              DMAT Holdings
            </div>

            <p className="mt-2 text-xs leading-5 text-zinc-600">
              Enter the stocks you currently own, number of
              shares, and average buy price.
            </p>
          </button>

          {/* Amounts */}
          <button
            type="button"
            onClick={() => changeMode("amounts")}
            className={`p-6 text-left transition ${
              mode === "amounts"
                ? "bg-[#111820]"
                : "bg-[#0b0f15] hover:bg-[#10151c]"
            }`}
          >
            <div className="mb-5">
              <Wallet
                size={20}
                className={
                  mode === "amounts"
                    ? "text-emerald-400"
                    : "text-zinc-600"
                }
              />
            </div>

            <div className="text-xs font-semibold uppercase tracking-[0.15em]">
              Investment Amounts
            </div>

            <p className="mt-2 text-xs leading-5 text-zinc-600">
              Enter how much money has been allocated to each
              asset.
            </p>
          </button>

          {/* Weights */}
          <button
            type="button"
            onClick={() => changeMode("weights")}
            className={`p-6 text-left transition ${
              mode === "weights"
                ? "bg-[#111820]"
                : "bg-[#0b0f15] hover:bg-[#10151c]"
            }`}
          >
            <div className="mb-5">
              <PieChart
                size={20}
                className={
                  mode === "weights"
                    ? "text-emerald-400"
                    : "text-zinc-600"
                }
              />
            </div>

            <div className="text-xs font-semibold uppercase tracking-[0.15em]">
              Portfolio Weights
            </div>

            <p className="mt-2 text-xs leading-5 text-zinc-600">
              Enter the percentage allocation you want for
              each asset.
            </p>
          </button>
        </div>

        {/* Holdings table */}
        <div className="border border-white/10 bg-[#0c1118]">
          <div className="flex items-center justify-between border-b border-white/10 px-6 py-5">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.2em]">
                {mode === "shares"
                  ? "DMAT Holdings"
                  : mode === "amounts"
                  ? "Investment Allocation"
                  : "Portfolio Allocation"}
              </div>

              <div className="mt-1 text-[10px] text-zinc-600">
                {mode === "shares"
                  ? "Enter shares and average purchase price."
                  : mode === "amounts"
                  ? "Enter the amount invested in each asset."
                  : "Total portfolio allocation must equal 100%."}
              </div>
            </div>

            <div className="font-mono text-[10px] text-zinc-600">
              {holdings.length}{" "}
              {holdings.length === 1
                ? "ASSET"
                : "ASSETS"}
            </div>
          </div>

          {/* Table header */}
          <div
            className={`hidden border-b border-white/10 bg-[#080b10] px-6 py-3 text-[9px] uppercase tracking-[0.18em] text-zinc-600 md:grid ${
              mode === "shares"
                ? "grid-cols-[1.2fr_1fr_1fr_40px]"
                : "grid-cols-[1.5fr_1fr_40px]"
            }`}
          >
            <div>Stock Symbol</div>

            {mode === "shares" && (
              <>
                <div>Shares</div>
                <div>Average Buy Price</div>
              </>
            )}

            {mode === "amounts" && (
              <div>Amount Invested</div>
            )}

            {mode === "weights" && (
              <div>Allocation</div>
            )}

            <div />
          </div>

          {/* Rows */}
          <div className="divide-y divide-white/10">
            {holdings.map((holding) => (
              <div
                key={holding.id}
                className={`grid gap-3 px-6 py-4 md:items-center ${
                  mode === "shares"
                    ? "md:grid-cols-[1.2fr_1fr_1fr_40px]"
                    : "md:grid-cols-[1.5fr_1fr_40px]"
                }`}
              >
                {/* Symbol */}
                <div>
                  <label className="mb-1 block text-[9px] uppercase tracking-wider text-zinc-700 md:hidden">
                    Stock Symbol
                  </label>

                  <input
                    value={holding.symbol}
                    onChange={(e) =>
                      updateHolding(
                        holding.id,
                        "symbol",
                        e.target.value.toUpperCase()
                      )
                    }
                    placeholder="NFLX"
                    className="w-full border border-white/10 bg-[#080b10] px-3 py-3 font-mono text-sm uppercase outline-none placeholder:text-zinc-700 focus:border-emerald-400/50"
                  />
                </div>

                {/* Shares */}
                {mode === "shares" && (
                  <>
                    <div>
                      <label className="mb-1 block text-[9px] uppercase tracking-wider text-zinc-700 md:hidden">
                        Shares
                      </label>

                      <input
                        type="number"
                        min="0"
                        step="any"
                        value={holding.shares}
                        onChange={(e) =>
                          updateHolding(
                            holding.id,
                            "shares",
                            e.target.value
                          )
                        }
                        placeholder="5"
                        className="w-full border border-white/10 bg-[#080b10] px-3 py-3 font-mono text-sm outline-none placeholder:text-zinc-700 focus:border-emerald-400/50"
                      />
                    </div>

                    {/* Buy price */}
                    <div>
                      <label className="mb-1 block text-[9px] uppercase tracking-wider text-zinc-700 md:hidden">
                        Average Buy Price
                      </label>

                      <div className="flex border border-white/10 bg-[#080b10]">
                        <span className="border-r border-white/10 px-3 py-3 font-mono text-xs text-zinc-600">
                          ₹
                        </span>

                        <input
                          type="number"
                          min="0"
                          step="any"
                          value={holding.buyPrice}
                          onChange={(e) =>
                            updateHolding(
                              holding.id,
                              "buyPrice",
                              e.target.value
                            )
                          }
                          placeholder="650"
                          className="w-full bg-transparent px-3 py-3 font-mono text-sm outline-none placeholder:text-zinc-700"
                        />
                      </div>
                    </div>
                  </>
                )}

                {/* Amount */}
                {mode === "amounts" && (
                  <div>
                    <label className="mb-1 block text-[9px] uppercase tracking-wider text-zinc-700 md:hidden">
                      Amount Invested
                    </label>

                    <div className="flex border border-white/10 bg-[#080b10]">
                      <span className="border-r border-white/10 px-3 py-3 font-mono text-xs text-zinc-600">
                        ₹
                      </span>

                      <input
                        type="number"
                        min="0"
                        step="any"
                        value={holding.amount}
                        onChange={(e) =>
                          updateHolding(
                            holding.id,
                            "amount",
                            e.target.value
                          )
                        }
                        placeholder="200000"
                        className="w-full bg-transparent px-3 py-3 font-mono text-sm outline-none placeholder:text-zinc-700"
                      />
                    </div>
                  </div>
                )}

                {/* Weight */}
                {mode === "weights" && (
                  <div>
                    <label className="mb-1 block text-[9px] uppercase tracking-wider text-zinc-700 md:hidden">
                      Allocation
                    </label>

                    <div className="flex border border-white/10 bg-[#080b10]">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="any"
                        value={holding.weight}
                        onChange={(e) =>
                          updateHolding(
                            holding.id,
                            "weight",
                            e.target.value
                          )
                        }
                        placeholder="20"
                        className="w-full bg-transparent px-3 py-3 font-mono text-sm outline-none placeholder:text-zinc-700"
                      />

                      <span className="border-l border-white/10 px-3 py-3 font-mono text-xs text-zinc-600">
                        %
                      </span>
                    </div>
                  </div>
                )}

                {/* Delete */}
                <button
                  type="button"
                  onClick={() =>
                    removeHolding(holding.id)
                  }
                  disabled={holdings.length === 1}
                  className="flex h-10 w-10 items-center justify-center text-zinc-700 transition hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-30"
                  title="Remove holding"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            ))}
          </div>

          {/* Add holding */}
          <div className="border-t border-white/10 px-6 py-4">
            <button
              type="button"
              onClick={addHolding}
              className="flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.18em] text-zinc-500 transition hover:text-emerald-400"
            >
              <Plus size={14} />
              Add Asset
            </button>
          </div>
        </div>

        {/* Weight summary */}
        {mode === "weights" && (
          <div className="mt-4 flex items-center justify-between border border-white/10 bg-[#0b0f15] px-6 py-4">
            <span className="text-[10px] uppercase tracking-[0.18em] text-zinc-600">
              Total Allocation
            </span>

            <span className="font-mono text-sm">
              {holdings
                .reduce(
                  (sum, holding) =>
                    sum +
                    Number(holding.weight || 0),
                  0
                )
                .toFixed(2)}
              %
            </span>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-4 border border-red-500/30 bg-red-500/5 px-4 py-3 text-xs text-red-400">
            {error}
          </div>
        )}

        {/* Navigation */}
        <div className="mt-8 flex flex-col-reverse justify-between gap-4 sm:flex-row">
          <button
            type="button"
            onClick={() => {
              window.location.href = "/";
            }}
            className="flex items-center justify-center gap-2 border border-white/10 px-5 py-4 text-[10px] font-medium uppercase tracking-[0.18em] text-zinc-500 transition hover:bg-white/5 hover:text-zinc-200"
          >
            <ArrowLeft size={15} />
            Back to Profile
          </button>

          <button
            type="button"
            onClick={handleContinue}
            className="group flex items-center justify-center gap-3 bg-emerald-400 px-6 py-4 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#06100c] transition hover:bg-emerald-300"
          >
            Continue to Dashboard

            <ArrowRight
              size={16}
              className="transition-transform group-hover:translate-x-1"
            />
          </button>
        </div>
      </section>
    </main>
  );
}