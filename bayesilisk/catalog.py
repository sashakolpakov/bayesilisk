from __future__ import annotations

import random
from collections.abc import Iterable

from .constants import (
    ATTENTION_SCENARIO_TEMPLATES,
    BILLING_EXPORT_ROUTE,
    EXPENSE_REVIEW_ROUTE,
    HR_DOCUMENT_ROUTE,
    TRAVEL_FUNDING_APPROVAL_ROUTE,
    TRAVEL_FUNDING_REQUEST_ROUTE,
)
from .types import Fragment, Scenario

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
        "role.manager_reviewer",
        "Expenses",
        "actor",
        {"actorRole": "manager", "actorEmployeeId": "emp-manager", "targetEmployeeId": "emp-002"},
        "Manager actor reviews a different employee's expense claim.",
    ),
    Fragment(
        "role.hr_manager",
        "HR",
        "actor",
        {"actorRole": "hr_manager", "actorEmployeeId": "emp-hr"},
        "Customer HR manager actor reviews personnel documents.",
    ),
    Fragment(
        "role.support_takeover_expired",
        "Support",
        "actor",
        {"actorRole": "support", "supportSessionActive": False, "supportSessionExpired": True},
        "Support actor has an expired takeover session.",
    ),
    Fragment(
        "role.support_takeover_active",
        "Support",
        "actor",
        {"actorRole": "support", "supportSessionActive": True, "supportSessionExpired": False},
        "Support actor has an active non-expired takeover session.",
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
        "module.billing_off",
        "module entitlements",
        "entitlement",
        {"modules": {"billing": False}},
        "Billing module is disabled.",
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
        "travel.funding_approved_late",
        "Travel",
        "data",
        {
            "businessFlow": ["travel funding request", "late travel funding approval"],
            "fundingApprovedOn": "2026-06-15",
            "travelFundingApproved": True,
        },
        "Travel funding is approved after the expense submission date.",
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
        "dms.wrong_process_document",
        "DMS",
        "data",
        {
            "dmsDocumentStatus": "approved",
            "dmsProcess": "recruiting",
            "documentTenantMatches": True,
            "expectedDmsProcess": "travel_expense",
        },
        "DMS document is tenant-scoped but belongs to the wrong process.",
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
        "travel.legs_missing_airplane",
        "Travel",
        "data",
        {
            "itineraryCoversExpenseDates": True,
            "segmentsChronological": True,
            "transportModesCoveredByItinerary": False,
            "travelLegs": [{"end": "2026-06-12", "mode": "train", "start": "2026-06-10"}],
            "tripEndsOn": "2026-06-12",
            "tripStartsOn": "2026-06-10",
        },
        "Travel itinerary is chronological but lacks an airplane leg for airfare.",
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

SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "mundane.billing_export_by_finance",
        "mundane",
        "Finance exports billing data with the billing module enabled.",
        ("role.finance", "module.billing_on", "billing.export_route"),
        ("roles.route_matrix_allowed", "billing.export_requires_role_and_module"),
    ),
    Scenario(
        "mundane.hr_document_by_hr_manager",
        "mundane",
        "Customer HR manager downloads an HR document through the customer HR route.",
        ("role.hr_manager", "hr.payroll_file_route"),
        ("roles.route_matrix_allowed", "hr.documents_customer_role_boundary"),
    ),
    Scenario(
        "mundane.manager_reviews_employee_expense",
        "mundane",
        "Manager reviews a different employee's expense with usable evidence.",
        (
            "role.manager_reviewer",
            "module.expenses_on",
            "route.expense_approve",
            "expense.train_ticket",
            "dms.correct_receipt",
            "travel.mundane_itinerary",
        ),
        (
            "roles.route_matrix_allowed",
            "roles.employee_self_review_forbidden",
            "modules.expense_approval_requires_module_and_receipt",
            "dms.tenant_process_boundary",
            "travel.expense_items_match_itinerary",
        ),
    ),
    Scenario(
        "mundane.support_takeover_active_control",
        "mundane",
        "Support actor has an active non-expired takeover session with no customer data route.",
        ("role.support_takeover_active",),
        ("support.takeover_session_required", "roles.route_matrix_allowed"),
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
        "roundup.billing_export_disabled_module",
        "round-up",
        "Finance actor reaches billing export while the billing module is disabled.",
        ("role.finance", "module.billing_off", "billing.export_route"),
        ("roles.route_matrix_allowed", "billing.export_requires_role_and_module"),
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
        "creative.support_active_hr_document_shortcut",
        "creative",
        "Active support takeover is still not a customer HR role for HR document download.",
        ("role.support_takeover_active", "hr.payroll_file_route", "module.billing_on"),
        (
            "roles.route_matrix_allowed",
            "support.takeover_session_required",
            "hr.documents_customer_role_boundary",
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
        "inconsistent.dms_wrong_process_receipt",
        "intentionally-inconsistent",
        "Tenant-scoped DMS evidence comes from the recruiting process during travel expense review.",
        (
            "role.finance",
            "module.expenses_on",
            "route.expense_approve",
            "expense.rental_car",
            "dms.wrong_process_document",
            "travel.mundane_itinerary",
        ),
        (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "dms.tenant_process_boundary",
            "travel.expense_items_match_itinerary",
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
        "roundup.travel_expense_before_late_funding",
        "round-up",
        "Travel expense is submitted before a late funding approval lands.",
        (
            "role.finance",
            "module.travel_on",
            "module.expenses_on",
            "route.travel_funding_request",
            "route.travel_funding_approve",
            "travel.funding_approved_late",
            "route.expense_approve",
            "expense.train_ticket",
            "dms.correct_receipt",
            "travel.mundane_itinerary",
        ),
        (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "travel.funding_before_expense",
            "travel.expense_items_match_itinerary",
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
        "inconsistent.travel_missing_airplane_leg",
        "intentionally-inconsistent",
        "Airfare is claimed against a chronological itinerary that lacks an airplane leg.",
        (
            "role.finance",
            "module.expenses_on",
            "route.expense_approve",
            "expense.airfare",
            "dms.correct_receipt",
            "travel.legs_missing_airplane",
        ),
        (
            "roles.route_matrix_allowed",
            "modules.expense_approval_requires_module_and_receipt",
            "travel.itinerary_chronology",
            "travel.expense_items_match_itinerary",
            "dms.tenant_process_boundary",
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


def attention_composite_scenarios(plane_ids: Iterable[str], count: int) -> list[Scenario]:
    scenarios: list[Scenario] = []
    seen: set[tuple[str, ...]] = set()
    for plane_id in plane_ids:
        template = ATTENTION_SCENARIO_TEMPLATES.get(plane_id)
        if not template:
            continue
        fragment_ids = tuple(template["fragments"])
        if fragment_ids in seen:
            continue
        seen.add(fragment_ids)
        scenarios.append(
            Scenario(
                f"generated.attention.{len(scenarios) + 1:02d}.{plane_id.replace('.', '_')}",
                "generated-grassmann-attention",
                template["title"],
                fragment_ids,
                tuple(template["invariants"]),
                generated=True,
                generation_basis=f"grassmann-attention:{plane_id}",
            )
        )
        if len(scenarios) >= count:
            break
    return scenarios

def generated_composite_scenarios(
    seed: int,
    count: int,
    attention_plane_ids: Iterable[str] | None = None,
    model_scenarios: list[Scenario] | None = None,
) -> list[Scenario]:
    rng = random.Random(seed + 271828)
    roles = ("role.finance", "role.employee_self", "role.support_takeover_expired", "role.support_takeover_active")
    module_sets = (
        ("module.travel_on", "module.expenses_on"),
        ("module.travel_on", "module.expenses_off"),
        ("module.expenses_on",),
    )
    funding_states = ("travel.funding_approved", "travel.funding_missing", "travel.funding_approved_late")
    itinerary_states = (
        "travel.legs_consistent_multimodal",
        "travel.inconsistent_itinerary",
        "travel.mundane_itinerary",
        "travel.legs_missing_airplane",
    )
    receipt_states = ("dms.correct_receipt", "dms.foreign_tenant_document", "dms.wrong_process_document")
    expense_modes = (
        ("expense.train_ticket",),
        ("expense.rental_car", "expense.train_ticket"),
        ("expense.rental_car", "expense.train_ticket", "expense.airfare"),
        ("expense.airfare", "expense.train_ticket"),
    )
    generated: list[Scenario] = attention_composite_scenarios(attention_plane_ids or (), count)
    seen: set[tuple[str, ...]] = {scenario.fragment_ids for scenario in generated}
    for scenario in model_scenarios or []:
        if len(generated) >= count:
            break
        if scenario.fragment_ids in seen:
            continue
        seen.add(scenario.fragment_ids)
        generated.append(scenario)
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
