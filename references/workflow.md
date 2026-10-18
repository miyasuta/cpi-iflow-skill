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

- `parameters.prop` / `parameters.propdef` hold externalized parameters; see [externalized-parameters.md](externalized-parameters.md). CPI creates them on the first save in the designer ([79f6c66]).
- **Do not infer the iFlow name from the `.iflw` file name.** A copied iFlow keeps the original file name (`X01_Sandbox/.../S01_ContentModifier.iflw`) and also the original HTTPS sender Address. The iFlow name is `Bundle-Name` / `Bundle-SymbolicName` in `META-INF/MANIFEST.MF` ([dbb80e2]).

## Development round trip

Steps on the CPI side are done by the user in the CPI web UI. Ask the user to do them and to report the result.

1. **Before editing locally**, the user pushes every change saved in the CPI designer or the Configure screen. "Unpushed changes" means changes saved in CPI but not yet pushed.
2. Edit the files locally, run `scripts/check_iflw.py`, commit, and push to the branch connected to the iFlow.
3. In CPI: **Pull** → **open the iFlow and check that the change arrived** → **Deploy** → wait for Started → call the iFlow to test it. Edit and Save are not needed: the user can deploy right after Pull, with the iFlow open in view mode ([21c75ae], [91b021b]).
   - Before Deploy, the user opens the iFlow in the designer (view mode is enough) and checks that the steps and values you changed are there: a new step on the diagram, a changed header value, the Address. For a change only inside a script file, open the step's script. If the change is not there, Pull again, then check again. In one evaluation, Pull reported no error but the iFlow kept the previous content; the first deployment ran the old version, and a second Pull fixed it ([83d2f85], see "Pull" below). The cause is **unverified**.
   - If the deployment fails or the result is wrong, check the Problems tab (a broken table value shows up only there, see "When Pull fails" below).
4. A **Push from CPI is not needed**, and skipping it avoids the "behind" dead end (see "Push rejected: artifact is behind" below). The next local edit can start from the local commit: two local edits in a row, each pulled and deployed without a Push in between, both worked ([21c75ae] → [91b021b]).

Why the Push can be skipped: even without Save, a Push from CPI is never empty. CPI rewrites the files in its own format (order of elements, waypoints, layout of `parameters.propdef`; see "Push" below) without changing keys, values, IDs or references ([0d5db9d]). The repository does not need that rewrite to continue.

When the user did Edit and Save in CPI after all (or changed values in the Configure screen), those are unpushed changes: before the next local edit, close edit mode (**Cancel**), reload the page if the iFlow still shows as locked (see "Push fails: artifact is locked" below), **Push**, and pull locally (step 1).

Limits:
- Deploying without Save was verified on an iFlow that had been saved in the designer before ([79f6c66]). For an iFlow that was never saved in the designer (a new, empty iFlow that was only pushed once), deploying without Save worked twice ([c3ddf1c]: an empty iFlow with a locally added HTTPS sender, Request Reply and HTTP receiver; [111453a]: an empty iFlow with a locally added HTTPS sender, Groovy Script and Exception Subprocess; both deployed and answered as expected). Two cases are not enough to rely on: still ask the user to Save before Deploy in that case.
- The round trip with Save and a final Push (the earlier procedure) also completed for every supported kind of edit: adding header rows, inserting a Content Modifier, double-escaped values, adding a `headerTable` key, changing the HTTPS sender Address and CSRF setting ([c5b72ce], [addffca], [9898936], [bd394aa], [159c7c1], [3bff3be]).

## Pull

