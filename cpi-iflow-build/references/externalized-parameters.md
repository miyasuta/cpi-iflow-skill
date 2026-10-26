# Externalized parameters

An externalized parameter replaces a value in the `.iflw` with `{{name}}`. Its value lives in `parameters.prop` and its declaration in `parameters.propdef`, both in `<iFlow>/src/main/resources/`. The user can later set a different value in the CPI **Configure** screen without editing the iFlow.

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples): `S03_ExternalizedParameters` on `main` (externalized in the CPI UI) and `X02_Sandbox` on `exp` (externalized locally). Anything not confirmed is marked **unverified**.

SAP documentation: [Externalize Parameters of an Integration Flow](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/45b2a0772db94bd9b0e57bc82d8d3797.html?locale=en-US&state=PRODUCTION&version=Cloud), [Configure Externalized Parameters of an Integration Flow](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/462a4782db7b485b94ffce5b6fe22c31.html?locale=en-US&state=PRODUCTION&version=Cloud).

## Supported in this skill version

| Task | Status |
|---|---|
| Externalize the HTTPS sender Address (`urlPath`) | Verified locally: pulled, deployed without Save, called ([21c75ae]). Also done in the UI ([669b621]). |
| Externalize a Content Modifier header cell value (`headerTable`, `Value` cell) | Verified locally the same way ([21c75ae]). Also done in the UI ([e5bb405]). |
| Externalize a Content Modifier body (`wrapContent`) | Done in the UI only ([0ca2726]); the same pattern as the other two. A local edit of it is **unverified**. |
| Change only the value (default) of an existing parameter | Verified locally on an iFlow with no Configure values ([91b021b]). |

