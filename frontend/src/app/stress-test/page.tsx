"use client";

import { useEffect, useState } from "react";
import Navigation from "@/components/Navigation";
import {
  ArrowLeft,
  ArrowRight,
  AlertTriangle,
  Shield,
} from "lucide-react";

type StressResult = {
  scenario: {
    name: string;
    asset_shocks: Record<string, number>;
  };
  portfolio_impact: number;
  portfolio_value_after: number;
  recovery_required: number | null;
  asset_contributions: Record<
    string,
    {
      weight: number;
      shock: number;
      contribution: number;
    }
  >;
};

type HistoricalStressResult = {
  scenario: {
    name: string;
    start_date: string;
    end_date: string;
    description: string;
  };
  portfolio_impact: number;
  portfolio_value_after: number;
  recovery_required: number | null;
  asset_contributions: Record<
    string,
    {
      weight: number;
      historical_return: number;
      contribution: number;
    }
  >;
};

const SCENARIOS = [
  {
    value: "MARKET_CORRECTION",
    label: "Market Correction",
    description:
      "Broad 10% decline across all portfolio assets.",
  },
  {
    value: "MARKET_CRASH",
    label: "Market Crash",
    description:
      "Broad 20% decline across all portfolio assets.",
  },
  {
    value: "SEVERE_CRASH",
    label: "Severe Crash",
    description:
      "Broad 35% decline across all portfolio assets.",
  },
  {
    value: "TECH_SELL_OFF",
    label: "Tech Sell-Off",
    description:
      "Technology and growth assets experience a larger decline.",
  },
  {
    value: "DEFENSIVE_SECTOR_SHOCK",
    label: "Defensive Sector Shock",
    description:
      "Defensive holdings experience a concentrated decline.",
  },
  {
    value: "CONSUMER_DISCRETIONARY_SHOCK",
    label: "Consumer Discretionary Shock",
    description:
      "Consumer-sensitive holdings experience a concentrated decline.",
  },
];

const HISTORICAL_SCENARIOS = [
  {
    value: "COVID_CRASH",
    label: "COVID-19 Crash",
    dates: "Feb 19, 2020 → Mar 23, 2020",
    description:
      "Actual portfolio performance during the initial COVID-19 market shock.",
  },
  {
    value: "2022_BEAR_MARKET",
    label: "2022 Bear Market",
    dates: "Jan 3, 2022 → Oct 12, 2022",
    description:
      "Actual portfolio performance during the 2022 equity bear market.",
  },
];

function percent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