| Fact | Evidence |
|---|---|
| With no unpushed UI changes, Pull takes over the remote content (the result equals a full replacement). Changed values, added and reordered table rows, added steps, and changed versions were all applied. | [bb5e4f0], [95802b3], [395e94c], [834f0c6], [6dab58a] |
| With unpushed UI changes, if the remote changed **the same place**, Pull is rejected: `The pull operation cannot be performed due to conflicts with the remote integration flow. Resolve the conflicts by manually aligning your local flow with the remote version.` | [9affede] (same Content Modifier body changed on both sides) |
| When Pull is rejected, nothing in CPI changes (no partial import). | [9affede] |
| With unpushed UI changes, if the remote changed a **different place**, Pull merges: the remote change arrives and the UI changes stay. In the observed case, two different properties of the same Content Modifier (`headerTable` remotely, `wrapContent` in the UI) merged. The exact merge granularity (for example, different rows of the same table) is **unverified**. | [c200359] |
| With unpushed UI changes, a remote change to the iFlow Description (`bpmn2:documentation`) is **not** taken over, and Pull still reports success. The next Push then overwrites the remote Description with the CPI value. | [24a9667], [c200359], [17f81ee] |
| A successful Pull therefore does not prove that every remote change arrived. Check in the designer or in the diff of the next Push. | [24a9667] |
| A Pull that reports no error may still leave the previous content in CPI. After a local commit ([83d2f85]) was pulled, the deployed iFlow behaved like the commit before it ([b7f7a59]); pulling again (no error) brought in the change. Whether the first Pull ran before the push arrived, or something else went wrong, is **unverified**. Always check in the designer before deploying. | [83d2f85] |
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
| A Push without any Edit or Save in CPI (Pull → Deploy only) still creates a commit. CPI rewrites the files: order of `bpmn2:sequenceFlow` and `BPMNEdge` elements, the end waypoint of a re-targeted edge (see below), line breaks and indentation of `parameters.propdef`, the final newline of `parameters.prop`, the `metainfo.prop` timestamp. Keys, values, IDs, references and `Bounds` stay the same. | [91b021b] → [0d5db9d] |

### Push rejected: artifact is behind

| Fact | Evidence |
|---|---|
| Other iFlows' commits ([b7f7a59], [83d2f85]) were pushed to the same branch. The user had pulled another iFlow, whose folder those commits did not touch (whether before or after those commits is unknown), did Edit → Save, and pushed from CPI. Push was rejected: `Your artifact is behind the latest commits on the <branch> branch. Pull the latest changes and update your artifact before push.` Pull then failed with `The pull operation cannot be performed as the content is already up to date.`, so neither Push nor Pull worked. | [4125596], [83d2f85] (messages reported by the user) |
| That Pull compares only the iFlow's folder while Push compares the branch head is a guess; it fits what happened but was not tested. | — |
| The dead end was resolved by committing the files **as CPI had saved them** into the iFlow's folder on the branch ([119da02]). After that, Pull worked, and a later Pull and Push from CPI worked too ([19e3402]). | [119da02], [19e3402] |
| It happened again on another branch: a commit that changed only another iFlow's folder ([f36f203]) was pushed after the iFlow had last changed ([7c04efd]); the user then pulled that iFlow in CPI, added a step in the designer, saved and pushed, and got the same "behind" message. Whether the user's Pull came before or after the other commit is not recorded. This fits "another iFlow's commit on the same branch is enough", but the exact condition is still **unverified**. | [7c04efd], [f36f203] (message reported by the user) |
| The same fix worked the second time: the files as CPI had saved them were committed into the iFlow's folder ([3052ccb]; it added `parameters.prop` and `parameters.propdef`, which CPI creates on the first save). Then Pull in CPI worked without errors, and the next Push from CPI after further designer changes worked too ([f34d292]). The commit took the place of the rejected Push. | [3052ccb], [f34d292] |

How to avoid it: **do not Push from CPI** (the round trip above does not need it), and do not Edit → Save in CPI unless a step requires it. Then the iFlow in CPI never has its own changes to push. When the user does work in the CPI designer that must be pushed, ask them to finish and Push that iFlow's designer work before you push local commits for other iFlows on the same branch.

If a Push from CPI is needed after all (the user saved changes in the designer or the Configure screen) and it is rejected as "behind":

