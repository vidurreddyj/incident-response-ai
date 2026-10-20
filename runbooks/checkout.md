# Checkout incident runbook
1. Confirm error-rate spike and affected endpoints.
2. Compare deployed SHA with the candidate commits and inspect their diffs.
3. Test the payment-token null-handling path.
4. If confirmed, follow your team's approval process to roll back.
5. Watch metrics until error rate returns to baseline.
