import com.sap.gateway.ip.core.customdev.util.Message

def Message processData(Message message) {
    message.setHeader("X-Eval3-Script", "inserted")
    return message
}
