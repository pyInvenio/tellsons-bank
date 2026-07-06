package com.tellsons.pii;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class TokenizationServiceTest {
    private final TokenizationService service = new TokenizationService();

    @ParameterizedTest
    @ValueSource(strings = {"", "   "})
    void rejectsBlankNamespace(String namespace) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> service.tokenize(namespace, "cust_test_0001"));
        assertEquals("namespace required", exception.getMessage());
    }

    @Test
    void rejectsNullNamespace() {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> service.tokenize(null, "cust_test_0001"));
        assertEquals("namespace required", exception.getMessage());
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "   "})
    void rejectsBlankValue(String value) {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> service.tokenize("acct_test_namespace", value));
        assertEquals("value required", exception.getMessage());
    }

    @Test
    void rejectsNullValue() {
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> service.tokenize("acct_test_namespace", null));
        assertEquals("value required", exception.getMessage());
    }

    @Test
    void isDeterministicForSameInputs() {
        String first = service.tokenize("acct_test_namespace", "cust_test_0001");
        String second = service.tokenize("acct_test_namespace", "cust_test_0001");

        assertEquals(first, second);
        assertTrue(first.startsWith("tok_"));
        assertEquals(28, first.length());
    }

    @Test
    void changesWhenNamespaceChanges() {
        String first = service.tokenize("acct_test_namespace_one", "cust_test_0001");
        String second = service.tokenize("acct_test_namespace_two", "cust_test_0001");

        assertNotEquals(first, second);
    }

    @Test
    void changesWhenValueChanges() {
        String first = service.tokenize("acct_test_namespace", "cust_test_0001");
        String second = service.tokenize("acct_test_namespace", "cust_test_0002");

        assertNotEquals(first, second);
    }

    @Test
    void tokenHasExpectedPrefixAndLength() {
        String token = service.tokenize("acct_test_namespace", "cust_test_0001");

        assertTrue(token.startsWith("tok_"));
        assertEquals(28, token.length());
    }
}
