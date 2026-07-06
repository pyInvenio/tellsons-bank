package com.tellsons.pii;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

class MaskingServiceTest {

    private MaskingService service;

    @BeforeEach
    void setUp() {
        service = new MaskingService();
    }

    @Nested
    class MaskSsn {

        @Test
        void masksCanonicalSsn() {
            assertEquals("***-**-0000", service.maskSsn("000-00-0000"));
        }

        @Test
        void masksNineDigitsWithoutDashes() {
            assertEquals("***-**-0000", service.maskSsn("000000000"));
        }

        @Test
        void masksNineDigitsWithSpacesAndPunctuation() {
            assertEquals("***-**-0000", service.maskSsn("000 00 0000"));
        }

        @ParameterizedTest
        @NullAndEmptySource
        @ValueSource(strings = {"   ", "\t"})
        void returnsEmptyForNullBlankOrWhitespace(String input) {
            assertEquals("", service.maskSsn(input));
        }

        @Test
        void masksFewerThanNineDigits() {
            // "12345" → 5 digits, not 9, suffix = digits.substring(max(0,5-4)) = digits.substring(1)
            assertEquals("***-**-2345", service.maskSsn("12345"));
        }

        @Test
        void masksFewerThanFourDigits() {
            // "12" → 2 digits, suffix = digits.substring(max(0,2-4)) = digits.substring(0) = "12"
            assertEquals("***-**-12", service.maskSsn("12"));
        }

        @Test
        void masksSingleDigit() {
            assertEquals("***-**-7", service.maskSsn("7"));
        }

        @Test
        void masksMoreThanNineDigits() {
            // "00000000001234" → 14 digits, not 9, suffix = digits.substring(max(0,14-4)) = digits.substring(10)
            assertEquals("***-**-1234", service.maskSsn("00000000001234"));
        }

        @Test
        void stripsNonDigitCharactersBeforeCounting() {
            // "abc1def2ghi3" → digits = "123", length 3, not 9
            assertEquals("***-**-123", service.maskSsn("abc1def2ghi3"));
        }

        @Test
        void masksOversizedSsnLikeInput() {
            String oversized = "1".repeat(50);
            String result = service.maskSsn(oversized);
            assertEquals("***-**-1111", result);
        }
    }

    @Nested
    class MaskAccount {

        @Test
        void returnsEmptyForNull() {
            assertEquals("", service.maskAccount(null));
        }

        @Test
        void returnsUnmaskedWhenFourOrFewerChars() {
            assertEquals("1234", service.maskAccount("1234"));
        }

        @Test
        void returnsUnmaskedForSingleChar() {
            assertEquals("7", service.maskAccount("7"));
        }

        @Test
        void returnsEmptyStringForEmptyInput() {
            assertEquals("", service.maskAccount(""));
        }

        @Test
        void masksAccountLongerThanFour() {
            assertEquals("****5678", service.maskAccount("acct_test_12345678"));
        }

        @Test
        void stripsSpacesBeforeMasking() {
            // "1234 5678" → compact "12345678" → "****5678"
            assertEquals("****5678", service.maskAccount("1234 5678"));
        }

        @Test
        void handlesExactlyFourCharsAfterSpaceRemoval() {
            assertEquals("5678", service.maskAccount("56 78"));
        }

        @Test
        void handlesVeryLongAccountNumber() {
            String longAcct = "acct_test_" + "0".repeat(100);
            String result = service.maskAccount(longAcct);
            assertEquals("****0000", result);
        }
    }

    @Nested
    class MaskName {

        @ParameterizedTest
        @NullAndEmptySource
        @ValueSource(strings = {"   ", "\t\n"})
        void returnsEmptyForNullBlankOrWhitespace(String input) {
            assertEquals("", service.maskName(input));
        }

        @Test
        void masksStandardName() {
            assertEquals("T***", service.maskName("Test User"));
        }

        @Test
        void masksSingleCharacterName() {
            assertEquals("A***", service.maskName("A"));
        }

        @Test
        void trimsLeadingWhitespace() {
            assertEquals("T***", service.maskName("  Test"));
        }

        @Test
        void trimsTrailingWhitespace() {
            assertEquals("T***", service.maskName("Test  "));
        }

        @Test
        void masksAccentedName() {
            assertEquals("É***", service.maskName("Émile"));
        }

        @Test
        void masksUnicodeNameWithCombiningMark() {
            // 'A' followed by combining acute accent (U+0301)
            String combining = "A\u0301naïs";
            String result = service.maskName(combining);
            assertEquals("A***", result);
        }

        @Test
        void masksVeryLongName() {
            String longName = "D" + "e".repeat(200) + "vin";
            assertEquals("D***", service.maskName(longName));
        }
    }
}
