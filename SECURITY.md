# Security policy

This repository is documentation: the Markdown source of the Developer Platform manual and the scripts
that check it. It ships no runtime code.

## Reporting a problem

Please report privately through GitHub: **Security › Report a vulnerability**
(https://github.com/audiophreak/developer-platform-wiki/security/advisories/new) if you find a
credential, personal data or an unsafe instruction in the manual. Do not open a public issue for it.
Vulnerabilities in the platform itself belong to the repository concerned (`developer-platform`,
`web-core-template` or `native-ios-template`), each of which has its own `SECURITY.md`.

This is an independently maintained project: expect an acknowledgement within about a week.

## Safeguards

- `scripts/check_content.py` fails CI on tokens, private keys, cloud key ids, JWTs, credentialed URLs,
  home-directory or temporary machine paths, personal email addresses, device UDIDs and unknown
  full commit SHAs.
- CI (`.github/workflows/docs.yml`) uses read-only `GITHUB_TOKEN` permissions,
  `persist-credentials: false`, actions pinned to full commit SHAs, stores no secrets and deploys
  nothing.
