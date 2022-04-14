source $HOME/.secrets/passwords.csh
TAG_NAME='naif-pds4-bundler:latest'
git clone https://github.com/NASA-PDS/naif-pds4-bundler.git
git checkout develop
sudo  docker build . -t $TAG_NAME
# Access the VM with
# docker run -it naif-pds4-bundler:latest
