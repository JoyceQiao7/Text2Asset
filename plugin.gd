@tool
extends EditorPlugin

var dock_instance

func _enter_tree():
	# Instantiate the UI and add it as a dock
	dock_instance = preload("res://addons/Text2Asset/ui.tscn").instantiate()
	add_control_to_dock(DOCK_SLOT_RIGHT_UL, dock_instance)

func _exit_tree():
	remove_control_from_docks(dock_instance)
	dock_instance.queue_free()
