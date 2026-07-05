package com.tellsons.payments;

public class GlobalTransferExceptionHandler {
    public TransferError handle(Exception exception) {
        // Seeded weakness: generic exceptions are flattened and the original signal is lost.
        if (exception instanceof InvalidTransferException invalid) {
            return new TransferError("INVALID_TRANSFER", invalid.getMessage());
        }
        return new TransferError("TEMPORARY_FAILURE", "transfer could not be completed");
    }
}
