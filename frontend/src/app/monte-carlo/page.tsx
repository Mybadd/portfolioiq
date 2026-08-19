"use client";

import { useEffect, useMemo, useState } from "react";
import Navigation from "@/components/Navigation";
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

const HORIZONS = ["1M", "3M", "6M", "1Y", "2Y"] as const;

type Horizon = (typeof HORIZONS)[number];

interface HistogramBin {
  lower: number;
  upper: number;
  count: number;
}

interface SimulationStatistics {
  mean_return: number;
  median_return: number;
  percentile_5: number;
  percentile_95: number;
  probability_of_loss: number;
  probability_loss_10: number;
  probability_loss_20: number;
  var: number;
  expected_shortfall: number;
  worst_return: number;
  best_return: number;
}

interface HorizonResult {
  method: string;
  simulations: number;
  horizon_days: number;
  confidence_level: number;
  historical_observations: number;
  statistics: SimulationStatistics;
  histogram: HistogramBin[];
}

interface MonteCarloResponse {
  portfolio_weights: Record<string, number>;
  method: string;
  simulations: number;
  confidence_level: number;
  horizons: Record<Horizon, HorizonResult>;
}
interface StoredPortfolio {
  calculatedWeights?: Record<string, number>;
}
function formatPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

function formatNumber(value: number): string {
  return value.toLocaleString();
}

