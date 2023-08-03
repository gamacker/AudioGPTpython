# AudioGPTpython
A way to use chatgpt through voice
You need to put your OpenAI api key into a .env file in order for this to work. It only costs a few cents to run this, though it might get slightly higher with extended use.
apikey=\<yourkeyhere>

For linux you may need:
sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt-get install ffmpeg libav-tools
sudo apt install espeak 

Then:
pip3 install -r requirements.txt
