import fs from "node:fs";
import path from "node:path";
import { generateHashedLink } from "@calcom/lib/generateHashedLink";
import { randomString } from "@calcom/lib/random";
import prisma from "@calcom/prisma";
import { BookingStatus } from "@calcom/prisma/enums";
import { expect } from "@playwright/test";
import { v4 as uuidv4 } from "uuid";

import { test } from "./lib/fixtures";
import {
  bookTimeSlot,
  createUserWithSeatedEventAndAttendees,
  selectFirstAvailableTimeSlotNextMonth,
} from "./lib/testUtils";

type ProbeResult = {
  actorRole: string;
  artifactPaths: string[];
  expectedStatus: number;
  failureDetail: string;
  invariantId: string;
  networkResponses: Array<{ status: number; url: string }>;
  observedStatus: number;
  passed: boolean;
  route: string;
  selector: string;
  source: "microsoft-playwright";
  targetUrl: string;
  timestamp: string;
  title: string;
};

type ProbeProposal = {
  connectorAction?: string | null;
  expectedStatus: number;
  invariantId: string;
  mutatedParams?: Record<string, string | null>;
  mutationId?: string;
  path?: string | null;
  proposalId: string;
  proposalKind?: string;
  routePattern: string;
  sequenceSteps?: Array<{
    connectorAction: string;
    params?: Record<string, string>;
  }>;
  sourceParam?: string | null;
  sourceText?: string;
  title: string;
};

const outputPath = process.env.BAYESILISK_CONTEXT_OUTPUT || "/private/tmp/calcom-bayesilisk-context.json";
const proposalInputPath = process.env.BAYESILISK_PROPOSALS_INPUT;

function loadProbeProposals() {
  if (!proposalInputPath) {
    return [];
  }
  const raw = JSON.parse(fs.readFileSync(proposalInputPath, "utf8"));
  return Array.isArray(raw) ? raw.filter((item): item is ProbeProposal => item && typeof item === "object") : [];
}

