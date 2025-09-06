"use client";

import { useTranslation } from "react-i18next";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { fetchJson } from "@/libs/api";

const schema = z.object({
  title: z.string().min(1),
});

export default function NewQuizPage() {
  const { t } = useTranslation();
  const router = useRouter();
  const { register, handleSubmit } = useForm<{ title: string }>({
    resolver: zodResolver(schema),
  });

  const onSubmit = handleSubmit(async (data) => {
    try {
      await fetchJson("/quizzes", {
        method: "POST",
        body: JSON.stringify(data),
      });
      router.push("/quizzes");
    } catch {
      // ignore errors for now
    }
  });

  return (
    <form onSubmit={onSubmit} className="p-4 max-w-md space-y-4">
      <div>
        <label className="block mb-1">{t("quiz.title")}</label>
        <Input {...register("title")} />
      </div>
      <Button type="submit">{t("quiz.new")}</Button>
    </form>
  );
}
