from backend.app.services.memory_service import (
    add_message,
    get_history,
    clear_history
)

add_message("abc", "user", "Hello")
add_message("abc", "assistant", "Hi!")

print(get_history("abc"))