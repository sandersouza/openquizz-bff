"use client";

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { joinGame } from "@/lib/api";

export default function Page() {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [code, setCode] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await joinGame(name, code);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <main>
      <h1>{t("join.title")}</h1>
      <form onSubmit={onSubmit}>
        <label>
          {t("join.name")}
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          {t("join.code")}
          <input value={code} onChange={(e) => setCode(e.target.value)} />
        </label>
        <button type="submit">{t("join.submit")}</button>
      </form>
    </main>
  );
}
