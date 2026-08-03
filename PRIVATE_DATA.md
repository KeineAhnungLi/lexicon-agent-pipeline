# Private data and local operation

Keep these items outside version control:

- production word lists and source spreadsheets;
- historical or complete generated/reviewed outputs;
- raw agent transcripts and prompts containing private entries;
- local `project.json`, `.env` files, API credentials, tokens, and authentication state;
- human evaluation records containing names or other personal information;
- proprietary dictionary text, licensed corpora, and uncertain third-party examples.

Local workspaces belong under an ignored `workspace/`, `workspaces/`, or another ignored descendant
of the repository. The CLI refuses to use the configuration directory itself as a workspace and
will not replace a non-empty workspace without both `--force-reset` and `--yes`.

If private data is accidentally committed, stop publication, rotate any exposed credential, remove
the material from Git history using an appropriate history-rewrite process, and obtain repository
owner approval before force-updating a remote. A normal follow-up deletion does not erase Git
history.
