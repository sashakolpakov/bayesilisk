from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

VERSION = "bayesilisk.v1.2"

EXPENSE_REVIEW_ROUTE = "/api/expense-claims/{claimId}/review"
BILLING_EXPORT_ROUTE = "/api/billing/exports"
HR_DOCUMENT_ROUTE = "/api/hr/documents"
TRAVEL_FUNDING_REQUEST_ROUTE = "/api/travel/funding-requests"
TRAVEL_FUNDING_APPROVAL_ROUTE = "/api/travel/funding-requests/{requestId}/approve"

ROLE_ROUTE_MATRIX: dict[str, set[str]] = {
    EXPENSE_REVIEW_ROUTE: {"finance", "manager", "admin", "owner"},
    BILLING_EXPORT_ROUTE: {"finance", "admin", "owner", "superadmin"},
    HR_DOCUMENT_ROUTE: {"hr_manager", "admin", "owner"},
    TRAVEL_FUNDING_REQUEST_ROUTE: {"employee", "manager", "finance", "admin", "owner"},
    TRAVEL_FUNDING_APPROVAL_ROUTE: {"manager", "finance", "admin", "owner"},
}

LIST_FACT_KEYS = {
    "businessFlow",
    "expenseCategories",
    "expenseItemDates",
    "routes",
    "transportModes",
    "travelLegs",
}
BOOLEAN_OR_FACT_KEYS = {"billingExportRequested", "receiptRequired", "travelFundingRequested"}
BOOLEAN_AND_FACT_KEYS = {
    "allRequiredReceiptsUsable",
    "itineraryCoversExpenseDates",
    "segmentsChronological",
    "transportModesCoveredByItinerary",
}
NUMERIC_SUM_FACT_KEYS = {"requiredReceiptCount"}
FINGERPRINT_PATTERN = re.compile(r"bayesilisk:[0-9a-f]{16}")

CONTEXT_INVARIANT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "roles.route_matrix_allowed": (
        "403",
        "access",
        "actor",
        "permission",
        "role",
        "route",
        "scope",
    ),
    "roles.employee_self_review_forbidden": (
        "approve own",
        "employee self",
        "manager conflict",
        "self review",
        "self-review",
    ),
    "modules.expense_approval_requires_module_and_receipt": (
        "expense",
        "module",
        "receipt",
        "reimbursement",
        "travel expense",
    ),
    "dms.tenant_process_boundary": (
        "candidateid",
        "contractid",
        "dms",
        "document",
        "metadata",
        "process context",
        "source reference",
        "tenant",
    ),
    "support.takeover_session_required": (
        "expired",
        "support",
        "takeover",
    ),
    "billing.export_requires_role_and_module": (
        "accounting export",
        "billing",
        "export",
        "invoice",
    ),
    "hr.documents_customer_role_boundary": (
        "contract",
        "hr document",
        "hr documents",
        "onboarding",
        "personnel file",
        "recruiting",
    ),
    "travel.itinerary_chronology": (
        "airplane",
        "flight",
        "itinerary",
        "leg",
        "rental car",
        "train",
    ),
    "travel.funding_before_expense": (
        "approval",
        "funding",
        "request",
        "travel request",
    ),
    "travel.expense_items_match_itinerary": (
        "airplane",
        "category",
        "expense date",
        "itinerary",
        "rental car",
        "train",
        "transport",
    ),
}

CONTEXT_COLLECTION_KEYS = {
    "agentNotes",
    "agents",
    "issues",
    "openIssues",
    "pullRequests",
    "prs",
    "recentFailures",
    "repositoryFacts",
}


@dataclass(frozen=True)
class Fragment:
    id: str
    domain: str
    kind: str
    facts: dict[str, Any]
    summary: str
    complete_alone: bool = False


@dataclass(frozen=True)
class Invariant:
    id: str
    layer: str
    expected: str
    prior: float
    fail_likelihood: float
    pass_likelihood: float
    difficulty: str
    evaluator: Callable[[dict[str, Any]], tuple[bool, str]]


@dataclass(frozen=True)
class Scenario:
    id: str
    tone: str
    title: str
    fragment_ids: tuple[str, ...]
    invariant_ids: tuple[str, ...]
    generated: bool = False
    generation_basis: str = "catalog"


