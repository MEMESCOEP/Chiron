### Chiron SETUP SCRIPT ###
# By MEMESCOEP
# Last updated 01-10-2025


## IMPORTS ##
from shell_source import source
from Utils import *
import subprocess
import importlib
import tarfile
import zipfile
import shutil
import time
import pip
import sys
import os


## VARIABLES ##
BaseWorkingDirectory = os.getcwd()
CurrentWorkingDir = os.getcwd()
ConfigFilesDirectory = os.path.join(BaseWorkingDirectory, "ConfigFiles")
BuildDirectory = os.path.join(BaseWorkingDirectory, "BuildFiles")
DistroDirectory = os.path.join(BuildDirectory, "Distro")
ChrootDirectory = os.path.join(DistroDirectory, "chroot")
InstallMissingModules = True
ShellDependencies = ["squashfs-tools", "xorriso", "debootstrap", "jq"]
FilesToDownload = []
InstallCommand = ["sudo", "apt-get", "install", "-y"]
PythonModules = ["requests", "tqdm", "sh"]


## FUNCTIONS ##
def ChDir(Directory):
    CurrentWorkingDir = Directory
    os.chdir(Directory)

# Print a colored message
def CustomPrint(Message, MessageType, PrintNewLine = False):
    if PrintNewLine == True:
        print()

    match MessageType:
        case MsgTypes.INFO:
            print(f"[{ANSI.GREEN}INFO{ANSI.END}] >> {Message}")

        case MsgTypes.WARNING:
            print(f"[{ANSI.YELLOW}WARNING{ANSI.END}] >> {Message}")

        case MsgTypes.ERROR:
            print(f"[{ANSI.RED}{ANSI.BLINK}ERROR{ANSI.END}] >> {Message}")

        case _:
            print(f"[{ANSI.PURPLE}UNKNOWN{ANSI.END}] >> {Message}")

# Import a python module
def ImportModule(ModuleName):
    CustomPrint(f"Importing module \"{ModuleName}\"...", MsgTypes.INFO)
    globals()[ModuleName] = importlib.import_module(ModuleName)

# Install a python module
def InstallModule(ModuleName):
    CustomPrint(f"Installing module \"{ModuleName}\"...", MsgTypes.INFO)

    try:
        if hasattr(pip, 'main'):
            pip.main(['install', ModuleName, "--break-system-packages"])
        else:
            pip._internal.main(['install', ModuleName, "--break-system-packages"])

        ImportModule(ModuleName)

    except Exception as EX:
        CustomPrint(f"Failed to install module \"{ModuleName}\": {EX}", MsgTypes.ERROR)