1. Ask the user for the iFlow's files as CPI saved them (their saved designer changes must be in it). In the CPI UI this is **Download** (the package's Artifacts tab → Actions → Download; options "Default Values Only" and "Merged Configured and Default Values", see [Working with an Integration Package](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/c433ce2a2bff4d9a9b69257583d1b2fe.html?locale=en-US&state=PRODUCTION&version=Cloud)). That the UI download gives the same files, and which option matches a Push, is **unverified**; tell the user so, and if the iFlow has Configure values, that the choice of option matters and is unknown. Both verified fixes used the OData API download instead (`GET /api/v1/IntegrationDesigntimeArtifacts(Id='<iFlow ID>',Version='active')/$value`), which returned the same files as a Push from CPI apart from timestamps ([c058b69]); if the user has API access, that route is verified ([119da02], [3052ccb]).
2. The zip has no top folder. Replace the contents of `<iFlow>/` on the branch with the zip's contents (delete the old files first, so nothing stale is left), run `check_iflw.py`, commit and push.
3. In CPI: Pull (it should no longer say "up to date"), then Push.

### Push fails: artifact is locked

| Fact | Evidence |
|---|---|
| After Edit → Save → Deploy, going back to the iFlow list without closing edit mode made Push fail with `The operation cannot be performed as the artifact is locked by another user.` Opening the iFlow and pressing Edit → Cancel did not clear the "Locked by ... (you)" label in the list; reloading the browser page did, and Push then worked. | [9898936] |
| Closing edit mode with Cancel (and reloading the page) before Push avoided the lock. Whether the reload alone is enough, or whether the lock also expires, is **unverified**. | [bd394aa], [159c7c1], [3bff3be] |

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
| Table rows, row order, and double escaping are not rewritten. | [95802b3] → [1b5d158], [4581ce0] → [c5b72ce], [c6d9ca3] → [9898936] |
| HTTPS sender `urlPath` and `xsrfProtection` edited locally are kept. | [96961e9] → [bd394aa], [ca0a3c9] → [159c7c1] |
| Older `cmdVariantUri` / `componentVersion` pairs are not migrated, and table keys left out of an older step are not added. | [834f0c6] → [fa1090f], [6dab58a] → [cc2ad15] |
| Invalid `bpmndi` coordinates are corrected. | [fc352ae] → [0c0adde] |
| The order of children in `bpmn2:process` and in `bpmndi` may change (same meaning). | [57b3074] |
| After a Content Modifier was inserted locally, CPI moved the end waypoint of the re-targeted edge (Start → Content Modifier) back to its old end at the End event (`460.0,158.0` → `703.5,158.0`). `sourceElement` / `targetElement` stayed correct, the designer still drew the line correctly, and the iFlow ran. This happened with Save ([3ef66d2] → [669b621]) and without any Save ([91b021b] → [0d5db9d]). The cause is **unverified**. Write the waypoints correctly anyway (see [iflw-structure.md](iflw-structure.md)); do not copy the rewritten value. | [669b621], [0d5db9d] |

### An iFlow that was never saved in the designer

The first Push of a new iFlow ([6f994f5]) differs from the same iFlow after it was saved in the designer and pushed ([af09698]): `ifl:property` order changes, the sender/receiver participants lose their `cmdVariantUri` / `componentVersion` properties, Start/End shapes change from 36x36 to 32x32, the collaboration gains properties such as `namespaceMapping` and `log`, and `parameters.prop` / `parameters.propdef` appear. Use files that were saved in the designer as the basis for edits.

## Diff noise

These changes carry no meaning. Ignore them when reading diffs, and do not "fix" them.

