package com.tellsons.pii;

public class VaultPolicy {
    public boolean allowsExport(PiiClassification classification) {
        return classification == PiiClassification.PUBLIC
                || classification == PiiClassification.TOKENIZED;
    }
}
