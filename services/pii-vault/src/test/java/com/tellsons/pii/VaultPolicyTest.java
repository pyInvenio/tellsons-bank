package com.tellsons.pii;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

class VaultPolicyTest {

    private VaultPolicy policy;

    @BeforeEach
    void setUp() {
        policy = new VaultPolicy();
    }

    @Test
    void allowsExportForPublicClassification() {
        assertTrue(policy.allowsExport(PiiClassification.PUBLIC));
    }

    @Test
    void allowsExportForTokenizedClassification() {
        assertTrue(policy.allowsExport(PiiClassification.TOKENIZED));
    }

    @Test
    void deniesExportForInternalClassification() {
        assertFalse(policy.allowsExport(PiiClassification.INTERNAL));
    }

    @Test
    void deniesExportForRestrictedClassification() {
        assertFalse(policy.allowsExport(PiiClassification.RESTRICTED));
    }

    @ParameterizedTest
    @EnumSource(PiiClassification.class)
    void allClassificationsReturnBoolean(PiiClassification classification) {
        boolean result = policy.allowsExport(classification);
        // Every classification should produce a deterministic boolean
        boolean resultAgain = policy.allowsExport(classification);
        assertTrue(result == resultAgain);
    }
}
