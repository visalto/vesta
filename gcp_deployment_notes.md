create vm
E2 -> 4 cpu x 16mb
attach disk with 100gb
enable logging and monitoring
--<END>--
install docker - official docker documentation steps for debian
ensure git is installed and configure email, username

# ACCESS PERMISSION IS SUPER IMPORTANT TO BE CORRECT

#### all the volumes depend on it

add vesta vm user
add user to docker group sudo usermod -aG docker <username>
switch to user - enable to be able to ssh with the user - generate a new rsa key pair (if you don't have one) - add to the "authorized" list of ssh keys under vm instance details
clone vesta parent repo - initialize each submodule
-(for deployment phase I went and manually set each submodule to the branch I wanted)

setup .env file on the parent repo - !Important linux host UID has to match with container UID. Otherwise platform will experience permission errors and wont be able to start.
create python venv and install requirements from parent vesta

run vesta to start
