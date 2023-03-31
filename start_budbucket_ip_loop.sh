EXECUTEPATH=$(pwd)
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [[ $EXECUTEPATH -ef $SCRIPTPATH ]]
then
	CHANGEDDIRS=false
else
	echo Moving to $SCRIPTPATH
	cd $SCRIPTPATH
	CHANGEDDIRS=true
fi

docker stop ip-loop
docker rm ip-loop
docker build -f /home/pi/DeepCultureMonitor/ip-build/Dockerfile . -t ip-loop
docker run -d -v /home/pi/DeepCultureMonitor/data/:/data/ --restart=unless-stopped --name ip-loop ip-loop

if [[ "$CHANGEDDIRS" = true ]]
then
	echo -e "\nMoving back to ${EXECUTEPATH}"
	cd $EXECUTEPATH
fi