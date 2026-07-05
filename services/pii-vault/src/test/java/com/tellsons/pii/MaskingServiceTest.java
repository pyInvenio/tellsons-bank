package com.tellsons.pii;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class MaskingServiceTest {
    @Test
    void masksCanonicalSsn() {
        assertEquals("***-**-0000", new MaskingService().maskSsn("000-00-0000"));
    }
}
