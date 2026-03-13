import type { Metadata } from "next";
import { Providers } from "@/lib/providers";
import { Sidebar } from "./components/layout/Sidebar";
import { Header } from "./components/layout/Header";
import { MobileNav } from "./components/layout/MobileNav";
import "./globals.css";

export const metadata: Metadata = {
  title: "ContribHub - AI-Powered Open Source Triage & Matching",
  description:
    "Intelligent GitHub issue triage and contributor matching platform. Auto-classify, prioritize, and match issues to the right contributors.",
  openGraph: {
    title: "ContribHub",
    description: "AI-Powered Open Source Triage & Matching",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-zinc-950 text-zinc-100 antialiased">
        <Providers>
          <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0">
              <Header />
              <main className="flex-1 pb-20 md:pb-0">{children}</main>
            </div>
          </div>
          <MobileNav />
        </Providers>
      </body>
    </html>
  );
}
