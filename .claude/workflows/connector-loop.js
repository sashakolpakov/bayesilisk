export const meta = {
  name: 'connector-loop',
  description: 'Drive the Bayesilisk closed connector loop against a locally-running app until convergence',
  whenToUse: 'When a target app is running locally (dev/staging only) and you want Bayesilisk to scan it, bind motifs, and fully drive the scan->execute->verify->repair loop hands-off, with Bayesilisk as the deterministic gate.',
  phases: [
    { title: 'Init', detail: 'scan/bind via the loop CLI to get the connector directive + proposals' },
    { title: 'Drive', detail: 'per round: execute the connector against the app, then verify via the loop CLI' },
  ],
}

// Config via args (all optional):
//   { spec?, source?, appBaseUrl?, serveCommand?, statePath?, workDir?, maxRounds?, license?, packs? }
// One of spec/source identifies what to probe. The app must already be running at
// appBaseUrl unless serveCommand is given (an agent starts it in the background).
const cfg = (args && typeof args === 'object') ? args : {}
const workDir = cfg.workDir || '/tmp/bayesilisk-loop'
const statePath = cfg.statePath || `${workDir}/state.json`
const stepPath = `${workDir}/step.json`
const observedPath = `${workDir}/observed-context.json`
const appBaseUrl = cfg.appBaseUrl || 'http://localhost:3000'
const maxRounds = cfg.maxRounds || 6
const startFlag = cfg.spec ? `--spec ${cfg.spec}` : (cfg.source ? `--source ${cfg.source}` : '')
const packFlags = (cfg.packs || []).map((p) => `--pack ${p}`).join(' ')
const licenseFlag = cfg.license ? `--license ${cfg.license}` : ''

const STEP_SCHEMA = {
  type: 'object',
  required: ['phase'],
  properties: {
    phase: { type: 'string', description: 'await-connector | repair | await-execution | converged | blocked | start' },
    nextAction: { type: 'string' },
    newFindingCount: { type: 'integer' },
    issuePayloadCount: { type: 'integer' },
    proposalCount: { type: 'integer' },
    blockedErrors: { type: 'array', items: { type: 'string' } },
  },
}

const EXEC_SCHEMA = {
  type: 'object',
  required: ['factCount'],
  properties: {
    factCount: { type: 'integer', description: 'observed facts written' },
    notes: { type: 'string' },
  },
}

const LOOP_CLI = (extra) =>
  `python3 -m bayesilisk connector loop --state ${statePath} ${packFlags} ${licenseFlag} ${extra} --output ${stepPath}`

phase('Init')
if (!startFlag) {
  log('No spec/source provided in args; pass {spec: "openapi.json"} or {source: "source-context.json"}.')
  return { phase: 'blocked', reason: 'no spec or source' }
}
if (cfg.serveCommand) {
  await agent(
    `Start the local target app for Bayesilisk probing. Create ${workDir} if needed, then run this in the background and confirm it is reachable at ${appBaseUrl}: \`${cfg.serveCommand}\`. Local/dev/staging only. Return when the base URL responds.`,
    { label: 'serve-app', phase: 'Init' },
  )
}

let step = await agent(
  `Run exactly: \`mkdir -p ${workDir} && ${LOOP_CLI(startFlag)}\`. Then read ${stepPath} and return {phase, nextAction, proposalCount: (its proposals length or 0)}. Do not modify Bayesilisk core.`,
  { schema: STEP_SCHEMA, label: 'loop:init', phase: 'Init' },
)
log(`init: ${step.phase} (${step.proposalCount || 0} proposals)`)

phase('Drive')
let round = 0
while (step.phase !== 'converged' && step.phase !== 'blocked' && round < maxRounds) {
  round++

  // Execute step — the only thing Bayesilisk cannot do. Real actions only; never fabricate status.
  const exec = await agent(
    [
      `You are a Bayesilisk connector executor for round ${round}. Read the proposed probes from ${stepPath} (field .proposals; each has connectorAction, routePattern, params/mutatedParams, expectedStatus, invariantId).`,
      `For EACH proposal, perform the REAL action against the locally-running app at ${appBaseUrl} (HTTP request or Playwright), using the app's own fixtures/auth as needed. Observe the REAL response status.`,
      `Write ${observedPath} as a Bayesilisk observed context: {"source":"connector-observation","repositoryFacts":[ ... ]}. One fact per executed proposal with fields: actorRole, artifactPaths [], expectedStatus (from the proposal), failureDetail, invariantId (from the proposal), networkResponses, observedStatus (the REAL status), passed (observedStatus===expectedStatus), route (the proposal routePattern), selector ("connector:"+connectorAction), source "connector-observation", targetUrl, timestamp (ISO-8601), title.`,
      `Hard rules: run only against ${appBaseUrl} (local/dev/staging) — never production; NEVER invent observedStatus or passed; do not edit Bayesilisk core; if a proposal cannot be executed, omit it rather than guessing. Return {factCount, notes}.`,
    ].join('\n'),
    { label: `execute:round-${round}`, phase: 'Drive' },
  )
  log(`round ${round}: executed ${exec ? exec.factCount : 0} fact(s)`)

  // Verify step — deterministic; Bayesilisk is the gate.
  step = await agent(
    `Run exactly: \`${LOOP_CLI(`--observed ${observedPath}`)}\`. Then read ${stepPath} and return {phase, nextAction, newFindingCount, issuePayloadCount: (its issuePayloads length or 0), blockedErrors: (observationValidation.errors or [])}.`,
    { schema: STEP_SCHEMA, label: `loop:verify-${round}`, phase: 'Drive' },
  )
  log(`round ${round}: ${step.phase} (+${step.newFindingCount || 0} new, ${step.issuePayloadCount || 0} total payloads)`)

  if (step.phase === 'blocked') {
    log(`blocked: ${(step.blockedErrors || []).slice(0, 3).join('; ')}`)
    break
  }
}

return {
  phase: step.phase,
  rounds: round,
  issuePayloadCount: step.issuePayloadCount || 0,
  statePath,
  note: 'Open issues only from the accumulated verified issue payloads; Bayesilisk verified, the agent executed.',
}
