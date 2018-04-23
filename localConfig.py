# encoding: utf-8
import json

class LocalFile:
    """
    file_name 文件名
    """
    dump = None  # type: str

    def __init__(self, file_name, is_json=False):
        self.file_name = file_name
        self.dump = None
        self.total_string = None
        self.is_json = is_json

    def load_from_file(self):
        try:
            file = open(self.file_name)
            file_text = file.read()
            if self.is_json:
                self.dump = json.loads(file_text)
            else:
                self.dump = file_text
            file.close()
        except Exception, e:
            self.dump = None

    def write_to_file(self):
        if self.is_json:
            if not isinstance(self.total_string, str):
                self.total_string = json.dumps(self.total_string, indent=4)
        with open(self.file_name, 'w') as f:
            f.write(self.total_string)


class BaseConfig:
    configuration = None  # type: str
    build_targets = None  # type: list
    workspace_path = None  # type: str
    schemes = None  # type: list
    local_text = None  # type: str
    def __init__(self,ini_Path):
        self.workspace_name = None
        self.local_text = None
        self.workspace_path = None
        self.schemes = None
        self.build_targets = None
        self.configuration = None
        self.final_archive_path = None
        self.ini_Path = ini_Path
        local = LocalFile(ini_Path)
        local.load_from_file()
        if local.dump is None:
            print "setting.ini doesn't exist.Creat an default one.You need to restart again"
            self.creat_config()
            exit(2)
        self.load_local_bin()
        print self.build_targets

    def load_local_bin(self):
        # type: () -> void
        local = LocalFile(self.ini_Path)
        local.load_from_file()
        ignore_prefix_array = ['#']
        array = local.dump.split('\n')
        for sentense in array:
            if len(sentense) == 0:
                continue
            if sentense[0] in ignore_prefix_array:
                continue
            result_array = sentense.split('=')
            if len(result_array) <= 1:
                continue
            key = result_array[0].replace(' ', '')
            value = result_array[-1].replace(' ', '')
            try:
                setattr(self, key, json.loads(value))
            except Exception,e:
                setattr(self, key, value)

    def save_to_file(self):
        local = LocalFile(self.ini_Path, False)
        local.total_string = self.local_text
        local.write_to_file()

    def creat_config(self):
        self.local_text = """#构建目录所在绝对路径 例如 workspace_path = /example/
workspace_path =
#构建项目工程名所在绝对路径 例如 workspace_name = Example.xcodeproj
workspace_name =
#需要构建的全部scheme 例如 schemes = ['example']
schemes =
#需要构建的全部型号
#包括iOS|iOSSimulator|macOS|tvOS|tvOSSimulator|watchOS|watchOSSimulator
#例如 build_targets = ['iOS','iOSSimulator']
build_targets =
#请输入最终完成构建的类型
#包括Release|Debug 以及其他自定构建类型
#例如 configuration = Release
configuration = 
#最终生成的包的绝对路径 
final_archive_path = """
        self.save_to_file()
