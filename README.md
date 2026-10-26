# cpi-iflow-skill

Claude skills for SAP Cloud Integration (CPI) integration flows (iFlows). (Work in progress)

| Skill | What it does | Needs |
|---|---|---|
| [cpi-iflow-design](cpi-iflow-design/SKILL.md) | Turns a goal ("read the orders from A, map them, send them to B") into an iFlow design that follows SAP's Integration Flow Design Guidelines, and declares it for your approval. Writes no XML. | Nothing: no tenant, no Git repository. Also useful if you build iFlows only in the CPI designer. |
| [cpi-iflow-build](cpi-iflow-build/SKILL.md) | Edits iFlows as files in a Git repository connected through Cloud Integration Git Access; you Pull them into CPI. Builds an approved design: writes the parts it has verified samples for and tells you how to build the rest in the CPI designer. | A Git Access repository; you work in the CPI web UI (Pull, Deploy). |

## Using them together

1. Tell Claude the goal. **cpi-iflow-design** declares the design: assumptions, flow table, why this shape, externalized values, build order, open questions (and the interfaces, when the design spans several iFlows).
2. Review the declaration and approve it, or ask for changes.
3. In the same conversation, ask to build it. **cpi-iflow-build** takes the approved declaration, marks each row as written by the skill or by you in the CPI designer, and waits for your OK before writing.
4. The build skill writes its rows; you Pull in CPI and build the remaining rows in the designer.

The declaration is handed over in the conversation, not as a file. Its format is the contract between the two skills: it is defined in [cpi-iflow-design/references/process.md](cpi-iflow-design/references/process.md) ("Declaration format"), and [cpi-iflow-build/references/from-declaration.md](cpi-iflow-build/references/from-declaration.md) relies on it. Change both together.

For small edits to an existing iFlow (a header value, an Address, one Content Modifier at a given place), use cpi-iflow-build alone.

## Installing

Copy both skill folders side by side into a skills folder, for example `.claude/skills/cpi-iflow-design/` and `.claude/skills/cpi-iflow-build/`. The build skill links to the design skill's declaration format through `../cpi-iflow-design/`.
