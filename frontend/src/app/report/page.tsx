"use client";

import { useEffect, useState } from "react";
import Navigation from "@/components/Navigation";
import {
  ArrowLeft,
  FileText,
  Shield,
  TrendingDown,
  Activity,
  BarChart3,
} from "lucide-react";

interface PortfolioData {
  calculatedWeights?: Record<string, number>;
  asset_count?: number;
  total_weight?: number;
  riskTolerance?: string;
}

interface RiskMetrics {
  annualized_volatility: number;
  maximum_drawdown: number;
  sharpe_ratio: number;
  historical_var: number;
  expected_shortfall: number;
}

interface RiskAnalysis {
  metrics: RiskMetrics;
  risk_score: number;
  risk_category: string;
  risk_contribution: Record<string, number>;
}

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
  method: string;
  trading_days: number;
}

interface StressResult {
  scenario_name?: string;
  portfolio_impact: number;
  portfolio_value_after: number;
}

interface HistoricalStressResult {
  event_name?: string;
  portfolio_impact: number;
  portfolio_value_after: number;
}

interface MonteCarloStatistics {
  mean_return: number;
  median_return: number;
  probability_of_loss: number;
  probability_loss_gt_10: number;
  probability_loss_gt_20: number;
  value_at_risk: number;
  expected_shortfall: number;
  percentile_5: number;
  percentile_95: number;
  worst_return: number;
  best_return: number;
}

interface MonteCarloResult {
  horizon?: string;
  trading_days?: number;
  statistics: MonteCarloStatistics;
}

interface MonteCarloStoredData {
  selected_horizon?: string;
  results?: Record<string, MonteCarloResult>;
}

function percent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function number(value: number) {
  return value.toFixed(2);
}

