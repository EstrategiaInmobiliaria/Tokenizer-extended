import { type NextPage } from "next";
import Head from "next/head";
import { PolynomialLesson } from "~/sections/polynomial/PolynomialLesson";

const PolynomialTimePage: NextPage = () => {
  return (
    <>
      <Head>
        <title>Tiempo polinómico · laboratorio visual</title>
        <meta
          name="description"
          content="Simulación interactiva para entender y explicar el tiempo polinómico con gráficos, movimiento y medidas reales."
        />
      </Head>
      <main className="min-h-screen bg-slate-50">
        <PolynomialLesson />
      </main>
    </>
  );
};

export default PolynomialTimePage;
