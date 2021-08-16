import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import re
from git import *

directory_string = input("Enter path of the directories you want to edit: ")
#Find and return a list with all the directories that have a jenkinsfile in them
def find_jenkinsfile(path, name = "Jenkinsfile"):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root))
    return result

#Open and edit the jenkinsfiles based on two regular expressions that the user enters
def open_and_edit(path_list):
    old_regex = input("Type the old regular expression you want to replace: ")
    new_regex = input("Type the new regular expression: ")
    commit_message = input("Type the commit message: ")
    for path in path_list:
        try:
            branch_list = ['master']
            for branch in branch_list:
                
                #Initialize the repo and index based on the .git file in the path
                repo = Repo.init(path).git
                index = Repo.init(path).index
                repo.checkout(branch)
                repo.pull()
                j_path = path + "\\Jenkinsfile"
                
                string_found = read_and_write(j_path, old_regex, new_regex)
                            
                #Commit and push only if the string we searched for was found in the Jenkinsfile
                if (string_found & (old_regex != new_regex)):
                    commit_and_push(repo, index, commit_message)
                    if branch == branch_list[-1]: #If the current branch you are editing is the last
                        while (input("The branches available are: \n" + repo.branch() + " \nDo you want to add any additional branches to update? (yes/no): ") == "yes"):
                            new_branch = input("Enter the name of the new branch: ")
                            branch_list.append(new_branch)       
                elif old_regex == new_regex:
                    print("You entered the same expression twice")
                else:
                    print("The expression '" + old_regex + "' was not found in " + j_path)
        except NameError as e:
            print("File not found")
            print(e)
            print("Error on directory: " + path)
        except AttributeError as e:
            print(e)
            print("Error on directory: " + path)

#Read and write the new Jenkinsfile
#Return True if the file was edited and false if not
def read_and_write(j_path, old_regex, new_regex):
    file_edited = False
    with open(j_path, "r") as file: #Read the Jenkinsfile       
        jenkinsfile_text = file.readlines() #Table with the Jenkinsfile lines as content
    with open(j_path, "w") as file: #Open the Jenkinsfile in non binary write mode
        string_found = False
        for line in jenkinsfile_text:
            #Tuple with the new string as first object and the amount of replacements as second
            replacement_tuple = re.subn(old_regex, new_regex, line)
            file.write(replacement_tuple[0])
            if replacement_tuple[1] > 0: #There was a change in the file since at least a line was edited
                file_edited = True
    return file_edited
                        
#Commit and push the changes
def commit_and_push(repo, index, commit_message):
    print("\n----------------------------GIT STATUS----------------------------\n")
    print(repo.status())
    print("\n-----------------------------GIT DIFF-----------------------------\n")
    print(repo.diff())
    repo.add("Jenkinsfile") #Add the file to prepare for commit
    if (input("Type 'commit' to commit the changes and anything else to skip: ") == "commit"):
        index.commit(commit_message)
        remote_branch = repo.remote("-v").split("\n")
        push_repository = re.sub("\t", " ", remote_branch[1])
        if (input("Type 'push' in order to push to " + push_repository + " and anything else to skip: ") == "push"):
            print(repo.push())
    

jenkinsfile_paths = find_jenkinsfile(directory_string)
open_and_edit(jenkinsfile_paths)