| Noise | Evidence |
|---|---|
| The `id` of `bpmn2:documentation` changes on every save (for example `Documentation_1791801235502` → `Documentation_1791801478283`). | [03225bf] and almost every later Push |
| Timestamp lines in `metainfo.prop` and `parameters.prop`. | [03225bf], [9d3de86] and later |
| `parameters.propdef` alternates between `<parameters><param_references/></parameters>` and `<parameters/>`. | [92c8b77], [1b5d158], [57b3074] |
| Line breaks and indentation of `parameters.propdef` (same content), and whether `parameters.prop` ends with a newline. | [0d5db9d] |
| The timestamp comment line(s) at the top of `parameters.prop`; after a Configure save, an extra empty `#` line. | [669b621], [e0da8c4] |
| Reordering of `BPMNShape` / `BPMNEdge`, of children of `bpmn2:process`, and of `ifl:property` elements. | [f319ffe], [052b9b2], [57b3074], [af09698] |
| Rounding of coordinates, for example a receiver's `Bounds` y `114.15318` → `114.0`. | [9898936] |
| After the user runs the designer's auto layout (format) and saves: new order of elements in the `.iflw` and new values for every `Bounds` and waypoint. Keys, values and references do not change. | [4992e7a] → [addffca] |

When the user performs one UI action per commit, the diff contains only the place that was changed, apart from this noise ([03225bf]–[052b9b2], [1ef9646], [a85e897], [ce88aae], [40a9c8b]).

## Testing a deployed iFlow

| Fact | Evidence |
|---|---|
| An HTTPS sender endpoint is called at `<runtime host>/http<urlPath>`. | [052b9b2], [758b608] |
| With the default `senderAuthType` `RoleBased` and `userRole` `ESBMessaging.send`, an OAuth `client_credentials` token from a service key with the `ESBMessaging.send` role works. | [052b9b2] |
| Calling before the deployment shows Started returned HTTP 404 `unknown_route`; after Started, the same URL worked. That the cause is the unfinished deployment is **unverified**. Wait for Started in the Monitor. | [052b9b2] |
| With CSRF protection on, a POST needs a CSRF token and the cookies returned with it. See [components/https-sender.md](components/https-sender.md). | [ca0a3c9] |
| Message headers set in Content Modifiers come back as HTTP response headers, with lower-case names (`x-s01-constant`). | [052b9b2] |

Never write client secrets or tokens into the repository.

