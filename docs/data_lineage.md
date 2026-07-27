# Data Lineage

The lineage model is a typed educational graph. It does not require a graph database.

Minimum flow:

```text
Loan Origination System
-> Customer Master
-> Credit Risk Data Mart
-> PD/LGD/EAD Engines
-> IFRS 9 ECL Engine
-> Finance Provision
-> FINREP-style Report
-> CET1 Bridge
-> COREP-style Report
```

Each node has an owner, steward, description, transformation, mapped controls and downstream nodes. The app supports upstream and downstream tracing from a selected node.

This helps explain why a source-data defect can affect PD, LGD, EAD, ECL, provisions, CET1 and regulatory-style reporting.
