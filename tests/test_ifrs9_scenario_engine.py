from src.data.generate_synthetic_data import generate_customers, generate_loans
from src.risk.ifrs9_scenario_engine import ecl_bridge, lifetime_pd, scenario_weighted_ecl, stage_migration_table


def test_lifetime_pd_greater_for_stage_two():
    assert lifetime_pd(0.05, stage=2, remaining_life_years=4) > 0.05
    assert lifetime_pd(0.05, stage=1, remaining_life_years=4) == 0.05


def test_scenario_weighted_ecl_outputs_loan_and_summary_tables():
    customers = generate_customers(n=120)
    loans = generate_loans(customers)
    loan_level, summary = scenario_weighted_ecl(loans)
    assert "weighted_ecl" in loan_level.columns
    assert set(summary["scenario"]) == {"Upside", "Baseline", "Downside"}
    assert loan_level["weighted_ecl"].sum() > 0


def test_stage_migration_table_and_bridge():
    customers = generate_customers(n=120)
    loans = generate_loans(customers)
    migration = stage_migration_table(loans, pd_multiplier=2.0)
    bridge = ecl_bridge(100, 10, 5, 20, 15)
    assert migration.values.sum() == len(loans)
    assert bridge.loc[bridge["component"].eq("Closing ECL"), "amount"].iloc[0] == 140
