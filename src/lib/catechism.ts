import catalog from "@/data/catechism.json";

export type Question = {
  id: string;
  section: string;
  question: string;
  answer: string;
  proofs: string[];
  prev: string | null;
  next: string | null;
  heidelberg: string[];
};

export type Catechism = {
  title: string;
  subtitle: string;
  author: string;
  year: number;
  place: string;
  sections: { id: number; title: string }[];
  questions: Question[];
  preface: string;
  prefaceTitle: string;
  niceneTitle: string;
  nicene: string;
  athanasianTitle: string;
  athanasian: string;
  appendixTitle: string;
  appendix: string;
};

export const catechism = catalog as Catechism;

export function getQuestion(id: string): Question | undefined {
  return catechism.questions.find((q) => q.id === id);
}

export function questionsBySection() {
  const groups: { title: string; questions: Question[] }[] = [];
  for (const q of catechism.questions) {
    const last = groups[groups.length - 1];
    if (!last || last.title !== q.section) {
      groups.push({ title: q.section, questions: [q] });
    } else {
      last.questions.push(q);
    }
  }
  return groups;
}
