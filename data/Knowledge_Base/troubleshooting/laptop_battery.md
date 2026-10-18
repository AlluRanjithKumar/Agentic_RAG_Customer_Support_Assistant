# AeroBook Battery Diagnostic Guide

**Document ID:** RT-TS-BAT-2.1  
**Effective date:** 2026-06-10  
**Applies to:** AeroBook Air 14 and AeroBook Pro 16

This guide diagnoses runtime, charging and battery-health complaints.

## Safety triage — perform first

If the battery is swollen, smoking, hissing, unusually hot, leaking, or separating the enclosure, tell the customer to stop using and charging the laptop.

Do not ask the customer to:

- Press the enclosure closed.
- Remove an internal battery.
- Continue charging for diagnostic purposes.
- Mail a swollen battery without specialist instructions.

Mark the case as `SAFETY_ESCALATION`. Safety triage replaces the normal calibration procedure.

## Charging diagnosis

1. Confirm that the wall outlet works.
2. Inspect the cable and charging port without inserting metal objects.
3. Use the supplied charger. The AeroBook Pro 16 requires 100W for full performance. A lower-wattage charger may show “connected, not charging” under heavy load without indicating a defect.
4. Shut down the laptop for five minutes, reconnect power, and observe the charging indicator.
5. If neither USB-C port charges an AeroBook Air 14 with a known-good 65W-or-higher charger, escalate for hardware diagnosis.

## Short runtime

Record screen brightness, active applications, power mode and whether the complaint occurs during gaming or video calls. High workload can reduce runtime without proving a defect.

1. Install pending firmware and operating-system updates.
2. Generate the Ranjith Diagnostics battery report.
3. Record design capacity, full-charge capacity and cycle count.
4. If no safety symptom exists, charge to 100% and keep it connected for 30 minutes.
5. Use the laptop normally until it reaches 10%, then recharge uninterrupted to 100%.
6. Generate the report again. Do not perform more than one calibration cycle for the same case.

## Decision rules

- Capacity below 60%, cycle count at or below 500, and within battery coverage: potential warranty claim.
- Capacity below 60% but cycle count above 500: normal consumable wear unless a safety symptom exists.
- Capacity at or above 80%: investigate applications and power settings before hardware service.
- Capacity from 60% through 79%: compare the result with workload and product age; do not automatically approve or reject the claim.

Final eligibility is governed by RT-POL-WAR-3.2 and the product catalog, not this troubleshooting guide alone.