function buildContext(results: ProbeResult[], proposals: ProbeProposal[] = []) {
  const failures = results.filter((result) => !result.passed);
  const sourceSignals = [
    {
      availableActions: ["open-public-booking-page"],
      expectedBehavior: {
        description: "Unknown rescheduleUid must not silently degrade into a normal booking flow.",
        status: 404,
      },
      invariantId: "calcom.unknown_reschedule_uid_must_not_open_booking_flow",
      params: [
        { name: "rescheduleUid", kind: "id", location: "query", required: false },
        { name: "bookingUid", kind: "id", location: "query", required: false },
      ],
      path: "apps/web/playwright/booking-seats.e2e.ts",
      proposalRules: {
        rescheduleUid: [
          { id: "unknown-id", value: "missing-rescheduleUid" },
          { id: "stale-id", value: "stale-rescheduleUid" },
        ],
      },
      routePattern: "/{username}/{eventType}?rescheduleUid={rescheduleUid}&bookingUid=null",
      source: "repository-scan",
      title: "TODO says missing rescheduleUid should force 404",
      text: "Cal.com source signal: booking-seats.e2e.ts contains `@TODO: force 404 when rescheduleUid is not found`; nearby tests exercise direct seated-event reschedule with `rescheduleUid` and `bookingUid=null`.",
    },
    {
      availableActions: ["open-private-booking-link"],
      expectedBehavior: {
        description: "Unknown rescheduleUid on a private booking link must not silently open a new booking flow.",
        status: 404,
      },
      invariantId: "calcom.private_link_unknown_reschedule_uid_must_not_open_booking_flow",
      params: [{ name: "rescheduleUid", kind: "id", location: "query", required: false }],
      path: "apps/web/lib/d/[link]/[slug]/getServerSideProps.tsx",
      proposalRules: {
        rescheduleUid: [
          { id: "unknown-id", value: "missing-rescheduleUid" },
          { id: "stale-id", value: "stale-rescheduleUid" },
        ],
      },
      routePattern: "/d/{hashedLink}/{eventType}?rescheduleUid={rescheduleUid}",
      source: "repository-scan",
      title: "Private booking link resolves rescheduleUid into booking context",
      text: "Cal.com source signal: private booking link SSR validates the hashed link, then calls getBookingForReschedule when rescheduleUid is present before rendering booking props.",
    },
    {
      availableActions: ["open-dynamic-booking-page"],
      expectedBehavior: {
        description: "Unknown rescheduleUid on a dynamic booking page must not silently open a new group booking flow.",
        status: 404,
      },
      invariantId: "calcom.dynamic_booking_unknown_reschedule_uid_must_not_open_booking_flow",
      params: [{ name: "rescheduleUid", kind: "id", location: "query", required: false }],
      path: "apps/web/playwright/dynamic-booking-pages.e2e.ts",
      proposalRules: {
        rescheduleUid: [
          { id: "unknown-id", value: "missing-rescheduleUid" },
          { id: "stale-id", value: "stale-rescheduleUid" },
        ],
      },
      routePattern: "/{username}+{username}?rescheduleUid={rescheduleUid}",
      source: "repository-scan",
      title: "Dynamic booking page has a passing valid reschedule flow",
      text: "Cal.com source signal: dynamic booking tests use rescheduleUid for a valid group booking reschedule; stale or unknown reschedule context should not silently become a new group booking.",
    },
    {
      availableActions: ["create-booking", "cancel-booking", "open-public-booking-route"],
      expectedBehavior: {
        description: "A cancelled booking UID must not be reusable as a public rescheduleUid.",
        status: 409,
      },
      invariantId: "calcom.cancelled_booking_uid_cannot_be_replayed_as_public_reschedule",
      path: "apps/web/playwright/bayesilisk-probes.e2e.ts",
      routePattern: "create-booking -> cancel-booking -> open-public-booking-route",
      source: "repository-scan",
      title: "Cancelled booking UID replay through public booking route is rejected",
      text: "Cal.com connector action graph creates a booking, cancels it, then replays the cancelled booking UID through the public booking route as rescheduleUid.",
    },
  ];
  return {
    source: "calcom-playwright-probe",
    agentNotes:
      failures.length > 0
        ? failures.map(
            (result) =>
              `Cal.com probe \`${result.title}\`: expected semantic status ${result.expectedStatus}, observed ${result.observedStatus}; invariant \`${result.invariantId}\`; route \`${result.route}\`.`
          )
        : ["Cal.com Bayesilisk probe found no workflow/business-rule mismatches."],
    priorAdjustments: {},
    probeProposals: proposals,
    repositoryFacts: [...sourceSignals, ...results],
    playwrightProbe: {
      artifactCount: 0,
      failedCount: failures.length,
      passedCount: results.length - failures.length,
      resultCount: results.length,
      target: "cal.com local Playwright fixtures",
    },
  };
}

async function recordProbe(
  results: ProbeResult[],
  probe: {
    actorRole: string;
    expectedStatus: number;
    invariantId: string;
    route: string;
    title: string;
  },
  action: () => Promise<
    | boolean
    | {
        artifactPaths?: string[];
        failureDetail?: string;
        networkResponses?: Array<{ status: number; url: string }>;
        observedStatus?: number;
        passed: boolean;
        targetUrl?: string;
      }
  >
) {
  let observedStatus = 500;
  let failureDetail = "";
  let artifactPaths: string[] = [];
  let networkResponses: Array<{ status: number; url: string }> = [];
  let targetUrl = probe.route;
  try {
    const result = await action();
    if (typeof result === "boolean") {
      observedStatus = result ? probe.expectedStatus : 200;
    } else {
      artifactPaths = result.artifactPaths ?? [];
      failureDetail = result.failureDetail ?? "";
      networkResponses = result.networkResponses ?? [];
      observedStatus = result.observedStatus ?? (result.passed ? probe.expectedStatus : 200);
      targetUrl = result.targetUrl ?? targetUrl;
    }
  } catch (error) {
    failureDetail = error instanceof Error ? error.message : String(error);
  }
  results.push({
    ...probe,
    artifactPaths,
    failureDetail,
    networkResponses,
    observedStatus,
    passed: observedStatus === probe.expectedStatus,
    selector: "apps/web/playwright/bayesilisk-probes.e2e.ts",
    source: "microsoft-playwright",
    targetUrl,
    timestamp: new Date().toISOString(),
  });
}

