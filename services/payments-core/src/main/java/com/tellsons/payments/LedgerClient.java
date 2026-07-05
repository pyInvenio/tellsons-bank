package com.tellsons.payments;

public interface LedgerClient {
    void post(LedgerEntry entry);
}
