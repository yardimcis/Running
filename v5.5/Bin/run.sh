#/bin/bash

#old PCB version list
InsmodCardVersion=("3.0.1" "3.0.2" "3.1.1" "3.1.2")
Dm6446CardVersion=("1.0.0" "1.0.1" "2.0.1" "2.0.2" "3.0.1" "3.0.2" "3.1.1" "3.1.2" "7.0.2")
RaspberryVersion=("4.0.2" "4.1.2" "4.2.2" "4.3.2" "4.4.2" "4.5.2" "4.6.2" "8.0.2" "8.1.2" "8.2.2" "8.3.2" "8.4.2" "8.5.2" "8.6.2" "9.0.2" "9.2.2" "9.3.2" "9.4.2" "9.5.2" "9.6.2" "10.0.2" "10.2.2")
Raspberry3DVersion=("4.0.2" "4.1.2" "4.2.2" "4.3.2" "4.4.2" "4.5.2" "4.6.2" "10.0.2" "10.2.2")
log_file_name="../Logs/Engine/Output.log"
environment_file_name="../Settings/Environment.xml"

#get run directory
DIR="$( cd -P "$( dirname "$0" )" && pwd )"

#check array
function ContainsElement
{
	local e
	for e in "${@:2}"; do [[ "$e" == "$1" ]] && return 0; done
	return 1
}

#check hardware version and write in to variable PCBversion
function GetHardwareVersion
{
	while read line
	do
		echo $line | grep -q HardwareVersion
		if [ $? == 0 ]; then
			PCBversion=`echo $line  | cut -d'>' -f2 | cut -d'<' -f1`
		fi
	done < "$1"
}

#check file size of Output.log
function CheckOutputFileSize
{
	FILESIZE=$(stat -c%s "$log_file_name")
	
	if [[ "$FILESIZE" -ge 2000000 ]]; then
		> "${log_file_name}"
		echo "Size of $log_file_name = $FILESIZE bytes. Deleted..."; >> ${log_file_name}
	fi
}
	
# go to DIR
cd $DIR

#check folder exists
function DirectoryExists
{
	if [[ ! -d "$1" ]]; then
		echo "Directory $1 does not exist, exitting..."; >> ${log_file_name}
		exit -1
	fi
}

#check file exists
function FileExists
{
	if [[ ! -f "$1" ]]; then
		echo "File $1 does not exist, exitting..."; >> ${log_file_name}
		exit -1
	fi
}

#check symbolic lib exists, if not create it
function CreateSymbolicLink
{
	if [[ -h  "$1" ]]; then
		target=`readlink "$1"`		
		if [[ "$target" != "$2" ]]; then			
			rm $1
			ln -s $2 $1
		fi
	else
		ln -s $2 $1
	fi
}

# check Release, Settings, Resources, Logs, Resources/html
DirectoryExists "../Bin"
DirectoryExists "../Libs"
DirectoryExists "../Settings"
DirectoryExists "../Logs"
DirectoryExists "../Resources/html"
DirectoryExists "../Resources/html/stream"
DirectoryExists "../Resources/html/java"


CheckOutputFileSize


#read PCB version
GetHardwareVersion $environment_file_name

#start io_modules for dm6446 circular PCB (v2) if the version is adequate
ContainsElement $PCBversion "${InsmodCardVersion[@]}"
IsInsmodeCard=$?
if [[ "$IsInsmodeCard" -eq "0" ]]; then
	old_directory=`pwd`
	echo "inserting ip_test_mode.ko"
	cd "../.."
	insmod io_test_mode.ko
	cd "${old_directory}"
fi

ContainsElement $PCBversion "${Dm6446CardVersion[@]}"
isdm6446Device=$?
# check critic files for dm6446
if [[ "$isdm6446Device" -eq "0" ]]; then
	FileExists "fir_unitserver_evmdm6446.x64P"
	FileExists "Distortion.xml"
	FileExists "Intrinsics.xml"
fi

ContainsElement $PCBversion "${Raspberry3DVersion[@]}"
isRaspberry3DDevice=$?
# check critic files for Raspberry Pi Stereo
if [[ "$isRaspberry3DDevice" -eq "0" ]]; then
	FileExists "StereoCalibration.yml"
fi

FileExists "CommonEngine"
FileExists "StreamingClient.cgi"

# check symbolic link for libraries
cd ../..
CreateSymbolicLink "lib" "Engine/Libs"
cd "Engine/Bin"

# check symbolic link for StreamingClient.cgi
cd ../Resources/html/stream
CreateSymbolicLink "StreamingClient.cgi" "../../../Bin/StreamingClient.cgi"
cd "../../../Bin"

# check symbolic link for logs
cd ../Resources/html
CreateSymbolicLink "Logs" "../../Logs"
cd "../../Bin"

# check symbolic link for logs
cd ../Resources/html
CreateSymbolicLink "Frames" "../../Frames"
cd "../../Bin"

# check symbolic link for settings
cd ../Resources/html
CreateSymbolicLink "Settings" "../../Settings"
cd "../../Bin"

# check symbolic link for temp
cd ../Resources/html
CreateSymbolicLink "temp" "/tmp"
cd "../../Bin"

#check memory modules
if [[ "$IsInsmodeCard" -eq "0" ]]; then
#if [[ ! -c "/dev/dsplink" ]]; then
	old_directory=`pwd`
	cd "../../dvsdk/dm6446/"
	bash "loadmodules.sh"
	cd "${old_directory}"
	if [[ `grep 3G $environment_file_name | tr -d '\t' | sed 's/^\([^<].*\)$/\1/'` == *on* ]]; then		
		echo "3G is ON" >> ${log_file_name}
		if [[ `pgrep pppd | wc -l` -le 0 ]]; then
			cd "../../dvsdk/dm6446/"
			bash "usb_modeswitch.sh"
		fi
	fi
	cd "${old_directory}"
#fi
fi

# kill time sych exe
pkill TimeSync
if [[ $? -ne 0 ]]; then
	echo "Cannot kill time synch exe" >> ${log_file_name}
fi

# kill time sych exe
if [[ `pgrep StreamingClient.cgi | wc -l` -gt 0 ]]; then
	pkill StreamingClient.cgi
	if [[ $? -ne 0 ]]; then
		echo "Cannot kill streaming clients" >> ${log_file_name}
	fi
fi

sleep 2

function startTimeSync {
	sleep 10

	while true; do
		cd /opt/TimeSync/Bin
		ps -ef | grep -F ./TimeSync | grep -v grep
		if [[ $? -ne 0 ]]; then
			./TimeSync
        else
            exit 1
		fi
	done
}
startTimeSync &
cd /opt/Engine/Bin
export LD_LIBRARY_PATH=../Libs
current_date=`date +%Y%m%d_%H%M%S`
echo "${current_date}: Engine starting" >> ${log_file_name}
./CommonEngine >> ${log_file_name} 2>&1
RESULT=$?
current_date=`date +%Y%m%d_%H%M%S`
echo "${current_date}: Engine exitted with: $RESULT" >> ${log_file_name}
