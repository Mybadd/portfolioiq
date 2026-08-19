"use client";

import { useState } from "react";
import { ArrowRight, ShieldCheck, TrendingUp } from "lucide-react";
import Navigation from "@/components/Navigation";
const riskOptions = ["LOW", "MODERATE", "HIGH"] as const;

const objectives = [
  "LONG_TERM_GROWTH",
  "CAPITAL_PRESERVATION",
  "INCOME",
  "BALANCED_GROWTH",
];

export default function Home() {
  const [investmentAmount, setInvestmentAmount] = useState("1000000");
  const [horizon, setHorizon] = useState("7");
  const [riskTolerance, setRiskTolerance] =
    useState<(typeof riskOptions)[number]>("MODERATE");
  const [maximumLoss, setMaximumLoss] = useState("20");
  const [objective, setObjective] = useState("LONG_TERM_GROWTH");
  const [error, setError] = useState("");

  const formatAmount = (value: string) => {
    const number = Number(value);

    if (!number) return "";

    return new Intl.NumberFormat("en-IN").format(number);
  };

  const handleSubmit = () => {
    setError("");

    const amount = Number(investmentAmount);
    const years = Number(horizon);
    const loss = Number(maximumLoss);

    if (amount <= 0) {
      setError("Investment amount must be greater than zero.");
      return;
    }

    if (years <= 0) {
      setError("Investment horizon must be greater than zero.");
      return;
    }

    if (loss <= 0 || loss > 100) {
      setError("Maximum acceptable loss must be between 1% and 100%.");
      return;
    }

    const profile = {
      investmentAmount: amount,
      investmentHorizonYears: years,
      riskTolerance,
      maximumAcceptableLoss: loss / 100,
      investmentObjective: objective,
    };

    sessionStorage.setItem(
      "portfolioiq-investor-profile",
      JSON.stringify(profile)
    );

    window.location.href = "/portfolio";
  };

  return (
  <main className="min-h-screen bg-[#080b10] text-zinc-100">
    <Navigation />

    {/* Rest of Profile page */}
      {/* Main content */}
      <section className="mx-auto grid min-h-[calc(100vh-105px)] max-w-7xl grid-cols-1 gap-12 px-6 py-14 lg:grid-cols-[0.9fr_1.1fr] lg:px-10 lg:py-20">
        {/* Left introduction */}
        <div className="flex flex-col justify-center">
          <div className="mb-6 flex items-center gap-2 text-[10px] uppercase tracking-[0.25em] text-emerald-400">
            <ShieldCheck size={14} />
            Investor Assessment
          </div>

          <h1 className="max-w-xl text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl">
            Understand your risk before you invest.
          </h1>

          <p className="mt-6 max-w-lg text-sm leading-7 text-zinc-400">
            PortfolioIQ combines your investment objectives with quantitative
            portfolio analysis to determine whether your portfolio fits your
            risk profile.
          </p>

          <div className="mt-10 grid max-w-lg grid-cols-2 gap-px overflow-hidden border border-white/10 bg-white/10">
            <div className="bg-[#0b0f15] p-5">
              <div className="text-[10px] uppercase tracking-[0.18em] text-zinc-600">
                Analysis
              </div>

              <div className="mt-2 text-sm text-zinc-300">
                Quantitative
              </div>
            </div>

            <div className="bg-[#0b0f15] p-5">
              <div className="text-[10px] uppercase tracking-[0.18em] text-zinc-600">
                Objective
              </div>

              <div className="mt-2 text-sm text-zinc-300">
                Investor-specific
              </div>
            </div>
          </div>

          <div className="mt-8 flex items-center gap-3 text-xs text-zinc-600">
            <TrendingUp size={15} />
            Your portfolio analysis starts with your investment goals.
          </div>
        </div>

        {/* Form */}
        <div className="flex items-center">
          <div className="w-full border border-white/10 bg-[#0c1118]">
            {/* Form header */}
            <div className="border-b border-white/10 px-6 py-5 sm:px-8">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.2em]">
                    Investor Profile
                  </div>

                  <div className="mt-1 text-xs text-zinc-600">
                    Step 01 / 07
                  </div>
                </div>

                <div className="font-mono text-xs text-zinc-600">
                  PIQ-01
                </div>
              </div>
            </div>

            <div className="space-y-7 p-6 sm:p-8">
              {/* Investment amount */}
              <div>
                <label className="text-[10px] font-medium uppercase tracking-[0.2em] text-zinc-500">
                  Investment Amount
                </label>

                <div className="mt-2 flex items-center border border-white/10 bg-[#080b10]">
                  <span className="border-r border-white/10 px-4 py-3 font-mono text-sm text-zinc-500">
                    ₹
                  </span>

                  <input
                    type="number"
                    min="1"
                    value={investmentAmount}
                    onChange={(e) => setInvestmentAmount(e.target.value)}
                    className="w-full bg-transparent px-4 py-3 font-mono text-lg outline-none placeholder:text-zinc-700"
                    placeholder="1000000"
                  />
                </div>

                <div className="mt-2 font-mono text-[10px] text-zinc-600">
                  {investmentAmount
                    ? `₹ ${formatAmount(investmentAmount)}`
                    : "Enter your investment amount"}
                </div>
              </div>

              {/* Horizon */}
              <div>
                <label className="text-[10px] font-medium uppercase tracking-[0.2em] text-zinc-500">
                  Investment Horizon
                </label>

                <div className="mt-2 flex items-center border border-white/10 bg-[#080b10]">
                  <input
                    type="number"
                    min="1"
                    value={horizon}
                    onChange={(e) => setHorizon(e.target.value)}
                    className="w-full bg-transparent px-4 py-3 font-mono text-lg outline-none"
                  />

                  <span className="border-l border-white/10 px-4 py-3 text-[10px] uppercase tracking-wider text-zinc-500">
                    Years
                  </span>
                </div>
              </div>

              {/* Risk tolerance */}
              <div>
                <label className="text-[10px] font-medium uppercase tracking-[0.2em] text-zinc-500">
                  Risk Tolerance
                </label>

                <div className="mt-2 grid grid-cols-3 border border-white/10">
                  {riskOptions.map((option) => (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setRiskTolerance(option)}
                      className={`border-r border-white/10 px-3 py-3 text-[10px] font-medium uppercase tracking-[0.15em] last:border-r-0 ${
                        riskTolerance === option
                          ? "bg-emerald-400 text-[#06100c]"
                          : "bg-[#080b10] text-zinc-500 hover:bg-white/5 hover:text-zinc-200"
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>

              {/* Maximum acceptable loss */}
              <div>
                <label className="text-[10px] font-medium uppercase tracking-[0.2em] text-zinc-500">
                  Maximum Acceptable Loss
                </label>

                <div className="mt-2 flex items-center border border-white/10 bg-[#080b10]">
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={maximumLoss}
                    onChange={(e) => setMaximumLoss(e.target.value)}
                    className="w-full bg-transparent px-4 py-3 font-mono text-lg outline-none"
                  />

                  <span className="border-l border-white/10 px-4 py-3 font-mono text-zinc-500">
                    %
                  </span>
                </div>

                <div className="mt-2 text-[10px] text-zinc-600">
                  The maximum historical loss you are comfortable with.
                </div>
              </div>

              {/* Objective */}
              <div>
                <label className="text-[10px] font-medium uppercase tracking-[0.2em] text-zinc-500">
                  Investment Objective
                </label>

                <select
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  className="mt-2 w-full appearance-none border border-white/10 bg-[#080b10] px-4 py-3 text-sm text-zinc-200 outline-none"
                >
                  {objectives.map((item) => (
                    <option key={item} value={item} className="bg-[#080b10]">
                      {item.replaceAll("_", " ")}
                    </option>
                  ))}
                </select>
              </div>

              {/* Error */}
              {error && (
                <div className="border border-red-500/30 bg-red-500/5 px-4 py-3 text-xs text-red-400">
                  {error}
                </div>
              )}

              {/* Continue */}
              <button
                type="button"
                onClick={handleSubmit}
                className="group flex w-full items-center justify-between bg-emerald-400 px-5 py-4 text-xs font-semibold uppercase tracking-[0.18em] text-[#06100c] transition hover:bg-emerald-300"
              >
                <span>Continue to Portfolio</span>

                <ArrowRight
                  size={17}
                  className="transition-transform group-hover:translate-x-1"
                />
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}