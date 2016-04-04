# cosmic-rays-lightning
Intellegently extract significant cosmic ray events and correlate them with observed lightning activity.

## SQL Database:
The SQL Database containing the cosmic ray data can be found here (requires Box.com login):
https://osu.box.com/cosmic-rays-lightning

### Metadata for SQL database:
- Name: CRData.db
- Size: 1.3GB
- Tables:
    - Data
        - number of records: 23,602,157
        - fields:
            - Station (TEXT)
            - Date (INT)
            - Hour (INT)
            - Lat (REAL)
            - Lon (REAL)
            - Alt (REAL)
            - Warn (TEXT)
            - Count (INT)

### Building the SQL database

## Mirroring the WDCCR directory
The unix program 'lftp' can be used to mirror the ftp directory structure on the WDDCR website. I used the following
steps to mirror the ftp directory:
1. Open a terminal
2. Enter lftp and connect to the ftp server:
```
 lftp ftp.stelab.nagoya-u.ac.jp/
```
 3. Use `mirror` to copy the directory structure
The given options are
    - The `-c` performs the mirror in continue mode in case of network interrupt
    - The `--parallel=<positive int>` the files to be downloaded in parallel (<positive int>-fold)
    - The `--exclude` and `--exclude-glob` commands exclude unwanted files. We are only interested in the LONGFORMAT files
 ```
 lftp:~> mirror -c --parallel=<positive int> --exclude SHORTFORMAT/ --exclude CARDFORMAT --exclude OLD/ --exclude ORIGINAL/ --exclude-glob *_all.txt --exclude-glob *.pdf  pub/WDCCR/STATIONS/ <target directory>
 ```
4. Type `exit` to exit lftp

These steps are based on an lftp tutorials found here:
- http://www.cyberciti.biz/faq/lftp-mirror-example/
- http://www.cyberciti.biz/faq/lftp-command-mirror-x-exclude-files-sub-directory-syntax/

