import os

def read_file_contents(filename):
    # Get the contents of a template file
    with open(os.path.join(filename), "r") as f:
        return f.read()
    
def write_file_contents(filename, contents):
    with open(filename, "w", newline='\n') as f:
        contents = contents.replace('\r', '')
        f.write(contents)

def ls(dirname):
    return os.listdir(dirname)