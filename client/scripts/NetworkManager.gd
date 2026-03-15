extends Node

signal response_received(text: String, emotion: String, animation_trigger: String)
signal request_failed(error_msg: String)

var http_request: HTTPRequest
var server_url: String = "http://127.0.0.1:8000/api/v1/chat/"

func _ready() -> void:
	if ProjectSettings.has_setting("application/config/server_url"):
		server_url = ProjectSettings.get_setting("application/config/server_url")
	http_request = HTTPRequest.new()
	http_request.timeout = 30.0 # 設定 30 秒超時
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)

func send_message(message: String, user_id: String = "player_001", character_id: String = "elf_ranger") -> void:
	var body: Dictionary = {
		"message": message,
		"user_id": user_id,
		"character_id": character_id
	}
	var json_str: String = JSON.stringify(body)
	var headers: PackedStringArray = ["Content-Type: application/json"]
	
	var err: int = http_request.request(server_url, headers, HTTPClient.METHOD_POST, json_str)
	if err != OK:
		request_failed.emit("Failed to send request: " + str(err))

func _on_request_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS or response_code != 200:
		request_failed.emit("Server error or unreachable. Code: " + str(response_code))
		return
		
	var body_string: String = body.get_string_from_utf8()
	var json: JSON = JSON.new()
	var parse_err: int = json.parse(body_string)
	
	if parse_err != OK:
		request_failed.emit("Failed to parse JSON response")
		return
		
	var data: Dictionary = json.data as Dictionary
	if data.has("response"):
		var text: String = data.get("response", "")
		var emotion: String = data.get("emotion", "neutral")
		var anim_raw = data.get("animation_trigger", null)
		var anim: String = str(anim_raw) if anim_raw != null else ""
		response_received.emit(text, emotion, anim)
	elif data.has("error"):
		request_failed.emit(data.get("error"))
	else:
		request_failed.emit("Unknown response format")
