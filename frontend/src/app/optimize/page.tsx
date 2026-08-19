"use client";

import { useEffect, useState } from "react";
import Navigation from "@/components/Navigation";
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Shield,
  TrendingDown,
} from "lucide-react";

type OptimizationMethod =
  | "MINIMUM_VARIANCE"
  | "RISK_PARITY"
  | "CVAR";

interface Comparison {
  before_volatility: number;
  after_volatility: number;
  before_drawdown: number;
  after_drawdown: number;
  before_sharpe: number;
  after_sharpe: number;
  before_var: number;
  after_var: number;
  before_expected_shortfall: number;
  after_expected_shortfall: number;
  before_risk_score: number;
  after_risk_score: number;
}

interface OptimizationResult {
  original_weights: Record<string, number>;
  optimized_weights: Record<string, number>;
  comparison: Comparison;
  maximum_weight: number;
  method: string;
  target_volatility: number | null;
  risk_free_rate: number;
  trading_days: number;
  risk_contribution_before: Record<string, number>;
  risk_contribution_after: Record<string, number>;
}

interface PortfolioData {
  calculatedWeights?: Record<string, number>;
}

const METHODS: {
  value: OptimizationMethod;
  title: string;
  description: string;
}[] = [
  {
    value: "MINIMUM_VARIANCE",
    title: "Minimum Variance",
    description:
      "Minimizes overall portfolio volatility using the historical covariance matrix.",
  },
  {
    value: "RISK_PARITY",
    title: "Risk Parity",
    description:
      "Attempts to distribute total portfolio risk equally across assets.",
  },
  {
    value: "CVAR",
    title: "CVaR",
    description:
      "Minimizes expected loss in the worst 5% of historical portfolio outcomes.",
  },
];

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function formatChange(before: number, after: number) {
  const change = (after - before) * 100;
  return `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`;
}

