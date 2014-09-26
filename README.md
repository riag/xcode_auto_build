# xcode_auto_build
该脚步主要用于编译iOS的app工程以及iOS下的静态库工程，使用了xcodebuild命令行工具来编译, 该脚本实现了以下功能:
 * 自动把模拟器和真机的静态库合并成一个
 * 自动复制工程依赖文件到指定目录


## 使用
### 配置
在项目目录下新建一个文件 auto_build.conf

```
PROJECT_NAME = 'testLib'		# 项目的唯一标识

LIBRARY_NAME = 'libtestLib.a'		# 如果该工程是静态库，需要指定静态库的名字

APP_NAME =  None			# 如果该工程是app，需要指定该app的名字

TARGET_NAME = ''

# 依赖其他工程的文件
# 格式: "其他项目标识": "目标目录"
# 会把其他项目dist_dir目录下文件复制到指定目录
# DEPEND_ON_DICT = { "testLib": '${PROJECT_DIR}/testAPP/ExtLib/testLib/', }
DEPEND_ON_DICT = {}			
				

SDK_LIST = [ 'iphoneos8.0', 'iphonesimulator8.0' ]

RELEASE_SDK_LIST = [ 'iphoneos8.0' ]

CONFIGURATION_LIST = ['Debug', 'Release']

BUILD_DIR = '${PROJECT_DIR}/build'	# xocde IDE里指定的编译目录

# 会自动把合拼后的静态库或app复制到该目录下
DIST_DIR = '${PROJECT_DIR}/dist'	

# 如果编译成功后，需要复制文件
# 格式： 源文件/目录，目标文件/目录
COPY_FILES_LIST = (
	('${PROJECT_DIR}/testLib/testLib.h','${DIST_DIR}/${CONFIGURATION}/include/'),
)

```

### 编译
脚本的用法：

	python xcode_auto_build.py --workdir .  --project testLib --project testAPP

```
	--workdir 项目的上一层目录
	--project 项目目录的名字
```

脚本会按照 --project 定义的项目顺序来编译，所以项目之间有依赖关系，需要手工定义好项目的编译顺序