# Download a file form a URL
def DownloadFile(URL, Filename):
    ServerResponse = requests.get(URL, stream=True)
    TotalSize = int(ServerResponse.headers.get('content-length', 0))
    with open(Filename, 'wb') as DownloadedFile, tqdm.tqdm(
            desc=Filename,
            total=TotalSize,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as PGBar:
        for Data in ServerResponse.iter_content(chunk_size=1024):
            Size = DownloadedFile.write(Data)
            PGBar.update(Size)

# Import & install required python dependencies
def TryImports():
    CustomPrint(f"Importing {len(PythonModules)} module(s)...", MsgTypes.INFO)

    for Module in PythonModules:
        try:
            ImportModule(Module)

        except:
            if InstallMissingModules == True:
                CustomPrint(f"Failed to import module \"{Module}\", it will be installed now.", MsgTypes.WARNING)
                InstallModule(Module)

            else:
                CustomPrint(f"Failed to import module \"{Module}\".", MsgTypes.ERROR)
                exit(-1)

# Parse command line arguments
def ParseArgs():
    for ArgIndex in range(1, len(sys.argv)):
        match sys.argv[ArgIndex]:
            case "--DontInstallMissing":
                CustomPrint("Automatic installation of missing modules will be disabled.", MsgTypes.INFO)
                InstallMissingModules = False

            case _:
                CustomPrint(f"Unknown argument \"{sys.argv[ArgIndex]}\".", MsgTypes.ERROR)
                exit(-1)

## MAIN CODE ##
ParseArgs()
TryImports()

# Delete any previous items
if os.path.exists(BuildDirectory):
    CustomPrint(f"Removing previous directory \"{BuildDirectory}\"...", MsgTypes.INFO)
    shutil.rmtree(BuildDirectory)

for Item in FilesToDownload:
    FileName = Item[1]
    DirName = Item[2]

    if os.path.exists(FileName):
        CustomPrint(f"Removing downloaded file \"{FileName}\"...", MsgTypes.INFO)
        os.remove(FileName)

    if os.path.exists(DirName):
        CustomPrint(f"Removing previous directory \"{DirName}\"...", MsgTypes.INFO)
        shutil.rmtree(DirName)

# Download files
try:
    os.mkdir(BuildDirectory)
    os.mkdir(DistroDirectory)
    os.mkdir(ChrootDirectory)

    # Clone git repositories
    """for Repository in GITRepos:
        GITURL = Repository[0]
        GITPath = Repository[1]
        GITBranch = Repository[2]
        CustomPrint(f"Cloning git repository from \"{GITURL}\" into directory \"{GITPath}\"...", MsgTypes.INFO)
        GitProc = subprocess.Popen(["git", "clone", "-b", GITBranch, GITURL, GITPath])
        GitProc.wait()

        if GitProc.returncode != None and GitProc.returncode != 0:
            raise Exception(f"Git clone failed with exit code {GitProc.returncode}.")

        print()"""

    # Download files that are not in git repositories
    for Item in FilesToDownload:
        FileName = Item[1]
        ExtractPath = Item[2]
        DownloadFilePath = os.path.join(BuildDirectory, FileName)

        CustomPrint(f"Downloading file \"{FileName}\"...", MsgTypes.INFO)
        DownloadFile(Item[0], DownloadFilePath)

        CustomPrint(f"Extracting file \"{FileName}\"...", MsgTypes.INFO, True)

        if DownloadFilePath.endswith(".zip"):
            with zipfile.ZipFile(DownloadFilePath, 'r') as ZipFile:
                ZipFile.extractall(ExtractPath)

        else:
            with tarfile.open(DownloadFilePath) as Tarball:
                Tarball.extractall(ExtractPath)

        # Check if there is a subdirectory to move files out of
        if len(os.listdir(ExtractPath)) == 1:
            SubDir = os.path.join(ExtractPath, os.listdir(ExtractPath)[0])

            if os.path.isdir(SubDir):
                ItemsToMove = os.listdir(SubDir)
                CustomPrint(f"Moving {len(ItemsToMove)} item(s) out of subdirectory...", MsgTypes.INFO)

                for ItemIndex in tqdm.tqdm(range(len(ItemsToMove)), total=len(ItemsToMove), desc="Moving items"):
                    SubItemPath = os.path.join(SubDir, ItemsToMove[ItemIndex])
                    NewItemPath = os.path.join(ExtractPath, ItemsToMove[ItemIndex])

                    if os.path.isfile(SubItemPath):
                        shutil.move(SubItemPath, NewItemPath)

                    elif os.path.isdir(SubItemPath):
                        shutil.move(SubItemPath + "/", NewItemPath + "/", copy_function=shutil.copytree)

                CustomPrint(f"Deleting empty directory \"{SubDir}\"...", MsgTypes.INFO, True)
                shutil.rmtree(SubDir)

        CustomPrint(f"Deleting file \"{DownloadFilePath}\"...", MsgTypes.INFO)
        os.remove(DownloadFilePath)

    # Sync filesystem changes to the disk
    CustomPrint("Syncing filesystem changes to disk...", MsgTypes.INFO)
    SyncProc = subprocess.Popen(['sync'])
    SyncProc.wait()

    if SyncProc.returncode != None and SyncProc.returncode != 0:
        CustomPrint(f"Sync failed with exit code {SyncProc.returncode}.", MsgTypes.ERROR, True)
        exit(SyncProc.returncode)

except Exception as EX:
    CustomPrint(f"Setup failed: {EX}", MsgTypes.ERROR, True)
    exit(-1)

# Install dependencies
CustomPrint(f"Installing {len(ShellDependencies)} dependencies...", MsgTypes.INFO)
InstallCommand.extend(ShellDependencies)
APTProc = subprocess.Popen(InstallCommand)
APTProc.wait()

if APTProc.returncode != None and APTProc.returncode != 0:
    CustomPrint(f"Dependency installation failed with exit code {APTProc.returncode}.", MsgTypes.ERROR, True)
    exit(APTProc.returncode)

CustomPrint("All dependencies installed successfully.", MsgTypes.INFO, True)
CustomPrint("Setup completed successfully.", MsgTypes.INFO)
