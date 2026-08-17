import { useMemo, useState } from "react";
import { QUIZ } from "~/data/ieGuide";
import { cn } from "~/utils/cn";

export function IeQuiz() {
  const [answers, setAnswers] = useState<Array<number | null>>(
    () => QUIZ.map(() => null)
  );
  const [submitted, setSubmitted] = useState(false);

  const score = useMemo(() => {
    return QUIZ.reduce((total, item, index) => {
      return total + (answers[index] === item.answer ? 1 : 0);
    }, 0);
  }, [answers]);

  return (
    <section id="cuestionario" className="scroll-mt-24">
      <header className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-widest text-teal-700">
          Autoevaluación
        </p>
        <h2 className="mt-1 text-3xl font-bold text-slate-900">
          Cuestionario de los tres pilares
        </h2>
        <p className="mt-2 max-w-3xl text-slate-600">
          Comprueba simbología ASME, pensadores y estructuras. No sustituye los
          casos del libro: es un filtro rápido antes de un examen o una
          exposición.
        </p>
      </header>

      <ol className="space-y-6">
        {QUIZ.map((item, questionIndex) => (
          <li
            key={item.question}
            className="rounded-xl border border-slate-200 bg-white p-4"
          >
            <p className="font-medium text-slate-900">
              {questionIndex + 1}. {item.question}
            </p>
            <div className="mt-3 grid gap-2">
              {item.options.map((option, optionIndex) => {
                const selected = answers[questionIndex] === optionIndex;
                const isCorrect = optionIndex === item.answer;
                const showResult = submitted && selected;
                return (
                  <label
                    key={option}
                    className={cn(
                      "flex cursor-pointer items-start gap-2 rounded-lg border px-3 py-2 text-sm",
                      selected
                        ? "border-teal-600 bg-teal-50"
                        : "border-slate-200 hover:bg-slate-50",
                      submitted && isCorrect && "border-emerald-600 bg-emerald-50",
                      showResult && !isCorrect && "border-rose-400 bg-rose-50"
                    )}
                  >
                    <input
                      type="radio"
                      className="mt-1"
                      name={`q-${questionIndex}`}
                      checked={selected}
                      onChange={() => {
                        setSubmitted(false);
                        setAnswers((current) =>
                          current.map((value, index) =>
                            index === questionIndex ? optionIndex : value
                          )
                        );
                      }}
                    />
                    <span>{option}</span>
                  </label>
                );
              })}
            </div>
            {submitted ? (
              <p className="mt-3 text-sm text-slate-600">
                <span className="font-semibold">Por qué: </span>
                {item.why}
              </p>
            ) : null}
          </li>
        ))}
      </ol>

      <div className="mt-6 flex flex-wrap items-center gap-4">
        <button
          type="button"
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
          onClick={() => setSubmitted(true)}
        >
          Calificar
        </button>
        <button
          type="button"
          className="rounded-md border border-slate-300 px-4 py-2 text-sm hover:bg-slate-50"
          onClick={() => {
            setAnswers(QUIZ.map(() => null));
            setSubmitted(false);
          }}
        >
          Reiniciar
        </button>
        {submitted ? (
          <p className="text-sm font-medium text-slate-800">
            Resultado: {score} / {QUIZ.length}
          </p>
        ) : null}
      </div>
    </section>
  );
}
