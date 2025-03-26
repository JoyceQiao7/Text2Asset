extends Control

@onready var style_selector = $OptionButton
@onready var text_input = $TextEdit
@onready var generate_button = $Button
@onready var status_label = $Label
@onready var http_request = $HTTPRequest

var current_description = ""  # Store the description for use in _on_request_completed
var image_counter = 0  # Ensure uniqueness even with duplicate descriptions
var current_style = ""
var GeminiAPIKEY = "REPLACE WITH YOUR GEMINI API KEY"
var RemovebgAPIKEY = "REPLACE WITH YOUR REMOVEBG API KEY"

func _ready():
	generate_button.connect("pressed", _on_generate_pressed)
	http_request.connect("request_completed", _on_request_completed)
	var dir = DirAccess.open("res://")
	if not dir.dir_exists("generated"):
		dir.make_dir("generated")

func _on_generate_pressed():
	var style = style_selector.get_item_text(style_selector.selected)
	current_style = style
	var description = text_input.text
	current_description = description
	status_label.text = "Generating..."
	generate_asset(style, description)

func generate_asset(style: String, description: String):
	var url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key=" + GeminiAPIKEY
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({
		"contents": [{
			"parts": [
				{"text": description + " in " + style + " style, isolated as a complete object with a one-color background, suitable as a game sprite."}
			]
		}],
		"generationConfig": {"responseModalities": ["Text", "Image"]}
	})
	http_request.request(url, headers, HTTPClient.METHOD_POST, body)

func remove_background(file_path: String):
	var url = "https://api.remove.bg/v1.0/removebg"
	var headers = [
		"X-Api-Key: " + RemovebgAPIKEY
	]
	
	# Read the image file into a PackedByteArray
	var file = FileAccess.open(file_path, FileAccess.READ)
	if file == null:
		status_label.text = "Error: Could not read file at " + file_path
		return
	var image_data = file.get_buffer(file.get_length())
	file.close()
	
	# Prepare multipart/form-data body
	var boundary = "----GodotBoundary" + str(randi())
	var body = PackedByteArray()
	
	# Add image_file field
	body.append_array(("--" + boundary + "\r\n").to_utf8_buffer())
	body.append_array(('Content-Disposition: form-data; name="image_file"; filename="' + file_path.get_file() + '"\r\n').to_utf8_buffer())
	body.append_array("Content-Type: image/png\r\n\r\n".to_utf8_buffer())
	body.append_array(image_data)
	body.append_array("\r\n".to_utf8_buffer())
	
	# Add size field
	body.append_array(("--" + boundary + "\r\n").to_utf8_buffer())
	body.append_array('Content-Disposition: form-data; name="size"\r\n\r\n'.to_utf8_buffer())
	body.append_array("auto\r\n".to_utf8_buffer())
	
	# Close the multipart body
	body.append_array(("--" + boundary + "--\r\n").to_utf8_buffer())
	
	# Set the Content-Type header with the boundary
	headers.append("Content-Type: multipart/form-data; boundary=" + boundary)
	
	# Store the output path in metadata for the response handler
	http_request.set_meta("output_path", file_path)
	http_request.request_raw(url, headers, HTTPClient.METHOD_POST, body)

func _on_request_completed(result, response_code, headers, body):
	if response_code == 200:
		if body.get_string_from_utf8().begins_with("{"):  # Gemini response
			var data = body.get_string_from_utf8()
			var json = JSON.parse_string(data)
			var candidate = json["candidates"][0]
			var parts = candidate["content"]["parts"]
			for part in parts:
				if "inlineData" in part and "data" in part["inlineData"]:
					var base64_data = part["inlineData"]["data"]
					var image_data = Marshalls.base64_to_raw(base64_data)
							
					# Generate unique image name and save the original image
					var safe_description = current_description.replace(" ", "_").replace(",", "").to_lower()
					if safe_description.length() > 50:
						safe_description = safe_description.substr(0, 50)
					image_counter += 1
					var file_path = "res://generated/" + safe_description + "_" + str(image_counter) + ".png"
					var file = FileAccess.open(file_path, FileAccess.WRITE)
					if file == null:
						status_label.text = "Error: Could not write file at " + file_path
						return
					file.store_buffer(image_data)
					file.close()
							
					status_label.text = "Generated image, removing background..."
					remove_background(file_path)
					return
			status_label.text = "No image data found in response"
		else:  # remove.bg response
			var output_path = http_request.get_meta("output_path")
			var file = FileAccess.open(output_path, FileAccess.WRITE)
			if file == null:
				status_label.text = "Error: Could not write file at " + output_path
				return
			file.store_buffer(body)
			file.close()
			status_label.text = "Background removed, saved to " + output_path
	else:
		status_label.text = "Error: " + str(response_code)
