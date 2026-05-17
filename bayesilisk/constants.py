from __future__ import annotations

import re
from typing import Any

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
SENSITIVE_FIELD_PATTERN = re.compile(r"(api[_-]?key|authorization|bearer|secret|token|password)", re.IGNORECASE)

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

GRASSMANN_ATTENTION_WEIGHTS = {
    "failureDensity": 0.45,
    "untestedness": 0.25,
    "sensitivity": 0.15,
    "playwrightEvidence": 0.10,
    "novelty": 0.05,
}

INVARIANT_SENSITIVITY = {
    "roles.route_matrix_allowed": 0.90,
    "roles.employee_self_review_forbidden": 0.82,
    "modules.expense_approval_requires_module_and_receipt": 0.86,
    "dms.tenant_process_boundary": 0.92,
    "support.takeover_session_required": 0.84,
    "billing.export_requires_role_and_module": 0.74,
    "hr.documents_customer_role_boundary": 0.92,
    "travel.itinerary_chronology": 0.58,
    "travel.funding_before_expense": 0.64,
    "travel.expense_items_match_itinerary": 0.62,
}

ATTENTION_SCENARIO_TEMPLATES: dict[str, dict[str, Any]] = {
    "roles.route_matrix_allowed": {
        "title": "Grassmann-attention route matrix probe",
        "fragments": (
            "role.support_takeover_expired",
            "route.expense_approve",
            "expense.receipt_missing",
            "dms.foreign_tenant_document",
            "creative.travel_expense_roundup",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "support.takeover_session_required",
            "modules.expense_approval_requires_module_and_receipt",
            "dms.tenant_process_boundary",
        ),
    },
    "roles.employee_self_review_forbidden": {
        "title": "Grassmann-attention employee self-review probe",
        "fragments": (
            "role.employee_self",
            "module.expenses_on",
            "route.expense_approve",
            "expense.train_ticket",
            "dms.correct_receipt",
            "travel.mundane_itinerary",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "roles.employee_self_review_forbidden",
            "modules.expense_approval_requires_module_and_receipt",
            "travel.expense_items_match_itinerary",
        ),
    },
    "modules.expense_approval_requires_module_and_receipt": {
        "title": "Grassmann-attention disabled expense approval probe",
        "fragments": (
            "role.finance",
            "module.expenses_off",
            "route.expense_approve",
            "expense.receipt_missing",
            "dms.correct_receipt",
            "creative.travel_expense_roundup",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "dms.tenant_process_boundary",
        ),
    },
    "dms.tenant_process_boundary": {
        "title": "Grassmann-attention foreign DMS evidence probe",
        "fragments": (
            "role.finance",
            "module.expenses_on",
            "route.expense_approve",
            "expense.rental_car",
            "dms.foreign_tenant_document",
            "travel.mundane_itinerary",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "dms.tenant_process_boundary",
        ),
    },
    "support.takeover_session_required": {
        "title": "Grassmann-attention expired support takeover probe",
        "fragments": (
            "role.support_takeover_expired",
            "hr.payroll_file_route",
            "creative.travel_expense_roundup",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "support.takeover_session_required",
            "hr.documents_customer_role_boundary",
        ),
    },
    "billing.export_requires_role_and_module": {
        "title": "Grassmann-attention billing export entitlement probe",
        "fragments": (
            "role.finance",
            "module.billing_off",
            "billing.export_route",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "billing.export_requires_role_and_module",
        ),
    },
    "hr.documents_customer_role_boundary": {
        "title": "Grassmann-attention HR document boundary probe",
        "fragments": (
            "role.support_takeover_expired",
            "hr.payroll_file_route",
            "module.billing_on",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "support.takeover_session_required",
            "hr.documents_customer_role_boundary",
        ),
    },
    "travel.funding_before_expense": {
        "title": "Grassmann-attention unapproved travel funding probe",
        "fragments": (
            "role.finance",
            "module.travel_on",
            "module.expenses_on",
            "route.travel_funding_request",
            "travel.funding_missing",
            "route.expense_approve",
            "expense.train_ticket",
            "dms.correct_receipt",
            "travel.mundane_itinerary",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "travel.funding_before_expense",
        ),
    },
    "travel.itinerary_chronology": {
        "title": "Grassmann-attention inconsistent itinerary probe",
        "fragments": (
            "role.finance",
            "module.expenses_on",
            "route.expense_approve",
            "expense.train_ticket",
            "dms.correct_receipt",
            "travel.inconsistent_itinerary",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "travel.itinerary_chronology",
            "travel.expense_items_match_itinerary",
        ),
    },
    "travel.expense_items_match_itinerary": {
        "title": "Grassmann-attention transport mode mismatch probe",
        "fragments": (
            "role.finance",
            "module.expenses_on",
            "route.expense_approve",
            "expense.airfare",
            "dms.correct_receipt",
            "travel.legs_missing_airplane",
        ),
        "invariants": (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "travel.itinerary_chronology",
            "travel.expense_items_match_itinerary",
            "dms.tenant_process_boundary",
        ),
    },
}
