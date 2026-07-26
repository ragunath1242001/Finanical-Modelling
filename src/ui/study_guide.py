from __future__ import annotations

import pandas as pd
import streamlit as st


STUDY_GUIDE: dict[str, list[dict[str, object]]] = {
    "Credit Risk and IFRS 9": [
        {
            "topic": "PD, LGD, EAD and Expected Loss",
            "definition": [
                "Credit risk is the risk that a borrower fails to repay as agreed.",
                "PD, LGD, and EAD are the three basic building blocks used to translate borrower risk into a monetary loss estimate.",
                "PD means Probability of Default. It answers: how likely is default?",
                "LGD means Loss Given Default. It answers: if default happens, how much of the exposure may be lost after recoveries?",
                "EAD means Exposure at Default. It answers: how much will the bank be exposed to when default happens?",
            ],
            "project_use": [
                "The Credit Risk page lets the user choose a loan and change PD, LGD, and EAD.",
                "The project ranks loans by expected loss, not just by loan size. This is important because a large loan with very low PD can be less risky than a smaller loan with very high PD and LGD.",
                "The same PD, LGD, and EAD concepts also feed IFRS 9, IRB approximation, stress testing, climate risk, and executive dashboard metrics.",
            ],
            "formulas": [
                "Expected Loss = PD x LGD x EAD",
                "Portfolio Expected Loss = sum(PD_i x LGD_i x EAD_i)",
                "Higher PD increases loss likelihood; higher LGD increases loss severity; higher EAD increases the amount exposed.",
            ],
            "memory": [
                "PD = Will they default?",
                "LGD = If they default, how much do we lose?",
                "EAD = How much money is exposed at default?",
                "Expected loss is a three-part multiplication, so all three variables matter.",
            ],
            "questions": [
                {
                    "question": "Why does a high loan amount not always mean high credit risk?",
                    "answer": "Because expected loss depends on PD, LGD, and EAD together. A large well-secured loan with low PD can have lower expected loss than a smaller unsecured loan with high PD and high LGD.",
                },
                {
                    "question": "If PD doubles and LGD/EAD stay constant, what happens to expected loss?",
                    "answer": "Expected loss doubles, because PD is multiplied directly in the ECL formula.",
                },
            ],
            "calculator": "ecl",
        },
        {
            "topic": "IFRS 9 ECL and Staging",
            "definition": [
                "IFRS 9 requires expected credit losses to be recognized before the loss is fully realized.",
                "Stage 1 is for performing exposures with no significant increase in credit risk.",
                "Stage 2 is for exposures with a significant increase in credit risk but not defaulted.",
                "Stage 3 is for defaulted or credit-impaired exposures.",
                "SICR means Significant Increase in Credit Risk. It is the trigger that moves an exposure from Stage 1 to Stage 2.",
            ],
            "project_use": [
                "The IFRS 9 page uses days past due, credit score deterioration, industry stress, and default flag to assign Stage 1, 2, or 3.",
                "The page shows 12-month ECL, lifetime ECL, provision amount, profit impact, retained earnings impact, and CET1 impact.",
                "This connects accounting provisions to regulatory capital because retained earnings are part of CET1.",
            ],
            "formulas": [
                "12-month ECL = 12-month PD x LGD x EAD",
                "Lifetime ECL = Lifetime PD x LGD x EAD",
                "Provision = 12-month ECL for Stage 1",
                "Provision = Lifetime ECL for Stage 2 and Stage 3 in this simplified project",
                "Profit impact = -Provision increase",
                "CET1 impact = -Provision increase, assuming retained earnings reduce CET1",
            ],
            "memory": [
                "Stage 1 = performing.",
                "Stage 2 = risk has increased significantly.",
                "Stage 3 = defaulted or credit-impaired.",
                "Stage 2 is not default. It is the warning zone before default.",
            ],
            "questions": [
                {
                    "question": "Why can a loan move to Stage 2 even without default?",
                    "answer": "Because Stage 2 is based on significant increase in credit risk. A loan can show deterioration through 30+ days past due, credit score decline, or severe sector stress before default happens.",
                },
                {
                    "question": "How does IFRS 9 connect to CET1?",
                    "answer": "Higher ECL increases provisions. Higher provisions reduce profit and retained earnings. Retained earnings are part of CET1, so CET1 can fall.",
                },
            ],
            "calculator": "ifrs9",
        },
        {
            "topic": "Credit Risk Model Development",
            "definition": [
                "Credit risk model development is the process of building, testing, validating, and monitoring a model that estimates borrower default risk.",
                "Discrimination measures whether the model ranks risky borrowers above safer borrowers. AUC is a common discrimination metric.",
                "Calibration measures whether predicted PDs match observed default rates.",
                "A challenger model is compared against a baseline model to test whether it improves performance without adding unacceptable complexity.",
            ],
            "project_use": [
                "The Credit Risk Model Development Lab trains a logistic regression baseline and a gradient boosting challenger model.",
                "It reports AUC, average precision, Brier score, precision, recall, ROC curve, calibration table, confusion matrix, feature importance, risk grades, and PSI.",
                "This makes the project deeper because it shows the model lifecycle, not just the final PD formula.",
            ],
            "formulas": [
                "AUC measures ranking power across thresholds.",
                "Brier Score = mean((Predicted PD - Actual Default)^2)",
                "Precision = True Positives / (True Positives + False Positives)",
                "Recall = True Positives / (True Positives + False Negatives)",
                "PSI = sum((Actual % - Expected %) x ln(Actual % / Expected %))",
            ],
            "memory": [
                "AUC = can the model rank risk?",
                "Calibration = do predicted PDs match reality?",
                "Brier = how far are probabilities from outcomes?",
                "PSI = has the score distribution shifted?",
            ],
            "questions": [
                {
                    "question": "Why is AUC not enough for a PD model?",
                    "answer": "AUC measures ranking, but PD models also need calibration. A model can rank borrowers well while still predicting probabilities that are too high or too low.",
                },
                {
                    "question": "Why compare logistic regression with gradient boosting?",
                    "answer": "Logistic regression is transparent and stable. Gradient boosting can capture nonlinear patterns. Comparing both shows the tradeoff between interpretability and predictive power.",
                },
            ],
            "calculator": "model_metrics",
        },
        {
            "topic": "IFRS 9 Scenario-Weighted ECL",
            "definition": [
                "IFRS 9 ECL should include forward-looking information, not only current borrower data.",
                "Scenario-weighted ECL combines multiple macroeconomic outcomes such as upside, baseline, and downside.",
                "Lifetime PD estimates default probability over the expected life of an exposure, especially relevant for Stage 2 and Stage 3.",
                "An ECL bridge explains why provisions moved between two reporting dates.",
            ],
            "project_use": [
                "The IFRS 9 Scenario ECL Engine calculates loan-level ECL under upside, baseline, and downside scenarios.",
                "It normalizes scenario weights, applies PD/LGD multipliers, approximates lifetime PD, and calculates weighted ECL.",
                "It also shows stage migration and a provision movement bridge.",
            ],
            "formulas": [
                "Lifetime PD = 1 - (1 - 12-month PD) ^ Remaining Life Years",
                "Scenario ECL = Scenario PD x Scenario LGD x EAD",
                "Weighted ECL = sum(Scenario ECL x Scenario Weight)",
                "Closing ECL = Opening ECL + New Lending - Repayments + Stage Migration + Macro Overlay",
            ],
            "memory": [
                "IFRS 9 is forward-looking.",
                "Stage 1 uses 12-month ECL.",
                "Stage 2 and Stage 3 need lifetime ECL.",
                "Scenario weights turn macro uncertainty into a provision number.",
            ],
            "questions": [
                {
                    "question": "Why use scenario weights in IFRS 9?",
                    "answer": "Because expected credit loss should reflect a probability-weighted view of possible future economic outcomes rather than a single forecast.",
                },
                {
                    "question": "What does an ECL bridge explain?",
                    "answer": "It explains movement from opening ECL to closing ECL through new lending, repayments, stage migration, and macro overlays.",
                },
            ],
            "calculator": "scenario_ecl",
        },
    ],
    "Basel, Capital and Regulatory Reporting": [
        {
            "topic": "Basel III Capital and RWA",
            "definition": [
                "Basel III is a global banking framework for capital, leverage, and liquidity resilience.",
                "CET1 is Common Equity Tier 1 capital, the highest quality regulatory capital.",
                "RWA means Risk-Weighted Assets. Assets are weighted by risk instead of being treated equally.",
                "A capital ratio compares capital to RWA, not simply to total assets.",
            ],
            "project_use": [
                "The Basel page calculates RWA, CET1 ratio, Tier 1 ratio, and total capital ratio.",
                "It shows why the composition of assets matters. Two banks with the same total assets can have different RWA if their asset risk differs.",
                "The app also shows how IFRS 9 provision shocks can reduce CET1.",
            ],
            "formulas": [
                "RWA = Exposure x Risk Weight",
                "CET1 Ratio = CET1 / RWA",
                "Tier 1 Ratio = (CET1 + AT1) / RWA",
                "Total Capital Ratio = (CET1 + AT1 + Tier 2) / RWA",
            ],
            "memory": [
                "Capital ratio is not capital divided by total assets. It is capital divided by risk-weighted assets.",
                "CET1 is the strongest capital layer.",
                "RWA translates asset risk into the denominator of capital ratios.",
            ],
            "questions": [
                {
                    "question": "Why can a bank with fewer assets need more capital than a larger bank?",
                    "answer": "Because capital depends on risk-weighted assets. A smaller bank with riskier assets can have higher RWA than a larger bank with safer assets.",
                },
                {
                    "question": "What happens to the CET1 ratio if RWA increases and CET1 stays the same?",
                    "answer": "The CET1 ratio falls because the denominator increases.",
                },
            ],
            "calculator": "basel",
        },
        {
            "topic": "IRB versus Standardized Approach",
            "definition": [
                "The standardized approach uses regulatory risk weights by exposure type.",
                "The Internal Ratings-Based approach uses internal risk estimates, subject to regulatory approval.",
                "IRB uses risk parameters such as PD, LGD, EAD, and maturity to estimate capital needs.",
            ],
            "project_use": [
                "The project compares standardized RWA with a simplified IRB-style estimate.",
                "It clearly labels the IRB calculation as an educational approximation, not the full regulatory formula.",
                "This helps explain that IFRS 9 and IRB may use similar inputs but answer different questions.",
            ],
            "formulas": [
                "Standardized RWA = Exposure x Standardized Risk Weight",
                "Simplified IRB capital estimate = sqrt(PD) x LGD x EAD x 1.06 x maturity adjustment",
                "IRB RWA equivalent = Capital estimate x 12.5",
            ],
            "memory": [
                "IFRS 9 asks: what loss do we expect?",
                "IRB asks: how much capital should we hold?",
                "Same ingredients, different regulatory purpose.",
            ],
            "questions": [
                {
                    "question": "Why should we not claim this project implements full IRB?",
                    "answer": "The real regulatory IRB formula is more complex and requires calibration, correlation, maturity adjustment, downturn LGD, validation, and regulatory approval. The project uses an educational approximation.",
                }
            ],
        },
        {
            "topic": "CRR3 and Basel Final Reforms",
            "definition": [
                "CRR3 is the EU implementation of the final Basel III reforms.",
                "The output floor limits how low internal-model RWA can fall compared with standardized RWA.",
                "Operational risk SMA is a standardized approach for operational risk capital.",
                "CVA is Credit Valuation Adjustment for counterparty credit risk in derivatives.",
            ],
            "project_use": [
                "The CRR3 page shows output floor, operational risk RWA, CVA-lite RWA, total RWA stack, and CET1 ratio impact.",
                "It demonstrates why an internal model can produce low RWA but still be constrained by a standardized floor.",
                "This makes the final Basel III reforms easier to understand from a capital planning view.",
            ],
            "formulas": [
                "Output Floor RWA = Standardized RWA x Floor Rate",
                "Binding Credit RWA = max(Internal Model RWA, Output Floor RWA)",
                "Operational Risk RWA = Operational Risk Capital x 12.5",
                "CVA-lite = Effective Exposure x Counterparty PD x LGD x Maturity x Discount Factor",
            ],
            "memory": [
                "Output floor = model freedom has a floor.",
                "CRR3 is about comparability and reducing excessive RWA variability.",
                "CVA brings derivative counterparty risk into capital.",
            ],
            "questions": [
                {
                    "question": "Why was the output floor introduced?",
                    "answer": "To reduce excessive variability in model-based RWA and make capital ratios more comparable across banks.",
                },
                {
                    "question": "When is the output floor binding?",
                    "answer": "When internal-model RWA is below the standardized RWA multiplied by the floor rate.",
                },
            ],
        },
        {
            "topic": "COREP and FINREP",
            "definition": [
                "COREP is capital reporting. It focuses on capital resources, RWA, leverage, and capital ratios.",
                "FINREP is financial reporting. It focuses on assets, liabilities, equity, income, provisions, and profit.",
                "COREP and FINREP are linked because accounting results can affect regulatory capital.",
            ],
            "project_use": [
                "The reporting page shows FINREP-style profit/equity and COREP-style capital ratios.",
                "It includes a reconciliation view showing risk exposure versus finance exposure.",
                "It illustrates how provisions affect profit and retained earnings, which can affect CET1.",
            ],
            "formulas": [
                "Equity = Assets - Liabilities",
                "Profit = Net Interest Income - Provisions - Operating Costs",
                "CET1 Ratio = CET1 / RWA",
                "Exposure Difference = Finance Exposure - Risk Exposure",
            ],
            "memory": [
                "FINREP = financial statements.",
                "COREP = capital adequacy.",
                "Reconciliation explains why finance and risk numbers may not match.",
            ],
            "questions": [
                {
                    "question": "How do IFRS 9 provisions flow into COREP?",
                    "answer": "Provisions reduce profit and retained earnings. Retained earnings are part of CET1, so COREP capital ratios can be affected.",
                }
            ],
        },
    ],
    "Stress, Liquidity and Planning": [
        {
            "topic": "Stress Testing",
            "definition": [
                "Stress testing estimates how a portfolio or bank behaves under adverse conditions.",
                "A stress scenario can change macroeconomic variables, PD, LGD, revenue, provisions, funding costs, and capital ratios.",
                "Stress testing is used for capital planning, risk appetite, and management actions.",
            ],
            "project_use": [
                "The stress page lets the user adjust PD multiplier, LGD multiplier, and revenue shock.",
                "It shows stressed PD, stressed LGD, stressed ECL, provision increase, CET1 impact, and a capital bridge.",
                "Management actions are linked to the severity of the stressed capital outcome.",
            ],
            "formulas": [
                "Stressed PD = min(Base PD x PD Multiplier, 100%)",
                "Stressed LGD = min(Base LGD x LGD Multiplier, 100%)",
                "Stressed ECL = Stressed PD x Stressed LGD x EAD",
                "Provision Increase = Stressed ECL - Baseline ECL",
            ],
            "memory": [
                "Stress testing asks: what if this bad scenario happens?",
                "Credit stress usually enters through PD and LGD.",
                "Capital impact usually flows through provisions and losses.",
            ],
            "questions": [
                {
                    "question": "What is the difference between baseline, adverse, and severe scenarios?",
                    "answer": "Baseline is the expected path. Adverse is a worse but plausible path. Severe is a more extreme but still useful stress for resilience planning.",
                }
            ],
        },
        {
            "topic": "Geopolitical Reverse Stress Testing",
            "definition": [
                "Reverse stress testing starts from a failure outcome and asks what scenario could cause it.",
                "Instead of asking what a scenario does, it asks what scenario is needed to break a threshold.",
                "A geopolitical reverse stress can include sanctions, trade disruption, cyber attack, energy shock, funding spread widening, or market losses.",
            ],
            "project_use": [
                "The reverse stress page starts with a target CET1 depletion in basis points.",
                "The user changes credit, market, operational, and funding shocks to see whether the target is breached.",
                "The page separates transmission channels so the user can explain how a geopolitical event reaches CET1.",
            ],
            "formulas": [
                "Target Loss = RWA x Target CET1 Depletion bps / 10,000",
                "Total Loss = Provision Increase + Market Loss + Operational Loss + Funding Cost Shock",
                "Stressed CET1 = Opening CET1 - Total Loss",
                "CET1 Depletion bps = (Opening CET1 Ratio - Stressed CET1 Ratio) x 10,000",
            ],
            "memory": [
                "Normal stress: scenario first, outcome second.",
                "Reverse stress: outcome first, scenario second.",
                "Geopolitical risk needs transmission channels: credit, market, funding, operations.",
            ],
            "questions": [
                {
                    "question": "Why is reverse stress testing useful?",
                    "answer": "It helps identify vulnerabilities that may not appear in normal scenarios and forces management to think about what could threaten viability or capital plans.",
                }
            ],
            "calculator": "reverse_stress",
        },
        {
            "topic": "Liquidity, LCR, NSFR and Leverage",
            "definition": [
                "Liquidity risk is the risk that a bank cannot meet cash outflows when due.",
                "Leverage ratio compares Tier 1 capital with total exposure without risk weights.",
                "LCR measures whether the bank has enough high-quality liquid assets for a 30-day stress period.",
                "NSFR measures whether the bank has enough stable funding for its asset profile over a longer horizon.",
            ],
            "project_use": [
                "The liquidity page lets the user change Tier 1 capital, total exposure, HQLA, cash outflows, ASF, and RSF.",
                "It calculates leverage ratio, LCR, NSFR, and compliance status.",
                "This demonstrates that solvency and liquidity are different.",
            ],
            "formulas": [
                "Leverage Ratio = Tier 1 Capital / Total Exposure",
                "LCR = HQLA / 30-day Net Cash Outflows",
                "NSFR = Available Stable Funding / Required Stable Funding",
            ],
            "memory": [
                "Capital answers: can losses be absorbed?",
                "Liquidity answers: can cash outflows be met?",
                "LCR = short-term survival.",
                "NSFR = stable long-term funding.",
            ],
            "questions": [
                {
                    "question": "Can a bank have good capital ratios but still fail?",
                    "answer": "Yes. If deposit outflows or funding stress are severe and liquid assets are insufficient, the bank can face liquidity failure even if capital ratios look acceptable.",
                }
            ],
            "calculator": "liquidity",
        },
        {
            "topic": "Forecasting",
            "definition": [
                "Forecasting estimates future values such as loan balances, deposits, income, provisions, and alert volume.",
                "Forecasts support planning, budgeting, capital projections, and stress testing.",
                "A forecast is not a guarantee. It is a structured assumption about the future.",
            ],
            "project_use": [
                "The forecasting page creates a 12-month forecast using recent trend extrapolation and a macro multiplier.",
                "It includes uncertainty bands to show that forecasts should be interpreted as ranges, not exact values.",
            ],
            "formulas": [
                "Forecast Value = Recent Trend Projection x Macro Multiplier",
                "Upper Band = Forecast + Uncertainty Margin",
                "Lower Band = Forecast - Uncertainty Margin",
            ],
            "memory": [
                "Forecasting creates the base path.",
                "Stress testing shocks the base path.",
                "Planning decisions depend on both.",
            ],
            "questions": [
                {
                    "question": "Why should forecasts include uncertainty bands?",
                    "answer": "Because future values are uncertain. Bands help users avoid treating a point forecast as a precise prediction.",
                }
            ],
        },
    ],
    "Financial Crime and Counterparty Risk": [
        {
            "topic": "Fraud Detection",
            "definition": [
                "Fraud detection identifies transactions that may be unauthorized, abusive, or intentionally deceptive.",
                "Fraud data is usually imbalanced: genuine transactions are common, fraud is rare.",
                "A threshold converts a fraud probability into an alert or no-alert decision.",
            ],
            "project_use": [
                "The fraud page scores synthetic transactions using amount, device mismatch, velocity, and merchant category.",
                "The user changes the threshold and sees alert volume, precision, and recall.",
                "This explains the tradeoff between too many false positives and too many missed fraud cases.",
            ],
            "formulas": [
                "Precision = True Positives / (True Positives + False Positives)",
                "Recall = True Positives / (True Positives + False Negatives)",
                "Alert if Fraud Probability >= Threshold",
            ],
            "memory": [
                "Precision asks: when we alert, how often are we right?",
                "Recall asks: how much fraud did we catch?",
                "Lower threshold catches more fraud but creates more alerts.",
            ],
            "questions": [
                {
                    "question": "Why is class imbalance important in fraud detection?",
                    "answer": "Because fraud is rare. A model can appear accurate by predicting everything as non-fraud, but it would be useless for catching fraud.",
                }
            ],
        },
        {
            "topic": "AML Transaction Monitoring",
            "definition": [
                "AML means Anti-Money Laundering.",
                "AML monitoring looks for suspicious behavior such as structuring, high-risk jurisdictions, rapid movement of funds, and unusual transaction patterns.",
                "AML alerts are often reviewed by investigators because rules can create many false positives.",
            ],
            "project_use": [
                "The AML page scores transactions using amount, country risk, round amount flag, rapid in-out movement, and frequency.",
                "It produces alert reasons and investigation priority.",
                "The project separates AML from fraud because their goals and investigation logic are different.",
            ],
            "formulas": [
                "AML Score = weighted rule score from transaction and customer risk factors",
                "High priority if AML score crosses the high-risk band",
            ],
            "memory": [
                "Fraud asks: is this transaction abusive or unauthorized?",
                "AML asks: does this behavior look suspicious for money laundering or sanctions risk?",
                "AML false positives are expected because monitoring rules are intentionally cautious.",
            ],
            "questions": [
                {
                    "question": "Why do AML systems produce many false positives?",
                    "answer": "Because rules are designed to catch suspicious patterns early, even if many cases later turn out to be legitimate after investigation.",
                }
            ],
        },
        {
            "topic": "XVA Counterparty Risk",
            "definition": [
                "XVA is a family of valuation adjustments used for derivatives.",
                "CVA is Credit Valuation Adjustment for counterparty credit risk.",
                "DVA is Debit Valuation Adjustment for own credit risk.",
                "FVA is Funding Valuation Adjustment for funding costs.",
                "MVA is Margin Valuation Adjustment for initial margin funding costs.",
            ],
            "project_use": [
                "The XVA page creates a simplified expected positive exposure profile.",
                "It estimates CVA, DVA, FVA, MVA, and total XVA cost using transparent assumptions.",
                "The page is not a pricing library; it exists to explain the key risk drivers.",
            ],
            "formulas": [
                "Expected Positive Exposure = Notional x Volatility Proxy x Time Decay x (1 - Collateral Coverage)",
                "CVA = sum(EPE_t x Marginal PD_t x LGD x Discount Factor_t)",
                "FVA = sum(EPE_t x Funding Spread x Discount Factor_t)",
                "MVA = sum(Initial Margin x Margin Funding Spread x Discount Factor_t)",
                "Total XVA Cost = CVA + FVA + MVA - DVA",
            ],
            "memory": [
                "CVA = counterparty may default.",
                "FVA = funding has a cost.",
                "MVA = margin has a funding cost.",
                "Collateral reduces exposure and usually reduces CVA.",
            ],
            "questions": [
                {
                    "question": "Why does collateral reduce CVA?",
                    "answer": "Collateral reduces effective exposure. Lower exposure means lower potential loss if the counterparty defaults.",
                }
            ],
            "calculator": "xva",
        },
    ],
    "Governance, Model Risk and Regulation": [
        {
            "topic": "BCBS 239 Data Governance",
            "definition": [
                "BCBS 239 is about effective risk data aggregation and risk reporting.",
                "It emphasizes that risk reports must be accurate, complete, timely, consistent, and traceable.",
                "Good models are not enough if the data feeding them is wrong or incomplete.",
            ],
            "project_use": [
                "The governance page checks missing PD, invalid loan amount, duplicate customer IDs, stale records, and missing customer IDs.",
                "It shows a data quality score, failed controls, lineage, reconciliation, and audit events.",
                "This connects data quality to IFRS 9, Basel, reporting, and executive decision-making.",
            ],
            "formulas": [
                "Data Quality Score = 1 - Failed Records / Possible Control Checks",
                "Reconciliation Difference = Finance Exposure - Risk Exposure",
            ],
            "memory": [
                "BCBS 239 = reliable risk data and reports.",
                "Traceability means knowing where a number came from.",
                "Reconciliation explains differences before reporting them.",
            ],
            "questions": [
                {
                    "question": "Why can a missing PD value be a governance issue?",
                    "answer": "Because PD feeds ECL, stress testing, capital analysis, and executive reporting. Missing PD can distort provisions and risk metrics.",
                }
            ],
        },
        {
            "topic": "Model Risk Management",
            "definition": [
                "Model risk is the risk of loss or bad decisions from incorrect or misused models.",
                "Model risk management covers development, validation, approval, deployment, monitoring, and retirement.",
                "A model needs evidence, documentation, limitations, monitoring, and ownership.",
            ],
            "project_use": [
                "The model risk page shows model inventory, validation findings, drift checks, lifecycle status, and 1LOD/2LOD issue queues.",
                "The explainability module provides customer-level reason codes.",
                "The drift module compares baseline and current distributions.",
            ],
            "formulas": [
                "Relative Drift = (Current Mean - Baseline Mean) / abs(Baseline Mean)",
                "Model Health can be viewed through performance, stability, explainability, open findings, and monitoring status.",
            ],
            "memory": [
                "A model is not finished when it is trained.",
                "Validation challenges the model before approval.",
                "Monitoring checks whether the model remains reliable after deployment.",
            ],
            "questions": [
                {
                    "question": "What is the difference between model development and model validation?",
                    "answer": "Development builds the model. Validation independently reviews whether it is fit for purpose, properly documented, tested, and controlled.",
                }
            ],
        },
        {
            "topic": "EU AI Act Governance",
            "definition": [
                "The EU AI Act introduces governance expectations for AI systems, especially high-risk systems.",
                "Financial use cases such as credit scoring can require strong controls around data, transparency, oversight, documentation, and monitoring.",
                "The project treats AI governance as an extension of model risk management.",
            ],
            "project_use": [
                "The AI governance page classifies an illustrative AI use case and calculates a weighted control score.",
                "Controls include risk management, data governance, documentation, logging, explainability, human oversight, robustness, and monitoring.",
                "It also includes a fairness-gap check using group approval rates.",
            ],
            "formulas": [
                "Control Score = sum(weights for implemented controls)",
                "Fairness Gap = abs(Approval Rate Group A - Approval Rate Group B)",
            ],
            "memory": [
                "High-risk AI needs evidence.",
                "Explainability without monitoring is incomplete.",
                "Human oversight means humans can challenge or override important automated outcomes.",
            ],
            "questions": [
                {
                    "question": "Why is explainability important in credit scoring?",
                    "answer": "Because borrowers, managers, validators, and regulators need understandable reasons for decisions and evidence that the model is not operating unfairly or unpredictably.",
                }
            ],
            "calculator": "ai_governance",
        },
        {
            "topic": "DORA Operational Resilience",
            "definition": [
                "DORA focuses on digital operational resilience in financial services.",
                "It covers ICT risk management, incident reporting, resilience testing, third-party risk, and oversight of critical providers.",
                "RTO means Recovery Time Objective. RPO means Recovery Point Objective.",
            ],
            "project_use": [
                "The DORA page classifies ICT incidents using affected users, downtime, data loss, critical service impact, and third-party involvement.",
                "It calculates a resilience score based on RTO, RPO, testing, and exit plan availability.",
                "It includes a small third-party provider register.",
            ],
            "formulas": [
                "Incident Score = weighted score for users, downtime, data loss, criticality, and third-party involvement",
                "Resilience Score = RTO met + RPO met + tested this year + exit plan available",
            ],
            "memory": [
                "DORA = can the digital operation survive disruption?",
                "RTO = how quickly must we recover?",
                "RPO = how much data loss can we tolerate?",
                "Third-party risk matters because outsourced services can still break the bank's operations.",
            ],
            "questions": [
                {
                    "question": "Why does third-party risk matter under DORA?",
                    "answer": "Because a bank remains accountable for critical services even when technology is outsourced. It needs oversight, testing, and exit plans.",
                }
            ],
            "calculator": "dora",
        },
        {
            "topic": "ESG and Climate Credit Risk",
            "definition": [
                "Climate risk can affect credit risk through transition risk and physical risk.",
                "Transition risk comes from policy, technology, carbon pricing, and business model changes.",
                "Physical risk comes from climate events affecting assets, operations, or collateral values.",
            ],
            "project_use": [
                "The climate page applies sector and physical-risk multipliers to PD.",
                "It increases LGD when collateral value declines.",
                "It calculates climate-adjusted ECL and ECL increase.",
            ],
            "formulas": [
                "Climate PD Multiplier = Sector Multiplier x Physical Risk Multiplier x Carbon Price Add-on x Disorderly Transition Add-on",
                "Adjusted PD = Base PD x Climate PD Multiplier",
                "Adjusted LGD = Base LGD + Collateral Decline x LGD Add-on",
                "Climate ECL = Adjusted PD x Adjusted LGD x EAD",
            ],
            "memory": [
                "Transition risk mainly hits borrower cash flow and PD.",
                "Physical risk can hit collateral and LGD.",
                "Climate risk becomes financial risk through credit parameters.",
            ],
            "questions": [
                {
                    "question": "How can carbon pricing affect credit risk?",
                    "answer": "Carbon pricing can increase costs for carbon-intensive sectors, weakening borrower profitability and increasing PD.",
                }
            ],
            "calculator": "climate",
        },
        {
            "topic": "1LOD and 2LOD Workflow",
            "definition": [
                "1LOD means First Line of Defense. It owns and manages risks in day-to-day operations.",
                "2LOD means Second Line of Defense. It provides independent oversight, challenge, monitoring, and guidance.",
                "Audit trail records what changed, who changed it, and why.",
            ],
            "project_use": [
                "The model risk and governance pages include issue queues and audit logs.",
                "A data quality issue can move from 1LOD investigation to 2LOD challenge and closure tracking.",
                "This shows ownership versus oversight rather than treating governance as a static checklist.",
            ],
            "formulas": [
                "No mathematical formula is needed. The control logic is workflow-based: identify issue, assign owner, assess impact, remediate, challenge, close, audit.",
            ],
            "memory": [
                "1LOD owns the risk.",
                "2LOD challenges the risk management.",
                "Audit records the evidence.",
            ],
            "questions": [
                {
                    "question": "Why should 2LOD not own the remediation?",
                    "answer": "Because 1LOD owns and manages the operational risk. 2LOD provides independent challenge and oversight, which would be weakened if it owned the remediation itself.",
                }
            ],
        },
    ],
}


