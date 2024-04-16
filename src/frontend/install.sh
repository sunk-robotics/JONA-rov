#!/bin/bash
sudo rm -rf /var/jona-server
sudo rm -rf /var/jona-server
echo "Deleted old frontend code"
sudo cp -r /home/sunk/JONA-rov/src/frontend /var/jona-server
sudo chown -R sunk:sunk /var/jona-server
echo "Installed new frontend code"