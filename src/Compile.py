### Chiron COMPILATION SCRIPT ###
# By MEMESCOEP
# Last updated 01-10-2025


## IMPORTS ##
from distutils.dir_util import copy_tree
from datetime import datetime
from Utils import *
import continuous_threading
import multiprocessing
import subprocess
import curses
import shutil
import psutil
import time
import grp
import pwd
import os
import io
import traceback


## VARIABLES ##
UbuntuVersionCodename = "noble"
FullBuildLogOutput = io.StringIO()
BuildStartTime = datetime.now()
CWD = os.getcwd()
InstallListFilePath = os.path.join(CWD, "InstallList.txt")
RootOfCurrentPath = os.path.abspath(os.sep)
UbuntuArchiveURL = "http://us.archive.ubuntu.com/ubuntu/"
BuildFilesPath = os.path.join(CWD, "BuildFiles")
RootFSFilesPath = os.path.join(CWD, "RootFSFiles")
ConfigFilesPath = os.path.join(RootFSFilesPath, "ConfigFiles")
ScriptFilesPath = os.path.join(CWD, "Scripts")
DistroPath = os.path.join(BuildFilesPath, "Distro")
ChrootDir = os.path.join(DistroPath, "chroot")
ImagePath = os.path.join(DistroPath, "image")
ImageArch = "amd64" # Can be amd64, i386, arm64, armhf, ppc64el, s390x, mips64el, or riscv64
ISOName = "Chiron.iso"
LogPath = os.path.join(CWD, f"Logs/{BuildStartTime.strftime("%m-%d-%Y_%H-%M-%S")}.txt")
LoadingChars = ['|', '/', '-', '\\']
FoldersToCopy = [[os.path.join(ConfigFilesPath, "xfce4/"), os.path.join(ChrootDir, "home/chiron/.config/xfce4/")],
                 [os.path.join(RootFSFilesPath, "DesktopShortcuts/"), os.path.join(ChrootDir, "home/chiron/Desktop/")]]

FilesToCopy = [[os.path.join(ConfigFilesPath, "HTop.cfg"), os.path.join(ChrootDir, "home/chiron/.config/htop/htoprc")],
               [os.path.join(ConfigFilesPath, "Grub.cfg"), os.path.join(ChrootDir, "image/isolinux/grub.cfg")],
               [os.path.join(ScriptFilesPath, "StartNetworking.sh"), os.path.join(ChrootDir, "Utilities/Autostart/StartNetworking.sh")],
               [os.path.join(ConfigFilesPath, "AutostartNetworking.systemd"), os.path.join(ChrootDir, "etc/systemd/system/AutostartNetworking.service")],
               [os.path.join(RootFSFilesPath, "Fonts/VGA_437.ttf"), os.path.join(ChrootDir, "usr/share/fonts/truetype/VGA_437.ttf")]]
               #[os.path.join(ConfigFilesPath, "Username.cfg"), os.path.join(ChrootDir, "etc/casper.conf")],
               #[os.path.join(ConfigFilesPath, "LSBRelease.txt"), os.path.join(ChrootDir, "etc/lsb-release")],
FlatpakPackages = []
APTINSTPackages = []
APTREMPackages = []
WindowList = []
WGETFiles = []
APTRepos = []
ArgStrs = []
MountedDevices = False
BuildRunning = True
InChroot = False
Clean = False
CompletedBuildSteps = 0
TerminalPercentage = 0.75
DiskRefreshDivisor = 150
StatusPercentage = 0.25
WindowUpdateTime = 0.01
StatsUpdateTime = 0.5
LoadSpinSpeed = 0.1
RefreshCount = 0
AvailableMEM = 0
TotalMemory = psutil.virtual_memory().total >> 20
StatusLine = 0
UsedMemory = 0
DiskUsage = 0
TermLine = 0
ExitCode = 0
CPUUsage = 0
CPUCount = multiprocessing.cpu_count()
JobCount = int(CPUCount * 1.5)
SpinnerThread = None
DiskDetails = None


