# Ranjith's Tech Synthetic Knowledge Base

This directory contains completely fictional data for a student-built agentic RAG customer-support project. **Ranjith's Tech is fictional.** No real customer or company information is included.

## Dataset snapshot

- Knowledge-base version: `2026.09`
- Default policy effective date: `2026-07-01`
- Currency: Indian rupees (INR)
- Support timezone: Asia/Kolkata
- Primary market: India

## File map

| Path | Format | Intended use |
|---|---|---|
| `Knowledge_Base/policies/warranty_policy.md` | Markdown | Warranty coverage, exclusions and tier-specific exceptions |
| `Knowledge_Base/policies/returns_refunds.txt` | Text | Return windows, fees and refund timing |
| `Knowledge_Base/policies/shipping_replacement.md` | Markdown | Delivery, damage and replacement rules |
| `Knowledge_Base/products/product_catalog.json` | JSON | Structured product and plan facts |
| `Knowledge_Base/troubleshooting/laptop_battery.md` | Markdown | Battery diagnosis and safety escalation |
| `Knowledge_Base/troubleshooting/connectivity_guide.md` | Markdown | Wi-Fi and Bluetooth decision tree |
| `Knowledge_Base/troubleshooting/audio_devices.md` | Markdown | Headphone troubleshooting procedures |
| `Knowledge_Base/faq/customer_faq.json` | JSON | Short frequently asked questions |
| `Knowledge_Base/tickets/historical_tickets.jsonl` | JSONL | Similar-case retrieval examples |
| `evaluation/questions.json` | JSON | Ground-truth routing and retrieval cases |

## Important cross-document rules

The documents intentionally contain rules that must be combined:

1. Product warranty duration comes from the product catalog, but eligibility and exclusions come from the warranty policy.
2. A defective product can avoid the opened-item restocking fee, but only after the troubleshooting or inspection requirement is satisfied.
3. Dead-on-arrival reports use the replacement workflow, not the ordinary return workflow.
4. Marketplace purchases may receive technical support, but refunds must normally be handled by the marketplace seller.
5. Battery health warnings can override the normal troubleshooting flow and require immediate escalation.
6. When two rules conflict, use the document with the later effective date. A product-specific rule overrides a general rule when effective dates are equal.

## Recommended metadata during ingestion

Attach at least: `source`, `category`, `effective_date`, `product_family`, `document_version`, and `section`.

Do not treat this README as a customer policy source. It is dataset documentation.
