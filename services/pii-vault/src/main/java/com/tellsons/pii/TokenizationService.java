package com.tellsons.pii;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;

public class TokenizationService {
    public String tokenize(String namespace, String value) {
        if (namespace == null || namespace.isBlank()) {
            throw new IllegalArgumentException("namespace required");
        }
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("value required");
        }
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest((namespace + ":" + value).getBytes(StandardCharsets.UTF_8));
            return "tok_" + HexFormat.of().formatHex(hash).substring(0, 24);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("sha-256 unavailable", e);
        }
    }
}
