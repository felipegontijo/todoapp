from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://felipegontijo@localhost:5432/todoapp'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo ID: {self.id} {self.description}>'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)


# db.create_all() --> no need since now we're using Flask-Migrate

@app.route('/')
def index():
    return render_template('index.html', todos = Todo.query.order_by('id').all())

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:    
        description = request.get_json()['description']
        new_todo = Todo(description=description)
        db.session.add(new_todo)
        db.session.commit()
        # access new_todo.description before the session is closed
        body['description'] = new_todo.description
        body['id'] = new_todo.id
        body['completed'] = new_todo.completed
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)

@app.route('/todos/<todo_id>/check', methods=['POST']) # route to handle changes of state in todos
def check_todo(todo_id): # pass in the todos id
    error = False
    try:
        is_checked = request.get_json()['is_checked'] # get the checked info from the client side request -- true or false
        todo = Todo.query.get(todo_id) # grab that todo in our database
        todo.completed = is_checked # set the todos completed property in database to the info received from client
        db.session.commit() # commit changes to db
    except:
        error = True
        db.session.rollback() # rollback in case of any errors
        print(sys.exc_info())
    finally:
        db.session.close() # always close the connection
    if error:
        abort(500) # show server error status message in case of error
    else:
        return redirect(url_for('index')) # redirect user to refreshed homepage if no error

@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete_todo(todo_id):
    error = False
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        # instead of the two steps above, we could do: Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({ 'success': True })

if __name__ == '__main__':
    app.run()