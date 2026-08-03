# Case study: migrating a private 4,812-entry run

A private predecessor processed a 4,812-entry lexicon in batches using generation, review, and
structural validation. The migration goal was to preserve the reproducible method without
publishing the source list, spreadsheet, model outputs, uncertain examples, or transcripts.

The public redesign made boundaries executable:

- configuration paths became relative and local configuration became ignored;
- semantic authorship moved behind an agent-provider interface;
- generation and review became distinct invocations and states;
- generated-only recovery now proceeds to review instead of regenerating automatically;
- merge accepts reviewed artifacts only and revalidates them;
- prompt/schema versions, timestamps, provider identity, and hashes became provenance;
- destructive reset requires an explicit two-part confirmation;
- 15 newly authored synthetic examples replaced source-adjacent samples;
- offline demo, CI, documentation, and a public-release audit became first-class.

No claim is made here about the private run’s linguistic accuracy or model performance. Its row
count supplies project context only.
