import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        headline: ["Newsreader", "serif"],
        body: ["Plus Jakarta Sans", "sans-serif"],
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Landing page colors (orange palette)
        "landing-primary": "#c24e2c",
        "landing-primary-container": "#e86b4a",
        "landing-primary-fixed": "#ffdbd0",
        "landing-on-primary-fixed-variant": "#7a2f15",
        "landing-secondary": "#645d56",
        "landing-tertiary": "#7c5730",
        "landing-background": "#fafaf9",
        "landing-surface": "#faf9f7",
        "landing-surface-variant": "#e3e2e0",
        "landing-surface-container-low": "#f4f3f1",
        "landing-on-background": "#1a1c1b",
        "landing-on-surface": "#1a1c1b",
        "landing-outline": "#88726c",
        "landing-outline-variant": "#dbc1b9",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      boxShadow: {
        startup: "0 8px 30px rgba(0,0,0,0.04), 0 0 1px rgba(0,0,0,0.1)",
        "startup-hover":
          "0 20px 40px rgba(0,0,0,0.06), 0 0 1px rgba(0,0,0,0.1)",
      },
    },
  },
  plugins: [],
};

export default config;
