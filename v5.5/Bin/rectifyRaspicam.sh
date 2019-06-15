#/bin/bash



#check file exists
function FileExists
{
	if [[ ! -f "$1" ]]; then
		echo "File $1 does not exist, exitting..."
		exit -1
	fi
}

#get run directory
DIR="/opt/Engine/Bin"
	
# go to DIR
cd $DIR

service CommonEngine stop

FileExists CommonEngine
export LD_LIBRARY_PATH=../Libs
echo "Canli Akisi Ac"
./CommonEngine RaspiCam

