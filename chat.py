import flet as ft
import os
import google.generativeai as genai
import time

# Configure the AI model using an environment variable for the API key
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    raise ValueError("The environment variable 'GENAI_API_KEY' is not set")
genai.configure(api_key=api_key)

def create_model(system_instruction):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 5000,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    return model

def get_ai_response(user_input, model):
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(user_input)
    return response.text

class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize() if user_name else "Unknown"

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER, ft.colors.BLUE, ft.colors.BROWN, ft.colors.CYAN,
            ft.colors.GREEN, ft.colors.INDIGO, ft.colors.LIME, ft.colors.ORANGE,
            ft.colors.PINK, ft.colors.PURPLE, ft.colors.RED, ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

def main(page: ft.Page):
    page.window.maximized = True
    page.title = "Flet Chat"

    chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
    )

    def join_chat_click(e):
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
        elif not system_instruction.value:
            system_instruction.error_text = "System instruction cannot be blank!"
            system_instruction.update()
        else:
            page.session.set("user_name", join_user_name.value)
            page.session.set("system_instruction", system_instruction.value)
            global model
            model = create_model(system_instruction.value)
            dialog.open = False
            new_message.prefix = ft.Text(f"{join_user_name.value}: ")
            chat.controls.append(ft.Text(f"{join_user_name.value} has joined the chat.", italic=True, color=ft.colors.BLACK45, size=12))
            page.update()

    def send_message_click(e):
        if new_message.value:
            user_name = page.session.get("user_name")
            user_message = new_message.value
            
            # Add user message to chat
            chat.controls.append(ChatMessage(Message(user_name, user_message, "chat_message")))
            new_message.value = ""
            page.update()

            # Show "AI is typing" message
            typing_message = ft.Text("AI is typing...", italic=True, color=ft.colors.BLACK45)
            chat.controls.append(typing_message)
            page.update()

            # Get AI response
            try:
                ai_response = get_ai_response(user_message, model)
                
                # Remove "AI is typing" message
                chat.controls.remove(typing_message)
                
                # Add AI response to chat
                chat.controls.append(ChatMessage(Message("AI Bot", ai_response, "chat_message")))
            except Exception as e:
                print(f"Error getting AI response: {e}")
                chat.controls.append(ft.Text("An error occurred while processing your request.", italic=True, color=ft.colors.RED))
            
            page.update()

    # Dialog for user display name and system instruction
    join_user_name = ft.TextField(label="Enter your name to join the chat", autofocus=True)
    system_instruction = ft.TextField(label="Enter system instruction for the AI")
    dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([join_user_name, system_instruction], width=300, height=140, tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_chat_click)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = dialog

    # Add components to the page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter" and not e.shift:
            send_message_click(e)

    page.on_keyboard_event = on_keyboard

ft.app(target=main)