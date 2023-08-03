import os
import subprocess
import win32com.client


# assuming 'text' is already defined
if text.lower().startswith("admin open "):
    filename = text[11:] + '.txt'  # extract filename from the text
    try:
        with open(filename, 'r') as file:
            command = file.read().strip()  # read file content into variable command
        
        # check the extension of the command
        _, extension = os.path.splitext(command)

        # for .url files
        if extension == '.url':
            command_to_run = f'start {command}'

        # for .lnk files
        elif extension == '.lnk':
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(command)
            target_path = shortcut.Targetpath  # get the path that the shortcut points to

            command_to_run = f'"{target_path}"'  # ensure the target path is surrounded by quotes in case it contains spaces

        else:
            command_to_run = command

        process = subprocess.Popen(command_to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        if output:
            print("Output: \n{}\n".format(output.decode("utf-8")))

        if error:
            print("Error: \n{}\n".format(error.decode("utf-8")))

    except FileNotFoundError:
        print("No such file: " + filename)
