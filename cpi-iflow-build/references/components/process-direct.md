# ProcessDirect

ProcessDirect connects two iFlows on the same tenant. The called iFlow has a ProcessDirect sender on its start event; the calling iFlow has a ProcessDirect receiver on a Request Reply step. Both name the same address.

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Adapter (sender) | (the adapter itself) | `ComponentType` | `ProcessDirect` |
| Adapter (sender) | (the adapter itself) | `ComponentNS` | `sap` |
| Adapter (sender) | (the adapter itself) | `Vendor` | `SAP` |
| Adapter (sender) | (the adapter itself) | `Name` | `ProcessDirect` |
| Adapter (sender) | (the adapter itself) | `ComponentSWCVName` | `external` |
| Adapter (sender) | (the adapter itself) | `ComponentSWCVId` | `1.1.2` |
| Adapter (sender) | (the adapter itself) | `componentVersion` | `1.1` |
| Adapter (sender) | (the adapter itself) | `cmdVariantUri` | `ctype::AdapterVariant/cname::ProcessDirect/vendor::SAP/tp::Not Applicable/mp::Not Applicable/direction::Sender/version::1.1.2` |
| Adapter (sender) | (the adapter itself) | `TransportProtocol` | `Not Applicable` |
| Adapter (sender) | (the adapter itself) | `TransportProtocolVersion` | `1.1.2` |
| Adapter (sender) | (the adapter itself) | `MessageProtocol` | `Not Applicable` |
| Adapter (sender) | (the adapter itself) | `MessageProtocolVersion` | `1.1.2` |
| Adapter (sender) | (the adapter itself) | `direction` | `Sender` |
| Adapter (sender) | the sender participant | `system` | its `name`, for example `Sender` |
| Adapter (sender) | (the adapter itself) | `Description` | empty |
| Address | the address the callers use | `address` | a path, for example `/Global/ODataV4Gateway/A4H` |
| Adapter (receiver) | (the adapter itself) | `cmdVariantUri` | `ctype::AdapterVariant/cname::ProcessDirect/vendor::SAP/tp::Not Applicable/mp::Not Applicable/direction::Receiver/version::1.1.1` |
| Adapter (receiver) | (the adapter itself) | `direction` | `Receiver` |
| Adapter (receiver) | the receiver participant | `system` | its `name`, for example `Receiver1` |
| Adapter (receiver) | the other keys | as for the sender | `ComponentType`, `ComponentNS`, `Vendor`, `Name`, `ComponentSWCVName`, `ComponentSWCVId` `1.1.2`, `componentVersion` `1.1`, `TransportProtocol`, `TransportProtocolVersion` `1.1.2`, `MessageProtocol`, `MessageProtocolVersion` `1.1.2`, `Description` |
| Address (receiver) | the called iFlow's address | `address` | the same path as on its sender, for example `/Global/ODataV4Gateway/A4H` |
| Integration Flow > Runtime Configuration > Allowed Header(s) | the headers passed between the two iFlows | `allowedHeaderList` | names separated by `\|`, on both iFlows (see Pitfalls) |

The receiver's `cmdVariantUri` ends in `version::1.1.1` while its other version keys are `1.1.2`; this is what the designer saved, and it deployed and ran.

## Pitfalls

- A header is passed to the called iFlow only when its name is in Allowed Header(s). With the list empty, headers set by the caller (for example a path in `odataServicePath`) did not arrive, the called iFlow built an empty address, and its backend returned `404`. With the names in `allowedHeaderList` of both iFlows, they arrived. The response headers that came back to the caller's client were also listed in the caller's `allowedHeaderList` (for example `odataStatusCode|ETag|Location|sap-messages`).
- Put the ProcessDirect receiver on a Request Reply step when the caller needs the reply; the called iFlow's body and headers then come back into the caller's message.
- The MCP server cpi-saper-dev-mcp has no ProcessDirect receiver in its catalog, so it cannot add one: add it once in the designer, save, import the iFlow, and build the rest through the MCP server.
- Saving an iFlow in the designer renamed its HTTP receiver channels to `HTTP`. After such a save, refer to adapters by their id, not by their name.
- A Router, Content Modifiers and HTTP receivers in the called iFlow ran for every caller request, and an error there reached the caller (see [exception-subprocess.md](exception-subprocess.md), Ending with Error End).
