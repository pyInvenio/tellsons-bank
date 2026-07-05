package com.tellsons.payments;

public class InvalidTransferException extends RuntimeException {
    public InvalidTransferException(String message) {
        super(message);
    }
}
