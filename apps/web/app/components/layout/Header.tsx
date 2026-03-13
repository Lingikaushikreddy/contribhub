"use client";

import { Bell, Settings, LogOut } from "lucide-react";
import { useSession, signOut } from "next-auth/react";
import { Avatar } from "../ui/Avatar";
import Link from "next/link";
import { useState } from "react";
import clsx from "clsx";

export function Header() {
  const { data: session } = useSession();
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <header className="sticky top-0 z-40 h-16 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-xl">
      <div className="flex items-center justify-between h-full px-6">
        {/* Left section */}
        <div className="flex items-center gap-4">
          <h1 className="text-sm font-semibold text-zinc-300">
            {/* Breadcrumb could go here */}
          </h1>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <button
            className="relative p-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-500 rounded-full" />
          </button>

          {/* Settings */}
          <Link
            href="/settings"
            className="p-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
            aria-label="Settings"
          >
            <Settings className="w-5 h-5" />
          </Link>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2.5 p-1.5 rounded-lg hover:bg-zinc-800 transition-colors"
            >
              <Avatar
                src={session?.user?.image || undefined}
                alt={session?.user?.name || "User"}
                size="md"
              />
              {session?.user?.name && (
                <span className="text-sm font-medium text-zinc-300 hidden lg:block">
                  {session.user.name}
                </span>
              )}
            </button>

            {showUserMenu && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setShowUserMenu(false)}
                />
                <div className="absolute right-0 top-12 z-50 w-56 rounded-xl border border-zinc-700 bg-zinc-900 shadow-2xl py-1.5 animate-fade-in">
                  <div className="px-4 py-2.5 border-b border-zinc-800">
                    <p className="text-sm font-medium text-zinc-200">
                      {session?.user?.name || "User"}
                    </p>
                    <p className="text-xs text-zinc-500 mt-0.5">
                      {session?.user?.email || "user@example.com"}
                    </p>
                  </div>
                  <Link
                    href="/profile"
                    className="flex items-center gap-2.5 px-4 py-2 text-sm text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <Avatar
                      src={session?.user?.image || undefined}
                      alt="Profile"
                      size="sm"
                    />
                    View Profile
                  </Link>
                  <Link
                    href="/settings"
                    className="flex items-center gap-2.5 px-4 py-2 text-sm text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <Settings className="w-4 h-4" />
                    Settings
                  </Link>
                  <div className="border-t border-zinc-800 mt-1.5 pt-1.5">
                    <button
                      onClick={() => signOut()}
                      className="flex items-center gap-2.5 px-4 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-zinc-800 transition-colors w-full text-left"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign Out
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
