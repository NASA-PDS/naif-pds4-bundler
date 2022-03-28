TAG_NAME='naif-pds4-bundler:latest'
mkdir npb
cd npb
git clone https://github-fn.jpl.nasa.gov/NAIF/naif-pds4-bundler.git
sudo docker build . -t $TAG_NAME
