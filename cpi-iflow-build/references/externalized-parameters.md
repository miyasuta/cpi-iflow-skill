# Externalized parameters

An externalized parameter replaces a value in the iFlow with `{{name}}`. The value that the parameter has when the iFlow is deployed is its default value. In the designer, the Externalized Parameters screen shows the parameter and lets a person set a different value (a configured value) without editing the iFlow.

This file holds only the behavior that was confirmed by a successful deployment and a call that worked.

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| HTTPS sender Address | Address | `urlPath` | `{{name}}`, for example `{{Address}}` |
| Content Modifier header cell, `Value` column | (no UI choice recorded) | `Value` cell of `headerTable` | `{{name}}`, for example `{{s03Greeting}}` |
| Content Modifier body | (no UI choice recorded) | `wrapContent` | `{{name}}`, for example `{{s03Body}}` |
| HTTP receiver Address | the start of the address | `httpAddressWithoutQuery` | `{{name}}` followed by expressions, for example `{{A4H_BaseUrl}}${property.odataServicePath}` |
| HTTP receiver Address | a parameter in the middle or at the end, after fixed text | `httpAddressWithoutQuery` | for example `https://{{echoHost}}/http/zdev/verify-echo-target`, or `https://<runtime host>/http/zdev/{{echoPath}}` |
| HTTP receiver Location ID | Location ID | `locationID` | `{{name}}`, for example `{{A4H_LocationID}}` (its value may be empty) |
| HTTP receiver Credential Name | Credential Name | `credentialName` | `{{name}}`, for example `{{A4H_Credential}}` |
| Content Modifier header cell, `Value` column | inside a constant | `Value` cell of `headerTable` | `{{name}}`, for example `{{A4H_SapClient}}` |

## Behavior

- In the fields of the Settings table, `{{name}}` replaces the whole value, except where a row shows it inside a larger value. Nothing else in the iFlow changes, and the iFlow has no separate declaration of the parameter.
- In a Content Modifier header table, `{{name}}` goes in the `Value` cell. The row keeps its other cells: `Type` stays `constant`, and the `Default` cell stays empty. The braces are not escaped inside the cell.
- Parameter names that were deployed successfully are letters and digits in camelCase (`Address`, `s03Address`, `x02Greeting`), and letters and digits with `_` (`A4H_BaseUrl`).
- A parameter at the start of a larger value worked: `{{A4H_BaseUrl}}${property.odataServicePath}${property.odataResourcePath}` in the HTTP receiver Address resolved to the parameter followed by the property values.
- A parameter in the middle (`https://{{echoHost}}/http/...`) or at the end (`https://<host>/http/zdev/{{echoPath}}`) of the HTTP receiver Address worked: the default value took the place of `{{name}}`, the fixed text around it stayed as written, and the target was reached.
- One parameter used in two fields worked: `{{A4H_Credential}}` and `{{A4H_LocationID}}` were in two HTTP receivers of one iFlow.
- A parameter whose value is empty (`A4H_LocationID=`) deployed and gave an empty Location ID.
- A default value chosen for the parameter is the value in effect after deployment when nothing is configured: a default of `/zt01/eval2` for the HTTPS sender Address was deployed, and the iFlow answered on `/zt01/eval2`, while the old address returned 404.
- Changing only the default value of an existing parameter, on an iFlow that has no configured values, takes effect on the next deployment.
- A value that a person sets in the Externalized Parameters screen (a configured value) is the value in effect after deployment. For the Address, the new address answered and the old one returned 404. The same was observed for a header cell and the body.
- Configuring a value does not change the `{{name}}` in the iFlow. The original default value is then no longer visible in the stored iFlow files.
- After the iFlow has been opened and saved in the designer, the designer adds to the parameter definitions a reference that ties the HTTPS sender Address parameter to the sender field (category `Sender`, attribute `/attrId::urlPath`). A parameter without this reference still worked when deployed.

## Pitfalls

- Do not assume that changing a default value changes the behavior of an iFlow that already has configured values: a configured value is expected to take precedence (SAP documentation), and this case was not deployed. Ask whether values were configured, and tell the person that this case is not verified.
- Only the fields in the Settings table were deployed externalized. Any other field is an unknown value: follow "Unknown values" in [SKILL.md](../SKILL.md).
- A parameter at the start, in the middle and at the end of a larger value was deployed only in the HTTP receiver Address. In any other field, a parameter inside a larger value is an unknown value.
- Parameter values with special characters (`<`, `&`, `=`, `:`, `\`, line breaks) were not deployed; they are unknown values too.
- The designer may rewrite the parameter definitions when the iFlow is saved. This did not change the behavior of the deployed iFlow.