## FUNCTIONS ##
# Unmount /dev and /run from the chroot
def Unmount(WindowToUpdate, OverrideMountCheck = False, UseConsole = True, ReadOutput = True):
    if MountedDevices == False and OverrideMountCheck == False:
        return

    UmountProc = Execute(["sudo", "umount", os.path.join(ChrootDir, "dev")], WindowToUpdate, ReadOutput)

    if UmountProc != None and UmountProc != 0:
        CustomPrint(f"Umount /dev returned exit code {UmountProc}.", MsgTypes.WARNING, WindowToUpdate, UseConsole)

    UmountProc = Execute(["sudo", "umount", os.path.join(ChrootDir, "run")], WindowToUpdate, ReadOutput)

    if UmountProc != None and UmountProc != 0:
        CustomPrint(f"Umount /run returned exit code {UmountProc}.", MsgTypes.WARNING, WindowToUpdate, UseConsole)

# Print a colored message
def CustomPrint(Message, MessageType, WindowToUpdate, UseConsole = False):
    global StatusLine

    if Message == None or len(Message.strip()) <= 0:
        return

    try:
        if FullBuildLogOutput.closed == False:
            FullBuildLogOutput.write(Message + "\n")

        if UseConsole == False and WindowToUpdate != None:
            WindowHeight, WindowWidth = WindowToUpdate.getmaxyx()
            WindowToUpdate.attroff(curses.color_pair(3))

            if MessageType is not MsgTypes.NOTYPE:
                WindowToUpdate.addstr(StatusLine, 0, "[")

            try:
                if StatusLine > WindowHeight - 1:
                    WindowToUpdate.scrollok(True)
                    WindowToUpdate.scroll()
                    WindowToUpdate.addstr(WindowHeight - 2, 0, Message)

            except Exception as EX:
                FullBuildLogOutput.write(f"[FAILURE ON WINDOW UPDATE] >> MSG = {Message}Err = {traceback.format_exc()}\n")
                #pass  # Handle any exceptions (e.g., window overflow)"""

            match MessageType:
                case MsgTypes.INFO:
                    WindowToUpdate.attron(curses.color_pair(3))
                    WindowToUpdate.addstr(StatusLine, 1, "INFO")
                    WindowToUpdate.attroff(curses.color_pair(3))
                    WindowToUpdate.addstr(StatusLine, 5, f"] >> {Message}")
                    StatusLine += ((len(Message) + 10) // WindowWidth) + 1

                case MsgTypes.WARNING:
                    WindowToUpdate.attron(curses.color_pair(2))
                    WindowToUpdate.addstr(StatusLine, 1, "WARN")
                    WindowToUpdate.attroff(curses.color_pair(2))
                    WindowToUpdate.addstr(StatusLine, 5, f"] >> {Message}")
                    StatusLine += ((len(Message) + 10) // WindowWidth) + 1

                case MsgTypes.ERROR:
                    WindowToUpdate.addstr(StatusLine, 1, "ERROR", curses.color_pair(5) | curses.A_BLINK)
                    WindowToUpdate.addstr(StatusLine, 6, f"] >> {Message}")
                    StatusLine += ((len(Message) + 11) // WindowWidth) + 1

                case MsgTypes.NOTYPE:
                    WindowToUpdate.addstr(StatusLine, 0, Message)
                    StatusLine += (len(Message) // WindowWidth) + 1

                case _:
                    WindowToUpdate.attron(curses.color_pair(1))
                    WindowToUpdate.addstr(StatusLine, 1, "UNKNOWN")
                    WindowToUpdate.attroff(curses.color_pair(1))
                    WindowToUpdate.addstr(StatusLine, 8, f"] >> {Message}")
                    StatusLine += ((len(Message) + 13) // WindowWidth) + 1

        else:
            match MessageType:
                case MsgTypes.INFO:
                    print(f"[{ANSI.GREEN}INFO{ANSI.END}] >> {Message}")

                case MsgTypes.WARNING:
                    print(f"[{ANSI.YELLOW}WARNING{ANSI.END}] >> {Message}")

                case MsgTypes.ERROR:
                    print(f"[{ANSI.RED}{ANSI.BLINK}ERROR{ANSI.END}] >> {Message}")

                case MsgTypes.NOTYPE:
                    print(Message)

                case _:
                    print(f"[{ANSI.PURPLE}UNKNOWN{ANSI.END}] >> {Message}")

    except:
        pass

# Construct a string from a list that can be used as a command line argument with a Bash script
# List items must not contain any quotation marks or slashes
# EX output: --Fruits "apple" "grape"
def CreateARGString(ListName, ListItems):
    if len(ListItems) <= 0:
        return None

    ArgStr = f"--{ListName}"

    for Item in ListItems:
        ArgStr += f" \"{Item}\""

    return ArgStr

# Add a spinning icon to the terminal output window
def AddSpinnerToTerminalWindow(TerminalWindow):
    global BuildRunning

    while BuildRunning == True:
        for Char in LoadingChars:
            if TermLine > 0:
                TerminalWindow.addstr(TermLine - 1, 0, Char)

            else:
                TerminalWindow.addstr(TermLine, 0, Char)

            time.sleep(LoadSpinSpeed)

    if TermLine > 0:
        TerminalWindow.addstr(TermLine - 1, 0, " ")

    else:
        TerminalWindow.addstr(TermLine, 0, " ")

# Execute a command and return its exit code
def Execute(CMD, WindowToUpdate, ReadOutput = True):
    global TermLine, BuildRunning
    MaxHeight = 0
    ProcOut = ""

    process = subprocess.Popen(
        CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    if WindowToUpdate != None:
        MaxHeight, _ = WindowToUpdate.getmaxyx()

    while BuildRunning == True:
        # Check if the process is still running and if it has output. Otherwise, exit
        if process.poll() is not None and not ProcOut:
            break

        if ReadOutput == True:
            ProcOut = process.stdout.readline()

            # If the process printed an empty line, skip printing anything
            if len(ProcOut.strip()) <= 0:
                continue

            # If there's output in stdout, display it in the provided window
            if ProcOut:
                try:
                    FullBuildLogOutput.write(ProcOut)
                    
                    if TermLine > MaxHeight - 1:
                        WindowToUpdate.scroll()
                        WindowToUpdate.addstr(MaxHeight - 2, 0, ProcOut)

                    else:
                        WindowToUpdate.addstr(TermLine, 0, ProcOut)
                        TermLine += 1

                except Exception as e:
                    pass # Used to keep the program from crashing if text is placves out of bounds (TO BE REPLACED)

        curses.napms(5)  # Delay to allow curses to update the screen and process input

    return process.returncode


def RefreshWindows(OverrideBuildRunning = False, Threaded = True):
    global BuildRunning

    while BuildRunning == True or OverrideBuildRunning == True:
        for Window in WindowList:
            if Threaded == True:
                Window.noutrefresh()

            else:
                Window.refresh()

        if Threaded == True:
            curses.doupdate()

        if OverrideBuildRunning == True:
            break

        time.sleep(WindowUpdateTime)

def RefreshSystemStats():
    global RefreshCount, DiskUsage, BuildRunning, InChroot

    while BuildRunning == True:
        AvailableMEM = psutil.virtual_memory().available >> 20
        UsedMemory = TotalMemory - AvailableMEM
        CPUUsage = psutil.cpu_percent()

        if RefreshCount % DiskRefreshDivisor == 0:
            DiskDetails = psutil.disk_usage(RootOfCurrentPath)
            DiskUsage = (DiskDetails.used / DiskDetails.total) * 100

        BuildDuration = str(datetime.now() - BuildStartTime)
        WindowList[1].erase()
        WindowList[1].addstr(0, 0, f"Build duration: {BuildDuration[:BuildDuration.index('.') + 3]}s")
        WindowList[1].addstr(1, 0, f"CPU usage: {CPUUsage}%")
        WindowList[1].addstr(2, 0, f"MEM usage: {UsedMemory}MB / {TotalMemory}MB ({AvailableMEM}MB available, {psutil.virtual_memory().percent}% used) ")
        WindowList[1].addstr(3, 0, f"Disk usage of \"{RootOfCurrentPath}\": {round(DiskUsage, 2)}% ({(DiskDetails.total - DiskDetails.used) >> 20}MB available, {DiskDetails.used >> 20}MB used, {DiskDetails.total >> 20}MB total)")
        RefreshCount += 1

        time.sleep(StatsUpdateTime)

def CursesWrapper(STDScr):
    global CompletedBuildSteps, ExitCode, SpinnerThread, BuildRunning

    try:
        # Clear screen and set up the environment
        STDScr.clear()
        curses.start_color()
        curses.curs_set(0)
        STDScr.nodelay(1)
        STDScr.scrollok(True)
        STDScr.refresh()

        # Create color schemes
        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)

        # Get screen dimensions (height and width of the terminal)
        height, width = STDScr.getmaxyx()

        # Split the screen into 3 windows
        # Main windows
        TermOutputWindow = curses.newwin(int(height * TerminalPercentage), width, 0, 0)
        ProgramStatusWindow = curses.newwin(int(height * StatusPercentage), width // 2, int(height * TerminalPercentage), 0)
        SystemStatsWindow = curses.newwin(int(height * StatusPercentage), (width // 2) + 1, int(height * TerminalPercentage), width // 2)

        # Subwindows
        TermOutputSubWindow = STDScr.subwin(int(height * TerminalPercentage) - 2, width - 3, 1, 2)
        ProgramStatusSubWindow = STDScr.subwin(int(height * StatusPercentage) - 2, (width // 2) - 4, int(height * TerminalPercentage) + 1, 2)
        SystemStatsSubWindow = STDScr.subwin(int(height * StatusPercentage) - 2, (width // 2) - 3, int(height * TerminalPercentage) + 1, (width // 2) + 2)

        # Set scroll lock to true for subwindows
        TermOutputSubWindow.scrollok(True)

        # Set up topmost windows
        TermOutputWindow.attron(curses.color_pair(1))
        ProgramStatusWindow.attron(curses.color_pair(1))
        SystemStatsWindow.attron(curses.color_pair(1))
        TermOutputWindow.box()
        ProgramStatusWindow.box()
        SystemStatsWindow.box()

        TermOutputWindow.attroff(curses.color_pair(1))
        TermOutputWindow.addstr(0, 5, "< ")
        TermOutputWindow.attron(curses.color_pair(3))
        TermOutputWindow.addstr(0, 7, "BUILD OUTPUT")
        TermOutputWindow.attroff(curses.color_pair(1))
        TermOutputWindow.addstr(0, 19, " >")

        ProgramStatusWindow.attroff(curses.color_pair(1))
        ProgramStatusWindow.addstr(0, 5, "< ")
        ProgramStatusWindow.attron(curses.color_pair(3))
        ProgramStatusWindow.addstr(0, 7, "STATUS")
        ProgramStatusWindow.attroff(curses.color_pair(1))
        ProgramStatusWindow.addstr(0, 13, " >")

        SystemStatsWindow.attroff(curses.color_pair(1))
        SystemStatsWindow.addstr(0, 5, "< ")
        SystemStatsWindow.attron(curses.color_pair(3))
        SystemStatsWindow.addstr(0, 7, "SYSTEM RESOURCES")
        SystemStatsWindow.attroff(curses.color_pair(1))
        SystemStatsWindow.addstr(0, 23, " >")

        # Set all subwindow color schemes
        TermOutputSubWindow.attron(curses.color_pair(4))
        ProgramStatusSubWindow.attron(curses.color_pair(4))
        SystemStatsSubWindow.attron(curses.color_pair(4))

        # Update topmost windows
        TermOutputWindow.refresh()
        ProgramStatusWindow.refresh()
        SystemStatsWindow.refresh()

        # Start refresh threads
        WindowList.extend([TermOutputSubWindow, SystemStatsSubWindow, ProgramStatusSubWindow])
        continuous_threading.ContinuousThread(target=RefreshWindows, name="Window update thread").start()
        continuous_threading.ContinuousThread(target=RefreshSystemStats, name="System statistics update thread").start()
        continuous_threading.ContinuousThread(target=AddSpinnerToTerminalWindow, name="Loading spinner thread", args=(TermOutputSubWindow, )).start()

        try:
            # Unmount /dev and /run from the chroot BEFORE we delete the folder. If we don't, that kinda causes severe issues
            CustomPrint("Unmounting /dev & /run to prevent potential filesystem issues...", MsgTypes.INFO, ProgramStatusSubWindow)
            Unmount(ProgramStatusSubWindow, True, False, False)
            #time.sleep(2)

            # Set up the build structure & clean the chroot dir if it exists so each build will be as clean as possible
            CustomPrint("Setting up build structure...", MsgTypes.INFO, ProgramStatusSubWindow)

            if os.path.exists(ChrootDir):
                shutil.rmtree(ChrootDir)
                os.mkdir(ChrootDir)

            CompletedBuildSteps += 1

            # Switch to the distro directory, compile the kernel & packages, and make an ISO image
            CustomPrint(f"Switching to distro path (\"{DistroPath}\")...", MsgTypes.INFO, ProgramStatusSubWindow)
            os.chdir(DistroPath)

            CustomPrint(f"Generating OS image for \"{ImageArch}\" with DebootStrap (using Ubuntu release \"{UbuntuVersionCodename}\")...", MsgTypes.INFO, ProgramStatusSubWindow)
            DebootStrapProc = Execute(["sudo", "debootstrap", f"--arch={ImageArch}", "--variant=minbase", UbuntuVersionCodename, ChrootDir, UbuntuArchiveURL], TermOutputSubWindow)

            if DebootStrapProc != None and DebootStrapProc != 0:
                raise Exception(f"DebootStrap returned exit code {DebootStrapProc}.")

            MountedDevices = True
            CompletedBuildSteps += 1

            # Copy folders to the chroot
            CustomPrint(f"Copying {len(FoldersToCopy)} folder(s) to the chroot...", MsgTypes.INFO, ProgramStatusSubWindow)

            for FolderIndex in range(len(FoldersToCopy)):
                DirName = os.path.dirname(FoldersToCopy[FolderIndex][1])

                if os.path.exists(DirName) == False:
                    os.makedirs(DirName)

                copy_tree(FoldersToCopy[FolderIndex][0], FoldersToCopy[FolderIndex][1])
                os.chown(FoldersToCopy[FolderIndex][1], pwd.getpwnam("nobody").pw_uid, grp.getgrnam("nogroup").gr_gid)

            CompletedBuildSteps += 1

            # Copy files to the chroot
            CustomPrint(f"Copying {len(FilesToCopy)} file(s) to the chroot...", MsgTypes.INFO, ProgramStatusSubWindow)

            for FileIndex in range(len(FilesToCopy)):
                DirName = os.path.dirname(FilesToCopy[FileIndex][1])

                if os.path.exists(DirName) == False:
                    os.makedirs(DirName)

                shutil.copy(FilesToCopy[FileIndex][0], FilesToCopy[FileIndex][1])
                os.chown(FilesToCopy[FileIndex][1], pwd.getpwnam("nobody").pw_uid, grp.getgrnam("nogroup").gr_gid)

            CompletedBuildSteps += 1

            # Define the chroot and perform the necessary operations inside of it
            CustomPrint(f"Defining chroot at \"{ChrootDir}\" and running chroot operations...", MsgTypes.INFO, ProgramStatusSubWindow)
            os.chdir(CWD)

            BashCMD = ["bash", "ChrootOperations.sh", ChrootDir]

            for ArgIndex in range(0, len(APTRepos) - 1):
                if APTRepos[ArgIndex] == None:
                    continue

                BashCMD.extend(APTRepos[ArgIndex].split(" "))

            for ArgIndex in range(0, len(ArgStrs)):
                if ArgStrs[ArgIndex] == None:
                    continue

                BashCMD.extend(ArgStrs[ArgIndex].split(" "))
            
            ChrootProc = Execute(BashCMD, TermOutputSubWindow)

            if ChrootProc != None and ChrootProc != 0:
                exit(0)
                raise Exception(f"Chroot operations returned exit code {ChrootProc}.")

            # Unmount /dev and /run from the chroot, because if we don't there will probably be major issues
            CustomPrint("Unmounting /dev and /run...", MsgTypes.INFO, ProgramStatusSubWindow)
            Unmount(ProgramStatusSubWindow, True, False)
            #time.sleep(2)
            CompletedBuildSteps += 1

            # Copy the generated image directory to a new one that's more easily accessible
            CustomPrint(f"Copying old image directory \"{os.path.join(ChrootDir, "image")}\" to new image directory \"{os.path.join(DistroPath, "image")}\"...", MsgTypes.INFO, ProgramStatusSubWindow)
            copy_tree(os.path.join(ChrootDir, "image"), os.path.join(DistroPath, "image"))
            CompletedBuildSteps += 1

            # Create a SquashFS filesystem image
            CustomPrint("Creating SquashFS...", MsgTypes.INFO, ProgramStatusSubWindow)
            SquashFSProc = Execute(["sudo", "mksquashfs", ChrootDir, os.path.join(DistroPath, "image/casper/filesystem.squashfs"), "-noappend", "-no-duplicates", "-no-recovery", "-wildcards", "-comp", "xz", "-b", "1M", "-Xdict-size", "100%", "-e", "\"var/cache/apt/archives/*\"", "-e", "\"root/*\"", "-e", "\"root/.*\"", "-e", "\"tmp/*\"", "-e", "\"tmp/.*\"", "-e", "\"swapfile\""], TermOutputSubWindow)

            if SquashFSProc != None and SquashFSProc != 0:
                raise Exception(f"SquashFS returned exit code {SquashFSProc}.")

            # Print the chroot filesystem size
            #CustomPrint("Printing filesystem size...", MsgTypes.INFO, ProgramStatusSubWindow)
            #os.system(f"printf $(sudo du -sx --block-size=1 {ChrootDir} | cut -f1) | sudo tee {os.path.join(DistroPath, "image/casper/filesystem.size")}")
            #CompletedBuildSteps += 1

            # Create an ISO image from the distro directory
            CustomPrint(f"Creating ISO image \"{os.path.join(CWD, ISOName)}\"...", MsgTypes.INFO, ProgramStatusSubWindow)

            XorrisoProc = Execute(["bash", "RunXorriso.sh", CWD, ISOName], TermOutputSubWindow)

            if XorrisoProc != None and XorrisoProc != 0:
                raise Exception(f"Xorriso returned exit code {XorrisoProc}.")

            CompletedBuildSteps += 1
            BuildDuration = str(datetime.now() - BuildStartTime)
            CustomPrint(f"Build completed successfully ({CompletedBuildSteps} steps, took {BuildDuration[:BuildDuration.index('.') + 3]}s).", MsgTypes.INFO, ProgramStatusSubWindow)

            TermOutputSubWindow.attron(curses.color_pair(3))
            TermOutputSubWindow.addstr(TermLine - 1, 0, "BUILD FINISHED!", curses.color_pair(3) | curses.A_BLINK)
            TermOutputSubWindow.attroff(curses.color_pair(3))

        except Exception as EX:
            try:
                ExitCode = -2 - CompletedBuildSteps
                BuildDuration = str(datetime.now() - BuildStartTime)
                CustomPrint(f"Build failed: {EX} (failed after {CompletedBuildSteps} steps and {BuildDuration[:BuildDuration.index('.') + 3]}s)", MsgTypes.ERROR, ProgramStatusSubWindow)

                TermOutputSubWindow.attron(curses.color_pair(5))
                TermOutputSubWindow.addstr(TermLine - 1, 0, "BUILD FAILED!", curses.color_pair(5) | curses.A_BLINK)
                TermOutputSubWindow.attroff(curses.color_pair(5))

            except Exception as EX:
                CustomPrint(f"Failed to update status title: {EX}", MsgTypes.ERROR, ProgramStatusSubWindow)

    except KeyboardInterrupt:
        CustomPrint("Compilation aborted by user (Received CTRL-C)", MsgTypes.INFO, ProgramStatusSubWindow)
        ExitCode = 1

    except Exception as EX:
        CustomPrint(f"An error occurred: {EX}", MsgTypes.ERROR, ProgramStatusSubWindow)

    BuildRunning = False

    try:
        CustomPrint("< PRESS ANY KEY TO EXIT >\n", MsgTypes.NOTYPE, ProgramStatusSubWindow)
        #TermOutputWindow.refresh()
        #ProgramStatusWindow.refresh()
        RefreshWindows(True, False)

    except:
        pass

    curses.echo()
    curses.curs_set(1)
    ProgramStatusSubWindow.getch()

## MAIN CODE ##
print("[== CHIRON COMPILATION SCRIPT ==]")
CustomPrint("Checking for superuser...", MsgTypes.INFO, None, True)

if os.geteuid() != 0:
    CustomPrint("This script requires superuser.", MsgTypes.ERROR, None, True)
    exit(-998)

# Parse the install list file and categorize packages & files based on their category
CustomPrint(f"Parsing install list file (\"{InstallListFilePath}\")...", MsgTypes.INFO, None, True)
ListToWrite = None

with open(InstallListFilePath, "r") as InstallListFile:
    for Line in InstallListFile:
        if len(Line.strip()) <= 0:
            continue

        elif ListToWrite != APTREMPackages and Line.strip() == "[CHROOT_APT_REMOVE]":
            ListToWrite = APTREMPackages
            continue

        elif ListToWrite != APTINSTPackages and Line.strip() == "[CHROOT_APT_INSTALL]":
            ListToWrite = APTINSTPackages
            continue

        elif ListToWrite != WGETFiles and Line.strip() == "[CHROOT_WGET]":
            ListToWrite = WGETFiles
            continue

        elif ListToWrite != APTRepos and Line.strip() == "[CHROOT_APT_REPOS]":
            ListToWrite = APTRepos
            continue

        elif ListToWrite != FlatpakPackages and Line.strip() == "[CHROOT_FLATPAK]":
            ListToWrite = FlatpakPackages
            continue

        if ListToWrite == None:
            CustomPrint(f"Skipping unorganized item \"{Line.strip()}\".", MsgTypes.WARNING, None, True)
            continue

        ListToWrite.append(Line.strip())

    InstallListFile.close()

CustomPrint(f"{len(APTRepos)} APT repositories will be added:\n  {'\n  '.join(APTRepos)}\n", MsgTypes.INFO, None, True)
CustomPrint(f"{len(APTINSTPackages)} APT package(s) will be installed:\n  {'\n  '.join(APTINSTPackages)}\n", MsgTypes.INFO, None, True)
CustomPrint(f"{len(APTREMPackages)} APT package(s) will be removed:\n  {'\n  '.join(APTREMPackages)}\n", MsgTypes.INFO, None, True)
CustomPrint(f"{len(WGETFiles)} file(s) will be downloaded (WGET):\n  {'\n  '.join(WGETFiles)}\n", MsgTypes.INFO, None, True)
CustomPrint(f"{len(FlatpakPackages)} flatpak package(s) will be installed:\n  {'\n  '.join(FlatpakPackages)}\n", MsgTypes.INFO, None, True)
ArgStrs = [CreateARGString("APTRepo", APTRepos),
           CreateARGString("APTInst", APTINSTPackages),
           CreateARGString("APTRem", APTREMPackages),
           CreateARGString("WGET", WGETFiles),
           CreateARGString("FlatpakInst", FlatpakPackages)
]

while None in ArgStrs:
    ArgStrs.remove(None)

CustomPrint(f"{len(ArgStrs)} chroot bash arguments generated:\n  {'\n  '.join([str(Arg) if Arg is not None else '' for Arg in ArgStrs])}\n", MsgTypes.INFO, None, True)
CustomPrint("Initializing curses...", MsgTypes.INFO, None, True)
curses.wrapper(CursesWrapper)

CustomPrint("Terminating threads...", MsgTypes.INFO, None, True)
continuous_threading.shutdown(0)

CustomPrint("Unmounting /dev & /run...", MsgTypes.INFO, None, True)
Unmount(None, True, True, False)

CustomPrint(f"Writing log to file \"{LogPath}\"...", MsgTypes.INFO, None, True)

with open(LogPath, "w") as LogOutFile:
    LogOutFile.write(FullBuildLogOutput.getvalue())

FullBuildLogOutput.close()

CustomPrint(f"Exitting with code {ExitCode}...", MsgTypes.INFO, None, True)
exit(ExitCode)