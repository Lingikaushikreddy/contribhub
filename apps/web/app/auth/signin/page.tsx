"use client";

import { signIn } from "next-auth/react";
import { Github, Sparkles, Shield, ArrowLeft } from "lucide-react";
import { Button } from "../../components/ui/Button";
import Link from "next/link";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 relative">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-indigo-600/8 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-72 h-72 bg-purple-600/8 rounded-full blur-3xl" />
      </div>

      {/* Back link */}
      <Link
        href="/"
        className="absolute top-6 left-6 flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to home
      </Link>

      {/* Sign in card */}
      <div className="relative w-full max-w-sm">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 rounded-2xl bg-indigo-600 mb-4 shadow-lg shadow-indigo-500/20">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">
            Welcome to ContribHub
          </h1>
          <p className="mt-2 text-sm text-zinc-400 text-center max-w-xs">
            Sign in with your GitHub account to start triaging issues and
            discovering contributions.
          </p>
        </div>

        {/* Sign in card */}
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6 shadow-2xl">
          <Button
            size="lg"
            icon={<Github className="w-5 h-5" />}
            className="w-full text-base py-3.5"
            onClick={() => signIn("github", { callbackUrl: "/dashboard" })}
          >
            Sign in with GitHub
          </Button>

          {/* Permissions note */}
          <div className="mt-5 space-y-2.5">
            <p className="text-xs text-zinc-500 font-medium">
              We&apos;ll request access to:
            </p>
            {[
              "Read your public profile information",
              "Access your email address",
              "Read and manage repository issues",
            ].map((perm) => (
              <div key={perm} className="flex items-center gap-2 text-xs text-zinc-500">
                <div className="w-1 h-1 rounded-full bg-zinc-600" />
                {perm}
              </div>
            ))}
          </div>
        </div>

        {/* Security note */}
        <div className="mt-6 flex items-center justify-center gap-2 text-xs text-zinc-600">
          <Shield className="w-3.5 h-3.5" />
          <span>Secured with OAuth 2.0. We never store your password.</span>
        </div>
      </div>
    </div>
  );
}
