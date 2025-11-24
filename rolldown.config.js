import { defineConfig } from "rolldown";
import svelte from "rollup-plugin-svelte";
import postcss from "rollup-plugin-postcss";
import tailwindcss from "@tailwindcss/postcss";
import { sveltePreprocess } from "svelte-preprocess";

export default defineConfig({
  input: "./web/index.js",
  output: {
    dir: "./src/db_schema_viz/static/",
  },
  plugins: [
    postcss({
      extract: true,
      plugins: [tailwindcss()],
    }),
    svelte({
      preprocess: sveltePreprocess(),
      compilerOptions: { runes: true }
    }),
  ],
});
