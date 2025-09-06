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
    <div className="p-4">
      <h1 className="text-xl mb-4">{t("nav.quizzes")}</h1>
      <table className="w-full text-left">
        <thead>
          <tr>
            <th className="p-2">{t("quiz.title")}</th>
            <th className="p-2">{t("quiz.questions")}</th>
          </tr>
        </thead>
        <tbody>
          {quizzes.map((q) => (
            <tr key={q.id} className="border-t">
              <td className="p-2">{q.title}</td>
              <td className="p-2">{q.questions_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <Link href="/quizzes/new">
        <Button className="mt-4">{t("quiz.new")}</Button>
      </Link>
    </div>
  );
}
