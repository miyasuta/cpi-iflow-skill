import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    def greeting = message.getHeaders().get("X-X02-Greeting") ?: "none"
    message.setHeader("X-X02-Script", "set-by-script")
    message.setBody("Groovy (edited) saw: " + greeting)
    return message
}
