package com.tellsons.pii;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;

class MaskingServiceTest {
    private final MaskingService service = new MaskingService();

    @Test
    void masksCanonicalSsn() {
        assertEquals("***-**-0000", service.maskSsn("000-00-0000"));
    }

    @ParameterizedTest
    @NullSource
    @ValueSource(strings = {"", "   "})
    void masksMissingSsnAsEmptyString(String input) {
        assertEquals("", service.maskSsn(input));
    }

    @ParameterizedTest
    @CsvSource({
            "12,***-**-12",
            "'000 00-0000',***-**-0000",
            "0000000000000,***-**-0000"
    })
    void masksNonCanonicalSsnBySuffix(String input, String expected) {
        assertEquals(expected, service.maskSsn(input));
    }

    @Test
    void masksAccountNullAsEmptyString() {
        assertEquals("", service.maskAccount(null));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "1234", "12 34"})
    void leavesShortAccountsUnchanged(String input) {
        assertEquals(input.replace(" ", ""), service.maskAccount(input));
    }

    @ParameterizedTest
    @CsvSource({
            "'4111 1111 1111 1111',****1111",
            "'acct test 12345678901234567890',****7890"
    })
    void masksLongAccountsByLastFourDigits(String input, String expected) {
        assertEquals(expected, service.maskAccount(input));
    }

    @ParameterizedTest
    @NullSource
    @ValueSource(strings = {"", "   "})
    void masksMissingDisplayNameAsEmptyString(String input) {
        assertEquals("", service.maskName(input));
    }

    @ParameterizedTest
    @CsvSource({
            "Q,Q***",
            "'  Test User  ',T***",
            "'  Ånaïs Demo  ',Å***"
    })
    void masksDisplayNameUsingTrimmedFirstCharacter(String input, String expected) {
        assertEquals(expected, service.maskName(input));
    }
}
