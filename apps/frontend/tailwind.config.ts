import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Sora", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      colors: {
        surface: "hsl(var(--surface))",
        card: "hsl(var(--card))",
        ink: "hsl(var(--ink))",
        accent: "hsl(var(--accent))",
        calm: "hsl(var(--calm))",
      },
      boxShadow: {
        aura: "0 10px 40px -18px rgba(0, 0, 0, 0.45)",
      },
      backgroundImage: {
        "hero-mesh":
          "radial-gradient(circle at 20% -10%, rgba(244, 113, 61, 0.35), transparent 35%), radial-gradient(circle at 85% 0%, rgba(20, 184, 166, 0.3), transparent 45%)",
      },
    },
  },
  plugins: [],
};

export default config;