def all_topics() -> list[str]:
    return [topic["topic"] for topics in STUDY_GUIDE.values() for topic in topics]


def _topic_lookup() -> dict[str, tuple[str, dict[str, object]]]:
    return {topic["topic"]: (category, topic) for category, topics in STUDY_GUIDE.items() for topic in topics}


def render_study_guide() -> None:
    st.subheader("Documentation & Study Guide")
    st.write("Use this page as a structured study notebook. Pick a topic from the tree, review the definitions and formulas, then test yourself with questions.")
    study_mode = st.segmented_control("Study mode", ["Read", "Quiz"], default="Read")

    if study_mode == "Quiz":
        render_quiz_mode()
        return

    lookup = _topic_lookup()
    left, right = st.columns([1, 2.2])

    with left:
        search = st.text_input("Search topics", placeholder="Example: IFRS 9, DORA, XVA, CET1")
        available_topics: list[str] = []
        for category, topics in STUDY_GUIDE.items():
            for topic in topics:
                name = str(topic["topic"])
                if search and search.lower() not in name.lower() and search.lower() not in category.lower():
                    continue
                available_topics.append(name)

        selected_topic = st.selectbox("Select topic", available_topics or all_topics())
        category, topic = lookup[selected_topic]
        st.caption("Topic tree")
        for category_name, topics in STUDY_GUIDE.items():
            with st.expander(category_name, expanded=not search):
                for topic_item in topics:
                    name = str(topic_item["topic"])
                    if search and search.lower() not in name.lower() and search.lower() not in category_name.lower():
                        continue
                    st.write(f"- {name}")

    with right:
        st.caption(category)
        st.header(str(topic["topic"]))
        tabs = st.tabs(["Meaning", "Project Use", "Formulas", "Memory", "Practice", "Interactive"])

        with tabs[0]:
            _render_bullets(topic["definition"])
        with tabs[1]:
            _render_bullets(topic["project_use"])
        with tabs[2]:
            _render_bullets(topic["formulas"])
        with tabs[3]:
            _render_bullets(topic["memory"])
        with tabs[4]:
            _render_questions(topic["questions"])
        with tabs[5]:
            _render_calculator(str(topic.get("calculator", "")))


