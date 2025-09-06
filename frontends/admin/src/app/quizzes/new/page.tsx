"use client";

import { useTranslation } from "react-i18next";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
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
  questionsLength: number;
  appendQuestion: () => void;
  removeQuestion: (index: number) => void;
};

function QuestionFields({
  index,
  control,
  register,
  t,
  questionsLength,
  appendQuestion,
  removeQuestion,
}: QuestionFieldsProps) {
  const {
    fields: answers,
    append: appendAnswer,
    remove: removeAnswer,
  } = useFieldArray({
    control,
    name: `questions.${index}.options` as const,
  });

  return (
    <div className="space-y-2">
      <div className="flex items-end gap-2">
        <div className="flex-grow">
          <label className="block mb-1">
            {t("quiz.question")} #{index + 1}
          </label>
          <Input {...register(`questions.${index}.text` as const)} />
        </div>
        <div>
          <label className="block mb-1">{t("quiz.time_limit")}</label>
          <Input
            type="number"
            min={10}
            max={60}
            {...register(`questions.${index}.time_limit_s` as const, {
              valueAsNumber: true,
            })}
            className="w-24"
          />
        </div>
        {questionsLength < 20 && index === questionsLength - 1 && (
          <Button type="button" variant="outline" onClick={appendQuestion}>
            +
          </Button>
        )}
        {questionsLength > 2 && (
          <Button
            type="button"
            variant="outline"
            onClick={() => removeQuestion(index)}
          >
            -
          </Button>
        )}
      </div>
      <div className="space-y-2">
        <label className="block mb-1">{t("quiz.answer")}</label>
        {answers.map((ansField, ansIndex) => (
          <div key={ansField.id} className="flex items-center gap-2">
            <Input
              className="flex-grow"
              {...register(
                `questions.${index}.options.${ansIndex}.text` as const
              )}
            />
            <input
              type="radio"
              value={ansIndex}
              {...register(`questions.${index}.correct` as const, {
                valueAsNumber: true,
              })}
              aria-label={t("quiz.correct")}
            />
            {answers.length < 5 && ansIndex === answers.length - 1 && (
              <Button
                type="button"
                variant="outline"
                onClick={() => appendAnswer({ text: "" })}
              >
                +
              </Button>
            )}
            {answers.length > 2 && (
              <Button
                type="button"
                variant="outline"
                onClick={() => removeAnswer(ansIndex)}
              >
                -
              </Button>
            )}
          </div>
        ))}
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
      <div>
        <label className="block mb-1">{t("quiz.title")}</label>
        <Input {...register("title")} />
      </div>
      <div className="space-y-6">
        {fields.map((field, index) => (
          <QuestionFields
            key={field.id}
            index={index}
            control={control}
            register={register}
            t={t}
            questionsLength={fields.length}
            appendQuestion={() =>
              append({
                text: "",
                time_limit_s: 20,
                options: [{ text: "" }, { text: "" }],
                correct: 0,
              })
            }
            removeQuestion={remove}
          />
        ))}
      </div>
      <Button type="submit">{t("quiz.new")}</Button>
    </form>
  );
}
