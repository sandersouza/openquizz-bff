import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Sidebar } from "@/components/layout/sidebar";
import { DarkModeToggle } from "@/components/dark-mode-toggle";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "OpenQUIZ Admin",
  description: "Admin interface",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <Providers>
          <div className="theme-toggle-fixed">
            <DarkModeToggle />
          </div>
          <div className="layout-root">
            <Sidebar />
            <main className="layout-main">
              <div className="floating-frame">
                {children}
              </div>
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
