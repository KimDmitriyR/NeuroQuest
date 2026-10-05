"""Versioning for the legal documents a parent agrees to at registration.

Bump CURRENT_TERMS_VERSION whenever the Terms of Use or Privacy Policy
text changes in a way that matters (not for typo fixes). This lets a
future "you agreed to an older version, please re-confirm" flow compare
ParentAccount.terms_version against this value - that re-consent flow
isn't built yet, this is just the version tag to make it possible later.

Keep in sync with frontend/src/pages/TermsPage.tsx and PrivacyPage.tsx.
"""

CURRENT_TERMS_VERSION = "2026-01-v1"
