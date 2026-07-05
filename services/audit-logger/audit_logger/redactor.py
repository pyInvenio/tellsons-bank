import re


class Redactor:
    SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    ACCOUNT = re.compile(r"\bacct_[a-zA-Z0-9_]{6,}\b")

    def redact(self, message: str) -> str:
        redacted = self.SSN.sub("***-**-****", message)
        redacted = self.ACCOUNT.sub("acct_***", redacted)
        return redacted
