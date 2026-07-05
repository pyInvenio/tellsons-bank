from __future__ import annotations

from dataclasses import dataclass
import unicodedata


@dataclass(frozen=True)
class CustomerProfile:
    customer_id: str
    display_name: str
    email_domain: str
    risk_segment: str


class ProfileNormalizer:
    def normalize(self, customer_id: str, display_name: str, email: str) -> CustomerProfile:
        if not customer_id.startswith("cust_test_"):
            raise ValueError("synthetic customer id required")
        cleaned_name = " ".join(unicodedata.normalize("NFKC", display_name).split())
        if "@" not in email:
            raise ValueError("email domain required")
        domain = email.rsplit("@", 1)[1].lower()
        segment = "REVIEW" if domain in {"example.invalid", "test.invalid"} else "STANDARD"
        return CustomerProfile(customer_id, cleaned_name, domain, segment)
