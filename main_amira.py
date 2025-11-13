
from slusdlib import aeries, core
from pandas import read_csv, read_sql_query,isna, to_datetime
from sqlalchemy import text
from decouple import config
from icecream import ic


import_file = 'Amira to Aeries Import - 1000043973-ASSESSMENTS-2025_2026.csv'
cnxn = aeries.get_aeries_cnxn() if config('ENVIRONMENT', default=None) == 'PROD' else aeries.get_aeries_cnxn(database=config('TEST_DATABASE', default='DST25000SLUSD_DAILY'), access_level='w')
sql = core.build_sql_object()
grade_filter = 'Second Grade'  # Grade Level for filter. Set to None to disable

grade_translation = {
    'Preschool': -20,
    'Pre-Kindergarten': -10,
    'Kindergarten': 00,
    'First Grade': 10,
    'Second Grade': 20,
    'Third Grade': 30,
    'Fourth Grade': 40,
    'Fifth Grade': 50,
    'Sixth Grade': 60,
    'Seventh Grade': 70,
    'Eighth Grade': 80,
    'Ninth Grade': 90,
    'Tenth Grade': 100,
    'Eleventh Grade': 110,
    'Twelfth Grade': 120,
}

language_translation = {
    'English': 'EN',
    'Spanish': 'SP',
}

school_translation = {
    'Garfield Elementary': 2,
    'Monroe Elementary': 6,
    'McKinley Elementary': 5,
    'Roosevelt Elementary': 7,
    'Jefferson Elementary': 3,
    'Washington Elementary': 8,
    'Halkin Elementary School': 9,
    'Madison (James) Elementary': 4,
}

column_mapping = {
    'Overall ARM': {
        'PT': 0,
        'PC': 'ARM PR', #BB
        'PL': 'ARM-Level', #BC
        'GE': 'ARM', #AV
    },
    'Decoding': {
        'PT': 1,
        'PC': 'Decoding PR', #AC
        'PL': '',
        'GE': '',
        },
    'Phonological Awareness': {
        'PT': 2,
        'PC': 'PA PR', #Z
        'PL': '',
        'GE': '',
    },
    'High Frequency Words': {
        'PT': 3,
        'PC': 'HFW PR', #AA
        'PL': '',
        'GE': '',
    },
    'Background Knowledge': {
        'PT': 4,
        'PC': 'BK PR', #AZ
        'PL': '',
        'GE': '',
    },
    'Structures and Reasoning': {
        'PT': 5,
        'PC': 'Comp PR', #AS
        'PL': '',
        'GE': '',
    },
    'Vocabulary': {
        'PT': 6,
        'PC': 'Vocabulary PR', #AB
        'PL': '',
        'GE': '',
    },
}

def get_next_TST_sq(id:int, cnxn) -> int:
    """Get the next sequence number for a given table."""
    print(f"Getting next sequence number for table:  ID: {id}")
    query = "SELECT top 1 SQ FROM TST WHERE PID = :id ORDER BY SQ DESC"
    result = read_sql_query(text(query), cnxn, params={"id": id})
    if not result.empty:
        next_sq = result['SQ'].iloc[0] + 1
        return int(next_sq)
    else:
        return 1

def main():
    data = read_csv(f'in/{import_file}', dtype=str)
    data = data[data['Grade'] == grade_filter] if grade_filter else data # Filter by Grade Level
    data['Assessment Date'] = to_datetime(
        data['Assessment Date'], 
        errors='coerce', 
        format='mixed' 
    )
    IUI = config('AUTOMATION_USER_ID', default=10837)
    IUN = config('AUTOMATION_USERNAME', default='Automation')
    with cnxn.connect() as connection:
        for key, row in data.iterrows():
            if isna(row['Assessment Date']): continue
            params = {
                'TA':'BOY25',
                'ID':'Amira',
                'SQ':None,
                'IUI':IUI,
                'IUN':IUN,
                }
            params['PID'] = row['Student Alt ID'] # Aeries Student ID
            # params['TD'] = datetime.strptime(row['Assessment Date'], '%Y-%m-%d %H:%M:%S')
            params['TD'] = row['Assessment Date'].strftime('%Y-%m-%d %H:%M:%S')
            if isna(params['TD'] or params['TD'] == ''): continue
            
            params['TY'] = language_translation[row['Language']]

            params['GR'] = grade_translation[row['Grade']]
            params['SCL'] = school_translation[row['School']]
            params['DT'] = row['Assessment Date'].strftime('%m%y')          
            
            for test in column_mapping.keys():
                # set sequence number
                params['SQ'] = params['SQ'] + 1 if params['SQ'] != None else get_next_TST_sq(params['PID'], cnxn)
                
                #  get keys
                ge_key = column_mapping[test]['GE']
                pc_key = column_mapping[test]['PC']
                pl_key = column_mapping[test]['PL']
                
                # set test-specific params
                params['PT'] = column_mapping[test]['PT']
                params['PC'] = float(row[pc_key]) if pc_key != '' else 0
                params['PL'] = float(row[pl_key]) if pl_key != '' else 0
                params['GE'] = int(round(float(row[ge_key]), 1) * 10) if ge_key != '' and not isna(row[ge_key]) else 0
                
                # Replace empty strings with 0
                params = {key: 0 if isna(value) else value for key, value in params.items()}  # Replace empty strings with 0
                
                connection.execute(
                    text(sql.INSERT_TST),
                    params
                )
            connection.commit()  

if __name__ == '__main__':
    main()