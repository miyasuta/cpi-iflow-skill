# Groovy Script step

A Groovy Script step is a `bpmn2:callActivity` in `bpmn2:process` with 7 `ifl:property` elements. The script itself is a separate file in `<iFlow>/src/main/resources/script/`. For the step's place in the file and the insertion steps, see [../iflw-structure.md](../iflw-structure.md).

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples): `S02_GroovyScript` on `main` (built in the CPI UI) and `X02_Sandbox` on `exp` (edited locally). Anything not confirmed is marked **unverified**.

Names, roles, addresses and header names in the examples below show the XML shape only. They are not design choices; the design decides them ([../design/process.md](../design/process.md)).

## Supported in this skill version

| Task | Status |
|---|---|
| Insert a Groovy Script step between two existing nodes, with a new script file | Verified locally: inserted after a Content Modifier, pulled, deployed without Save, called ([6126bba]). Keys and script survived a later Push from CPI ([c058b69]). |
| Change the code of an existing script file | Verified locally: only the `.groovy` file changed, pulled, deployed without Save, called ([4f27892]). The same change in the UI also touches only the `.groovy` file ([95d958e]). |

Not supported (no sample): Script Collections (`scriptBundleId`), a function name other than the default (`scriptFunction`), JavaScript steps, a script outside `script/`, two Groovy steps in one iFlow, and other step versions.

## Template

Copy this exactly (from [f7c70d0], with `script` from [1a8d423]). Only `id`, `name`, `incoming`, `outgoing` and the file name in `script` change:

```xml
<bpmn2:callActivity id="CallActivity_Local2" name="Groovy Script 1">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>scriptFunction</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>scriptBundleId</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Script</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::GroovyScript/version::1.1.2</value>
        </ifl:property>
        <ifl:property>
            <key>subActivityType</key>
            <value>GroovyScript</value>
        </ifl:property>
        <ifl:property>
            <key>script</key>
            <value>script1.groovy</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>SequenceFlow_Local1</bpmn2:incoming>
    <bpmn2:outgoing>SequenceFlow_Local2</bpmn2:outgoing>
</bpmn2:callActivity>
```

- `script` holds the **file name only** (`script1.groovy`), not `script/script1.groovy` ([1a8d423], [6126bba]).
- `scriptFunction` empty: the script's `processData` function ran ([95d958e], [6126bba]). Always define `def Message processData(Message message)`.
- `componentVersion` `1.1` with `version::1.1.2` is the pair the UI wrote on this tenant ([f7c70d0]). Do not change it.
- `BPMNShape`: 100x60, like any step ([f7c70d0], [6126bba]).

## The script file

- Path: `<iFlow>/src/main/resources/script/<name>.groovy`. The UI created `script1.groovy` ([1a8d423]). Use `script1.groovy` for the first Groovy step; other names and locations are **unverified**.
- No other file needs a change: adding the step and the script changed only the `.iflw` and the `.groovy` file (apart from timestamps) in the UI ([f7c70d0], [1a8d423]), and the local insertion changed only those two ([6126bba]).
- Write it in the form that ran ([95d958e], [6126bba]), without a `package` line:

```groovy
import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    def greeting = message.getHeaders().get("X-X02-Greeting") ?: "none"
    message.setHeader("X-X02-Script", "set-by-script")
    message.setBody("Groovy saw: " + greeting)
    return message
}
```

- Used and verified in these scripts: `message.getBody(String)`, `message.getHeaders().get(name)`, `message.setHeader(name, value)`, `message.setProperty(name, value)`, `message.getProperty(name)`, `message.setBody(value)` ([95d958e], [6126bba]).
- The UI template starts with `package script`; when the script was edited and saved in the UI, that line was dropped ([1a8d423] → [95d958e]). Scripts without it run. Keeping it is **unverified**; leave an existing file's first line as it is.
- A Push from CPI may add a final newline to the file ([c058b69]). That is noise.

## A step without a script

In the UI, a Groovy step with an empty `script` shows the Problems error `Script File not defined for Script Processor step`, but can still be saved and pushed ([f7c70d0]). What Pull or deployment does with an empty `script`, or with a `script` whose file is missing, is **unverified**. `scripts/check_iflw.py` reports both as errors: always write the file.

## Procedure: insert a Groovy Script step

1. Insert the `callActivity` from the template between two nodes, following "Inserting a step between two nodes" in [../iflw-structure.md](../iflw-structure.md) (flows, `incoming`/`outgoing`, shape, edges, waypoints).
2. Create `src/main/resources/script/script1.groovy` next to `scenarioflows/`.
3. If the script reads a header **from the HTTP request**, add that header to Allowed Header(s) (next section).
4. Run `python3 scripts/check_iflw.py <iFlow folder>`, commit both files, push, and follow the round trip in [../workflow.md](../workflow.md) (Pull → Deploy → call).

To change what an existing script does, edit only its `.groovy` file ([4f27892]).

## Allowed Header(s): reading request headers

| Fact | Evidence |
|---|---|
| The iFlow's Runtime Configuration setting Allowed Header(s) is the `ifl:property` `allowedHeaderList` of `bpmn2:collaboration` `Collaboration_1`. It is `<value/>` by default. | [f268336] |
| While it was empty, the request header `X-S02-Name` could not be read with `message.getHeaders().get("X-S02-Name")` (the script fell back to its default). After setting it to `X-S02-Name` and redeploying, the same script read it, and the header was also returned in the HTTP response. | [95d958e], [f268336] |
| Setting it in the UI changed only that line: `<value/>` → `<value>X-S02-Name</value>`. | [f268336] |
| Headers set inside the iFlow (by a Content Modifier before the script) were readable without Allowed Header(s). | [6126bba] |

So, when a script must read a request header, set `allowedHeaderList` to the header name:

```xml
<ifl:property>
    <key>allowedHeaderList</key>
    <value>X-S02-Name</value>
</ifl:property>
```

Setting `allowedHeaderList` **locally** to a single name was verified once: pulled, deployed without Save, and the header reached a Router condition ([6ef7611]; not tested with a Groovy Script). SAP documents that the setting lists the headers retained while the incoming message is processed: names separated by `|` without spaces, **regular expressions are allowed** (for example `AB_[0-9]|CD_[0-9]`), and a single `*` allows all headers but is discouraged ([Specify the Runtime Configuration](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/0c1c96e50ff340869090469d260976f3.html?locale=en-US&state=PRODUCTION&version=Cloud)). Only a single exact name was tested; `|`-separated lists and regular expressions are **unverified**, so tell the user when you write one. List only the headers the iFlow needs, never `*`.

[6ef7611]: https://github.com/miyasuta/cpi-iflow-samples/commit/6ef7611
[1a8d423]: https://github.com/miyasuta/cpi-iflow-samples/commit/1a8d423
[4f27892]: https://github.com/miyasuta/cpi-iflow-samples/commit/4f27892
[6126bba]: https://github.com/miyasuta/cpi-iflow-samples/commit/6126bba
[95d958e]: https://github.com/miyasuta/cpi-iflow-samples/commit/95d958e
[c058b69]: https://github.com/miyasuta/cpi-iflow-samples/commit/c058b69
[f268336]: https://github.com/miyasuta/cpi-iflow-samples/commit/f268336
[f7c70d0]: https://github.com/miyasuta/cpi-iflow-samples/commit/f7c70d0
