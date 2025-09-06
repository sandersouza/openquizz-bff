"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslation } from "react-i18next";
import { fetchJson } from "@/libs/api";
import { Button } from "@/components/ui/button";

type Quiz = {
  id: string;
  title: string;
  questions_count: number;
};

export default function QuizzesPage() {
  const { t } = useTranslation();
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);

  useEffect(() => {
    fetchJson<Quiz[]>("/quizzes?limit=10").then(setQuizzes).catch(() => {});
  }, []);

  return (
    <div className="page-container">
      <h1 className="page-title">{t("nav.quizzes")}</h1>
      <table className="table-base">
        <thead>
          <tr>
            <th className="table-th">{t("quiz.title")}</th>
            <th className="table-th">{t("quiz.questions")}</th>
          </tr>
        </thead>
        <tbody>
          {quizzes.map((q) => (
            <tr key={q.id} className="table-row">
              <td className="table-td">{q.title}</td>
              <td className="table-td">{q.questions_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <Link href="/quizzes/new">
        <Button className="btn-top-gap">{t("quiz.new")}</Button>
      </Link>
    </div>
  );
}
