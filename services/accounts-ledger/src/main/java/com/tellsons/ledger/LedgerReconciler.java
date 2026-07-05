package com.tellsons.ledger;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class LedgerReconciler {
    public List<ReconciliationFinding> reconcile(List<LedgerEntry> entries) {
        Map<String, List<LedgerEntry>> byAccount = entries.stream()
                .collect(Collectors.groupingBy(LedgerEntry::accountId));
        List<ReconciliationFinding> findings = new ArrayList<>();

        for (Map.Entry<String, List<LedgerEntry>> account : byAccount.entrySet()) {
            BigDecimal debits = BigDecimal.ZERO;
            BigDecimal credits = BigDecimal.ZERO;
            String currency = null;
            for (LedgerEntry entry : account.getValue()) {
                if (entry.debit().signum() < 0 || entry.credit().signum() < 0) {
                    findings.add(new ReconciliationFinding("NEGATIVE_COMPONENT", account.getKey(), entry.entryId()));
                }
                if (currency == null) {
                    currency = entry.currency();
                } else if (!currency.equals(entry.currency())) {
                    findings.add(new ReconciliationFinding("MIXED_CURRENCY", account.getKey(), entry.entryId()));
                }
                debits = debits.add(entry.debit());
                credits = credits.add(entry.credit());
            }
            if (debits.compareTo(credits) != 0) {
                findings.add(new ReconciliationFinding("OUT_OF_BALANCE", account.getKey(), debits + " != " + credits));
            }
        }

        return findings;
    }
}
