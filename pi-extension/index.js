// Pi agent harness extension for the SEO Content Pipeline.
//
// Pi loads this as a built-in extension.  It registers the
// pipeline as a system-level tool so any agent running inside
// Pi can invoke keyword research → scraping → analysis → drafting.
//
// Canonical instructions: AGENTS.md at the repo root.

import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

const PIPELINE_INSTRUCTIONS = readFileSync(
  resolve(ROOT, "AGENTS.md"),
  "utf-8",
);

export default {
  id: "seo-pipeline",
  name: "SEO Content Pipeline",
  version: "0.3.0",
  description: "4-stage SEO content pipeline: keyword research → competitor scraping → SEO gap analysis → article drafting.",

  async onSessionStart(session) {
    session.tools.push({
      name: "run-seo-pipeline",
      description: "Run the full 4-stage SEO content pipeline for a topic",
      parameters: {
        type: "object",
        properties: {
          topic: {
            type: "string",
            description: "The business domain or keyword topic",
          },
          stage: {
            type: "string",
            enum: ["all", "research", "scrape", "analyze", "draft"],
            description: "Pipeline stage to run (default: all)",
          },
        },
        required: ["topic"],
      },
      async handler({ topic, stage }) {
        return {
          type: "system",
          content: `Running SEO pipeline for "${topic}" (stage: ${stage || "all"}).\n\n${PIPELINE_INSTRUCTIONS}`,
        };
      },
    });
  },
};
