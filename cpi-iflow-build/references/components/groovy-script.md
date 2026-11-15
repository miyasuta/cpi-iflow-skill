# Groovy Script

A Groovy Script step runs a script file that belongs to the iFlow. The step names the file; the file holds the code.

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Groovy Script | (the step itself) | `componentVersion` | `1.1` |
| Groovy Script | (the step itself) | `activityType` | `Script` |
| Groovy Script | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::GroovyScript/version::1.1.2` |
| Groovy Script | (the step itself) | `subActivityType` | `GroovyScript` |
| (no UI label recorded) | the function to run | `scriptFunction` | empty; the function `processData` ran |
| (no UI label recorded) | script collection | `scriptBundleId` | empty |
| (no UI label recorded) | the script file | `script` | the file name only, for example `script1.groovy` (not `script/script1.groovy`) |

## The script file

The file is `src/main/resources/script/<file name>.groovy` in the iFlow. This form deployed and ran, with no `package` line:

```groovy
import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    def greeting = message.getHeaders().get("X-X02-Greeting") ?: "none"
    message.setHeader("X-X02-Script", "set-by-script")
    message.setBody("Groovy saw: " + greeting)
    return message
}
```

Calls that deployed and ran: `message.getBody(String)`, `message.getHeaders().get(name)`, `message.setHeader(name, value)`, `message.setProperty(name, value)`, `message.getProperty(name)`, `message.setBody(value)`.

## Pitfalls

- The step needs its script file. Without a file named in `script`, the designer reports the error `Script File not defined for Script Processor step`. Every deployed Groovy Script step had its file in `script/`.
- Define `processData` with exactly the signature above: `scriptFunction` is empty, and that function ran.
- The script file was `script1.groovy` in every iFlow that deployed with this step version. Changing only the code of an existing file, with the step untouched, deployed and the new code ran.
- A header set earlier in the iFlow (for example by a Content Modifier) can be read in the script without any further setting.
- A header sent by the caller cannot be read in the script unless its name is in Allowed Header(s) on the integration flow: while the list was empty, the script got its default value; with the name listed, it read the sent value. The header was then also returned in the response. See [router.md](router.md) for the key.
- A script that throws an exception ends the main flow at that step. An Exception Subprocess catches it; see [exception-subprocess.md](exception-subprocess.md).
- A Groovy Script step added between two existing steps, together with a new script file, deployed and ran.
