from flask import Flask, request, render_template_string, g, redirect
import mysql.connector
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notes Service</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-3xl">
        <h1 class="text-4xl font-bold text-center text-gray-800 mb-8">✍️ Notes Service</h1>

        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <form method="POST" class="space-y-4">
                <textarea
                    name="content"
                    rows="4"
                    placeholder="Write your note here..."
                    required
                    class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                ></textarea>
                <button
                    type="submit"
                    class="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition duration-200"
                >
                    Add Note
                </button>
            </form>
        </div>

        <h2 class="text-2xl font-semibold text-gray-800 mb-4">📝 Notes:</h2>
        <div class="space-y-4">
            {% for note in notes %}
                <div class="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition duration-200 transform hover:-translate-y-1 relative group">
                    {{ note[1] }}
                    <form method="POST" action="/delete/{{ note[0] }}" class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <button type="submit"
                                class="flex items-center justify-center bg-red-50 hover:bg-red-100 text-red-500 hover:text-red-700 rounded-full w-8 h-8 transition-colors duration-200"
                                onclick="return confirm('Вы уверены, что хотите удалить эту заметку?')">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </form>
                </div>
            {% endfor %}
        </div>

        <div class="fixed bottom-4 right-4">
            <div class="bg-gray-800 text-white px-4 py-2 rounded-full text-sm">
                🖥️ Served by: {{ server_name }}
            </div>
        </div>
    </div>
</body>
</html>
"""

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host='10.250.1.166', # TODO server2
            user='notes_user',
            password='notes_password',
            database='notes_db',
            charset='utf8mb4'
        )
    return g.db

@app.route('/', methods=['GET', 'POST'])
def index():
    server_name = request.headers.get('X-Server-Name', 'Unknown')

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('INSERT INTO notes (content) VALUES (%s)', (content,))
            db.commit()
            cursor.close()

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM notes ORDER BY id DESC')
    notes = cursor.fetchall()
    cursor.close()

    return render_template_string(HTML_TEMPLATE, notes=notes, server_name=server_name)

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM notes WHERE id = %s', (note_id,))
    db.commit()
    cursor.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