export default function StressTestPage() {
  const [weights, setWeights] =
    useState<Record<string, number>>({});

  const [scenario, setScenario] =
    useState("MARKET_CRASH");

  const [historicalScenario, setHistoricalScenario] =
    useState("COVID_CRASH");

  const [result, setResult] =
    useState<StressResult | null>(null);

  const [historicalResult, setHistoricalResult] =
    useState<HistoricalStressResult | null>(null);

  const [mode, setMode] =
    useState<"HYPOTHETICAL" | "HISTORICAL">(
      "HYPOTHETICAL"
    );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  useEffect(() => {
    const stored =
      sessionStorage.getItem(
        "portfolioiq-portfolio"
      );

    if (!stored) {
      window.location.href = "/portfolio";
      return;
    }

    try {
      const portfolio = JSON.parse(stored);

      if (
        !portfolio.calculatedWeights ||
        Object.keys(
          portfolio.calculatedWeights
        ).length === 0
      ) {
        window.location.href = "/portfolio";
        return;
      }

      setWeights(
        portfolio.calculatedWeights
      );
    } catch {
      setError(
        "Unable to restore portfolio data."
      );
    }
  }, []);

  // ==========================================================
  // Hypothetical Stress Test
  // ==========================================================

  const runStressTest = async () => {
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
        "http://127.0.0.1:8000/api/stress-test/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            weights,
            scenario,
          }),
        }
      );

      if (!response.ok) {
        let message =
          "Stress test failed.";

        try {
          const data =
            await response.json();

          if (data.detail) {
            message = data.detail;
          }
        } catch {
          // Keep default message.
        }

        throw new Error(message);
      }

      const data: StressResult =
        await response.json();

      setResult(data);
      setHistoricalResult(null);

      sessionStorage.setItem(
        "portfolioiq-stress-test",
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

  // ==========================================================
  // Historical Stress Test
  // ==========================================================

  const runHistoricalStressTest =
    async () => {
      if (
        Object.keys(weights).length === 0
      ) {
        setError(
          "Portfolio weights are unavailable."
        );
        return;
      }

      setLoading(true);
      setError("");

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/stress-test/historical",
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              weights,
              scenario: historicalScenario,
            }),
          }
        );

        if (!response.ok) {
          let message =
            "Historical stress test failed.";

          try {
            const data =
              await response.json();

            if (data.detail) {
              message = data.detail;
            }
          } catch {
            // Keep default message.
          }

          throw new Error(message);
        }

        const data: HistoricalStressResult =
          await response.json();

        setHistoricalResult(data);
        setResult(null);

        sessionStorage.setItem(
          "portfolioiq-historical-stress-test",
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

  // ==========================================================
  // Largest Contributors
  // ==========================================================

  const largestHypotheticalContributor =
    result
      ? Object.entries(
          result.asset_contributions
        ).sort(
          ([, a], [, b]) =>
            a.contribution -
            b.contribution
        )[0]
      : null;

  const largestHistoricalContributor =
    historicalResult
      ? Object.entries(
          historicalResult.asset_contributions
        ).sort(
          ([, a], [, b]) =>
            a.contribution -
            b.contribution
        )[0]
      : null;

  // ==========================================================
  // Render
  // ==========================================================

  return (
  <main className="min-h-screen bg-[#080b10] text-zinc-200">
    <Navigation />

    <div className="mx-auto max-w-7xl px-6 py-10">

        {/* ==================================================
            Header
        ================================================== */}

        <div className="mb-10">
          <button
            onClick={() =>
              (window.location.href =
                "/risk")
            }
            className="mb-6 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-zinc-600 hover:text-zinc-300"
          >
            <ArrowLeft size={13} />
            Back to Risk
          </button>

          <div className="flex items-start justify-between">
            <div>
              <div className="text-[10px] uppercase tracking-[0.3em] text-emerald-400">
                PortfolioIQ / Stress Testing
              </div>

              <h1 className="mt-3 text-3xl font-semibold tracking-tight">
                Scenario Analysis
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-600">
                Evaluate how your portfolio responds
                to hypothetical market shocks and
                historical market events.
              </p>
            </div>

            <div className="hidden items-center gap-2 border border-white/10 bg-[#0c1118] px-4 py-3 md:flex">
              <Shield
                size={16}
                className="text-emerald-400"
              />

              <span className="text-[9px] uppercase tracking-[0.18em] text-zinc-600">
                Quant Risk Engine
              </span>
            </div>
          </div>
        </div>

        {/* ==================================================
            Mode Selector
        ================================================== */}

        <section className="mb-8 border border-white/10 bg-[#0c1118] p-2">
          <div className="grid grid-cols-2 gap-2">

            <button
              type="button"
              onClick={() => {
                setMode("HYPOTHETICAL");
                setResult(null);
                setHistoricalResult(null);
                setError("");
              }}
              className={`px-5 py-4 text-[10px] font-semibold uppercase tracking-[0.18em] transition ${
                mode === "HYPOTHETICAL"
                  ? "bg-emerald-400 text-black"
                  : "text-zinc-600 hover:bg-white/5 hover:text-zinc-300"
              }`}
            >
              Hypothetical Scenarios
            </button>

            <button
              type="button"
              onClick={() => {
                setMode("HISTORICAL");
                setResult(null);
                setHistoricalResult(null);
                setError("");
              }}
              className={`px-5 py-4 text-[10px] font-semibold uppercase tracking-[0.18em] transition ${
                mode === "HISTORICAL"
                  ? "bg-emerald-400 text-black"
                  : "text-zinc-600 hover:bg-white/5 hover:text-zinc-300"
              }`}
            >
              Historical Scenarios
            </button>

          </div>
        </section>

        {/* ==================================================
            Hypothetical Scenario Selection
        ================================================== */}

        {mode === "HYPOTHETICAL" && (
          <section className="mb-8 border border-white/10 bg-[#0c1118] p-6">

            <div className="mb-6">
              <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                Select Stress Scenario
              </div>

              <div className="mt-1 text-xs text-zinc-700">
                Apply a hypothetical shock to the
                current portfolio.
              </div>
            </div>

            <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">
              {SCENARIOS.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => {
                    setScenario(
                      item.value
                    );
                    setResult(null);
                    setError("");
                  }}
                  className={`p-5 text-left transition ${
                    scenario === item.value
                      ? "bg-[#111820]"
                      : "bg-[#0b0f15] hover:bg-[#10151c]"
                  }`}
                >
                  <div className="flex items-center justify-between">

                    <span className="text-xs font-semibold uppercase tracking-[0.12em]">
                      {item.label}
                    </span>

                    {scenario ===
                      item.value && (
                      <span className="h-2 w-2 rounded-full bg-emerald-400" />
                    )}

                  </div>

                  <p className="mt-3 text-xs leading-5 text-zinc-600">
                    {item.description}
                  </p>
                </button>
              ))}
            </div>

            {error && (
              <div className="mt-5 border border-red-400/20 bg-red-400/5 p-4 text-xs text-red-300">
                {error}
              </div>
            )}

            <button
              onClick={runStressTest}
              disabled={loading}
              className="mt-6 flex items-center gap-3 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-black hover:bg-emerald-300 disabled:opacity-50"
            >
              {loading
                ? "Running Scenario..."
                : "Run Stress Test"}

              {!loading && (
                <ArrowRight size={14} />
              )}
            </button>

          </section>
        )}

        {/* ==================================================
            Historical Scenario Selection
        ================================================== */}

        {mode === "HISTORICAL" && (
          <section className="mb-8 border border-white/10 bg-[#0c1118] p-6">

            <div className="mb-6">
              <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                Historical Market Events
              </div>

              <div className="mt-1 text-xs text-zinc-700">
                Evaluate the current portfolio against
                actual historical market periods.
              </div>
            </div>

            <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-2">

              {HISTORICAL_SCENARIOS.map(
                (item) => (
                  <button
                    key={item.value}
                    type="button"
                    onClick={() => {
                      setHistoricalScenario(
                        item.value
                      );
                      setHistoricalResult(
                        null
                      );
                      setError("");
                    }}
                    className={`p-6 text-left transition ${
                      historicalScenario ===
                      item.value
                        ? "bg-[#111820]"
                        : "bg-[#0b0f15] hover:bg-[#10151c]"
                    }`}
                  >
                    <div className="flex items-center justify-between">

                      <span className="text-xs font-semibold uppercase tracking-[0.12em]">
                        {item.label}
                      </span>

                      {historicalScenario ===
                        item.value && (
                        <span className="h-2 w-2 rounded-full bg-emerald-400" />
                      )}

                    </div>

                    <div className="mt-3 font-mono text-[10px] text-emerald-400">
                      {item.dates}
                    </div>

                    <p className="mt-3 text-xs leading-5 text-zinc-600">
                      {item.description}
                    </p>
                  </button>
                )
              )}

            </div>

            {error && (
              <div className="mt-5 border border-red-400/20 bg-red-400/5 p-4 text-xs text-red-300">
                {error}
              </div>
            )}

            <button
              onClick={
                runHistoricalStressTest
              }
              disabled={loading}
              className="mt-6 flex items-center gap-3 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-black hover:bg-emerald-300 disabled:opacity-50"
            >
              {loading
                ? "Analyzing Historical Event..."
                : "Analyze Historical Event"}

              {!loading && (
                <ArrowRight size={14} />
              )}
            </button>

          </section>
        )}

        {/* ==================================================
            Hypothetical Results
        ================================================== */}

        {result &&
          mode === "HYPOTHETICAL" && (
            <>
              <section className="mb-8 grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">

                <div className="bg-[#0c1118] p-7">
                  <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-600">
                    Portfolio Impact
                  </div>

                  <div className="mt-3 font-mono text-3xl text-red-400">
                    {percent(
                      result.portfolio_impact
                    )}
                  </div>

                  <div className="mt-2 text-xs text-zinc-700">
                    Estimated portfolio loss
                  </div>
                </div>

                <div className="bg-[#0c1118] p-7">
                  <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-600">
                    Value After Shock
                  </div>

                  <div className="mt-3 font-mono text-3xl text-zinc-200">
                    {percent(
                      result.portfolio_value_after
                    )}
                  </div>

                  <div className="mt-2 text-xs text-zinc-700">
                    Remaining portfolio value
                  </div>
                </div>

                <div className="bg-[#0c1118] p-7">
                  <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-600">
                    Recovery Required
                  </div>

                  <div className="mt-3 font-mono text-3xl text-amber-400">
                    {result.recovery_required ===
                    null
                      ? "N/A"
                      : percent(
                          result.recovery_required
                        )}
                  </div>

                  <div className="mt-2 text-xs text-zinc-700">
                    Gain required to recover losses
                  </div>
                </div>

              </section>

              {largestHypotheticalContributor && (
                <section className="mb-8 border border-white/10 bg-[#0c1118] p-6">
                  <div className="flex items-start gap-4">

                    <AlertTriangle
                      size={18}
                      className="mt-1 text-amber-400"
                    />

                    <div>
                      <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                        Largest Loss Contributor
                      </div>

                      <div className="mt-2 text-lg font-semibold">
                        {
                          largestHypotheticalContributor[0]
                        }
                      </div>

                      <p className="mt-1 text-xs text-zinc-600">
                        Contributes{" "}
                        <span className="font-mono text-red-400">
                          {percent(
                            largestHypotheticalContributor[1]
                              .contribution
                          )}
                        </span>{" "}
                        to the total portfolio loss
                        under this scenario.
                      </p>
                    </div>

                  </div>
                </section>
              )}

              <section className="border border-white/10 bg-[#0c1118]">

                <div className="border-b border-white/10 p-6">
                  <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                    Asset-Level Stress Impact
                  </div>

                  <div className="mt-1 text-xs text-zinc-700">
                    {result.scenario.name}
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left">

                    <thead>
                      <tr className="border-b border-white/10 text-[9px] uppercase tracking-[0.15em] text-zinc-700">
                        <th className="px-6 py-4">
                          Asset
                        </th>

                        <th className="px-6 py-4">
                          Weight
                        </th>

                        <th className="px-6 py-4">
                          Shock
                        </th>

                        <th className="px-6 py-4">
                          Loss Contribution
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {Object.entries(
                        result.asset_contributions
                      ).map(
                        ([
                          symbol,
                          data,
                        ]) => (
                          <tr
                            key={symbol}
                            className="border-b border-white/5 last:border-0"
                          >
                            <td className="px-6 py-5 font-mono text-xs text-zinc-300">
                              {symbol}
                            </td>

                            <td className="px-6 py-5 font-mono text-xs text-zinc-500">
                              {percent(
                                data.weight
                              )}
                            </td>

                            <td className="px-6 py-5 font-mono text-xs text-red-400">
                              {percent(
                                data.shock
                              )}
                            </td>

                            <td className="px-6 py-5">
                              <div className="flex items-center gap-4">

                                <div className="h-1.5 w-32 bg-zinc-900">
                                  <div
                                    className="h-1.5 bg-red-400"
                                    style={{
                                      width: `${Math.min(
                                        Math.abs(
                                          data.contribution
                                        ) * 100,
                                        100
                                      )}%`,
                                    }}
                                  />
                                </div>

                                <span className="font-mono text-xs text-red-400">
                                  {percent(
                                    data.contribution
                                  )}
                                </span>

                              </div>
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>

                  </table>
                </div>
              </section>

              <div className="mt-8 flex justify-between">

                <button
                  onClick={() =>
                    (window.location.href =
                      "/risk")
                  }
                  className="flex items-center gap-2 border border-white/10 px-5 py-3 text-[10px] uppercase tracking-[0.18em] text-zinc-500 hover:text-zinc-200"
                >
                  <ArrowLeft size={13} />
                  Back to Risk
                </button>

                <button
                  onClick={() =>
                    (window.location.href =
                      "/dashboard")
                  }
                  className="flex items-center gap-2 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-black hover:bg-emerald-300"
                >
                  Dashboard
                  <ArrowRight size={13} />
                </button>

              </div>
            </>
          )}

        {/* ==================================================
            Historical Results
        ================================================== */}

        {historicalResult &&
          mode === "HISTORICAL" && (
            <>
              <section className="mb-8 border border-white/10 bg-[#0c1118] p-6">

                <div className="text-[10px] uppercase tracking-[0.2em] text-emerald-400">
                  Historical Event
                </div>

                <h2 className="mt-2 text-xl font-semibold">
                  {historicalResult.scenario.name}
                </h2>

                <div className="mt-2 font-mono text-[10px] text-zinc-600">
                  {historicalResult.scenario.start_date}
                  {" → "}
                  {historicalResult.scenario.end_date}
                </div>

                <p className="mt-4 max-w-3xl text-xs leading-6 text-zinc-600">
                  {
                    historicalResult
                      .scenario.description
                  }
                </p>

              </section>

              <section className="mb-8 grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">

                <div className="bg-[#0c1118] p-7">
                  <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-600">
                    Historical Impact
                  </div>

                  <div className="mt-3 font-mono text-3xl text-red-400">
                    {percent(
                      historicalResult.portfolio_impact
                    )}
                  </div>

                  <div className="mt-2 text-xs text-zinc-700">
                    Actual portfolio loss during event
                  </div>
                </div>

                <div className="bg-[#0c1118] p-7">
                  <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-600">
                    Value After Event
                  </div>

                  <div className="mt-3 font-mono text-3xl text-zinc-200">
                    {percent(
                      historicalResult.portfolio_value_after
                    )}
                  </div>

                  <div className="mt-2 text-xs text-zinc-700">
                    Remaining portfolio value
                  </div>
                </div>

                <div className="bg-[#0c1118] p-7">
                  <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-600">
                    Recovery Required
                  </div>

                  <div className="mt-3 font-mono text-3xl text-amber-400">
                    {historicalResult.recovery_required ===
                    null
                      ? "N/A"
                      : percent(
                          historicalResult.recovery_required
                        )}
                  </div>

                  <div className="mt-2 text-xs text-zinc-700">
                    Gain required to recover losses
                  </div>
                </div>

              </section>

              {largestHistoricalContributor && (
                <section className="mb-8 border border-white/10 bg-[#0c1118] p-6">

                  <div className="flex items-start gap-4">

                    <AlertTriangle
                      size={18}
                      className="mt-1 text-amber-400"
                    />

                    <div>

                      <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                        Largest Historical Loss Contributor
                      </div>

                      <div className="mt-2 text-lg font-semibold">
                        {
                          largestHistoricalContributor[0]
                        }
                      </div>

                      <p className="mt-1 text-xs leading-5 text-zinc-600">
                        Contributed{" "}
                        <span className="font-mono text-red-400">
                          {percent(
                            largestHistoricalContributor[1]
                              .contribution
                          )}
                        </span>{" "}
                        to the portfolio loss during
                        this historical event.
                      </p>

                    </div>

                  </div>

                </section>
              )}

              <section className="border border-white/10 bg-[#0c1118]">

                <div className="border-b border-white/10 p-6">

                  <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                    Historical Asset Performance
                  </div>

                  <div className="mt-1 text-xs text-zinc-700">
                    Actual asset returns and portfolio
                    contributions during the event.
                  </div>

                </div>

                <div className="overflow-x-auto">

                  <table className="w-full text-left">

                    <thead>
                      <tr className="border-b border-white/10 text-[9px] uppercase tracking-[0.15em] text-zinc-700">

                        <th className="px-6 py-4">
                          Asset
                        </th>

                        <th className="px-6 py-4">
                          Weight
                        </th>

                        <th className="px-6 py-4">
                          Historical Return
                        </th>

                        <th className="px-6 py-4">
                          Loss Contribution
                        </th>

                      </tr>
                    </thead>

                    <tbody>

                      {Object.entries(
                        historicalResult.asset_contributions
                      ).map(
                        ([
                          symbol,
                          data,
                        ]) => (
                          <tr
                            key={symbol}
                            className="border-b border-white/5 last:border-0"
                          >

                            <td className="px-6 py-5 font-mono text-xs text-zinc-300">
                              {symbol}
                            </td>

                            <td className="px-6 py-5 font-mono text-xs text-zinc-500">
                              {percent(
                                data.weight
                              )}
                            </td>

                            <td className="px-6 py-5 font-mono text-xs text-red-400">
                              {percent(
                                data.historical_return
                              )}
                            </td>

                            <td className="px-6 py-5">

                              <div className="flex items-center gap-4">

                                <div className="h-1.5 w-32 bg-zinc-900">

                                  <div
                                    className="h-1.5 bg-red-400"
                                    style={{
                                      width: `${Math.min(
                                        Math.abs(
                                          data.contribution
                                        ) * 100,
                                        100
                                      )}%`,
                                    }}
                                  />

                                </div>

                                <span className="font-mono text-xs text-red-400">
                                  {percent(
                                    data.contribution
                                  )}
                                </span>

                              </div>

                            </td>

                          </tr>
                        )
                      )}

                    </tbody>

                  </table>

                </div>

              </section>

              <div className="mt-8 flex justify-between">

                <button
                  onClick={() =>
                    (window.location.href =
                      "/risk")
                  }
                  className="flex items-center gap-2 border border-white/10 px-5 py-3 text-[10px] uppercase tracking-[0.18em] text-zinc-500 hover:text-zinc-200"
                >
                  <ArrowLeft size={13} />
                  Back to Risk
                </button>

                <button
                  onClick={() =>
                    (window.location.href =
                      "/dashboard")
                  }
                  className="flex items-center gap-2 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-black hover:bg-emerald-300"
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