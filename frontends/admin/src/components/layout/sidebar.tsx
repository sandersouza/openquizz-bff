"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslation } from "react-i18next";

import { cn } from "@/lib/utils";
import { Button } from "../ui/button";
import { DarkModeToggle } from "../dark-mode-toggle";

export function Sidebar() {
  const { t } = useTranslation();
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const links = [
    { href: "/quizzes", label: t("nav.quizzes") },
    { href: "/sessions", label: t("nav.sessions") },
    { href: "/analytics", label: t("nav.analytics") },
  ];

  return (
    <div
      className={cn(
        "relative transition-all duration-300",
        collapsed ? "w-4" : "w-48"
      )}
    >
      <aside
        className={cn(
          "h-screen border-r p-4 flex flex-col gap-4 bg-background rounded-r-md transition-transform duration-300",
          collapsed ? "-translate-x-full" : "translate-x-0"
        )}
      >
        <nav className="flex flex-col gap-2">
          {links.map((link) => (
            <Link key={link.href} href={link.href}>
              <Button
                variant={
                  pathname.startsWith(link.href) ? "secondary" : "ghost"
                }
                className="w-full justify-start"
              >
                {link.label}
              </Button>
            </Link>
          ))}
        </nav>
        <div className="mt-auto">
          <DarkModeToggle />
        </div>
      </aside>
      <button
        type="button"
        onClick={() => setCollapsed((c) => !c)}
        className="absolute top-2 -right-3 w-6 h-6 flex items-center justify-center rounded-r-md border bg-background shadow" 
      >
        {collapsed ? ">" : "<"}
      </button>
    </div>
  );
}
