from .models import ChatServerSettings
def chat_server_settings_context(request):
    settings_obj = ChatServerSettings.load()
    return {
       'chat_server_settings': settings_obj,
    }