"""Educational data-lineage graph for BCBS 239 risk aggregation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class LineageNode:
    node_id: str
    name: str
    node_type: str
    owner: str
    data_steward: str
    description: str
    source: str
    transformation: str
    controls: list[str]
    downstream_nodes: list[str]
    regulatory_relevance: str


@dataclass(frozen=True)
class LineageEdge:
    source_node: str
    target_node: str
    transformation: str
    frequency: str
    validation_rule: str


LINEAGE_NODES = [
    LineageNode("LOS", "Loan Origination System", "Source system", "Business Owner", "Data Steward", "Captures borrower, facility and collateral data.", "Synthetic customer and loan feed", "Raw capture", ["DQ-001", "DQ-002"], ["CUST"], "Source completeness and traceability."),
    LineageNode("CUST", "Customer Master", "Reference data", "Business Owner", "Data Steward", "Stores customer identifier and demographic attributes.", "Loan Origination System", "Customer consolidation", ["DQ-003", "DQ-017"], ["RDM"], "Identity consistency for aggregation."),
    LineageNode("RDM", "Credit Risk Data Mart", "Data mart", "Risk Data Owner", "Risk Data Steward", "Combines customer, loan, PD, LGD and EAD fields.", "Customer Master and loan feed", "Join, validate, enrich", ["DQ-004", "DQ-005", "DQ-006", "DQ-015"], ["PDENG"], "Risk aggregation and model input quality."),
    LineageNode("PDENG", "PD/LGD/EAD Engines", "Risk engine", "Model Owner", "Model Risk Steward", "Calculates or receives credit-risk parameters.", "Credit Risk Data Mart", "Validated risk parameter calculation", ["DQ-008", "DQ-011"], ["IFRS9"], "Inputs to ECL, IRB and stress testing."),
    LineageNode("IFRS9", "IFRS 9 ECL Engine", "Accounting engine", "Finance/Risk Owner", "IFRS 9 Steward", "Stages loans and calculates 12-month or lifetime ECL.", "PD/LGD/EAD Engines", "Scenario-weighted expected loss", ["DQ-012", "DQ-013"], ["FINPROV"], "Provision reporting."),
    LineageNode("FINPROV", "Finance Provision", "Finance adjustment", "Finance Owner", "Finance Steward", "Posts provision impact into financial reporting view.", "IFRS 9 ECL Engine", "Provision bridge and reconciliation", ["DQ-014"], ["FINREP"], "FINREP-style reporting readiness."),
    LineageNode("FINREP", "FINREP-style Report", "Report", "Regulatory Reporting Owner", "Reporting Steward", "Shows simplified balance sheet and profit impact.", "Finance Provision", "Aggregate financial metrics", ["DQ-014", "DQ-016"], ["CET1"], "Educational financial reporting."),
    LineageNode("CET1", "CET1 Bridge", "Capital bridge", "Capital Owner", "Capital Steward", "Links provision movements to retained earnings and CET1.", "FINREP-style Report", "Simplified capital bridge", ["DQ-014"], ["COREP"], "Capital ratio impact."),
    LineageNode("COREP", "COREP-style Report", "Report", "Regulatory Reporting Owner", "Reporting Steward", "Shows simplified capital resources, RWA and ratios.", "CET1 Bridge", "Capital ratio aggregation", ["DQ-014", "DQ-016"], [], "Educational capital reporting."),
]

LINEAGE_EDGES = [
    LineageEdge("LOS", "CUST", "Customer attributes feed", "Daily", "Customer ID populated and unique."),
    LineageEdge("CUST", "RDM", "Customer-loan join", "Daily", "Loan customer IDs match customer master."),
    LineageEdge("RDM", "PDENG", "Risk parameter preparation", "Daily", "PD/LGD/EAD ranges valid."),
    LineageEdge("PDENG", "IFRS9", "ECL input handoff", "Monthly", "Model version and origination PD available."),
    LineageEdge("IFRS9", "FINPROV", "Provision output", "Monthly", "Scenario weights total 100%."),
    LineageEdge("FINPROV", "FINREP", "Finance aggregation", "Monthly", "Risk and finance provision reconcile."),
    LineageEdge("FINREP", "CET1", "Retained earnings bridge", "Monthly", "Provision impact approved."),
    LineageEdge("CET1", "COREP", "Capital reporting handoff", "Monthly", "Exposure and CET1 reconcile."),
]

LINEAGE_STEPS = [node.name for node in LINEAGE_NODES]


def lineage_nodes_frame() -> pd.DataFrame:
    return pd.DataFrame([{**node.__dict__, "controls": ", ".join(node.controls), "downstream_nodes": ", ".join(node.downstream_nodes)} for node in LINEAGE_NODES])


def lineage_edges_frame() -> pd.DataFrame:
    return pd.DataFrame([edge.__dict__ for edge in LINEAGE_EDGES])


def lineage_node(node_id: str) -> LineageNode:
    for node in LINEAGE_NODES:
        if node.node_id == node_id:
            return node
    raise KeyError(f"Unknown lineage node: {node_id}")


def downstream_lineage(node_id: str) -> list[LineageNode]:
    selected = lineage_node(node_id)
    return [lineage_node(child) for child in selected.downstream_nodes]


def upstream_lineage(node_id: str) -> list[LineageNode]:
    parents = [edge.source_node for edge in LINEAGE_EDGES if edge.target_node == node_id]
    return [lineage_node(parent) for parent in parents]


def controls_for_node(node_id: str) -> list[str]:
    return lineage_node(node_id).controls
