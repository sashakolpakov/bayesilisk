from __future__ import annotations

from typing import Any

from .constants import BILLING_EXPORT_ROUTE, EXPENSE_REVIEW_ROUTE, HR_DOCUMENT_ROUTE, ROLE_ROUTE_MATRIX
from .types import Invariant

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
    expected_process = facts.get("expectedDmsProcess")
    if expected_process and facts.get("dmsProcess") != expected_process:
        return False, f"DMS document process `{facts.get('dmsProcess')}` does not match `{expected_process}`"
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

def bayesian_posterior(prior: float, likelihood: float) -> float:
    denominator = prior * likelihood + (1.0 - prior) * (1.0 - likelihood)
    return round((prior * likelihood) / denominator, 6)


def clamp_probability(value: float) -> float:
    return min(0.95, max(0.05, value))


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
