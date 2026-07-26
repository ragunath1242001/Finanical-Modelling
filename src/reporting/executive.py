def management_actions(cet1_ratio: float, lcr: float, nsfr: float, data_quality_score: float) -> list[str]:
    actions = []
    if cet1_ratio < 0.10:
        actions.append("Review dividend distributions, risky asset growth, and capital plan.")
    if lcr < 1.0:
        actions.append("Increase high-quality liquid assets or reduce 30-day net cash outflows.")
    if nsfr < 1.0:
        actions.append("Lengthen funding profile and reduce unstable funding dependence.")
    if data_quality_score < 95:
        actions.append("Prioritize BCBS 239 remediation for failed controls before regulatory reporting.")
    return actions or ["Maintain monitoring; current simulated indicators are within management appetite."]
