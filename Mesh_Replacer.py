'''
READ ME

Author
Micah Jordan

Date
5/7/2021

This Unreal tool allows the user to replace multiple meshes in a level with new imports and make adjustments to the newly created material instance of the mesh.

Functions: 
- Import FBX meshes 
- Replace placeholder mesh in game level with newly imported mesh 
    - Location and rotation of new mesh should be the same as placeholder 
- Create a Master Material 
- Create a material instance for each newly imported FBX 
- Input values for certain material properties 
    - Base Color, Normal, Metallic, Roughness 

Add this folder as a plugin to the desired project make use of the tool. 

'''

import unreal
import os

def replace_mesh_actor (fbx_path, destination_path, location, rotation):
   
    # Get FBX namespace
    file_path_dir, file_path_name = os.path.split(fbx_path)
    fbx_name, file_path_ext = os.path.splitext(file_path_name)

    # Make FBX file path in unreal
    unreal_fbx_path = destination_path + "/{0}".format (fbx_name)

    fbx_imported = unreal.EditorAssetLibrary.does_asset_exist (unreal_fbx_path)

    # Import the FBX
    if not fbx_imported: 

        # Setting fbx section options
        fbx_import_data = unreal.FbxAnimSequenceImportData()
        fbx_import_data.set_editor_property ("convert_scene", True)
        fbx_import_data.set_editor_property ("convert_scene_unit", True)
        fbx_import_data.set_editor_property ("force_front_x_axis", False)

        # Setting import options 
        ui_import_options = unreal.FbxImportUI()
        ui_import_options.reset_to_default()
        ui_import_options.set_editor_property("automated_import_should_detect_type", False)
        ui_import_options.set_editor_property("create_physics_asset", False)
        ui_import_options.set_editor_property("import_animations", False)
        ui_import_options.set_editor_property("import_as_skeletal", True)
        ui_import_options.set_editor_property("import_materials", False)
        ui_import_options.set_editor_property("import_mesh", True)
        ui_import_options.set_editor_property("import_rigid_mesh", False)
        ui_import_options.set_editor_property("import_textures", False)
        ui_import_options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
        ui_import_options.set_editor_property("skeleton", None)
        ui_import_options.set_editor_property("anim_sequence_import_data", fbx_import_data)

        # Import fbx with options, fbx path, and destination path
        asset_import_task = unreal.AssetImportTask()
        asset_import_task.set_editor_property("automated", True)
        asset_import_task.set_editor_property("destination_path", destination_path)
        asset_import_task.set_editor_property("filename", fbx_path)
        asset_import_task.set_editor_property("options", ui_import_options)
        asset_import_task.set_editor_property("save", True)

        tasks = [asset_import_task]

        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

        unreal.AssetTools.import_asset_tasks(asset_tools, tasks)

    # Replace in game mesh with new fbx path 
    fbx_obj = unreal.EditorAssetLibrary.load_asset (unreal_fbx_path)
    unreal.EditorLevelLibrary.spawn_actor_from_object (fbx_obj, location, rotation)
    fbx_asset_data = unreal.EditorAssetLibrary.find_asset_data(unreal_fbx_path)

    # Create Material folder 
    mat_folder = destination_path + "Materials/"

    if not unreal.EditorAssetLibrary.does_directory_exist(mat_folder):
        unreal.EditorAssetLibrary.make_directory(mat_folder)

    # Create Master Material 
    master_mat_exists = unreal.EditorAssetLibrary.does_asset_exist (mat_folder + "Master_Material")
    
    if not master_mat_exists: 
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        master_mat = asset_tools.create_asset("Master_Material", mat_folder, unreal.Material, unreal.MaterialFactoryNew())

        # Create parameter values for master material 
        
        # Temporary textures 
        temp_base = unreal.EditorAssetLibrary.find_asset_data("/Game/StarterContent/Textures/T_Concrete_Tiles_D").get_asset()
        temp_normal = unreal.EditorAssetLibrary.find_asset_data("/Game/StarterContent/Textures/T_Brick_Clay_Beveled_N").get_asset()
        
        # Base Color 
        b_color_node = unreal.MaterialEditingLibrary.create_material_expression(master_mat,unreal.MaterialExpressionTextureSampleParameter2D,-384,200)
        b_color_node.texture = temp_base
       
        # Metallic
        metallic_node = unreal.MaterialEditingLibrary.create_material_expression(master_mat,unreal.MaterialExpressionScalarParameter,-384,200)
        
        # Normal
        normal_node = unreal.MaterialEditingLibrary.create_material_expression(master_mat,unreal.MaterialExpressionTextureSampleParameter2D,-384,200)
        normal_node.texture = temp_normal
        normal_node.sampler_type = unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
       
        # Roughness 
        roughness_node = unreal.MaterialEditingLibrary.create_material_expression(master_mat,unreal.MaterialExpressionScalarParameter,-384,200)
        
        # Connect new parameter nodes to material property 
        unreal.MaterialEditingLibrary.connect_material_property(b_color_node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        unreal.MaterialEditingLibrary.connect_material_property(metallic_node, "", unreal.MaterialProperty.MP_METALLIC)
        unreal.MaterialEditingLibrary.connect_material_property(normal_node, "RGB", unreal.MaterialProperty.MP_NORMAL)
        unreal.MaterialEditingLibrary.connect_material_property(roughness_node, "", unreal.MaterialProperty.MP_ROUGHNESS)
        
        # Save Master Material 
        master_mat_obj = unreal.load_object(None, mat_folder + "Master_Material")
        unreal.MaterialEditingLibrary.recompile_material (master_mat_obj) 
        unreal.EditorAssetLibrary.save_asset(mat_folder + "Master_Material" , only_if_is_dirty = False)

    # Create material instance
    mat_inst_name = "MI_" + fbx_name
    mat_inst_path = mat_folder + mat_inst_name
       
    if not unreal.EditorAssetLibrary.does_asset_exist(mat_inst_path): 
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        mat_inst = asset_tools.create_asset(mat_inst_name, mat_folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())

        # Set parent material for material instance and save 
        master_mat_data = unreal.EditorAssetLibrary.find_asset_data(mat_folder + "Master_Material")
        unreal.MaterialEditingLibrary.set_material_instance_parent(mat_inst, master_mat_data.get_asset()) 
        unreal.EditorAssetLibrary.save_asset(mat_folder + mat_inst_name, only_if_is_dirty = False)

    # Get material instance object 
    mat_inst_obj = unreal.load_object(None, mat_inst_path)

    # Assigning material to fbx and save
    fbx_asset = fbx_asset_data.get_asset()
    fbx_asset.set_material(0, mat_inst_obj)
    unreal.EditorAssetLibrary.save_asset(unreal_fbx_path, only_if_is_dirty = False)


def set_mat_tex (curr_mat, mat_path, tex_path, array_index):

    if tex_path != "None": 

        tex_asset = unreal.EditorAssetLibrary.find_asset_data(tex_path).get_asset()
 
        if array_index == 0: 
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(curr_mat, "Param", tex_asset)

        if array_index == 1: 
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(curr_mat, "Param_1", tex_asset)
        
        unreal.EditorAssetLibrary.save_asset(mat_path, only_if_is_dirty = False)         
        
    else: 
        pass 


def set_mat_scalar_param (curr_mat, mat_path, value, array_index):
    
    if value != 0.0: 

        if array_index == 0: 
            unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(curr_mat, "Param", value)

        if array_index == 1: 
            unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(curr_mat, "Param_1", value)  
        
        unreal.EditorAssetLibrary.save_asset(mat_path, only_if_is_dirty = False)         
        
    else: 
        pass 


         
        





