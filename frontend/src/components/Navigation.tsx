"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigationItems = [
  ["01", "Profile", "/"],
  ["02", "Portfolio", "/portfolio"],
  ["03", "Dashboard", "/dashboard"],
  ["04", "Risk", "/risk"],
  ["05", "Optimize", "/optimize"],
  ["06", "Stress Test", "/stress-test"],
  ["07", "Monte Carlo", "/monte-carlo"],
  ["08", "Report", "/report"],
] as const;

export default function Navigation() {
  const pathname = usePathname();

  return (
    <div className="border-b border-white/10 bg-[#0b0f15]">
      <div className="mx-auto flex max-w-7xl items-center overflow-x-auto px-6 lg:px-10">
        {navigationItems.map(
          ([number, label, route]) => {
            const active = pathname === route;

            return (
              <Link
                key={route}
                href={route}
                className={`shrink-0 border-r border-white/10 px-5 py-4 text-[10px] uppercase tracking-[0.18em] transition ${
                  active
                    ? "bg-white/5 text-emerald-400"
                    : "text-white/50 hover:bg-white/5 hover:text-white"
                }`}
              >
                <span className="mr-2 text-white/30">
                  {number}
                </span>

                {label}
              </Link>
            );
          }
        )}
      </div>
    </div>
  );
}