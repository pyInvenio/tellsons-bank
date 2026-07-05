package com.tellsons.payments;

import java.util.Optional;

public interface AccountRepository {
    Optional<Account> find(String accountId);
}
