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

docker stop server
docker rm server
docker build -f /home/pi/budbucket/server-build/Dockerfile . -t server
docker run -d -v /home/pi/budbucket/data/:/data/  -p 3141:3141 --restart=unless-stopped --name server server

if [[ "$CHANGEDDIRS" = true ]]
then
	echo -e "\nMoving back to ${EXECUTEPATH}"
	cd $EXECUTEPATH
fi