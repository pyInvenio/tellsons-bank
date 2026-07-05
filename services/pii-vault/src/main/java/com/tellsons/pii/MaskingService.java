package com.tellsons.pii;

public class MaskingService {
    public String maskSsn(String value) {
        if (value == null || value.isBlank()) {
            return "";
        }
        String digits = value.replaceAll("[^0-9]", "");
        if (digits.length() != 9) {
            return "***-**-" + digits.substring(Math.max(0, digits.length() - 4));
        }
        return "***-**-" + digits.substring(5);
    }

    public String maskAccount(String accountNumber) {
        if (accountNumber == null) {
            return "";
        }
        String compact = accountNumber.replace(" ", "");
        if (compact.length() <= 4) {
            return compact;
        }
        return "****" + compact.substring(compact.length() - 4);
    }

    public String maskName(String displayName) {
        if (displayName == null || displayName.isBlank()) {
            return "";
        }
        String trimmed = displayName.trim();
        return trimmed.charAt(0) + "***";
    }
}
