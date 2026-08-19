"use client";

import { useEffect, useState } from "react";
import Navigation from "@/components/Navigation";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  ChevronRight,
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

interface PortfolioData {
  inputMode?: string;
  holdings?: unknown[];
  calculatedWeights?: Record<string, number>;
  assetCount?: number;
  totalWeight?: number;
}

interface InvestorProfile {
  investmentAmount?: number;
  investmentHorizonYears?: number;
  riskTolerance?: string;
  maximumAcceptableLoss?: number;
  maxAcceptableLoss?: number;
  investmentObjective?: string;
}

interface MetricDisplay {
  label: string;
  value: string;
  status: string;
}

export default function DashboardPage() {
  const [investmentAmount, setInvestmentAmount] = useState(0);
  const [investmentHorizon, setInvestmentHorizon] = useState(0);
  const [riskTolerance, setRiskTolerance] = useState("");
  const [objective, setObjective] = useState("");
  const [maximumAcceptableLoss, setMaximumAcceptableLoss] =
    useState(20);

  const [portfolio, setPortfolio] =
    useState<PortfolioData | null>(null);

  const [riskAnalysis, setRiskAnalysis] =
    useState<RiskAnalysis | null>(null);

  const [loading, setLoading] = useState(true);
  const [riskLoading, setRiskLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    setError("");

    try {
      /*
       * ------------------------------------------------------
       * 1. Load investor profile
       * ------------------------------------------------------
       */

      const storedProfile = sessionStorage.getItem(
        "portfolioiq-investor-profile"
      );

      if (!storedProfile) {
        window.location.href = "/";
        return;
      }

      const profile: InvestorProfile =
        JSON.parse(storedProfile);

      setInvestmentAmount(
        Number(profile.investmentAmount ?? 0)
      );

      setInvestmentHorizon(
        Number(profile.investmentHorizonYears ?? 0)
      );

      setRiskTolerance(
        profile.riskTolerance ?? ""
      );

      setObjective(
        profile.investmentObjective ?? ""
      );

      const acceptableLoss =
        profile.maximumAcceptableLoss ??
        profile.maxAcceptableLoss ??
        20;

      setMaximumAcceptableLoss(
        Number(acceptableLoss)
      );

      /*
       * ------------------------------------------------------
       * 2. Load portfolio
       * ------------------------------------------------------
       */

      const storedPortfolio = sessionStorage.getItem(
        "portfolioiq-portfolio"
      );

      if (!storedPortfolio) {
        window.location.href = "/portfolio";
        return;
      }

      const portfolioData: PortfolioData =
        JSON.parse(storedPortfolio);

      setPortfolio(portfolioData);

      /*
       * ------------------------------------------------------
       * 3. Check whether a previous risk result exists
       * ------------------------------------------------------
       */

      const storedRiskAnalysis =
        sessionStorage.getItem(
          "portfolioiq-risk-analysis"
        );

      if (storedRiskAnalysis) {
        try {
          const parsedRisk: RiskAnalysis =
            JSON.parse(storedRiskAnalysis);

          setRiskAnalysis(parsedRisk);
        } catch {
          sessionStorage.removeItem(
            "portfolioiq-risk-analysis"
          );
        }
      }

      /*
       * ------------------------------------------------------
       * 4. Calculate fresh risk analysis
       * ------------------------------------------------------
       */

      const weights =
        portfolioData.calculatedWeights ?? {};

      if (Object.keys(weights).length === 0) {
        setError(
          "Portfolio weights are unavailable. Please return to the Portfolio page."
        );
        setLoading(false);
        return;
      }

      setRiskLoading(true);

      /*
       * Backend expects maximum_acceptable_loss
       * as a decimal:
       *
       * 20% -> 0.20
       * 30% -> 0.30
       */
      const acceptableLossDecimal =
        Number(acceptableLoss) / 100;

      const response = await fetch(
        "http://127.0.0.1:8000/api/risk/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            weights,
            risk_free_rate: 0.0,
            confidence_level: 0.95,

            investor_profile: {
              investment_amount:
                Number(profile.investmentAmount ?? 0),

              investment_horizon_years:
                Number(
                  profile.investmentHorizonYears ?? 0
                ),

              risk_tolerance:
                profile.riskTolerance ?? "",

              maximum_acceptable_loss:
                acceptableLossDecimal,

              investment_objective:
                profile.investmentObjective ?? "",
            },
          }),
        }
      );

      if (!response.ok) {
        let message =
          "Unable to calculate portfolio risk.";

        try {
          const errorData = await response.json();

          if (errorData.detail) {
            message = errorData.detail;
          }
        } catch {
          // Keep default error message.
        }

        throw new Error(message);
      }

      const result: RiskAnalysis =
        await response.json();

      setRiskAnalysis(result);

      sessionStorage.setItem(
        "portfolioiq-risk-analysis",
        JSON.stringify(result)
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load portfolio risk analysis."
      );
    } finally {
      setRiskLoading(false);
      setLoading(false);
    }
  };

  /*
   * --------------------------------------------------------
   * Loading state
   * --------------------------------------------------------
   */

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#080b10] text-zinc-100">
        <div className="text-center">
          <div className="mx-auto h-2 w-2 animate-pulse rounded-full bg-emerald-400" />

          <div className="mt-4 text-[10px] uppercase tracking-[0.2em] text-zinc-500">
            Loading Portfolio Analysis
          </div>
        </div>
      </main>
    );
  }

  const calculatedWeights =
    portfolio?.calculatedWeights ?? {};

  const metrics = riskAnalysis
    ? buildMetrics(riskAnalysis.metrics)
    : [];

  const riskContributions =
    riskAnalysis
      ? Object.entries(
          riskAnalysis.risk_contribution
        )
          .map(([symbol, value]) => ({
            symbol,
            value: Number(value) * 100,
          }))
          .sort((a, b) => b.value - a.value)
      : [];

  const largestRiskContributor =
    riskContributions[0];

  /*
   * --------------------------------------------------------
   * Backend risk score
   * --------------------------------------------------------
   */

  const riskScore =
    riskAnalysis?.risk_score ?? 0;

  const riskLevel =
    riskAnalysis?.risk_category ?? "UNKNOWN";

  /*
   * --------------------------------------------------------
   * Backend investor compatibility
   * --------------------------------------------------------
   */

  const compatibility =
    riskAnalysis?.compatibility;

  const compatibilityStatus =
    compatibility?.recommendation ?? "UNKNOWN";

  /*
   * Determine whether the backend assessment says that
   * the maximum acceptable loss has been exceeded.
   */

  const drawdownExceedsTolerance =
    compatibility
      ? Math.abs(
          compatibility.maximum_drawdown
        ) >
        compatibility.maximum_acceptable_loss
      : false;

  const portfolioStatus =
    compatibilityStatus === "SUITABLE"
      ? "Within Tolerance"
      : compatibilityStatus === "REVIEW"
      ? "Review Required"
      : compatibilityStatus === "NOT SUITABLE"
      ? "Not Suitable"
      : "Analysis Pending";

  /*
   * --------------------------------------------------------
   * Risk score styling
   * --------------------------------------------------------
   */

  const riskScoreClass =
    riskLevel === "VERY HIGH"
      ? "border-red-400/30 bg-red-400/5 text-red-400"
      : riskLevel === "HIGH"
      ? "border-orange-400/30 bg-orange-400/5 text-orange-400"
      : riskLevel === "MODERATE"
      ? "border-amber-400/30 bg-amber-400/5 text-amber-400"
      : riskLevel === "LOW"
      ? "border-emerald-400/30 bg-emerald-400/5 text-emerald-400"
      : "border-zinc-400/30 bg-zinc-400/5 text-zinc-400";

  /*
   * --------------------------------------------------------
   * Display values
   * --------------------------------------------------------
   */

  const drawdown =
    Math.abs(
      riskAnalysis?.metrics.maximum_drawdown ?? 0
    ) * 100;

  const acceptableLoss =
    compatibility
      ? compatibility.maximum_acceptable_loss * 100
      : maximumAcceptableLoss;

  const recommendations =
    riskAnalysis?.recommendations ?? [];

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
              {riskLevel}
            </div>
          </div>
        </div>
      </header>

      <Navigation />

      {/* Main */}
      <section className="mx-auto max-w-7xl px-6 py-10 lg:px-10 lg:py-14">
        {/* Heading */}
        <div className="mb-8 flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div>
            <div className="mb-4 flex items-center gap-2 text-[10px] uppercase tracking-[0.25em] text-emerald-400">
              <BarChart3 size={14} />
              Portfolio Overview
            </div>

            <h1 className="text-4xl font-semibold tracking-tight">
              Risk Dashboard
            </h1>

            <p className="mt-3 max-w-xl text-sm leading-6 text-zinc-500">
              A quantitative overview of your portfolio&apos;s
              risk, performance characteristics, and investor
              compatibility.
            </p>
          </div>

          <div className="border border-white/10 bg-[#0c1118] px-5 py-4">
            <div className="text-[9px] uppercase tracking-[0.18em] text-zinc-600">
              Portfolio Status
            </div>

            <div className="mt-2 flex items-center gap-2 text-sm">
              <span
                className={`h-2 w-2 rounded-full ${
                  compatibilityStatus === "SUITABLE"
                    ? "bg-emerald-400"
                    : compatibilityStatus ===
                      "REVIEW"
                    ? "bg-amber-400"
                    : compatibilityStatus ===
                      "NOT SUITABLE"
                    ? "bg-red-400"
                    : "bg-zinc-600"
                }`}
              />

              {portfolioStatus}
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-8 border border-red-500/30 bg-red-500/5 px-5 py-4 text-xs leading-5 text-red-400">
            {error}
          </div>
        )}

        {/* Risk score */}
        <div className="grid gap-px border border-white/10 bg-white/10 lg:grid-cols-[1fr_2fr]">
          <div className="bg-[#0c1118] p-7">
            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Overall Risk Score
            </div>

            <div className="mt-6 flex items-end gap-3">
              <span className="font-mono text-6xl font-medium tracking-tight">
                {riskScore.toFixed(2)}
              </span>

              <span className="mb-2 font-mono text-sm text-zinc-600">
                / 100
              </span>
            </div>

            <div
              className={`mt-4 inline-flex items-center gap-2 border px-3 py-2 text-[10px] uppercase tracking-[0.18em] ${riskScoreClass}`}
            >
              <ShieldAlert size={13} />
              {riskLevel}
            </div>
          </div>

          {/* Investor compatibility */}
          <div className="bg-[#0c1118] p-7">
            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Investor Compatibility
            </div>

            <div className="mt-5 flex items-start gap-4">
              {compatibilityStatus ===
              "NOT SUITABLE" ? (
                <AlertTriangle
                  size={22}
                  className="mt-1 shrink-0 text-red-400"
                />
              ) : compatibilityStatus ===
                "REVIEW" ? (
                <AlertTriangle
                  size={22}
                  className="mt-1 shrink-0 text-amber-400"
                />
              ) : (
                <ShieldAlert
                  size={22}
                  className="mt-1 shrink-0 text-emerald-400"
                />
              )}

              <div>
                <div className="text-lg font-medium">
                  {compatibilityStatus}
                </div>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
                  {compatibility?.reasons?.length ? (
                    compatibility.reasons.map(
                      (reason, index) => (
                        <span
                          key={index}
                          className="block"
                        >
                          {reason}
                        </span>
                      )
                    )
                  ) : riskAnalysis ? (
                    "Portfolio risk characteristics are consistent with the investor profile."
                  ) : (
                    "Risk analysis is not available."
                  )}
                </p>

                <div className="mt-3 text-[10px] uppercase tracking-[0.14em] text-zinc-700">
                  Tolerance:{" "}
                  {compatibility?.risk_tolerance ??
                    riskTolerance ??
                    "Not specified"}
                  {" • "}
                  Horizon:{" "}
                  {compatibility?.investment_horizon_years ??
                    investmentHorizon}{" "}
                  years
                  {" • "}
                  Acceptable Loss:{" "}
                  {acceptableLoss.toFixed(1)}%
                </div>

                {compatibility && (
                  <div className="mt-3 text-[10px] uppercase tracking-[0.14em] text-zinc-700">
                    Historical Drawdown:{" "}
                    {Math.abs(
                      compatibility.maximum_drawdown
                    ).toFixed(2)}
                    %
                  </div>
                )}

                <button
                  type="button"
                  onClick={() => {
                    window.location.href = "/risk";
                  }}
                  className="mt-5 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-400 hover:text-emerald-300"
                >
                  View detailed assessment
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Metrics */}
        <div className="mt-8">
          <div className="mb-4 text-[10px] uppercase tracking-[0.2em] text-zinc-600">
            Key Risk Metrics
          </div>

          <div className="grid gap-px border border-white/10 bg-white/10 sm:grid-cols-2 lg:grid-cols-5">
            {metrics.map((metric) => (
              <div
                key={metric.label}
                className="bg-[#0c1118] p-5"
              >
                <div className="text-[9px] uppercase tracking-[0.14em] text-zinc-600">
                  {metric.label}
                </div>

                <div className="mt-4 font-mono text-2xl">
                  {metric.value}
                </div>

                <div className="mt-2 text-[9px] uppercase tracking-[0.14em] text-zinc-700">
                  {metric.status}
                </div>
              </div>
            ))}

            {metrics.length === 0 && (
              <div className="col-span-full bg-[#0c1118] p-5 text-xs text-zinc-600">
                Risk metrics unavailable.
              </div>
            )}
          </div>
        </div>

        {/* Portfolio and risk contribution */}
        <div className="mt-8 grid gap-px border border-white/10 bg-white/10 lg:grid-cols-2">
          {/* Allocation */}
          <div className="bg-[#0c1118] p-7">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                  Portfolio Allocation
                </div>

                <div className="mt-1 text-xs text-zinc-700">
                  Current portfolio weights
                </div>
              </div>

              <PieChartIcon />
            </div>

            <div className="mt-7 space-y-5">
              {Object.entries(calculatedWeights).map(
                ([symbol, value]) => (
                  <div key={symbol}>
                    <div className="mb-2 flex justify-between text-[10px]">
                      <span className="font-mono text-zinc-400">
                        {symbol}
                      </span>

                      <span className="font-mono text-zinc-600">
                        {(Number(value) * 100).toFixed(
                          2
                        )}
                        %
                      </span>
                    </div>

                    <div className="h-1 bg-zinc-900">
                      <div
                        className="h-1 bg-zinc-400"
                        style={{
                          width: `${
                            Number(value) * 100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                )
              )}
            </div>

            {Object.keys(calculatedWeights).length ===
              0 && (
              <div className="mt-7 text-xs text-zinc-600">
                Portfolio allocation data unavailable.
              </div>
            )}
          </div>

          {/* Risk contribution */}
          <div className="bg-[#0c1118] p-7">
            <div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
                Risk Contribution
              </div>

              <div className="mt-1 text-xs text-zinc-700">
                Contribution to total portfolio risk
              </div>
            </div>

            <div className="mt-7 space-y-5">
              {riskContributions.map(
                (item, index) => (
                  <div key={item.symbol}>
                    <div className="mb-2 flex justify-between text-[10px]">
                      <span className="font-mono text-zinc-400">
                        {index + 1}. {item.symbol}
                      </span>

                      <span className="font-mono text-zinc-600">
                        {item.value.toFixed(1)}%
                      </span>
                    </div>

                    <div className="h-1 bg-zinc-900">
                      <div
                        className={`h-1 ${
                          index === 0
                            ? "bg-amber-400"
                            : "bg-zinc-500"
                        }`}
                        style={{
                          width: `${Math.min(
                            item.value,
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                )
              )}
            </div>

            {largestRiskContributor && (
              <div className="mt-7 border-t border-white/10 pt-5">
                <div className="flex items-start gap-3">
                  <TrendingUp
                    size={15}
                    className="mt-0.5 text-amber-400"
                  />

                  <p className="text-xs leading-5 text-zinc-500">
                    <span className="font-mono text-zinc-300">
                      {largestRiskContributor.symbol}
                    </span>{" "}
                    currently contributes approximately{" "}
                    <span className="font-mono text-zinc-300">
                      {largestRiskContributor.value.toFixed(
                        1
                      )}
                      %
                    </span>{" "}
                    of total portfolio risk.
                  </p>
                </div>
              </div>
            )}

            {riskContributions.length === 0 && (
              <div className="mt-7 text-xs text-zinc-600">
                Risk contribution data unavailable.
              </div>
            )}
          </div>
        </div>

        {/* Recommendations */}
        <div className="mt-8 border border-amber-400/20 bg-amber-400/[0.03] p-7">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
            <div className="flex gap-4">
              <TrendingDown
                size={20}
                className="mt-1 shrink-0 text-amber-400"
              />

              <div>
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-400">
                  Recommended Actions
                </div>

                {recommendations.length > 0 ? (
                  <div className="mt-3 space-y-3">
                    {recommendations.map(
                      (recommendation, index) => (
                        <div
                          key={index}
                          className="text-sm leading-6 text-zinc-500"
                        >
                          <span className="mr-2 font-mono text-amber-400">
                            {String(index + 1).padStart(
                              2,
                              "0"
                            )}
                          </span>

                          {recommendation}
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
                    The portfolio is currently broadly
                    aligned with the investor profile.
                  </p>
                )}
              </div>
            </div>

            <button
              type="button"
              onClick={() => {
                window.location.href = "/optimize";
              }}
              className="flex shrink-0 items-center justify-center gap-2 bg-emerald-400 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#06100c] hover:bg-emerald-300"
            >
              Explore Optimization
              <ChevronRight size={14} />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 flex justify-end">
          <button
            type="button"
            onClick={() => {
              window.location.href = "/risk";
            }}
            className="flex items-center gap-2 border border-white/10 px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-zinc-400 hover:bg-white/5 hover:text-zinc-100"
          >
            Continue to Risk Analysis
            <ArrowRight size={14} />
          </button>
        </div>
      </section>
    </main>
  );
}

/*
 * Convert backend risk metrics into the format required
 * by the Dashboard UI.
 */
function buildMetrics(
  risk: RiskMetrics
): MetricDisplay[] {
  return [
    {
      label: "Annualized Volatility",
      value: `${(
        risk.annualized_volatility * 100
      ).toFixed(2)}%`,
      status:
        risk.annualized_volatility >= 0.25
          ? "HIGH"
          : risk.annualized_volatility >= 0.15
          ? "MODERATE"
          : "LOW",
    },

    {
      label: "Maximum Drawdown",
      value: `${(
        risk.maximum_drawdown * 100
      ).toFixed(2)}%`,
      status:
        Math.abs(risk.maximum_drawdown) >= 0.30
          ? "HIGH"
          : Math.abs(risk.maximum_drawdown) >= 0.15
          ? "MODERATE"
          : "LOW",
    },

    {
      label: "Sharpe Ratio",
      value: risk.sharpe_ratio.toFixed(3),
      status:
        risk.sharpe_ratio >= 1
          ? "STRONG"
          : risk.sharpe_ratio >= 0.5
          ? "POSITIVE"
          : "WEAK",
    },

    {
      label: "Historical VaR (95%)",
      value: `${(
        risk.historical_var * 100
      ).toFixed(2)}%`,
      status: "1-DAY",
    },

    {
      label: "Expected Shortfall",
      value: `${(
        risk.expected_shortfall * 100
      ).toFixed(2)}%`,
      status: "1-DAY",
    },
  ];
}

function PieChartIcon() {
  return (
    <div className="relative h-6 w-6 rounded-full border border-zinc-600">
      <div className="absolute right-0 top-0 h-3 w-3 border-b border-l border-zinc-600 bg-[#0c1118]" />
    </div>
  );
}