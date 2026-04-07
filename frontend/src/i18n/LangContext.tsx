import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";
import { translations } from "./translations";
import type { Lang } from "./translations";

interface LangContextType {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: string) => string;
}

const LangContext = createContext<LangContextType>({
  lang: "es",
  setLang: () => {},
  t: (key) => key,
});

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(
    () => (localStorage.getItem("floraflow-lang") as Lang) || "es"
  );

  const switchLang = (l: Lang) => {
    setLang(l);
    localStorage.setItem("floraflow-lang", l);
  };

  const t = (key: string) => translations[lang][key] || key;

  return (
    <LangContext.Provider value={{ lang, setLang: switchLang, t }}>
      {children}
    </LangContext.Provider>
  );
}

export const useLang = () => useContext(LangContext);
