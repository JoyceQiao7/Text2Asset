extends Node

var ui_instance

func _ready():
	ui_instance = preload("res://addons/Text2Asset/ui.tscn").instantiate()
	add_child(ui_instance)
