import fs from "node:fs";

import { test } from "./lib/fixtures";

type AgentResponse = {
  raw: string;
  parsed: Record<string, unknown> | null;
};

const outputPath = process.env.BAYESILISK_LLM_AGENT_OUTPUT || "/private/tmp/calcom-llm-agent-oracle.json";
const appendOutput = process.env.BAYESILISK_LLM_AGENT_APPEND === "1";
const ollamaBaseUrl = process.env.BAYESILISK_OLLAMA_BASE_URL || "http://localhost:11434";
const model = process.env.BAYESILISK_LLM_AGENT_MODEL || "qwen2.5-coder:3b";

function parseJson(raw: string): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
  } catch {
    const match = raw.match(/\{[\s\S]*\}/);
    if (!match) return null;
    try {
      const parsed = JSON.parse(match[0]);
      return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
    } catch {
      return null;
    }
  }
}

async function askAgent(prompt: string): Promise<AgentResponse> {
  const response = await fetch(`${ollamaBaseUrl}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      stream: false,
      messages: [
        {
          role: "system",
          content:
            "You are an autonomous browser testing agent. Return only strict JSON. You are not allowed to call external tools.",
        },
        { role: "user", content: prompt },
      ],
    }),
  });
  const data = await response.json();
  const raw = String(data.message?.content ?? "");
  return { raw, parsed: parseJson(raw) };
}

test("LLM-agent-only oracle baseline for unknown rescheduleUid", async ({ page, users }) => {
  const user = await users.create({ name: "Bayesilisk LLM agent baseline" });
  const [eventType] = user.eventTypes;
  const unknownUid = "missing-agent-rescheduleUid";
  const candidateUrls = [
    `/${user.username}/${eventType.slug}`,
    `/${user.username}/${eventType.slug}?rescheduleUid=${unknownUid}&bookingUid=null`,
  ];

  const action = await askAgent(`Choose the single browser URL that best tests whether Cal.com rejects an unknown rescheduleUid.

Candidate URLs:
${candidateUrls.map((url, index) => `${index}: ${url}`).join("\n")}

Return JSON with keys: selectedIndex, reason, expectedStatus.`);

  const selectedIndex =
    typeof action.parsed?.selectedIndex === "number" &&
    action.parsed.selectedIndex >= 0 &&
    action.parsed.selectedIndex < candidateUrls.length
      ? action.parsed.selectedIndex
      : null;
  const selectedUrl = selectedIndex === null ? null : candidateUrls[selectedIndex];

  let observation: Record<string, unknown> = {
    error: "agent-did-not-select-a-valid-url",
    selectedUrl,
  };

  if (selectedUrl) {
    const response = await page.goto(selectedUrl);
    const bookingFormVisible = await page.locator('[name="email"]').isVisible();
    const notFoundTextCount =
      (await page.locator("text=This event does not exist").count()) + (await page.locator("text=404").count());
    observation = {
      selectedUrl,
      finalUrl: page.url(),
      httpStatus: response?.status() ?? null,
      bookingFormVisible,
      notFoundTextCount,
      title: await page.title(),
    };
  }

  const verdict = await askAgent(`You are judging this browser observation as the test oracle.

Invariant: an unknown rescheduleUid must not open a normal Cal.com booking flow. Expected semantic status is 404.

Observation JSON:
${JSON.stringify(observation, null, 2)}

Return JSON with keys: verdict, expectedStatus, observedStatus, reason.
Use verdict "pass" if the invariant held and "fail" if the invariant was violated.`);

  const expectedSemanticStatus = 404;
  const observedSemanticStatus =
    observation.bookingFormVisible === true ? 200 : observation.notFoundTextCount ? 404 : observation.httpStatus ?? null;
  const verifierVerdict = observedSemanticStatus === expectedSemanticStatus ? "pass" : "fail";
  const agentVerdict = typeof verdict.parsed?.verdict === "string" ? verdict.parsed.verdict : "invalid";

  const result = {
    model,
    task: "unknown-rescheduleUid-browser-driving-oracle-baseline",
    action,
    observation,
    verdict,
    deterministicCheck: {
      expectedSemanticStatus,
      observedSemanticStatus,
      verdict: verifierVerdict,
    },
    agentOracleMatchedDeterministicCheck: agentVerdict === verifierVerdict,
  };

  if (appendOutput) {
    fs.appendFileSync(outputPath, `${JSON.stringify(result)}\n`, "utf8");
  } else {
    fs.writeFileSync(
      outputPath,
      `${JSON.stringify(
        result,
        null,
        2
      )}\n`,
      "utf8"
    );
  }
});
