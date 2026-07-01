// seo-pipeline — OpenCode plugin.
//
// Registers the pipeline as an OpenCode server plugin so the 4-stage workflow
// is available in every chat session without manually loading AGENTS.md.
//
// Add to opencode.json:
//   { "plugin": ["@attaxa/seo-pipeline"] }
//
// Canonical pipeline instructions live in AGENTS.md at the project root.

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "../..");

export default function ({ registerCommand }) {
  registerCommand({
    name: "seo-pipeline",
    description: "4-stage SEO content pipeline: research → scrape → analyze → draft",
    async handler(args) {
      const agentsMd = fs.readFileSync(
        path.join(root, "AGENTS.md"),
        "utf-8"
      );
      const topic = args?.join(" ") || "";
      return {
        type: "system",
        content: `Follow the SEOP pipeline for ${topic || "the configured domain"}.\n\n${agentsMd}`,
      };
    },
  });
}
