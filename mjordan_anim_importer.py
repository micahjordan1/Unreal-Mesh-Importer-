'''
READ ME

Author 
Micah Jordan 

This Unreal tool allows the user to import a batch of animation files from a directory, and apply them to an exsiting skeletal mesh in the Unreal project. 
Add this corresponding folder as a new plugin to make use of it. 

'''

import unreal
import os

def import_skeletal_animation(skeleton, input_path, destination_path):

    # Setting animation section options
    anim_seq_import_data = unreal.FbxAnimSequenceImportData()
    anim_seq_import_data.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    anim_seq_import_data.set_editor_property("convert_scene", True)
    anim_seq_import_data.set_editor_property("use_default_sample_rate", True)
    anim_seq_import_data.set_editor_property("import_bone_tracks", True)
    anim_seq_import_data.set_editor_property("import_meshes_in_bone_hierarchy", False)
    anim_seq_import_data.set_editor_property("import_custom_attribute", False)
    anim_seq_import_data.set_editor_property("remove_redundant_keys", False)

    # Setting import options
    ui_import_options = unreal.FbxImportUI()
    ui_import_options.reset_to_default()
    ui_import_options.set_editor_property("automated_import_should_detect_type", False)
    ui_import_options.set_editor_property("create_physics_asset", False)
    ui_import_options.set_editor_property("import_animations", True)
    ui_import_options.set_editor_property("import_as_skeletal", False)
    ui_import_options.set_editor_property("import_materials", False)
    ui_import_options.set_editor_property("import_mesh", False)
    ui_import_options.set_editor_property("import_rigid_mesh", False)
    ui_import_options.set_editor_property("import_textures", False)
    ui_import_options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
    ui_import_options.set_editor_property("skeleton", skeleton)
    ui_import_options.set_editor_property("anim_sequence_import_data", anim_seq_import_data)

    # Import animation with options, input path, and destination path
    asset_import_task = unreal.AssetImportTask()
    asset_import_task.set_editor_property("automated", True)
    asset_import_task.set_editor_property("destination_path", destination_path)
    asset_import_task.set_editor_property("filename", input_path)
    asset_import_task.set_editor_property("options", ui_import_options)
    asset_import_task.set_editor_property("save", True)

    tasks = [asset_import_task]

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    unreal.AssetTools.import_asset_tasks(asset_tools, tasks)


# import each anim file in given directory 
def import_batch_skel_anim (skeleton, input_dir, destination_path): 
    
    for anim_file in os.listdir(input_dir): 

        full_anim_path = os.path.join (input_dir, anim_file) 

        import_skeletal_animation(skeleton, full_anim_path, destination_path)




