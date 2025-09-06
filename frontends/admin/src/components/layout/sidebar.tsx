"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslation } from "react-i18next";

import { cn } from "@/lib/utils";
import { Button } from "../ui/button";
import { BookOpen, PlayCircle, BarChart3 } from "lucide-react";

export function Sidebar() {
  const { t } = useTranslation();
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const links = [
    { href: "/quizzes", label: t("nav.quizzes"), icon: BookOpen },
    { href: "/sessions", label: t("nav.sessions"), icon: PlayCircle },
    { href: "/analytics", label: t("nav.analytics"), icon: BarChart3 },
  ];

  return (
    <div
      className={cn(
        "sidebar-wrapper",
        collapsed ? "sidebar-wrapper-collapsed" : "sidebar-wrapper-expanded"
      )}
    >
      <aside
        className={cn(
          "sidebar",
          collapsed ? "sidebar-collapsed" : "sidebar-expanded"
        )}
      >
        <nav className="nav-list">
          {links.map((link) => {
            const Icon = link.icon;
            const active = pathname.startsWith(link.href);
            return (
              <Link key={link.href} href={link.href}>
                <Button
                  variant={active ? "secondary" : "ghost"}
                  className={cn("menu-button", collapsed && "menu-button-collapsed")}
                  aria-label={collapsed ? link.label : undefined}
                  title={collapsed ? link.label : undefined}
                >
                  <Icon className="menu-icon" />
                  <span className={cn("menu-label", collapsed && "menu-label-hidden")}>{link.label}</span>
                  <span className={cn(!collapsed ? undefined : "menu-spacer-hidden")} aria-hidden="true" />
                </Button>
              </Link>
            );
          })}
        </nav>
        {/* Theme toggle moved to global top-right in layout */}
      </aside>
      <button
        type="button"
        onClick={() => setCollapsed((c) => !c)}
        className="toggle-tab"
        aria-label={collapsed ? "Exibir menu" : "Ocultar menu"}
      >
        <span className="hamburger" aria-hidden="true">
          <span className="hamburger-line" />
          <span className="hamburger-line" />
          <span className="hamburger-line" />
        </span>
      </button>
    </div>
  );
}
