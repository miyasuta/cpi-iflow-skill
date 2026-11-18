# cpi-iflow-skill

Claude skills for SAP Cloud Integration (CPI) integration flows (iFlows). (Work in progress)

| Skill | What it does | Needs |
|---|---|---|
| [cpi-iflow-design](cpi-iflow-design/SKILL.md) | Turns a goal ("read the orders from A, map them, send them to B") into an iFlow design that follows SAP's Integration Flow Design Guidelines, writes it to `docs/<design name>.md` with a flow diagram, asks the open questions one at a time, and waits for your approval. Writes no XML. | Nothing: no tenant, no MCP server. Also useful if you build iFlows only in the CPI designer. |
| [cpi-iflow-build](cpi-iflow-build/SKILL.md) | Builds an iFlow through an MCP server: writes it with settings taken from a reference of values confirmed by a deployment and a call that worked, validates, stops for your approval, then pushes, deploys and calls it. Also builds an approved design from cpi-iflow-design. | An MCP server for Cloud Integration with the capabilities below. |

## Using them together

1. Tell Claude the goal. **cpi-iflow-design** writes the design to `docs/<design name>.md` in your project: assumptions, a flow diagram (Mermaid) and flow table, why this shape, externalized values, build order, questions (and the interfaces, when the design spans several iFlows). In the conversation it shows the diagram and a short summary.
2. It asks the open questions one at a time, with its recommendation, and updates the file after each answer. Then approve the design, or ask for changes.
3. Ask to build it. **cpi-iflow-build** reads the approved design file, looks up each row's settings in its references, and tells you about values it has not verified.
4. It writes and validates through the MCP server, then stops and shows what it wrote. After your approval it pushes, deploys and calls the iFlow.

The design is handed over as the file under `docs/`. Its format is the contract between the two skills: it is defined in [cpi-iflow-design/references/process.md](cpi-iflow-design/references/process.md) ("Declaration format"), and [cpi-iflow-build/references/from-declaration.md](cpi-iflow-build/references/from-declaration.md) relies on it. Change both together.

For small edits to an existing iFlow (a header value, an Address, one Content Modifier at a given place), use cpi-iflow-build alone.

## Setup

### 1. Install the skills: clone and symlink

Fork the repository first (recommended): the references grow in your copy as you use the build skill (see "How the skill grows"). Then clone it anywhere; `<path-to-clone>` is a placeholder:

```bash
git clone https://github.com/<your-fork>/cpi-iflow-skill.git <path-to-clone>
mkdir -p ~/.claude/skills
ln -s <path-to-clone>/cpi-iflow-design ~/.claude/skills/cpi-iflow-design
ln -s <path-to-clone>/cpi-iflow-build  ~/.claude/skills/cpi-iflow-build
```

Symlink both folders: the build skill links to the design skill's declaration format through `../cpi-iflow-design/`. With symlinks, `git pull` takes effect immediately. Restart Claude Code so that both skills show up in the skill list.

### 2. Register an MCP server (for cpi-iflow-build only)

cpi-iflow-design needs no MCP server. cpi-iflow-build works with any MCP server that offers these capabilities (it names roles, not tools):

| Role | Needed |
|---|---|
| Write (create and edit iFlows) | Required |
| Validate | Required |
| Push to the tenant | Required |
| Deploy | Required |
| Call the deployed iFlow | Required |
| Diff (what was written, compared with the tenant) | Optional |
| Import from the tenant | Optional |

An example is [cpi-saper-dev-mcp](https://github.com/devstylator/cpi-saper-dev-mcp) (tools such as `iflow_edit`, `iflow_validate`, `iflow_diff`). These are facts about that server, not requirements of the skill:

- **Register it per project, with project scope** (`.mcp.json` in the project where you use it), not user-wide. Then the tools that can change a tenant are not available in every project.
- Its configuration and service keys stay in that project's `.cpi/` folder, outside Git. Never commit them.
- Its confirmation dialogs appear only in the terminal CLI (`claude`). In the Claude Desktop Code tab and in the VS Code extension they are not shown and are rejected, so there the server needs `unattendedTestMode: true`, limited with `allowedPackages`.

The skill also uses mcp-sap-docs as an optional MCP server for the SAP documentation step of "Unknown values".

Follow the server's own documentation for installing it and creating the service key.

## How the skill grows

The references of cpi-iflow-build are a settings reference that grows as you use it. When a step, adapter or setting is not in the references, the skill finds its value (SAP documentation, or a field you set once in the CPI designer), writes it, and stops for your approval before pushing. Then:

- **Only values that deployed and then worked when called are added.** A value that was validated or pushed but failed to deploy, or that deployed but whose call failed or gave a wrong result, is never added. A script can deploy and still fail at run time.
- **The skill proposes, you approve.** It adds nothing before you agree: one row in the Settings table of the component's file, plus a pitfall only if something surprised it.
- **The skill never commits.** It tells you which files changed. They stay uncommitted in your clone until you commit them together later (and, if you like, offer them upstream with a pull request).
