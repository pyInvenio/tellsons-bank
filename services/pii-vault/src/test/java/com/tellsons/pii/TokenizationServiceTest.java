package com.tellsons.pii;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

class TokenizationServiceTest {

    private TokenizationService service;

    @BeforeEach
    void setUp() {
        service = new TokenizationService();
    }

    @Nested
    class NamespaceValidation {

        @ParameterizedTest
        @NullAndEmptySource
        @ValueSource(strings = {"   ", "\t"})
        void rejectsNullBlankOrWhitespaceNamespace(String ns) {
            IllegalArgumentException ex = assertThrows(
                    IllegalArgumentException.class,
                    () -> service.tokenize(ns, "cust_test_001"));
            assertEquals("namespace required", ex.getMessage());
        }
    }

    @Nested
    class ValueValidation {

        @ParameterizedTest
        @NullAndEmptySource
        @ValueSource(strings = {"   ", "\t"})
        void rejectsNullBlankOrWhitespaceValue(String val) {
            IllegalArgumentException ex = assertThrows(
                    IllegalArgumentException.class,
                    () -> service.tokenize("ssn", val));
            assertEquals("value required", ex.getMessage());
        }
    }

    @Nested
    class HappyPath {

        @Test
        void producesDeterministicToken() {
            String token1 = service.tokenize("ssn", "000-00-0000");
            String token2 = service.tokenize("ssn", "000-00-0000");
            assertEquals(token1, token2);
        }

        @Test
        void tokenStartsWithPrefix() {
            String token = service.tokenize("ssn", "000-00-0000");
            assertTrue(token.startsWith("tok_"));
        }

        @Test
        void tokenHasExpectedLength() {
            // "tok_" (4 chars) + 24 hex chars = 28 total
            String token = service.tokenize("acct", "acct_test_source");
            assertEquals(28, token.length());
        }

        @Test
        void differentNamespaceProducesDifferentToken() {
            String ssnToken = service.tokenize("ssn", "000-00-0000");
            String acctToken = service.tokenize("account", "000-00-0000");
            assertNotEquals(ssnToken, acctToken);
        }

        @Test
        void differentValueProducesDifferentToken() {
            String token1 = service.tokenize("ssn", "000-00-0000");
            String token2 = service.tokenize("ssn", "123-45-0000");
            assertNotEquals(token1, token2);
        }

        @Test
        void tokenizesVeryLongValue() {
            String longValue = "cust_test_" + "x".repeat(500);
            String token = service.tokenize("profile", longValue);
            assertTrue(token.startsWith("tok_"));
            assertEquals(28, token.length());
        }

        @Test
        void tokenContainsOnlyHexAfterPrefix() {
            String token = service.tokenize("ssn", "000-00-0000");
            String hex = token.substring(4);
            assertTrue(hex.matches("[0-9a-f]{24}"));
        }
    }
}
