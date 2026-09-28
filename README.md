# AI Student Study Assistant

A beginner-friendly Python project that helps college students build a personalized study plan using AI.

## Features

- Collect student study details
- Generate a day-by-day study plan
- Track study task progress
- Save data in a local JSON file
- Use OpenAI API if an API key is available
- Provide a simple terminal menu interface

## Project Structure

- `main.py` - main application
- `requirements.txt` - Python dependencies
- `study_data.json` - saved student plan and progress
- `.env.example` - template for environment variables
- `README.md` - project instructions

## Requirements

- Python 3.10+
- Internet access for AI API calls

## Install dependencies

```bash
pip install -r requirements.txt
```

## Set up the OpenAI API key

Do not hard-code your API key into the source code.

### macOS / Linux

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

### Windows Command Prompt

```cmd
set OPENAI_API_KEY=your_api_key_here
```

You can also create a `.env` file if you want, but this project reads directly from the environment variable.

## Run the app

```bash
python main.py
```

## How it works

1. The program asks the user for personal study information.
2. It creates a study plan using a beginner-friendly algorithm.
3. If the `OPENAI_API_KEY` environment variable is set, it can ask OpenAI for an AI-generated recommendation.
4. The plan and progress are saved to `study_data.json` so the data stays available after restart.

## Example menu

```text
===== AI STUDENT STUDY ASSISTANT =====

1. Create Study Plan
2. View Study Plan
3. Update Task Status
4. View Progress
5. Get AI Recommendation
6. Exit
```

## Beginner-friendly Python concepts used

- Variables
- Input/output
- if/else statements
- loops
- functions
- lists
- dictionaries
- JSON file handling
- exception handling
- API requests
- basic object-oriented programming

## License

This project is for learning and demonstration purposes.
