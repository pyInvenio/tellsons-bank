package com.tellsons.payments;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class GlobalTransferExceptionHandlerTest {
    private final GlobalTransferExceptionHandler handler = new GlobalTransferExceptionHandler();

    @Test
    void mapsInvalidTransferException() {
        TransferError error = handler.handle(new InvalidTransferException("x"));

        assertEquals("INVALID_TRANSFER", error.code());
        assertEquals("x", error.message());
    }

    @Test
    void flattensGenericException() {
        TransferError error = handler.handle(new RuntimeException("boom"));

        assertEquals("TEMPORARY_FAILURE", error.code());
        assertEquals("transfer could not be completed", error.message());
    }
}