Not supported (no sample): externalizing any other field, a part of a value (`/x/{{a}}`), the same parameter in two fields, removing an externalization, renaming a parameter, values with special characters (`<`, `&`, `=`, `:`, `\`, line breaks), and creating `parameters.prop` / `parameters.propdef` when they do not exist yet.

## The three places

### 1. The value in the `.iflw`

Replace the **whole** value of the `ifl:property` with `{{name}}`. Nothing else in the `.iflw` changes; there is no declaration of the parameter in the `.iflw` ([669b621], [e5bb405], [0ca2726]).

```xml
<!-- HTTPS sender (bpmn2:messageFlow) -->
<ifl:property>
    <key>urlPath</key>
    <value>{{s03Address}}</value>
</ifl:property>

<!-- Content Modifier body -->
<ifl:property>
    <key>wrapContent</key>
    <value>{{s03Body}}</value>
</ifl:property>
```

In a table cell, `{{` and `}}` are not escaped. Keep the row as it is (`Type` stays `constant`, `Default` stays empty) and replace only the text of the `Value` cell ([e5bb405]):

```xml
<value>&lt;row&gt;&lt;cell id='Action'&gt;Create&lt;/cell&gt;&lt;cell id='Type'&gt;constant&lt;/cell&gt;&lt;cell id='Value'&gt;{{s03Greeting}}&lt;/cell&gt;&lt;cell id='Default'&gt;&lt;/cell&gt;&lt;cell id='Name'&gt;X-S03-Greeting&lt;/cell&gt;&lt;cell id='Datatype'&gt;&lt;/cell&gt;&lt;/row&gt;</value>
```

Parameter names in the samples are letters and digits in camelCase (`s03Address`, `x02Greeting`). SAP's documentation forbids `,` `?` `/` quotes `<` `>` `;` `:` `[` `]` and `! @ # $ % & * ( ) = +` in a parameter. Use letters and digits only.

### 2. `parameters.prop`

A Java-properties-style file: a timestamp comment line, then one `name=value` line per parameter ([669b621], [21c75ae]):

```
#Sat Oct 17 21:07:52 UTC 2026
x02Address=/x02/externalized
x02Greeting=from-prop
```

- Keep the existing first line(s) as they are. The timestamp does not need to change: a Pull with the old timestamp applied the new value ([91b021b]).
- CPI writes the lines sorted by parameter name ([0ca2726]). Do the same.
- The value is written as is; spaces are not escaped (`s03Body=S03 base body`, [0ca2726]). Special characters are **unverified**.
- The file may or may not end with a newline; CPI wrote both ([e5bb405], [0d5db9d]).

### 3. `parameters.propdef`

One `<parameter>` per parameter, then `<param_references>`. This is the file that was written locally and accepted ([21c75ae]); it is CPI's own format ([e5bb405]) with only the names changed:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?><parameters><parameter>
    <key/>
    <name>x02Address</name>
    <type>xsd:string</type>
    <isRequired>false</isRequired>
    <constraint/>
    <description/>
    <additionalMetadata/>
  </parameter><parameter>
    <key/>
    <name>x02Greeting</name>
    <type>xsd:string</type>
    <isRequired>false</isRequired>
    <constraint/>
    <description/>
    <additionalMetadata/>
  </parameter><param_references><reference attribute_category="Sender" attribute_id="/attrId::urlPath" attribute_uilabel="" param_key="x02Address"/></param_references></parameters>
```

- Copy the `<parameter>` block exactly; change only `<name>`. Append new parameters after the existing ones (CPI keeps them in the order they were added, [0ca2726]).
- An iFlow without parameters has `<parameters><param_references/></parameters>` ([79f6c66]) (or `<parameters/>`, see [workflow.md](workflow.md) "Diff noise"). Replace it with the full form above.
- CPI may later re-indent the file (each `<parameter>`, `<param_references>` and `<reference>` on its own line, [0d5db9d]). Both layouts are accepted; do not reformat an existing file.

### `reference`: required for the HTTPS sender Address

When CPI externalized the HTTPS sender Address, it added a `<reference>` to `<param_references>`; for the Content Modifier header cell and body it did not ([669b621], [e5bb405], [0ca2726]). Write it exactly like this, changing only `param_key`:

```xml
<reference attribute_category="Sender" attribute_id="/attrId::urlPath" attribute_uilabel="" param_key="x02Address"/>
```

- For a Content Modifier header cell or body, write **no** `reference`.
- With the reference, the Address appears on the **Sender** tab of the Configure screen; the other parameters appear on the **More** tab (observed by the user on [e0da8c4]).
- What happens without the reference for the Address, and which other fields need one, is **unverified**. For a field not listed in this file, do not guess a reference: the field is not supported.

## Procedure: externalize a value

1. Check that `parameters.prop` and `parameters.propdef` exist in `<iFlow>/src/main/resources/`. If they do not (an iFlow that was never saved in the designer, such as [2f1316e]), stop: writing them from scratch is **unverified**. Ask the user to open the iFlow in CPI, Edit → Save → Push, and pull locally; CPI creates both files on the first save.
2. Pick a parameter name (letters and digits). The default value is the value currently in the `.iflw`, unless the user asks for another one.
3. Replace the value in the `.iflw` with `{{name}}`.
4. Add `name=value` to `parameters.prop`, keeping the lines sorted by name.
5. Add a `<parameter>` to `parameters.propdef`. For the HTTPS sender Address, also add the `reference`.
6. Run `python3 scripts/check_iflw.py <iFlow folder>`. It reports a `{{name}}` that is missing from either file as an error.
7. Commit, push, and follow the round trip in [workflow.md](workflow.md): Pull → Deploy → call. After Pull, the value appears in CPI as the parameter's **Default Value**, with "No Value Configured" as the Configured Value ([21c75ae]).

## Procedure: change only a value

Change the value after `=` in `parameters.prop`. Do not touch the `.iflw`, `parameters.propdef`, or the timestamp line. After Pull, the Default Value in CPI changes, and a deployment without Save uses it ([91b021b]).

This was verified only on an iFlow with no Configure values. See the next section first.

## Configure values and Git

| Fact | Evidence |
|---|---|
| After the user sets values in the Configure screen, saves, and pushes, `parameters.prop` holds the **configured** values. The `.iflw` (still `{{name}}`) and `parameters.propdef` do not change. | [e0da8c4] |
| The original default values are then nowhere in Git. Git cannot tell a default value from a configured one. | [e0da8c4] |
| After deployment, the configured values were in effect (new Address answered, the old one returned 404). | [e0da8c4] |
| A `parameters.prop` that was pulled is treated as **default values** (Default Value set, Configured Value empty). | [21c75ae], [91b021b] |

So the value in `parameters.prop` in Git is the value in effect at the time CPI pushed it: the configured value if there is one, otherwise the default.

**Unverified:** changing `parameters.prop` locally for an iFlow that **has** configured values. SAP documents that a configured value always takes precedence over the default value. Since Pull writes default values, the local change may have no effect while the configured value stays. Before changing a value locally, ask the user whether values were set in the Configure screen for this iFlow. If yes, tell the user this case is unverified, and suggest changing the value in the Configure screen instead, or checking the Externalized Parameters tab and the call result after Pull and deployment.

Also **unverified**: whether CPI keeps the original default values after Configure values were set.

[0ca2726]: https://github.com/miyasuta/cpi-iflow-samples/commit/0ca2726
[0d5db9d]: https://github.com/miyasuta/cpi-iflow-samples/commit/0d5db9d
[21c75ae]: https://github.com/miyasuta/cpi-iflow-samples/commit/21c75ae
[2f1316e]: https://github.com/miyasuta/cpi-iflow-samples/commit/2f1316e
[669b621]: https://github.com/miyasuta/cpi-iflow-samples/commit/669b621
[79f6c66]: https://github.com/miyasuta/cpi-iflow-samples/commit/79f6c66
[91b021b]: https://github.com/miyasuta/cpi-iflow-samples/commit/91b021b
[e0da8c4]: https://github.com/miyasuta/cpi-iflow-samples/commit/e0da8c4
[e5bb405]: https://github.com/miyasuta/cpi-iflow-samples/commit/e5bb405