async function executeWorkflowSequenceProposal(
  proposal: ProbeProposal,
  fixtures: {
    bookings: any;
    page: any;
    users: any;
  }
) {
  const state: Record<string, string | number | null> = {};
  let targetUrl = proposal.title;
  let networkResponses: Array<{ status: number; url: string }> = [];
  let bookingFormVisible = false;
  let blockedStateVisible = false;
  const steps = proposal.sequenceSteps ?? [];

  for (const step of steps) {
    if (step.connectorAction === "create-booking") {
      const user = await fixtures.users.create({ name: `Bayesilisk sequence ${proposal.proposalId}` });
      const [eventType] = user.eventTypes;
      const booking = await fixtures.bookings.create(user.id, user.username, eventType.id);
      state["booking.uid"] = booking.uid;
      state["booking.id"] = booking.id;
      state["eventType.slug"] = eventType.slug;
      state["user.username"] = user.username;
      continue;
    }

    if (step.connectorAction === "cancel-booking") {
      const bookingId = state["booking.id"];
      if (typeof bookingId !== "number") {
        throw new Error("cancel-booking requires booking.id from a previous step");
      }
      await prisma.booking.update({ where: { id: bookingId }, data: { status: BookingStatus.CANCELLED } });
      state["booking.status.cancelled"] = "true";
      continue;
    }

    if (step.connectorAction === "open-public-booking-route") {
      const username = state["user.username"];
      const eventTypeSlug = state["eventType.slug"];
      if (typeof username !== "string" || typeof eventTypeSlug !== "string") {
        throw new Error("open-public-booking-route requires user.username and eventType.slug");
      }
      const params = new URLSearchParams();
      for (const [paramName, stateKey] of Object.entries(step.params ?? {})) {
        const value = state[stateKey];
        if (typeof value === "string") {
          params.set(paramName, value);
        }
      }
      params.set("bookingUid", "null");
      const response = await fixtures.page.goto(`/${username}/${eventTypeSlug}?${params.toString()}`);
      targetUrl = fixtures.page.url();
      networkResponses = [{ status: response?.status() ?? 0, url: response?.url() ?? targetUrl }];
      bookingFormVisible = await fixtures.page.locator('[name="email"]').isVisible();
      blockedStateVisible =
        (await fixtures.page.locator('[data-testid="cancelled-headline"]').count()) > 0 ||
        (await fixtures.page.locator("[data-testid=success-page]").count()) > 0 ||
        (await fixtures.page.locator("text=This booking has been cancelled").count()) > 0;
      continue;
    }

    throw new Error(`Unsupported sequence connectorAction: ${step.connectorAction}`);
  }

  return {
    failureDetail: blockedStateVisible && !bookingFormVisible
      ? ""
      : `Bayesilisk-generated sequence replayed a cancelled booking UID as public rescheduleUid and reached ${targetUrl} with semantic status ${
          networkResponses[0]?.status ?? 200
        } instead of a blocked cancelled-booking state.`,
    networkResponses,
    observedStatus: blockedStateVisible && !bookingFormVisible ? proposal.expectedStatus : networkResponses[0]?.status ?? 200,
    passed: blockedStateVisible && !bookingFormVisible,
    targetUrl,
  };
}

test.describe.configure({ mode: "serial" });

test.afterEach(async ({ users }) => {
  await users.deleteAll();
});

