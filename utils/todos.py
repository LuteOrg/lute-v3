import os
import glob
import re
import subprocess

class Todout:
    def __init__(self):
        self.verbose = False

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, v):
        self._verbose = v

    def debug_print(self, msg):
        if self.verbose:
            print(msg)

    def find_files(self, directory, exclude_dirs=None, exclude_files=None, maxdepth=10):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise Exception(f"Missing directory: {directory}")

        self.debug_print(f"Searching {directory} excluding dirs {exclude_dirs} and files {exclude_files}")

        if exclude_dirs is None:
            exclude_dirs = []
        if exclude_files is None:
            exclude_files = []

        exclude_files = [e if (e.startswith("./") or e.startswith('/')) else f"./{e}" for e in exclude_files]
        files = []

        os.chdir(directory)
        self.debug_print(f"Searching {os.getcwd()}")
        self.debug_print(f"excluding dirs {exclude_dirs}")

        find_command = f'find . -type f -maxdepth {maxdepth} -print0 | xargs -0 grep -li todo 2>/dev/null'
        result = subprocess.run(find_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        files = result.stdout.split("\n")
        # self.debug_print('initial files:')
        # self.debug_print(files)

        files = [f for f in files if not any(f.startswith(e) or f.startswith(f"{e}/") for e in exclude_dirs)]

        files = [f for f in files if f not in exclude_files]

        if self.verbose:
            print("Found files:\n" + "\n".join(files))

        return files

    def grepfiles(self, rootdir, files):
        results = []
        for f in files:
            fullname = os.path.abspath(os.path.join(rootdir, f))
            command = f'grep -i todo {fullname}'
            self.debug_print(command)
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            result_lines = result.stdout.split("\n")
            self.debug_print(result_lines)
            result_lines = [r for r in result_lines if not r.startswith('Binary file')]
            results.extend([(f, r.strip()) for r in result_lines if r.strip() != ''])
        return results

    def get_grouping(self, line):
        tmp = line.strip()
        tmp = re.sub('^.*todo', '', tmp)
        if tmp.startswith(":"):
            return ""
        if ":" not in tmp:
            return ""
        return tmp.split(":", 1)[0].strip()

    def get_todo_data(self, directory, exclude_dirs=None, exclude_files=None, maxdepth=10):
        files = self.find_files(directory, exclude_dirs, exclude_files, maxdepth)
        ret = []
        for file in files:
            results = self.grepfiles(directory, [file])
            for file, line in results:
                ret.append({'file': file, 'line': line, 'group': self.get_grouping(line.lower())})
        return ret



def write_report(data):
    data = [ r for r in data if r['file'] != '' ]
    # print(data)
    groups = sorted(set(d['group'] for d in data))
    
    for g in groups:
        curr_group_data = [d for d in data if d['group'] == g]
        
        heading = g if g != "" else "<None>"
        print("\nGroup: " + heading)
        for d in curr_group_data:
            print(f"  {d['file'].ljust(50)}:  {d['line']}")

t = Todout()
t.verbose = False
current_script_path = os.path.abspath(__file__)
rootdir = os.path.join(os.path.dirname(current_script_path), '..')
rootdir = os.path.abspath(rootdir)
venvdir = os.path.join(rootdir, '.venv')
htmlcovdir = os.path.join(rootdir, 'htmlcov')
lutedir = os.path.join(rootdir, 'lute')
testdir = os.path.join(rootdir, 'tests')

d = t.get_todo_data(rootdir, [venvdir, lutedir, testdir, './htmlcov', './.git', './.venv'], [ './utils/todos.py', './.pylintrc', './tasks.py' ], 99)
write_report(d)
