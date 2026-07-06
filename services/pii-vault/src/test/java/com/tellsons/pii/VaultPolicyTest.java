package com.tellsons.pii;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class VaultPolicyTest {
    private final VaultPolicy policy = new VaultPolicy();

    @ParameterizedTest
    @CsvSource({
            "PUBLIC,true",
            "TOKENIZED,true",
            "INTERNAL,false",
            "RESTRICTED,false"
    })
    void evaluatesExportPermissions(PiiClassification classification, boolean expected) {
        assertEquals(expected, policy.allowsExport(classification));
    }
}
