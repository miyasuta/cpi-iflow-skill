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

## Settings for step version 2.0.0 (Groovy 4)

The step version `2.0.0` runs the script with Groovy 4 (the tenant showed runtime 4.0.29 when it ran; the tenant updates it). It deployed and ran (a header was added to the response) with these settings; the other keys of the table above are as for 1.1.2.

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Groovy Script | (the step itself) | `componentVersion` | `2.0` |
| Groovy Script | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::GroovyScript/version::2.0.0` |
| (no UI label recorded) | the script file | `script` | `v2/<file name>.groovy`, for example `v2/script1.groovy` |

The script file is `src/main/resources/script/v2/<file name>.groovy`. This form deployed and ran:

```groovy
package script.v2
import com.sap.it.script.v2.api.Message;

def Message processData(Message message) {
    message.setHeader("X-Added-By", "groovy-script")
    return message
}
```

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
- With step version `2.0.0`, the script must use the 2.x form (`package script.v2`, `import com.sap.it.script.v2.api.Message;`). The 1.x import `com.sap.gateway.ip.core.customdev.util.Message` deployed without any error and failed at the first call with HTTP 500: `unable to resolve class com.sap.gateway.ip.core.customdev.util.Message`. A deployment alone does not show it; call the iFlow.
- The designer's template for a new script of a 2.0.0 step shows the 2.x form. The 1.x and 2.x scripts are separate files (`script/<name>.groovy` and `script/v2/<name>.groovy`).