export default function ReportPage() {
  const [portfolio, setPortfolio] =
    useState<PortfolioData | null>(null);

  const [risk, setRisk] =
    useState<RiskAnalysis | null>(null);

  const [optimization, setOptimization] =
    useState<OptimizationResult | null>(null);

  const [stress, setStress] =
    useState<StressResult | null>(null);

  const [historicalStress, setHistoricalStress] =
    useState<HistoricalStressResult | null>(null);

  const [monteCarlo, setMonteCarlo] =
    useState<MonteCarloResult | null>(null);

  const [monteCarloHorizon, setMonteCarloHorizon] =
    useState("");

  const [error, setError] = useState("");

  useEffect(() => {
    try {
      const storedPortfolio =
        sessionStorage.getItem(
          "portfolioiq-portfolio"
        );

      const storedRisk =
        sessionStorage.getItem(
          "portfolioiq-risk-analysis"
        );

      const storedOptimization =
        sessionStorage.getItem(
          "portfolioiq-optimization"
        );

      const storedStress =
        sessionStorage.getItem(
          "portfolioiq-stress-test"
        );

      const storedHistoricalStress =
        sessionStorage.getItem(
          "portfolioiq-historical-stress-test"
        );

      const storedMonteCarlo =
        sessionStorage.getItem(
          "portfolioiq-monte-carlo"
        );

      if (storedPortfolio) {
        setPortfolio(
          JSON.parse(storedPortfolio)
        );
      }

      if (storedRisk) {
        setRisk(
          JSON.parse(storedRisk)
        );
      }

      if (storedOptimization) {
        setOptimization(
          JSON.parse(storedOptimization)
        );
      }

      if (storedStress) {
        setStress(
          JSON.parse(storedStress)
        );
      }

      if (storedHistoricalStress) {
        setHistoricalStress(
          JSON.parse(storedHistoricalStress)
        );
      }

      if (storedMonteCarlo) {
        const parsed: MonteCarloStoredData =
          JSON.parse(storedMonteCarlo);

        const selected =
          parsed.selected_horizon;

        if (
          selected &&
          parsed.results?.[selected]
        ) {
          setMonteCarlo(
            parsed.results[selected]
          );

          setMonteCarloHorizon(
            selected
          );
        } else if (
          parsed.results
        ) {
          const first =
            Object.entries(
              parsed.results
            )[0];

          if (first) {
            setMonteCarloHorizon(
              first[0]
            );

            setMonteCarlo(
              first[1]
            );
          }
        }
      }
    } catch {
      setError(
        "Unable to load stored analysis results."
      );
    }
  }, []);

  const weights =
    portfolio?.calculatedWeights ?? {};

  return (
    <main className="min-h-screen bg-[#080b10] text-zinc-200">
      <Navigation />

      <div className="mx-auto max-w-7xl px-6 py-10">

        {/* Header */}
        <div className="mb-10 flex items-start justify-between">
          <div>
            <button
              type="button"
              onClick={() =>
                (window.location.href =
                  "/dashboard")
              }
              className="mb-6 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-zinc-600 transition hover:text-zinc-300"
            >
              <ArrowLeft size={13} />
              Back to Dashboard
            </button>

            <div className="flex items-center gap-3">
              <FileText
                size={18}
                className="text-emerald-400"
              />

              <div className="text-[10px] uppercase tracking-[0.3em] text-emerald-400">
                PortfolioIQ / Report
              </div>
            </div>

            <h1 className="mt-3 text-3xl font-semibold tracking-tight">
              Portfolio Risk Report
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-600">
              Consolidated quantitative analysis of
              portfolio risk, optimization, stress
              scenarios, and Monte Carlo simulation.
            </p>
          </div>

          <div className="hidden items-center gap-2 border border-white/10 bg-[#0c1118] px-4 py-3 md:flex">
            <Shield
              size={16}
              className="text-emerald-400"
            />

            <span className="text-[9px] uppercase tracking-[0.18em] text-zinc-600">
              Quantitative Report
            </span>
          </div>
        </div>

        {error && (
          <div className="mb-8 border border-red-400/20 bg-red-400/5 p-4 text-xs text-red-300">
            {error}
          </div>
        )}

        {/* Portfolio Summary */}
        <section className="mb-8">
          <div className="mb-4 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
            Portfolio Summary
          </div>

          <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">

            <div className="bg-[#0c1118] p-6">
              <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                Assets
              </div>

              <div className="mt-3 font-mono text-2xl">
                {portfolio?.asset_count ??
                  Object.keys(weights).length}
              </div>
            </div>

            <div className="bg-[#0c1118] p-6">
              <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                Risk Tolerance
              </div>

              <div className="mt-3 font-mono text-2xl text-emerald-400">
                {portfolio?.riskTolerance ??
                  "—"}
              </div>
            </div>

            <div className="bg-[#0c1118] p-6">
              <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                Allocation
              </div>

              <div className="mt-3 font-mono text-2xl">
                {portfolio?.total_weight != null
                  ? percent(
                      portfolio.total_weight
                    )
                  : "—"}
              </div>
            </div>
          </div>

          <div className="mt-4 border border-white/10 bg-[#0c1118] p-6">
            <div className="mb-5 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Portfolio Allocation
            </div>

            <div className="space-y-4">
              {Object.entries(weights).map(
                ([symbol, weight]) => (
                  <div key={symbol}>
                    <div className="mb-2 flex justify-between text-[10px]">
                      <span className="font-mono text-zinc-400">
                        {symbol}
                      </span>

                      <span className="font-mono text-zinc-600">
                        {percent(weight)}
                      </span>
                    </div>

                    <div className="h-1 bg-zinc-900">
                      <div
                        className="h-1 bg-emerald-400"
                        style={{
                          width: `${weight * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                )
              )}

              {Object.keys(weights).length === 0 && (
                <div className="text-xs text-zinc-700">
                  Portfolio data unavailable.
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Risk Analysis */}
        <section className="mb-8">
          <div className="mb-4 flex items-center gap-3">
            <Activity
              size={15}
              className="text-emerald-400"
            />

            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Risk Analysis
            </div>
          </div>

          {risk ? (
            <>
              <div className="mb-4 grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Risk Score
                  </div>

                  <div className="mt-2 font-mono text-3xl text-emerald-400">
                    {number(
                      risk.risk_score
                    )}
                  </div>

                  <div className="mt-2 text-[10px] uppercase tracking-wider text-zinc-600">
                    {risk.risk_category}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Volatility
                  </div>

                  <div className="mt-3 font-mono text-2xl">
                    {percent(
                      risk.metrics
                        .annualized_volatility
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Sharpe Ratio
                  </div>

                  <div className="mt-3 font-mono text-2xl">
                    {number(
                      risk.metrics.sharpe_ratio
                    )}
                  </div>
                </div>
              </div>

              <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Maximum Drawdown
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {percent(
                      risk.metrics.maximum_drawdown
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Historical VaR
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {percent(
                      risk.metrics.historical_var
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Expected Shortfall
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {percent(
                      risk.metrics.expected_shortfall
                    )}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="border border-white/10 bg-[#0c1118] p-6 text-xs text-zinc-700">
              Risk analysis has not been completed.
            </div>
          )}
        </section>

        {/* Optimization */}
        <section className="mb-8">
          <div className="mb-4 flex items-center gap-3">
            <BarChart3
              size={15}
              className="text-emerald-400"
            />

            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Portfolio Optimization
            </div>
          </div>

          {optimization ? (
            <>
              <div className="mb-4 border border-white/10 bg-[#0c1118] p-6">
                <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                  Optimization Method
                </div>

                <div className="mt-2 text-lg font-semibold">
                  {optimization.method.replaceAll(
                    "_",
                    " "
                  )}
                </div>

                <div className="mt-2 text-xs text-zinc-700">
                  Based on{" "}
                  {optimization.trading_days?.toLocaleString() ??
                    "historical"}{" "}
                  trading days of historical returns.
                </div>
              </div>

              <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-2">

                <div className="bg-[#0c1118] p-6">
                  <div className="mb-5 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                    Original Allocation
                  </div>

                  <div className="space-y-3">
                    {Object.entries(
                      optimization.original_weights
                    ).map(
                      ([symbol, value]) => (
                        <div
                          key={symbol}
                          className="flex justify-between font-mono text-xs"
                        >
                          <span className="text-zinc-400">
                            {symbol}
                          </span>

                          <span className="text-zinc-600">
                            {percent(value)}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="mb-5 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                    Optimized Allocation
                  </div>

                  <div className="space-y-3">
                    {Object.entries(
                      optimization.optimized_weights
                    ).map(
                      ([symbol, value]) => (
                        <div
                          key={symbol}
                          className="flex justify-between font-mono text-xs"
                        >
                          <span className="text-zinc-400">
                            {symbol}
                          </span>

                          <span className="text-emerald-400">
                            {percent(value)}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-4 grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Risk Before
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {number(
                      optimization.comparison
                        .before_risk_score
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Risk After
                  </div>

                  <div className="mt-3 font-mono text-xl text-emerald-400">
                    {number(
                      optimization.comparison
                        .after_risk_score
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Risk Change
                  </div>

                  <div className="mt-3 flex items-center gap-2 font-mono text-xl">
                    <TrendingDown
                      size={15}
                      className="text-emerald-400"
                    />

                    {(
                      optimization.comparison
                        .after_risk_score -
                      optimization.comparison
                        .before_risk_score
                    ).toFixed(2)}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="border border-white/10 bg-[#0c1118] p-6 text-xs text-zinc-700">
              Optimization has not been completed.
            </div>
          )}
        </section>

        {/* Stress Testing */}
        <section className="mb-8">
          <div className="mb-4 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
            Stress Testing
          </div>

          <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-2">

            <div className="bg-[#0c1118] p-6">
              <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                Hypothetical Scenario
              </div>

              {stress ? (
                <>
                  <div className="mt-2 text-sm font-semibold">
                    {stress.scenario_name ??
                      "Selected Scenario"}
                  </div>

                  <div className="mt-5 grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-[8px] uppercase text-zinc-700">
                        Portfolio Impact
                      </div>

                      <div className="mt-1 font-mono text-xl">
                        {percent(
                          stress.portfolio_impact
                        )}
                      </div>
                    </div>

                    <div>
                      <div className="text-[8px] uppercase text-zinc-700">
                        Value After
                      </div>

                      <div className="mt-1 font-mono text-xl">
                        {stress.portfolio_value_after.toLocaleString()}
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="mt-4 text-xs text-zinc-700">
                  Hypothetical stress test has not
                  been completed.
                </div>
              )}
            </div>

            <div className="bg-[#0c1118] p-6">
              <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                Historical Scenario
              </div>

              {historicalStress ? (
                <>
                  <div className="mt-2 text-sm font-semibold">
                    {historicalStress.event_name ??
                      "Historical Event"}
                  </div>

                  <div className="mt-5 grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-[8px] uppercase text-zinc-700">
                        Portfolio Impact
                      </div>

                      <div className="mt-1 font-mono text-xl">
                        {percent(
                          historicalStress.portfolio_impact
                        )}
                      </div>
                    </div>

                    <div>
                      <div className="text-[8px] uppercase text-zinc-700">
                        Value After
                      </div>

                      <div className="mt-1 font-mono text-xl">
                        {historicalStress.portfolio_value_after.toLocaleString()}
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="mt-4 text-xs text-zinc-700">
                  Historical stress test has not
                  been completed.
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Monte Carlo */}
        <section className="mb-10">
          <div className="mb-4 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
            Monte Carlo Simulation
          </div>

          {monteCarlo ? (
            <>
              <div className="mb-4 border border-white/10 bg-[#0c1118] p-6">
                <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                  Simulation Horizon
                </div>

                <div className="mt-2 text-lg font-semibold">
                  {monteCarloHorizon ||
                    monteCarlo.horizon ||
                    "Selected Horizon"}
                </div>

                {monteCarlo.trading_days && (
                  <div className="mt-2 text-xs text-zinc-700">
                    {monteCarlo.trading_days} trading days
                  </div>
                )}
              </div>

              <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Mean Return
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {percent(
                      monteCarlo.statistics.mean_return
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Median Return
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {percent(
                      monteCarlo.statistics.median_return
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Probability of Loss
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {percent(
                      monteCarlo.statistics
                        .probability_of_loss
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    VaR
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {percent(
                      monteCarlo.statistics
                        .value_at_risk
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    Expected Shortfall
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {percent(
                      monteCarlo.statistics
                        .expected_shortfall
                    )}
                  </div>
                </div>

                <div className="bg-[#0c1118] p-6">
                  <div className="text-[9px] uppercase tracking-[0.15em] text-zinc-600">
                    5th Percentile
                  </div>

                  <div className="mt-3 font-mono text-xl">
                    {percent(
                      monteCarlo.statistics
                        .percentile_5
                    )}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="border border-white/10 bg-[#0c1118] p-6 text-xs text-zinc-700">
              Monte Carlo simulation has not been
              completed.
            </div>
          )}
        </section>

        {/* Disclaimer */}
        <section className="mb-8 border border-white/10 bg-[#0c1118] p-6">
          <div className="text-[9px] uppercase tracking-[0.2em] text-zinc-600">
            Quantitative Decision Support
          </div>

          <p className="mt-3 max-w-4xl text-xs leading-6 text-zinc-600">
            This report summarizes quantitative portfolio
            analysis based on historical market data,
            optimization models, stress scenarios, and
            historical bootstrap simulation. The results
            are intended for analytical decision support and
            do not constitute a guaranteed forecast or
            automated investment recommendation.
          </p>
        </section>

        {/* Footer */}
        <div className="flex flex-wrap justify-between gap-3">
          <button
            type="button"
            onClick={() =>
              (window.location.href =
                "/dashboard")
            }
            className="flex items-center gap-2 border border-white/10 px-5 py-3 text-[10px] uppercase tracking-[0.18em] text-zinc-500 transition hover:text-zinc-200"
          >
            <ArrowLeft size={13} />
            Dashboard
          </button>

          <button
            type="button"
            onClick={() =>
              window.print()
            }
            className="flex items-center gap-2 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-black transition hover:bg-emerald-300"
          >
            Print Report
          </button>
        </div>

      </div>
    </main>
  );
}