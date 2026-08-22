// Sends one Langfuse OTLP trace span per agent turn (prompt -> final response).
// No-ops when LANGFUSE_PUBLIC_KEY/LANGFUSE_SECRET_KEY aren't set to real values,
// so this is safe to ship even before ~/.config/langfuse/env is filled in.
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { randomBytes } from "node:crypto";
import { appendFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";

const LOG_PATH = join(homedir(), ".pi", "agent", "langfuse-extension.log");

function textOf(content: unknown): string {
  if (!Array.isArray(content)) return "";
  return content
    .filter((block: any) => block && block.type === "text" && typeof block.text === "string")
    .map((block: any) => block.text)
    .join("\n");
}

async function log(line: string) {
  try {
    await appendFile(LOG_PATH, `${new Date().toISOString()} ${line}\n`);
  } catch {}
}

export default function (pi: ExtensionAPI) {
  const publicKey = process.env.LANGFUSE_PUBLIC_KEY;
  const secretKey = process.env.LANGFUSE_SECRET_KEY;
  const baseUrl = process.env.LANGFUSE_BASE_URL || process.env.LANGFUSE_HOST;

  if (
    !publicKey ||
    !secretKey ||
    !baseUrl ||
    publicKey.includes("REPLACE_ME") ||
    secretKey.includes("REPLACE_ME")
  ) {
    return;
  }

  const authHeader = `Basic ${Buffer.from(`${publicKey}:${secretKey}`).toString("base64")}`;
  const endpoint = `${baseUrl.replace(/\/+$/, "")}/api/public/otel/v1/traces`;

  type PendingTurn = { traceId: string; spanId: string; prompt: string; startNs: bigint };
  const turns = new Map<string, PendingTurn>();
  let currentModel = "unknown";

  const nowNs = () => BigInt(Date.now()) * 1_000_000n;
  const attr = (key: string, value: string) => ({ key, value: { stringValue: value } });

  async function sendSpan(params: {
    traceId: string;
    spanId: string;
    sessionId: string;
    startNs: bigint;
    endNs: bigint;
    model: string;
    input: string;
    output: string;
    usage?: Record<string, number>;
  }) {
    const attributes = [
      attr("langfuse.trace.name", "pi-coding-agent"),
      attr("langfuse.session.id", params.sessionId),
      attr("langfuse.observation.type", "generation"),
      attr("langfuse.observation.model.name", params.model),
      attr("gen_ai.request.model", params.model),
      attr("langfuse.observation.input", JSON.stringify(params.input)),
      attr("gen_ai.prompt", params.input),
      attr("langfuse.observation.output", JSON.stringify(params.output)),
      attr("gen_ai.completion", params.output),
    ];
    if (params.usage) {
      attributes.push(attr("langfuse.observation.usage_details", JSON.stringify(params.usage)));
    }

    const body = {
      resourceSpans: [
        {
          resource: { attributes: [attr("service.name", "pi-coding-agent")] },
          scopeSpans: [
            {
              scope: { name: "pi-langfuse-extension" },
              spans: [
                {
                  traceId: params.traceId,
                  spanId: params.spanId,
                  name: "pi-turn",
                  startTimeUnixNano: params.startNs.toString(),
                  endTimeUnixNano: params.endNs.toString(),
                  attributes,
                },
              ],
            },
          ],
        },
      ],
    };

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          Authorization: authHeader,
          "Content-Type": "application/json",
          "x-langfuse-ingestion-version": "4",
        },
        body: JSON.stringify(body),
      });
      if (!res.ok) await log(`send failed: ${res.status} ${await res.text()}`);
    } catch (err) {
      await log(`send error: ${err instanceof Error ? err.message : String(err)}`);
    }
  }

  pi.on("model_select", async (event: any) => {
    if (event?.model?.id) currentModel = `${event.model.provider}/${event.model.id}`;
  });

  pi.on("before_agent_start", async (event: any, ctx: any) => {
    const sessionId = ctx?.sessionManager?.getSessionId?.() ?? "unknown-session";
    turns.set(sessionId, {
      traceId: randomBytes(16).toString("hex"),
      spanId: randomBytes(8).toString("hex"),
      prompt: event.prompt ?? "",
      startNs: nowNs(),
    });
  });

  pi.on("agent_end", async (event: any, ctx: any) => {
    const sessionId = ctx?.sessionManager?.getSessionId?.() ?? "unknown-session";
    const turn = turns.get(sessionId);
    if (!turn) return;
    turns.delete(sessionId);

    const assistantMessages = (event.messages ?? []).filter((m: any) => m.role === "assistant");
    const output = assistantMessages.map((m: any) => textOf(m.content)).join("\n");
    const usage = assistantMessages.reduce((acc: Record<string, number>, m: any) => {
      const u = m.usage;
      if (!u) return acc;
      acc.inputTokens = (acc.inputTokens ?? 0) + (u.inputTokens ?? 0);
      acc.outputTokens = (acc.outputTokens ?? 0) + (u.outputTokens ?? 0);
      acc.cost = (acc.cost ?? 0) + (u.cost?.total ?? 0);
      return acc;
    }, {});

    await sendSpan({
      traceId: turn.traceId,
      spanId: turn.spanId,
      sessionId,
      startNs: turn.startNs,
      endNs: nowNs(),
      model: currentModel,
      input: turn.prompt,
      output,
      usage: Object.keys(usage).length ? usage : undefined,
    });
  });
}