[03225bf]: https://github.com/miyasuta/cpi-iflow-samples/commit/03225bf
[052b9b2]: https://github.com/miyasuta/cpi-iflow-samples/commit/052b9b2
[0c0adde]: https://github.com/miyasuta/cpi-iflow-samples/commit/0c0adde
[0d5db9d]: https://github.com/miyasuta/cpi-iflow-samples/commit/0d5db9d
[111453a]: https://github.com/miyasuta/cpi-iflow-samples/commit/111453a
[119da02]: https://github.com/miyasuta/cpi-iflow-samples/commit/119da02
[159c7c1]: https://github.com/miyasuta/cpi-iflow-samples/commit/159c7c1
[17f81ee]: https://github.com/miyasuta/cpi-iflow-samples/commit/17f81ee
[19e3402]: https://github.com/miyasuta/cpi-iflow-samples/commit/19e3402
[1b5d158]: https://github.com/miyasuta/cpi-iflow-samples/commit/1b5d158
[1ef9646]: https://github.com/miyasuta/cpi-iflow-samples/commit/1ef9646
[21c75ae]: https://github.com/miyasuta/cpi-iflow-samples/commit/21c75ae
[24a9667]: https://github.com/miyasuta/cpi-iflow-samples/commit/24a9667
[3052ccb]: https://github.com/miyasuta/cpi-iflow-samples/commit/3052ccb
[395e94c]: https://github.com/miyasuta/cpi-iflow-samples/commit/395e94c
[3bff3be]: https://github.com/miyasuta/cpi-iflow-samples/commit/3bff3be
[3dbd8d9]: https://github.com/miyasuta/cpi-iflow-samples/commit/3dbd8d9
[3ef66d2]: https://github.com/miyasuta/cpi-iflow-samples/commit/3ef66d2
[40a9c8b]: https://github.com/miyasuta/cpi-iflow-samples/commit/40a9c8b
[4125596]: https://github.com/miyasuta/cpi-iflow-samples/commit/4125596
[4581ce0]: https://github.com/miyasuta/cpi-iflow-samples/commit/4581ce0
[4992e7a]: https://github.com/miyasuta/cpi-iflow-samples/commit/4992e7a
[519851d]: https://github.com/miyasuta/cpi-iflow-samples/commit/519851d
[56e0a25]: https://github.com/miyasuta/cpi-iflow-samples/commit/56e0a25
[57b3074]: https://github.com/miyasuta/cpi-iflow-samples/commit/57b3074
[669b621]: https://github.com/miyasuta/cpi-iflow-samples/commit/669b621
[6dab58a]: https://github.com/miyasuta/cpi-iflow-samples/commit/6dab58a
[6f994f5]: https://github.com/miyasuta/cpi-iflow-samples/commit/6f994f5
[758b608]: https://github.com/miyasuta/cpi-iflow-samples/commit/758b608
[7827ffc]: https://github.com/miyasuta/cpi-iflow-samples/commit/7827ffc
[79f6c66]: https://github.com/miyasuta/cpi-iflow-samples/commit/79f6c66
[7c04efd]: https://github.com/miyasuta/cpi-iflow-samples/commit/7c04efd
[834f0c6]: https://github.com/miyasuta/cpi-iflow-samples/commit/834f0c6
[83d2f85]: https://github.com/miyasuta/cpi-iflow-samples/commit/83d2f85
[91b021b]: https://github.com/miyasuta/cpi-iflow-samples/commit/91b021b
[92c8b77]: https://github.com/miyasuta/cpi-iflow-samples/commit/92c8b77
[95802b3]: https://github.com/miyasuta/cpi-iflow-samples/commit/95802b3
[96961e9]: https://github.com/miyasuta/cpi-iflow-samples/commit/96961e9
[9898936]: https://github.com/miyasuta/cpi-iflow-samples/commit/9898936
[9affede]: https://github.com/miyasuta/cpi-iflow-samples/commit/9affede
[9d3de86]: https://github.com/miyasuta/cpi-iflow-samples/commit/9d3de86
[a517576]: https://github.com/miyasuta/cpi-iflow-samples/commit/a517576
[a85e897]: https://github.com/miyasuta/cpi-iflow-samples/commit/a85e897
[addffca]: https://github.com/miyasuta/cpi-iflow-samples/commit/addffca
[af09698]: https://github.com/miyasuta/cpi-iflow-samples/commit/af09698
[b7f7a59]: https://github.com/miyasuta/cpi-iflow-samples/commit/b7f7a59
[bb5e4f0]: https://github.com/miyasuta/cpi-iflow-samples/commit/bb5e4f0
[bd394aa]: https://github.com/miyasuta/cpi-iflow-samples/commit/bd394aa
[c058b69]: https://github.com/miyasuta/cpi-iflow-samples/commit/c058b69
[c200359]: https://github.com/miyasuta/cpi-iflow-samples/commit/c200359
[c3ddf1c]: https://github.com/miyasuta/cpi-iflow-samples/commit/c3ddf1c
[c5b72ce]: https://github.com/miyasuta/cpi-iflow-samples/commit/c5b72ce
[c6d9ca3]: https://github.com/miyasuta/cpi-iflow-samples/commit/c6d9ca3
[ca0a3c9]: https://github.com/miyasuta/cpi-iflow-samples/commit/ca0a3c9
[cc2ad15]: https://github.com/miyasuta/cpi-iflow-samples/commit/cc2ad15
[ce88aae]: https://github.com/miyasuta/cpi-iflow-samples/commit/ce88aae
[dbb80e2]: https://github.com/miyasuta/cpi-iflow-samples/commit/dbb80e2
[e0da8c4]: https://github.com/miyasuta/cpi-iflow-samples/commit/e0da8c4
[f319ffe]: https://github.com/miyasuta/cpi-iflow-samples/commit/f319ffe
[f34d292]: https://github.com/miyasuta/cpi-iflow-samples/commit/f34d292
[f36f203]: https://github.com/miyasuta/cpi-iflow-samples/commit/f36f203
[fa1090f]: https://github.com/miyasuta/cpi-iflow-samples/commit/fa1090f
[fc352ae]: https://github.com/miyasuta/cpi-iflow-samples/commit/fc352ae
