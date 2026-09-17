import { env } from "~/env.mjs";
import { openSourceModels, tempLlama3HackGetRevision } from "~/models";
import { promises as fs } from "fs";
import { resolve } from "path";
import { z } from "zod";

async function download() {
  for (const modelName of Object.values(openSourceModels.Values)) {
    const [orgId, modelId] = z
      .tuple([z.string(), z.string()])
      .parse(modelName.split("/"));

    const rev = tempLlama3HackGetRevision(modelName);

    for (const file of ["tokenizer.json", "tokenizer_config.json"]) {
      const targetDir = resolve("public/hf", orgId, modelId);
      const targetPath = resolve(targetDir, file);

      if (await fs.stat(targetPath).catch(() => null)) {
        console.log("Skipping", targetPath);
        continue;
      }

      try {
        // eg https://huggingface.co/codellama/CodeLlama-7b-hf/resolve/main/tokenizer.json
        const headers: Record<string, string> = {
          ContentType: "application/json",
        };
        
        if (env.HF_API_KEY) {
          headers.Authorization = `Bearer ${env.HF_API_KEY}`;
        }

        const res = await fetch(
          `https://huggingface.co/${orgId}/${modelId}/resolve/${encodeURIComponent(
            rev
          )}/${file}`,
          { headers }
        );

        if (!res.ok) {
          console.warn(
            `Warning: Failed to fetch ${file} for ${modelName} (HTTP ${res.status}). This model may require authentication or may not be publicly accessible. Skipping...`
          );
          continue;
        }

        await fs.mkdir(targetDir, { recursive: true });
        console.log("Writing to", targetPath);
        await fs.writeFile(targetPath, await res.text());
      } catch (error) {
        console.warn(
          `Warning: Failed to download ${file} for ${modelName}:`,
          error instanceof Error ? error.message : String(error),
          "Skipping..."
        );
      }
    }
  }
}

download();
