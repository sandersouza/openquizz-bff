"use client";

import { useTranslation } from "react-i18next";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { PlusIcon, MinusIcon } from "lucide-react";
import {
  useForm,
  useFieldArray,
  type Control,
  type UseFormRegister,
} from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { fetchJson } from "@/libs/api";

const answerSchema = z.object({
  text: z.string().min(1),
});

const questionSchema = z
  .object({
    text: z.string().min(1),
    time_limit_s: z.number().int().min(10).max(60),
    options: z.array(answerSchema).min(2).max(5),
    correct: z.number().int(),
  })
  .refine((q) => q.correct >= 0 && q.correct < q.options.length, {
    message: "Correct answer must be one of the options",
    path: ["correct"],
  });

const schema = z.object({
  title: z.string().min(1),
  questions: z.array(questionSchema).min(2).max(20),
});

type QuizForm = z.infer<typeof schema>;

type QuestionFieldsProps = {
  index: number;
  control: Control<QuizForm>;
  register: UseFormRegister<QuizForm>;
  t: (key: string) => string;
  removeQuestion: (index: number) => void;
};

function QuestionFields({ index, control, register, t, removeQuestion }: QuestionFieldsProps) {
  const {
    fields: answers,
    append: appendAnswer,
    remove: removeAnswer,
  } = useFieldArray({
    control,
    name: `questions.${index}.options` as const,
  });

  return (
    <div className="space-y-4 rounded-lg border p-4">
      <div className="flex items-start gap-2">
        <Input
          placeholder={t("quiz.question")}
          className="flex-grow"
          {...register(`questions.${index}.text` as const)}
        />
        <div className="flex items-center gap-2">
          <Input
            type="number"
            min={10}
            max={60}
            className="w-20"
            {...register(`questions.${index}.time_limit_s` as const, {
              valueAsNumber: true,
            })}
          />
          <span className="text-sm text-muted-foreground">
            {t("quiz.seconds")}
          </span>
        </div>
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={() => removeQuestion(index)}
        >
          <MinusIcon className="size-4" />
        </Button>
      </div>
      <div className="space-y-2">
        {answers.map((ansField, ansIndex) => (
          <div key={ansField.id} className="flex items-center gap-2">
            <Input
              className="flex-grow"
              placeholder={t("quiz.answer")}
              {...register(`questions.${index}.options.${ansIndex}.text` as const)}
            />
            <input
              type="radio"
              value={ansIndex}
              {...register(`questions.${index}.correct` as const, {
                valueAsNumber: true,
              })}
              aria-label={t("quiz.correct")}
            />
          </div>
        ))}
        <div className="flex gap-2 pt-2">
          {answers.length < 5 && (
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => appendAnswer({ text: "" })}
            >
              <PlusIcon className="size-4" />
            </Button>
          )}
          {answers.length > 2 && (
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => removeAnswer(answers.length - 1)}
            >
              <MinusIcon className="size-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function NewQuizPage() {
  const { t } = useTranslation();
  const router = useRouter();
  const { register, handleSubmit, control } = useForm<QuizForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      questions: [
        {
          text: "",
          time_limit_s: 20,
          options: [{ text: "" }, { text: "" }],
          correct: 0,
        },
      ],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "questions",
  });

  const onSubmit = handleSubmit(async (data) => {
    const payload = {
      title: data.title,
      questions: data.questions.map((q: QuizForm["questions"][number]) => ({
        id: crypto.randomUUID(),
        text: q.text,
        options: q.options.map((o: { text: string }) => o.text),
        correct: [q.correct],
        time_limit_s: q.time_limit_s,
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
    <form onSubmit={onSubmit} className="p-4 space-y-4">
      <Input placeholder={t("quiz.title")} {...register("title")} />
      <div className="space-y-4">
        {fields.map((field, index) => (
          <QuestionFields
            key={field.id}
            index={index}
            control={control}
            register={register}
            t={t}
            removeQuestion={remove}
          />
        ))}
      </div>
      {fields.length < 20 && (
        <Button
          type="button"
          variant="outline"
          onClick={() =>
            append({
              text: "",
              time_limit_s: 20,
              options: [{ text: "" }, { text: "" }],
              correct: 0,
            })
          }
        >
          {t("quiz.add_question")}
        </Button>
      )}
      <Button type="submit">{t("quiz.new")}</Button>
    </form>
  );
}
