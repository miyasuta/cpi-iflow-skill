# Content Modifier

A Content Modifier sets Message Header rows, Exchange Property rows and the Message Body. A step added to an iFlow takes the same settings as one added in the designer.

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Content Modifier | (the step itself) | `componentVersion` | `1.6` |
| Content Modifier | (the step itself) | `activityType` | `Enricher` |
| Content Modifier | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::Enricher/version::1.6.5` |
| Message Header | the table of rows | `headerTable` | rows in the form below, or empty |
| Exchange Property | the table of rows | `propertyTable` | rows in the form below, or empty |
| Message Body > Type | Constant | `bodyType` | `constant` |
| Message Body > Type | Expression | `bodyType` | `expression` |
| Message Body | the body text | `wrapContent` | the text, for example `Constant header: ${header.X-S01-Constant}` |

A new step has exactly these 7 keys: `bodyType`, `propertyTable`, `headerTable`, `wrapContent`, `componentVersion`, `activityType`, `cmdVariantUri`. An empty table is an empty value.

Other version pairs also deployed, and the two kinds of step can sit in one iFlow:

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Content Modifier | (the step itself) | `componentVersion` | `1.5` |
| Content Modifier | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::Enricher/version::1.5.0` |
| Content Modifier | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::Enricher/version::1.6.6`, with `componentVersion` `1.6` |

## Rows of Message Header and Exchange Property

Both tables use the same row form. One row is six cells in this order, and several rows are written one after another:

`<row><cell id='Action'>Create</cell><cell id='Type'>constant</cell><cell id='Value'>hello</cell><cell id='Default'></cell><cell id='Name'>X-S01-Constant</cell><cell id='Datatype'></cell></row>`

| UI field | UI choice | Cell | Value |
|---|---|---|---|
| Action | Create | `Action` | `Create` |
| Action | Delete | `Action` | `Delete`; `Name` is `$name=<header name>` (for example `$name=X-Drop`), `Type` `constant`, `Value` empty |
| Source Type | Constant | `Type` | `constant` |
| Source Type | Expression | `Type` | `expression` |
| Source Type | Header | `Type` | `header`; `Value` is the name of the header to copy, `Datatype` empty |
| Source Type | Property | `Type` | `property`; `Value` is the property name, `Datatype` empty |
| Source Type | XPath | `Type` | `xpath`; `Value` is the XPath (for example `/r/t`), `Datatype` `java.lang.String` |
| Source Value | the value | `Value` | the text; for Expression for example `${header.X-S01-Constant}` |
| Data Type | Constant | `Datatype` | empty |
| Data Type | Expression | `Datatype` | `java.lang.String` |
| (no UI label recorded) | the header or property name | `Name` | for example `X-S01-Constant` or `s01Property` |
| (no UI label recorded) | not used | `Default` | empty |

## Pitfalls

- The body text is the value of `wrapContent` for both body types. There is no other body key.
- Use `expression` for a body that contains `${header.<name>}` or `${property.<name>}`; they were resolved at runtime. With `constant`, `${header.X-In}` came back as literal text. A body of plain text with type `constant` also deployed.
- A step with a non-empty body replaces the body. With two Content Modifiers in a row, the response body is the body of the later one.
- A header or property set in a Content Modifier can be read in the body of the same step.
- A Delete row whose `Name` is the plain header name (`X-Drop`) deployed, but at run time the whole step was skipped without any error: none of its rows or its body took effect, and the step was missing from the message log. With `$name=X-Drop`, the form the designer saves, the header was deleted.
- Rows run from top to bottom. A later row's expression (`${header.X-First}`) read a header set by an earlier row of the same table.
- A Property row in `headerTable` did not see a property set in `propertyTable` of the same step: the header was not created. A property set in an earlier step was read.
- A Header row copying a header sent by the caller needs that name in Allowed Header(s) on the integration flow (see [https-sender.md](https-sender.md)); the copied `X-In` was listed there.
- A header set in an earlier step is still there after later steps. With an HTTPS sender, headers set here came back as response headers with lower-case names (`x-s01-constant`).
- Both a Constant and an Expression row deployed in `headerTable`, and an Expression row reading a header deployed in `propertyTable`. A Constant row in `propertyTable` deployed too.
- Rows added to an existing table, and an empty table replaced by a table with rows, deployed. The row order in the value is the order shown in the designer.
- A header value containing `<`, `&` or `>` is written escaped once as XML text inside its cell (`&lt;`, `&amp;`, `&gt;`). The table value is escaped once more in the stored file (`&amp;lt;` for `<`); check the stored form in the diff. With that stored form, `a<b & c>d` deployed and came back unchanged as a response header.
- A step with an older pair (`1.5` with `version::1.5.0`) kept its version when saved; CPI did not upgrade it. Keep an existing step's pair as it is, and use the 1.6 pair for a new step. A `1.5.0` step with only 5 keys (no `headerTable`, `propertyTable`) deployed, and so did adding a `headerTable` key to such a step (after `bodyType`, before `wrapContent`).
