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

docker stop devices
docker rm devices
docker build -f /home/pi/DeepCultureMonitor/build/Dockerfile . -t devices
docker run -d -v /home/pi/DeepCultureMonitor/data/:/data/ --privileged --restart=unless-stopped --name devices devices

if [[ "$CHANGEDDIRS" = true ]]
then
	echo -e "\nMoving back to ${EXECUTEPATH}"
	cd $EXECUTEPATH
fi