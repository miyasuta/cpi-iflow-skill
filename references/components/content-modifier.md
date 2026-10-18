# Content Modifier

A Content Modifier is a `bpmn2:callActivity` in the process, configured by `ifl:property` elements. For its place in the file and for inserting a step, see [../iflw-structure.md](../iflw-structure.md).

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

Names, roles, addresses and header names in the examples below show the XML shape only. They are not design choices; the design decides them ([../design/process.md](../design/process.md)).

## Supported in this skill version

- Add, change, or reorder rows of Message Header (`headerTable`) and Exchange Property (`propertyTable`) with Type `constant` or `expression`
- Set the Message Body (`bodyType`, `wrapContent`)
- Insert a new Content Modifier between two existing nodes

Not supported: other Source Types (Header, Property, XPath, Number Range, Local/Global Variable) for new rows, Actions other than `Create`, values in `Default`. Keep existing rows that use them exactly as they are.

## Keys of a new Content Modifier

Use exactly these 7 keys. This is a Content Modifier added locally that pulled, saved, deployed and ran ([395e94c], again in [4992e7a]); a Content Modifier added in the UI has the same keys and versions ([9d3de86]).

```xml
<bpmn2:callActivity id="CallActivity_Local1" name="Added Locally">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>bodyType</key>
            <value>expression</value>
        </ifl:property>
        <ifl:property>
            <key>propertyTable</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>headerTable</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>wrapContent</key>
            <value>Step 2 reached. ${header.X-S01-Constant}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.6</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Enricher</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Enricher/version::1.6.5</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>SequenceFlow_6</bpmn2:incoming>
    <bpmn2:outgoing>SequenceFlow_Local1</bpmn2:outgoing>
</bpmn2:callActivity>
```

An empty Content Modifier from the UI has `bodyType` `constant` and empty `headerTable`, `propertyTable`, `wrapContent` ([9d3de86]).

## Versions (`cmdVariantUri` and `componentVersion`)

| Fact | Evidence |
|---|---|
| The UI writes `version::1.6.5` with `componentVersion` `1.6` (this tenant, October 2026). | [9d3de86] |
| The older pair `version::1.5.0` / `1.5` pulls, saves, deploys and runs without warnings. | [834f0c6] → [fa1090f] |
| CPI does not migrate an older step on save. Each step keeps its own version, so `1.5.0` and `1.6.5` steps can be mixed in one iFlow. | [fa1090f], [cc2ad15] |
| With `1.5.0`, a 5-key form without `headerTable` / `propertyTable` is accepted, and CPI does not add the missing keys. | [6dab58a] → [cc2ad15] |
| Adding a `headerTable` key to such a `1.5.0` step works: put it after `bodyType` and before `wrapContent`. It pulled, showed its rows in the designer, deployed, ran, and survived the next Push. | [1c9b002] → [3bff3be] |
| Adding `propertyTable` to such a step, or adding a missing table key to a `1.6.5` step: **unverified**. | — |
| The same 5-key form with `1.6.5`: **unverified**. | — |
| Mixed pairs (for example `version::1.6.5` with `1.5`): **unverified**. | — |

Rules:
- Existing step: keep its `cmdVariantUri` and `componentVersion` unchanged.
- New step: use `version::1.6.5` / `1.6` with all 7 keys, as above.
- Never invent another version or pair.

## Message Header and Exchange Property tables

Both values are tables stored as escaped XML strings. **Read [../escaping.md](../escaping.md) before writing them.**

| Fact | Evidence |
|---|---|
| One row = `<row>`, one column = `<cell id='...'>`. The six columns are `Action`, `Type`, `Value`, `Default`, `Name`, `Datatype`, written in this order. | [f319ffe], [a85e897] |
| `headerTable` and `propertyTable` have the same columns and format; only the key differs. | [ab24901] |
| `Action` is `Create` (the only value seen). | [f319ffe], [ab24901], [a85e897] |
| `Default` is empty (the only value seen). | [f319ffe], [a85e897] |
| Rows added locally are accepted and not rewritten by CPI. | [95802b3] → [1b5d158], [4581ce0] → [c5b72ce], [c6d9ca3] → [9898936] |
| An empty table (`<value/>`) can be replaced by a table with rows. | [c6d9ca3] → [9898936] |
| Row order in the file is the order shown in the UI. Reordering locally changes the UI order and survives Push. | [95802b3], [1b5d158] |
| A row added in the UI is placed first (top). A row added locally may go at the end instead: it stays at the end after save and Push and works the same. | [2c68cbe], [a85e897], [4581ce0] → [c5b72ce] |
| Whether row order affects evaluation at runtime (a later row reading a header set by an earlier row): **unverified**. | — |

### Type

| UI Source Type | `Type` value | `Datatype` | Evidence |
|---|---|---|---|
| Constant | `constant` | empty | [f319ffe], [a85e897] |
| Expression | `expression` | `java.lang.String` | [2c68cbe], [ab24901], [a85e897] |

Constant and Expression headers, and an Expression property that reads a header, worked at runtime ([052b9b2], [bb5e4f0], [95802b3]). Other Datatype values are **unverified**.

### Row examples (inner XML, before escaping)

Header, Constant ([f319ffe]):

```xml
<row><cell id='Action'>Create</cell><cell id='Type'>constant</cell><cell id='Value'>hello</cell><cell id='Default'></cell><cell id='Name'>X-S01-Constant</cell><cell id='Datatype'></cell></row>
```