export default function MonteCarloPage() {
  const [data, setData] =
    useState<MonteCarloResponse | null>(null);

  const [selectedHorizon, setSelectedHorizon] =
    useState<Horizon>("1M");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
  async function loadSimulation() {
    try {
      setLoading(true);
      setError(null);

      const storedPortfolio =
        sessionStorage.getItem("portfolioiq-portfolio");

      if (!storedPortfolio) {
        throw new Error(
          "No portfolio found. Please create a portfolio first."
        );
      }

      const portfolio =
        JSON.parse(storedPortfolio) as StoredPortfolio;

      if (
        !portfolio.calculatedWeights ||
        Object.keys(portfolio.calculatedWeights).length === 0
      ) {
        throw new Error(
          "Portfolio weights are unavailable. Please recreate your portfolio."
        );
      }

      const response = await fetch(
        `${API_BASE_URL}/api/monte-carlo/simulate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            weights: portfolio.calculatedWeights,
            simulations: 10000,
            confidence_level: 0.95,
            random_seed: 42,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail ||
            "Monte Carlo simulation failed."
        );
      }

      const result =
        (await response.json()) as MonteCarloResponse;

      setData(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load Monte Carlo simulation."
      );
    } finally {
      setLoading(false);
    }
  }

  loadSimulation();
}, []);

  const selectedResult = useMemo(() => {
    if (!data) {
      return null;
    }

    return data.horizons[selectedHorizon];
  }, [data, selectedHorizon]);

  const maxHistogramCount = useMemo(() => {
    if (!selectedResult) {
      return 1;
    }

    return Math.max(
      ...selectedResult.histogram.map(
        (bin) => bin.count
      ),
      1
    );
  }, [selectedResult]);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <p className="text-slate-400">
              Running Monte Carlo simulations...
            </p>
            <p className="mt-2 text-sm text-slate-500">
              Calculating 1M, 3M, 6M, 1Y and 2Y horizons.
            </p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-slate-950 text-white">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="rounded-2xl border border-red-900/50 bg-red-950/30 p-8">
            <h1 className="text-xl font-semibold">
              Monte Carlo Simulation
            </h1>

            <p className="mt-3 text-red-300">
              {error}
            </p>
          </div>
        </div>
      </main>
    );
  }

  if (!data || !selectedResult) {
    return (
      <main className="min-h-screen bg-slate-950 text-white">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <p className="text-slate-400">
              No simulation data available.
            </p>
          </div>
        </div>
      </main>
    );
  }

  const statistics =
    selectedResult.statistics;

  return (
  <main className="min-h-screen bg-slate-950 text-white">
    <Navigation />

    <div className="mx-auto max-w-7xl px-6 py-10">

        {/* Header */}
        <div className="mb-8">
          <p className="text-sm font-medium uppercase tracking-wider text-emerald-400">
            PortfolioIQ
          </p>

          <h1 className="mt-2 text-3xl font-bold">
            Monte Carlo Simulation
          </h1>

          <p className="mt-2 max-w-3xl text-slate-400">
            Historical bootstrap simulation for
            forward-looking portfolio return and
            tail-risk analysis.
          </p>
        </div>

        {/* Configuration */}
        <section className="mb-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">

          <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">

            <div>
              <label
                htmlFor="horizon"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Simulation Horizon
              </label>

              <select
                id="horizon"
                value={selectedHorizon}
                onChange={(event) =>
                  setSelectedHorizon(
                    event.target.value as Horizon
                  )
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-emerald-500 md:w-56"
              >
                {HORIZONS.map((horizon) => (
                  <option
                    key={horizon}
                    value={horizon}
                  >
                    {horizon}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">

              <div>
                <p className="text-slate-500">
                  Method
                </p>
                <p className="mt-1 font-medium text-slate-200">
                  Historical Bootstrap
                </p>
              </div>

              <div>
                <p className="text-slate-500">
                  Horizon
                </p>
                <p className="mt-1 font-medium text-slate-200">
                  {selectedResult.horizon_days} trading days
                </p>
              </div>

              <div>
                <p className="text-slate-500">
                  Simulations
                </p>
                <p className="mt-1 font-medium text-slate-200">
                  {formatNumber(
                    selectedResult.simulations
                  )}
                </p>
              </div>

              <div>
                <p className="text-slate-500">
                  Historical Data
                </p>
                <p className="mt-1 font-medium text-slate-200">
                  {formatNumber(
                    selectedResult.historical_observations
                  )} days
                </p>
              </div>

            </div>
          </div>
        </section>

        {/* Metric cards */}
        <section className="grid gap-4 md:grid-cols-3">

          <MetricCard
            title="Mean Return"
            value={formatPercent(
              statistics.mean_return
            )}
          />

          <MetricCard
            title="Median Return"
            value={formatPercent(
              statistics.median_return
            )}
          />

          <MetricCard
            title="Probability of Loss"
            value={formatPercent(
              statistics.probability_of_loss
            )}
          />

          <MetricCard
            title="VaR (95%)"
            value={formatPercent(
              statistics.var
            )}
            negative
          />

          <MetricCard
            title="Expected Shortfall (95%)"
            value={formatPercent(
              statistics.expected_shortfall
            )}
            negative
          />

        </section>

        {/* Distribution */}
        <section className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">

          <div className="mb-6">
            <h2 className="text-xl font-semibold">
              Simulated Return Distribution
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Distribution of simulated portfolio
              returns over the selected horizon.
            </p>
          </div>

          <div className="overflow-x-auto">
            <div className="flex h-80 min-w-[900px] items-end gap-[2px] rounded-lg border border-slate-800 bg-slate-950 px-4 pb-10 pt-6">

              {selectedResult.histogram.map(
                (bin, index) => {
                  const height =
                    (bin.count /
                      maxHistogramCount) *
                    100;

                  return (
                    <div
                      key={`${bin.lower}-${index}`}
                      className="group relative flex h-full flex-1 items-end"
                    >
                      <div
                        className="w-full rounded-t-sm bg-emerald-500/70 transition hover:bg-emerald-400"
                        style={{
                          height: `${Math.max(
                            height,
                            bin.count > 0
                              ? 1
                              : 0
                          )}%`,
                        }}
                        title={`${formatPercent(
                          bin.lower
                        )} to ${formatPercent(
                          bin.upper
                        )}: ${formatNumber(
                          bin.count
                        )} simulations`}
                      />
                    </div>
                  );
                }
              )}

            </div>
          </div>

          <div className="mt-4 flex justify-between text-xs text-slate-500">
            <span>
              {formatPercent(
                selectedResult.histogram[0]?.lower ??
                  0
              )}
            </span>

            <span>
              Return
            </span>

            <span>
              {formatPercent(
                selectedResult.histogram[
                  selectedResult.histogram.length - 1
                ]?.upper ?? 0
              )}
            </span>
          </div>

        </section>

        {/* Portfolio */}
        <section className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">

          <h2 className="mb-4 text-xl font-semibold">
            Portfolio Weights
          </h2>

          <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-5">

            {Object.entries(
              data.portfolio_weights
            ).map(([symbol, weight]) => (
              <div
                key={symbol}
                className="rounded-lg border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-sm text-slate-500">
                  {symbol}
                </p>

                <p className="mt-1 text-lg font-semibold text-white">
                  {formatPercent(weight)}
                </p>
              </div>
            ))}

          </div>

        </section>

      </div>
    </main>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  negative?: boolean;
}

function MetricCard({
  title,
  value,
  negative = false,
}: MetricCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

      <p className="text-sm text-slate-500">
        {title}
      </p>

      <p
        className={`mt-2 text-2xl font-bold ${
          negative
            ? "text-red-400"
            : "text-emerald-400"
        }`}
      >
        {value}
      </p>

    </div>
  );
}