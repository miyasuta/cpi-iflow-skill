import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    def body = message.getBody(String)
    def name = message.getHeaders().get("X-S02-Name") ?: "world"
    message.setHeader("X-S02-Script", "set-by-script")
    message.setProperty("s02Property", "from-script")
    message.setBody("Hello, " + name + ". Property: " + message.getProperty("s02Property") + ". Received: " + body)
    return message
}