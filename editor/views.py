from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
import subprocess
import tempfile


@api_view(['POST'])
def execute_code(request):
    """
    API Endpoint to execute code sent from the frontend.
    Expected input: {"code": "<code_string>", "language": "<language>"}
    """
    code = request.data.get('code', '')
    language = request.data.get('language', '')

    if not code or not language:
        return Response({"error": "Code and language are required."}, status=400)

    # Map language to file extensions and execution commands
    language_map = {
        "javascript": {"ext": "js", "command": "node"},
        "python": {"ext": "py", "command": "python3"},
        "java": {"ext": "java", "command": "javac && java"},
        "c": {"ext": "c", "command": "gcc -o program && ./program"},
        "cpp": {"ext": "cpp", "command": "g++ -o program && ./program"},
        "php": {"ext": "php", "command": "php"},
    }

    if language not in language_map:
        return Response({"error": f"Language '{language}' not supported."}, status=400)

    lang_config = language_map[language]

    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix=f".{lang_config['ext']}", delete=False) as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_file.flush()

            # Build the execution command
            if "&&" in lang_config['command']:
                compile_cmd, run_cmd = lang_config['command'].split("&&")
                compile_process = subprocess.run(
                    compile_cmd.strip().split() + [temp_file.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if compile_process.returncode != 0:
                    return Response({"output": compile_process.stderr}, status=400)

                # Run the compiled program
                run_process = subprocess.run(
                    run_cmd.strip().split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                output = run_process.stdout or run_process.stderr
            else:
                process = subprocess.run(
                    lang_config['command'].split() + [temp_file.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                output = process.stdout or process.stderr

        return Response({"output": output})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
