#!/usr/bin/env python3
import sys
import os
import run
from pathlib import Path
import csv

# STARTS ALL HERE

def tootStart_MAIN(mode):
        if (mode == 0):
            print('Not Live. Testing Mode')
        elif (mode == 1):
            print('Looping through text file...')
            """ Arguments:
            key {string} -- Name of the key in the config.json file.
            """

            my_file = Path(__file__).parent / 'list.txt'
        
            if not my_file.is_file():

                print('--- list.txt not found in toot.py. Exiting.')

                sys.exit()

            config_file = open(Path(__file__).parent / 'list.txt')
            try:
                config = config_file.read()
            except:
                if not config:
        
                    print('--- list.txt in toot.py is a file but we can\'t open it. Exiting.')

                sys.exit()
            # Ok although sloppy with all this non objected oriented sys exit stuff... we should have the file ready to read...

            z = open((Path(__file__).parent / 'list.txt'))
            for line in z.readlines():
                cols = line.split(',')
                line_status_pulled= []
                twitter_nametopull_pulled = []
                mastodon_secret_pulled = []
                mastodon_host_pulled = []
                try:
                    line_status_pulled= int(cols[0].strip())
                    twitter_nametopull_pulled = cols[1].strip()
                    mastodon_secret_pulled = cols[2].strip()
                    mastodon_host_pulled = cols[3].strip()
                except:
                    print('ERROR: Assigning individual account info from text file to variables 07061234')

                # You have the individual entry now. Do what you want with it.
                if (line_status_pulled == 1):
                    currentRun = run.runME(twitter_nametopull_pulled,mastodon_secret_pulled,mastodon_host_pulled)
                    print(currentRun)
                elif (line_status_pulled == 0):
                    print ('\n\nEntry: '+twitter_nametopull_pulled+' set to skip in lists file. No Action Taken.\n\n')
                # / You have the individual entry now. Do what you want with it.
            z.close

if __name__ == '__main__':
    program_Mode=tootStart_MAIN(1)
