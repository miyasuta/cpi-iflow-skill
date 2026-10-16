# Escaping in table properties

Some `ifl:property` values hold a table as an XML string: `headerTable` and `propertyTable` of the Content Modifier, and `clientCertificates` of the HTTPS sender. This file explains how to write them.

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

## Two layers

A table value is an **inner XML** fragment of `<row>` / `<cell>` elements, escaped once as the text of `<value>` in the `.iflw` (the **outer XML**).

| Fact | Evidence |
|---|---|
| Inner XML: a sequence of `<row><cell id='column'>value</cell>...</row>`. Attribute values use single quotes (`'`). | [f319ffe], [2c68cbe] |
| In the `.iflw`, the inner `<` and `>` appear as `&lt;` and `&gt;`, for example `&lt;row&gt;&lt;cell id='Action'&gt;Create&lt;/cell&gt;...`. The `'` is not escaped. | [f319ffe], [a85e897], [40a9c8b] |
| `${...}` is not escaped in either layer, for example `${header.SAP_MessageProcessingLogID}`. | [2c68cbe] |
| An empty table is `<value/>`. | [9d3de86], [ce88aae] |
| CPI also writes and accepts a row of empty cells, for example `clientCertificates` after Authorization was switched back to User Role: `&lt;row&gt;&lt;cell id='clientCertificate.subjectDN'&gt;&lt;/cell&gt;&lt;cell id='clientCertificate.issuerDN'&gt;&lt;/cell&gt;&lt;/row&gt;`. | [a3c03ec] |

## `<`, `&`, `>` inside a cell value: escape twice

Escape the character for the inner XML first (`<` → `&lt;`), then escape the result again for the outer XML (`&lt;` → `&amp;lt;`).

| Real value | Inner XML | Written in the `.iflw` |
|---|---|---|
| `<` | `&lt;` | `&amp;lt;` |
| `&` | `&amp;` | `&amp;amp;` |
| `>` | `&gt;` | `&amp;gt;` |

Example: the value `a<b & c>d` is written as `a&amp;lt;b &amp;amp; c&amp;gt;d` ([95802b3]).

| Fact | Evidence |
|---|---|
| Written this way, the value pulls, saves, deploys and runs. The UI shows `a<b & c>d` as Source Value and the response header value is `a<b & c>d`. | [95802b3] |
| CPI does not rewrite the double escaping on save or Push, even after other rows were added in the UI. | [1b5d158], [a85e897] |
| A new row with the value `x<y & z`, written as `x&amp;lt;y &amp;amp; z`, pulled, showed `x<y & z` in the designer, deployed, returned `x-eval3: x<y & z`, and was unchanged after Push. | [c6d9ca3] → [9898936] |
| A `<` escaped only once (`&lt;` in the `.iflw`) gives a designer validation error: `org.xml.sax.SAXParseException; ... Element type "b" must be followed by either attribute specifications, ">" or "/>"`. | [a517576] |
| An `&` escaped only once (`&amp;` in the `.iflw`) gives: `The entity name must immediately follow the '&' in the entity reference`. | [7827ffc] |
| In both cases **the whole table appears empty** in the designer, including valid rows. Other tables and the body of the same step are not affected. | [a517576], [7827ffc] |
| In both cases Pull succeeds. The error only appears in the designer's Problems tab (Location: Integration Flow Configuration). | [a517576], [7827ffc] |
| Whether a `>` escaped only once is accepted is **unverified**. Always escape `>` twice too. | — |

Because Pull does not catch these errors, run `scripts/check_iflw.py`: it unescapes each `headerTable` / `propertyTable` / `clientCertificates` once and checks that the result parses as rows and cells. It also prints a warning for a `>` in a cell that is escaped only once.

## Scope

| Fact | Evidence |
|---|---|
| The double-escaping rule was tested on `headerTable`. | [95802b3], [a517576], [7827ffc] |
| `propertyTable` has the same columns and storage format as `headerTable`, but special characters in it are **unverified**. | [ab24901] |
| `clientCertificates` (HTTPS sender) uses the same once-escaped table format. Special characters in it are **unverified**. | [40a9c8b] |
| `wrapContent` (Content Modifier message body) is plain text, not a table. How to write `<` or `&` in it is **unverified**: do not put `<` or `&` in a body; tell the user this is not covered yet. | — |

[1b5d158]: https://github.com/miyasuta/cpi-iflow-samples/commit/1b5d158
[2c68cbe]: https://github.com/miyasuta/cpi-iflow-samples/commit/2c68cbe
[40a9c8b]: https://github.com/miyasuta/cpi-iflow-samples/commit/40a9c8b
[7827ffc]: https://github.com/miyasuta/cpi-iflow-samples/commit/7827ffc
[95802b3]: https://github.com/miyasuta/cpi-iflow-samples/commit/95802b3
[9898936]: https://github.com/miyasuta/cpi-iflow-samples/commit/9898936
[9d3de86]: https://github.com/miyasuta/cpi-iflow-samples/commit/9d3de86
[a3c03ec]: https://github.com/miyasuta/cpi-iflow-samples/commit/a3c03ec
[a517576]: https://github.com/miyasuta/cpi-iflow-samples/commit/a517576
[a85e897]: https://github.com/miyasuta/cpi-iflow-samples/commit/a85e897
[ab24901]: https://github.com/miyasuta/cpi-iflow-samples/commit/ab24901
[c6d9ca3]: https://github.com/miyasuta/cpi-iflow-samples/commit/c6d9ca3
[ce88aae]: https://github.com/miyasuta/cpi-iflow-samples/commit/ce88aae
[f319ffe]: https://github.com/miyasuta/cpi-iflow-samples/commit/f319ffe
