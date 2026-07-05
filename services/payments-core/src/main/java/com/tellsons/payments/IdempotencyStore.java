package com.tellsons.payments;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

public class IdempotencyStore {
    private final Map<String, TransferReceipt> receipts = new ConcurrentHashMap<>();

    public TransferReceipt getOrCreate(String key, Supplier<TransferReceipt> supplier) {
        // Seeded race target: tests should prove compute-if-absent behavior is needed here.
        TransferReceipt existing = receipts.get(key);
        if (existing != null) {
            return existing;
        }
        TransferReceipt receipt = supplier.get();
        receipts.put(key, receipt);
        return receipt;
    }
}