FRAGMENTS: tuple[Fragment, ...] = (
    Fragment(
        "role.employee_self",
        "HR",
        "actor",
        {"actorRole": "employee", "actorEmployeeId": "emp-001", "targetEmployeeId": "emp-001"},
        "Employee actor targets their own record.",
    ),
    Fragment(
        "role.finance",
        "Billing",
        "actor",
        {"actorRole": "finance", "actorEmployeeId": "emp-fin"},
        "Finance actor with review and export intent.",
    ),
    Fragment(
        "role.support_takeover_expired",
        "Support",
        "actor",
        {"actorRole": "support", "supportSessionActive": False, "supportSessionExpired": True},
        "Support actor has an expired takeover session.",
    ),
    Fragment(
        "module.expenses_on",
        "module entitlements",
        "entitlement",
        {"modules": {"expenses": True}},
        "Expenses module is enabled for the organization.",
    ),
    Fragment(
        "module.expenses_off",
        "module entitlements",
        "entitlement",
        {"modules": {"expenses": False}},
        "Expenses module is disabled for the organization.",
    ),
    Fragment(
        "module.travel_on",
        "module entitlements",
        "entitlement",
        {"modules": {"travel": True}},
        "Travel module is enabled.",
    ),
    Fragment(
        "module.billing_on",
        "module entitlements",
        "entitlement",
        {"modules": {"billing": True}},
        "Billing module is enabled.",
    ),
    Fragment(
        "route.travel_funding_request",
        "Travel",
        "route",
        {"routes": [TRAVEL_FUNDING_REQUEST_ROUTE], "travelFundingRequested": True},
        "Travel funding request route receives a request.",
    ),
    Fragment(
        "route.travel_funding_approve",
        "Travel",
        "route",
        {"routes": [TRAVEL_FUNDING_APPROVAL_ROUTE], "decision": "approve"},
        "Travel funding approval route receives an approve decision.",
    ),
    Fragment(
        "travel.funding_approved",
        "Travel",
        "data",
        {
            "businessFlow": ["travel funding request", "travel funding approval"],
            "fundingApprovedOn": "2026-06-09",
            "travelFundingApproved": True,
        },
        "Travel funding is approved before expenses are submitted.",
    ),
    Fragment(
        "travel.funding_missing",
        "Travel",
        "data",
        {
            "businessFlow": ["travel funding request without approval"],
            "travelFundingApproved": False,
        },
        "Travel funding request exists but has no approval.",
    ),
    Fragment(
        "route.expense_approve",
        "Expenses",
        "route",
        {"routes": [EXPENSE_REVIEW_ROUTE], "decision": "approve"},
        "Expense review endpoint receives an approve decision.",
    ),
    Fragment(
        "expense.receipt_missing",
        "Expenses",
        "data",
        {
            "allRequiredReceiptsUsable": False,
            "category": "hotel",
            "claimItemId": "item-hotel",
            "receiptRequired": True,
            "requiredReceiptCount": 1,
        },
        "Hotel claim item has no usable linked DMS receipt.",
    ),
    Fragment(
        "expense.rental_car",
        "Expenses",
        "data",
        {
            "allRequiredReceiptsUsable": True,
            "expenseCategories": ["rental_car"],
            "expenseItemDates": ["2026-06-11"],
            "expenseSubmittedOn": "2026-06-13",
            "receiptRequired": True,
            "requiredReceiptCount": 1,
            "transportModes": ["rental_car"],
        },
        "Rental car expense has a usable receipt and a trip-date service date.",
    ),
    Fragment(
        "expense.train_ticket",
        "Expenses",
        "data",
        {
            "allRequiredReceiptsUsable": True,
            "expenseCategories": ["train"],
            "expenseItemDates": ["2026-06-10"],
            "expenseSubmittedOn": "2026-06-13",
            "receiptRequired": True,
            "requiredReceiptCount": 1,
            "transportModes": ["train"],
        },
        "Train ticket expense has a usable receipt.",
    ),
    Fragment(
        "expense.airfare",
        "Expenses",
        "data",
        {
            "allRequiredReceiptsUsable": True,
            "expenseCategories": ["airplane"],
            "expenseItemDates": ["2026-06-12"],
            "expenseSubmittedOn": "2026-06-13",
            "receiptRequired": True,
            "requiredReceiptCount": 1,
            "transportModes": ["airplane"],
        },
        "Airplane ticket expense has a usable receipt.",
    ),
    Fragment(
        "dms.foreign_tenant_document",
        "DMS",
        "data",
        {"dmsDocumentStatus": "approved", "dmsProcess": "travel_expense", "documentTenantMatches": False},
        "DMS document belongs to another tenant.",
    ),
    Fragment(
        "dms.correct_receipt",
        "DMS",
        "data",
        {"dmsDocumentStatus": "approved", "dmsProcess": "travel_expense", "documentTenantMatches": True},
        "DMS receipt is tenant-scoped and approved for travel expense.",
    ),
    Fragment(
        "travel.legs_consistent_multimodal",
        "Travel",
        "data",
        {
            "itineraryCoversExpenseDates": True,
            "segmentsChronological": True,
            "transportModesCoveredByItinerary": True,
            "travelLegs": [
                {"end": "2026-06-10", "mode": "train", "start": "2026-06-10"},
                {"end": "2026-06-11", "mode": "rental_car", "start": "2026-06-11"},
                {"end": "2026-06-12", "mode": "airplane", "start": "2026-06-12"},
            ],
            "tripEndsOn": "2026-06-12",
            "tripStartsOn": "2026-06-10",
        },
        "Train, rental car, and airplane legs are chronological and cover expense dates.",
    ),
    Fragment(
        "travel.inconsistent_itinerary",
        "Travel",
        "data",
        {
            "itineraryCoversExpenseDates": False,
            "segmentsChronological": False,
            "transportModesCoveredByItinerary": False,
            "travelLegs": [
                {"end": "2026-06-12", "mode": "airplane", "start": "2026-06-12"},
                {"end": "2026-06-10", "mode": "train", "start": "2026-06-11"},
            ],
            "tripEndsOn": "2026-06-10",
            "tripStartsOn": "2026-06-12",
        },
        "Travel itinerary ends before it starts and contains non-chronological legs.",
    ),
    Fragment(
        "travel.mundane_itinerary",
        "Travel",
        "data",
        {
            "itineraryCoversExpenseDates": True,
            "segmentsChronological": True,
            "transportModesCoveredByItinerary": True,
            "travelLegs": [{"end": "2026-06-12", "mode": "train", "start": "2026-06-10"}],
            "tripEndsOn": "2026-06-12",
            "tripStartsOn": "2026-06-10",
        },
        "Travel itinerary is chronological.",
    ),
    Fragment(
        "billing.export_route",
        "Billing",
        "route",
        {"billingExportRequested": True, "routes": [BILLING_EXPORT_ROUTE]},
        "Billing export route is requested.",
    ),
    Fragment(
        "hr.payroll_file_route",
        "HR",
        "route",
        {"hrDocumentAction": "download", "routes": [HR_DOCUMENT_ROUTE], "targetEmployeeId": "emp-002"},
        "HR document route is requested for another employee.",
    ),
    Fragment(
        "creative.travel_expense_roundup",
        "Travel",
        "scenario",
        {"roundUpScenario": True, "scenarioIntent": "travel+expense+support+DMS composed from partial fragments"},
        "Creative round-up composes travel, expense, support, and DMS fragments.",
    ),
)


def has_route(facts: dict[str, Any], route: str) -> bool:
    return route in set(facts.get("routes", []))


def route_matrix_allowed(facts: dict[str, Any]) -> tuple[bool, str]:
    actor_role = facts.get("actorRole")
    routes = facts.get("routes", [])
    if not actor_role or not routes:
        return True, "no actor/route access pattern to evaluate"
    for route in routes:
        allowed_roles = ROLE_ROUTE_MATRIX.get(route)
        if allowed_roles is not None and actor_role not in allowed_roles:
            return False, f"role `{actor_role}` is not allowed to access `{route}`"
    return True, "actor role is allowed for all requested routes"


