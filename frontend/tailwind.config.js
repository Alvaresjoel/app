/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#57564F",      // Custom primary color
        secondary: "#7A7A73",    // Custom secondary color
        accent1: "#DDDAD0",       // Custom accent color
        accent2: "#F8F3CE", 

      },
    },
  },
  plugins: [],
}

