"use client";
import { useEffect, useState } from "react";

import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  ShieldAlert,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

const metrics = [
  {
    label: "Annualized Volatility",
    value: "19.38%",
    status: "MODERATE",
  },
  {
    label: "Maximum Drawdown",
    value: "-39.10%",
    status: "HIGH",
  },
  {
    label: "Sharpe Ratio",
    value: "0.838",
    status: "POSITIVE",
  },
  {
    label: "Historical VaR (95%)",
    value: "-1.69%",
    status: "1-DAY",
  },
  {
    label: "Expected Shortfall",
    value: "-2.74%",
    status: "1-DAY",
  },
];

const riskContributions = [
  { symbol: "NFLX", value: 52.3 },
  { symbol: "UNH", value: 24.1 },
  { symbol: "PEP", value: 11.2 },
  { symbol: "WMT", value: 7.8 },
  { symbol: "DIS", value: 4.6 },
];

export default function DashboardPage() {
    const [investmentAmount, setInvestmentAmount] = useState(0);
    const [investmentHorizon, setInvestmentHorizon] = useState(0);
    const [riskTolerance, setRiskTolerance] = useState("");
    const [objective, setObjective] = useState("");
    const [portfolio, setPortfolio] = useState<any>(null);
useEffect(() => {
  const storedProfile = sessionStorage.getItem(
    "portfolioiq-investor-profile"
  );

  if (!storedProfile) {
    window.location.href = "/";
    return;
  }

  const profile = JSON.parse(storedProfile);

  setInvestmentAmount(profile.investmentAmount);
  setInvestmentHorizon(profile.investmentHorizonYears);
  setRiskTolerance(profile.riskTolerance);
  setObjective(profile.investmentObjective);
    const storedPortfolio = sessionStorage.getItem(
        "portfolioiq-portfolio"
        );

        if (!storedPortfolio) {
        window.location.href = "/portfolio";
        return;
        }

        setPortfolio(JSON.parse(storedPortfolio));
}, []);

  return (
    <main className="min-h-screen bg-[#080b10] text-zinc-100">
      {/* Header */}
      <header className="border-b border-white/10">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 lg:px-10">
          <div>
            <div className="text-lg font-semibold tracking-[0.18em]">
              PORTFOLIO<span className="text-emerald-400">IQ</span>
            </div>

            <div className="mt-0.5 text-[9px] uppercase tracking-[0.28em] text-zinc-500">
              Quantitative Portfolio Intelligence
            </div>
          </div>

          <div className="flex items-center gap-3 text-[10px] uppercase tracking-[0.18em] text-zinc-500">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Analysis Complete
          </div>
        </div>
      </header>

      {/* Progress */}
      <div className="border-b border-white/10 bg-[#0b0f15]">
        <div className="mx-auto flex max-w-7xl items-center overflow-x-auto px-6 lg:px-10">
          {[
            ["01", "Profile"],
            ["02", "Portfolio"],
            ["03", "Dashboard"],
            ["04", "Risk"],
            ["05", "Optimize"],
            ["06", "Stress Test"],
            ["07", "Report"],
          ].map(([number, label]) => {
            const active = number === "03";

            return (
              <div
                key={number}
                className={`flex shrink-0 items-center gap-2 border-r border-white/10 px-4 py-3 first:pl-0 ${
                  active ? "text-zinc-100" : "text-zinc-600"
                }`}
              >
                <span
                  className={`font-mono text-[10px] ${
                    active ? "text-emerald-400" : "text-zinc-600"
                  }`}
                >
                  {number}
                </span>

                <span className="text-[10px] uppercase tracking-[0.14em]">
                  {label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

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
              A quantitative overview of your portfolio's risk,
              performance characteristics, and investor compatibility.
            </p>
          </div>

          <div className="border border-white/10 bg-[#0c1118] px-5 py-4">
            <div className="text-[9px] uppercase tracking-[0.18em] text-zinc-600">
              Portfolio Status
            </div>

            <div className="mt-2 flex items-center gap-2 text-sm">
              <span className="h-2 w-2 rounded-full bg-amber-400" />
              Review Required
            </div>
          </div>
        </div>

        {/* Risk score */}
        <div className="grid gap-px border border-white/10 bg-white/10 lg:grid-cols-[1fr_2fr]">
          <div className="bg-[#0c1118] p-7">
            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Overall Risk Score
            </div>

            <div className="mt-6 flex items-end gap-3">
              <span className="font-mono text-6xl font-medium tracking-tight">
                38
              </span>

              <span className="mb-2 font-mono text-sm text-zinc-600">
                / 100
              </span>
            </div>

            <div className="mt-4 inline-flex items-center gap-2 border border-amber-400/30 bg-amber-400/5 px-3 py-2 text-[10px] uppercase tracking-[0.18em] text-amber-400">
              <ShieldAlert size={13} />
              Moderate Risk
            </div>
          </div>

          <div className="bg-[#0c1118] p-7">
            <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-600">
              Investor Compatibility
            </div>

            <div className="mt-5 flex items-start gap-4">
              <AlertTriangle
                size={22}
                className="mt-1 shrink-0 text-amber-400"
              />

              <div>
                <div className="text-lg font-medium">
                  Review
                </div>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
                  Historical maximum drawdown exceeds your
                  maximum acceptable loss of 20%.
                </p>

                <button
                  onClick={() =>
                    (window.location.href = "/risk-analysis")
                  }
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
              {[
                ["NFLX", 20],
                ["PEP", 25],
                ["WMT", 20],
                ["UNH", 15],
                ["DIS", 20],
              ].map(([symbol, value]) => (
                <div key={symbol}>
                  <div className="mb-2 flex justify-between text-[10px]">
                    <span className="font-mono text-zinc-400">
                      {symbol}
                    </span>

                    <span className="font-mono text-zinc-600">
                      {value}%
                    </span>
                  </div>

                  <div className="h-1 bg-zinc-900">
                    <div
                      className="h-1 bg-zinc-400"
                      style={{ width: `${value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
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
              {riskContributions.map((item, index) => (
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
                        width: `${item.value}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-7 border-t border-white/10 pt-5">
              <div className="flex items-start gap-3">
                <TrendingUp
                  size={15}
                  className="mt-0.5 text-amber-400"
                />

                <p className="text-xs leading-5 text-zinc-500">
                  NFLX currently contributes approximately
                  52.3% of total portfolio risk. Consider
                  reviewing its allocation.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Recommendation */}
        <div className="mt-8 border border-amber-400/20 bg-amber-400/[0.03] p-7">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
            <div className="flex gap-4">
              <TrendingDown
                size={20}
                className="mt-1 shrink-0 text-amber-400"
              />

              <div>
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-400">
                  Recommended Action
                </div>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
                  Consider reducing portfolio exposure because
                  historical drawdown exceeds your maximum
                  acceptable loss.
                </p>
              </div>
            </div>

            <button
              onClick={() =>
                (window.location.href = "/optimization")
              }
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
            onClick={() =>
              (window.location.href = "/risk-analysis")
            }
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

function PieChartIcon() {
  return (
    <div className="relative h-6 w-6 rounded-full border border-zinc-600">
      <div className="absolute right-0 top-0 h-3 w-3 border-l border-b border-zinc-600 bg-[#0c1118]" />
    </div>
  );
}