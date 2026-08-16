"use client";

import { useEffect, useState } from "react";

import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  BarChart3,
  ShieldAlert,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

interface RiskMetrics {
  annualized_volatility: number;
  maximum_drawdown: number;
  sharpe_ratio: number;
  historical_var: number;
  expected_shortfall: number;
}

interface RiskAnalysis {
  weights: Record<string, number>;
  metrics: RiskMetrics;

  risk_score: number;
  risk_category: string;

  risk_contribution: Record<string, number>;

  compatibility: {
    recommendation: string;
    risk_score: number;
    risk_tolerance: string;
    maximum_drawdown: number;
    maximum_acceptable_loss: number;
    investment_horizon_years: number;
    reasons: string[];
  };

  recommendations: string[];

  confidence_level: number;
  risk_free_rate: number;
  trading_days: number;
}

export default function RiskPage() {
  const [riskAnalysis, setRiskAnalysis] =
    useState<RiskAnalysis | null>(null);

  const [error, setError] = useState("");

  useEffect(() => {
    loadRiskAnalysis();
  }, []);

  const loadRiskAnalysis = () => {
    try {
      const storedRisk =
        sessionStorage.getItem(
          "portfolioiq-risk-analysis"
        );

      if (!storedRisk) {
        setError(
          "Risk analysis is not available. Please complete the portfolio analysis first."
        );
        return;
      }

      const parsedRisk: RiskAnalysis =
        JSON.parse(storedRisk);

      setRiskAnalysis(parsedRisk);
    } catch {
      setError(
        "Unable to load the stored risk analysis."
      );
    }
  };

  if (error) {
    return (
      <main className="min-h-screen bg-[#080b10] text-zinc-100">
        <header className="border-b border-white/10">
          <div className="mx-auto flex h-16 max-w-7xl items-center px-6 lg:px-10">
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
          </div>
        </header>

        <section className="mx-auto flex min-h-[70vh] max-w-7xl items-center justify-center px-6">
          <div className="max-w-lg border border-red-400/20 bg-red-400/[0.03] p-8 text-center">
            <AlertTriangle
              size={28}
              className="mx-auto text-red-400"
            />

            <h1 className="mt-5 text-xl font-medium">
              Risk Analysis Unavailable
            </h1>

            <p className="mt-3 text-sm leading-6 text-zinc-500">
              {error}
            </p>

            <button
              type="button"
              onClick={() => {
                window.location.href =
                  "/dashboard";
              }}
              className="mt-6 inline-flex items-center gap-2 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#06100c]"
            >
              Return to Dashboard
              <ArrowLeft size={14} />
            </button>
          </div>
        </section>
      </main>
    );
  }

  if (!riskAnalysis) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#080b10] text-zinc-100">
        <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-500">
          Loading Risk Analysis
        </div>
      </main>
    );
  }

  const {
    metrics,
    risk_score,
    risk_category,
    risk_contribution,
    compatibility,
    recommendations,
    confidence_level,
    risk_free_rate,
    trading_days,
  } = riskAnalysis;

  const riskScoreClass =
    risk_category === "VERY HIGH"
      ? "border-red-400/30 bg-red-400/5 text-red-400"
      : risk_category === "HIGH"
      ? "border-orange-400/30 bg-orange-400/5 text-orange-400"
      : risk_category === "MODERATE"
      ? "border-amber-400/30 bg-amber-400/5 text-amber-400"
      : risk_category === "LOW"
      ? "border-emerald-400/30 bg-emerald-400/5 text-emerald-400"
      : "border-zinc-400/30 bg-zinc-400/5 text-zinc-400";

  const riskContributions = Object.entries(
    risk_contribution
  )
    .map(([symbol, contribution]) => ({
      symbol,
      contribution:
        Number(contribution) * 100,
    }))
    .sort(
      (a, b) =>
        b.contribution - a.contribution
    );

  const largestContributor =
    riskContributions[0];

  const compatibilityClass =
    compatibility.recommendation ===
    "SUITABLE"
      ? "text-emerald-400"
      : compatibility.recommendation ===
        "REVIEW"
      ? "text-amber-400"
      : "text-red-400";

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

          <div className="text-right">
            <div className="text-[9px] uppercase tracking-[0.18em] text-zinc-600">
              Risk Classification
            </div>

            <div
              className={`mt-2 inline-flex items-center gap-2 border px-3 py-2 text-[10px] uppercase tracking-[0.18em] ${riskScoreClass}`}
            >
              <ShieldAlert size={13} />
              {risk_category}
            </div>
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
          ].map(
            ([number, label, route]) => {
              const active = number === "04";

              return (
                <button
                  type="button"
                  key={number}
                  onClick={() => {
                    window.location.href =
                      route;
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
            }
          )}
        </div>
      </div>

      {/* Main */}
      <section className="mx-auto max-w-7xl px-6 py-10 lg:px-10 lg:py-14">
        {/* Heading */}
        <div className="mb-8">
          <div className="mb-4 flex items-center gap-2 text-[10px] uppercase tracking-[0.25em] text-emerald-400">
            <BarChart3 size={14} />
            Quantitative Analysis
          </div>

          <h1 className="text-4xl font-semibold tracking-tight">
            Risk Analysis
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-500">
            Detailed analysis of portfolio risk based on
            historical market returns, portfolio
            characteristics, and investor constraints.
          </p>
        </div>

        {/* Risk Score */}
        <div className="grid gap-px border border-white/10 bg-white/10 lg:grid-cols-[1fr_2fr]">
          <div className="bg-[#0c1118] p-7">
            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Overall Risk Score
            </div>

            <div className="mt-6 flex items-end gap-3">
              <span className="font-mono text-6xl font-medium tracking-tight">
                {risk_score.toFixed(2)}
              </span>

              <span className="mb-2 font-mono text-sm text-zinc-600">
                / 100
              </span>
            </div>

            <div
              className={`mt-4 inline-flex items-center gap-2 border px-3 py-2 text-[10px] uppercase tracking-[0.18em] ${riskScoreClass}`}
            >
              <ShieldAlert size={13} />
              {risk_category}
            </div>
          </div>

          <div className="bg-[#0c1118] p-7">
            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Risk Interpretation
            </div>

            <div className="mt-5 grid gap-6 sm:grid-cols-3">
              <InfoBlock
                label="Confidence Level"
                value={`${(
                  confidence_level * 100
                ).toFixed(0)}%`}
              />

              <InfoBlock
                label="Risk-Free Rate"
                value={`${(
                  risk_free_rate * 100
                ).toFixed(2)}%`}
              />

              <InfoBlock
                label="Trading Days"
                value={trading_days.toLocaleString()}
              />
            </div>

            <p className="mt-6 max-w-2xl text-sm leading-6 text-zinc-500">
              The overall risk score combines portfolio
              volatility, drawdown, Value at Risk,
              Expected Shortfall, and historical
              risk-adjusted performance.
            </p>
          </div>
        </div>

        {/* Metrics */}
        <div className="mt-8">
          <div className="mb-4 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
            Quantitative Risk Metrics
          </div>

          <div className="grid gap-px border border-white/10 bg-white/10 sm:grid-cols-2 lg:grid-cols-5">
            <MetricCard
              label="Annualized Volatility"
              value={`${(
                metrics.annualized_volatility *
                100
              ).toFixed(2)}%`}
              description="Annualized variability of portfolio returns."
            />

            <MetricCard
              label="Maximum Drawdown"
              value={`${(
                metrics.maximum_drawdown *
                100
              ).toFixed(2)}%`}
              description="Largest historical decline from a portfolio peak."
            />

            <MetricCard
              label="Sharpe Ratio"
              value={metrics.sharpe_ratio.toFixed(
                3
              )}
              description="Historical risk-adjusted return."
            />

            <MetricCard
              label="Historical VaR"
              value={`${(
                metrics.historical_var *
                100
              ).toFixed(2)}%`}
              description={`${(
                confidence_level * 100
              ).toFixed(
                0
              )}% historical loss threshold.`}
            />

            <MetricCard
              label="Expected Shortfall"
              value={`${(
                metrics.expected_shortfall *
                100
              ).toFixed(2)}%`}
              description="Average return beyond the VaR threshold."
            />
          </div>
        </div>

        {/* Risk Contribution */}
        <div className="mt-8 border border-white/10 bg-[#0c1118] p-7">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                Asset-Level Risk Contribution
              </div>

              <p className="mt-2 text-xs text-zinc-700">
                Relative contribution of each asset to
                total portfolio variance.
              </p>
            </div>

            <TrendingUp
              size={18}
              className="text-zinc-600"
            />
          </div>

          <div className="mt-8 space-y-6">
            {riskContributions.map(
              (item, index) => (
                <div key={item.symbol}>
                  <div className="mb-2 flex justify-between text-[10px]">
                    <span className="font-mono text-zinc-400">
                      {item.symbol}
                    </span>

                    <span className="font-mono text-zinc-500">
                      {item.contribution.toFixed(
                        2
                      )}
                      %
                    </span>
                  </div>

                  <div className="h-2 bg-zinc-900">
                    <div
                      className={`h-2 ${
                        index === 0
                          ? "bg-amber-400"
                          : "bg-zinc-500"
                      }`}
                      style={{
                        width: `${Math.min(
                          item.contribution,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              )
            )}
          </div>

          {largestContributor && (
            <div className="mt-8 border-t border-white/10 pt-6">
              <div className="flex items-start gap-3">
                <TrendingDown
                  size={16}
                  className="mt-0.5 text-amber-400"
                />

                <p className="text-sm leading-6 text-zinc-500">
                  <span className="font-mono text-zinc-300">
                    {largestContributor.symbol}
                  </span>{" "}
                  is currently the largest contributor
                  to portfolio risk at approximately{" "}
                  <span className="font-mono text-amber-400">
                    {largestContributor.contribution.toFixed(
                      1
                    )}
                    %
                  </span>
                  .
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Compatibility */}
        <div className="mt-8 grid gap-px border border-white/10 bg-white/10 lg:grid-cols-2">
          <div className="bg-[#0c1118] p-7">
            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Investor Compatibility
            </div>

            <div
              className={`mt-5 text-2xl font-medium ${compatibilityClass}`}
            >
              {compatibility.recommendation}
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <InfoBlock
                label="Risk Tolerance"
                value={
                  compatibility.risk_tolerance
                }
              />

              <InfoBlock
                label="Investment Horizon"
                value={`${compatibility.investment_horizon_years} years`}
              />

              <InfoBlock
                label="Maximum Acceptable Loss"
                value={`${(
                  compatibility.maximum_acceptable_loss *
                  100
                ).toFixed(1)}%`}
              />

              <InfoBlock
                label="Historical Drawdown"
                value={`${Math.abs(
                  compatibility.maximum_drawdown *
                    100
                ).toFixed(2)}%`}
              />
            </div>
          </div>

          <div className="bg-[#0c1118] p-7">
            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Assessment Reasons
            </div>

            <div className="mt-5 space-y-4">
              {compatibility.reasons.map(
                (reason, index) => (
                  <div
                    key={index}
                    className="flex gap-3"
                  >
                    <AlertTriangle
                      size={15}
                      className="mt-1 shrink-0 text-amber-400"
                    />

                    <p className="text-sm leading-6 text-zinc-500">
                      {reason}
                    </p>
                  </div>
                )
              )}
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="mt-8 border border-amber-400/20 bg-amber-400/[0.03] p-7">
          <div className="flex items-start gap-4">
            <TrendingDown
              size={20}
              className="mt-1 shrink-0 text-amber-400"
            />

            <div className="w-full">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-400">
                Recommended Actions
              </div>

              <div className="mt-5 space-y-4">
                {recommendations.length > 0 ? (
                  recommendations.map(
                    (recommendation, index) => (
                      <div
                        key={index}
                        className="flex gap-3 text-sm leading-6 text-zinc-500"
                      >
                        <span className="font-mono text-amber-400">
                          {String(
                            index + 1
                          ).padStart(2, "0")}
                        </span>

                        <span>
                          {recommendation}
                        </span>
                      </div>
                    )
                  )
                ) : (
                  <p className="text-sm text-zinc-500">
                    No specific risk-reduction
                    recommendations were generated.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 flex flex-col justify-between gap-4 sm:flex-row">
          <button
            type="button"
            onClick={() => {
              window.location.href =
                "/dashboard";
            }}
            className="flex items-center justify-center gap-2 border border-white/10 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-zinc-400 hover:bg-white/5 hover:text-zinc-100"
          >
            <ArrowLeft size={14} />
            Back to Dashboard
          </button>

          <button
            type="button"
            onClick={() => {
              window.location.href =
                "/optimize";
            }}
            className="flex items-center justify-center gap-2 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#06100c] hover:bg-emerald-300"
          >
            Continue to Optimization
            <ArrowRight size={14} />
          </button>
        </div>
      </section>
    </main>
  );
}

function MetricCard({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description: string;
}) {
  return (
    <div className="bg-[#0c1118] p-5">
      <div className="text-[9px] uppercase tracking-[0.14em] text-zinc-600">
        {label}
      </div>

      <div className="mt-4 font-mono text-2xl">
        {value}
      </div>

      <p className="mt-3 text-[10px] leading-5 text-zinc-700">
        {description}
      </p>
    </div>
  );
}

function InfoBlock({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="border border-white/10 bg-[#0a0e14] p-4">
      <div className="text-[9px] uppercase tracking-[0.14em] text-zinc-600">
        {label}
      </div>

      <div className="mt-2 font-mono text-sm text-zinc-300">
        {value}
      </div>
    </div>
  );
}