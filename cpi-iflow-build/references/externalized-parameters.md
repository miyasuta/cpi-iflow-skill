# Externalized parameters

An externalized parameter replaces a value in the iFlow with `{{name}}`. The value that the parameter has when the iFlow is deployed is its default value. In the designer, the Externalized Parameters screen shows the parameter and lets a person set a different value (a configured value) without editing the iFlow.

This file holds only the behavior that was confirmed by a successful deployment and a call that worked.

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| HTTPS sender Address | Address | `urlPath` | `{{name}}`, for example `{{Address}}` |
| Content Modifier header cell, `Value` column | (no UI choice recorded) | `Value` cell of `headerTable` | `{{name}}`, for example `{{s03Greeting}}` |
| Content Modifier body | (no UI choice recorded) | `wrapContent` | `{{name}}`, for example `{{s03Body}}` |

## Behavior

- The whole value of the field is replaced by `{{name}}`. Nothing else in the iFlow changes, and the iFlow has no separate declaration of the parameter.
- In a Content Modifier header table, `{{name}}` goes in the `Value` cell. The row keeps its other cells: `Type` stays `constant`, and the `Default` cell stays empty. The braces are not escaped inside the cell.
- Parameter names that were deployed successfully are letters and digits in camelCase (`Address`, `s03Address`, `x02Greeting`).
- A default value chosen for the parameter is the value in effect after deployment when nothing is configured: a default of `/zt01/eval2` for the HTTPS sender Address was deployed, and the iFlow answered on `/zt01/eval2`, while the old address returned 404.
- Changing only the default value of an existing parameter, on an iFlow that has no configured values, takes effect on the next deployment.
- A value that a person sets in the Externalized Parameters screen (a configured value) is the value in effect after deployment. For the Address, the new address answered and the old one returned 404. The same was observed for a header cell and the body.
- Configuring a value does not change the `{{name}}` in the iFlow. The original default value is then no longer visible in the stored iFlow files.
- After the iFlow has been opened and saved in the designer, the designer adds to the parameter definitions a reference that ties the HTTPS sender Address parameter to the sender field (category `Sender`, attribute `/attrId::urlPath`). A parameter without this reference still worked when deployed.

## Pitfalls

- Do not assume that changing a default value changes the behavior of an iFlow that already has configured values: a configured value is expected to take precedence (SAP documentation), and this case was not deployed. Ask whether values were configured, and tell the person that this case is not verified.
- Only the fields in the Settings table were deployed externalized. Any other field is an unknown value: follow "Unknown values" in [SKILL.md](../SKILL.md).
- Only a whole field value replaced by `{{name}}` was deployed. `{{name}}` inside a larger value (for example `/x/{{a}}`) and one parameter reused in two fields were not deployed; they are unknown values too.
- Parameter values with special characters (`<`, `&`, `=`, `:`, `\`, line breaks) were not deployed; they are unknown values too.
- The designer may rewrite the parameter definitions when the iFlow is saved. This did not change the behavior of the deployed iFlow.
