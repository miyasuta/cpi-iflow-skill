# Git Access workflow

How an iFlow travels between Cloud Integration (CPI) and the Git repository, what Pull and Push do, how conflicts behave, and what to ignore when reading diffs.

Every fact below was observed on a real tenant. Commit hashes link to the evidence in [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples) (S01 on `main`, `X01_Sandbox` on `exp`). Anything not confirmed is marked **unverified**.

## Repository layout

- The Git Access target is a whole repository. A sub-path cannot be chosen.
- Each iFlow is connected to exactly one branch, but different iFlows in the same repository can use different branches ([dbb80e2]).
- Each iFlow is a folder named after the iFlow ([92c8b77], [dbb80e2]):

  ```
  <iFlow name>/
  ├── META-INF/MANIFEST.MF
  ├── metainfo.prop
  └── src/main/resources/
      ├── parameters.prop
      ├── parameters.propdef
      └── scenarioflows/integrationflow/<name>.iflw
  ```

- **Do not infer the iFlow name from the `.iflw` file name.** A copied iFlow keeps the original file name (`X01_Sandbox/.../S01_ContentModifier.iflw`) and also the original HTTPS sender Address. The iFlow name is `Bundle-Name` / `Bundle-SymbolicName` in `META-INF/MANIFEST.MF` ([dbb80e2]).

## Development round trip

Steps on the CPI side are done by the user in the CPI web UI. Ask the user to do them and to report the result.

1. **Before editing locally**, the user pushes every change saved in the CPI designer. "Unpushed changes" means changes saved in the designer but not yet pushed.
2. Edit the files locally, run `scripts/check_iflw.py`, commit, and push to the branch connected to the iFlow.
3. In CPI: **Pull** → open the iFlow in the designer and check the Problems tab → **Save** → **Deploy** → call the iFlow to test it.
4. In CPI: **Push**, so the repository receives the content as CPI normalizes it (see below). Pull that commit locally before the next edit.

## Pull

