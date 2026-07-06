package com.tellsons.pii;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class PiiRecordTest {

    @Test
    void constructsWithSyntheticData() {
        PiiRecord record = new PiiRecord("cust_test_001", "***-**-0000", "tok_abc123");
        assertEquals("cust_test_001", record.customerId());
        assertEquals("***-**-0000", record.maskedSsn());
        assertEquals("tok_abc123", record.accountToken());
    }

    @Test
    void supportsNullFields() {
        PiiRecord record = new PiiRecord(null, null, null);
        assertEquals(null, record.customerId());
        assertEquals(null, record.maskedSsn());
        assertEquals(null, record.accountToken());
    }
}