def expenses_module_and_receipt(facts: dict[str, Any]) -> tuple[bool, str]:
    if not has_route(facts, EXPENSE_REVIEW_ROUTE) or facts.get("decision") != "approve":
        return True, "not an expense approval route"
    if not facts.get("modules", {}).get("expenses", False):
        return False, "expense approval reached while expenses module is disabled or absent"
    if facts.get("receiptRequired") and not facts.get("allRequiredReceiptsUsable", facts.get("receiptUsable", True)):
        return False, "required receipt evidence is missing or unusable"
    return True, "expense approval has module entitlement and usable required receipts"


def employee_self_review_forbidden(facts: dict[str, Any]) -> tuple[bool, str]:
    if facts.get("decision") != "approve":
        return True, "not an approval decision"
    if facts.get("actorEmployeeId") and facts.get("actorEmployeeId") == facts.get("targetEmployeeId"):
        return False, "employee self-review would approve their own record"
    return True, "actor and target employee are separated"


def dms_tenant_boundary(facts: dict[str, Any]) -> tuple[bool, str]:
    if "documentTenantMatches" not in facts:
        return True, "no DMS document involved"
    if not facts.get("documentTenantMatches"):
        return False, "DMS document crosses tenant boundary"
    if facts.get("dmsDocumentStatus") not in {"approved", "accepted"}:
        return False, "DMS document status is not usable"
    return True, "DMS document is tenant-scoped and usable"


def support_takeover_active(facts: dict[str, Any]) -> tuple[bool, str]:
    if facts.get("actorRole") != "support":
        return True, "not a support actor"
    if not facts.get("supportSessionActive") or facts.get("supportSessionExpired"):
        return False, "support access lacks an active non-expired takeover session"
    return True, "support takeover session is active"


def billing_export_entitled(facts: dict[str, Any]) -> tuple[bool, str]:
    if not facts.get("billingExportRequested") and not has_route(facts, BILLING_EXPORT_ROUTE):
        return True, "not a billing export"
    if not facts.get("modules", {}).get("billing", False):
        return False, "billing export requested without billing module entitlement"
    if facts.get("actorRole") not in ROLE_ROUTE_MATRIX[BILLING_EXPORT_ROUTE]:
        return False, "billing export actor role is not allowed"
    return True, "billing export has module and role entitlement"


def hr_document_boundary(facts: dict[str, Any]) -> tuple[bool, str]:
    if facts.get("hrDocumentAction") is None and not has_route(facts, HR_DOCUMENT_ROUTE):
        return True, "not an HR document action"
    if facts.get("actorRole") not in ROLE_ROUTE_MATRIX[HR_DOCUMENT_ROUTE]:
        return False, "HR document action requires HR/admin/customer owner role"
    return True, "HR document route has a customer HR/admin role"


def itinerary_consistent(facts: dict[str, Any]) -> tuple[bool, str]:
    if "tripStartsOn" not in facts:
        return True, "no itinerary involved"
    if facts.get("tripEndsOn") < facts.get("tripStartsOn") or not facts.get("segmentsChronological"):
        return False, "itinerary is inconsistent or non-chronological"
    return True, "itinerary dates and segments are chronological"


def travel_funding_before_expense(facts: dict[str, Any]) -> tuple[bool, str]:
    if not facts.get("expenseCategories") and not has_route(facts, EXPENSE_REVIEW_ROUTE):
        return True, "not a travel expense approval flow"
    if not facts.get("travelFundingApproved"):
        if facts.get("travelFundingRequested"):
            return False, "travel expense flow has a funding request but no approved funding"
        return False, "travel expense flow has no approved funding"
    if facts.get("expenseSubmittedOn") and facts.get("fundingApprovedOn"):
        if facts["expenseSubmittedOn"] < facts["fundingApprovedOn"]:
            return False, "travel expense was submitted before funding approval"
    return True, "travel funding is approved before expense review"


def travel_expense_matches_itinerary(facts: dict[str, Any]) -> tuple[bool, str]:
    if not facts.get("transportModes") or "tripStartsOn" not in facts:
        return True, "not a transport expense with itinerary data"
    if not facts.get("segmentsChronological"):
        return False, "transport expense is attached to non-chronological itinerary legs"
    if not facts.get("itineraryCoversExpenseDates"):
        return False, "expense item dates are outside the itinerary window"
    if not facts.get("transportModesCoveredByItinerary"):
        return False, "expense transport modes are not covered by itinerary legs"
    return True, "transport expense dates and modes match the itinerary"


