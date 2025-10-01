module.exports = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0b7285",
          dark: "#0a4a57",
          light: "#d0f4ff"
        }
      }
    }
  },
  plugins: [require("@tailwindcss/typography")]
};
