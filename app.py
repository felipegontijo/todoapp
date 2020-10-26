from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

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
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo ID: {self.id}, description: {self.description}, completed: {self.completed}>'

class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=True, default=False)
    todos = db.relationship('Todo', backref='list', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<List ID: {self.id}, name: {self.name}, todos: {self.todos}'

# db.create_all() --> no need since now we're using Flask-Migrate

@app.route('/')
def index():
    return redirect(url_for('get_list', list_id=1))

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:    
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        new_todo = Todo(description=description, list_id=list_id)
        db.session.add(new_todo)
        db.session.commit()
        # access new_todo.description before the session is closed
        body['description'] = new_todo.description
        body['id'] = new_todo.id
        body['completed'] = new_todo.completed
        body['list_id'] = new_todo.list_id
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

@app.route('/lists/<list_id>')
def get_list(list_id):
    lists = List.query.order_by('id').all()
    todos = Todo.query.filter_by(list_id=list_id).order_by('id').all()
    active_list = List.query.get(list_id)
    
    return render_template('index.html', todos=todos, lists=lists, active_list=active_list)

@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False
    body = {}
    try:
        list_name = request.get_json()['name']
        new_list = List(name=list_name)
        db.session.add(new_list)
        db.session.commit()
        body['name'] = new_list.name
        body['id'] = new_list.id
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

@app.route('/lists/<list_id>/check', methods=['POST'])
def check_list(list_id):
    error = False
    body = []
    try:
        is_list_checked = request.get_json()['is_list_checked']
        list_to_change = List.query.get(list_id)
        list_to_change.completed = is_list_checked
        for todo in Todo.query.filter_by(list_id=list_id).order_by('id').all():
            todo.completed = is_list_checked
            body.append(todo.id)
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
        return jsonify(body)

@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
    error = False
    try:
        list_to_delete = List.query.get(list_id)
        db.session.delete(list_to_delete)
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