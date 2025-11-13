# Amira to Aeries Import Tool

A Python-based automation tool for importing Amira reading assessment data into the Aeries Student Information System (SIS).

## Overview

This tool processes Amira assessment CSV files and imports the data into the Aeries TST (Test Scores) table. It handles multiple assessment types including Overall ARM, Decoding, Phonological Awareness, High Frequency Words, Background Knowledge, Structures and Reasoning, and Vocabulary.

## Features

- **Automated Data Import**: Bulk import of Amira assessment data into Aeries
- **Grade Level Filtering**: Optional filtering by specific grade levels
- **Multiple Assessment Types**: Supports 7 different assessment categories
- **Language Support**: Handles both English and Spanish assessments
- **Data Validation**: Includes date validation and NaN handling
- **Environment Configuration**: Supports both production and test database environments
- **Secure Configuration**: All sensitive data stored in environment variables

## Prerequisites

- Python 3.x
- Access to Aeries database
- Required Python packages (see Dependencies)

## Dependencies

```
pandas
sqlalchemy
python-decouple
icecream
slusdlib (custom library for Aeries and core SQL operations)
```

## Installation

1. Clone the repository
2. Install required packages:
   ```bash
   pip install pandas sqlalchemy python-decouple icecream
   ```
3. Configure your `.env` file (see Configuration section)

## Configuration

1. Copy the `.env.example` file to create your `.env` file:
   ```bash
   cp env.example .env
   ```

2. Update the `.env` file with your actual values:

```env
# Environment setting: PROD for production, TEST for test environment
ENVIRONMENT=PROD

# Test database name (only used when ENVIRONMENT=TEST)
TEST_DATABASE=YOUR_TEST_DATABASE_NAME

# Automation user credentials for database inserts
AUTOMATION_USER_ID=10837
AUTOMATION_USERNAME=Automation
```

**Important**: Never commit your `.env` file to version control. It is already included in `.gitignore`.

### Grade Translation

The tool supports the following grade levels:
- Preschool (-20)
- Pre-Kindergarten (-10)
- Kindergarten (0)
- First through Twelfth Grade (10-120, increments of 10)

### School Translation

Supported schools and their codes:
- Garfield Elementary (2)
- Monroe Elementary (6)
- McKinley Elementary (5)
- Roosevelt Elementary (7)
- Jefferson Elementary (3)
- Washington Elementary (8)
- Halkin Elementary School (9)
- Madison (James) Elementary (4)

### Language Translation

- English (EN)
- Spanish (SP)

## Usage

1. Place your Amira CSV export file in the `in/` directory
2. Update the `import_file` variable in `main_amira.py` with your filename:
   ```python
   import_file = 'your_amira_export_file.csv'
   ```
3. (Optional) Set the `grade_filter` variable to filter by specific grade level, or set to `None` to import all grades:
   ```python
   grade_filter = 'Second Grade'  # or None to disable filtering
   ```
4. Run the script:
   ```bash
   python main_amira.py
   ```

## Assessment Types

The tool processes seven assessment types:

| Assessment Type | PT Code | Percentile Column | Proficiency Level | Grade Equivalent |
|----------------|---------|-------------------|-------------------|------------------|
| Overall ARM | 0 | ARM PR | ARM-Level | ARM |
| Decoding | 1 | Decoding PR | - | - |
| Phonological Awareness | 2 | PA PR | - | - |
| High Frequency Words | 3 | HFW PR | - | - |
| Background Knowledge | 4 | BK PR | - | - |
| Structures and Reasoning | 5 | Comp PR | - | - |
| Vocabulary | 6 | Vocabulary PR | - | - |

## Input File Format

The CSV file should include the following columns:
- Student Alt ID (Aeries Student ID)
- Assessment Date
- Grade
- School
- Language
- Assessment-specific percentile rankings (ARM PR, Decoding PR, etc.)
- ARM-Level (for Overall ARM)
- ARM (Grade Equivalent for Overall ARM)

## Database Schema

The tool inserts data into the Aeries TST table with the following fields:
- PID (Student ID)
- ID (Test Identifier: "Amira")
- PT (Test Part/Type)
- GR (Grade Level)
- DT (Date Code)
- GE (Grade Equivalent)
- PC (Percentile)
- TD (Test Date)
- PL (Proficiency Level)
- TA (Test Administration: "BOY25")
- SQ (Sequence Number)
- SCL (School Code)
- TY (Test Type/Language)
- IDT (Insert DateTime)
- IUI (Insert User ID - from AUTOMATION_USER_ID env variable)
- IUN (Insert User Name - from AUTOMATION_USERNAME env variable)
- DTS (Date Time Stamp)

## Error Handling

- Skips records with invalid or missing assessment dates
- Handles NaN values by converting to 0
- Validates date formats with fallback error handling

## File Structure

```
.
├── .env                    # Environment configuration (not tracked)
├── env.example             # Example environment configuration
├── .gitignore              # Git ignore rules
├── main_amira.py           # Main import script
├── in/                     # Input directory for CSV files
│   └── .gitkeep
├── SQL/
│   └── INSERT_TST.sql      # SQL insert statement template
└── README.md               # This file
```

## Notes

- The tool automatically generates sequence numbers for each test record
- All inserts are committed in a single transaction per student
- Test dates are formatted as MM/YY for the DT field
- Grade equivalents are rounded and stored as integers (multiplied by 10)

## Security

This repository follows security best practices:

- **Environment Variables**: All sensitive data (database credentials, user IDs) are stored in `.env` file
- **Git Ignore**: `.env` file, CSV files (containing student data), and test files are excluded from version control
- **Parameterized Queries**: SQL queries use parameterized statements to prevent SQL injection
- **Example Configuration**: `env.example` provides a template without exposing sensitive values

**Setup Checklist**:
1. ✅ Copy `env.example` to `.env`
2. ✅ Update `.env` with your actual credentials
3. ✅ Verify `.env` is listed in `.gitignore`
4. ✅ Never commit `.env` to version control

## Support

For issues related to the Aeries connection or SLUSD-specific configurations, consult the `slusdlib` library documentation.

## License

[Add your license information here]