test("Bayesilisk Cal.com workflow probes", async ({ page, users, bookings }) => {
  const results: ProbeResult[] = [];
  const proposals = loadProbeProposals();

  if (proposals.length) {
    for (const proposal of proposals) {
      if (proposal.proposalKind === "workflow-sequence") {
        await recordProbe(
          results,
          {
            actorRole: "attendee",
            expectedStatus: proposal.expectedStatus,
            invariantId: proposal.invariantId,
            route: (proposal.sequenceSteps ?? []).map((step) => step.connectorAction).join(" -> "),
            title: proposal.title,
          },
          async () => executeWorkflowSequenceProposal(proposal, { bookings, page, users })
        );
        continue;
      }
      if (
        proposal.connectorAction !== "open-public-booking-page" &&
        proposal.connectorAction !== "open-private-booking-link" &&
        proposal.connectorAction !== "open-dynamic-booking-page"
      ) {
        continue;
      }
      await recordProbe(
        results,
        {
          actorRole: "attendee",
          expectedStatus: proposal.expectedStatus,
          invariantId: proposal.invariantId,
          route: proposal.routePattern,
          title: proposal.title,
        },
        async () => {
          const user = await users.create({ name: `Bayesilisk proposal ${proposal.proposalId}` });
          const [eventType] = user.eventTypes;
          const proposedRescheduleUid = proposal.mutatedParams?.rescheduleUid;
          const rescheduleUid =
            typeof proposedRescheduleUid === "string" && proposedRescheduleUid
              ? proposedRescheduleUid
              : `missing-${randomString(12)}`;
          let targetUrl: string;
          if (proposal.connectorAction === "open-private-booking-link") {
            const eventWithPrivateLink = await prisma.eventType.update({
              where: { id: eventType.id },
              data: {
                hashedLink: {
                  create: [{ link: generateHashedLink(eventType.id) }],
                },
              },
              include: { hashedLink: true },
            });
            targetUrl = `/d/${eventWithPrivateLink.hashedLink[0]?.link}/${eventWithPrivateLink.slug}?rescheduleUid=${rescheduleUid}`;
          } else if (proposal.connectorAction === "open-dynamic-booking-page") {
            const secondUser = await users.create({ username: `bayesilisk-dynamic-${randomString(6)}` });
            targetUrl = `/${user.username}+${secondUser.username}?rescheduleUid=${rescheduleUid}`;
          } else {
            targetUrl = `/${user.username}/${eventType.slug}?rescheduleUid=${rescheduleUid}&bookingUid=null`;
          }
          const response = await page.goto(targetUrl);
          const bookingFormVisible = await page.locator('[name="email"]').isVisible();
          const pageLooksNotFound =
            (response?.status() ?? 200) === 404 ||
            (await page.locator("text=This event does not exist").count()) > 0 ||
            (await page.locator("text=404").count()) > 0;

          return {
            failureDetail: bookingFormVisible
              ? "Bayesilisk-proposed unknown reschedule identifier was ignored and the normal booking form was visible."
              : "",
            networkResponses: [{ status: response?.status() ?? 0, url: response?.url() ?? page.url() }],
            observedStatus: pageLooksNotFound && !bookingFormVisible ? 404 : response?.status() ?? 200,
            passed: pageLooksNotFound && !bookingFormVisible,
            targetUrl: page.url(),
          };
        }
      );
    }

    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, `${JSON.stringify(buildContext(results, proposals), null, 2)}\n`, "utf8");
    return;
  }

  await recordProbe(
    results,
    {
      actorRole: "organizer",
      expectedStatus: 409,
      invariantId: "calcom.cancelled_booking_cannot_be_rescheduled",
      route: "/reschedule/{cancelledBookingUid}",
      title: "Cancelled booking direct reschedule route is rejected",
    },
    async () => {
      const user = await users.create({ name: "Bayesilisk cancelled booking" });
      const [eventType] = user.eventTypes;
      const booking = await bookings.create(user.id, user.username, eventType.id);
      await prisma.booking.update({ where: { id: booking.id }, data: { status: BookingStatus.CANCELLED } });

      await page.goto(`/reschedule/${booking.uid}`);
      await expect(page.locator('[data-testid="cancelled-headline"]')).toBeVisible();
      return !page.url().includes("rescheduleUid");
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "attendee",
      expectedStatus: 409,
      invariantId: "calcom.cancelled_booking_uid_cannot_be_replayed_as_public_reschedule",
      route: "/{username}/{eventType}?rescheduleUid={cancelledBookingUid}&bookingUid=null",
      title: "Cancelled booking UID replay through public booking route is rejected",
    },
    async () => {
      const user = await users.create({ name: "Bayesilisk cancelled booking replay" });
      const [eventType] = user.eventTypes;
      const booking = await bookings.create(user.id, user.username, eventType.id);
      await prisma.booking.update({ where: { id: booking.id }, data: { status: BookingStatus.CANCELLED } });

      const targetUrl = `/${user.username}/${eventType.slug}?rescheduleUid=${booking.uid}&bookingUid=null`;
      const response = await page.goto(targetUrl);
      const bookingFormVisible = await page.locator('[name="email"]').isVisible();
      const blockedStateVisible =
        (await page.locator('[data-testid="cancelled-headline"]').count()) > 0 ||
        (await page.locator("[data-testid=success-page]").count()) > 0 ||
        (await page.locator("text=This booking has been cancelled").count()) > 0;

      return {
        failureDetail: bookingFormVisible
          ? "A cancelled booking UID was accepted as a public rescheduleUid and the normal booking form was visible."
          : "",
        networkResponses: [{ status: response?.status() ?? 0, url: response?.url() ?? page.url() }],
        observedStatus: blockedStateVisible && !bookingFormVisible ? 409 : response?.status() ?? 200,
        passed: blockedStateVisible && !bookingFormVisible,
        targetUrl: page.url(),
      };
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "organizer",
      expectedStatus: 409,
      invariantId: "calcom.reschedule_uid_must_match_event_type",
      route: "/{username}/{wrongEventType}?rescheduleUid={bookingUid}",
      title: "Reschedule UID for another event type redirects to original event type",
    },
    async () => {
      const user = await users.create({ name: "Bayesilisk wrong event type" });
      const [originalEventType, wrongEventType] = user.eventTypes;
      const booking = await bookings.create(user.id, user.username, originalEventType.id);

      await page.goto(`/${user.username}/${wrongEventType.slug}?rescheduleUid=${booking.uid}`);
      await expect(page).toHaveURL(new RegExp(`${user.username}/${originalEventType.slug}`));
      return true;
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "attendee",
      expectedStatus: 409,
      invariantId: "calcom.disabled_event_type_blocks_cancellation",
      route: "/api/cancel",
      title: "Disabled cancellation event type rejects cancellation API",
    },
    async () => {
      const user = await users.create({
        name: "Bayesilisk no cancel",
        eventTypes: [
          {
            title: "No Cancel No Reschedule",
            slug: "no-cancel-no-reschedule",
            length: 30,
            disableCancelling: true,
            disableRescheduling: true,
          },
        ],
      });
      await page.goto(`/${user.username}/no-cancel-no-reschedule`);
      await selectFirstAvailableTimeSlotNextMonth(page);
      await bookTimeSlot(page, {
        name: "Bayesilisk Booker",
        email: users.trackEmail({ username: "bayesilisk-booker", domain: "example.com" }),
      });
      await expect(page.locator("[data-testid=success-page]")).toBeVisible();
      const bookingUid = new URL(page.url()).pathname.split("/").pop();
      const csrfTokenResponse = await page.request.get("/api/csrf");
      const { csrfToken } = await csrfTokenResponse.json();
      const response = await page.request.post("/api/cancel", {
        data: { uid: bookingUid, csrfToken },
        headers: { "Content-Type": "application/json" },
      });
      const body = await response.json();
      return response.status() === 400 && body.message === "This event type does not allow cancellations";
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "attendee",
      expectedStatus: 404,
      invariantId: "calcom.unknown_reschedule_uid_must_not_open_booking_flow",
      route: "/{username}/{eventType}?rescheduleUid={unknownUid}&bookingUid=null",
      title: "Unknown reschedule UID must not silently open the booking flow",
    },
    async () => {
      const user = await users.create({ name: "Bayesilisk unknown reschedule uid" });
      const [eventType] = user.eventTypes;
      const unknownRescheduleUid = `missing-${randomString(12)}`;

      const response = await page.goto(
        `/${user.username}/${eventType.slug}?rescheduleUid=${unknownRescheduleUid}&bookingUid=null`
      );
      const bookingFormVisible = await page.locator('[name="email"]').isVisible();
      const artifactPath = `/private/tmp/calcom-unknown-reschedule-${unknownRescheduleUid}.png`;
      const pageLooksNotFound =
        (response?.status() ?? 200) === 404 ||
        (await page.locator("text=This event does not exist").count()) > 0 ||
        (await page.locator("text=404").count()) > 0;

      if (bookingFormVisible) {
        await page.screenshot({ fullPage: true, path: artifactPath });
      }

      return {
        artifactPaths: bookingFormVisible ? [artifactPath] : [],
        failureDetail: bookingFormVisible
          ? "Unknown rescheduleUid was ignored and the normal booking form was visible."
          : "",
        networkResponses: [{ status: response?.status() ?? 0, url: response?.url() ?? page.url() }],
        observedStatus: pageLooksNotFound && !bookingFormVisible ? 404 : response?.status() ?? 200,
        passed: pageLooksNotFound && !bookingFormVisible,
        targetUrl: page.url(),
      };
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "attendee",
      expectedStatus: 404,
      invariantId: "calcom.dynamic_booking_unknown_reschedule_uid_must_not_open_booking_flow",
      route: "/{username}+{username}?rescheduleUid={unknownUid}",
      title: "Dynamic booking page must not ignore an unknown reschedule UID",
    },
    async () => {
      const pro = await users.create({ name: "Bayesilisk dynamic pro" });
      const free = await users.create({ username: `bayesilisk-free-${randomString(6)}` });
      const unknownRescheduleUid = `missing-${randomString(12)}`;
      const response = await page.goto(`/${pro.username}+${free.username}?rescheduleUid=${unknownRescheduleUid}`);
      const bookingFormVisible = await page.locator('[name="email"]').isVisible();
      const pageLooksNotFound =
        (response?.status() ?? 200) === 404 ||
        (await page.locator("text=This event does not exist").count()) > 0 ||
        (await page.locator("text=404").count()) > 0;

      return {
        failureDetail: bookingFormVisible
          ? "Unknown rescheduleUid on a dynamic booking page was ignored and the normal booking form was visible."
          : "",
        networkResponses: [{ status: response?.status() ?? 0, url: response?.url() ?? page.url() }],
        observedStatus: pageLooksNotFound && !bookingFormVisible ? 404 : response?.status() ?? 200,
        passed: pageLooksNotFound && !bookingFormVisible,
        targetUrl: page.url(),
      };
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "user",
      expectedStatus: 410,
      invariantId: "calcom.password_reset_old_token_invalidated",
      route: "/auth/forgot-password/{oldResetRequestId}",
      title: "Superseded password reset token must remain invalid",
    },
    async () => {
      const user = await users.create({ name: "Bayesilisk reset token" });

      for (let attempt = 0; attempt < 2; attempt += 1) {
        await page.goto("/auth/forgot-password");
        await page.waitForSelector("text=Forgot Password?");
        await page.fill('input[name="email"]', `${user.username}@example.com`);
        await page.press('input[name="email"]', "Enter");
        await page.waitForSelector("text=Reset link sent");
      }

      const requests = await prisma.resetPasswordRequest.findMany({
        where: { email: user.email },
        select: { id: true },
        orderBy: { createdAt: "asc" },
      });
      const oldRequest = requests[0];
      await page.goto(`/auth/forgot-password/${oldRequest.id}`);
      const whoopsVisible = await page.locator("text=Whoops").isVisible();

      return {
        failureDetail: whoopsVisible ? "" : "Superseded reset token did not render the expired/Whoops state.",
        networkResponses: [],
        observedStatus: whoopsVisible ? 410 : 200,
        passed: whoopsVisible,
        targetUrl: page.url(),
      };
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "attendee",
      expectedStatus: 404,
      invariantId: "calcom.private_link_unknown_reschedule_uid_must_not_open_booking_flow",
      route: "/d/{hashedLink}/{eventType}?rescheduleUid={unknownUid}",
      title: "Private booking link must not ignore an unknown reschedule UID",
    },
    async () => {
      const user = await users.create({ name: "Bayesilisk private link unknown reschedule uid" });
      const [eventType] = user.eventTypes;
      const eventWithPrivateLink = await prisma.eventType.update({
        where: { id: eventType.id },
        data: {
          hashedLink: {
            create: [{ link: generateHashedLink(eventType.id) }],
          },
        },
        include: { hashedLink: true },
      });
      const unknownRescheduleUid = `missing-${randomString(12)}`;
      const response = await page.goto(
        `/d/${eventWithPrivateLink.hashedLink[0]?.link}/${eventWithPrivateLink.slug}?rescheduleUid=${unknownRescheduleUid}`
      );
      const bookingFormVisible = await page.locator('[name="email"]').isVisible();
      const artifactPath = `/private/tmp/calcom-private-link-unknown-reschedule-${unknownRescheduleUid}.png`;
      const pageLooksNotFound =
        (response?.status() ?? 200) === 404 ||
        (await page.locator("text=This event does not exist").count()) > 0 ||
        (await page.locator("text=404").count()) > 0;

      if (bookingFormVisible) {
        await page.screenshot({ fullPage: true, path: artifactPath });
      }

      return {
        artifactPaths: bookingFormVisible ? [artifactPath] : [],
        failureDetail: bookingFormVisible
          ? "Unknown rescheduleUid on a private booking link was ignored and the normal booking form was visible."
          : "",
        networkResponses: [{ status: response?.status() ?? 0, url: response?.url() ?? page.url() }],
        observedStatus: pageLooksNotFound && !bookingFormVisible ? 404 : response?.status() ?? 200,
        passed: pageLooksNotFound && !bookingFormVisible,
        targetUrl: page.url(),
      };
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "attendee",
      expectedStatus: 404,
      invariantId: "calcom.unknown_direct_reschedule_route_must_404",
      route: "/reschedule/{unknownUid}",
      title: "Unknown direct reschedule route must return not found",
    },
    async () => {
      const unknownRescheduleUid = `missing-${randomString(12)}`;
      const response = await page.goto(`/reschedule/${unknownRescheduleUid}`);
      const pageLooksNotFound =
        (response?.status() ?? 200) === 404 ||
        (await page.locator("text=This event does not exist").count()) > 0 ||
        (await page.locator("text=404").count()) > 0;

      return {
        failureDetail: pageLooksNotFound ? "" : "Unknown direct reschedule route did not render a not-found page.",
        networkResponses: [{ status: response?.status() ?? 0, url: response?.url() ?? page.url() }],
        observedStatus: pageLooksNotFound ? 404 : response?.status() ?? 200,
        passed: pageLooksNotFound,
        targetUrl: page.url(),
      };
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "attendee",
      expectedStatus: 403,
      invariantId: "calcom.seated_booking_random_seat_reference_cannot_cancel",
      route: "/booking/{bookingUid}?cancel=true&seatReferenceUid={unknownSeatReferenceUid}",
      title: "Random seat reference must not expose seated booking cancellation",
    },
    async () => {
      const { booking } = await createUserWithSeatedEventAndAttendees({ users, bookings }, [
        { name: "Bayesilisk Seat One", email: users.trackEmail({ username: "seat-one", domain: "example.com" }), timeZone: "Europe/Berlin" },
        { name: "Bayesilisk Seat Two", email: users.trackEmail({ username: "seat-two", domain: "example.com" }), timeZone: "Europe/Berlin" },
      ]);

      await page.goto(`/booking/${booking.uid}?cancel=true&seatReferenceUid=${uuidv4()}`);
      return (await page.locator("text=Cancel").count()) === 0;
    }
  );

  await recordProbe(
    results,
    {
      actorRole: "attendee",
      expectedStatus: 403,
      invariantId: "calcom.seated_booking_requires_seat_reference_for_attendee_cancellation",
      route: "/booking/{bookingUid}?cancel=true",
      title: "Seated booking cancellation requires a concrete seat reference",
    },
    async () => {
      const { booking } = await createUserWithSeatedEventAndAttendees({ users, bookings }, [
        { name: "Bayesilisk Seat Three", email: users.trackEmail({ username: "seat-three", domain: "example.com" }), timeZone: "Europe/Berlin" },
        { name: "Bayesilisk Seat Four", email: users.trackEmail({ username: "seat-four", domain: "example.com" }), timeZone: "Europe/Berlin" },
      ]);

      await page.goto(`/booking/${booking.uid}?cancel=true`);
      return (await page.locator("text=Cancel").count()) === 0 && (await page.locator("text=Login").count()) === 1;
    }
  );

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(buildContext(results), null, 2)}\n`, "utf8");
});