INVARIANTS: tuple[Invariant, ...] = (
    Invariant(
        "roles.route_matrix_allowed",
        "permission/role matrix",
        "Every generated access pattern must use a role allowed by the route matrix.",
        0.66,
        0.86,
        0.14,
        "hard",
        route_matrix_allowed,
    ),
    Invariant(
        "roles.employee_self_review_forbidden",
        "roles/data boundaries",
        "Employee self-review remains forbidden for approvals.",
        0.62,
        0.84,
        0.16,
        "easy",
        employee_self_review_forbidden,
    ),
    Invariant(
        "modules.expense_approval_requires_module_and_receipt",
        "modules/routes/data boundaries",
        "Expense approvals require expenses entitlement and usable required receipt evidence.",
        0.72,
        0.88,
        0.12,
        "easy",
        expenses_module_and_receipt,
    ),
    Invariant(
        "dms.tenant_process_boundary",
        "data boundaries",
        "DMS evidence must stay in tenant and approved process boundaries.",
        0.68,
        0.82,
        0.18,
        "easy",
        dms_tenant_boundary,
    ),
    Invariant(
        "support.takeover_session_required",
        "roles/routes",
        "Support access requires active non-expired takeover scope.",
        0.58,
        0.80,
        0.20,
        "easy",
        support_takeover_active,
    ),
    Invariant(
        "billing.export_requires_role_and_module",
        "roles/modules/routes",
        "Billing exports require billing entitlement and finance/admin role.",
        0.55,
        0.78,
        0.22,
        "easy",
        billing_export_entitled,
    ),
    Invariant(
        "hr.documents_customer_role_boundary",
        "roles/routes/data boundaries",
        "HR document routes require customer HR/admin roles, not support/platform shortcuts.",
        0.52,
        0.76,
        0.24,
        "hard",
        hr_document_boundary,
    ),
    Invariant(
        "travel.itinerary_chronology",
        "scenario consistency",
        "Travel scenarios must not silently accept inconsistent itineraries.",
        0.46,
        0.74,
        0.26,
        "easy",
        itinerary_consistent,
    ),
    Invariant(
        "travel.funding_before_expense",
        "business scenario sequence",
        "Travel expenses require approved funding before expense submission or approval.",
        0.50,
        0.79,
        0.21,
        "hard",
        travel_funding_before_expense,
    ),
    Invariant(
        "travel.expense_items_match_itinerary",
        "business scenario consistency",
        "Rental car, train, and airplane expenses must match chronological itinerary legs.",
        0.48,
        0.77,
        0.23,
        "hard",
        travel_expense_matches_itinerary,
    ),
)


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "mundane.billing_export_by_finance",
        "mundane",
        "Finance exports billing data with the billing module enabled.",
        ("role.finance", "module.billing_on", "billing.export_route"),
        ("roles.route_matrix_allowed", "billing.export_requires_role_and_module"),
    ),
    Scenario(
        "mundane.travel_funding_to_multimodal_expense",
        "mundane",
        "Travel funding request is approved before rental car, train, and airplane expenses.",
        (
            "role.finance",
            "module.travel_on",
            "module.expenses_on",
            "route.travel_funding_request",
            "route.travel_funding_approve",
            "travel.funding_approved",
            "route.expense_approve",
            "expense.rental_car",
            "expense.train_ticket",
            "expense.airfare",
            "dms.correct_receipt",
            "travel.legs_consistent_multimodal",
        ),
        (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "dms.tenant_process_boundary",
            "travel.funding_before_expense",
            "travel.expense_items_match_itinerary",
        ),
    ),
    Scenario(
        "roundup.expense_missing_receipt_disabled_module",
        "round-up",
        "Expense approval composed from disabled module, missing receipt, and travel context.",
        (
            "role.finance",
            "module.expenses_off",
            "route.expense_approve",
            "expense.receipt_missing",
            "travel.mundane_itinerary",
            "creative.travel_expense_roundup",
        ),
        (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "travel.itinerary_chronology",
        ),
    ),
    Scenario(
        "creative.support_foreign_dms_expense_review",
        "creative",
        "Expired support session tries to inspect a foreign DMS receipt during expense review.",
        (
            "role.support_takeover_expired",
            "route.expense_approve",
            "expense.receipt_missing",
            "dms.foreign_tenant_document",
            "creative.travel_expense_roundup",
        ),
        (
            "roles.route_matrix_allowed",
            "support.takeover_session_required",
            "dms.tenant_process_boundary",
            "modules.expense_approval_requires_module_and_receipt",
        ),
    ),
    Scenario(
        "inconsistent.employee_self_review_bad_itinerary",
        "intentionally-inconsistent",
        "Employee self-approval is paired with an impossible itinerary.",
        (
            "role.employee_self",
            "route.expense_approve",
            "dms.correct_receipt",
            "expense.train_ticket",
            "travel.inconsistent_itinerary",
        ),
        (
            "roles.route_matrix_allowed",
            "roles.employee_self_review_forbidden",
            "travel.itinerary_chronology",
            "travel.expense_items_match_itinerary",
            "dms.tenant_process_boundary",
        ),
    ),
    Scenario(
        "roundup.support_hr_document_shortcut",
        "round-up",
        "Support-flavored HR document shortcut composed from partial actor and HR route fragments.",
        ("role.support_takeover_expired", "hr.payroll_file_route", "module.billing_on"),
        (
            "roles.route_matrix_allowed",
            "support.takeover_session_required",
            "hr.documents_customer_role_boundary",
        ),
    ),
    Scenario(
        "roundup.travel_funding_unapproved_multimodal_expense",
        "round-up",
        "Rental car, train, and airplane expenses are approved after a funding request with no approval.",
        (
            "role.finance",
            "module.travel_on",
            "module.expenses_on",
            "route.travel_funding_request",
            "travel.funding_missing",
            "route.expense_approve",
            "expense.rental_car",
            "expense.train_ticket",
            "expense.airfare",
            "dms.correct_receipt",
            "travel.legs_consistent_multimodal",
        ),
        (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "travel.funding_before_expense",
            "travel.expense_items_match_itinerary",
        ),
    ),
    Scenario(
        "inconsistent.travel_air_train_leg_mismatch",
        "intentionally-inconsistent",
        "Airplane and train expenses are attached to reversed travel dates and mismatched legs.",
        (
            "role.finance",
            "module.expenses_on",
            "route.expense_approve",
            "expense.train_ticket",
            "expense.airfare",
            "dms.correct_receipt",
            "travel.inconsistent_itinerary",
        ),
        (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "travel.itinerary_chronology",
            "travel.expense_items_match_itinerary",
            "dms.tenant_process_boundary",
        ),
    ),
)


def generated_composite_scenarios(seed: int, count: int) -> list[Scenario]:
    rng = random.Random(seed + 271828)
    roles = ("role.finance", "role.employee_self", "role.support_takeover_expired")
    module_sets = (
        ("module.travel_on", "module.expenses_on"),
        ("module.travel_on", "module.expenses_off"),
        ("module.expenses_on",),
    )
    funding_states = ("travel.funding_approved", "travel.funding_missing")
    itinerary_states = ("travel.legs_consistent_multimodal", "travel.inconsistent_itinerary", "travel.mundane_itinerary")
    receipt_states = ("dms.correct_receipt", "dms.foreign_tenant_document")
    expense_modes = (
        ("expense.train_ticket",),
        ("expense.rental_car", "expense.train_ticket"),
        ("expense.rental_car", "expense.train_ticket", "expense.airfare"),
        ("expense.airfare", "expense.train_ticket"),
    )
    generated: list[Scenario] = []
    seen: set[tuple[str, ...]] = set()
    attempts = 0
    while len(generated) < count and attempts < count * 8:
        attempts += 1
        role = rng.choice(roles)
        modules = rng.choice(module_sets)
        funding = rng.choice(funding_states)
        itinerary = rng.choice(itinerary_states)
        dms = rng.choice(receipt_states)
        expenses = rng.choice(expense_modes)
        include_funding_approval = funding == "travel.funding_approved" and rng.choice((True, False))
        fragments = [
            role,
            *modules,
            "route.travel_funding_request",
            funding,
            "route.expense_approve",
            *expenses,
            dms,
            itinerary,
            "creative.travel_expense_roundup",
        ]
        if include_funding_approval:
            fragments.insert(4, "route.travel_funding_approve")
        fragment_ids = tuple(dict.fromkeys(fragments))
        if fragment_ids in seen:
            continue
        seen.add(fragment_ids)
        tone = "generated-inconsistent" if itinerary == "travel.inconsistent_itinerary" else "generated-round-up"
        title = "Generated composite travel expense probe"
        if set(expenses) >= {"expense.rental_car", "expense.train_ticket", "expense.airfare"}:
            title = "Generated multi-modal travel expense probe"
        generated.append(
            Scenario(
                f"generated.{len(generated) + 1:02d}.{role.split('.')[-1]}.{funding.split('.')[-1]}.{itinerary.split('.')[-1]}",
                tone,
                title,
                fragment_ids,
                (
                    "roles.route_matrix_allowed",
                    "modules.expense_approval_requires_module_and_receipt",
                    "dms.tenant_process_boundary",
                    "travel.funding_before_expense",
                    "travel.expense_items_match_itinerary",
                    "travel.itinerary_chronology",
                ),
                generated=True,
                generation_basis="seeded composite fragment generator",
            )
        )
    return generated