def _render_bullets(items: object) -> None:
    for item in items if isinstance(items, list) else []:
        st.write(f"- {item}")


def _render_questions(items: object) -> None:
    questions = items if isinstance(items, list) else []
    for index, item in enumerate(questions, start=1):
        question = item.get("question", "") if isinstance(item, dict) else ""
        answer = item.get("answer", "") if isinstance(item, dict) else ""
        with st.expander(f"Q{index}. {question}"):
            st.write(answer)


def _render_calculator(kind: str) -> None:
    if not kind:
        st.info("This topic is mainly conceptual. Use the other tabs to revise the definitions, project usage, formulas, and questions.")
        return

    if kind == "ecl":
        pd_value = st.slider("PD", 0.0, 1.0, 0.04, 0.005, key="study_ecl_pd")
        lgd_value = st.slider("LGD", 0.0, 1.0, 0.45, 0.01, key="study_ecl_lgd")
        ead_value = st.number_input("EAD", min_value=0.0, value=100_000.0, step=5_000.0, key="study_ecl_ead")
        st.metric("Expected loss", f"EUR {pd_value * lgd_value * ead_value:,.0f}")
        st.code(f"ECL = {pd_value:.3f} x {lgd_value:.3f} x {ead_value:,.0f}", language="text")

    elif kind == "ifrs9":
        dpd = st.slider("Days past due", 0, 120, 35, key="study_ifrs9_dpd")
        score_change = st.slider("Credit score change", -200, 50, -75, key="study_ifrs9_score")
        default_flag = st.checkbox("Default flag", key="study_ifrs9_default")
        if default_flag or dpd >= 90:
            stage = "Stage 3"
            reason = "Default or 90+ days past due."
        elif dpd >= 30 or score_change <= -60:
            stage = "Stage 2"
            reason = "Significant increase in credit risk."
        else:
            stage = "Stage 1"
            reason = "Performing exposure."
        st.metric("Simplified stage", stage)
        st.write(reason)

    elif kind == "basel":
        exposure = st.number_input("Exposure", min_value=1.0, value=1_000_000.0, step=50_000.0, key="study_basel_exp")
        risk_weight = st.slider("Risk weight", 0.0, 1.5, 0.75, 0.05, key="study_basel_rw")
        cet1 = st.number_input("CET1", min_value=1.0, value=120_000.0, step=10_000.0, key="study_basel_cet1")
        rwa_value = exposure * risk_weight
        st.metric("RWA", f"EUR {rwa_value:,.0f}")
        st.metric("CET1 ratio", f"{cet1 / rwa_value:.2%}" if rwa_value else "n/a")

    elif kind == "model_metrics":
        tp = st.number_input("True positives", min_value=0, value=25, step=1, key="study_model_tp")
        fp = st.number_input("False positives", min_value=0, value=15, step=1, key="study_model_fp")
        fn = st.number_input("False negatives", min_value=0, value=10, step=1, key="study_model_fn")
        predicted_pd = st.slider("Predicted PD", 0.0, 1.0, 0.08, 0.01, key="study_model_pred")
        actual_default = st.selectbox("Actual outcome", [0, 1], key="study_model_actual")
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        brier = (predicted_pd - actual_default) ** 2
        st.metric("Precision", f"{precision:.1%}")
        st.metric("Recall", f"{recall:.1%}")
        st.metric("One-observation Brier contribution", f"{brier:.4f}")

    elif kind == "scenario_ecl":
        upside = st.number_input("Upside ECL", min_value=0.0, value=80_000.0, step=5_000.0, key="study_scen_up")
        baseline = st.number_input("Baseline ECL", min_value=0.0, value=100_000.0, step=5_000.0, key="study_scen_base")
        downside = st.number_input("Downside ECL", min_value=0.0, value=165_000.0, step=5_000.0, key="study_scen_down")
        downside_weight = st.slider("Downside weight", 0.0, 1.0, 0.25, 0.05, key="study_scen_down_w")
        upside_weight = st.slider("Upside weight", 0.0, 1.0, 0.20, 0.05, key="study_scen_up_w")
        baseline_weight = max(0.0, 1 - upside_weight - downside_weight)
        weighted = upside * upside_weight + baseline * baseline_weight + downside * downside_weight
        st.metric("Baseline weight", f"{baseline_weight:.0%}")
        st.metric("Weighted ECL", f"EUR {weighted:,.0f}")

    elif kind == "reverse_stress":
        rwa_value = st.number_input("RWA", min_value=1.0, value=50_000_000.0, step=1_000_000.0, key="study_rev_rwa")
        target_bps = st.slider("Target CET1 depletion bps", 50, 600, 300, 25, key="study_rev_bps")
        st.metric("Loss needed", f"EUR {rwa_value * target_bps / 10_000:,.0f}")
        st.code("Loss needed = RWA x target bps / 10,000", language="text")

    elif kind == "liquidity":
        hqla = st.number_input("HQLA", min_value=1.0, value=120.0, step=10.0, key="study_liq_hqla")
        outflows = st.number_input("30-day net cash outflows", min_value=1.0, value=100.0, step=10.0, key="study_liq_out")
        asf = st.number_input("Available stable funding", min_value=1.0, value=105.0, step=10.0, key="study_liq_asf")
        rsf = st.number_input("Required stable funding", min_value=1.0, value=100.0, step=10.0, key="study_liq_rsf")
        st.metric("LCR", f"{hqla / outflows:.1%}")
        st.metric("NSFR", f"{asf / rsf:.1%}")

    elif kind == "ai_governance":
        implemented = st.slider("Implemented control points", 0, 100, 72, key="study_ai_score")
        gap_a = st.slider("Approval rate group A", 0.0, 1.0, 0.68, 0.01, key="study_ai_a")
        gap_b = st.slider("Approval rate group B", 0.0, 1.0, 0.55, 0.01, key="study_ai_b")
        st.metric("Control score", f"{implemented}/100")
        st.metric("Fairness gap", f"{abs(gap_a - gap_b):.1%}")

    elif kind == "dora":
        rto = st.slider("RTO hours", 0.5, 24.0, 4.0, 0.5, key="study_dora_rto")
        actual = st.slider("Actual recovery hours", 0.5, 48.0, 6.0, 0.5, key="study_dora_actual")
        st.metric("RTO met?", "Yes" if actual <= rto else "No")
        st.write("If actual recovery is greater than RTO, remediation is required.")

    elif kind == "climate":
        base_pd = st.slider("Base PD", 0.0, 0.5, 0.04, 0.005, key="study_clim_pd")
        multiplier = st.slider("Climate PD multiplier", 1.0, 3.0, 1.6, 0.05, key="study_clim_mult")
        st.metric("Adjusted PD", f"{min(base_pd * multiplier, 1.0):.2%}")

    elif kind == "xva":
        epe = st.number_input("Expected positive exposure", min_value=0.0, value=1_000_000.0, step=50_000.0, key="study_xva_epe")
        pd_value = st.slider("Counterparty PD", 0.0, 0.2, 0.025, 0.001, key="study_xva_pd")
        lgd_value = st.slider("LGD", 0.0, 1.0, 0.60, 0.01, key="study_xva_lgd")
        st.metric("One-period CVA estimate", f"EUR {epe * pd_value * lgd_value:,.0f}")

    else:
        st.info("No calculator is attached to this topic yet.")


