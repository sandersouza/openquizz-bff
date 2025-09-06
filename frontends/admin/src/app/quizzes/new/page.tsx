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
  questions: z.array(questionSchema).min(1).max(20),
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
    <div className="card">
      <div className="row">
        <Input
          placeholder={t("quiz.question")}
          className="grow"
          {...register(`questions.${index}.text` as const)}
        />
        <div className="inline-row">
          <Input
            type="number"
            min={10}
            max={60}
            className="w-20p"
            {...register(`questions.${index}.time_limit_s` as const, {
              valueAsNumber: true,
            })}
          />
          <span className="muted-note">
            {t("quiz.seconds")}
          </span>
        </div>
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={() => removeQuestion(index)}
        >
          <MinusIcon className="icon-sm" />
        </Button>
      </div>
      <div className="row-gap">
        {answers.map((ansField, ansIndex) => (
          <div key={ansField.id} className="inline-row">
            <Input
              className="grow"
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
        <div className="row-actions">
          {answers.length < 5 && (
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => appendAnswer({ text: "" })}
            >
              <PlusIcon className="icon-sm" />
            </Button>
          )}
          {answers.length > 2 && (
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => removeAnswer(answers.length - 1)}
            >
              <MinusIcon className="icon-sm" />
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
    <form onSubmit={onSubmit} className="form-root">
      <Input placeholder={t("quiz.title")} {...register("title")} />
      <div className="stack">
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