def bayesian_posterior(prior: float, likelihood: float) -> float:
    denominator = prior * likelihood + (1.0 - prior) * (1.0 - likelihood)
    return round((prior * likelihood) / denominator, 6)


def clamp_probability(value: float) -> float:
    return min(0.95, max(0.05, value))


def merge_unique(existing: list[Any], incoming: list[Any]) -> list[Any]:
    merged = list(existing)
    for item in incoming:
        if item not in merged:
            merged.append(item)
    return merged


def merge_facts(fragments: list[Fragment]) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    modules: dict[str, bool] = {}
    conflicts: list[dict[str, Any]] = []

    for fragment in fragments:
        for key, value in fragment.facts.items():
            if key == "modules":
                modules.update(value)
            elif key in LIST_FACT_KEYS:
                facts[key] = merge_unique(facts.get(key, []), value)
            elif key in BOOLEAN_OR_FACT_KEYS:
                facts[key] = bool(facts.get(key, False) or value)
            elif key in BOOLEAN_AND_FACT_KEYS:
                facts[key] = bool(facts.get(key, True) and value)
            elif key in NUMERIC_SUM_FACT_KEYS:
                facts[key] = int(facts.get(key, 0)) + int(value)
            elif key in facts and facts[key] != value:
                conflicts.append(
                    {
                        "fragmentId": fragment.id,
                        "key": key,
                        "previous": facts[key],
                        "incoming": value,
                    }
                )
                facts[key] = value
            else:
                facts[key] = value
    if modules:
        facts["modules"] = modules
    if conflicts:
        facts["factConflicts"] = conflicts
    return facts


def sub_scenarios(fragments: list[Fragment]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"subscenario.{index}.{fragment.id}",
            "fragmentId": fragment.id,
            "domain": fragment.domain,
            "kind": fragment.kind,
            "completeAlone": fragment.complete_alone,
            "summary": fragment.summary,
        }
        for index, fragment in enumerate(fragments, start=1)
    ]


def access_pattern(facts: dict[str, Any]) -> dict[str, Any]:
    data_signals = {
        key: facts[key]
        for key in (
            "allRequiredReceiptsUsable",
            "documentTenantMatches",
            "itineraryCoversExpenseDates",
            "segmentsChronological",
            "targetEmployeeId",
            "transportModesCoveredByItinerary",
        )
        if key in facts
    }
    return {
        "actorRole": facts.get("actorRole", "unknown"),
        "businessFlow": facts.get("businessFlow", []),
        "decision": facts.get("decision"),
        "expenseCategories": facts.get("expenseCategories", []),
        "modules": facts.get("modules", {}),
        "routes": facts.get("routes", []),
        "transportModes": facts.get("transportModes", []),
        "dataSignals": data_signals,
    }


