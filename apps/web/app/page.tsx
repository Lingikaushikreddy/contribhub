"use client";

import {
  Sparkles,
  Target,
  Activity,
  ArrowRight,
  Github,
  Zap,
  Users,
  BarChart3,
  Shield,
} from "lucide-react";
import { Button } from "./components/ui/Button";
import Link from "next/link";
import clsx from "clsx";

const FEATURES = [
  {
    icon: Zap,
    title: "Auto-Triage",
    description:
      "AI classifies incoming issues by category, priority, and complexity in seconds. Label accurately with 94%+ confidence.",
    color: "text-amber-400",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/20",
  },
  {
    icon: Target,
    title: "Smart Matching",
    description:
      "Match issues to contributors based on skills, interests, and track record. Right person, right task, every time.",
    color: "text-indigo-400",
    bgColor: "bg-indigo-500/10",
    borderColor: "border-indigo-500/20",
  },
  {
    icon: Activity,
    title: "Health Scoring",
    description:
      "Real-time health scores across 6 dimensions: docs, responsiveness, resolution rate, community, code quality, and releases.",
    color: "text-emerald-400",
    bgColor: "bg-emerald-500/10",
    borderColor: "border-emerald-500/20",
  },
];

const STATS = [
  { value: "50K+", label: "Issues Triaged", icon: BarChart3 },
  { value: "10K+", label: "Contributors Matched", icon: Users },
  { value: "94.2%", label: "AI Accuracy", icon: Target },
  { value: "2.4min", label: "Avg Response Time", icon: Zap },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background gradient effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-600/5 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-6xl mx-auto px-6 pt-20 pb-24 sm:pt-28 sm:pb-32">
          {/* Badge */}
          <div className="flex justify-center mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-sm">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span className="text-indigo-300 font-medium">
                Powered by advanced AI models
              </span>
            </div>
          </div>

          {/* Main heading */}
          <h1 className="text-center text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight">
            <span className="text-zinc-100">AI-Powered</span>
            <br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Open Source Triage
            </span>
            <br />
            <span className="text-zinc-100">& Matching</span>
          </h1>

          {/* Subtitle */}
          <p className="mt-6 text-center text-lg sm:text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
            Automatically classify, prioritize, and respond to GitHub issues.
            Match the right contributors to the right tasks. Built for
            maintainers who value their time.
          </p>

          {/* CTA buttons */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/signin">
              <Button
                size="lg"
                icon={<Github className="w-5 h-5" />}
                className="text-base px-8 py-4"
              >
                Install GitHub App
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button
                variant="secondary"
                size="lg"
                icon={<ArrowRight className="w-5 h-5" />}
                className="text-base px-8 py-4"
              >
                View Demo Dashboard
              </Button>
            </Link>
          </div>

          {/* Trust indicator */}
          <div className="mt-8 flex items-center justify-center gap-2 text-sm text-zinc-500">
            <Shield className="w-4 h-4" />
            <span>SOC 2 compliant. Your code stays yours.</span>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="border-y border-zinc-800 bg-zinc-900/50">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {STATS.map((stat) => {
              const Icon = stat.icon;
              return (
                <div key={stat.label} className="text-center">
                  <div className="flex justify-center mb-3">
                    <div className="p-2.5 rounded-xl bg-zinc-800 border border-zinc-700">
                      <Icon className="w-5 h-5 text-indigo-400" />
                    </div>
                  </div>
                  <p className="text-3xl sm:text-4xl font-bold text-zinc-100 tracking-tight">
                    {stat.value}
                  </p>
                  <p className="mt-1 text-sm text-zinc-500">{stat.label}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-6xl mx-auto px-6 py-20 sm:py-28">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-zinc-100 tracking-tight">
            Everything your project needs
          </h2>
          <p className="mt-4 text-lg text-zinc-400 max-w-xl mx-auto">
            From issue intake to contributor onboarding, ContribHub handles the
            heavy lifting so you can focus on building.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className={clsx(
                  "rounded-2xl border p-8 transition-all hover:scale-[1.02]",
                  feature.borderColor,
                  "bg-zinc-900"
                )}
              >
                <div
                  className={clsx(
                    "w-12 h-12 rounded-xl flex items-center justify-center",
                    feature.bgColor
                  )}
                >
                  <Icon className={clsx("w-6 h-6", feature.color)} />
                </div>
                <h3 className="mt-5 text-xl font-semibold text-zinc-100">
                  {feature.title}
                </h3>
                <p className="mt-3 text-sm text-zinc-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* How It Works */}
      <section className="border-t border-zinc-800 bg-zinc-900/30">
        <div className="max-w-6xl mx-auto px-6 py-20 sm:py-28">
          <h2 className="text-center text-3xl sm:text-4xl font-bold text-zinc-100 tracking-tight mb-16">
            How it works
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Install the GitHub App",
                description:
                  "One click to connect your repositories. ContribHub starts analyzing your issue history immediately.",
              },
              {
                step: "02",
                title: "AI triages every issue",
                description:
                  "New issues are classified by category, priority, and complexity. Draft responses are generated for review.",
              },
              {
                step: "03",
                title: "Match & grow contributors",
                description:
                  "Contributors discover perfectly-matched issues. Skills grow over time with progressive difficulty matching.",
              },
            ].map((item) => (
              <div key={item.step} className="relative">
                <div className="text-6xl font-black text-zinc-800/50 mb-4">
                  {item.step}
                </div>
                <h3 className="text-lg font-semibold text-zinc-100">
                  {item.title}
                </h3>
                <p className="mt-2 text-sm text-zinc-400 leading-relaxed">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-6xl mx-auto px-6 py-20 sm:py-28">
        <div className="rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-600/10 to-purple-600/10 p-12 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-zinc-100 tracking-tight">
            Ready to streamline your project?
          </h2>
          <p className="mt-4 text-lg text-zinc-400 max-w-xl mx-auto">
            Join thousands of maintainers using ContribHub to save time and grow
            their contributor community.
          </p>
          <div className="mt-8">
            <Link href="/auth/signin">
              <Button
                size="lg"
                icon={<Github className="w-5 h-5" />}
                className="text-base px-8 py-4"
              >
                Get Started Free
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800 py-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span className="text-sm font-semibold text-zinc-400">ContribHub</span>
          </div>
          <p className="text-xs text-zinc-600">
            Built with care for the open source community.
          </p>
        </div>
      </footer>
    </div>
  );
}
