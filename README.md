##zStream

zStream is a simple python application that will connect to zkillboard websockets to parse killmails and output to IRC

the project is in it's infancy and will probably go through rapid changes

The plan going forward is to support simple IRC and Discord connections
however as of writing this the only output is with PLwebhooks for sopel

###install
    cp config.py.example config.py
    pip3 install -r requirements.txt
    
###run
    python3 main.py
    
That's it