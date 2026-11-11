if build_games
  if host_system == 'windows'
    game_module_target = shared_module(
      game_binary_name,
      game_sources,
      include_directories: game_include_dirs,
      link_with: game_idlib_library,
      cpp_args: game_common_cpp_args,
      c_args: game_common_c_args,
      cpp_pch: game_module_pch_headers,
      override_options: game_target_override_options,
      link_args: game_module_link_args,
      vs_module_defs: game_module_defs_file,
      name_prefix: module_filename_prefix,
      install: true,
      install_dir: install_module_dir,
    )
  elif host_system == 'darwin'
    game_module_target = shared_library(
      game_binary_name,
      game_sources,
      include_directories: game_include_dirs,
      link_with: game_idlib_library,
      cpp_args: game_common_cpp_args,
      c_args: game_common_c_args,
      cpp_pch: game_module_pch_headers,
      override_options: game_target_override_options,
      link_args: game_module_link_args + ['-Wl,-install_name,@loader_path/' + game_binary_name + '.dylib'],
      link_depends: game_module_link_depends,
      gnu_symbol_visibility: 'hidden',
      name_prefix: module_filename_prefix,
      name_suffix: 'dylib',
      install: true,
      install_dir: install_module_dir,
    )
  else
    game_module_target = shared_module(
      game_binary_name,
      game_sources,
      include_directories: game_include_dirs,
      link_with: game_idlib_library,
      cpp_args: game_common_cpp_args,
      c_args: game_common_c_args,
      cpp_pch: game_module_pch_headers,
      override_options: game_target_override_options,
      link_args: game_module_link_args,
      link_depends: game_module_link_depends,
      gnu_symbol_visibility: 'hidden',
      name_prefix: module_filename_prefix,
      install: true,
      install_dir: install_module_dir,
    )
  endif
endif

if build_game_d3xp
  if host_system == 'windows'
    game_d3xp_module_target = shared_module(
      game_d3xp_binary_name,
      game_d3xp_sources,
      include_directories: game_include_dirs,
      link_with: game_idlib_library_d3xp,
      cpp_args: game_common_cpp_args + game_d3xp_cpp_args,
      c_args: game_common_c_args,
      cpp_pch: game_module_pch_headers,
      override_options: game_target_override_options,
      link_args: game_module_link_args,
      vs_module_defs: game_d3xp_module_defs_file,
      name_prefix: module_filename_prefix,
      install: true,
      install_dir: install_module_dir,
    )
  elif host_system == 'darwin'
    game_d3xp_module_target = shared_library(
      game_d3xp_binary_name,
      game_d3xp_sources,
      include_directories: game_include_dirs,
      link_with: game_idlib_library_d3xp,
      cpp_args: game_common_cpp_args + game_d3xp_cpp_args,
      c_args: game_common_c_args,
      cpp_pch: game_module_pch_headers,
      override_options: game_target_override_options,
      link_args: game_module_link_args + ['-Wl,-install_name,@loader_path/' + game_d3xp_binary_name + '.dylib'],
      link_depends: game_module_link_depends,
      gnu_symbol_visibility: 'hidden',
      name_prefix: module_filename_prefix,
      name_suffix: 'dylib',
      install: true,
      install_dir: install_module_dir,
    )
  else
    game_d3xp_module_target = shared_module(
      game_d3xp_binary_name,
      game_d3xp_sources,
      include_directories: game_include_dirs,
      link_with: game_idlib_library_d3xp,
      cpp_args: game_common_cpp_args + game_d3xp_cpp_args,
      c_args: game_common_c_args,
      cpp_pch: game_module_pch_headers,
      override_options: game_target_override_options,
      link_args: game_module_link_args,
      link_depends: game_module_link_depends,
      gnu_symbol_visibility: 'hidden',
      name_prefix: module_filename_prefix,
      install: true,
      install_dir: install_module_dir,
    )
  endif
endif

baseod3_manifest_conf = configuration_data()
baseod3_manifest_conf.set('OPEND3_VERSION_BASE', opend3_version_base)
baseod3_manifest = configure_file(
  input: 'mod.json.in',
  output: 'mod.json',
  configuration: baseod3_manifest_conf,
)

install_data(
  baseod3_manifest,
  install_dir: install_game_dir,
)

custom_target(
  'opend3_stage_mod_manifest_direct_run',
  input: baseod3_manifest,
  output: 'stage-mod-manifest.stamp',
  command: [
    py,
    meson.project_source_root() / 'tools' / 'build' / 'stage_direct_run_game_module.py',
    '--source',
    '@INPUT@',
    '--destination',
    meson.project_build_root() / 'baseod3' / 'mod.json',
    '--stamp',
    '@OUTPUT@',
  ],
  depend_files: files('../../tools/build/stage_direct_run_game_module.py'),
  build_always_stale: true,
  build_by_default: true,
)
