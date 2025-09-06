"use client";

import Link from "next/link";
import { useTranslation } from "react-i18next";
import { DarkModeToggle } from "../dark-mode-toggle";

export function Sidebar() {
  const { t } = useTranslation();
  return (
    <aside className="w-48 p-4 border-r min-h-screen flex flex-col gap-4">
      <nav className="flex flex-col gap-2">
        <Link href="/quizzes">{t("nav.quizzes")}</Link>
        <Link href="/sessions">{t("nav.sessions")}</Link>
        <Link href="/analytics">{t("nav.analytics")}</Link>
      </nav>
      <div className="mt-auto">
        <DarkModeToggle />
      </div>
    </aside>
  );
}
