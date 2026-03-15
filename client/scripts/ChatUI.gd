extends Control

@onready var chat_history: RichTextLabel = $MarginContainer/HBoxContainer/VBoxContainer/ScrollContainer/ChatHistory
@onready var line_edit: LineEdit = $MarginContainer/HBoxContainer/VBoxContainer/InputArea/LineEdit
@onready var send_button: Button = $MarginContainer/HBoxContainer/VBoxContainer/InputArea/SendButton
@onready var avatar_rect: TextureRect = $MarginContainer/HBoxContainer/AvatarRect

# 預載頭像圖片 (需在 assets/ 目錄放置這些圖片)
# 為避免啟動報錯，如果沒有圖片則保持為空
var avatars = {
	"neutral": load("res://assets/neutral.png"),
	"happy": load("res://assets/happy.png"),
	"sad": load("res://assets/sad.png"),
	"angry": load("res://assets/angry.png")
}

var character_name = "Elf Ranger"

func _ready() -> void:
	# 設定初始頭像
	_set_avatar("neutral")
	
	# 連接 NetworkManager 信號
	# 需要先將 NetworkManager 加到 Autoload (Project Settings -> Globals -> NetworkManager)
	if has_node("/root/NetworkManager"):
		var net = get_node("/root/NetworkManager")
		net.response_received.connect(_on_ai_response_received)
		net.request_failed.connect(_on_ai_request_failed)

func _on_send_button_pressed() -> void:
	_send_message()

func _on_line_edit_text_submitted(_new_text: String) -> void:
	_send_message()

func _send_message() -> void:
	var text = line_edit.text.strip_edges()
	if text.is_empty():
		return
		
	line_edit.clear()
	_append_chat("You", text, "#5b8cff") 
	
	line_edit.editable = false
	send_button.disabled = true
	
	if has_node("/root/NetworkManager"):
		get_node("/root/NetworkManager").send_message(text)
	else:
		_append_chat("System", "NetworkManager is not loaded in Autoload.", "#ff4444")

func _on_ai_response_received(text: String, emotion: String, _animation_trigger: String) -> void:
	line_edit.editable = true
	send_button.disabled = false
	
	_append_chat(character_name, text, "#ffcc5b")
	_set_avatar(emotion)

func _on_ai_request_failed(error_msg: String) -> void:
	line_edit.editable = true
	send_button.disabled = false
	
	_append_chat("System", "Error: " + error_msg, "#ff4444")

func _append_chat(sender: String, message: String, color: String = "#ffffff") -> void:
	var bbcode = "[color=%s][b]%s:[/b][/color] %s\n\n" % [color, sender, message]
	chat_history.append_text(bbcode)

func _set_avatar(emotion: String) -> void:
	if avatars.has(emotion) and avatars[emotion] != null:
		avatar_rect.texture = avatars[emotion]
	else:
		# fallback
		avatar_rect.texture = avatars["neutral"]
