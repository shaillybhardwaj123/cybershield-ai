# 🧪 CyberShield AI: Agent Evaluation Pipeline

This document explains the evaluation design, scoring metrics, test cases, and quality checks used to assess the agent intelligence of **CyberShield AI**.

---

## 1. Evaluation Methodology

Automated and interactive testing checks that the multi-agent system correctly logs and classifies threats. We test on three criteria:
1. **Scam Detection Accuracy (Recall & Precision)**: Ensuring that safe URLs/messages are not flagged as threats, and that actual scams are caught with correct threat classifications.
2. **Explanation Quality & Accessibility**: Explanations must avoid technical jargon so students and non-technical users can understand *why* a message is flagged.
3. **System Performance (Latency)**: Latency is tracked through the `observability_traces` database table to optimize the pipeline and check response thresholds.

---

## 2. Test Dataset Schema

We evaluate against 8 representative test cases representing:
- **Advance Fee Internships**: E.g., fake Google internship requesting a registration fee.
- **Scholarship Scams**: E.g., fake student welfare portals requiring deposit payments.
- **Phishing Credential Theft**: Account block threat language directing to typosquatted domains.
- **Safe Communications**: Legitimate campus links and placement cell notifications.
- **Credential Harvesting Links**: Misleading subdomains requesting bank credentials.
- **Typosquatting Domains**: e.g., base domain base `micr0soft` mimicker.

### Evaluation Cases Details
| Description | Input Sample | Expected Verdict | Expected Category |
|-------------|--------------|------------------|-------------------|
| Google Job Fee | Select for WFH, pay ₹499 fee, contact on Telegram @Hr | DANGEROUS | fake job offer |
| Netbanking Phish | SBI account suspended. Verify NetBanking at link | DANGEROUS | phishing |
| Real Scholarship | Register at official portal scholarships.gov.in | SAFE | safe |
| Typosquatted Domain | Update Windows credentials at micr0soft.com | DANGEROUS | phishing / URL scam |
| Real Placement | Placement Cell meeting in Hall B at 3 PM | SAFE | safe |
| YouTube Subscribe | Earn ₹2000 per hour liking videos. HR @Youtube | SUSPICIOUS | fake job offer |

---

## 3. Visual Dashboard Pipeline

Our Admin Page features a custom evaluation trigger. Clicking "Run Agent Eval Suite" does the following:
1. Feeds the test dataset to the API `/api/scan`.
2. Computes real-time latency and verdict output comparison.
3. Renders a pass/fail table on the dashboard showing accuracy rates.

This pipeline can also be run via the CLI using:
```bash
agents-cli eval dataset synthesize
agents-cli eval run
```
This prints the standard grading reports based on metrics configured in `tests/eval/eval_config.yaml`.
