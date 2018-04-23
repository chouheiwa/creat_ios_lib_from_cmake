from localConfig import BaseConfig
import os, re, random, string,getopt,sys


# -sdk .+$
class re_python:
    @staticmethod
    def re_find(serch_str, in_str):
        # type: (str, str) -> str
        key = in_str
        p1 = serch_str
        pattern1 = re.compile(p1)
        matcher1 = re.search(pattern1, key)
        if matcher1 is None:
            return matcher1
        return matcher1.group(0)


class base_commnd_class:
    def __init__(self):
        self.work_space_path = BaseConfig.shared_base_config().workspace_path
        self.work_space_name = BaseConfig.shared_base_config().workspace_name
        self.build_schemes = BaseConfig.shared_base_config().schemes
        self.total_need_builds = BaseConfig.shared_base_config().build_targets
        self.build_configuration = BaseConfig.shared_base_config().configuration
        self.final_archive_path = BaseConfig.shared_base_config().final_archive_path


class run_os_command:
    def __init__(self):
        pass

    def run_script_get_result(self, script):
        # type: (str) -> str
        """

        :type script: str
        """
        result = os.popen(script)
        return result.read()

    def generate_shell(self, string):
        print string
        file_name = self.generate_random() + '.sh'
        with open(file_name, 'w+') as f:
            f.write(string)
        os.system("chmod +x {}".format(file_name))
        print "run shell script"
        os.system("./{}".format(file_name))
        os.system("rm -f {}".format(file_name))

    def generate_random(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))


class xbuild_commnd(run_os_command):
    xcode_build_sdk = None  # type: Dict[str, str]

    def __init__(self, base_command):

        self.buildNum = None
        self.jenkinsProjectName = None
        self.xcode_build_sdk = {}
        self.get_all_can_build_sdk()
        self.base_command = base_command

    def build_all(self):
        for result in self.base_command.total_need_builds:
            self.xcode_build(self.base_command.work_space_path + self.base_command.work_space_name,
                             self.base_command.build_schemes, self.base_command.build_configuration,
                             self.xcode_build_sdk.get(result))

    def get_all_can_build_sdk(self):
        shell_string = self.run_script_get_result('xcodebuild -showsdks')
        result_arr = shell_string.split('\n')
        while result_arr.__contains__(''):
            result_arr.remove('')
        for i in range(0, len(result_arr)):
            result_str = result_arr[i]
            if i % 2 == 1:
                self.xcode_build_sdk[result_arr[i - 1].replace(' SDKs:', '').replace(' ', '')] = re_python.re_find(
                    r'-sdk .+$', result_str)

    def xcode_build(self, project_path, schemes, configuration, sdk):
        # type: (string, list, string, string) -> None
        build_type = ''
        if project_path.endswith('xcodeproj'):
            build_type = '-project'
        elif project_path.endswith('xcworkspace'):
            build_type = '-workspace'
        final_str = "xcodebuild {} {} -scheme {} -configuration {} {}".format(build_type, project_path,
                                                                              ' '.join(schemes), configuration, sdk)
        self.generate_shell(final_str)

    def find_a_file(self):
        file_lists = os.listdir(self.base_command.work_space_path)

        if not os.path.exists(self.base_command.final_archive_path + 'arch'):
            os.system("mkdir {}".format(self.base_command.final_archive_path + 'arch'))

        for result_str in file_lists:
            if self.base_command.build_configuration in result_str:
                extra_command = 'macOS'
                if '-' in result_str:
                    extra_command = result_str.split('-')[-1]
                for final_a_file_name in os.listdir(self.base_command.work_space_path + result_str):
                    if '.a' in final_a_file_name:
                        lastest_name = final_a_file_name.replace('.a', '_' + extra_command) + '.a'
                        shell_script = "mv {} {}\n".format(self.base_command.work_space_path + result_str + '/' + final_a_file_name,self.base_command.final_archive_path + lastest_name)
                        shell_script = shell_script + "rm -rf {}".format(self.base_command.work_space_path + result_str)
                        self.generate_shell(shell_script)

    def zip_final(self,final_name):
        shell_script = "cd {}\n".format(self.base_command.final_archive_path)
        shell_script = shell_script + "zip -m {}.zip *.a".format(final_name)
        self.generate_shell(shell_script)


def main(argv):
    try:
        options, args = getopt.getopt(argv, "h", ["buildNum=","jenkinsProjectName="])
    except getopt.GetoptError:
        print "error input"
        sys.exit(2)
    xbuild = xbuild_commnd(base_commnd_class())  # type: xbuild_commnd
    for key,value in options:
        if key in "--buildNum":
            setattr(xbuild,"buildNum",value)
        if key in "--jenkinsProjectName":
            setattr(xbuild,"jenkinsProjectName",value)
    xbuild.build_all()
    xbuild.find_a_file()
    xbuild.zip_final(xbuild.jenkinsProjectName + '_' + xbuild.buildNum)

if __name__ == '__main__':
    main(sys.argv[1:])

