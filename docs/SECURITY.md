# Security and privacy

Treat word lists, prompts, outputs, and transcripts as potentially sensitive. The public repository
stores none of the historical production artifacts.

Use least-privilege provider execution. Review explicit CLI extra arguments. Do not bake Codex
authentication, tokens, user profiles, or local configuration into a container. CI uses only the
offline mock and requires no model secret.

The public audit checks a bounded set of common secrets, machine paths, suspicious private
filenames, large files, and required release assets. It cannot guarantee absence of all secrets or
establish copyright ownership. Combine it with Git history inspection and human review.

Report vulnerabilities privately to the repository owner once a public contact method exists. No
contact address is invented in this initial public release.