| Fact | Evidence |
|---|---|
| With no unpushed UI changes, Pull takes over the remote content (the result equals a full replacement). Changed values, added and reordered table rows, added steps, and changed versions were all applied. | [bb5e4f0], [95802b3], [395e94c], [834f0c6], [6dab58a] |
| With unpushed UI changes, if the remote changed **the same place**, Pull is rejected: `The pull operation cannot be performed due to conflicts with the remote integration flow. Resolve the conflicts by manually aligning your local flow with the remote version.` | [9affede] (same Content Modifier body changed on both sides) |
| When Pull is rejected, nothing in CPI changes (no partial import). | [9affede] |
| With unpushed UI changes, if the remote changed a **different place**, Pull merges: the remote change arrives and the UI changes stay. In the observed case, two different properties of the same Content Modifier (`headerTable` remotely, `wrapContent` in the UI) merged. The exact merge granularity (for example, different rows of the same table) is **unverified**. | [c200359] |
| With unpushed UI changes, a remote change to the iFlow Description (`bpmn2:documentation`) is **not** taken over, and Pull still reports success. The next Push then overwrites the remote Description with the CPI value. | [24a9667], [c200359], [17f81ee] |
| A successful Pull therefore does not prove that every remote change arrived. Check in the designer or in the diff of the next Push. | [24a9667] |
| SAP documents only Push and Pull as Git operations. A UI action to resolve a conflict (for example, discarding the UI changes) is not documented; how to resolve one in practice is **unverified**. | [Using Git Operations](https://help.sap.com/docs/SAP_INTEGRATION_SUITE/9519789d5664487f8b9cd89eba514477/12347021da2f446b899aa2f780703c27.html?locale=en-US&state=PRODUCTION&version=CLOUD) |

### When Pull fails or the iFlow does not open cleanly

| Symptom | Cause | Evidence |
|---|---|---|
| Pull fails with `Artifact pull failed due to unexpected error` (no details). | A step was added without `bpmndi` (no shape for the new step, no edge for the new flow, and the existing edge not re-targeted). Adding consistent `bpmndi` fixed it. Which of these gaps alone causes the failure is **unverified**. See [iflw-structure.md](iflw-structure.md). | [56e0a25], [395e94c] |
| Pull succeeds, but the designer shows a validation error (`SAXParseException`) in the Problems tab and a whole Header or Property table looks empty. | A table value contains a `<` or `&` that is escaped only once. See [escaping.md](escaping.md). | [a517576], [7827ffc] |

## Push

| Fact | Evidence |
|---|---|
| After a merging Pull, Push creates a normal commit on top of the remote head containing both the remote and the UI changes. | [17f81ee] |
| Pushing from CPI while the remote is ahead and has not been pulled: behavior is **unverified**. Always Pull before Push. | — |

## iFlow Description

| Fact | Evidence |
|---|---|
| The Description is `bpmn2:documentation` (`textFormat="text/plain"`) directly under `bpmn2:collaboration` `Collaboration_1` in the `.iflw`. | [af09698] |
| Editing its text locally and pulling (with no unpushed UI changes) shows it on the General tab, and it survives the next Push. Only its `id` is regenerated. | [bb5e4f0], [758b608], [519851d], [92c8b77] |
| `description` in `metainfo.prop` has no effect: a local change does not appear in the UI after Pull and is reset to empty by the next Push. **Do not edit `metainfo.prop`.** | [3dbd8d9], [af09698], [bb5e4f0], [758b608] |

## What CPI changes when the designer saves

### Edits made locally

| Fact | Evidence |
|---|---|
| Hand-written IDs (`CallActivity_Local1`, `SequenceFlow_Local1`, …) are kept. | [395e94c] → [57b3074] |
| Table rows, row order, and double escaping are not rewritten. | [95802b3] → [1b5d158] |
| Older `cmdVariantUri` / `componentVersion` pairs are not migrated, and table keys left out of an older step are not added. | [834f0c6] → [fa1090f], [6dab58a] → [cc2ad15] |
| Invalid `bpmndi` coordinates are corrected. | [fc352ae] → [0c0adde] |
| The order of children in `bpmn2:process` and in `bpmndi` may change (same meaning). | [57b3074] |

### An iFlow that was never saved in the designer

The first Push of a new iFlow ([6f994f5]) differs from the same iFlow after it was saved in the designer and pushed ([af09698]): `ifl:property` order changes, the sender/receiver participants lose their `cmdVariantUri` / `componentVersion` properties, Start/End shapes change from 36x36 to 32x32, the collaboration gains properties such as `namespaceMapping` and `log`, and `parameters.prop` / `parameters.propdef` appear. Use files that were saved in the designer as the basis for edits.

## Diff noise

These changes carry no meaning. Ignore them when reading diffs, and do not "fix" them.

| Noise | Evidence |
|---|---|
| The `id` of `bpmn2:documentation` changes on every save (for example `Documentation_1791801235502` → `Documentation_1791801478283`). | [03225bf] and almost every later Push |
| Timestamp lines in `metainfo.prop` and `parameters.prop`. | [03225bf], [9d3de86] and later |
| `parameters.propdef` alternates between `<parameters><param_references/></parameters>` and `<parameters/>`. | [92c8b77], [1b5d158], [57b3074] |
| Reordering of `BPMNShape` / `BPMNEdge`, of children of `bpmn2:process`, and of `ifl:property` elements. | [f319ffe], [052b9b2], [57b3074], [af09698] |

When the user performs one UI action per commit, the diff contains only the place that was changed, apart from this noise ([03225bf]–[052b9b2], [1ef9646], [a85e897], [ce88aae], [40a9c8b]).

## Testing a deployed iFlow

| Fact | Evidence |
|---|---|
| An HTTPS sender endpoint is called at `<runtime host>/http<urlPath>`. | [052b9b2], [758b608] |
| With the default `senderAuthType` `RoleBased` and `userRole` `ESBMessaging.send`, an OAuth `client_credentials` token from a service key with the `ESBMessaging.send` role works. | [052b9b2] |
| Calling before the deployment shows Started returned HTTP 404 `unknown_route`; after Started, the same URL worked. That the cause is the unfinished deployment is **unverified**. Wait for Started in the Monitor. | [052b9b2] |
| Message headers set in Content Modifiers come back as HTTP response headers, with lower-case names (`x-s01-constant`). | [052b9b2] |

Never write client secrets or tokens into the repository.

[03225bf]: https://github.com/miyasuta/cpi-iflow-samples/commit/03225bf
[052b9b2]: https://github.com/miyasuta/cpi-iflow-samples/commit/052b9b2
[0c0adde]: https://github.com/miyasuta/cpi-iflow-samples/commit/0c0adde
[17f81ee]: https://github.com/miyasuta/cpi-iflow-samples/commit/17f81ee
[1b5d158]: https://github.com/miyasuta/cpi-iflow-samples/commit/1b5d158
[1ef9646]: https://github.com/miyasuta/cpi-iflow-samples/commit/1ef9646
[24a9667]: https://github.com/miyasuta/cpi-iflow-samples/commit/24a9667
[395e94c]: https://github.com/miyasuta/cpi-iflow-samples/commit/395e94c
[3dbd8d9]: https://github.com/miyasuta/cpi-iflow-samples/commit/3dbd8d9
[40a9c8b]: https://github.com/miyasuta/cpi-iflow-samples/commit/40a9c8b
[519851d]: https://github.com/miyasuta/cpi-iflow-samples/commit/519851d
[56e0a25]: https://github.com/miyasuta/cpi-iflow-samples/commit/56e0a25
[57b3074]: https://github.com/miyasuta/cpi-iflow-samples/commit/57b3074
[6dab58a]: https://github.com/miyasuta/cpi-iflow-samples/commit/6dab58a
[6f994f5]: https://github.com/miyasuta/cpi-iflow-samples/commit/6f994f5
[758b608]: https://github.com/miyasuta/cpi-iflow-samples/commit/758b608
[7827ffc]: https://github.com/miyasuta/cpi-iflow-samples/commit/7827ffc
[834f0c6]: https://github.com/miyasuta/cpi-iflow-samples/commit/834f0c6
[92c8b77]: https://github.com/miyasuta/cpi-iflow-samples/commit/92c8b77
[95802b3]: https://github.com/miyasuta/cpi-iflow-samples/commit/95802b3
[9affede]: https://github.com/miyasuta/cpi-iflow-samples/commit/9affede
[9d3de86]: https://github.com/miyasuta/cpi-iflow-samples/commit/9d3de86
[a517576]: https://github.com/miyasuta/cpi-iflow-samples/commit/a517576
[a85e897]: https://github.com/miyasuta/cpi-iflow-samples/commit/a85e897
[af09698]: https://github.com/miyasuta/cpi-iflow-samples/commit/af09698
[bb5e4f0]: https://github.com/miyasuta/cpi-iflow-samples/commit/bb5e4f0
[c200359]: https://github.com/miyasuta/cpi-iflow-samples/commit/c200359
[cc2ad15]: https://github.com/miyasuta/cpi-iflow-samples/commit/cc2ad15
[ce88aae]: https://github.com/miyasuta/cpi-iflow-samples/commit/ce88aae
[dbb80e2]: https://github.com/miyasuta/cpi-iflow-samples/commit/dbb80e2
[f319ffe]: https://github.com/miyasuta/cpi-iflow-samples/commit/f319ffe
[fa1090f]: https://github.com/miyasuta/cpi-iflow-samples/commit/fa1090f
[fc352ae]: https://github.com/miyasuta/cpi-iflow-samples/commit/fc352ae
