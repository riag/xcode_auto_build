# coding:utf-8

import sys
import os
import subprocess
from string import Template

APP_CONFIG_NAME = 'build.ios.conf'
SUPPORT_FIELD_DICT = {
		'PROJECT_NAME' : None,
		'LIBRARY_NAME' : None,
                'APP_NAME': None,
		'TARGET_NAME' : None,
		'SDK_LIST' : [ 'iphoneos7.1', 'iphonesimulator7.1' ],
		'RELEASE_SDK_LIST' : [ 'iphoneos7.1' ],
		'CONFIGURATION_LIST' : [ 'Debug', 'Release' ],
		'BUILD_DIR' : '${PROJECT_DIR}/build',
		'DIST_DIR' : '${PROJECT_DIR}/dist',
		'COPY_FILES_LIST' : [],
		'DEPEND_ON_DICT': {},
		'SDK_VERSION': None,
		}
	
RELEASE_CONFIGUATION = 'Release'

class ExecCommandError(Exception):
	def __init__(self, code, cmd):
		self.code = code
		self.cmd = cmd

		super(ExecCommandError, self).__init__()

class DependOnPorjectFailed(Exception):
	def __init__(self, name):
		self.name = name
		super(DependOnPorjectFailed, self).__init__()

def makedirs(path):
	if os.path.exists(path) and os.path.isdir(path):
		return
	os.makedirs(path)

def command(cmd, succes_code_list=(0,), shell=True):
	m = ' '.join(cmd)

	code = subprocess.call(m, shell=shell) 
	print >>sys.stdout, 'exec command: %s' % m
	if code not in succes_code_list:
		raise ExecCommandError(code, cmd)

def command_result(cmd, shell=True):
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=shell)
	output = proc.stdout.read()
	return output


def _build(sdk, configuration, variable_list, target=None):
	args = ['-sdk', sdk]

	args.extend(['-configuration', configuration])
	if target:
		args.extend(['-target', target])

	arch="arm7 arm7s"
	args.extend(['ARCH="%s"' % arch,])
	args.extend(['ONLY_ACTIVE_ARCH=No',])
	args.extend(variable_list)

	cmd = ['xcodebuild']
	cmd.extend(args)
	return command(cmd)

def pre_build(project_dir, conf_vars, build_result):
	build_dir = conf_vars['BUILD_DIR']
	dist_dir = conf_vars['DIST_DIR']

	def clean_or_mkdir(path):
		if os.path.exists(path) and os.path.isdir(path):
			command(['rm', '-f', '-r', path])
		os.makedirs(path)

	clean_or_mkdir(build_dir)
	clean_or_mkdir(dist_dir)

	if build_result is None: return

	tmp_vars = {
			'PROJECT_DIR': project_dir,
		}
	tmp_vars.update(conf_vars)

	# 把依赖的工程文件复制到指定的目录
	depend_on_porjects = conf_vars['DEPEND_ON_DICT']
	for name, dest_path in depend_on_porjects.items():
		src = build_result.get(name, None)
		dest = Template(dest_path).safe_substitute(tmp_vars)

		if src is None:
			raise DependOnPorjectFailed(name)

		src = os.path.join(src, '*')
		_real_copy(src, dest, shell=True)

def _get_sdk_current_version():
	result = command_result("xcrun -sdk iphoneos --show-sdk-version")
        if result is None: return ""
        return result.rstrip();

def build(project_dir, variable_list, conf_vars):
	sdk_list = conf_vars['SDK_LIST']
	release_sdk_list = conf_vars['RELEASE_SDK_LIST']
	configuration_list = conf_vars['CONFIGURATION_LIST']
	target = conf_vars['TARGET_NAME']
        APP_NAME = conf_vars['APP_NAME']
	build_dir = conf_vars['BUILD_DIR']
	dist_dir = conf_vars['DIST_DIR']
	sdk_version = conf_vars['SDK_VERSION']

	current_sdk_version = _get_sdk_current_version()
	if sdk_version is None:
		sdk_version = current_sdk_version

	for configuration in configuration_list:

		k = sdk_list
		if configuration == RELEASE_CONFIGUATION:
			k = release_sdk_list

		for sdk in k:
			# 如果sdk不带版本号的话，就加上版本号
			if sdk in ('iphoneos', 'iphonesimulator'):
				sdk = '%s%s' % (sdk, sdk_version)

			_build(sdk, configuration, variable_list, target)
                        if not APP_NAME: continue

                        # 复制app到dist目录下
                        m = _get_reald_build_folder_name(configuration, sdk)
                        app_path = os.path.join(build_dir, m, APP_NAME)
                        real_dist_path = os.path.join(dist_dir, m)
                        makedirs(real_dist_path)
                        _real_copy(app_path, real_dist_path)