export default function OptimizePage() {
  const [weights, setWeights] =
    useState<Record<string, number>>({});

  const [method, setMethod] =
    useState<OptimizationMethod>("MINIMUM_VARIANCE");

  const [maximumWeight, setMaximumWeight] =
    useState("30");

  const [targetVolatility, setTargetVolatility] =
    useState("");

  const [riskFreeRate, setRiskFreeRate] =
    useState("0");

  const [result, setResult] =
    useState<OptimizationResult | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  useEffect(() => {
    const storedPortfolio =
      sessionStorage.getItem(
        "portfolioiq-portfolio"
      );

    if (!storedPortfolio) {
      window.location.href = "/portfolio";
      return;
    }

    try {
      const portfolio: PortfolioData =
        JSON.parse(storedPortfolio);

      const calculatedWeights =
        portfolio.calculatedWeights ?? {};

      if (
        Object.keys(calculatedWeights).length === 0
      ) {
        window.location.href = "/portfolio";
        return;
      }

      setWeights(calculatedWeights);
    } catch {
      setError(
        "Unable to restore portfolio data."
      );
    }
  }, []);

  const optimize = async () => {
    if (Object.keys(weights).length === 0) {
      setError(
        "Portfolio weights are unavailable."
      );
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/optimization/optimize",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            weights,
            maximum_weight:
              Number(maximumWeight) / 100,
            target_volatility:
              targetVolatility.trim()
                ? Number(targetVolatility) / 100
                : null,
            risk_free_rate:
              Number(riskFreeRate) / 100,
            method,
          }),
        }
      );

      if (!response.ok) {
        let message =
          "Portfolio optimization failed.";

        try {
          const errorData =
            await response.json();

          if (errorData.detail) {
            message = errorData.detail;
          }
        } catch {
          // Keep default message.
        }

        throw new Error(message);
      }

      const data: OptimizationResult =
        await response.json();

      setResult(data);

      sessionStorage.setItem(
        "portfolioiq-optimization",
        JSON.stringify(data)
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to PortfolioIQ backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const comparisonMetrics = result
    ? [
        {
          label: "Annualized Volatility",
          before:
            result.comparison.before_volatility,
          after:
            result.comparison.after_volatility,
          lowerIsBetter: true,
        },
        {
          label: "Maximum Drawdown",
          before:
            result.comparison.before_drawdown,
          after:
            result.comparison.after_drawdown,
          lowerIsBetter: true,
        },
        {
          label: "Sharpe Ratio",
          before:
            result.comparison.before_sharpe,
          after:
            result.comparison.after_sharpe,
          lowerIsBetter: false,
        },
        {
          label: "Historical VaR",
          before:
            result.comparison.before_var,
          after:
            result.comparison.after_var,
          lowerIsBetter: true,
        },
        {
          label: "Expected Shortfall",
          before:
            result.comparison.before_expected_shortfall,
          after:
            result.comparison.after_expected_shortfall,
          lowerIsBetter: true,
        },
        {
          label: "Risk Score",
          before:
            result.comparison.before_risk_score,
          after:
            result.comparison.after_risk_score,
          lowerIsBetter: true,
          percent: false,
        },
      ]
    : [];

  const isImproved = (
    before: number,
    after: number,
    lowerIsBetter: boolean
  ) => {
    return lowerIsBetter
      ? after < before
      : after > before;
  };

  return (
  <main className="min-h-screen bg-[#080b10] text-zinc-200">
    <Navigation />

    <div className="mx-auto max-w-7xl px-6 py-10">

        {/* Header */}
        <div className="mb-10 flex items-start justify-between">
          <div>
            <button
              onClick={() =>
                (window.location.href =
                  "/risk")
              }
              className="mb-6 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-zinc-600 transition hover:text-zinc-300"
            >
              <ArrowLeft size={13} />
              Back to Risk
            </button>

            <div className="text-[10px] uppercase tracking-[0.3em] text-emerald-400">
              PortfolioIQ / Optimization
            </div>

            <h1 className="mt-3 text-3xl font-semibold tracking-tight">
              Quantitative Optimization
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-600">
              Compare quantitative portfolio construction
              methods and evaluate how the optimized allocation
              changes portfolio risk.
            </p>
          </div>

          <div className="hidden items-center gap-2 border border-white/10 bg-[#0c1118] px-4 py-3 md:flex">
            <Shield
              size={16}
              className="text-emerald-400"
            />
            <span className="text-[9px] uppercase tracking-[0.18em] text-zinc-600">
              Quant Engine
            </span>
          </div>
        </div>

        {/* Method selection */}
        <section className="mb-8">
          <div className="mb-4 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
            Optimization Method
          </div>

          <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">
            {METHODS.map((item) => (
              <button
                key={item.value}
                type="button"
                onClick={() => {
                  setMethod(item.value);
                  setResult(null);
                  setError("");
                }}
                className={`p-6 text-left transition ${
                  method === item.value
                    ? "bg-[#111820]"
                    : "bg-[#0b0f15] hover:bg-[#10151c]"
                }`}
              >
                <div className="mb-5 flex items-center justify-between">
                  <BarChart3
                    size={18}
                    className={
                      method === item.value
                        ? "text-emerald-400"
                        : "text-zinc-600"
                    }
                  />

                  {method === item.value && (
                    <CheckCircle2
                      size={15}
                      className="text-emerald-400"
                    />
                  )}
                </div>

                <div className="text-xs font-semibold uppercase tracking-[0.15em]">
                  {item.title}
                </div>

                <p className="mt-3 text-xs leading-5 text-zinc-600">
                  {item.description}
                </p>
              </button>
            ))}
          </div>
        </section>

        {/* Constraints */}
        <section className="mb-8 border border-white/10 bg-[#0c1118] p-6">
          <div className="mb-6">
            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Optimization Constraints
            </div>

            <div className="mt-1 text-xs text-zinc-700">
              Control the feasible portfolio space.
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-3">

            <div>
              <label className="mb-2 block text-[9px] uppercase tracking-wider text-zinc-600">
                Maximum Asset Weight
              </label>

              <div className="flex border border-white/10 bg-[#080b10]">
                <input
                  type="number"
                  min="1"
                  max="100"
                  step="1"
                  value={maximumWeight}
                  onChange={(e) =>
                    setMaximumWeight(
                      e.target.value
                    )
                  }
                  className="w-full bg-transparent px-3 py-3 font-mono text-sm outline-none"
                />

                <span className="border-l border-white/10 px-3 py-3 font-mono text-xs text-zinc-600">
                  %
                </span>
              </div>
            </div>

            <div>
              <label className="mb-2 block text-[9px] uppercase tracking-wider text-zinc-600">
                Target Volatility
              </label>

              <div className="flex border border-white/10 bg-[#080b10]">
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  placeholder="Optional"
                  value={targetVolatility}
                  onChange={(e) =>
                    setTargetVolatility(
                      e.target.value
                    )
                  }
                  className="w-full bg-transparent px-3 py-3 font-mono text-sm outline-none placeholder:text-zinc-700"
                />

                <span className="border-l border-white/10 px-3 py-3 font-mono text-xs text-zinc-600">
                  %
                </span>
              </div>
            </div>

            <div>
              <label className="mb-2 block text-[9px] uppercase tracking-wider text-zinc-600">
                Risk-Free Rate
              </label>

              <div className="flex border border-white/10 bg-[#080b10]">
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={riskFreeRate}
                  onChange={(e) =>
                    setRiskFreeRate(
                      e.target.value
                    )
                  }
                  className="w-full bg-transparent px-3 py-3 font-mono text-sm outline-none"
                />

                <span className="border-l border-white/10 px-3 py-3 font-mono text-xs text-zinc-600">
                  %
                </span>
              </div>
            </div>

          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {Object.entries(weights).map(
              ([symbol, weight]) => (
                <div
                  key={symbol}
                  className="border border-white/10 bg-[#080b10] px-3 py-2 font-mono text-[10px]"
                >
                  <span className="text-zinc-400">
                    {symbol}
                  </span>

                  <span className="ml-3 text-zinc-700">
                    {formatPercent(weight)}
                  </span>
                </div>
              )
            )}
          </div>

          {error && (
            <div className="mt-5 border border-red-400/20 bg-red-400/5 p-4 text-xs text-red-300">
              {error}
            </div>
          )}

          <button
            type="button"
            onClick={optimize}
            disabled={loading}
            className="mt-6 flex items-center gap-3 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-black transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Running Optimization..."
              : "Run Optimization"}

            {!loading && (
              <ArrowRight size={14} />
            )}
          </button>
        </section>

        {/* Results */}
        {result && (
          <>
            {/* Result header */}
            <section className="mb-8 border border-white/10 bg-[#0c1118] p-7">
              <div className="flex flex-wrap items-start justify-between gap-5">
                <div>
                  <div className="text-[10px] uppercase tracking-[0.2em] text-emerald-400">
                    Optimization Complete
                  </div>

                  <h2 className="mt-2 text-xl font-semibold">
                    {result.method.replaceAll(
                      "_",
                      " "
                    )}
                  </h2>

                  <p className="mt-2 text-xs text-zinc-600">
                    Based on {result.trading_days.toLocaleString()} trading days
                    of historical asset returns.
                  </p>
                </div>

                <div className="text-right">
                  <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-700">
                    Risk Score
                  </div>

                  <div className="mt-1 font-mono text-3xl text-emerald-400">
                    {result.comparison.after_risk_score.toFixed(
                      1
                    )}
                  </div>
                </div>
              </div>
            </section>

            {/* Comparison */}
            <section className="mb-8">
              <div className="mb-4 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                Before / After Analysis
              </div>

              <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">
                {comparisonMetrics.map(
                  (metric) => {
                    const improved =
                      isImproved(
                        metric.before,
                        metric.after,
                        metric.lowerIsBetter
                      );

                    return (
                      <div
                        key={metric.label}
                        className="bg-[#0c1118] p-6"
                      >
                        <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                          {metric.label}
                        </div>

                        <div className="mt-5 grid grid-cols-2 gap-4">
                          <div>
                            <div className="text-[8px] uppercase text-zinc-700">
                              Before
                            </div>

                            <div className="mt-1 font-mono text-sm text-zinc-500">
                              {metric.percent === false
                                ? metric.before.toFixed(2)
                                : formatPercent(
                                    metric.before
                                  )}
                            </div>
                          </div>

                          <div>
                            <div className="text-[8px] uppercase text-zinc-700">
                              After
                            </div>

                            <div
                              className={`mt-1 font-mono text-sm ${
                                improved
                                  ? "text-emerald-400"
                                  : "text-zinc-300"
                              }`}
                            >
                              {metric.percent === false
                                ? metric.after.toFixed(2)
                                : formatPercent(
                                    metric.after
                                  )}
                            </div>
                          </div>
                        </div>

                        <div className="mt-4 flex items-center justify-between">
                          <span className="font-mono text-[9px] text-zinc-700">
                            {formatChange(
                              metric.before,
                              metric.after
                            )}
                          </span>

                          {improved && (
                            <TrendingDown
                              size={13}
                              className="text-emerald-400"
                            />
                          )}
                        </div>
                      </div>
                    );
                  }
                )}
              </div>
            </section>

            {/* Allocation */}
            <section className="mb-8 grid gap-px border border-white/10 bg-white/10 lg:grid-cols-2">

              <div className="bg-[#0c1118] p-7">
                <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                  Optimized Allocation
                </div>

                <div className="mt-6 space-y-5">
                  {Object.entries(
                    result.optimized_weights
                  ).map(
                    ([symbol, value]) => {
                      const before =
                        result.original_weights[
                          symbol
                        ] ?? 0;

                      return (
                        <div key={symbol}>
                          <div className="mb-2 flex justify-between text-[10px]">
                            <span className="font-mono text-zinc-400">
                              {symbol}
                            </span>

                            <span className="font-mono text-zinc-600">
                              {formatPercent(value)}
                            </span>
                          </div>

                          <div className="h-1 bg-zinc-900">
                            <div
                              className="h-1 bg-emerald-400"
                              style={{
                                width: `${value * 100}%`,
                              }}
                            />
                          </div>

                          <div className="mt-1 text-[9px] font-mono text-zinc-700">
                            Previous:{" "}
                            {formatPercent(before)}
                            {" · "}
                            Change:{" "}
                            {formatChange(
                              before,
                              value
                            )}
                          </div>
                        </div>
                      );
                    }
                  )}
                </div>
              </div>

              <div className="bg-[#0c1118] p-7">
                <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                  Risk Contribution
                </div>

                <div className="mt-2 text-xs text-zinc-700">
                  Contribution to total portfolio risk.
                </div>

                <div className="mt-6 space-y-5">
                  {Object.entries(
                    result.risk_contribution_after
                  ).map(
                    ([symbol, value]) => (
                      <div key={symbol}>
                        <div className="mb-2 flex justify-between text-[10px]">
                          <span className="font-mono text-zinc-400">
                            {symbol}
                          </span>

                          <span className="font-mono text-zinc-600">
                            {formatPercent(value)}
                          </span>
                        </div>

                        <div className="h-1 bg-zinc-900">
                          <div
                            className="h-1 bg-zinc-500"
                            style={{
                              width: `${value * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>

            </section>

            {/* Footer */}
            <div className="flex flex-wrap justify-between gap-3">
              <button
                type="button"
                onClick={() =>
                  (window.location.href =
                    "/risk")
                }
                className="flex items-center gap-2 border border-white/10 px-5 py-3 text-[10px] uppercase tracking-[0.18em] text-zinc-500 transition hover:text-zinc-200"
              >
                <ArrowLeft size={13} />
                Back to Risk
              </button>

              <button
                type="button"
                onClick={() =>
                  (window.location.href =
                    "/dashboard")
                }
                className="flex items-center gap-2 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-black transition hover:bg-emerald-300"
              >
                Dashboard
                <ArrowRight size={13} />
              </button>
            </div>
          </>
        )}

      </div>
    </main>
  );
}