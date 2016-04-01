# cosmic-rays-lightning
Intellegently extract significant cosmic ray events and correlate them with observed lightning activity.

## SQL Database:
The SQL Database containing the cosmic ray data can be found here:
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
