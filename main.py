import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import re
from git import *

directory_string = input("Enter path of the directories you want to edit: ")
#Find and return a list with all the directories that have a jenkinsfile in them
def find_jenkinsfile(path, name = "Jenkinsfile"):
    result = []
    directory_paths = []
    #List all the directories in the path argument and put them in a list
    for dir in os.listdir(path):
        directory_paths.append(os.path.join(path, dir))
    #Search recursively for every directory in the directory_paths list for the "name" file
    for dir in directory_paths:
        for root, dirs, files in os.walk(dir):
            if name in files:
                result.append(os.path.join(root))
                break #Stop searching in the sub directories when the file is found
    return result

#Open and edit the jenkinsfiles based on two regular expressions that the user enters
def open_and_edit(path_list):
    old_regex = input("Type the old regular expression you want to replace: ")
    new_regex = input("Type the new regular expression: ")
    commit_message = input("Type the commit message: ")
    for path in path_list:
        try:
            #Initialize the repo and index based on the .git file in the path
            repo = Repo.init(path).git
            index = Repo.init(path).index
            j_path = path + "\\Jenkinsfile"
            jenkinsfile_lines = read_file(j_path)
            if regex_found(jenkinsfile_lines, old_regex):
                print("-----------------------------------------------------------------")
                print("The branches available on project " + path + " are: \n" + repo.branch())
                print("-----------------------------------------------------------------")
                initial_branch = input("Type the initial branch you want to update: ")
                
                branch_list = [initial_branch]
                for branch in branch_list:
                    repo.checkout(branch)
                    repo.pull()
                    jenkinsfile_lines = read_file(j_path)
                    write_file(j_path, jenkinsfile_lines, old_regex, new_regex)
                    #Commit and push the changes
                    if (old_regex != new_regex):
                        commit_and_push(repo, index, commit_message)
                        if branch == branch_list[-1]: #If the current branch you are editing is the last
                            while (input("The branches available are: \n" + repo.branch() + " \nDo you want to add any additional branches to update? (yes/no): ") == "yes"):
                                new_branch = input("Enter the name of the new branch: ")
                                branch_list.append(new_branch)       
                    else:
                        print("You entered the same expression twice")
        except FileNotFoundError:
            print(e)
            print("Error on directory: " + path + "\n -----------------------------------------------------------------")
        except NameError as e:
            print("File not found")
            print(e)
            print("Error on directory: " + path + "\n -----------------------------------------------------------------")
        except AttributeError as e:
            print(e)
            print("Error on directory: " + path + "\n -----------------------------------------------------------------")
        except GitCommandError as e:
            print ("Error with git")
            print (e)
            print("Error on directory: " + path + "\n -----------------------------------------------------------------")

#Returns True if the regex is foud in the lines list
def regex_found(lines, old_regex):
    for x in lines:
        if (re.search(old_regex, x) != None):
            return True
    return False

#Read the file in the path and return a list with the lines it contains
def read_file(path):
    with open(path, "r") as file: #Read the Jenkinsfile       
        jenkinsfile_text = file.readlines() #List with the Jenkinsfile lines as content
    return jenkinsfile_text

#Open and write the new Jenkinsfile
def write_file(j_path, jenkinsfile_text, old_regex, new_regex):
    with open(j_path, "w") as file: #Open the Jenkinsfile in non binary write mode
        for line in jenkinsfile_text:
            line_sub = re.sub(old_regex, new_regex, line) #New string after replacing the regex if it exists
            file.write(line_sub)
                        
#Commit and push the changes
def commit_and_push(repo, index, commit_message):
    print("\n-----------------------------GIT DIFF-----------------------------\n")
    print(repo.diff())
    repo.add("Jenkinsfile") #Add the file to prepare for commit
    print("\n----------------------------GIT STATUS----------------------------\n")
    print(repo.status())


    if (input("Type 'commit' to commit the changes and anything else to skip: ") == "commit"):
        index.commit(commit_message)
        remote_branch = repo.remote("-v").split("\n")
        push_repository = re.sub("\t", " ", remote_branch[1])
        if (input("Type 'push' in order to push to " + push_repository + " and anything else to skip: ") == "push"):
            repo.push()
            print("\n-----------------------------GIT DIFF-----------------------------\n")

jenkinsfile_paths = find_jenkinsfile(directory_string)
open_and_edit(jenkinsfile_paths)
