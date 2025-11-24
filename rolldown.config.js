import { defineConfig } from "rolldown";
import svelte from "rollup-plugin-svelte";

export default defineConfig({
  input: "./web/index.js",
  output: {
    dir: "./src/db_schema_viz/static/",
  },
  plugins: [
    svelte({ compilerOptions: { runes: true } }),
  ],
});
