"use client";

import { useTranslation } from "react-i18next";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useForm, useFieldArray } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { fetchJson } from "@/libs/api";
const questionSchema = z.object({
  question: z.string().min(1),
  answer: z.string().min(1),
});

const schema = z.object({
  title: z.string().min(1),
  questions: z.array(questionSchema).min(1),
});

type QuizForm = z.infer<typeof schema>;

export default function NewQuizPage() {
  const { t } = useTranslation();
  const router = useRouter();
  const { register, handleSubmit, control } = useForm<QuizForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      questions: [{ question: "", answer: "" }],
    },
  });

  const { fields, append } = useFieldArray({
    control,
    name: "questions",
  });

  const onSubmit = handleSubmit(async (data) => {
    const payload = {
      title: data.title,
      questions: data.questions.map((q) => ({
        id: crypto.randomUUID(),
        text: q.question,
        options: [q.answer],
        correct: [0],
        time_limit_s: 20,
      })),
    };
    try {
      await fetchJson("/quizzes", {
        method: "POST",
        body: JSON.stringify(payload),
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
      <div className="space-y-4">
        {fields.map((field, index) => (
          <div key={field.id} className="space-y-2">
            <div>
              <label className="block mb-1">
                {t("quiz.question")} #{index + 1}
              </label>
              <Input {...register(`questions.${index}.question` as const)} />
            </div>
            <div>
              <label className="block mb-1">{t("quiz.answer")}</label>
              <Input {...register(`questions.${index}.answer` as const)} />
            </div>
          </div>
        ))}
        <Button
          type="button"
          variant="outline"
          onClick={() => append({ question: "", answer: "" })}
        >
          {t("quiz.add_question")}
        </Button>
      </div>
      <Button type="submit">{t("quiz.new")}</Button>
    </form>
  );
}
