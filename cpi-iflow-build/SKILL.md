---
name: cpi-iflow-build
description: Use when building or changing an SAP Cloud Integration (CPI) integration flow (iFlow) through an MCP server that can write, validate, push, deploy and call iFlows - requires the MCP server's iFlow editing tools; without them the skill only points to the setup. Covers HTTPS sender, Content Modifier (headers, exchange properties, body), Groovy Script, Router on a request header with Allowed Header(s), Request Reply with an HTTP receiver (GET or POST, None or OAuth2 Client Credentials), Exception Subprocess returning an error response, and externalized parameters. Also use to build an iFlow from a design declaration the user approved (from the cpi-iflow-design skill), and when a step, adapter or setting is not in the references yet, so that its value is found, verified by a deployment and added instead of guessed.
---

# CPI iFlow build

This skill is a **settings reference** for SAP Cloud Integration iFlows, plus the workflow to build with it through an MCP server. Every value in [references/](references/) was confirmed by a successful deployment **and a call that did what the iFlow is meant to do**: a value is in the references only if an iFlow deployed with it and ran correctly. A deployment alone proves nothing about a script or an expression: it can deploy and still fail at run time.

## Rules

- **Pass every setting explicitly, from the references.** This covers every setting the references list for the steps and adapters used, including the integration-flow settings they list; a setting the references do not cover is an unknown value. Never rely on the MCP server's default values: a default may differ from the references, change with a new server version, or change when the server is replaced.
- **Never guess a value and push it.** A value that is not in the references goes through "Unknown values".
- **Never write `.iflw` or other iFlow files by hand.** Writing goes through the MCP server only.
- **Stop once before push** (Workflow step 5), even when a declaration was approved: approving a design is not approving the values written for it.
- Never write credentials (client secrets, tokens, passwords) anywhere. Write only the name of a credential the person deployed in Security Material.
- Leave everything the task does not need unchanged.

## Workflow

1. **Check the prerequisite.** If no MCP tool for writing iFlows is available, tell the person to set up an MCP server as described in the setup section of the repository README (https://github.com/miyasuta/cpi-iflow-skill), and stop. Check also which of the capabilities in "Required MCP capabilities" the server has.
2. **Take the input**: an approved design declaration from cpi-iflow-design (read [references/from-declaration.md](references/from-declaration.md)), or a request whose steps are already clear. A goal without steps goes to cpi-iflow-design first.
3. **Read before writing**: the reference file of every component the iFlow uses, and [references/externalized-parameters.md](references/externalized-parameters.md) when something is externalized. List the settings each step needs; any setting not found goes through "Unknown values".
4. **Write and validate.** Write through the MCP server, passing every value from the references. Run the validation and fix every error it reports before going on.
5. **Stop before push.** Show a summary of the diff of what was written (without diff, the list of every value written, per step). Mark every place where an unknown (unverified) value was used, and say what it is. End your turn and wait for the person's explicit approval. A correction is not approval: fix, validate, and show the summary again.
6. **Push, deploy, call.** After approval, push and deploy. If the deployment fails, report the error, fix the cause, and return to step 5. When it succeeds, call the iFlow to check that it does its job; for a declaration, use the test call its build order names.
7. **Propose additions.** If a value that was not in the references deployed successfully and the call then worked as intended, follow "Growing the references".

## Unknown values

A value is unknown when the references do not have it: a setting of a component with a file, or any setting of a component with no file. A flow shape the references do not describe (for example a step placement, routes joining an End, or an end type not listed) is unknown too: flag it at the stop before push; it becomes verified only by a successful deployment followed by a call that works. For each one:

1. **References.** Look again, including the pitfalls of the component's file and related files.
2. **SAP documentation.** Search it (with mcp-sap-docs if it is available) for the field and its possible values. Do not use the Neo environment documentation.
3. **Designer.** If the documentation does not settle the exact key and value, ask the person to set that field once in the CPI designer and save the iFlow. Import the iFlow from the tenant and read the key and value from the diff. Without the import capability, this step is not available: ask the person for the value instead.
4. **Write and stop.** Write the value and stop before push (Workflow step 5), naming the value as unknown and saying where it came from (documentation, designer, the person).
5. **Deploy and call.** If the deployment succeeds and the call then does what the iFlow is meant to do (read the message log when it does not), the value is verified: propose the addition ("Growing the references"). If the deployment fails, or it succeeds but the call fails or gives a wrong result, the value is not verified: never add it to the references.

Never invent a key or a value that none of these steps produced.

## Growing the references

After a deployment succeeds and a call confirms that the iFlow works with a value that was not in the references, propose adding it. Do not add anything before the person agrees.

- **Where**: the file of that component in `references/components/`. For a new component, a new file in the same form as the existing ones (a short description, a `## Settings` table, a `## Pitfalls` list). For an externalized field, [references/externalized-parameters.md](references/externalized-parameters.md).
- **What**: one row in the Settings table (UI field, UI choice, key, value) and, only if something surprised you (a rejected form, a silent failure, a value that differs from what the designer shows), one pitfall. No dates, no commit hashes, no links to evidence: being in the references means it deployed and ran correctly.
- **Only values confirmed by a working call.** A value that was validated, pushed or deployed but whose call failed or gave a wrong result, or that was never called, is never added. A deployment that succeeds while the call fails (for example a script that does not compile) is worth a pitfall for the verified value, not a row for the failed one.
- **After writing**: do no git operation (no commit, no branch, no push). Tell the person which files changed and that the changes are uncommitted; they commit them together later.

## Required MCP capabilities

The skill names roles, not tools. Examples are the tools of cpi-saper-dev-mcp.

| Role | Needed | Example tool |
|---|---|---|
| Write (create and edit iFlows) | Required | `iflow_edit` |
| Validate | Required | `iflow_validate` |
| Push to the tenant | Required | |
| Deploy | Required | |
| Call the deployed iFlow | Required | |
| Diff (what was written, compared with the tenant) | Optional | `iflow_diff` |
| Import from the tenant | Optional | |

- Without **diff**: at the stop before push, show the list of every value written, per step.
- Without **import from the tenant**: step 3 of "Unknown values" (set it once in the designer) is not available; ask the person for the value.
- Without any required role: say which one is missing and stop.

## References

Read only what the task needs.

| Task | Read |
|---|---|
| Building from an approved cpi-iflow-design declaration: reading it, deciding each row, showing unverified rows before push, several iFlows | [references/from-declaration.md](references/from-declaration.md) |
| HTTPS sender: Address, CSRF protection, authorization | [references/components/https-sender.md](references/components/https-sender.md) |
| Content Modifier: header and property rows, body, versions | [references/components/content-modifier.md](references/components/content-modifier.md) |
| Groovy Script step and its script file; reading a request header | [references/components/groovy-script.md](references/components/groovy-script.md) |
| Router: conditions on a header, default route, End per route, Allowed Header(s) | [references/components/router.md](references/components/router.md) |
| Request Reply step | [references/components/request-reply.md](references/components/request-reply.md) |
| HTTP receiver: Address, Query, Method, Authentication, Credential Name | [references/components/http-receiver.md](references/components/http-receiver.md) |
| Exception Subprocess returning an error response | [references/components/exception-subprocess.md](references/components/exception-subprocess.md) |
| Externalized parameters: which fields, default and configured values | [references/externalized-parameters.md](references/externalized-parameters.md) |