def _merge_one_library(lib_name, path_list, out_path):
	t_list = [ os.path.join(k, lib_name)  for k in path_list ]
	cmd = ['lipo', '-create']
	cmd.extend(t_list)
	cmd.append('-output')
	cmd.append(os.path.join(out_path, lib_name))

	return command(cmd)

def _get_reald_build_folder_name(configuration, sdk):
        name = ''
        for t in ['iphoneos', 'iphonesimulator']:
                if sdk.startswith(t):
                        name ='%s-%s' %(configuration, t)
                        break
        return name


def _merge_configuration_library(
		build_dir, dist_dir, lib_name, 
		configuration, sdk_list
		):
	lib_list = []
	for sdk in sdk_list:
                name = _get_reald_build_folder_name(configuration, sdk)
		path = os.path.join(build_dir, name)
		lib_list.append(path)

	out_dir = os.path.join(dist_dir, configuration, 'lib')

	makedirs(out_dir)
	_merge_one_library(lib_name, lib_list, out_dir)

def merge_library(project_dir, conf_vars):
	sdk_list = conf_vars['SDK_LIST']
	release_sdk_list = conf_vars['RELEASE_SDK_LIST']
	configuration_list = conf_vars['CONFIGURATION_LIST']
	build_dir = conf_vars['BUILD_DIR']
	dist_dir = conf_vars['DIST_DIR']
	lib_name = conf_vars['LIBRARY_NAME']

	assert lib_name
	
	for configuration in configuration_list:
		k = sdk_list
		if configuration == RELEASE_CONFIGUATION:
			k = release_sdk_list

		_merge_configuration_library(
				build_dir, dist_dir, lib_name,
				configuration, k
				)

def _real_copy(src, dest, shell=True):
	if dest.endswith('/'): makedirs(dest)

	return command(['cp', '-rf', src, dest], shell=shell)


def copy_files(project_dir, conf_vars):
	copy_files_list = conf_vars['COPY_FILES_LIST']
	configuration_list = conf_vars['CONFIGURATION_LIST']

	tmp_vars = {
			'PROJECT_DIR': project_dir,
		}
	tmp_vars.update(conf_vars)
	dist_path = conf_vars['DIST_DIR']
	for configuration in configuration_list:
		tmp_vars['CONFIGURATION'] = configuration
		#dest_path = os.path.join(dist_path, configuration)
		for k in copy_files_list:
			src, dest = k
			src = Template(src).safe_substitute(tmp_vars)
			dest = Template(dest).safe_substitute(tmp_vars)

			#复制文件
			_real_copy(src, dest)
		
def post_build(project_dir, conf_vars):
	
	lib_name = conf_vars['LIBRARY_NAME']
	if not lib_name: return

        merge_library(project_dir, conf_vars)
	copy_files(project_dir, conf_vars)


def prepare_conf(module, tmp_vars):

	conf_vars = {}
	for k,default in SUPPORT_FIELD_DICT.items():
		v = getattr(module, k, default)

		if isinstance(v, basestring):
			v = Template(v).safe_substitute(tmp_vars)

		conf_vars[k] = v

	return conf_vars

def build_project(project_dir, variable_list, build_result):
	os.chdir(project_dir)
	print >>sys.stdout, 'build project %s' % project_dir

	import imp
	module = imp.load_source(APP_CONFIG_NAME, os.path.join(project_dir, APP_CONFIG_NAME))

	tmp_vars = {
			'PROJECT_DIR': project_dir, 
		}
	conf_vars = prepare_conf(module, tmp_vars)

	pre_build(project_dir, conf_vars, build_result)

	build(project_dir, variable_list, conf_vars)

	post_build(project_dir, conf_vars)

	return conf_vars

def build_multiple_projects(project_dir_list, variable_list):
	build_result = {}

	for project_dir in project_dir_list:
		conf_vars = build_project(project_dir, variable_list, build_result)

		project_name = conf_vars['PROJECT_NAME']
		dist_dir = conf_vars['DIST_DIR']

		build_result[project_name] = dist_dir 

def _real_main(options):
	workdir = os.path.abspath(options.workdir)
	project_list = options.project_list

	if not project_list:
		build_project(workdir, options.variable_list, None)
	else:
		t = [ os.path.join(workdir, k) for k in project_list ]
		build_multiple_projects(t, options.variable_list)

if __name__ == '__main__':
	import argparse

	parse = argparse.ArgumentParser()
	parse.add_argument('--workdir',) 
	parse.add_argument('--project', dest='project_list', action='append')
	parse.add_argument('-D', dest='variable_list', action='append')

	args = parse.parse_args()
	if (not args.workdir and not args.project_list):
		parse.print_help()

	_real_main(args)