def finding_fingerprint(scenario: Scenario, invariant: Invariant, fragments: list[Fragment]) -> str:
    payload = {
        "fragments": [fragment.id for fragment in fragments],
        "invariant": invariant.id,
        "scenario": scenario.id,
        "tool": VERSION,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return f"bayesilisk:{digest[:16]}"


def load_observations(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_context(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _context_items(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _context_items(nested)
    elif isinstance(value, list | tuple):
        for nested in value:
            yield from _context_items(nested)


def _context_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, int | float | bool):
        yield str(value)
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _context_strings(nested)
    elif isinstance(value, list | tuple):
        for nested in value:
            yield from _context_strings(nested)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list | tuple | set):
        return []
    return sorted({item for item in value if isinstance(item, str)})


def _count_context_collection(context: dict[str, Any], key: str) -> int:
    value = context.get(key)
    if isinstance(value, list | tuple):
        return len(value)
    if isinstance(value, dict):
        return len(value)
    return 0


def _context_prior_adjustments(text: str) -> tuple[dict[str, float], dict[str, int]]:
    lower = text.lower()
    keyword_hits: dict[str, int] = {}
    adjustments: dict[str, float] = {}
    for invariant_id, keywords in CONTEXT_INVARIANT_KEYWORDS.items():
        hits = sum(lower.count(keyword) for keyword in keywords)
        if hits <= 0:
            continue
        keyword_hits[invariant_id] = hits
        adjustments[invariant_id] = round(min(0.18, 0.018 * hits), 6)
    return adjustments, keyword_hits


def context_summary(context: dict[str, Any] | None) -> dict[str, Any]:
    context = context or {}
    text_values = list(_context_strings(context))
    text = "\n".join(text_values)
    fingerprints = sorted(set(FINGERPRINT_PATTERN.findall(text)))
    prior_adjustments, keyword_hits = _context_prior_adjustments(text)
    return {
        "source": context.get("source", "mcp-context" if context else "none"),
        "agentNoteCount": _count_context_collection(context, "agentNotes"),
        "issueCount": _count_context_collection(context, "issues")
        + _count_context_collection(context, "openIssues"),
        "pullRequestCount": _count_context_collection(context, "pullRequests")
        + _count_context_collection(context, "prs"),
        "repositoryFactCount": _count_context_collection(context, "repositoryFacts"),
        "textSignalCount": len([value for value in text_values if value.strip()]),
        "fingerprints": fingerprints,
        "keywordHits": keyword_hits,
        "priorAdjustments": prior_adjustments,
    }


def context_observations(context: dict[str, Any] | None) -> dict[str, Any]:
    summary = context_summary(context)
    context = context or {}
    muted = set(summary["fingerprints"])
    muted.update(_string_list(context.get("mutedFingerprints")))
    fixed = set(_string_list(context.get("fixedFingerprints")))
    confirmed = set(_string_list(context.get("confirmedFingerprints")))
    explicit_adjustments = context.get("priorAdjustments", {})
    prior_adjustments = dict(summary["priorAdjustments"])
    if isinstance(explicit_adjustments, dict):
        for invariant_id, delta in explicit_adjustments.items():
            if isinstance(invariant_id, str) and isinstance(delta, int | float):
                prior_adjustments[invariant_id] = round(float(delta), 6)
    scenario_adjustments = context.get("scenarioAdjustments", {})
    if not isinstance(scenario_adjustments, dict):
        scenario_adjustments = {}
    return {
        "source": summary["source"],
        "fixedFingerprints": sorted(fixed),
        "confirmedFingerprints": sorted(confirmed),
        "mutedFingerprints": sorted(muted),
        "priorAdjustments": prior_adjustments,
        "scenarioAdjustments": scenario_adjustments,
    }


def merge_observations(base: dict[str, Any] | None, incoming: dict[str, Any] | None) -> dict[str, Any]:
    base = base or {}
    incoming = incoming or {}
    merged = dict(base)
    merged["source"] = incoming.get("source") or base.get("source", "none")
    for key in ("fixedFingerprints", "confirmedFingerprints", "mutedFingerprints"):
        merged[key] = sorted(set(_string_list(base.get(key))) | set(_string_list(incoming.get(key))))
    for key in ("priorAdjustments", "scenarioAdjustments"):
        merged_values = {}
        if isinstance(base.get(key), dict):
            merged_values.update(base[key])
        if isinstance(incoming.get(key), dict):
            merged_values.update(incoming[key])
        merged[key] = merged_values
    return merged


def observation_basis(
    fingerprint: str,
    scenario: Scenario,
    invariant: Invariant,
    observations: dict[str, Any],
) -> dict[str, Any]:
    fixed = set(observations.get("fixedFingerprints", []))
    confirmed = set(observations.get("confirmedFingerprints", []))
    muted = set(observations.get("mutedFingerprints", []))
    invariant_adjustments = observations.get("priorAdjustments", {})
    scenario_adjustments = observations.get("scenarioAdjustments", {})

    prior_delta = 0.0
    tags: list[str] = []
    if fingerprint in fixed:
        prior_delta -= 0.28
        tags.append("fixed-regression-watch")
    if fingerprint in confirmed:
        prior_delta += 0.18
        tags.append("confirmed-local-breakage")
    if fingerprint in muted:
        prior_delta -= 0.45
        tags.append("muted-known-non-issue")
    if invariant.id in invariant_adjustments:
        prior_delta += float(invariant_adjustments[invariant.id])
        tags.append(f"invariant-adjustment:{invariant.id}")
    if scenario.id in scenario_adjustments:
        prior_delta += float(scenario_adjustments[scenario.id])
        tags.append(f"scenario-adjustment:{scenario.id}")
    return {
        "source": observations.get("source", "none"),
        "tags": tags or ["fresh-prior"],
        "priorDelta": round(prior_delta, 6),
    }


def finding_classification(passed: bool, risk_score: float, invariant: Invariant) -> str:
    if passed:
        return "control-confirmed"
    if invariant.difficulty == "hard":
        return "breakage.hard-to-find"
    if risk_score >= 0.80:
        return "breakage.easy"
    return "finding.candidate-breakage"


def posterior_mode(passed: bool, risk_score: float, invariant: Invariant) -> str:
    if passed:
        return "posterior-control-confidence"
    if risk_score >= 0.85:
        return "highest-fault-probability"
    if invariant.difficulty == "hard":
        return "harder-to-find-after-easy-breakages"
    return "fault-probability-elevated"


def issue_readiness(passed: bool, classification: str, basis: dict[str, Any]) -> str:
    tags = set(basis.get("tags", []))
    if passed:
        return "no-issue-control"
    if "muted-known-non-issue" in tags:
        return "do-not-open-muted"
    if "fixed-regression-watch" in tags:
        return "regression-watch"
    if classification.startswith("breakage."):
        return "ready-for-issue"
    return "probe-only"


def report_sections(findings: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        "confirmedBreakages": [
            finding["fingerprint"]
            for finding in findings
            if finding["observedResult"] == "fail" and finding["issueReadiness"] == "ready-for-issue"
        ],
        "candidateProbes": [
            finding["fingerprint"]
            for finding in findings
            if finding["observedResult"] == "fail" and finding["issueReadiness"] in {"probe-only", "regression-watch"}
        ],
        "hardToFindModes": [
            finding["fingerprint"]
            for finding in findings
            if finding["posteriorMode"] == "harder-to-find-after-easy-breakages"
            or finding["classification"] == "breakage.hard-to-find"
        ],
        "controls": [
            finding["fingerprint"]
            for finding in findings
            if finding["observedResult"] == "pass"
        ],
    }


def build_report(
    seed: int,
    limit: int | None = None,
    generated_count: int = 8,
    observations: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observations = observations or {}
    rng = random.Random(seed)
    fragment_by_id = {fragment.id: fragment for fragment in FRAGMENTS}
    invariant_by_id = {invariant.id: invariant for invariant in INVARIANTS}
    generated_scenarios = generated_composite_scenarios(seed, generated_count)
    scenario_order = [*SCENARIOS, *generated_scenarios]
    rng.shuffle(scenario_order)

    findings: list[dict[str, Any]] = []
    for scenario in scenario_order:
        fragments = [fragment_by_id[fragment_id] for fragment_id in scenario.fragment_ids]
        facts = merge_facts(fragments)
        pattern = access_pattern(facts)
        entries = sub_scenarios(fragments)
        for invariant_id in scenario.invariant_ids:
            invariant = invariant_by_id[invariant_id]
            passed, observation = invariant.evaluator(facts)
            likelihood = invariant.pass_likelihood if passed else invariant.fail_likelihood
            fingerprint = finding_fingerprint(scenario, invariant, fragments)
            basis = observation_basis(fingerprint, scenario, invariant, observations)
            adjusted_prior = clamp_probability(invariant.prior + basis["priorDelta"])
            risk_score = bayesian_posterior(adjusted_prior, likelihood)
            observed_result = "pass" if passed else "fail"
            classification = finding_classification(passed, risk_score, invariant)
            mode = posterior_mode(passed, risk_score, invariant)
            readiness = issue_readiness(passed, classification, basis)
            title = suggested_title(scenario, invariant, observed_result, classification)
            body = suggested_body(
                scenario,
                invariant,
                fragments,
                observation,
                risk_score,
                classification,
                mode,
                pattern,
                fingerprint,
                readiness,
                basis,
            )
            findings.append(
                {
                    "id": f"{scenario.id}:{invariant.id}",
                    "fingerprint": fingerprint,
                    "dedupeKey": f"{fingerprint}:{invariant.id}",
                    "scenarioId": scenario.id,
                    "scenarioTitle": scenario.title,
                    "scenarioTone": scenario.tone,
                    "generatedScenario": scenario.generated,
                    "generationBasis": scenario.generation_basis,
                    "subScenarios": entries,
                    "fragments": [
                        {
                            "completeAlone": fragment.complete_alone,
                            "domain": fragment.domain,
                            "id": fragment.id,
                            "kind": fragment.kind,
                            "summary": fragment.summary,
                        }
                        for fragment in fragments
                    ],
                    "accessPattern": pattern,
                    "expectedInvariant": invariant.expected,
                    "invariantId": invariant.id,
                    "invariantLayer": invariant.layer,
                    "observedResult": observed_result,
                    "observation": observation,
                    "classification": classification,
                    "issueReadiness": readiness,
                    "observationBasis": basis,
                    "prior": invariant.prior,
                    "adjustedPrior": adjusted_prior,
                    "likelihood": likelihood,
                    "posteriorProbability": risk_score,
                    "posteriorMode": mode,
                    "riskScore": risk_score,
                    "suggestedIssueTitle": title,
                    "suggestedIssueBody": body,
                }
            )

    findings.sort(key=lambda item: (-item["riskScore"], item["posteriorMode"], item["id"]))
    if limit is not None:
        findings = findings[:limit]
    sections = report_sections(findings)
    return {
        "tool": VERSION,
        "seed": seed,
        "deterministic": True,
        "productionAccess": False,
        "generatedScenarioCount": len(generated_scenarios),
        "domains": ["Travel", "Expenses", "Billing", "HR", "Support", "DMS", "module entitlements"],
        "prioritizationPolicy": (
            "Sort by posterior fault probability first. Fix or document breakage.easy findings, rerun with the "
            "same seed, then promote harder-to-find-after-easy-breakages modes."
        ),
        "invariants": [
            {
                "difficulty": invariant.difficulty,
                "expected": invariant.expected,
                "failLikelihood": invariant.fail_likelihood,
                "id": invariant.id,
                "layer": invariant.layer,
                "passLikelihood": invariant.pass_likelihood,
                "prior": invariant.prior,
            }
            for invariant in INVARIANTS
        ],
        "roleRouteMatrix": {route: sorted(roles) for route, roles in ROLE_ROUTE_MATRIX.items()},
        "sections": sections,
        "findings": findings,
    }


def build_contextual_report(
    seed: int,
    limit: int | None = None,
    generated_count: int = 8,
    observations: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    summary = context_summary(context)
    merged_observations = merge_observations(observations, context_observations(context))
    report = build_report(
        seed,
        limit=limit,
        generated_count=generated_count,
        observations=merged_observations,
    )
    report["contextSummary"] = summary
    report["contextObservationSource"] = merged_observations.get("source", "none")
    report["rankedProbes"] = ranked_probes(report, limit=limit)
    report["issuePayloads"] = issue_payloads(report, context=context, limit=limit)
    return report


def ranked_probes(report: dict[str, Any], limit: int | None = None) -> list[dict[str, Any]]:
    probes = [
        {
            "accessPattern": finding["accessPattern"],
            "classification": finding["classification"],
            "fingerprint": finding["fingerprint"],
            "generatedScenario": finding["generatedScenario"],
            "invariantId": finding["invariantId"],
            "issueReadiness": finding["issueReadiness"],
            "observedResult": finding["observedResult"],
            "posteriorMode": finding["posteriorMode"],
            "reproduce": (
                f"python3 tools/bayesilisk/bayesilisk.py --seed {report['seed']} "
                f"--generated-count {report['generatedScenarioCount']} --format json"
            ),
            "riskScore": finding["riskScore"],
            "scenarioId": finding["scenarioId"],
            "scenarioTitle": finding["scenarioTitle"],
            "title": finding["suggestedIssueTitle"],
        }
        for finding in report["findings"]
        if finding["observedResult"] == "fail"
    ]
    if limit is not None:
        return probes[:limit]
    return probes


def _existing_context_titles(context: dict[str, Any] | None) -> set[str]:
    titles: set[str] = set()
    if not context:
        return titles
    for item in _context_items(context):
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        if isinstance(title, str):
            titles.add(title.strip().lower())
    return titles


def issue_payloads(
    report: dict[str, Any],
    context: dict[str, Any] | None = None,
    limit: int | None = None,
    include_existing: bool = False,
) -> list[dict[str, Any]]:
    existing_fingerprints = set(context_summary(context)["fingerprints"])
    existing_titles = _existing_context_titles(context)
    payloads: list[dict[str, Any]] = []
    for finding in report["findings"]:
        if finding["observedResult"] != "fail" or finding["issueReadiness"] != "ready-for-issue":
            continue
        title = finding["suggestedIssueTitle"]
        title_key = title.strip().lower()
        dedupe_state = "new"
        if finding["fingerprint"] in existing_fingerprints:
            dedupe_state = "existing-fingerprint"
        elif title_key in existing_titles:
            dedupe_state = "existing-title"
        if dedupe_state != "new" and not include_existing:
            continue
        labels = ["bayesilisk", "usa"]
        if finding["generatedScenario"]:
            labels.append("generated-scenario")
        payloads.append(
            {
                "body": finding["suggestedIssueBody"],
                "classification": finding["classification"],
                "dedupeKey": finding["dedupeKey"],
                "dedupeState": dedupe_state,
                "fingerprint": finding["fingerprint"],
                "invariantId": finding["invariantId"],
                "issueReadiness": finding["issueReadiness"],
                "labels": labels,
                "posteriorMode": finding["posteriorMode"],
                "riskScore": finding["riskScore"],
                "scenarioId": finding["scenarioId"],
                "title": title,
            }
        )
        if limit is not None and len(payloads) >= limit:
            break
    return payloads


def suggested_title(
    scenario: Scenario,
    invariant: Invariant,
    observed_result: str,
    classification: str,
) -> str:
    if observed_result == "fail":
        return f"Bayesilisk {classification}: {scenario.tone} scenario violates {invariant.id}"
    return f"Bayesilisk {classification}: {scenario.tone} scenario confirms {invariant.id}"


def suggested_body(
    scenario: Scenario,
    invariant: Invariant,
    fragments: list[Fragment],
    observation: str,
    risk_score: float,
    classification: str,
    mode: str,
    pattern: dict[str, Any],
    fingerprint: str,
    readiness: str,
    basis: dict[str, Any],
) -> str:
    fragment_lines = "\n".join(f"- `{fragment.id}` ({fragment.domain}): {fragment.summary}" for fragment in fragments)
    pattern_json = json.dumps(pattern, indent=2, sort_keys=True)
    basis_json = json.dumps(basis, indent=2, sort_keys=True)
    return (
        f"Scenario `{scenario.id}`: {scenario.title}\n\n"
        f"Fingerprint: `{fingerprint}`\n\n"
        f"Classification: `{classification}`\n\n"
        f"Issue readiness: `{readiness}`\n\n"
        f"Posterior mode: `{mode}`\n\n"
        f"Expected invariant: {invariant.expected}\n\n"
        f"Observed: {observation}\n\n"
        f"Risk score: {risk_score:.6f}\n\n"
        f"Observation basis:\n```json\n{basis_json}\n```\n\n"
        f"Access pattern:\n```json\n{pattern_json}\n```\n\n"
        f"Fragments:\n{fragment_lines}\n\n"
        "Reproduce with `python3 tools/bayesilisk/bayesilisk.py --seed <seed> --format json`."
    )


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Bayesilisk Report",
        "",
        f"- Tool: `{report['tool']}`",
        f"- Seed: `{report['seed']}`",
        f"- Deterministic: `{str(report['deterministic']).lower()}`",
        f"- Production access: `{str(report['productionAccess']).lower()}`",
        f"- Generated scenarios: `{report['generatedScenarioCount']}`",
        f"- Prioritization: {report['prioritizationPolicy']}",
        "",
        "## Sections",
        "",
        f"- Confirmed breakages: `{len(report['sections']['confirmedBreakages'])}`",
        f"- Candidate probes: `{len(report['sections']['candidateProbes'])}`",
        f"- Hard-to-find modes: `{len(report['sections']['hardToFindModes'])}`",
        f"- Controls: `{len(report['sections']['controls'])}`",
        "",
        "## Findings",
        "",
    ]
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['suggestedIssueTitle']}",
                "",
                f"- Scenario: `{finding['scenarioId']}` ({finding['scenarioTone']})",
                f"- Fingerprint: `{finding['fingerprint']}`",
                f"- Generated scenario: `{str(finding['generatedScenario']).lower()}`",
                f"- Classification: `{finding['classification']}`",
                f"- Issue readiness: `{finding['issueReadiness']}`",
                f"- Posterior mode: `{finding['posteriorMode']}`",
                f"- Expected invariant: {finding['expectedInvariant']}",
                f"- Observed result: `{finding['observedResult']}`",
                f"- Observation: {finding['observation']}",
                f"- Observation basis: `{', '.join(finding['observationBasis']['tags'])}`",
                f"- Risk score: `{finding['riskScore']:.6f}`",
                "- Sub-scenarios:",
            ]
        )
        for entry in finding["subScenarios"]:
            complete = str(entry["completeAlone"]).lower()
            lines.append(f"  - `{entry['fragmentId']}` [{entry['domain']}], complete alone: `{complete}`")
        lines.extend(
            [
                "- Access pattern:",
                "```json",
                json.dumps(finding["accessPattern"], indent=2, sort_keys=True),
                "```",
                "",
                "Suggested Gitea issue body:",
                "",
                "````markdown",
                finding["suggestedIssueBody"],
                "````",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_output(content: str, output_path: Path | None) -> None:
    if output_path is None:
        print(content, end="")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bayesilisk Bayesian permission and scenario verifier.")
    parser.add_argument("--seed", type=int, default=150, help="Deterministic scenario ordering seed.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Report format.")
    parser.add_argument("--output", type=Path, default=None, help="Optional output file.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of findings.")
    parser.add_argument("--generated-count", type=int, default=8, help="Number of seeded generated composite scenarios.")
    parser.add_argument("--observations", type=Path, default=None, help="Optional JSON observation history.")
    parser.add_argument("--context", type=Path, default=None, help="Optional JSON context from agents, Gitea, or repo scans.")
    parser.add_argument(
        "--issue-payloads",
        action="store_true",
        help="Emit only deduped Gitea issue payloads for ready failed findings.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    observations = load_observations(args.observations)
    context = load_context(args.context)
    if context:
        report = build_contextual_report(
            args.seed,
            limit=args.limit,
            generated_count=args.generated_count,
            observations=observations,
            context=context,
        )
    else:
        report = build_report(
            args.seed,
            limit=args.limit,
            generated_count=args.generated_count,
            observations=observations,
        )
    if args.issue_payloads:
        content = json.dumps(issue_payloads(report, context=context, limit=args.limit), indent=2, sort_keys=True) + "\n"
        write_output(content, args.output)
        return 0
    if args.format == "json":
        content = json.dumps(report, indent=2, sort_keys=True) + "\n"
    else:
        content = markdown_report(report)
    write_output(content, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