Exchange Property, Expression ([ab24901]):

```xml
<row><cell id='Action'>Create</cell><cell id='Type'>expression</cell><cell id='Value'>${header.X-S01-Constant}</cell><cell id='Default'></cell><cell id='Name'>s01Property</cell><cell id='Datatype'>java.lang.String</cell></row>
```

In the `.iflw`, the same Constant header row is written as ([f319ffe]):

```xml
<value>&lt;row&gt;&lt;cell id='Action'&gt;Create&lt;/cell&gt;&lt;cell id='Type'&gt;constant&lt;/cell&gt;&lt;cell id='Value'&gt;hello&lt;/cell&gt;&lt;cell id='Default'&gt;&lt;/cell&gt;&lt;cell id='Name'&gt;X-S01-Constant&lt;/cell&gt;&lt;cell id='Datatype'&gt;&lt;/cell&gt;&lt;/row&gt;</value>
```

Several rows are simply concatenated inside one `<value>`.

## Message Body (`bodyType`, `wrapContent`)

| Fact | Evidence |
|---|---|
| The body text is the value of `wrapContent`. There is no other body key. | [052b9b2] |
| `bodyType` is `constant` or `expression` (the only two choices in the UI). The body is in `wrapContent` in both cases; switching the type changes only the `bodyType` line. | [052b9b2], [1ef9646] |
| `${header.xxx}` and `${property.xxx}` in the body are resolved at runtime (confirmed with `bodyType` `expression`; with `constant` **unverified**, so use `expression`). | [052b9b2] |
| `bodyType` `expression` without any `${...}` gives the designer warning `Expression Text does not have any expression parameters, but specified as 'Expression'.` (not an error). Use `constant` for plain text. | [c200359] |
| A step with a non-empty `wrapContent` replaces the body: with two Content Modifiers in a row, the response body is the second one's. To change the response, change the body of the **last** step that sets one, or ask the user which step to change. | [395e94c] |
| Headers and properties set in a Content Modifier can be read in the body of **the same** Content Modifier: the tables are applied before the body is evaluated (`bodyType` `expression`). | [4992e7a] (`${property.evalProp}` → `eval-two`), [1c9b002] (`${header.X-F2}` → `f-two`) |
| `<` or `&` in the body: **unverified**. See [../escaping.md](../escaping.md#scope). | — |

Example body ([052b9b2]): `Constant header: ${header.X-S01-Constant}, Expression header: ${header.X-S01-Expression}, Property: ${property.s01Property}`

## Runtime behavior

| Fact | Evidence |
|---|---|
| Headers set here are returned as HTTP response headers by the HTTPS sender, with lower-case names (`x-s01-constant`). | [052b9b2], [bb5e4f0], [95802b3] |
| A header set in an earlier step is still present after later steps. | [395e94c] |
| A header value with `<` and `&`, double-escaped in the `.iflw`, is returned unescaped (`x-eval3: x<y & z`). | [c6d9ca3] |

[052b9b2]: https://github.com/miyasuta/cpi-iflow-samples/commit/052b9b2
[1b5d158]: https://github.com/miyasuta/cpi-iflow-samples/commit/1b5d158
[1c9b002]: https://github.com/miyasuta/cpi-iflow-samples/commit/1c9b002
[1ef9646]: https://github.com/miyasuta/cpi-iflow-samples/commit/1ef9646
[2c68cbe]: https://github.com/miyasuta/cpi-iflow-samples/commit/2c68cbe
[395e94c]: https://github.com/miyasuta/cpi-iflow-samples/commit/395e94c
[3bff3be]: https://github.com/miyasuta/cpi-iflow-samples/commit/3bff3be
[4581ce0]: https://github.com/miyasuta/cpi-iflow-samples/commit/4581ce0
[4992e7a]: https://github.com/miyasuta/cpi-iflow-samples/commit/4992e7a
[6dab58a]: https://github.com/miyasuta/cpi-iflow-samples/commit/6dab58a
[834f0c6]: https://github.com/miyasuta/cpi-iflow-samples/commit/834f0c6
[95802b3]: https://github.com/miyasuta/cpi-iflow-samples/commit/95802b3
[9898936]: https://github.com/miyasuta/cpi-iflow-samples/commit/9898936
[9d3de86]: https://github.com/miyasuta/cpi-iflow-samples/commit/9d3de86
[a85e897]: https://github.com/miyasuta/cpi-iflow-samples/commit/a85e897
[ab24901]: https://github.com/miyasuta/cpi-iflow-samples/commit/ab24901
[bb5e4f0]: https://github.com/miyasuta/cpi-iflow-samples/commit/bb5e4f0
[c200359]: https://github.com/miyasuta/cpi-iflow-samples/commit/c200359
[c5b72ce]: https://github.com/miyasuta/cpi-iflow-samples/commit/c5b72ce
[c6d9ca3]: https://github.com/miyasuta/cpi-iflow-samples/commit/c6d9ca3
[cc2ad15]: https://github.com/miyasuta/cpi-iflow-samples/commit/cc2ad15
[f319ffe]: https://github.com/miyasuta/cpi-iflow-samples/commit/f319ffe
[fa1090f]: https://github.com/miyasuta/cpi-iflow-samples/commit/fa1090f
