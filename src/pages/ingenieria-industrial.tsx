import { type NextPage } from "next";
import Head from "next/head";
import { StudyGuide } from "~/sections/ie/StudyGuide";
import { BOOK } from "~/data/ieGuide";

const IngenieriaIndustrialPage: NextPage = () => {
  return (
    <>
      <Head>
        <title>
          {BOOK.title} · Guía de estudio ({BOOK.edition})
        </title>
        <meta
          name="description"
          content="Cronología, diagramas de flujo ASME y organigramas para estudiar Introducción a la Ingeniería Industrial."
        />
      </Head>
      <StudyGuide />
    </>
  );
};

export default IngenieriaIndustrialPage;