def study_guide_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [{"category": category, "topic": topic["topic"]} for category, topics in STUDY_GUIDE.items() for topic in topics]
    )


QUIZ_BANK = [
    {
        "topic": "PD, LGD, EAD and Expected Loss",
        "question": "Which formula calculates expected credit loss?",
        "options": ["PD x LGD x EAD", "CET1 / RWA", "HQLA / Cash Outflows"],
        "answer": "PD x LGD x EAD",
        "explanation": "Expected loss combines default likelihood, loss severity, and exposure.",
    },
    {
        "topic": "IFRS 9 ECL and Staging",
        "question": "What does Stage 2 represent in IFRS 9?",
        "options": ["Significant increase in credit risk but not defaulted", "No credit risk", "Always defaulted"],
        "answer": "Significant increase in credit risk but not defaulted",
        "explanation": "Stage 2 is the SICR stage. It is not the same as default.",
    },
    {
        "topic": "Basel III Capital and RWA",
        "question": "What is the denominator of the CET1 ratio?",
        "options": ["Risk-weighted assets", "Total deposits", "Net interest income"],
        "answer": "Risk-weighted assets",
        "explanation": "CET1 ratio = CET1 capital / RWA.",
    },
    {
        "topic": "CRR3 and Basel Final Reforms",
        "question": "When does the output floor bind?",
        "options": ["When internal-model RWA is below the floor", "When LCR is above 100%", "When fraud alerts increase"],
        "answer": "When internal-model RWA is below the floor",
        "explanation": "The output floor creates a lower bound based on standardized RWA.",
    },
    {
        "topic": "BCBS 239 Data Governance",
        "question": "Why does missing PD matter?",
        "options": ["It can distort ECL and risk reports", "It only affects UI color", "It improves calibration automatically"],
        "answer": "It can distort ECL and risk reports",
        "explanation": "PD feeds ECL, stress testing, capital analysis, and reporting.",
    },
    {
        "topic": "Model Risk Management",
        "question": "What does calibration check?",
        "options": ["Whether predicted PDs match observed default rates", "Whether code imports", "Whether assets equal liabilities"],
        "answer": "Whether predicted PDs match observed default rates",
        "explanation": "A model can rank well but still produce poorly calibrated probabilities.",
    },
    {
        "topic": "DORA Operational Resilience",
        "question": "What does RTO mean?",
        "options": ["Recovery Time Objective", "Risk Transfer Option", "Regulatory Threshold Output"],
        "answer": "Recovery Time Objective",
        "explanation": "RTO is the target time within which a service should be recovered.",
    },
    {
        "topic": "XVA Counterparty Risk",
        "question": "What does CVA mainly capture?",
        "options": ["Counterparty credit risk", "Loan origination cost", "Deposit liquidity risk"],
        "answer": "Counterparty credit risk",
        "explanation": "CVA adjusts derivative value for counterparty default risk on positive exposure.",
    },
]


def render_quiz_mode() -> None:
    st.write("Answer the questions first, then expand the explanation. Use the score summary to see where to revise.")
    topic_filter = st.selectbox("Quiz topic", ["All topics"] + sorted({item["topic"] for item in QUIZ_BANK}))
    questions = [item for item in QUIZ_BANK if topic_filter == "All topics" or item["topic"] == topic_filter]
    correct = 0
    answered = 0
    for index, item in enumerate(questions, start=1):
        st.markdown(f"**Q{index}. {item['question']}**")
        selected = st.radio("Choose one", item["options"], key=f"quiz_{topic_filter}_{index}", index=None)
        if selected is not None:
            answered += 1
            if selected == item["answer"]:
                correct += 1
                st.success("Correct")
            else:
                st.error(f"Incorrect. Correct answer: {item['answer']}")
            with st.expander("Explanation"):
                st.write(item["explanation"])
    st.metric("Score", f"{correct}/{len(questions)}" if answered else "Not started")
